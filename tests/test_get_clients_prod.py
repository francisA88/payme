from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from authmanager import AuthManager

import requests

auth = AuthManager()
api_k = auth.get_access_token()

FLUTTERWAVE_BASE_URL = 'https://api.flutterwave.cloud/f4bexperience'
customers = requests.get(FLUTTERWAVE_BASE_URL+"/customers", headers={
    "Authorization": f"Bearer {api_k}",
    "Accept": "application/json"
}).json()

print(customers)