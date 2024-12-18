import os, random, time, multiprocessing
from datetime import datetime

import TrackNode as Node
import AdjList as List
import Map as MapStructure

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from flask import Flask, session, url_for, redirect, request
from flask_cors import CORS
import deezer

import asyncio
import websockets

# Asynchronous method to continuously monitor and record the user's heart rate
async def heart_rate(shared_hr):
    # Pulsoid's websocket URL
    url = "wss://dev.pulsoid.net/api/v1/data/real_time?access_token=a051ca5c-1be4-4c94-91d1-c23937388f5c&response_mode=text_plain_only_heart_rate"
    try:
        # Upon a successful websocket connection
        async with websockets.connect(url) as websocket:
            # Run forever
            while True:
                # Wait for a message from the websocket, which is the user's current heart rate
                message = await websocket.recv()
                # Update the user's heart rate on the backend
                shared_hr.value = int(message)

    except Exception as e:
        print(f"Error connecting to WebSocket: {e}")

# This method is used for multiprocessing since it normally doesn't work with async methods.
def start_track(shared_hr):
    # Runs the async method to monitor and record heart rate.
    asyncio.run(heart_rate(shared_hr))

# Initialize the Deezer client so we can interact with the API.
deezer = deezer.Client()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
CORS(app)

# Spotify Application Details
client_id = '6763d6f8edfb46f790cc18ba91bd761b'
client_secret = '2168293833d4470694944c0cdb469cdc'
redirect_uri = 'http://localhost:5000/callback'
scope = ('playlist-read-private, '
         'app-remote-control, '
         'streaming, '
         'user-top-read, '
         'user-read-playback-state, '
         'playlist-modify-public, '
         'playlist-modify-private'
         )
cache_handler = FlaskSessionCacheHandler(session)

username = ''
adj_list = List.AdjList()
song_map = MapStructure.Map()
pool = 0
songs_loaded = False
current_song = Node.TrackNode()
data_structure = ''
playlistID = ''
playlist_requested = False

# Spotify authentication object
spotify_auth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True
)
spotify = Spotify(auth_manager=spotify_auth)

# Initial routing framework with Flask from a Spotipy tutorial by Imdad Codes.
@app.route('/')
def home():
    # Checks to see if the user is not authenticated with Spotify.
    if not spotify_auth.validate_token(cache_handler.get_cached_token()):
        # If they aren't redirect them to the authentication URL
        auth_url = spotify_auth.get_authorize_url()
        return redirect(auth_url)
    # Otherwise, start the main program.
    return redirect(url_for('get_playlists'))

# Spotify app requires a callback URL after authentication is successful.
@app.route('/callback')
def callback():
    spotify_auth.get_access_token(request.args['code'])
    global username
    username = spotify.me()['display_name']
    return redirect(url_for('connected'))

@app.route('/begin', methods=['POST'])
def begin():
    if username != '':
        global pool
        global data_structure
        global playlistID
        pool = request.get_json()['pool']
        data_structure = request.get_json()['dataStructure']
        playlistID = request.get_json()['IDofPlaylist']
        return 'success', 204
    return 'failed', 405

# First creates an empty playlist, then adds all the songs played from the session to the playlist.
def playlistCreation(playlist_songs):
    global playlist_requested

    # Make a playlist
    time_now = datetime.now()
    time_string = time_now.strftime('%Y-%m-%d %H:%M:%S')
    user_id = spotify.me()['id']
    new_playlist = spotify.user_playlist_create(
        user=user_id,
        name=f'HeartBeats: {time_string}',
        public=False
    )
    spotify.user_playlist_add_tracks(
        user=user_id,
        playlist_id=new_playlist['id'],
        tracks=playlist_songs)

    playlist_requested = False


