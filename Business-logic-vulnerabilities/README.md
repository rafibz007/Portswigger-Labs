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

## Inconsistent handling of exceptional input

Again testing the max length limits.

Creating an account with really long email truncates it to constant size.

```
abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc@exploit-0a6500c00373cd8c800c57a6010c00e8.exploit-server.net
```

turns into:

```
abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc
```

and we still receive a verification email.

Because of that we can try to register an account in a subdomain `@dontwannacry.com.exploit-0a6500c00373cd8c800c57a6010c00e8.exploit-server.net` and make a name long enough to truncate the domain of the email leaving us with `@dontwannacry.com` giving us access to the admin panel at `/admin`.

The char limit is 255 and our target email domain `@dontwannacry.com` takes up 17 chars, so our malicious email should look like this: 

```
python

'c'*(255-len("@dontwannacry.com")) + '@dontwannacry.com.exploit-0a6500c00373cd8c800c57a6010c00e8.exploit-server.net'
```

which solves the lab.

## Inconsistent security controls

The application requires email validation when creating an account, but does not require it when changing an email once logged it.

Therefore we can create an accout with our custom email and then change it to email at `@dontwannacry.com` domain to get access to admin panel.

## Weak isolation on dual-use endpoint

In password change functionality when we play around with the request we can come to couple of conclusions:
 - when new passwords are different and we provide valid current password we can error that new passwords do not match
 - when we provide different new passwords and not valid or empty current password we will receive an error that current password is not valid
 - when we remove current password parameter we again see not matching new passwords error, so the param is not evaluated when it is not present 
 - when change the username we can an error the the current password is not valid (could be used for brute-forcing)

We can now modify the request to not provide current password and to set username to `administrator`. This way we will change admin password and be able to login and solve the lab.

## Insufficient workflow validation

When placing an order the validation for unsufficient funds is performed. We can receive an error or be redirected to `/cart/order-confirmation?order-confirmed=true`.

When we have in our cart too expensive items we can bypass insufficient fund validation and navigate straight to `/cart/order-confirmation?order-confirmed=true` endpoint which will place the order and solve the lab.

## Authentication bypass via flawed state machine

The authentication flow consist of couple of steps:
 - login page with passing the credentials
 - role selector page with selecting possible roles

When we break the flow and after `POST /login` we navigate straight to `/`, therefore dropping `GET /role-select` our role gets defaulted to `admin` and we have access to the admin panel.

Both `POST /login` and `GET /role-select` set us a new session cookie, probably changing our state in state machine, but cookie set after `POST /login` allows us to use the page and defaults our role to admin, therefore `GET /role-select` need to be dropped.

## Flawed enforcement of business rules

After receiving two coupons (on from top of the page `NEWCUST5` and other from the bottom signing up to newsletter `SIGNUP30`) we add the jacket to the basket and navigate there. 

Now we can observe that applying two time in a row the same coupon will result in an error. We can apply two coupons at the same time and here comes the bug, because the app when checking if the coupon was used checks only the last provided one, not all of them.

So given that, we can provide infinite amount of coupon in this order `NEWCUST5`, `SIGNUP30`, `NEWCUST5`, `SIGNUP30`, `NEWCUST5`, ...

Therefore lowering our price to pay to 0 and solving the lab.

## Infinite money logic flaw

Gift cards worth of 10$ can be bought. This combined with unlimited `SIGNUP30` newsletter `30% discount` coupon lets us pay `7$` and redeem it for `10$` achieving wealth (unlimited money).

The flow can be made using Burp, but in Community edition to do not get slowed down I am using Python-as-request extension I have made a simple python script for cloning the money.

```
python infinite-money.py
```

## Authentication bypass via encryption oracle

Each time the user logs in usign `stay signed in` functionality the different cookie is generated:

`aCSd2QjqgsPUw8qlV0WGzlMWb3lbtCmr5SxsNc+NQGk=`
`LxxAU8lULRhr6v8MHfu0mC0SgyrVSN3iji5u4ywRQSc=`

So it suggests using a timestamp or a salt in generating a cookie. Or the  value is simply random.

When creating a comment under the post, in case the email is invalid the `notification` cookie will be set and error `Invalid email address: dfgdfg` will be displayed. `notification` cookie looks similar to `stay-signed-in` cookie (is in the same way ciphered and server must decrypt it on requests).

It turns out that we can replace `notification` cookie value with `stay-signed-in` cookie value in order to decode it. Found cookie structure: 
 - `LxxAU8lULRhr6v8MHfu0mC0SgyrVSN3iji5u4ywRQSc=`: `wiener:1702301512133`
 - `aCSd2QjqgsPUw8qlV0WGzlMWb3lbtCmr5SxsNc+NQGk=`: `wiener:1702301152210`

The values `1702301512133` and `1702301152210` corelates to creation timestamps.

Then `stay-signed-in` cookie structure looks like this: `base64(encrypt(username:timestamp.now()))`

The `Invalid email address: dfgdfg` message is encoded and stored as `notification` cookie. Now we need to find a way to encrypt only `administrator:1702301512133` message.

`notification` cookie values depending on email specified:
 - `J0ux6WYvGUVn9Qzx4DQL/PRTwfyeyISGGKSg8r7EP/4=`: `test`
 - `J0ux6WYvGUVn9Qzx4DQL/FWfsauavzBBYkAHXvtzsDk=`: `abcd`
 - `J0ux6WYvGUVn9Qzx4DQL/D6iib+S8zg4qRhofj6Ieco7Se9Cp2Afjc+pTtSTQ3xHBPqkkUAPrftAvgOx0UOSBw==`: `administrator:1702301512133`

Analyzing this we can conclude that first characters are always the same and may represent `Invalid email address:` part of the message. This can mean that block enryption algorithm is used.

We can remove remove first part of the token (base64 decode it, remove first 23 bytes - length of the first part of the message - and base64 encode it) and try to send the cookie again, after what we receive 500 response with error `Input length must be multiple of 16 when decrypting with padded cipher`.

We can try to pad to 32 bytes with `'x'*(32-len("Invalid email address: "))` and the add our data:

 - `J0ux6WYvGUVn9Qzx4DQL/DEOD5VuJzAIAWvt0El9P+OPloJlqZ6lCMWdxPMKYtN6`: `xxxxxxxxxtest`
 - `J0ux6WYvGUVn9Qzx4DQL/DEOD5VuJzAIAWvt0El9P+P4YlyKUYnp9zCLKkUwHcGs`: `xxxxxxxxxabcd`
 - `J0ux6WYvGUVn9Qzx4DQL/DEOD5VuJzAIAWvt0El9P+PZXKCqBWZ0pqlvdrzlS+fPhb+JVK0zTCANvhRQZkxhgQ==`: `xxxxxxxxxadministrator:1702301512133`

We can now try to construct the proper `stay-signed-in` cookie for the administrator:

Take our encrypted cookie: `J0ux6WYvGUVn9Qzx4DQL/DEOD5VuJzAIAWvt0El9P+PZXKCqBWZ0pqlvdrzlS+fPhb+JVK0zTCANvhRQZkxhgQ==`, base64 decode it, remove first 32 bytes (beggining of the error message and our padding with `x`), then base64 encode again: `2VygqgVmdKapb3a85Uvnz4W/iVStM0wgDb4UUGZMYYE=`

Testing our new cookie as notification decrypts prefectly to `administrator:1702301512133`, so now we can use this cookie (remove `session` cookie and replace `stay-sign-in` one with our custom one) and solve the lab.
