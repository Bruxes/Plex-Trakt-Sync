# filename: test_trakt_config.py

import requests
import configparser
import os
import sys

# --- Configuration Loading ---
config = configparser.ConfigParser()
script_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, 'config.ini')

print("--- Running Trakt Configuration Test ---")

# 1. Check if config.ini exists
if not os.path.exists(config_path):
    print(f"❌ FAILURE: config.ini not found. Please make sure the file exists.")
    sys.exit(1)
print("✅ Found config.ini file.")
config.read(config_path)

# 2. Check for required keys
try:
    CLIENT_ID = config['Trakt']['ClientId']
    ACCESS_TOKEN = config['Trakt']['AccessToken']
    if 'YOUR_CLIENT_ID_HERE' in CLIENT_ID or not CLIENT_ID:
        print("❌ FAILURE: 'ClientId' in config.ini has not been set.")
        sys.exit(1)
    if not ACCESS_TOKEN:
        print("❌ FAILURE: 'AccessToken' in config.ini is empty.")
        print("   Please run 'get_trakt_token.py' to generate a token first.")
        sys.exit(1)
except KeyError as e:
    print(f"❌ FAILURE: Could not find key {e} in config.ini.")
    sys.exit(1)
print("✅ Found all required keys in config.ini.")

# 3. Test connection to Trakt API
print("▶️  Attempting to connect to Trakt API with your token...")

test_url = "https://api.trakt.tv/users/me"
headers = {
    'Content-Type': 'application/json',
    'trakt-api-version': '2',
    'trakt-api-key': CLIENT_ID,
    'Authorization': f"Bearer {ACCESS_TOKEN}"
}

try:
    response = requests.get(test_url, headers=headers)
    response.raise_for_status()
    
    user_data = response.json()
    username = user_data.get('username')
    
    print(f"✅ Successfully connected to Trakt API.")
    print("\n-----------------------------------------")
    print(f"🎉 SUCCESS! Your configuration is correct!")
    print(f"   Connected to Trakt as: {username}")
    print("-----------------------------------------")

except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print(f"❌ FAILURE: Connection failed with a 401 Unauthorized error.")
        print("   This means your AccessToken is incorrect, expired, or revoked.")
        print("   Please try running 'get_trakt_token.py' again to get a new token.")
    else:
        print(f"❌ FAILURE: An HTTP error occurred: {e}")
except requests.exceptions.RequestException as e:
    print(f"❌ FAILURE: A network error occurred. Could not connect to Trakt.")
    print(f"   Error: {e}")