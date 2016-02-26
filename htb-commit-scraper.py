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


# create application
app = Flask(__name__)
app.config.from_object(__name__)

client_id = "f9ba003f3e1eba4ff7f5"
client_secret = "78dc535324b5e6fd8699748df2140f268147a8e4"
authorization_base_url = 'https://github.com/login/oauth/authorize'
token_url = 'https://github.com/login/oauth/access_token'
redirect_uri = 'http://localhost:5000/callback'

tokens = []

@app.route("/")
def demo():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. Github)
    using an URL with a few key OAuth parameters.
    """
    github = OAuth2Session(client_id, redirect_uri=redirect_uri, scope = ['repo'])
    authorization_url, state = github.authorization_url(authorization_base_url)

    # State is used to prevent CSRF, keep this for later
    session['oauth_state'] = state
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.

@app.route("/callback", methods=["GET"])
def callback():
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """

    github = OAuth2Session(client_id, state=session['oauth_state'])
    token = github.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)

    session['oauth_token'] = token

    # At this point you can fetch protected resources but lets save
    # the token and show how this is done from a persisted token
    # in /profile.

    return redirect(url_for('commits'))
    #return json_r['commit']['author']['date']
    #return ''#json_r['commit']['author']['date']


    #print session['oauth_token']
    #add token to list of tokens
    #tokens.append(token)

    #return redirect(url_for('commits'))

@app.route("/commits", methods=["GET"])
def commits():
    OAUTH_KEY = session['oauth_token']
    OWNER = ''
    REPO = ''

    #authorise user using token
    github = OAuth2Session(client_id, token=OAUTH_KEY)

    #get user details including username and repo
    user_info = github.get('https://api.github.com/user')
    json_ui = user_info.json()

    OWNER = json_ui['login']

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

    #REPO = latest_repo['name']

    """Get latest commit to REPO"""
    commit = (github.get('https://api.github.com/repos/%s/%s/commits/master' % (OWNER, REPO))).json()

    commit_date = dateutil.parser.parse(commit['commit']['author']['date'])

    #check if commit has been made in the last 5 minutes
    if (commit_date - current_date).total_seconds() < (5*60):
        commit_message = commit['commit']['message']
        session['commit_message'] = commit_message


    return commit_message
if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.secret_key = os.urandom(24)
    app.run(debug=True)
