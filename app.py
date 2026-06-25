from flask import Flask, render_template, redirect, request
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = 'http://127.0.0.1:5000/callback'
SPOTIFY_AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'

user_access_token = None

def create_playlist(playlist_name, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    url = 'https://api.spotify.com/v1/me/playlists'
    data = {'name': playlist_name}
    response = requests.post(url, headers=headers, json=data)
    return response.json() if response.status_code == 201 else None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/team")
def team():
    return render_template("team.html")

@app.route("/input")
def input():
    return render_template("input.html")

@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")


@app.route("/authorize_spotify")
def authorize_spotify():
    return redirect(
        f"{SPOTIFY_AUTHORIZE_URL}"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=playlist-modify-private%20playlist-modify-public"
    )

@app.route("/callback")
def callback():
    global user_access_token

    #authorization code from the Spotify callback
    code = request.args.get('code')

    response = requests.post(
        SPOTIFY_TOKEN_URL,
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        }
    )

    #extracting the access token, and store it
    if response.status_code == 200:
        data = response.json()
        user_access_token = data['access_token']

        return redirect("/input")
    else:
        response.raise_for_status()
        print(f"Error during authorization: {response.text}")
        return f"Error during authorization: {response.text}"

@app.route("/create_playlist", methods=['POST'])
def handle_playlist_creation():
    global user_access_token

    if user_access_token is not None:
        playlist_name = request.form.get('playlistName')
        playlist_genre = request.form.getlist('playlistGenre') 
        playlist_languages = request.form.getlist('playlistLanguages')  
        num_tracks = int(request.form.get('numTracks'))  
        release_year_start = request.form.get('releaseYearStart')  
        release_year_end = request.form.get('releaseYearEnd')  

        response = create_playlist(playlist_name, user_access_token)

        if response:
            playlist_id = response['id']

            tracks_to_add = []
            for genre in playlist_genre:
                for language in playlist_languages:
                    search_query = f"genre:{genre} artist:{language} year:{release_year_start}-{release_year_end}"
                    print(f"Search Query: {search_query}")

                    search_response = requests.get(
                        f"https://api.spotify.com/v1/search?q={search_query}&type=track&limit={num_tracks}",
                        headers={'Authorization': f'Bearer {user_access_token}'}
                    )
                    if search_response.status_code == 200:
                        tracks_data = search_response.json().get('tracks', {}).get('items', [])
                        print(f"Tracks Found: {len(tracks_data)}")
                        tracks_to_add.extend([track['uri'] for track in tracks_data])

            
            if len(tracks_to_add) > num_tracks:
                tracks_to_add = tracks_to_add[:num_tracks]

            
            if tracks_to_add:
                add_tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
                add_tracks_response = requests.post(
                    add_tracks_url,
                    headers={'Authorization': f'Bearer {user_access_token}', 'Content-Type': 'application/json'},
                    data=json.dumps({'uris': tracks_to_add})
                )

                if add_tracks_response.status_code == 201:
                    return f"Playlist '{playlist_name}' created and tracks added successfully!"
                else:
                    return "Playlist created, but failed to add tracks."
            else:
                return "No tracks found based on selected criteria."
        else:
            return "Failed to create the playlist."
    else:
        return "Access token not found."

if __name__ == "__main__":
    app.run(debug=True)