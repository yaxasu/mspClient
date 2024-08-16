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

USERNAME = f""
PASSWORD = ""
SERVER = "us"

FRIEND_USERNAME = ""

#-----------------------------------------------------------------------------------------
# LOGIN STUFF - AMF request sent to api to recieve ticket, accesstoken, profileid, etc.
# Then a websocket client is established for a persistant realtime connection.
#-----------------------------------------------------------------------------------------

res = MSPClient.userLogin(SERVER, USERNAME, PASSWORD)
client = MSPClient(SERVER, res[0], res[1], res[2], res[3], res[4], res[5])
client.establish_websocket_connection()

#-----------------------------------------------------------------------------------------
# Make requests and edit stuff under this! :)
#-----------------------------------------------------------------------------------------

frienndd = client.getActorIdFromUser(FRIEND_USERNAME)
idd = client.getMovieIdFromActorId(frienndd)
response = client.watchMovie(idd)
print(response)

#-----------------------------------------------------------------------------------------
# Close the connection once requests are done
#-----------------------------------------------------------------------------------------

client.close_connection()