from slacker import Slacker
import urllib3.contrib.pyopenssl
import time
import psycopg2
from nltk.tokenize import TweetTokenizer
import nltk
import requests
import json

import spotify_connect

def slackPost(message):
    #avoid insecure https requests because of python version 2.7
    urllib3.contrib.pyopenssl.inject_into_urllib3()

    #open connection to slack team
    slack = Slacker('xoxp-22587310162-22583961635-22592796609-102d04a936')

    # Send a message to #general channel
    slack.chat.post_message('#general', message, None, as_user=True)

def getCommit(table_row):
    conn = psycopg2.connect(database="users", user="postgres", password="htbcommitscraper", host="178.62.99.27", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT * from gitcommits WHERE id=" + str(table_row))
    rows = cur.fetchall()
    if len(rows) == 1:
        return row[0]
    else :
        return False
        #do nothing since no new commits have been made

#credits - Andreea, Ramona, Andra
#not working very well with coefficient at the moment need to find new solution
def parseCommitMessage(message):
    # using the Sentiment Analysis API
    url = "http://text-processing.com/api/sentiment/"

    #tokenize the message
    tokenizer = TweetTokenizer()
    tokens = tokenizer.tokenize(message)

    coefficient = 0
    num_neutral = 0
    for token in tokens:

        request = requests.post(url,data="text="+token).json()
        if request['label'] == "neutral":
            coefficient /= 5
            num_neutral += 1
        else :
            pos = request['probability']['pos']
            neg = request['probability']['neg']
            coefficient += 100 * (pos - neg)

    if coefficient >= 0.5 * 100 * len(tokens):
        return {"on top of the world", "unstoppable", "excited"}
    elif coefficient >= 0.2 * 100 * len(tokens):
        return {"feel good", "happy", "fun"}
    elif coefficient >= 0.1 * 100 * len(tokens):
        return {"productive", "work", "focus"}
    elif coefficient > 0:
        return {"chilled, relax, calm"}
    elif coefficient > -0.05 * 100 * len(tokens):
        return {"unhappy, sad"}
    elif coefficient > -0.1 * 100 * len(tokens):
        return {"frustrated", "annoyed", "angry"}
    else:
        return {"irritated", "furious", "disheartened"}


def getSpotifyTrack(keywords):
    return ''

def createSlackMessage(username, message, track_name, track_artist):
    message = "New track on the playlist! \"%s\" by %s. This one\'s for %s, who is feeling %s with their latest commit." % (track_name, track_artist, username, message)
    return message

def main():
    table_row = 1
    while 1:
        time.sleep(5*60)
        commit = getCommit(table_row)
        keywords = parseCommitMessage(commit[3])
        track_name, track_artist = getSpotifyTrack(keywords)
        message = createSlackMessage(commit[1],keywords, track_name, track_artist)
        slackPost(message)
        row += 1

# if __name__ == "__main__":
#     main()
