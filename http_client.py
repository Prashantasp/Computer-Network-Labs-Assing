# http_client.py
import requests

def http_client():
    url = "https://httpbin.org"  # Test API

    try:
        # GET request
        print("=== GET Request ===")
        response = requests.get(f"{url}/get")
        print("Status Code:", response.status_code)
        print("Headers:", response.headers)
        print("Body:", response.text[:200], "...")  # printing first 200 chars

        # POST request
        print("\n=== POST Request ===")
        data = {"name": "Prashant", "course": "Computer Networks"}
        response = requests.post(f"{url}/post", data=data)
        print("Status Code:", response.status_code)
        print("Headers:", response.headers)
        print("Body:", response.text[:200], "...")

    except requests.RequestException as e:
        print("Error:", e)

if __name__ == "__main__":
    http_client()
