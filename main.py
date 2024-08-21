from client import MSPClient

server = "us"
username = "starwarfare123"
password = "nishit2003"
target = "npm5"

res = MSPClient.user_login(server, username, password)
client = MSPClient(server, *res)
client.establish_websocket_connection()

response = client.buy_fame_booster()
resss = client.get_actor_id_from_user(target)
coinsss = client.msp_query(resss)

# res = client.bot_generator()
print(coinsss)


client.close_connection()