import requests
import json
import os
import time

spotify_base = "https://api.spotify.com/v1"

refresh_endpoint = "https://accounts.spotify.com/api/token"

playlist_id = os.environ["PLAYLIST_ID"] 

def refresh_token():
    headers = {
        "Authorization":os.environ["CLIENT_BASIC_AUTH"], 
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = "grant_type=refresh_token&refresh_token=" + os.environ["SFY_REFRESH_TOKEN"]
    resp = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    if resp.status_code == 200:
        return resp.json()
    else:
        print("error getting token {}".format(resp.status_code))

def client_creds():
    headers = {
        "Authorization":os.environ["CLIENT_BASIC_AUTH"], 
        "Content-Type": "application/x-www-form-urlencoded"
    }
    resp = requests.post("https://accounts.spotify.com/api/token", headers=headers, data="grant_type=client_credentials")
    if resp.status_code == 200:
        json = resp.json()
        print(json["access_token"])
        return json["access_token"]

def search(token, query):
    headers = {
        "Authorization":"Bearer " + token
    }
    resp = requests.get(spotify_base + "/search?q=" + query["keywords"] + "&type=" + query["type"], headers=headers)
    if resp.status_code == 200:
        json = resp.json()
        return json

def get_artist_top_tracks(token, id):
    headers = {
        "Authorization":"Bearer " + token
    }
    resp = requests.get(spotify_base + "/artists/" + id + "/top-tracks?country=FI", headers=headers)
    if resp.status_code == 200:
        return resp.json()

def add_tracks_to_playlist(auth_token, playlist_id, track_uris):
    headers = {
        "Authorization":"Bearer " + auth_token,
        "Content-Type": "application/json"
    }

    while len(track_uris) > 100:
        resp = requests.post(spotify_base + "/playlists/" + playlist_id + "/tracks", headers=headers, data=json.dumps({"uris": track_uris[0:99]}))        
        if resp.status_code == 201:
            print("added 100 tracks ")
        else:
            print("error adding 100 tracks to playlist. status {}".format(resp.status_code))
        del track_uris[0:99]
    
    resp = requests.post(spotify_base + "/playlists/" + playlist_id + "/tracks", headers=headers, data=json.dumps({"uris": track_uris}))        
    if resp.status_code == 201:
        print("added rest {} tracks ".format(len(track_uris)))
    else:
        print("error adding rest ({}) to playlist. status {}".format(len(track_uris), resp.status_code))


def read_artists(filename):
    with open(filename, "r") as file:
        return file.readlines()

client_token = client_creds()

track_uris = []
artists = read_artists("roskilde_2019.txt")
for a in artists:
    search_result = search(client_token, {"keywords":a.replace(" ", "%20"), "type":"artist"})
    time.sleep(.100)
    artist_items = search_result["artists"].get("items", [])
    if len(artist_items) > 0:
        tracks_result = get_artist_top_tracks(client_token, artist_items[0]["id"])
        for track in tracks_result["tracks"]:
            print("adding track {}, uri: {}".format(track["name"], track["uri"]))
            track_uris.append(track["uri"])
auth_json = refresh_token()
add_tracks_to_playlist(auth_json["access_token"], playlist_id, track_uris)


# print(json.dumps(tracks))