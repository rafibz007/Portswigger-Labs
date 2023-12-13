# File upload vulnerabilities

- https://portswigger.net/web-security/file-upload
- https://portswigger.net/web-security/file-upload#exploiting-flawed-validation-of-file-uploads
- https://portswigger.net/web-security/file-upload#uploading-files-using-put

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

