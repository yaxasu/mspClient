import json
import websocket
import requests

class MSPClient:
    def __init__(self, server, profile_id, access_token):
        self.server = server
        self.profile_id = profile_id
        self.access_token = access_token
        self.ws = None

    def establish_connection(self):
        # Determine the correct server URL
        address = "https://presence-us.mspapis.com/getServer" if self.server == "us" else "https://presence.mspapis.com/getServer"
        formatted_address = requests.get(address).text.replace('-', '.')
        formatted_url = f"ws://{formatted_address}:10843/{formatted_address.replace('.', '-')}/?transport=websocket"
        
        # Establish the WebSocket connection
        self.ws = websocket.WebSocket()
        self.ws.connect(formatted_url)
        print("WebSocket connection established.")

        # Prepare and send the message payload
        message_payload = json.dumps([
            "10", {
                "messageType": 10,
                "messageContent": {
                    "version": 3,
                    "applicationId": "APPLICATION_WEB",
                    "country": self.server,
                    "username": self.profile_id,
                    "access_token": self.access_token
                }
            }
        ])
        self.ws.send(f"42{message_payload}")
        print("Message sent.")

    def close_connection(self):
        if self.ws:
            self.ws.close()
            print("WebSocket connection closed.")
        else:
            print("No WebSocket connection to close.")