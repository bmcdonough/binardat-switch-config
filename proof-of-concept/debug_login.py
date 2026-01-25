"""Debug script to test login POST request."""

import requests
from rc4_crypto import encrypt_credentials

# Configuration
HOST = "192.168.2.1"
USERNAME = "admin"
PASSWORD = "admin"
RC4_KEY = "iensuegdul27c90d"

# Create session
session = requests.Session()

# Get login page first to establish session
print("Getting login page...")
response = session.get(f"http://{HOST}/")
print(f"Status: {response.status_code}")
print(f"Cookies: {dict(session.cookies)}")
print()

# Encrypt credentials
enc_user, enc_pass = encrypt_credentials(USERNAME, PASSWORD, RC4_KEY)
print(f"Encrypted username: {enc_user}")
print(f"Encrypted password: {enc_pass}")
print()

# Try login POST
login_data = {
    "name": enc_user,
    "pwd": enc_pass,
}

print("Posting to /login.cgi...")
response = session.post(
    f"http://{HOST}/login.cgi",
    data=login_data,
    timeout=30.0,
)

print(f"Status code: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"Cookies after login: {dict(session.cookies)}")
print()

print("Response content:")
print(response.text[:1000])  # First 1000 chars
print()

# Try to parse as JSON
try:
    json_data = response.json()
    print("JSON response:")
    print(json_data)
except ValueError:
    print("Response is not JSON")
