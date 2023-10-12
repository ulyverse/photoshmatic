import json
import os
import requests

from utils import Helper

def __dir__():
    return " "

def check_first_run_exist():
    if not os.path.exists("etc/f.txt"):
        with open("etc/f.txt", "w") as f:
            f.write("Q2O12MAZV343EXLU2FNSDF74LKS76LJF")

def setup():
    return get_id() == Helper.get_uniq_identifier()

def get_id():
    check_first_run_exist()
    with open("etc/f.txt", "r") as f:
        return f.read()

def set_id():
    with open("etc/f.txt", "w") as f:
        f.write(Helper.get_uniq_identifier())

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
