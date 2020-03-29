from flask import Flask, request, jsonify, render_template

import os
import requests
import json
import logging

from conversion import Converter
from bot import ChatBot

# Create flask instance
app = Flask(__name__)
port = int(os.environ.get("PORT", 5000))

# Create an instance of the chat bot
bot = ChatBot()

@app.route('/')
def index():
    gif = "https://66.media.tumblr.com/0a14eda38c31356d1e164009ef1edf2f/tumblr_mjpnd23P7x1qhbw13o1_400.gifv"
    return render_template('index.html', gif_url=gif)

@app.route('/compare', methods=["POST"])
def compare():
    return bot.compare(request.json)

@app.route('/events', methods=['POST'])
def message_received():
    # Get the POST data sent from Webex Teams
    return bot.receive_message(request.json)

@app.route('/actions', methods=['POST'])
def attachment_action_received():
    return bot.execute_action(request.json)

# run Flask app
if __name__ == "__main__":
    # Check for correct environment variables
    if (os.environ.get("WEBEX_TEAMS_ACCESS_TOKEN") == ''):
        print("WEBEX_TEAMS_ACCESS_TOKEN not found in environment variables")
        exit()
    elif (os.getenv('DIALOGFLOW_PROJECT_ID') == ''):
        print("DIALOGFLOW_PROJECT_ID not found in environment variables")
        exit()

    app.run("0.0.0.0", port=port)
    