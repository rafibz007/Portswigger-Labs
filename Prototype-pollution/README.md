# Prototype pollution

- https://portswigger.net/web-security/prototype-pollution
- https://portswigger.net/web-security/prototype-pollution/javascript-prototypes-and-inheritance
- https://portswigger.net/web-security/prototype-pollution/client-side
- https://portswigger.net/web-security/prototype-pollution/client-side/browser-apis
- https://portswigger.net/research/widespread-prototype-pollution-gadgets
- https://portswigger.net/web-security/prototype-pollution/server-side
- https://portswigger.net/research/server-side-prototype-pollution
- https://portswigger.net/burp/documentation/desktop/tools/dom-invader/prototype-pollution#detecting-sources-for-prototype-pollution

## DOM XSS via client-side prototype pollution

For learning purposes the lab was done using DOM Invader and by manual testing.

### DOM Invader

Turning on `DOM Invader` and setting `Attack Type` to `Prototype pollution` retrieves with two detected sources:
 - `__proto__[property]=value` in search
 - `constructor[prototype][property]=value` in search 

Testing the first finding we can notice that `Object.prototype` was polluted and contains arbitrary `testproperty` with value `DOM_INVADER_PP_POC`.

Now scanning for gadgets reviels one `script.src` sink and points to the code:

```
if(config.transport_url) {
    let script = document.createElement('script');
    script.src = config.transport_url;
    document.body.appendChild(script);
}
```

Now clicking `Exploit` opens a new page with the url `/?search=nsteng9k1'"<>&__proto__[transport_url]=data:,alert(1)` performing XSS

Pollution probably happends in `deparam.js` script.

### Manual

By accessing url `/?__proto__[foo]=bar` we can now check whether pollution was successful, by running `console.log(Object.prototype)` and noticing new `foo` property with `bar` value.

Now in order to test for gadgets, we intercept all the requests in responses and for the script we want to test we add `debugger` statement at the beggining of the script. Now after loading the page, the script execution will pause. Running below code in the console will pollute `Object.prototype` and inform us of every access to its new arbitrary value:

```
Object.defineProperty(Object.prototype, 'transport_url', {
    get() {
        console.trace();
        return 'polluted';
    }
})
```

From this we can read, at which line of code the value is accessed and notice it is being passed to `script.src`.

Now we can craft our own exploit: `?__proto__[transport_url]=data:,alert(1);`

NOTE: In `data:,alert(1);` payload `,` char is because of how this the script tag with data is defined. Usually we have comma separated configuration (type, encoding etc.) and the code

## DOM XSS via an alternative prototype pollution vector

Using `DOM Invader` we can quickly notice one source in search. Now as we scan for gadgets we notice that the value is being passes into `eval` in `searchLogger` function.


Now using dev tools debbuger pausing on `eval` function or the console we can figure out the working payload that solves the lab: `?__proto__.sequence=alert(1)+`.

The `+` sign is there because the code appends `1` at the end of the string, which normnally causes syntaxt error, but `+` sign bypasses this problem.

## Client-side prototype pollution via flawed sanitization

This time DOM Intruder did not find any sources, but be can notice loaded `deparamSanitised.js` script which uses `sanitizeKey` function defined as:

```
function sanitizeKey(key) {
    let badProperties = ['constructor','__proto__','prototype'];
    for(let badProperty of badProperties) {
        key = key.replaceAll(badProperty, '');
    }
    return key;
}
```

Since `replaceAll` function is not called recursively, we can bypass the protection like this: `sanitizeKey("__pro__proto__to__")`

Now accessing `?__pro__proto__to__[foo]=bar` updates the prototype with `foo` property.

`DOM Invader` was able to scan for gadgets and revieled again `transport_url` param passed to `script.src` sink.

Now accessing `?__pro__proto__to__[transport_url]=data:,alert(1);` solves the lab.

## Client-side prototype pollution in third-party libraries

DOM Invader found prototype polution in hash, which tested manually is successful. Testing for gadgets finds one sink in minified js library `ga.js` at `hitCallback` parameter.

Accessing `#__proto__[hitCallback]=alert(1)` successfully triggers `alert` function, so in order to solve the lab we need to deliver to the victim the following page:

```
<script>
location = "https://0a5800d1033bc7ab81b3851200a90031.web-security-academy.net/#__proto__[hitCallback]=alert(document.cookie)"
</script>
```

We cannot use an iframe because of `X-Frame-Options`, but redirection is good enough.

## Client-side prototype pollution via browser APIs

`DOM Invader` found two sources in search and was able to determine a `script.src` sink to which `transport_url` param is passed.

This time the parram is defined using the code below, which unables us to modify the parameter with casual prototype pollution. The value of `transport_url` is set to `false`, and then made uncofigurable.

```
let config = {params: deparam(new URL(location).searchParams.toString()), transport_url: false};
Object.defineProperty(config, 'transport_url', {configurable: false, writable: false});
```

`defineProperty` function accepts `descriptor` object as the third parameter, which defines this behaviour, but since the `value` param, defining default value, was not set, we can try to pollute it.

Accessing `?__proto__[value]=data:,alert(1)` pollutes the prototype with `value` key, which then is used in `defineProperty` function, causing the new value being set, which triggers XSS and solves the lab.

## Privilege escalation via server-side prototype pollution

`POST /my-account/change-address` request performs user billing info update with the provided request body:

```
{"address_line_1":"Wiener HQ","address_line_2":"One Wiener Way","city":"Wienerville","postcode":"BU1 1RP","country":"UK","sessionId":"pAxXXWsIcNAPVPJSLCaDvdCdZyFuXDm2"}
```

The response contains additional parameters, such as `isAdmin`. Tries to add `"isAdmin":true` param to the update request did not do the trick.

Adding `"__proto__":{"foo":"bar"}` to the request responds with additional param `"foo":"bar"`, which suggests that we have a prototype pollution here.

Providing invalid json results in 500 response with error description, that parsing failed.

Adding `"__proto__":{"isAdmin":true}` param to the update request responds with `"isAdmin":true`, polluting the prototype by adding `isAdmin` param set to true for every user. This means that probably the user object contains `isAdmin` param if it is an admin, and does not contain it at all if they are not one.

Now having elevated privillages we can access the Admin panel and solve the lab.
