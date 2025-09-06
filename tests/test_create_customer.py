import requests
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from authmanager import AuthManager

authmanager = AuthManager()
FLUTTERWAVE_API_KEY = authmanager.get_access_token()
FLUTTERWAVE_BASE_URL = 'https://api.flutterwave.cloud/developersandbox'

def create_flutterwave_customer(payload, headers):
	resp = requests.post(f"{FLUTTERWAVE_BASE_URL}/customers", json=payload, headers=headers, timeout=10)
	if resp.status_code == 201:
		return resp.json()
	elif resp.status_code == 409:
		resp = requests.get(f"{FLUTTERWAVE_BASE_URL}/customers", params={"email": payload['email']}, headers=headers, timeout=10)
		if resp.status_code != 200:
			resp.raise_for_status()
		return resp.json()
	
	resp.raise_for_status()
	return resp.json()

payload = {
	"name": {
		"first": "Francis",
		"last": "Cranfis"
    },
	"email": "franciscranfis@gmail.com",
	"meta": {
		"phone_number": "07011567890"
    }
}
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {FLUTTERWAVE_API_KEY}"
}

customers = create_flutterwave_customer(payload, headers)
print(customers)