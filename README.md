# SentiSounds
*Sounds For The Soul*

<img src="frontend\src\assets\sentisounds_icon.png" width="200" style="display:block;margin:0 auto;">

SentiSounds is a web application designed to cater to the sound your soul craves. Just tell us how you feel and we'll deliver a carefully curated list of songs to fit your mood.

## Prerequisites
- Python 3.10+
- pip
- The Python packages listed in the `requirements.txt` file
    - > pip install -r requirements.txt
- PSQL 12.18+
- NGINX 1.18.0+
- We also recommend setting up a virtual environment through venv, pyenv, or conda

## Secrets
We provide an updated `secrets.example.json` file to serve as a template for
your secret keys and tokens. A description of each field is provided below:
- open_ai
    - api_key: The API key provided by OpenAI for your application
    - prompt: The system prompt to feed the GPT model for genre generation.
    Ensure that your prompt returns a list of 5 strings via JSON under a 'genres' key
- spotify
    - client_id: The client ID provided by Spotify for your application
    - client_secret: The client secret provided by Spotify for your application
    - redirect_uri: The URI to redirect users to after they have successfully authentication. Generally, this should be the address of your index page
    - base_token: Information about the base Spotify account (to use for
        non-authenticated users)
        - access_token: The access token of your base Spotify account
        - token_type: The type of token retrieved for the base account (generally "Bearer")
        - expires_in: How long until the token expires
        - scope: The scope of the authentication (generally "user-read-private")
        - expires_at: The time at which the token will expire
        - refresh_token: The token to use to refresh the base token
- database
    - host: The host of your database (generally localhost)
    - port: The port for your database (generally 5432)
    - username: The username of the database user you set up (generally postgres)
    - password: The database's password
    - database_name: The name assigned to the database
- email
    - address: The literal email address to send authentication emails from
    - password: The password of the Google account (this is technically not required for SentiSounds functionality)
    - passkey: The app password acquired via Google's [App Password](https://security.google.com/settings/security/apppasswords?pli=1) functionality
        - You will need to ensure your Google Account [allows](https://knowledge.workspace.google.com/kb/how-to-create-app-passwords-000009237) for App Passwords
- youtube
    - api_key: The API key acquired via the YouTube API

A `secrets.json` file must be created with the above fields and be placed in the same directory as `secrets.example.json`.

Additionally, a `.cache/youtube_id_cache.json` file must be created (this also *must* remain .gitignor-ed to ensure YouTube API terms of service are met).

## Service Deployment
- Change the permissions for `scripts/enable_services.sh` via `chmod u+x scripts/enable_services.sh`
- Running `sudo scripts/enable_services.sh` will automatically install the NGINX package, install/update the required Python packages, start the PSQL service, and begin the API
- Running the API automatically creates all required tables on the PSQL database (assuming the PSQL service was successfully started and ran)
- If the app is deployed on a linux-based system with `systemd`, the script can automatically run by the daemon on startup

## Web Deployment
- The first line of the `CNAME` file must be the domain of the website (for example, sentisounds.com)
- The `Service Deployment` section summarizes how to start the web service
- The web service will be available on `10.0.0.4:80` by default

## API Usage
- API documentation is completely written and updated in `backend/docs` accessed via `index.html`
- To make call the API, route calls to `10.0.0.4:5000` with the respective GET or POST method documented
- Pay special attention to whether parameters must be passed in the body as form-data or in the URL as a parameter (this is explicitely mentioned in the documentation as well)
- To restart the API service, run `sudo scripts/restart.sh`

___

<img src="frontend\src\assets\landingPage.png" style="display:block;margin:0 auto;">
