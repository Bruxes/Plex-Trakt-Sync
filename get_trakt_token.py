# filename: get_trakt_token.py

import requests
import configparser
import os
import sys
import webbrowser
import time

# --- CONFIGURATION ---
config = configparser.ConfigParser()
script_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, 'config.ini')

if not os.path.exists(config_path):
    print(f"🚨 Error: config.ini not found in the script's directory.")
    sys.exit(1)

config.read(config_path)

try:
    CLIENT_ID = config['Trakt']['ClientId']
    CLIENT_SECRET = config['Trakt']['ClientSecret']
    if 'YOUR_CLIENT' in CLIENT_ID or 'YOUR_CLIENT' in CLIENT_SECRET:
        raise KeyError
except KeyError:
    print("🚨 Error: Please fill in both your ClientId and ClientSecret in config.ini first.")
    sys.exit(1)
# ---------------------

TRAKT_API_URL = "https://api.trakt.tv"

# 1. Request a device code from Trakt
print("--- Trakt.tv Token Generation ---")
print("\nStep 1: Requesting a device code from Trakt...")
code_payload = {'client_id': CLIENT_ID}
code_response = requests.post(f"{TRAKT_API_URL}/oauth/device/code", json=code_payload)

if code_response.status_code != 200:
    print(f"🚨 Error: Could not get a device code from Trakt. Response: {code_response.text}")
    sys.exit(1)

code_data = code_response.json()
device_code = code_data['device_code']
user_code = code_data['user_code']
verification_url = code_data['verification_url']
interval = code_data['interval']
expires_in = code_data['expires_in']

# 2. Instruct the user to authorize the app
print("✅ Device code received.")
print("\nStep 2: Please authorize the application.")
print(f"   Go to the following URL in your browser: {verification_url}")
print(f"   And enter this code: {user_code}")
webbrowser.open(verification_url)

# 3. Poll for the token
print("\nStep 3: Waiting for you to authorize... (This might take a moment)")
start_time = time.time()
while time.time() - start_time < expires_in:
    token_payload = {
        'code': device_code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    token_response = requests.post(f"{TRAKT_API_URL}/oauth/device/token", json=token_payload)

    if token_response.status_code == 200:
        token_data = token_response.json()
        access_token = token_data['access_token']
        refresh_token = token_data['refresh_token']
        
        config.set('Trakt', 'AccessToken', access_token)
        config.set('Trakt', 'RefreshToken', refresh_token)
        with open(config_path, 'w') as configfile:
            config.write(configfile)
            
        print("\n🎉 SUCCESS! 🎉")
        print("Your Access Token and Refresh Token have been automatically saved to config.ini.")
        sys.exit(0)
    
    elif token_response.status_code == 400:
        is_pending = False
        try:
            if token_response.json().get('error') == 'pending':
                is_pending = True
        except requests.exceptions.JSONDecodeError:
            print("   ... (Received empty response, assuming 'pending' due to network environment) ...")
            is_pending = True
        
        if is_pending:
            print("   ...still waiting for authorization...")
            time.sleep(interval)
        else:
            print(f"\n🚨 ERROR! Received a 400 Bad Request that was not a 'pending' status: {token_response.text}")
            sys.exit(1)
    else:
        print(f"\n🚨 ERROR! An unexpected error occurred while polling for the token: {token_response.text}")
        sys.exit(1)

print("\n🚨 ERROR: Authorization timed out. Please run the script and try again.")