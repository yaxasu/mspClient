#-----------------------------------------------------------------------------------------
# 
# Main file to be edited for establishing the client, and interacting with the API
#
#-----------------------------------------------------------------------------------------

from amf import invoke_method, get_session_id, ticket_header
from client import MSPClient
import time

#-----------------------------------------------------------------------------------------
# Edit login info as needed
#-----------------------------------------------------------------------------------------

USERNAME = ""
PASSWORD = ""
SERVER = "us"

FRIEND_USER = ""

#-----------------------------------------------------------------------------------------
# LOGIN STUFF - AMF request sent to api to recieve ticket, accesstoken, profileid, etc.
# Then a websocket client is established for a persistant realtime connection.
#-----------------------------------------------------------------------------------------

res = MSPClient.userLogin(SERVER, USERNAME, PASSWORD)
client = MSPClient(SERVER, res[0], res[1], res[2], res[3], res[4])
client.establish_websocket_connection()

#-----------------------------------------------------------------------------------------
# Make requests and edit stuff under this! :)
#-----------------------------------------------------------------------------------------
friend_actor = client.getActorIdFromUser(FRIEND_USER)
resp = client.sendAutograph(friend_actor)
print(resp)

#-----------------------------------------------------------------------------------------
# Close the connection once requests are done
#-----------------------------------------------------------------------------------------
# time.sleep(2)
client.close_connection()