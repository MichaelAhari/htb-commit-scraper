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
import urllib

from spotifyconnect import spotifyConnect, addTrack, searchArtist, getArtistTrack

#import spotify python api
import spotipy
import spotipy.util as util


# create application
app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:htbcommitscraper@178.62.99.27/users'
app.config['DEBUG'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = os.urandom(24)

db.init_app(app)


from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

class LoginForm(Form):
    reponame = StringField('reponame', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class User(db.Model):
    __tablename__ = 'gitusers'
    id = db.Column(db.Integer, primary_key=True)
    repo = db.Column(db.String(30))
    owner = db.Column(db.String(30))

    def __init__(self, repo, owner):
        self.repo = repo
        self.owner = owner

    def __repr__(self):
        return '<User %r>' % self.owner

class Commit(db.Model):
    __tablename__ = 'gitcommits'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    repo = db.Column(db.String(30))
    message = db.Column(db.String(120))

    def __init__(self, username, repo, message):
        self.username = username
        self.repo = repo
        self.message = message

    def __repr__(self):
        return '<User %r>' % self.login

#create database
db.create_all()


client_id = "f9ba003f3e1eba4ff7f5"
client_secret = "78dc535324b5e6fd8699748df2140f268147a8e4"
authorization_base_url = 'https://github.com/login/oauth/authorize'
token_url = 'https://github.com/login/oauth/access_token'
redirect_uri = 'https://hacktheburgh.michaelahari.co.uk/callback'
#redirect_uri = 'http://localhost:5000/callback'

@app.route("/", methods=["GET","POST"])
def home():


#    if 'oauth' in request.cookies:
#        return redirect(url_for('callback'))
#    else:

    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. Github)
    using an URL with a few key OAuth parameters.
    """
    #get token and create authorized session
    github = OAuth2Session(client_id, redirect_uri=redirect_uri, scope = ['write:repo_hook, repo'])
    authorization_url, state = github.authorization_url(authorization_base_url)
    # State is used to prevent CSRF, keep this for later
    session['oauth_state'] = state
    return redirect(authorization_url)

# Step 2: User authorization, this happens on the provider.

@app.route("/callback", methods=["GET", "POST"])
def callback():

    """Get REPO name from user"""
    #form = LoginForm()
    #if form.validate_on_submit():

    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """

    #check if repo is valid repo
    github = OAuth2Session(client_id, state=session['oauth_state'])
    token = github.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url)

    session['token'] = token
    session['token'].permanent = True

    return redirect(url_for('form'))

@app.route("/form", methods=["GET","POST"])
def form():
    error=None
    if not session.has_key('token'):
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():

        OAUTH_KEY = session['token']
        github = OAuth2Session(client_id, token=OAUTH_KEY)

        """check if repo exits"""
        #get user details including username and repo
        user_info = github.get('https://api.github.com/user')
        json_ui = user_info.json()

        OWNER = json_ui['login']

        REPO = form.reponame.data

        #check if repo already exists in database
        if User.query.filter_by(repo=REPO,owner=OWNER).count() > 0:
            error = "Looks like you already registered that repo!"
            return render_template('form.html',title='Sign up', form=form,error=error)

        #get repo
        repo_info = github.get('https://api.github.com/repos/%s/%s' % (OWNER, REPO))

        if repo_info.status_code == 200:

            #add user to table
            new_record = User(REPO, OWNER)#params: login,repo,owner
            db.session.add(new_record)
            db.session.commit()

            """Create webhook"""
            # POST /repos/:owner/:repo/hooks
            json_data = {"name": "web",
                            "active": True,
                            "events": ["push"],
                            "config": {"url": "http://hacktheburgh.michaelahari.co.uk/webhook","content_type":"json", "insecure_ssl":1}}


            create_hook = github.post('https://api.github.com/repos/%s/%s/hooks' % (OWNER,REPO),data=json.dumps(json_data))

            if create_hook.status_code == 201:
                flash('Tracking commits to git repo:"%s"' % (form.reponame.data))
                return redirect(url_for('valid', repo=REPO, owner=OWNER))
        else:
            error = "We couldn't find a matching repository you own"
            return render_template('form.html',title='Sign up', form=form,error=error)

    return render_template('form.html',title='Sign up', form=form,error=error)




