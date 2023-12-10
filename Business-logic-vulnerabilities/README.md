# Business logic vulnerabilities

- https://portswigger.net/web-security/logic-flaws
- https://portswigger.net/web-security/logic-flaws/examples

## Excessive trust in client-side controls

In the product details screen you can add the product to the cart.

To achieve this `POST /cart` request is performed with parameters such as `quantity` and `price`. 

The request can be intercepted and `price` parameter can be changed to some arbitrary small value. Backend server would not complain and allow us to add to the cart the product in different price and then submit the order normally.

## High-level logic vulnerability

In the cart screen, the amount of items in the cart can be modified by `+` and `-` signs, which make `POST /cart` request with parameters such as `productId` and `quantity`. In that request the server does not check whether the total amount of items is negative.

We can place a normal order and add negative amount of other items to lower the price.

## Low-level logic flaw

This time we are not able to add negative amount of items or change their size, so what we can try is to test total cost limits.

At max 99 items can be added with one `POST /cart` request. With simple python script we are able to add the most valueable item to the cart and observe what happends:

```
import requests

burp0_cookies = {"session": "Aq55Ovpa8Up6ykF5wtaM2Kl0dlGJ1geK"}
burp0_headers = {...}
burp0_data = {"productId": "1", "redir": "CART", "quantity": "99"}
burp0_url = "https://0a1e008c036251298166e33600ff00d8.web-security-academy.net:443/cart"

while True:
    requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data)
```

Alternatively Burp Tubo Intruder could be used.

Until some time we can observe that the total amount changes to big negative number, overflowing server number size.

The order cannot be made with total amount less than 0, so we can calculate how much more items we need to add and then place an order once we nearly pass 0.
