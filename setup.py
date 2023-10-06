import json
import os
import requests

from utils import Helper

def is_setup_done():
    return os.path.exists("firstrun.json")

def setup():
    if is_setup_done():
        with open("firstrun.json", "r") as f: 
            id = Helper.get_uniq_identifier() 
            data = json.load(f)
            if data['id'] == id:
                return True
    
    return False

def enter_license_code():
    key = input("Enter your license key:")
    if validate_license_key(key):
        with open("firstrun.json", "w") as f:
            data = {}
            data['id'] = Helper.get_uniq_identifier()
            data['key'] = key
            json.dump(data, f)
            return True
    return False

#ASSUME THIS IS FROM API CALL
def validate_license_key(key):
    response = requests.post("https://lifecalendr.com/api/key", data={"lkey":key})
    
    if response.status_code == 200 and response.json()['message'] == True:
        return True
    else:
        return False
        
