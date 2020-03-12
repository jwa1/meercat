from flask import Flask, request, jsonify, render_template
from webexteamssdk import WebexTeamsAPI, Webhook
import dialogflow

import os
import requests
import json

# Create flask instance
app = Flask(__name__)
# Create the Webex Teams API connection object
api = WebexTeamsAPI()

@app.route('/')
def index():
    gif = "https://66.media.tumblr.com/0a14eda38c31356d1e164009ef1edf2f/tumblr_mjpnd23P7x1qhbw13o1_400.gifv"
    return render_template('index.html', gif_url=gif)

@app.route('/compare', methods=["POST"])
def compare():
    data = request.get_json(silent=True)

    reply = {
        "fulfillmentText": "Test"
        }
    return jsonify(reply)

def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(
            session=session, query_input=query_input)

        return response.query_result

@app.route('/events', methods=['POST'])
def message_received():
    # Get the POST data sent from Webex Teams
    json_data = request.json
    print("\n")
    print("WEBHOOK POST RECEIVED:")
    print(json_data)
    print("\n")
    # Create a Webhook object from the JSON data
    webhook_obj = Webhook(json_data)
    # Get the room details
    room = api.rooms.get(webhook_obj.data.roomId)

    # Get the message details
    message = api.messages.get(webhook_obj.data.id)
    # Get the sender's details
    person = api.people.get(message.personId)

    print("NEW MESSAGE IN ROOM '{}'".format(room.title))
    print("FROM '{}'".format(person.displayName))
    print("MESSAGE '{}'\n".format(message.text))

    # This is a VERY IMPORTANT loop prevention control step.
    # If you respond to all messages...  You will respond to the messages
    # that the bot posts and thereby create a loop condition.
    me = api.people.me()
    if message.personId == me.id:
        # Message was sent by me (bot); do not respond.
        return "OK"

    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    response = detect_intent_texts(project_id, "unique", message.text, 'en')
    response_text = { "message":  response.fulfillment_text }

    text = f"Model: {response.parameters.fields.get('model')}\nPlatform:{response.parameters.fields.get('platform')}"

    api.messages.create(roomId=room.id, text=text)

    if response.fulfillment_text:
        api.messages.create(roomId=room.id, text=response.fulfillment_text)

    return jsonify(response_text)

# run Flask app
if __name__ == "__main__":
    # Check for correct environment variables
    if (os.environ.get("WEBEX_TEAMS_ACCESS_TOKEN") == ''):
        print("WEBEX_TEAMS_ACCESS_TOKEN not found in environment variables")
        exit()

    # Check if the token represents a bot
    me_resp = api.people.me()
    if me_resp.type != 'bot':
        print('WEBEX_TEAMS_ACCESS_TOKEN does not belong to a bot...exiting')
        exit()

    app.run(port=5000)
    