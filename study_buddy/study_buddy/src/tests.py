from passlib.hash import bcrypt
import os

password = 'random1234'
print(bcrypt.hash(password))

# import requests module 
import requests 
from requests.auth import HTTPBasicAuth 
  
# Making a get request 
response = requests.post(' http://127.0.0.1:8000/token', 
            auth = HTTPBasicAuth('celery_service', password)) 
  
# print request object 
print(response) 

import requests
import os

def get_auth_token():
    """
    Retrieve an authentication token from the backend.
    """
    token_endpoint = "http://127.0.0.1:8000/token"
    payload = {
        "username": "celery_service",  # or any predefined username for Celery
        "password": password
    }
    try:
        response = requests.post(token_endpoint, data=payload, timeout=5)
        response.raise_for_status()
        token = response.json().get("access_token")
        if not token:
            raise ValueError("No token received from the backend.")
        return token
    except requests.RequestException as e:
        print(f"Failed to retrieve token: {e}")
        raise

print(get_auth_token())