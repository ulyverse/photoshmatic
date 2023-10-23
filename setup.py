#dependency modules
import requests

#custom modules
from utils import Helper


def __dir__():
    return " "

def enter_license_code(key):
    if validate_license_key(key):
        return True
    return False

#ASSUME THIS IS FROM API CALL
def validate_license_key(key):
    response = requests.post("https://lifecalendr.com/api/register", data={"licensekey":key, "id": Helper.get_uniq_identifier()})
    
    return response.status_code == 200 and response.json()['status']

def validate_registered_device():
    response = requests.post("https://lifecalendr.com/api/registered", data={"id": Helper.get_uniq_identifier()})

    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def validate_trial_key(trialkey):
    response = requests.post("https://lifecalendr.com/api/trialkey", data={"trialkey":trialkey})

    return response.status_code == 200 and response.json()['status']

def validate_version():
    response = requests.post("https://lifecalendr.com/api/version", data={"version":"v1.0"})

    return response.status_code == 200 and response.json()['status']
