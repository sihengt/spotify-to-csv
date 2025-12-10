from flask import Flask, redirect, request
import requests
import yaml
import random
import string
import urllib
import pandas as pd

REDIRECT_URI = "http://127.0.0.1:8000/callback"

"""
Returns access token if all is ok. Uses code.
"""
def login_to_spotify(code, client_id, client_secret):
    res = requests.post('https://accounts.spotify.com/api/token',
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={"grant_type": "authorization_code",
                          "redirect_uri": REDIRECT_URI,
                          "client_id": client_id,
                          "client_secret": client_secret,
                          "code": code})
    if res.ok:
        data = res.json()
        return data["access_token"]
    else:
        raise Exception(f"Error. Code obtained: {res}")

def get_all_playlists(access_token):
    res = requests.get('https://api.spotify.com/v1/me/playlists',
                       headers={"Authorization": f"Bearer {access_token}"})
    if res.ok:
        print(res.json())
        return res.json()
    else:
        print(f"Status code: {res.status_code}")
        print("die")

def generate_random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def main():
    # We need "secret.yaml"!
    with open("secret.yaml") as f:
        config = yaml.safe_load(f)
        CLIENT_ID = config['client_id']
        CLIENT_SECRET = config['client_secret']


    # 0. Authorization (https://developer.spotify.com/documentation/web-api/tutorials/code-flow)
    app = Flask(__name__)
    
    @app.route("/login")
    def login():
        state = generate_random_string(16)
        scope = 'playlist-read-private'

        query = {'response_type': 'code',
                 'client_id': CLIENT_ID,
                 'scope': scope,
                 'redirect_uri': REDIRECT_URI,
                 'state': state}
        
        auth_url = ("https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(query))
        return redirect(auth_url)
    
    @app.route("/callback")
    def callback():
        print("hello!")
        code = request.args.get('code')
        state = request.args.get('state')
        
        # 1. Get access token
        access_token = login_to_spotify(code, CLIENT_ID, CLIENT_SECRET)
        
        # 2. Get all playlists
        playlists_json = get_all_playlists(access_token)

        # 3. Process playlists
        tracks_dict = {'playlist':[], 'track':[], 'artist':[]}
        
        for playlist in playlists_json['items']:
            pl_name = playlist['name']
            pl_owner = playlist['owner']
            pl_public = playlist['public']
            # TODO: HARDCODED?!
            if pl_owner['id'] != 'tropicvelvet':
                continue
            
            pl_tracks = playlist['tracks']['href'] # this is a href link to the Web API endpoint where full details of the playlist's tracks can be retrieved.
            print(pl_tracks)
            res = requests.get(pl_tracks,
                    headers={"Authorization": f"Bearer {access_token}"})
            
            # iterate through res.json()['items']
            for song in res.json()['items']:
                # assume first artist is the main artist first.
                main_artist_name = song['track']['artists'][0]['name']
                track_name = song['track']['name']
                track_spotify_id = song['track']['id']
                tracks_dict['playlist'].append(pl_name)
                tracks_dict['track'].append(track_name)
                tracks_dict['artist'].append(main_artist_name)

        df = pd.DataFrame.from_dict(tracks_dict)
        df.to_csv("songs.csv", index=False)
        breakpoint()
        
        return f"Received code: {code}<br> State: {state}."



    app.run(port=8000, debug=True)



if __name__ == "__main__":
    main()
