#using .env variables for client and secret.
import os, pathlib
import dotenv
from datetime import datetime, timedelta

import requests

env_path = pathlib.Path(__file__).parent / '.prod.env'
dotenv.load_dotenv(env_path)

class AuthManager:
    def __init__(self):
        self.credentials = {}
        self.load_credentials()

    def load_credentials(self):
        client_id = os.getenv("FLW_CLIENT_ID")
        client_secret = os.getenv("FLW_CLIENT_SECRET")
        hash = os.getenv("HASH")
        if not hash:
            raise Exception("Missing Flutterwave API hash in environment")
        if not client_id or not client_secret:
            raise Exception("Missing Flutterwave API credentials in environment")

        self.credentials.update({
            "client_id": client_id,
            "client_secret": client_secret,
            "access_token": None,
            "expiry": None,
            "hash": hash
        })

    def get_credentials(self):
        return self.credentials
    
    def generate_access_token(self):
        # idx = 0

        header = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "client_id": self.credentials["client_id"],
            "client_secret": self.credentials["client_secret"],
            "grant_type": "client_credentials"
        }

        response = requests.post(url='https://idp.flutterwave.com/realms/flutterwave/protocol/openid-connect/token', headers=header, data=data)

        response_json = response.json()
        if response.status_code == 200:
            self.credentials['access_token'] = response_json.get("access_token")
            expires_in = response_json.get("expires_in", 0)
            self.credentials['expiry'] = datetime.now() + timedelta(seconds=expires_in)
        else:
            raise Exception("Failed to generate access token")

        return response_json
    
    def get_access_token(self):
        # idx = 0

        if not self.credentials['access_token'] or self.credentials['expiry'] is None:
            self.generate_access_token()
        
        expiry_delta = self.credentials['expiry'] - datetime.now()
        if expiry_delta < timedelta(minutes=1):
            self.generate_access_token()

        return self.credentials['access_token']
