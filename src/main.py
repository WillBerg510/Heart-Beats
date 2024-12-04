import os, random

import TrackNode as Node
import AdjList as List
import Map as MapStructure

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from flask import Flask, session, url_for, redirect, request
import deezer

deezer = deezer.Client()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

client_id = '6763d6f8edfb46f790cc18ba91bd761b'
client_secret = '2168293833d4470694944c0cdb469cdc'
redirect_uri = 'http://localhost:5000/callback'
scope = 'playlist-read-private, app-remote-control, streaming, user-top-read, user-read-playback-state'
cache_handler = FlaskSessionCacheHandler(session)

toCommunicate = ''
adj_list = List.AdjList();
song_map = MapStructure.Map();

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
    return redirect(url_for('get_playlists'))

@app.route('/get_playlists')
def get_playlists():
    if not spotify_auth.validate_token(cache_handler.get_cached_token()):
        auth_url = spotify_auth.get_authorize_url()
        return redirect(auth_url)

    top_track = spotify.current_user_top_tracks(limit=50)
    top_track['items'] += spotify.current_user_top_tracks(limit=50, offset=50)['items']

    global adj_list
    global song_map

    for track in top_track['items']:
        if track is None:
            continue
        deezer_track = deezer.search(track['name'])

        bpm = 0
        index = 0
        for song in deezer_track:
            index += 1
            if song.title == track['name'] and song.artist.name == track['artists'][0]['name']:
                bpm = song.bpm
                break
            if index >= 5:
                break

        if bpm > 0:
            song_node = Node.TrackNode(
                name=track['name'],
                artist=track['artists'][0]['name'],
                cover_link=track['album']['images'][0]['url'],
                bpm=bpm,
                genres=spotify.artist(track['artists'][0]['id'])['genres'],
                release_year=track['album']['release_date'][:4]
            )
            adj_list.add_node(song_node)
            song_map.add_node((int(bpm / 10) * 10, int(bpm / 10) * 10 + 9), song_node)

    adj_list.form_connections()

    tracks_html = '<br>'.join([f'{node[0].get_name()} | '
                               f'Genres: {node[0].get_genres()} | '
                               f'BPM: {node[0].get_bpm()} | '
                               f'Release Year: {node[0].get_release_year()} | '
                               f'Connected to: {", ".join(similar_node.get_name() for similar_node in adj_list.get_adjacent(node[0]))} | '
                               f'Similarity scores: {", ".join(str(similarity) for similarity in adj_list.get_similarity_scores(node[0]))}'
                               f'<br> <img src={node[0].get_cover()} style=\"height:10%;\">'
                               for node in adj_list.get_list().values()])

    tracks_html += '<br>Tempo Range Map<br>'
    tracks_html += '<br>'.join(str(tempo_range[0][0]) + '-' + str(tempo_range[0][1]) + ': ' + ', '.join(node.get_name() for node in tempo_range[1]) for tempo_range in song_map.get_map())

    devices = spotify.devices()
    device = None
    for device in devices['devices']:
        if device['is_active']:
            device = device['id']
            break
        if device['type'] == "Computer":
            device = device['id']

    #spotify.start_playback(uris=[top_track['items'][random.randint(0,49)]['external_urls']['spotify']], device_id=device)

    global toCommunicate
    toCommunicate = spotify.me()['display_name']

    return tracks_html

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/initial_info')
def initial_info():
    return {
        "username": toCommunicate
    }

if __name__ == "__main__":
    app.run(debug=True)