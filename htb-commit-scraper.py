
from requests_oauthlib import OAuth2Session
from flask.json import jsonify
import os
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash


# create application
app = Flask(__name__)
app.config.from_object(__name__)

client_id = "f9ba003f3e1eba4ff7f5"
client_secret = "78dc535324b5e6fd8699748df2140f268147a8e4"
authorization_base_url = 'https://github.com/login/oauth/authorize'
token_url = 'https://github.com/login/oauth/access_token'

tokens = []

@app.route("/")
def demo():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. Github)
    using an URL with a few key OAuth parameters.
    """
    github = OAuth2Session(client_id, scope = ['repo'])
    authorization_url, state = github.authorization_url(authorization_base_url)

    # State is used to prevent CSRF, keep this for later.
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
    token = json.load(github.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url))

    # At this point you can fetch protected resources but lets save
    # the token and show how this is done from a persisted token
    # in /profile.
    session['oauth_token'] = token

    #add token to list of tokens
    tokens.append(token)

    return redirect('http://localhost:5000/commits')

@app.route("/commits")
def commits():
    return ''

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True)
