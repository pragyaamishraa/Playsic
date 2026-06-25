# 🎵 PlaySic

A personalised Spotify playlist curator that generates playlists based on your 
genre, language, and release year preferences — then adds them directly to your 
Spotify account.

Built as a college team project (2 members) using Agile methodology.

## Features
- Spotify OAuth 2.0 login and authorisation flow
- Custom playlist generation based on genre, language, and year range filters
- Automatic playlist creation directly in the user's Spotify account
- Multi-step form UI with validation

## Tech Stack
- **Backend:** Python, Flask
- **Auth:** Spotify Web API, OAuth 2.0
- **Frontend:** HTML, CSS, JavaScript

## My Contribution
I owned backend development — the Flask server, Spotify OAuth 2.0 integration, 
and playlist generation logic. Frontend UI was built by my teammate.

## Setup & Run Locally
1. Clone this repo
2. Create a `.env` file with your own Spotify API credentials:

SPOTIFY_CLIENT_ID=your_client_id_here

SPOTIFY_CLIENT_SECRET=your_client_secret_here
3. Install dependencies:
pip install -r requirements.txt
4. Run the app:
python app.py
5. Open `http://127.0.0.1:5000` in your browser

## Note
This project is not actively maintained and runs in Spotify's Development Mode,
meaning only whitelisted Spotify accounts can use it. Built as a college minor 
project (Sept–Nov 2023).