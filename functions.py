from client import MSPClient

def pixeler():
    user1 = "sirneel"
    pass1 = "2003nishit"
    user2 = "starwarfare123"
    pass2 = "nishit2003"
    giftActor = 2016815973

    server = "us"

    res1 = MSPClient.userLogin(server, user1, pass1)
    res2 = MSPClient.userLogin(server, user2, pass2)

    client1 = MSPClient(server, res1[0], res1[1], res1[2], res1[3], res1[4], res1[5])
    client2 = MSPClient(server, res2[0], res2[1], res2[2], res2[3], res2[4], res2[5])

    client1.establish_websocket_connection()
    client2.establish_websocket_connection()

    for i in range(25):
        client1.sendGift(client2.actor_id, giftActor)

        giftId = client2.viewGift()
        client2.openGift(giftId)
        client2.sendGift(client1.actor_id, giftActor)

        giftId = client1.viewGift()
        client1.openGift(giftId)

    client1.close_connection()
    client2.close_connection()

# pixeler()

def watchMovie(movieId):
    with open("bots.txt", "r") as bots_file:
        accounts = bots_file.readlines()

    for account in accounts:
        account = account.strip()
        username, password = account.split(":")
        server = "us"

        print(username)

        res = MSPClient.userLogin(server, username, password)
        client = MSPClient(server, res[0], res[1], res[2], res[3], res[4], res[5])
        client.establish_websocket_connection()
        client.validateBot()

        res = client.watchMovie(movieId)
        print(res)
        
        client.close_connection()

        x = input()
        if x == "q":
            quit()

#watchMovie(33086999)

