
#to use this client.py "from api.client import get"


import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
import time
import json

#global constants
_TIMEOUT = 10
RETRIES = 3
RATE_LIMIT_DELAY = 0.1

    
def validate_url(url): # Validates URL format
    if url is None: 
        return False
    if not isinstance(url, str):
        return False
    if not url.startswith(('http://', 'https://')):
        return False
    return True
         
        
def send_request(url): # Sends GET request to URL with error handling
    
    try:
        response = requests.get(url, timeout=_TIMEOUT)
        return response
    except (HTTPError, ConnectionError, Timeout, RequestException):
        return None
    
def handle_status(response): # Handles HTTP response status codes
    
    status_code = response.status_code
    
    if 200 <= status_code < 300:
        return "OK"
    
    elif status_code == 404:
        return "NOT_FOUND"
    
    elif status_code == 429:
        return "RETRY_AFTER_DELAY"
    
    elif 500 <= status_code < 600:
        return "RETRY"
    
    elif 400 <= status_code < 500:
        return "STOP"
    
    return "STOP"

#handles JSON Errors
def parse_json(response):
    
    try:
        data = response.json()
        
        return data
    
    except json.JSONDecodeError:
        return None

# the mac daddy that runs all above            
def get(url):
    
    short_delay = 0.25
    long_delay = 1.0
    
    
    if not validate_url(url):
        return None
    
    for attempt in range(RETRIES):
        
        response = send_request(url)
        
        if response is None: 
            continue
        
        action = handle_status(response)
        
        if action == "OK": 
            break
        
        if action == "NOT_FOUND": 
            return None
        
        if action == "RETRY_AFTER_DELAY":
            time.sleep(long_delay)
            continue
        
        if action == "RETRY":
            time.sleep(short_delay)
            continue
        
        if action == "STOP":
            return None
        
    else:
         
        return None
        
    data = parse_json(response)
    if data is None:
        return None
    
    time.sleep(RATE_LIMIT_DELAY)
    
    return data
        
        
    

    