@app.route('/connected')
def connected():
    global pool
    global current_song
    global playlistID
    print('Connected to Spotify account. Head to https://dsa-heartbeats.netlify.app/ to continue.')
    while pool == 0:
        time.sleep(0.01)
    if not spotify_auth.validate_token(cache_handler.get_cached_token()):
        auth_url = spotify_auth.get_authorize_url()
        return redirect(auth_url)

    if pool == 1:
        track_list = spotify.current_user_top_tracks(limit=50)

    if pool == 2:
        track_list = spotify.playlist(playlist_id=playlistID)['tracks']
        num_tracks = track_list['total'] - 100
        if num_tracks > 0:
            num_tracks = num_tracks // 100
            print(num_tracks)
            offset = 100
            while num_tracks > 0:
                num_tracks -= 1
                add_tracks = spotify.playlist_tracks(playlist_id=playlistID, limit=100, offset=offset)['items']
                offset += 100
                track_list['items'] += add_tracks


    global adj_list
    global song_map

    # List of song ids
    playlist_songs = []

    for track in track_list['items']:
        if pool == 2:
            track = track['track']
        if track is None:
            continue

        acceptable_symbols = [',', '\'', '-', '.', '(', ')', ' ', '\"', '!', '&']
        track_name = ''.join(letter for letter in track['name'] if (letter.isalnum() or letter in acceptable_symbols))
        deezer_track = deezer.search(track=track_name, artist=track['artists'][0]['name'])

        bpm = 0
        index = 0
        for song in deezer_track:
            index += 1
            if song.title == track['name'] and song.artist.name == track['artists'][0]['name']:
                bpm = song.bpm
                break
            if index >= 10:
                break

        print(track['name'] + " |  " + str(bpm))

        if bpm > 0:
            song_node = Node.TrackNode(
                name=track['name'],
                artist=track['artists'][0]['name'],
                cover_link=track['album']['images'][0]['url'],
                bpm=bpm,
                genres=spotify.artist(track['artists'][0]['id'])['genres'],
                release_year=track['album']['release_date'][:4],
                uri=track['external_urls']['spotify'],
                duration=int(track['duration_ms']/1000),
            )
            adj_list.add_node(song_node)
            song_map.add_node((int(bpm / 10) * 10, int(bpm / 10) * 10 + 9), song_node)
    
    if data_structure == 'Graph':
        adj_list.form_connections()

    devices = spotify.devices()
    device = None
    for device in devices['devices']:
        if device['is_active']:
            device = device['id']
            break
        if device['type'] == "Computer" or device['type'] == "Smartphone":
            device = device['id']

    global songs_loaded
    songs_loaded = True
    
    if data_structure == 'Graph':
        queue_song = adj_list.get_next_song(adj_list.get_starting_song(), shared_hr.value)
        spotify.start_playback(uris=[queue_song.get_uri()], device_id=device)
        while True:
            current_song = queue_song
            playlist_songs.append(current_song.get_uri())
            while not spotify.current_playback() or spotify.current_playback()['progress_ms'] / 1000 < queue_song.get_duration() - 3:
                time.sleep(1)
                if playlist_requested:
                    playlistCreation(playlist_songs)
            queue_song = adj_list.get_next_song(queue_song, shared_hr.value)
            spotify.add_to_queue(uri=queue_song.get_uri(), device_id=device)
            while not spotify.current_playback()['progress_ms'] / 1000 < 5:
                time.sleep(1)
                if playlist_requested:
                    playlistCreation(playlist_songs)
    elif data_structure == 'Map':
        queue_song = song_map.get_starting_song(shared_hr.value)
        spotify.start_playback(uris=[queue_song.get_uri()], device_id=device)
        while True:
            current_song = queue_song
            playlist_songs.append(current_song.get_uri())
            while not spotify.current_playback() or spotify.current_playback()['progress_ms'] / 1000 < queue_song.get_duration() - 3:
                time.sleep(1)
                if playlist_requested:
                    playlistCreation(playlist_songs)
            queue_song = song_map.get_next_song(queue_song, shared_hr.value)
            spotify.add_to_queue(uri=queue_song.get_uri(), device_id=device)
            while not spotify.current_playback()['progress_ms'] / 1000 < 5:
                time.sleep(1)
                if playlist_requested:
                    playlistCreation(playlist_songs)

    # This code won't ever run, but we used it to test out fetching info from the Spotify API and adding it to our graph
    tracks_html = '<br>'.join([f'{node[0].get_name()} | '
                               f'Genres: {node[0].get_genres()} | '
                               f'BPM: {node[0].get_bpm()} | '
                               f'Release Year: {node[0].get_release_year()} | '
                               f'Connected to: {", ".join(similar_node.get_name() for similar_node in adj_list.get_adjacent(node[0]))} | '
                               f'Similarity scores: {", ".join(str(similarity) for similarity in adj_list.get_similarity_scores(node[0]))}'
                               f'<br> <img src={node[0].get_cover()} style=\"height:10%;\">'
                               for node in adj_list.get_list().values()])

    tracks_html += '<br><br>Tempo Range Map<br>'
    tracks_html += '<br>'.join(str(tempo_range[0][0]) + '-' + str(tempo_range[0][1]) + ': ' + ', '.join(node.get_name() for node in tempo_range[1]) for tempo_range in song_map.get_map())

    return tracks_html

@app.route('/make_playlist')
def make_playlist():
    global playlist_requested
    playlist_requested = True
    return 'success', 204

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/username')
def username_info():
    global username
    return {
        "username": username,
    }

@app.route('/heart_rate')
def hr_route():
    return {
        "heartRate": shared_hr.value,
    }

@app.route('/songs_loaded')
def loaded():
    return {
        "loaded": songs_loaded,
    }

@app.route('/song_information')
def song_information():
    if not songs_loaded or not adj_list.get_adjacent:
        return 'failed', 405
    information = {
        "thisSong": {
            "name": current_song.get_name(),
            "bpm": current_song.get_bpm(),
            "artist": current_song.get_artist(),
            "album_cover": current_song.get_cover()
        },
        "otherSongs": {}
    }
    if data_structure == "Graph":
        i = 0
        for connected_song in adj_list.get_adjacent(current_song):
            information["otherSongs"]["id" + str(i)] = {
                "name": connected_song.get_name(),
                "bpm": connected_song.get_bpm(),
                "artist": connected_song.get_artist(),
                "album_cover": connected_song.get_cover()
            }
            i += 1
    if data_structure == "Map":
        i = 0
        for tempo_song in song_map.get_nodes((int(shared_hr.value / 10) * 10, int(shared_hr.value / 10) * 10 + 9)):
            information["otherSongs"]["id" + str(i)] = {
                "name": tempo_song.get_name(),
                "bpm": tempo_song.get_bpm(),
                "artist": tempo_song.get_artist(),
                "album_cover": tempo_song.get_cover()
            }
            i += 1
    return information

if __name__ == "__main__":
    # Creates a global variable for the heart rate that is shared with the parallel processes
    shared_hr = multiprocessing.Value('i', 0)
    # Create and start the parallel process that will continuously update the user's heart rate
    heartrate = multiprocessing.Process(target=start_track, args=(shared_hr,))
    heartrate.start()

    # Start the web app
    app.run(debug=True)