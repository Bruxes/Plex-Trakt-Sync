# Plex-Trakt-Sync

<img width="256" height="256" alt="image" src="https://github.com/user-attachments/assets/da29ce42-1321-44a5-9587-3d181c20ca20" />


A simple and robust Python script to automatically sync your Plex watch history to Trakt.tv, triggered by Tautulli.

This project is designed to be a user-friendly solution that handles both TV shows and movies, with automatic token refreshing to keep it running smoothly.

## Project Files

-   **`trakt_sync.py`**: The main script that Tautulli runs to sync watch history.
-   **`config.ini`**: The central configuration file. **This is the only file you need to edit.**
-   **`get_trakt_token.py`**: A helper script that you run once to automatically generate your API token.
-   **`test_trakt_config.py`**: A script to test your configuration and ensure everything is working.

## Features

-   **Automatic Scrobbling**: Syncs watched episodes and movies to Trakt in real-time.
-   **Handles Both Shows & Movies**: Correctly identifies and syncs both media types.
-   **Automatic Token Refresh**: If your access token expires, the script automatically gets a new one so it never stops working.
-   **Secure**: Keeps your API credentials separate from the main script in a `config.ini` file.
-   **Easy Setup**: A simple, guided process to get your tokens.

## Setup Instructions

### 1. Prerequisites

-   A working Plex Media Server and Tautulli instance.
-   Python 3 installed on the machine where Tautulli runs.
-   The `requests` library for Python. If you don't have it, install it:

    ```bash
    pip install requests

### 2. Get Your Trakt API Credentials

1.  Go to the Trakt API Applications page: **[https://trakt.tv/oauth/applications/new](https://trakt.tv/oauth/applications/new)**
2.  Fill in the form:
    -   **Name**: `Tautulli Sync` (or anything you like)
    -   **Redirect uri**: `urn:ietf:wg:oauth:2.0:oob`
3.  Click **SAVE APP**. You will now be shown your **Client ID** and **Client Secret**.
4.  Open the `config.ini` file from this repository.
5.  Copy your **Client ID** and **Client Secret** and paste them into the corresponding fields in `config.ini`. Save the file.

### 3. Generate Your Trakt API Token

1.  Run the `get_trakt_token.py` script from your terminal:

    ```bash
    python get_trakt_token.py

3.  The script will guide you. It will provide a code and open a URL in your browser.
4.  Enter the code on the Trakt website and authorize the application.
5.  Return to the terminal. The script will automatically detect the authorization and save your tokens to `config.ini`.

### 4. Verify Your Setup (Recommended)

Run the included test script to verify that your configuration is correct.

    python test_trakt_config.py

If successful, it will show a success message with your Trakt username.

### 5. Tautulli Configuration

1.  In Tautulli, go to **Settings > Notification Agents > Add a new notification agent** and select **Script**.
2.  **Configuration Tab:**
    -   **Script Folder**: Select the folder where you saved the scripts.
    -   **Script File**: Choose `trakt_sync.py`.
3.  **Triggers Tab:**
    -   Check the box for **Watched**.
4.  **Arguments Tab:**
    -   Go to the **Watched** section.
    -   In the text box, enter the following arguments:

    ```bash
    --title "{show_name}" --media_type "{media_type}" --season "{season_num}" --episode "{episode_num}"

## That's it!

Your setup is complete. The project is now fully configured and ready to sync your watch history.

---
## License
This project is licensed under the MIT License.
