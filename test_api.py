import requests
import json


base_url = "http://localhost:5000/"
api_key =  "ct43-31bg-72b7-7b4e"




def login(username, password):
    post_data =  {
        'api_key' : api_key,
        'username' : username,
        'password' : password
    }
    r = requests.post(base_url + "api/login", json = post_data)
    print r.json()

def register(username, password):
    post_data =  {
        'api_key' : api_key,
        'username' : username,
        'password' : password
    }
    r = requests.post(base_url + "api/register", json = post_data)
    print r.json()




login("mcandres@gmail.com1", "dondon888")
login("mcandres@gmail.com", "dondon888")
register("mcandres@gmail.com", "dondon888")
#login("mcandres666@gmail.com", "dondon888")

