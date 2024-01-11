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

