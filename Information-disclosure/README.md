# Information disclosure

- https://portswigger.net/web-security/information-disclosure
- https://portswigger.net/web-security/information-disclosure/exploiting#common-sources-of-information-disclosure

## Information disclosure in error messages

Navigating to product page and changing the `productId` param to a string respond with a stacktrace with `java.lang.NumberFormatException`.

Version is displayed at the bottom of the log: `Apache Struts X X.X.X`

## Information disclosure on debug page

Fuff scan did not return any results:

```
ffuf -w /opt/SecLists/Discovery/Web-Content/common.txt -u 'https://0a53000003c63d30854db33c00660035.web-security-academy.net/FUZZ' -fc 404
```

Looking at page source at the home page we can see a comment:

```
<!-- <a href=/cgi-bin/phpinfo.php>Debug</a> -->
```

We can now navigate to `/cgi-bin/phpinfo.php` and solve the lab.

## Source code disclosure via backup files

We can navigate to `/robots.txt` file and reveal disallowed `/backup` directory.

Then we can navigate to backed up java file and read the hard coded password.

## Authentication bypass via information disclosure

To solve this lab we need to wrap our head around `TRACE` HTTP method: 

https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/TRACE

It is used for debbuging and allow to retrieve the message that the server received.

We can perform `TRACE /admin` request and reveal `X-Custom-Ip-Authorization` request header added probably by application proxy. Its value was my public IP address.

This may be used to determine whether or not the request came from the localhost IP address or from the internet.

We can perform `GET /admin` request adding `X-Custom-Ip-Authorization: 127.0.0.1` header and we receive 200 response with admin panel. 

We can edit Burp proxy settings to append this header to every request or simply finish the lab via Repeater.

## Information disclosure in version control history

We can navigate to `/.git` endpoint and reveal its presence.

Download the repository file and navigate to it:

```
wget -r https://0a2c00e20443188882e69318007e00a6.web-security-academy.net/.git
```

Since this is regular git repository, we can use `tig` tool, in order to easily browse commit names and their content.

Other tools could be used to browse all commits in case the password would be present in a detached one.

Here the password is simply present in `Remove admin password from config` commit, so we can grab it and login as `administrator`.
