import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

def network_check(url):
    print(f"Checking URL: {url}...")
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        print(f"Success! Status Code: {response.status_code}")
    except HTTPError as http_error:
        print(f"HTTP error: {http_error} for {url}")
    except ConnectionError as conn_error:
        print(f"Connection Error: {conn_error} for {url}")
    except Timeout as time_error:
        print(f"Timeout Error: {time_error} for {url}")
    except RequestException as req_err:
        print(f"Request Error: {req_err} for {url}")
        
if __name__ == "__main__":
    valid_url = 'https://pokeapi.co/api/v2/pokemon/1'
    print("Valid URL Test: Success")