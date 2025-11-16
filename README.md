# Plex-Trakt-Sync

<p align="center">
  <img src="https://github.com/user-attachments/assets/da29ce42-1321-44a5-9587-3d181c20ca20?raw=true" width="250" alt="Trakt & Plex Integration">
</p>

A modern and robust Python script to automatically scrobble your watched movies and TV shows from Plex to Trakt.tv, triggered by Tautulli.

This project is designed to be a user-friendly solution. **You only need to edit the `config.ini` file to get started.**

## Project Files

-   **`trakt_sync.py`**: The main script that Tautulli will run.
-   **`config.ini`**: The central configuration file. **This is the only file you need to edit.**
-   **`get_trakt_token.py`**: A helper script that you run once to automatically generate your API token.
-   **`test_trakt_config.py`**: A test script to help you know if you did everything correctly.

## Setup Instructions

Follow these steps carefully. The entire configuration is handled in the `config.ini` file.

### 1. Prerequisites

-   A working Plex Media Server and Tautulli instance.
-   Python 3 installed on the machine where Tautulli runs.
-   The `requests` library for Python. If you don't have it, install it:

    pip install requests

### 2. Generate Your Trakt API Token (One-Time Setup)

This process uses the `get_trakt_token.py` script to automatically generate and save your token.

**Step 2.1: Get Your Client ID and Secret**
1.  Go to the Trakt API Applications page: **[https://trakt.tv/oauth/applications/new](https://trakt.tv/oauth/applications/new)**
2.  Fill in the form:
    -   **Name**: `Tautulli Sync` (or anything you like)
    -   **Redirect uri**: `urn:ietf:wg:oauth:2.0:oob`
3.  Click **SAVE APP**. You will now be shown your **Client ID** and **Client Secret**.
4.  Open the `config.ini` file from this repository.
5.  Copy your **Client ID** and **Client Secret** and paste them into the corresponding fields in `config.ini`. Save the file.

**Step 2.2: Run the Token Generation Script**
1.  Now, run the `get_trakt_token.py` script from your terminal:

    python get_trakt_token.py

2.  The script will give you a code and open a URL in your browser.
3.  Enter the code on the Trakt website and authorize the application.
4.  Return to the terminal. The script will automatically detect the authorization and save your tokens to `config.ini`.

### 3. Verify Your Setup (Recommended)

After completing the configuration, run the included test script to verify that everything is working correctly.

    python test_trakt_config.py

**If the test is successful**, you will see a success message with your Trakt username.

### 4. Tautulli Configuration

1.  In Tautulli, go to **Settings > Notification Agents > Add a new notification agent**.
2.  Select **Script**.
3.  **Configuration Tab:**
    -   **Script Folder**: Select the folder where you saved the scripts.
    -   **Script File**: Choose `trakt_sync.py`.
4.  **Triggers Tab:**
    -   Check the box for **Watched**.
5.  **Arguments Tab:**
    -   Go to the **Watched** section.
    -   Enter the following arguments for both movies and episodes:

    --title "{title}" --media_type "{media_type}" --season "{season_num}" --episode "{episode_num}" --show_name "{show_name}"

## That's it!

Your setup is complete. The project is now fully configured and ready to go.

---
## License
This project is licensed under the MIT License.
