# Access Control

- https://portswigger.net/web-security/access-control
- https://portswigger.net/web-security/access-control#vertical-privilege-escalation
- https://portswigger.net/web-security/access-control#horizontal-privilege-escalation
- https://portswigger.net/web-security/access-control/idor

## Unprotected admin functionality

Looking at `/robots.txt` we cn see that `/administrator-panel` is disabled there.

Once we access it we enter it we can see that it is not protected at all and we can delete a user and solve the lab.

## Unprotected admin functionality with unpredictable URL

Once we see a page source of the Home page, we can see a script appending link `/admin-o099r6` to the admin panel if the user is logged in as admin.

We can access it, since there are no protections in place, and solvethe lab.

## User role controlled by request parameter

On login `Admin` cookie is set with value of `false`. Setting it to `true` and reloading a page creates `Admin Panel` link, and allows us to access it and use it.

## User role can be modified in user profile

`POST /my-account/change-email` request has a json body containing email field only, but responds with json body containing more keys:

```
{
    "username": "wiener",
    "email": "wiener@normal-user.net",
    "apikey": "OUr4KiCERJQXurstgDQ6J1JOrpbHaV9r",
    "roleid": 1
}
```

We can try to modify the request and pass additional `roleid` param.

```
{
    "email":"wiener@normal-user.net",
    "roleid": 0
}
```

Responds with: `"Role ID must be in range 1-127"`, so trying further `"roleid": 2` we get success and the response contain newly set `roleid` and we get access to the admin panel.

## URL-based access control can be circumvented

Accessing `/admin` page results in `Access denied` response.

Changing request method to `PUT`, `POST`, `TRACE`, ... did not allow us to bypass this.

By making request `GET /` and adding `X-Original-Url: /admin` header we are able to access the admin panel. 

Front-end proxy system must not support `X-Original-Url` header and takes for validation the path from `GET /` and accepts it. Back-end system must support it and overwrites the path with `X-Original-Url` header value `/admin` granting us access.

To solve the lab we need to perform `GET /?username=carlos` (note that query params must be passed here) with `X-Original-Url: /admin/delete` header.

## Method-based access control can be circumvented

Logged in as `administrator` to familiarize with admin panel. Performing `POST /admin-roles` with body `username=carlos&action=upgrade` will elevate user privillages, but the server will accept also the `GET /admin-roles?username=carlos&action=upgrade` request and process it the same way.

Logging now as `wiener` and accessing the `/admin` page we receive unauthed error.

Configuration must not allow `GET /admin` and `POST /admin-roles` requests to not admin users, but since we can change roles also with `GET /admin-roles`, we can bypass this protection and simply got to `/admin-roles?username=wiener&action=upgrade` as `wiener`.

## User ID controlled by request parameter

After login `/my-account?id=wiener` directs us to our user details page.

Simply changing user id `/my-account?id=carlos` shows us the user details page of other user.

## User ID controlled by request parameter, with unpredictable user IDs

Logging in and going to user details page we can see that now user is referenced via hard to guess UUID: `/my-account?id=512b66e0-e945-46be-8aa2-0284a138e0c8`, so in order to try to access another user account we need to find other users UUIDs.

Browsing through the posts we can notice that they have authors pointing to users and the app allows us to filter for posts made by certain users by providing their UUID. For example `carlos` posts link to `/blogs?userId=1ccc5d08-134f-4602-890b-cf3dd8864c34` page.

Now we can try to access user details page using carlos UUID: `/my-account?id=1ccc5d08-134f-4602-890b-cf3dd8864c34` and grab their API key.

## User ID controlled by request parameter with data leakage in redirect

After login `/my-account?id=wiener` directs us to our user details page.

Now trying to access `/my-account?id=carlos` we receive 302 redirect status, but the body contains full `carlos` user details page containing their API key.

## User ID controlled by request parameter with password disclosure

After login `/my-account?id=wiener` directs us to our user details page and contains our user password in `password` type input with functionality for changing it.

Going to `/my-account?id=administrator` we can steal their password and login as them to solve the lab.

## Insecure direct object references

Going to the Live Chat functionality we can chat with a bot and then save the transcript of the conversation. Downloading it is done via `GET /download-transcript/2.txt`.

By changing the filename we can try to access different users chat transcripts saved previously.

`GET /download-transcript/1.txt` retrieves us the chat history in which a user provided their password. We now login as `carlos` using this password to solve the lab.

## Multi-step process with no access control on one step

Reviewing the admin functionality shows that granting admin privilages to other users is done by two steps:
 - `POST /admin-roles` with params `username=carlos&action=upgrade`
 - `POST /admin-roles` with params `action=upgrade&confirmed=true&username=carlos`

Now we can login as regular user `wiener` and try to redo the steps.

First request results in 401 response, but the second one with `confirmed=true` param bypasses authorization check and results in success solving the lab.

## Referer-based access control

Reviewing the admin functionality shows that granting admin privilages to other users is done by `GET /admin-roles?username=carlos&action=upgrade` request. With the `Referer: https://0ae700e50401dc8c81e1252200940011.web-security-academy.net/admin` header.

We can observe that changing / removing `Referer` header results in 401 error.

Now logging as wiener and performing the same request `GET /admin-roles?username=wiener&action=upgrade` with `Referer: https://0ae700e50401dc8c81e1252200940011.web-security-academy.net/admin` header results in success and solves the lab.
