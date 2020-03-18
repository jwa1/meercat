from flask import jsonify
from webexteamssdk import WebexTeamsAPI, Webhook

import json
import os
from pprint import pprint
import logging

from conversion import Converter
import utils


class ChatBot():
    def __init__(self):
        super().__init__()
        self.api = WebexTeamsAPI()
        self.me = self.api.people.me()

        # Create instance of the Converter model
        project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
        self.converter = Converter(project_id, "unique")

        # Check if the token represents a bot
        me_resp = self.api.people.me()
        if me_resp.type != 'bot':
            print('WEBEX_TEAMS_ACCESS_TOKEN does not belong to a bot...exiting')
            exit()

    def compare(self, json_data):
        data = json_data

        # We can do some magic on the session id as we stored it as a combo of room and person id
        session_id = data["session"].split('/')[-1].split(".")
        person_id = session_id[0]
        room_id = session_id[1]

        # The text to return and send back to the user
        # This will sometimes be overridden by DialogFlow
        fulfillment_text = ""

        fields = data["queryResult"]["parameters"]
        if fields:
            model = fields.get("Model", None)
            if model and model:
                print(f"Found model {model}")
                match = self.converter.find_equivalent_switch(model)

                # Check if we found any switch matching the model
                if not match:
                    fulfillment_text = "Sorry, I couldn't find any switch matching that model number."
                elif len(match) > 1:
                    fulfillment_text = "I've found multiple matches for that model - please be more specific.\n"
                    for switch in match:
                        fulfillment_text += f"* {switch.model}\n"
                    fulfillment_text = fulfillment_text[:-1]
                else:
                    attachment = utils.generate_adaptive_card(model, match[0])
                    self.api.messages.create(roomId=room_id, text=str(match[0]), attachments=[attachment])
        
        reply = {"fulfillmentText": fulfillment_text}
        return jsonify(reply)

    def receive_message(self, json_data):
        # Create a Webhook object from the JSON data
        webhook_obj = Webhook(json_data)
        # Get the room details
        room = self.api.rooms.get(webhook_obj.data.roomId)

        # Get the message details
        message = self.api.messages.get(webhook_obj.data.id)
        # Get the sender's details
        person = self.api.people.get(message.personId)

        if __debug__:
            print(f"\nNEW MESSAGE IN ROOM '{room.title}'")
            print(f"FROM '{person.displayName}'")
            print(f"MESSAGE '{message.text}'\n")

        # This is a VERY IMPORTANT loop prevention control step.
        # If you respond to all messages...  You will respond to the messages
        # that the bot posts and thereby create a loop condition.
        if message.personId == self.me.id:
            # Message was sent by me (bot); do not respond.
            return "OK"

        if not message.text or message.text == "":
            print("Empty message.")
            return "OK"

        # Create a unique session id as a combo of person and room id
        # We will also use this in the future to send content back (probably a little hacky)
        session_id = message.personId + "." + room.id

        # Call DialogFlow API to parse intent of message
        response = self.converter.detect_intent_texts(session_id, message.text, 'en')

        # 
        response_message = response.fulfillment_text
        
        if response_message:
            self.api.messages.create(roomId=room.id, text=str(response_message))

        response_text = { "message":  response_message }
        return jsonify(response_text)