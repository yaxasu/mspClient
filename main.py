from msp import invoke_method, get_session_id, ticket_header
from client import MSPClient
import time

#-----------------------------------------------------------------------------------------
# Edit this as needed
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

# Actually establish websocket connection
client = MSPClient(SERVER, profile_id, access_token)
client.establish_connection()

#-----------------------------------------------------------------------------------------
# Make requests and edit stuff here
#-----------------------------------------------------------------------------------------


code, resp = invoke_method(
    SERVER,
    "MovieStarPlanet.WebService.MovieService.AMFMovieService.GetMovieById",
    [
        ticket_header(ticket),
        33086376
    ],
    get_session_id()
)
print(code, resp)



#-----------------------------------------------------------------------------------------
# Close the connection once requests are done
#-----------------------------------------------------------------------------------------
time.sleep(5)
client.close_connection()