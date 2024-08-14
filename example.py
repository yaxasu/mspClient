"""
This example shows how to login to MSP and send a authenticated request
to the LoadActorDetailsExtended method.
"""

from msp import invoke_method, get_session_id, ticket_header, MSPClient
from datetime import datetime
import time


# Set login credentials and server name
USERNAME = "npm7"
PASSWORD = "2003nishit"
SERVER = "us"

# Call the login method and retrieve the response
code, resp = invoke_method(
    SERVER,
    "MovieStarPlanet.WebService.User.AMFUserServiceWeb.Login", 
    [
        USERNAME,
        PASSWORD,
        [],
        None,
        None,
        "MSP1-Standalone:XXXXXX"
    ],
    get_session_id()
)

# Check if login was successful
status = resp.get('loginStatus', {}).get('status')
if status != "Success":
    print(f"Login failed, status: {status}")
    quit()

# Retrieve the auth ticket and actor ID from the login response
actor_id = resp['loginStatus']['actor']['ActorId']
name = resp['loginStatus']['actor']['Name']
ticket = resp['loginStatus']['ticket']
access_token = resp['loginStatus']['nebulaLoginStatus']['accessToken']
profile_id = resp['loginStatus']['nebulaLoginStatus']['profileId']

# Establish websocket connection
client = MSPClient(SERVER, profile_id, access_token)
client.establish_connection()

# time.sleep(60)

code, resp = invoke_method(
    SERVER,
    "MovieStarPlanet.WebService.UserSession.AMFUserSessionService.GetActorIdFromName",
    [
        "starwarfare123"
    ],
    get_session_id()
)
friend_actor = resp

code, resp = invoke_method(
    SERVER,
    "MovieStarPlanet.WebService.UserSession.AMFUserSessionService.GiveAutographAndCalculateTimestamp",
    [
        ticket_header(ticket),
        actor_id,
        friend_actor
    ],
    get_session_id()
)
print(resp)

client.close_connection()