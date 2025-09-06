from authmanager import AuthManager

if __name__ == "__main__":
    print("Testing AuthManager")
    auth = AuthManager()
    token = auth.get_access_token()
    print("Access Token:", token)
    print("Credentials:", auth.get_credentials())
