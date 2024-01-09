# Prototype pollution

- https://portswigger.net/web-security/prototype-pollution
- https://portswigger.net/web-security/prototype-pollution/javascript-prototypes-and-inheritance
- https://portswigger.net/web-security/prototype-pollution/client-side
- https://portswigger.net/web-security/prototype-pollution/server-side
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
