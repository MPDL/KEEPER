#!/usr/bin/env python3

import requests

password = input("Password: ")
otp = input("OTP: ")

url = "https://keeper.mpdl.mpg.de/api2/auth-token/"

payload = {
    "username": "keeper@mpdl.mpg.de",
    "password": password
}
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "X-SEAFILE-OTP": otp
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)
