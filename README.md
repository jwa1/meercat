# Meercat

A Webex Teams bot to provide product conversion between Catalyst and Meraki platforms.

## Installation

1. Create and activate virtual environment:
`python3 -m venv venv` and `source venv/bin/activate`
2. Install packages `pip install -r requirements.txt`
3. Create .env file `touch .env` with appropriate tokens:

   `WEBEX_TEAMS_ACCESS_TOKEN, DIALOGFLOW_PROJECT_ID, GOOGLE_APPLICATION_CREDENTIALS`
4. Run `ngrok http 5000`
5. Create WebEx webhooks `python tools/create_webhooks.py`
6. Run application `flask run`
