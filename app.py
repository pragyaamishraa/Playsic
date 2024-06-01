from flask import Flask, render_template, redirect, request
import requests
import json
app = Flask(__name__)

CLIENT_ID = '071e87f9bc66436889c57d3af513e1fb'
CLIENT_SECRET = 'ee4db2057c354787a94c0408a9aa9525'
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

if __name__ == "_main_":
    app.run(debug=True)

"""
from flask import Flask, render_template, redirect, request
import requests
import json

app = Flask(__name__)

CLIENT_ID = '071e87f9bc66436889c57d3af513e1fb'
CLIENT_SECRET = 'ee4db2057c354787a94c0408a9aa9525'
REDIRECT_URI = 'http://127.0.0.1:5000/callback'
SPOTIFY_AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'

user_access_token = None

@app.route("/create_playlist", methods=['POST'])
def create_playlist():
    playlist_name = request.form.get('playlistName')
    playlist_genre = request.form.get('playlistGenre')
    num_tracks = request.form.get('numTracks')
    playlist_languages = request.form.getlist('playlistLanguages')

    print(f"Received form data: {playlist_name}, {playlist_genre}, {num_tracks}, {playlist_languages}")

    if user_access_token:
        print(f"User Access Token: {user_access_token}")

        create_playlist_url = 'https://api.spotify.com/v1/me/playlists'

        headers = {
            'Authorization': f'Bearer {user_access_token}',
            'Content-Type': 'application/json',
        }

        playlist_data = {
            'name': playlist_name,
            'description': f'A playlist of {playlist_genre} songs in {", ".join(playlist_languages)}',
            'public': True
        }

        print(f"Playlist Data: {playlist_data}")

        response = requests.post(create_playlist_url, headers=headers, data=json.dumps(playlist_data))

        # Print the response details for debugging
        print(f"Playlist Creation - Response Status Code: {response.status_code}")
        print(f"Playlist Creation - Response Body: {response.text}")

        if response.status_code == 201:
            return "Playlist created successfully!"  # You might want to redirect or render a success page
        else:
            return f"Failed to create playlist: {response.text}"
    else:
        return "Access token not found. Please authenticate with Spotify first."


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

    code = request.args.get('code')

    print(f"Received authorization code: {code}")

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

    # Handle the response, extract the access token, and store it
    if response.status_code == 200:
        data = response.json()
        user_access_token = data.get('access_token')

        # Print or log the obtained access token for debugging
        print(f"Obtained access token: {user_access_token}")

        # Redirect the user to the "input" page after obtaining the access token
        return redirect("/input")
    else:
        response.raise_for_status()
        print(f"Error during authorization: {response.text}")
        return f"Error during authorization: {response.text}"



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


if __name__ == "__main__":
    debug=True

"""
'''
from flask import Flask, render_template, redirect, request
import requests
import os
import json

app = Flask(__name__)

CLIENT_ID = os.environ.get('071e87f9bc66436889c57d3af513e1fb')
CLIENT_SECRET = os.environ.get('ee4db2057c354787a94c0408a9aa9525')
REDIRECT_URI = 'http://127.0.0.1:5000/callback'

SPOTIFY_API_CONFIG = {
    'authorize_url': 'https://accounts.spotify.com/authorize',
    'token_url': 'https://accounts.spotify.com/api/token',
}

# This variable will store the user's access token
user_access_token = None

# Function to create a playlist on the user's Spotify account
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

@app.route("/authorize_spotify")
def authorize_spotify():
    return redirect(
        f"{SPOTIFY_API_CONFIG['authorize_url']}"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=playlist-modify-private%20playlist-modify-public"
    )

@app.route("/callback")
def callback():
    global user_access_token

    # Get the authorization code from the Spotify callback
    code = request.args.get('code')

    # Exchange the authorization code for access and refresh tokens
    response = requests.post(
        SPOTIFY_API_CONFIG['token_url'],
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        }
    )


    # Handle the response, extract the access token, and store it
    if response.status_code == 200:
        data = response.json()
        user_access_token = data['access_token']

        # For now, simply print the access token to the console
        print(f"Access Token: {user_access_token}")

        # You can redirect the user to another page or perform additional actions here
        return "Access Token obtained successfully!"
    else:
        response.raise_for_status()
        print(f"Error during authorization: {response.text}")
        return f"Error during authorization: {response.text}"


@app.route("/user_profile")
def user_profile():
    global user_access_token

    # Make a request to the Spotify API to get the user's profile information
    headers = {'Authorization': f'Bearer {user_access_token}'}
    response = requests.get('https://api.spotify.com/v1/me', headers=headers)

    if response.status_code == 200:
        data = response.json()
        user_access_token = data['access_token']
        print(f"Access Token: {user_access_token}")

    # ... rest of the code
    else:
        print(f"Error during authorization: {response.text}")
        return f"Error during authorization: {response.text}"

@app.route("/user_profile")
def user_profile_route():
    global user_access_token

    # Make a request to the Spotify API to get the user's profile information
    headers = {'Authorization': f'Bearer {user_access_token}'}
    response = requests.get('https://api.spotify.com/v1/me', headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        user_display_name = user_data.get('display_name', 'Unknown User')
        return f"Welcome, {user_display_name}!"
    else:
        print(f"Error retrieving user profile: {response.text}")
        return f"Error retrieving user profile: {response.text}"

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/team")
def team():
    return render_template("team.html")

@app.route("/input")
def input():
    return render_template("input.html")

@app.route("/create_playlist", methods=['POST'])
def handle_playlist_creation():
    global user_access_token

    if user_access_token is not None:
        playlist_name = request.form.get('playlistName')
        response = create_playlist(playlist_name, user_access_token)

        if response:
            return f"Playlist '{playlist_name}' created successfully!"
        else:
            return "Failed to create the playlist."
    else:
        return "Access token not found."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)'''