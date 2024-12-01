import os, random

import spotipy, flask
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from flask import Flask, session, url_for, redirect, request

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

client_id = '6763d6f8edfb46f790cc18ba91bd761b'
client_secret = '2168293833d4470694944c0cdb469cdc'
redirect_uri = 'http://localhost:5000/callback'
scope = 'playlist-read-private, app-remote-control, streaming, user-top-read, user-read-playback-state'
cache_handler = FlaskSessionCacheHandler(session)

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

    playlists = spotify.current_user_playlists()
    playlists_info = []
    for item in playlists['items']:
        if item is None:
            continue
        playlists_info.append((item['name'], item['external_urls']['spotify']))
    playlists_html = '<br>'.join([f'{name}: {url}' for name, url in playlists_info])

    top_track = spotify.current_user_top_tracks(limit=10)

    devices = spotify.devices()
    device = None
    for device in devices['devices']:
        if device['is_active']:
            device = device['id']
            break
        if device['type'] == "Computer":
            device = device['id']
    spotify.start_playback(uris=[top_track['items'][random.randint(0,9)]['external_urls']['spotify']], device_id=device)

    return playlists_html

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)