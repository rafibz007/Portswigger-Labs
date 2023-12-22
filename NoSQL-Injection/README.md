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
