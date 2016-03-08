import spotipy
import spotipy.util as util
import os

os.environ['SPOTIPY_CLIENT_ID']='8189ec06c3b842fe8328860ac9d55bc1'
os.environ['SPOTIPY_CLIENT_SECRET']='3d850530b8524db6a8a406167d68cb1b'
os.environ['SPOTIPY_REDIRECT_URI']=('http://localhost:5000/spotifycallback').encode('utf-8')

def addTracks(track_ids):

    username = 'michaelahari'
    scope = 'playlist-modify-public'
    token = util.prompt_for_user_token(username, scope)
    playlist_id = "5B1sHuZjlgROjT54SjA1iP"
    track_ids = {"spotify:track:2SIwqSjxMgPEWtAaVDGnas"}

    if token:
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        results = sp.user_playlist_add_tracks(username, playlist_id, track_ids)
        return True
    else:
        return False