@app.route("/valid",methods=["GET","POST"])
def valid():

    if request.args.get("repo") == None:
        return redirect(url_for('home'))

    REPO = request.args.get("repo")
    OWNER = request.args.get("owner")

    return render_template('valid.html', title='Awesome!', repo=REPO, owner=OWNER)

    #return "Woo it works up to here"

# @app.route("/commits", methods=["GET", "POST"])
# def commits():


    # """refreshes token"""
    # User.query.filter_by(login=session['login']).delete()
    #
    #
    # new_record = User(session['login'], session['oauthkey'], session['repo'], session['owner'])
    #
    # db.session.add(new_record)
    # db.session.commit()
    #
    #
    # #get all users from database
    # users = User.query.all()
    #
    # for user in users:
    #
    #     LOGIN = user.login
    #     OAUTH_KEY = user.oauthkey
    #     REPO = user.repo
    #     OWNER = user.owner
    #
    #     """Get latest commit to REPO"""
    #     github = OAuth2Session(client_id, token=OAUTH_KEY)
    #     commit = (github.get('https://api.github.com/repos/%s/%s/commits/master' % (OWNER, REPO))).json()
    #     commit_date = dateutil.parser.parse(commit['commit']['author']['date'])
    #
    #     #check if commit has been made in the last 5 minutes
    #     current_date = datetime.datetime.now(pytz.utc)
    #     if (commit_date - current_date).total_seconds() < (5*60):
    #         MESSAGE = commit['commit']['message']
    #
    #     #connect to spotify API
    #     SPOTIFY_BASE_URL = 'https://api.spotify.com'
    #     TRACK = '2kli84TSRXN5XoGsY75Nan'
    #     requests.post(SPOTIFY_BASE_URL + '/v1/users/michaelahari/playlists/5B1sHuZjlgROjT54SjA1i/'+'{"uris": ["spotify:track:0r4SsYcwvd8URat6AS2m6f"]}')
    #
    # return MESSAGE

@app.route("/webhook", methods=["GET","POST"])
def webhook():

    if request.headers.get('X-GitHub-Event') == "push":
        json_data = json.loads(request.data)
        USERNAME = json_data['head_commit']['author']['username']
        REPO = json_data['repository']['name']
        MESSAGE = json_data['head_commit']['message']

        #set up call to slack webhook
        text = "*" + USERNAME + "* just pushed a commit to `" + REPO + "`: _\"" + MESSAGE + "\"_"
        json_data={"text":text,"username":REPO,"icon_emoji": ":octocat:"}
        url = "https://hooks.slack.com/services/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" # hack the burgh group, #github channel
        #url = "https://hooks.slack.com/services/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"

        post = requests.post(url, data=json.dumps(json_data))

        #write commit to database
        new_record = Commit(USERNAME, REPO, MESSAGE)#params: username,repo,message
        db.session.add(new_record)
        db.session.commit()
    return ''


# @app.route("/spotifyrequest", methods=["GET","POST"])
# def spotifyrequest():
#
#     json_data = request.data
#     # if json_data['token'] == "jYmxefM3gQ7KsykEcTljri07":
#     #     SEARCH_TERM = json_data['text'][10:]
#     #     artist_id = searchArtist(SEARCH_TERM)
#     #     if artist_id == False:
#     #         return ''#do nothing
#     #     token = spotifyConnect()
#     #     track_info = getArtistTrack(artist_id,token)
#     #     addTrack(track_info['uri'], token)
#     #
#     #     #set up call to slack webhook
#     #     text = "Request from " + json_data['user_name'] + " approved!" + "New track on the playlist: " + track_info['name'] + " by " + track_info['artist']
#     #     json_data={"channel":"#spotify", "text":text,"username":"SpotifyBot","icon_emoji": ":spotify:"}
#     #     url = "https://hooks.slack.com/services/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"
#
#         #return ''
#     return ''

if __name__ == '__main__':
    app.run(debug=True)
