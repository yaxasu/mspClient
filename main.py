#-----------------------------------------------------------------------------------------
# 
# Main file to be edited for establishing the client, and interacting with the API
#
#-----------------------------------------------------------------------------------------

from msp import invoke_method, get_session_id, ticket_header
from client import MSPClient
import time

#-----------------------------------------------------------------------------------------
# Edit login info as needed
#-----------------------------------------------------------------------------------------

USERNAME = ""
PASSWORD = ""
SERVER = "us"

#-----------------------------------------------------------------------------------------
# LOGIN STUFF - AMF request sent to api to recieve ticket, accesstoken, profileid, etc.
# Then a websocket client is established for a persistant realtime connection.
#-----------------------------------------------------------------------------------------
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

# Retrieve stuff from login response
actor_id = resp['loginStatus']['actor']['ActorId']
name = resp['loginStatus']['actor']['Name']
ticket = resp['loginStatus']['ticket']
access_token = resp['loginStatus']['nebulaLoginStatus']['accessToken']
profile_id = resp['loginStatus']['nebulaLoginStatus']['profileId']

# Actually establish the websocket connection
client = MSPClient(SERVER, profile_id, access_token)
client.establish_connection()

#-----------------------------------------------------------------------------------------
# Make requests and edit stuff under this! :)
#-----------------------------------------------------------------------------------------


code, resp = invoke_method(
    SERVER,
    "MovieStarPlanet.WebService.UserSession.AMFUserSessionService.LoadActorDetailsExtended", 
    [
        ticket_header(ticket),
        actor_id
    ],
    get_session_id()
)
print(code, resp)



#-----------------------------------------------------------------------------------------
# Close the connection once requests are done
#-----------------------------------------------------------------------------------------
time.sleep(3)
client.close_connection()