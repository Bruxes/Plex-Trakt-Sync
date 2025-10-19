# filename: trakt_sync.py (Tautulli Bug Workaround Version)

import requests
import configparser
import os
import sys
import argparse

# --- CONFIGURATION ---
config = configparser.ConfigParser()
script_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, 'config.ini')

def load_config():
    """Loads configuration from config.ini."""
    if not os.path.exists(config_path):
        print("🚨 Error: config.ini not found.")
        sys.exit(1)
    config.read(config_path)
    try:
        return {
            'client_id': config['Trakt']['ClientId'],
            'client_secret': config['Trakt']['ClientSecret'],
            'access_token': config['Trakt']['AccessToken'],
            'refresh_token': config['Trakt']['RefreshToken']
        }
    except KeyError as e:
        print(f"🚨 Error: Missing key {e} in config.ini.")
        sys.exit(1)

# --- TOKEN REFRESH LOGIC ---
def refresh_token(conf):
    """Uses the refresh token to get a new access token."""
    print("🔄 Access token might be expired. Attempting to refresh...")
    refresh_payload = {
        "refresh_token": conf['refresh_token'],
        "client_id": conf['client_id'],
        "client_secret": conf['client_secret'],
        "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
        "grant_type": "refresh_token"
    }
    response = requests.post("https://api.trakt.tv/oauth/token", json=refresh_payload)
    if response.status_code == 200:
        token_data = response.json()
        new_access_token = token_data['access_token']
        new_refresh_token = token_data['refresh_token']
        
        config.set('Trakt', 'AccessToken', new_access_token)
        config.set('Trakt', 'RefreshToken', new_refresh_token)
        with open(config_path, 'w') as configfile:
            config.write(configfile)
        
        print("✅ Token refreshed successfully.")
        return new_access_token
    else:
        print(f"🚨 FATAL: Could not refresh token. Please re-authenticate using get_trakt_token.py. Response: {response.text}")
        return None

# --- API FUNCTIONS ---
def make_api_request(method, url, headers, json_payload=None):
    """Makes an API request and handles token refresh automatically."""
    response_func = requests.post if method.lower() == 'post' else requests.get
    response = response_func(url, headers=headers, json=json_payload)

    if response.status_code == 401: # Token expired
        conf = load_config()
        new_token = refresh_token(conf)
        if new_token:
            headers['Authorization'] = f"Bearer {new_token}"
            return response_func(url, headers=headers, json=json_payload)
    return response

def search_media(headers, title, media_type='show'):
    """Searches for a show or movie on Trakt to get its IDs."""
    # Ensure media_type is either 'show' or 'movie' for the API call
    search_type = 'show' if media_type == 'show' else 'movie'
    print(f"🔎 Searching for {search_type} '{title}' on Trakt...")
    search_url = f"https://api.trakt.tv/search/{search_type}?query={requests.utils.quote(title)}"
    response = make_api_request('get', search_url, headers, None)
    
    if response.status_code == 200:
        results = response.json()
        if results:
            # Ensure the key exists before accessing
            result_key = search_type
            if result_key in results[0]:
                 first_result = results[0][result_key]
                 print(f"✅ Found '{first_result['title']}' (Year: {first_result.get('year', 'N/A')})")
                 return first_result
            else:
                 print(f"❌ Unexpected result format from Trakt search for '{title}'.")
                 return None

    print(f"❌ {search_type.capitalize()} '{title}' not found on Trakt.")
    return None

def scrobble_media(headers, media_object, media_type, season=None, episode=None):
    """Sends the scrobble (watch event) to Trakt."""
    scrobble_payload = { "progress": 100 }
    
    # Use 'show' even if Tautulli incorrectly sent 'episode'
    if media_type == 'show':
        scrobble_payload["show"] = { "ids": media_object['ids'] }
        scrobble_payload["episode"] = { "season": season, "number": episode }
        print(f"▶️  Syncing S{season:02d}E{episode:02d} to Trakt...")
    elif media_type == 'movie':
        scrobble_payload["movie"] = { "ids": media_object['ids'] }
        print(f"▶️  Syncing movie '{media_object['title']}' to Trakt...")
    else:
        print(f"🚨 Error: Unknown media type '{media_type}' for scrobbling.")
        return

    response = make_api_request('post', "https://api.trakt.tv/scrobble/stop", headers, scrobble_payload)
    if response.status_code == 201:
        print("🎉 Success! Media synced to Trakt.")
    else:
        print(f"💔 Error syncing media. Response: {response.text}")

def main():
    conf = load_config()
    parser = argparse.ArgumentParser(description="Syncs Plex watch history from Tautulli to Trakt.")
    # Allow 'episode' temporarily but treat it as 'show'
    parser.add_argument('--title', required=True, help="The title of the media.")
    parser.add_argument('--media_type', required=True, help="The type of media ('movie' or 'show').")
    parser.add_argument('--episode', type=int, help="The episode number (for shows).")
    parser.add_argument('--season', type=int, help="The season number (for shows).")

    args = parser.parse_args()
    
    # --- WORKAROUND FOR TAUTULLI BUG ---
    # If Tautulli sends 'episode', treat it as 'show'
    actual_media_type = 'show' if args.media_type == 'episode' else args.media_type
    if args.media_type == 'episode':
        print(f"ℹ️  Received '--media_type episode' from Tautulli, treating as 'show'.")
    # ------------------------------------

    print(f"\n🎬 Tautulli reported a watch for '{args.title}' ({args.media_type}).") # Log original value
    
    headers = {
        'Content-Type': 'application/json',
        'trakt-api-version': '2',
        'trakt-api-key': conf['client_id'],
        'Authorization': f"Bearer {conf['access_token']}"
    }

    # Find the media on Trakt first using the corrected media type
    media_data = search_media(headers, args.title, actual_media_type)
    
    if media_data:
        # Handle scrobbling using the corrected media type
        if actual_media_type == 'show':
            if args.season is not None and args.episode is not None:
                scrobble_media(headers, media_data, 'show', args.season, args.episode)
            else:
                print("🚨 Error: Missing season/episode number for a show scrobble.")
        elif actual_media_type == 'movie':
            scrobble_media(headers, media_data, 'movie')

if __name__ == "__main__":
    main()
