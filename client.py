#-----------------------------------------------------------------------------------------
# 
# MAIN MSP CLIENT
#
#-----------------------------------------------------------------------------------------

import json
import websocket
import requests
from msp import invoke_method, get_session_id, ticket_header
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
        
    def establish_websocket_connection(self):
        """Establish a WebSocket connection to the server."""
        address = "https://presence-us.mspapis.com/getServer" if self.server == "us" else "https://presence.mspapis.com/getServer"
        formatted_address = requests.get(address).text.replace('-', '.')
        formatted_url = f"ws://{formatted_address}:10843/{formatted_address.replace('.', '-')}/?transport=websocket"
        
        self.ws = websocket.WebSocket()
        self.ws.connect(formatted_url)
        print("WebSocket connection established.")

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
        """Close the WebSocket connection."""
        if self.ws:
            self.ws.close()
            print("WebSocket connection closed.")
        else:
            print("No WebSocket connection to close.")

    @staticmethod
    def user_login(server, username, password):
        """Login to the MSP server and retrieve user information."""
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

        actor_id = resp['loginStatus']['actor']['ActorId']
        name = resp['loginStatus']['actor']['Name']
        ticket = resp['loginStatus']['ticket']
        access_token = resp['loginStatus']['nebulaLoginStatus']['accessToken']
        profile_id = resp['loginStatus']['nebulaLoginStatus']['profileId']
        culture = resp['loginStatus']['actorLocale'][0]

        return [actor_id, name, ticket, access_token, profile_id, culture]

    def get_actor_id_from_user(self, user):
        """Get the ActorId from the username."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.UserSession.AMFUserSessionService.GetActorIdFromName",
            [user],
            get_session_id()
        )
        return resp
    
    def msp_query(self, friend_actor_id):
        """Query for user details."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.AMFActorService.BulkLoadActors",
            [
                ticket_header(self.ticket),
                [friend_actor_id]
            ],
            get_session_id()
        )
        return [resp[0]['Money'], resp[0]["Diamonds"], resp[0]["Fame"]]

    def send_autograph(self, friend_actor_id):
        """Send an autograph to a friend."""
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
    
    def get_movie_id_from_actor_id(self, friend_actor):
        """Get MovieId from ActorId."""
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
    
    def get_movie(self, movie_id):
        """Retrieve a movie by its ID."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.MovieService.AMFMovieService.GetMovieById",
            [
                ticket_header(self.ticket),
                movie_id,
            ],
            get_session_id()
        )
        return resp
    
    def watch_movie(self, movie_id):
        """Mark a movie as watched."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.MovieService.AMFMovieService.MovieWatched",
            [
                ticket_header(self.ticket),
                movie_id,
                self.actor_id
            ],
            get_session_id()
        )
        return resp

    def view_gift(self):
        """View the latest gift."""
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
        gift_id = resp['Items'][0]['GiftId']
        return int(gift_id)
    
    def open_gift(self, gift_id):
        """Open a gift."""
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
        return resp

    def send_gift(self, friend_actor, gift_id):
        """Send a gift to a friend."""
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

    def validate_bot(self):
        """Validate the bot by claiming a daily award."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.Awarding.AMFAwardingService.claimDailyAward",
            [
                ticket_header(self.ticket),
                "wheel",
                120,
                self.actor_id
            ],
            get_session_id()
        )
        print(resp)

    def feed_bonster(self, bonster_id):
        """Feed a bonster."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.Bonster.AMFBonsterService.FeedBonster",
            [
                ticket_header(self.ticket),
                bonster_id,
                6,
                self.actor_id
            ],
            get_session_id()
        )
        print(resp)

    def wash_bonster(self, bonster_id):
        """Wash a bonster."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.Bonster.AMFBonsterService.WashBonster",
            [
                ticket_header(self.ticket),
                bonster_id,
                100,
                self.actor_id
            ],
            get_session_id()
        )
        print(resp)
    
    def play_with_bonster(self, bonster_id):
        """Play with a bonster."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.Bonster.AMFBonsterService.PlayWithBonster",
            [
                ticket_header(self.ticket),
                bonster_id,
                100,
                self.actor_id
            ],
            get_session_id()
        )
        print(resp)

    def buy_fame_booster(self):
        """Buy a fame booster."""
        code, resp = invoke_method(
            self.server,
            "MovieStarPlanet.WebService.Spending.AMFSpendingService.BuyFameBooster",
            [
                ticket_header(self.ticket),
                self.actor_id
            ],
            get_session_id()
        )
        return resp
