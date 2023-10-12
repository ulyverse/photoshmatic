import json
import os
import requests

from utils import Helper

def __dir__():
    return " "

def is_setup_done():
    return os.path.exists("firstrun.json")

def setup():
    return get_id() == Helper.get_uniq_identifier()

def get_id():
    if is_setup_done():
        with open("firstrun.json", "r") as f:
            data = json.load(f)
            return data['id']
    return None

def set_id():
    with open("firstrun.json", "w") as f:
        json.dump({'id':Helper.get_uniq_identifier()}, f)

def enter_license_code(key):
    if validate_license_key(key):
        set_id()
        return True
    return False

#ASSUME THIS IS FROM API CALL
def validate_license_key(key):
    response = requests.post("https://lifecalendr.com/api/register", data={"licensekey":key, "id": Helper.get_uniq_identifier()})
    
    return response.status_code == 200 and response.json()['status']

def validate_registered_device():
    response = requests.post("https://lifecalendr.com/api/registered", data={"id": Helper.get_uniq_identifier()})

    if response.status_code == 200 and response.json()['status']:
        set_id()
        return True
    
    return False

def validate_version():
    response = requests.post("https://lifecalendr.com/api/version", data={"version":"v1.0"})

    return response.status_code == 200 and response.json()['status']
