from concurrent.futures import ThreadPoolExecutor
from client import MSPClient
import time
import random

def send_autograph_for_account(server, username, password, target_user, delay=1):
    res = MSPClient.user_login(server, username, password)
    client = MSPClient(server, *res)
    client.establish_websocket_connection()
    client.validate_bot()

    friend_actor_id = client.get_actor_id_from_user(target_user)
    res = client.send_autograph(friend_actor_id)
    print(f"Autograph sent: {res}")

    client.close_connection()
    time.sleep(delay)

def give_autographs():
    server = "us"
    target_user = "starwarfare123"

    with open("bots.txt", "r") as bots_file:
        accounts = [line.strip().split(":") for line in bots_file]

    # Using multithreading to send autographs concurrently
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(send_autograph_for_account, server, username, password, target_user, delay=1)
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

def watch_movie():
    server = "us"
    movie_id = 33087247

    with open("bots.txt", "r") as bots_file:
        accounts = [line.strip().split(":") for line in bots_file]

    # Using multithreading to watch movies concurrently
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for username, password in accounts:
            futures.append(executor.submit(watch_movie_for_account, server, username, password, movie_id))
            time.sleep(random.uniform(4, 6))
        for future in futures:
            future.result()


if __name__ == "__main__":
    watch_movie()
