from client import MSPClient
import time
from concurrent.futures import ThreadPoolExecutor

def pixeler():
    """
    Function to automate gift exchange and fame boosting between two accounts.
    """
    server = "us"
    gift_actor_id = 2016815973

    # Login information for two accounts
    accounts = [
        ("sirneel", "2003nishit"),
        ("starwarfare123", "nishit2003")
    ]

    # Login and establish connections for both clients
    clients = []
    for username, password in accounts:
        res = MSPClient.user_login(server, username, password)
        client = MSPClient(server, *res)
        client.establish_websocket_connection()
        clients.append(client)

    # First client buys a fame booster
    clients[0].buy_fame_booster()

    # Perform gift exchange between the two accounts
    for _ in range(26):
        clients[0].send_gift(clients[1].actor_id, gift_actor_id)
        gift_id = clients[1].view_gift()
        clients[1].open_gift(gift_id)
        clients[1].send_gift(clients[0].actor_id, gift_actor_id)
        gift_id = clients[0].view_gift()
        clients[0].open_gift(gift_id)

    # Close connectionss
    for client in clients:
        client.close_connection()

def watch_movie():
    """
    Function to automate the process of watching a specific movie using multiple accounts.
    """
    server = "us"
    movie_id = 33087419

    with open("bots.txt", "r") as bots_file:
        accounts = [line.strip().split(":") for line in bots_file]

    for username, password in accounts:
        print(f"Processing account: {username}")
        
        res = MSPClient.user_login(server, username, password)
        client = MSPClient(server, *res)
        client.establish_websocket_connection()
        client.validate_bot()

        res = client.watch_movie(movie_id)
        print(f"Watched Movie: {res}")
        client.close_connection()

        if input("Press 'q' to quit, any other key to continue: ") == "q":
            break

def give_autographs():
    """
    Function to send autographs from multiple accounts to a specified user.
    """
    server = "us"
    target_user = "simplyjas"

    with open("bots.txt", "r") as bots_file:
        accounts = [line.strip().split(":") for line in bots_file]

    for username, password in accounts:
        print(f"Processing account: {username}")
        
        res = MSPClient.user_login(server, username, password)
        client = MSPClient(server, *res)
        client.establish_websocket_connection()
        client.validate_bot()

        friend_actor_id = client.get_actor_id_from_user(target_user)
        res = client.send_autograph(friend_actor_id)
        print(f"Autograph sent: {res}")

        time.sleep(2)
        client.close_connection()

def care_for_bonsters():
    """
    Function to automate feeding, washing, and playing with bonsters.
    """
    username, password = "sirneel", "2003nishit"
    server = "us"
    bonster_ids = [4818939, 4818932, 4818936, 4818934, 4818938, 4818937, 4818933, 4818935, 4818931, 4818273]

    res = MSPClient.user_login(server, username, password)
    client = MSPClient(server, *res)
    client.establish_websocket_connection()
    client.validate_bot()

    for bonster_id in bonster_ids:
        for _ in range(5):
            print(f"Feeding Bonster {bonster_id}: {client.feed_bonster(bonster_id)}")
        print(f"Washing Bonster {bonster_id}: {client.wash_bonster(bonster_id)}")
        print(f"Playing with Bonster {bonster_id}: {client.play_with_bonster(bonster_id)}")
        time.sleep(2)

    client.close_connection()

# MULTITHREADING STUFF

def send_autograph_for_account(server, username, password, target_user):
    res = MSPClient.user_login(server, username, password)
    client = MSPClient(server, *res)
    client.establish_websocket_connection()
    client.validate_bot()

    friend_actor_id = client.get_actor_id_from_user(target_user)
    res = client.send_autograph(friend_actor_id)
    print(f"Autograph sent: {res}")

    client.close_connection()

def give_threaded_autographs():
    server = "us"
    target_user = "<joel2>"

    with open("bots.txt", "r") as bots_file:
        accounts = [line.strip().split(":") for line in bots_file]

    # Using multithreading to send autographs concurrently
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(send_autograph_for_account, server, username, password, target_user)
            for username, password in accounts
         ]
        for future in futures:
            future.result()

def watch_movie_for_account(server, username, password, movie_id):
    res = MSPClient.user_login(server, username, password)
    client = MSPClient(server, *res)
    client.establish_websocket_connection()
    client.validate_bot()

    res = client.watch_movie(movie_id)
    print(f"Watched Movie: {res}")

    client.close_connection()

def watch_threaded_movie():
    server = "us"
    movie_id = 33087309

    with open("bots.txt", "r") as bots_file:
        accounts = [line.strip().split(":") for line in bots_file]

    # Using multithreading to watch movies concurrently
    with ThreadPoolExecutor() as executor:
        futures = []
        for username, password in accounts:
            futures.append(executor.submit(watch_movie_for_account, server, username, password, movie_id))
            time.sleep(random.uniform(6, 7))
        for future in futures:
            future.result()




pixeler()
