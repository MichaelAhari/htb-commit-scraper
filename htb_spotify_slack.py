from slacker import Slacker
import urllib3.contrib.pyopenssl
import time
import psycopg2
from nltk.tokenize import TweetTokenizer
import nltk
import requests
import json
import spotipy
import spotipy.util as util
import os

from spotifyconnect import spotifyConnect, getTrack, addTrack

def getCommit(table_row):
    conn = psycopg2.connect(database="***", user="***", password="***", host="***", port="***")
    cur = conn.cursor()
    cur.execute("SELECT * from gitcommits WHERE id=" + str(table_row))
    rows = cur.fetchall()
    if len(rows) == 1:
        return rows[0]
    else :
        return False
        #do nothing since no new commits have been made

#credits - Andreea, Ramona, Andra who developed this at StacsHack 2016
def parseCommitMessage(message):
    # using the Sentiment Analysis API
    url = "http://text-processing.com/api/sentiment/"

    request = requests.post(url,data="text="+message)
    if request.status_code == 200:
        request = json.loads(request.text)
        if request['label'] == "pos":
            if float(request['probability']['pos']) >= 0.8:
                return "confidence boost"
            elif float(request['probability']['pos']) >= 0.7:
                return "great day"
            elif float(request['probability']['pos']) >= 0.6:
                return "feeling good"
            else:
                return "good vibes"

        elif request['label'] == "neg":
            if float(request['probability']['neg']) >= 0.8:
                return "breakup songs"
            elif float(request['probability']['neg']) >= 0.7:
                return "stress buster"
            elif float(request['probability']['neg']) >= 0.6:
                return "life sucks"
            else:
                return "badass"

        else:
            if float(request['probability']['neutral']) >= 0.7:
                return "peaceful piano"
            else:
                return "tropical house"
    else:
        return "tropical house"

def addSpotifyTrack(playlist_info):
    token = spotifyConnect()

    track = getTrack(playlist_info, token)

    track_uri = track['track']['uri']

    addTrack(track_uri, token)

    track_name = track['track']['name']

    return track_name


def createSlackMessage(username, message, track_name):
    message = "New track on the playlist: \"%s\". This one is for %s, who is feeling %s." % (track_name, username, message)
    return message

def slackPost(message):
    # #avoid insecure https requests because of python version 2.7
    # urllib3.contrib.pyopenssl.inject_into_urllib3()
    #
    # #open connection to slack team
    # slack = Slacker('xoxp-22587310162-22583961635-22592796609-102d04a936')
    #
    # # Send a message to #general channel
    # slack.chat.post_message('#general', message, None, as_user=True)


    #set up call to slack webhook
    json_data={"channel": "#spotify", "text":message,"username":"SpotifyBot","icon_emoji": ":spotify:"}
    url = "***" # hack the burgh group, #spotify channel
    #url = "***"

    post = requests.post(url, data=json.dumps(json_data))

def main():
    """Set up enviroment variables for spotify api"""
    os.environ['SPOTIPY_CLIENT_ID']='***'
    os.environ['SPOTIPY_CLIENT_SECRET']='***'
    os.environ['SPOTIPY_REDIRECT_URI']=('http://michaelahari.co.uk/spotifycallback').encode('utf-8')

    playlists = {"confidence boost":{"playlist_id": "0Vib1QAMtMaiywa3QSEq40","artist":"spotify","sentiment":"on top of the world"},
                "feeling good":{"playlist_id":"1B9o7mER9kfxbmsRH9ko4z","artist":"spotify", "sentiment":"good"},
                "great day":{"playlist_id":"2PXdUld4Ueio2pHcB6sM8j","artist":"spotify", "sentiment":"great"},
                "good vibes":{"playlist_id":"3xgbBiNc7mh3erYsCl8Fwg", "artist":"spotify", "sentiment":"those good vibes"},
                "breakup songs":{"playlist_id":"6dm9jZ2p8iGGTLre7nY4hf", "artist":"sonymusic", "sentiment":"sad"},
                "stress buster":{"playlist_id":"6JC48D3eRvkUHACDtyu0Gs","artist":"spotify_uk_", "sentiment":"stressed"},
                "life sucks":{"playlist_id":"5eSMIpsnkXJhXEPyRQCTSc", "artist":"spotify", "sentiment":"down"},
                "badass":{"playlist_id":"3V1WI57CMyQdmxy3aibCB4", "artist":"spotify_uk_", "sentiment":"badass"},
                "peaceful piano":{"playlist_id":"63dDpdoVHvx5RkK87g4LKk", "artist":"spotify", "sentiment":"peaceful"},
                "brain food":{"playlist_id":"67nMZWgcUxNa5uaiyLDR2x", "artist":"spotify", "sentiment":"productive"},
                "afternoon acoustic":{"playlist_id":"16BpjqQV1Ey0HeDueNDSYz", "artist":"spotify", "sentiment":"chilled"},
                "tropical house":{"playlist_id":"5IqZyShbVqwR9GQ1FVmHCT","artist":"spotify_uk_", "sentiment":"upbeat"}}

    table_row = 0
    while True:
        table_row = table_row + 1
        time.sleep(5*60)
        commit = getCommit(table_row)
        if commit:
            sentiment = parseCommitMessage(commit[3])
            track_name = addSpotifyTrack(playlists[sentiment])
            message = createSlackMessage(commit[1],playlists[sentiment]["sentiment"], track_name)
            slackPost(message)
        table_row += 1

if __name__ == "__main__":
    main()
