import spotipy
import spotipy.util as util
import os
import json
import requests
from random import randint

os.environ['SPOTIPY_CLIENT_ID']='8189ec06c3b842fe8328860ac9d55bc1'
os.environ['SPOTIPY_CLIENT_SECRET']='3d850530b8524db6a8a406167d68cb1b'
os.environ['SPOTIPY_REDIRECT_URI']=('http://localhost:5000/spotifycallback').encode('utf-8')

def spotifyConnect():
    username = 'michaelahari'
    scope = 'playlist-modify-private'
    token = util.prompt_for_user_token(username, scope)
    return token

def getTrack(playlist_info, token):

    #set up
    USER_ID = playlist_info["artist"]
    PLAYLIST_ID = playlist_info["playlist_id"]

    sp = spotipy.Spotify(auth=token)
    sp.trace = False

    #get tracks in playlist
    request = sp.user_playlist(USER_ID, playlist_id=PLAYLIST_ID, fields="tracks")
    tracks = request['tracks']['items']
    item = randint(0,len(tracks)-1)

    #get tracks already in our playlist
    request = sp.user_playlist('michaelahari', playlist_id="0H8XxdGolLwGr45HVEU9Dm", fields="tracks")
    current_tracks = request['tracks']['items']

    #check its not already in the playlist
    while tracks[item] in current_tracks:
        item = randint(0,len(tracks)-1)

    #return track
    return tracks[item]


    # for track in tracks:
    #     print track['track']['name']
    # request = requests.get(json_data['playlists']['items'][0]['tracks']['href'])
    # print request.status_code
    #print request['items'][0]['track']['name']


def addTrack(track_id, token):

    #set up
    USER_ID="michaelahari"
    PLAYLIST_ID = "0H8XxdGolLwGr45HVEU9Dm"
    TRACK_IDS = [track_id]

    sp = spotipy.Spotify(auth=token)
    sp.trace = False

    request = sp.user_playlist_add_tracks(USER_ID, PLAYLIST_ID, TRACK_IDS)

def searchArtist(search_term):
    # #set up
    # sp = spotipy.Spotify(auth=token)
    # sp.trace = False
    #
    # result = sp.search(q=search_term, type="artist")
    #
    # if result.status_code == 204:
    #     return False
    # else:
    #     artist_data = result['artists']['items'][0]
    #     artist_id = artist_data['id']
    #     return artist_id
    return ''

def getArtistTrack(artist_id,token):
    # #set up
    # sp = spotipy.Spotify(auth=token)
    # sp.trace = False
    #
    # top_tracks = sp.artist_top_tracks(artist_id)
    #
    # track = top_tracks['tracks'][0]
    #
    # artist = track['artists'][0]['name']
    # track_name = track['name']
    # track_uri = track['uri']
    #
    # return {"name":track_name, "uri":track_uri, "artist":artist}
    return ''
