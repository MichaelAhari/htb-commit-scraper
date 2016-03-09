import spotipy
import spotipy.util as util
import os
import json
import requests

os.environ['SPOTIPY_CLIENT_ID']='8189ec06c3b842fe8328860ac9d55bc1'
os.environ['SPOTIPY_CLIENT_SECRET']='3d850530b8524db6a8a406167d68cb1b'
os.environ['SPOTIPY_REDIRECT_URI']=('http://localhost:5000/spotifycallback').encode('utf-8')

def spotifyConnect():
    username = 'michaelahari'
    scope = 'playlist-modify-public'
    token = util.prompt_for_user_token(username, scope)
    return token

def getTracks(playlist_id, token):
    #no authorization required
    USER_ID="spotify"
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    request = sp.user_playlist(USER_ID, playlist_id=playlist_id, fields="tracks")
    # request = requests.get("https://api.spotify.com/v1/search?q=%s&type=playlist" % (playlist))
    tracks = request['tracks']['items']
    for track in tracks:
        print track['track']['name']
    # request = requests.get(json_data['playlists']['items'][0]['tracks']['href'])
    # print request.status_code
    #print request['items'][0]['track']['name']


def addTracks(playlist_id, track_id):

    username = 'michaelahari'
    scope = 'playlist-modify-public'
    token = util.prompt_for_user_token(username, scope)
    playlist_id = "5B1sHuZjlgROjT54SjA1iP"

    if token:
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        results = sp.user_playlist_add_tracks(username, playlist_id, track_ids)
        return True
    else:
        return False
