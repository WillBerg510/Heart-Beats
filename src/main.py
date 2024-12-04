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

async def heart_rate(shared_hr):
    url = "wss://dev.pulsoid.net/api/v1/data/real_time?access_token=a051ca5c-1be4-4c94-91d1-c23937388f5c&response_mode=text_plain_only_heart_rate"
    try:
        async with websockets.connect(url) as websocket:
            while True:
                message = await websocket.recv()
                shared_hr.value = int(message)

    except Exception as e:
        print(f"Error connecting to WebSocket: {e}")

def start_track(shared_hr):
    asyncio.run(heart_rate(shared_hr))

deezer = deezer.Client()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
CORS(app)

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

spotify_auth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True
)
spotify = Spotify(auth_manager=spotify_auth)

@app.route('/')
def home():
    if not spotify_auth.validate_token(cache_handler.get_cached_token()):
        auth_url = spotify_auth.get_authorize_url()
        return redirect(auth_url)
    return redirect(url_for('get_playlists'))

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
        pool = request.get_json()['pool']
        return 'success', 204
    return 'failed', 405

@app.route('/connected')
def connected():
    global pool
    global current_song
    print('Connected to Spotify account. Head to https://dsa-heartbeats.netlify.app/ to continue.')
    while pool == 0:
        time.sleep(0.01)
    if not spotify_auth.validate_token(cache_handler.get_cached_token()):
        auth_url = spotify_auth.get_authorize_url()
        return redirect(auth_url)

    if pool == 1:
        top_track = spotify.current_user_top_tracks(limit=25)
        #top_track['items'] += spotify.current_user_top_tracks(limit=50, offset=50)['items']

    #playlist = spotify.playlist_items(playlist_id="6bDQr1LIm5Ih1UtHAjd42M", fields="items")
    #playlist['items'] += spotify.playlist_items(playlist_id="6bDQr1LIm5Ih1UtHAjd42M", fields="items", offset=100)['items']

    global adj_list
    global song_map

    # List of song ids
    playlist_songs = []

    for track in top_track['items']:
        #track = item['track']
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
                uri=track['external_urls']['spotify']
            )
            adj_list.add_node(song_node)
            song_map.add_node((int(bpm / 10) * 10, int(bpm / 10) * 10 + 9), song_node)
            playlist_songs.append(track['uri'])

    adj_list.form_connections()

    devices = spotify.devices()
    device = None
    for device in devices['devices']:
        if device['is_active']:
            device = device['id']
            break
        if device['type'] == "Computer":
            device = device['id']

    global songs_loaded
    songs_loaded = True

    starting_song = adj_list.get_next_song(adj_list.get_starting_song(), shared_hr.value);
    spotify.add_to_queue(uri=starting_song.get_uri(), device_id=device)

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

    #spotify.start_playback(uris=[top_track['items'][random.randint(0,49)]['external_urls']['spotify']], device_id=device)

    # Make a playlist
    time_now = datetime.now()
    time_string = time_now.strftime('%Y-%m-%d %H:%M:%S')
    user_id = spotify.me()['id']
    new_playlist = spotify.user_playlist_create(
        user=user_id,
        name=f'Heart Beats: {time_string}',
        public=False
    )
    #spotify.user_playlist_add_tracks(
    #    user=user_id,
    #    playlist_id=new_playlist['id'],
    #    tracks=playlist_songs)

    return tracks_html

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

if __name__ == "__main__":
    # Creates a global variable for the heart rate that is shared with the parallel processes
    shared_hr = multiprocessing.Value('i', 0)
    # Create and start the parallel process that will continuously update the user's heart rate
    heartrate = multiprocessing.Process(target=start_track, args=(shared_hr,))
    heartrate.start()

    # Start the web app
    app.run(debug=True)