# DOM-based vulnerabilities

- https://portswigger.net/web-security/dom-based

## DOM XSS using web messages

No `X-Frame-Options` header that would prevent loading this page in the `iframe` and additionally event listener preset for `message` event without origin verification that passes the input without sanitization to the `innerHtml` function.

Event listener for `message` event is our source, and `innerHtml` function is the sink.

Deliver below payload to the victim to solve the lab. It will load the victim page as an iframe and on load will post a message to all origins, causing vulnerable `message` event listener trigger.

```
<iframe src="https://0aa600ac04c124c89e1a8aa5009800fc.web-security-academy.net/" style="width: 100%; height: 100%;" frameBorder="0" onload='this.contentWindow.postMessage("<img src=X onerror=\"print()\"/>", "*")'></iframe>
```
