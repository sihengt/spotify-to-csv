import requests
from flask import Flask
import yaml

with open("secret.yaml") as f:
    config = yaml.safe_load(f)
    CLIENT_ID = config['client_id']
    CLIENT_SECRET = config['client_secret']



"""
Returns access token if all is ok
"""
def login(client_id, client_secret):
    res = requests.post('https://accounts.spotify.com/api/token',
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={"grant_type": "client_credentials",
                            "client_id": client_id,
                            "client_secret": client_secret})
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
    else:
        print(f"Status code: {res.status_code}")
        print("die")

def main():
    # 1. Get access token
    access_token = login(CLIENT_ID, CLIENT_SECRET)
    
    # 2. Get all playlists
    get_all_playlists(access_token)
    

if __name__ == "__main__":
    main()
