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
