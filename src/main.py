import os, random

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

    top_track_info = []
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
                print(f'{song.artist.name} | {song.bpm}')
                break
            if index >= 3:
                break

        if bpm != 0:
            top_track_info.append((track['name'], bpm))

    tracks_html = '<br>'.join([f'{name}: {bpm}' for name, bpm in top_track_info])

    devices = spotify.devices()
    device = None
    for device in devices['devices']:
        if device['is_active']:
            device = device['id']
            break
        if device['type'] == "Computer":
            device = device['id']
    #spotify.start_playback(uris=[top_track['items'][random.randint(0,99)]['external_urls']['spotify']], device_id=device)

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