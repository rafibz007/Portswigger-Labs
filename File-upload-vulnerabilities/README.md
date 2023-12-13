# File upload vulnerabilities

- https://portswigger.net/web-security/file-upload
- https://portswigger.net/web-security/file-upload#exploiting-flawed-validation-of-file-uploads
- https://portswigger.net/web-security/file-upload#uploading-files-using-put
- https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/php-tricks-esp#rce-via-.httaccess

## Remote code execution via web shell upload

After logging in we can upload the avatar.

File upload does not perform any validation and allow to upload any type of file, which is them available at `/files/avatars/<filename>.<extension>`

When I have uploaded .txt file and accessed it the server responded with `Content-Type: text/plain` header and file content in the body.

We can check whether the server will execute php file when serving them. (for now not bothering about potential directory traversal or IDOR allowing to access other avatars/files)

Upload `file-1.php` and access it at `/files/avatars/file-1.php`.

Additionally it is possible to use `cmd` query params to execute other command on the system.

## Web shell upload via Content-Type restriction bypass

Now once we try to upload a wrong file we receive an error

```
Sorry, file type text/plain is not allowed Only image/jpeg and image/png are allowed
```

By intercepting the request or using the Repeater we can change `Content-Type` of the multipart form field containing our file to `image/png` (not the `Content-Type` of the entire request, this should be set to `multipart/form-data; boundary=...`) and this will result in a success.

Upload `file-1.php` changing `Content-Type` to `image/png` and access it at `/files/avatars/file-1.php`.

## Web shell upload via path traversal

This time the app does not validate the type of the file at all.

After uploading `file-1.php` and accessing it at `/files/avatars/file-1.php` it responds with the file content and does not execute the php code.

On uploading the form data image we can modify `filename` in `Content-Disposition` part and hope that the application uses it insecurely during file saving.

Changing `filename` to `../file-1.php` results in `File saved in avatars/file-1.php` response and the file is still in `/files/avatars` directory. But encoding `../` to `..%2f` does the trick and results in `File saved in avatars/../file.php`. The file is then accessible in `/files` endpoint / directory and it executes the code.

*Also what could have been tried is to upload `.htaccess` file that would overwrite permissions and allow php execution in `files/avatars` directory.*

## Web shell upload via extension blacklist bypass

This the app provides some kind of validation for uploaded files.

When uploading file with php extension we will receive and error that php files are forbidden. Uploading php5 extension will not fail, but the file will not be executed when accessed at `/files/avatars/file-1.php5`

From response header `Server: Apache/2.4.41 (Ubuntu)` we know that what is running on the backend is probably Apache

We can upload `.htaccess` file that will overwrite local settings and instruct Apache server to execute files with .php5 extension. After that uploading `file-1.php5` and accessing it at `/files/avatars/file-1.php5` results in RCE solving the lab.

## Web shell upload via obfuscated file extension

Trying to upload `file-1.php` as the avatar results in 403 Forbidden response. Changing form field `Content-Type` to `image/png` does not bypass this protection. Extension may be checked.

Intercepting the request and changing uploaded form field `filename` to `file-1.php%00.png` (injecting null byte with .png extension at the end) bypasses the defense and responds with `The file avatars/file-1.php has been uploaded`. 

Validation maybe written in a high-level language like PHP or Java, but the server processes the file using lower-level functions in C/C++. This difference passes validation but when writing a file detects null byte and treats it like the end of a string.

Now we access the file at `/files/avatars/file-1.php` and see that it is being executed, which solves the lab.

## Remote code execution via polyglot web shell upload

Trying to upload `file-1.php` as the avatar results in 403 Forbidden response. Changing form field `Content-Type` to `image/png` does not bypass this protection. Obfuscating filename extension did not work.

We can try to prepare png file with metadata containing malicious payload which hopefully will be executed once uploaded.

```
exiftool -all= files/cat.jpg && exiftool -comment="$(cat files/file-1.php)" files/cat.jpg
```

Checking the file we can see our payload was successfully written:

```
exiftool files/cat.jpg
```

Now uploading a `cat.jpg` file was obviously successful, but of course will not be executed. Now we can try to change the filename to `cat.php` and upload this, which also is a success!

Now we can access the file at `/files/avatars/cat.php` and see that it was executed, which solves the lab.
