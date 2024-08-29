from client import MSPClient

server = "us"
username = "starwarfare123"
password = "nishit2003"
target = "simplyjas"

res = MSPClient.user_login(server, username, password)
client = MSPClient(server, *res)
client.establish_websocket_connection()

resss = client.get_actor_id_from_user(target)
coinsss = client.msp_query(resss)

print(coinsss)

client.close_connection()