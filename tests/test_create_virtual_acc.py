import requests
from pathlib import Path
import sys
import uuid
import os

from test_create_customer import create_flutterwave_customer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from authmanager import AuthManager

authmanager = AuthManager()
FLUTTERWAVE_API_KEY = authmanager.get_access_token()
print("CLIENT ID FROM TEST: ", os.environ["FLW_CLIENT_ID"])
FLUTTERWAVE_BASE_URL = 'https://api.flutterwave.cloud/developersandbox'

def create_flutterwave_virtual_account(customer_id):
	expiry_seconds = 1800  # 30 minutes
	reference = str(uuid.uuid4())
	va_payload = {
		"reference": reference,
		"customer_id": customer_id,
		"expiry": expiry_seconds,
		"amount": 100,
		"currency": "NGN",
		"account_type": "dynamic",
		"narration": "Sapa Reduction Scheme"
	}
	va_headers = {
		"Authorization": f"Bearer {authmanager.get_access_token()}",
		"X-Idempotency-Key": str(uuid.uuid4()),
		"Content-Type": "application/json"
	}
	va_resp = requests.post(f"{FLUTTERWAVE_BASE_URL}/virtual-accounts", json=va_payload, headers=va_headers, timeout=10)
	va_resp.raise_for_status()
	return va_resp.json()

customer = create_flutterwave_customer({
    "name": {
        "first": "Francis",
        "last": "Cranfis"
    },
    "email": "franciscranfis@gmail.com",
    "meta": {
        "phone_number": "07011567890"
    }
},
{
    "Content-Type": "application/json",
    "Authorization": f"Bearer {FLUTTERWAVE_API_KEY}"
}
)

if customer.get('status') == 'success':
    cus_data = customer['data']
    if isinstance(cus_data, list): customer_id = customer['data'][0]['id']
    else: customer_id = customer['data']['id']
    va = create_flutterwave_virtual_account(customer_id)
    print(va)
    if va.get('status') == 'success':
        va_data = va['data']
        print("Virtual Account Created Successfully")
        print(f"Account Number: {va_data.get('account_number')}")
        print(f"Bank Name: {va_data.get('account_bank_name')}")
        print(f"Account Type: {va_data.get('account_type')}")
        print(f"Reference: {va_data.get('reference')}")
    else:
        print("Virtual account creation failed:", va.get('message', 'Unknown error'))

