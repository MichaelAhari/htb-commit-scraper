import spotipy
import spotipy.util as util
import os
import json
import requests
from random import randint

def spotifyConnect():
    username = 'michaelahari'
    scope = 'playlist-modify-public'
    token = util.prompt_for_user_token(username, scope)
    return token

def getTrack(playlist_id, token):

    #set up
    USER_ID="spotify"
    sp = spotipy.Spotify(auth=token)
    sp.trace = False

    #get tracks in playlist
    request = sp.user_playlist(USER_ID, playlist_id=playlist_id, fields="tracks")
    tracks = request['tracks']['items']
    item = randint(0,len(tracks)-1)

    #get tracks already in our playlist
    request = sp.user_playlist(USER_ID, playlist_id="0H8XxdGolLwGr45HVEU9Dm", fields="tracks")
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
    PLAYLIST_ID = "5B1sHuZjlgROjT54SjA1iP"
    TRACK_IDS = [track_id]

    sp = spotipy.Spotify(auth=token)
    sp.trace = False

    request = sp.user_playlist_add_tracks(USER_ID, PLAYLIST_ID, TRACK_IDS)
