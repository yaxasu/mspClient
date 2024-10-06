from utils.client import MSPClient
from utils.functions import pixeler, watch_movie, give_threaded_autographs

username = input("Enter your username: ")
password = input("Enter your password: ")
print("Logging in...")
res = MSPClient.user_login("us", username, password)
client = MSPClient("us", *res)

print("1: Automated pixeler \n2: Automated movie watcher \n3: Autographer \n4: query")
option = input()

if option == "1":
    pixeler()

elif option == "2":
    target_user = input("Enter the target username: ")
    target_user_actor_id = client.get_actor_id_from_user(target_user)
    watch_movie(target_user_actor_id)

elif option == "3":
    target_user = input("Enter the target username: ")
    give_threaded_autographs(target_user)
    
elif option == "4":
    target_username = input("Enter the target username: ")
    target_actor_id = client.get_actor_id_from_user(target_username)
    information = client.msp_query(target_actor_id)
    print(information)