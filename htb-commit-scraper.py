import json
import requests
from requests_oauthlib import OAuth2Session
from flask.json import jsonify
import os
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import dateutil.parser
import datetime
import pytz
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from flask import make_response

#import spotify python api
import spotipy
import spotipy.util as util


# create application
app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:htbcommitscraper@178.62.99.27/users'
db.init_app(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(30))
    oauthkey = db.Column(JSON)
    repo = db.Column(db.String(30))
    owner = db.Column(db.String(30))

    def __init__(self, login, oauthkey, repo, owner):
        self.login = login
        self.oauthkey = oauthkey
        self.repo = repo
        self.owner = owner

    def __repr__(self):
        return '<User %r>' % self.login

#create database
db.create_all()


client_id = "f9ba003f3e1eba4ff7f5"
client_secret = "78dc535324b5e6fd8699748df2140f268147a8e4"
authorization_base_url = 'https://github.com/login/oauth/authorize'
token_url = 'https://github.com/login/oauth/access_token'
redirect_uri = 'http://localhost:5000/callback'


@app.route("/")
def home():


#    if 'oauth' in request.cookies:
#        return redirect(url_for('callback'))
#    else:

    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. Github)
    using an URL with a few key OAuth parameters.
    """
    github = OAuth2Session(client_id, redirect_uri=redirect_uri, scope = ['repo'])
    authorization_url, state = github.authorization_url(authorization_base_url)

    # State is used to prevent CSRF, keep this for later
    session['oauth_state'] = state
    return redirect(authorization_url)
    response = make_response(redirect(authorization_url))
    response.set_cookie('oauth_state', state)
    return response

# Step 2: User authorization, this happens on the provider.

@app.route("/callback", methods=["GET", "POST"])
def callback():

    #if 'oauth_state' not in request.cookies:
    #    return redirect(url_for('home'))
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """

    github = OAuth2Session(client_id, state=session['oauth_state'])
    token = github.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url)

    #session['oauth_token'] = token

    # At this point you can fetch protected resources but lets save
    # the token and show how this is done from a persisted token
    # in /profile.
    session['oauthkey'] = token
    OAUTH_KEY = token

    #authorise user using token
    github = OAuth2Session(client_id, token=OAUTH_KEY)

    #get user details including username and repo
    user_info = github.get('https://api.github.com/user')
    json_ui = user_info.json()

    LOGIN = json_ui['login']
    session['login'] = LOGIN

    #get repos
    repo_info = github.get('https://api.github.com/user/repos')

    """Get the most recent repository using created_at key"""
    dates = []
    for repo in repo_info.json():
        #add date of creation to list, converting from ISO8601 to datetime python type
        dates.append(dateutil.parser.parse(repo['created_at']))

    current_date = datetime.datetime.now(pytz.utc)
    DATE_CREATED = max(date for date in dates if date < current_date)

    #get latest repo name
    for repo in repo_info.json():
        if dateutil.parser.parse(repo['created_at']) == DATE_CREATED:
            REPO = repo['name']
            session['repo'] = REPO
            OWNER = repo['owner']['login']
            session['owner'] = OWNER

    #add record to database
    new_record = User(LOGIN, OAUTH_KEY, REPO, OWNER)

    User.query.filter_by(login=LOGIN).delete()

    db.session.add(new_record)
    db.session.commit()

    response = make_response(redirect(url_for('commits')))
    response.set_cookie('oauth', 'authorized')
    return response

@app.route("/commits", methods=["GET", "POST"])
def commits():


    """refreshes token"""
    User.query.filter_by(login=session['login']).delete()


    new_record = User(session['login'], session['oauthkey'], session['repo'], session['owner'])

    db.session.add(new_record)
    db.session.commit()


    #get all users from database
    users = User.query.all()

    for user in users:

        LOGIN = user.login
        OAUTH_KEY = user.oauthkey
        REPO = user.repo
        OWNER = user.owner

        """Get latest commit to REPO"""
        github = OAuth2Session(client_id, token=OAUTH_KEY)
        commit = (github.get('https://api.github.com/repos/%s/%s/commits/master' % (OWNER, REPO))).json()
        commit_date = dateutil.parser.parse(commit['commit']['author']['date'])

        #check if commit has been made in the last 5 minutes
        current_date = datetime.datetime.now(pytz.utc)
        if (commit_date - current_date).total_seconds() < (5*60):
            MESSAGE = commit['commit']['message']

        #connect to spotify API
        SPOTIFY_BASE_URL = 'https://api.spotify.com'
        TRACK = '2kli84TSRXN5XoGsY75Nan'
        requests.post(SPOTIFY_BASE_URL + '/v1/users/michaelahari/playlists/5B1sHuZjlgROjT54SjA1i/'+'{"uris": ["spotify:track:0r4SsYcwvd8URat6AS2m6f"]}')

    return MESSAGE

@app.route("/spotify", methods=["GET", "POST"])
def spotify():



    return ''

@app.route("/spotifycallback", methods=["GET", "POST"])
def spotify_callback():

    return 'Success!'

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.secret_key = os.urandom(24)
    app.run(debug=True)
