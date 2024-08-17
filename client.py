#-----------------------------------------------------------------------------------------
# 
# MAIN MSP CLIENT
#
#-----------------------------------------------------------------------------------------

import json
import websocket
import requests
from amf import invoke_method, get_session_id, ticket_header
from datetime import datetime

#-----------------------------------------------------------------------------------------
# Needs to be built out by adding more functions/features
#-----------------------------------------------------------------------------------------
class MSPClient:
    def __init__(self, server, actor_id, name, ticket, access_token, profile_id, culture):
        self.server = server
        self.actor_id = actor_id
        self.name = name
        self.ticket = ticket
        self.access_token = access_token
        self.profile_id = profile_id
        self.culture = culture
        self.ws = None
        
    # Making realtime connection to IP address provided by the servers loadbalancer
    def establish_websocket_connection(self):
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

    # Close websocket connection
    def close_connection(self):
        if self.ws:
            self.ws.close()
            print("WebSocket connection closed.")
        else:
            print("No WebSocket connection to close.")

    # Login for user must be done before websocket connection
    def userLogin(server, username, password):
        code, resp = invoke_method(
            server,
            "MovieStarPlanet.WebService.User.AMFUserServiceWeb.Login",
            [
                username,
                password,
                [],
                None,
                None,
                "MSP1-Standalone:XXXXXX"
            ],
            get_session_id()
        )

        status = resp['loginStatus']['status']
        if status != "Success":
            print(f"Login failed, status: {status}")
            quit()

        # Retrieve stuff from login response
        actor_id = resp['loginStatus']['actor']['ActorId']
        name = resp['loginStatus']['actor']['Name']
        ticket = resp['loginStatus']['ticket']
        access_token = resp['loginStatus']['nebulaLoginStatus']['accessToken']
        profile_id = resp['loginStatus']['nebulaLoginStatus']['profileId']
        culture = resp['loginStatus']['actorLocale'][0]

        return [actor_id, name, ticket, access_token, profile_id, culture]

    #-------------------------------------------------------------------------------------
    # Add more stuff under here. ex. def watchmovie(movie_id), etc.
    #-------------------------------------------------------------------------------------

    # Get ActorId from username
    def getActorIdFromUser(self, user):
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.UserSession.AMFUserSessionService.GetActorIdFromName",
            [
                user
            ],
            get_session_id()
        )
        return resp
    
    # Query for user details. *EDIT RETURN INFO AS NEEDED*
    def mspQuery(self, friend_actor_id):
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.AMFActorService.BulkLoadActors",
            [
                ticket_header(self.ticket),
                [friend_actor_id]
            ],
            get_session_id()
        )
        return [resp[0]['Money'], resp[0]["Diamonds"]]

    # Send autograph
    def sendAutograph(self, friend_actor_id):
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.UserSession.AMFUserSessionService.GiveAutographAndCalculateTimestamp",
            [
                ticket_header(self.ticket),
                self.actor_id,
                friend_actor_id
            ],
            get_session_id()
        )
        return resp
    
    # Get MovieId from actorid
    def getMovieIdFromActorId(self, friend_actor):
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.MovieService.AMFMovieService.GetMovieListForActor",
            [
                ticket_header(self.ticket),
                friend_actor,
                2,
                0,
                16
            ],
            get_session_id()
        )
        return resp["list"][0]["movieId"]
    
    # Watch movie
    def watchMovie(self, movieId):
        
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.MovieService.AMFMovieService.MovieWatched",
            [
                ticket_header(self.ticket),
                movieId,
                self.actor_id
            ],
            get_session_id()
        )
        return resp
    

    def viewGift(self):
        # View the gift
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.Gifts.AMFGiftsService+Version2.GetGiftsNewPaged",
            [
                ticket_header(self.ticket),
                self.actor_id,
                0,
                6
            ],
            get_session_id()
        )
        giftId = resp['Items'][0]['GiftId']
        # actorClothesRelId = resp['Items'][0]['ActorClothesRelId']
        return int(giftId)
    
    def openGift(self, gift_id):
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.Gifts.AMFGiftsService+Version2.OpenGift",
            [
                ticket_header(self.ticket),
                self.actor_id,
                gift_id
            ],
            get_session_id()
        )
        print(resp)

    # Send Gift
    def sendGift(self, friend_actor, gift_id):
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.Gifts.AMFGiftsService+Version2.GiveGiftOfCategory",
            [
                ticket_header(self.ticket),
                self.actor_id,
                friend_actor,
                gift_id,
                0,
                1,
                "Gift_item_3.swf"
            ],
            get_session_id()
        )
        print(resp)