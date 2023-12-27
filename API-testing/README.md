# API Testing

- https://portswigger.net/web-security/api-testing

## Exploiting an API endpoint using documentation

Once logging in and changing our email we can notice `PATCH /api/user/wiener` request.

Now navigating to `/api` endpoint we notice full REST API description with tools for testing it.

Using `DELETE /user/[username: String]` request for `carlos` solves the lab.


## Finding and exploiting an unused API endpoint

While browsing the page we can observe that `api/productPrice.js` script is loaded, containing the link to `/api/products/{productId}/price`.

Performing `GET /api/products/1/price` request responds with full product details in json format.

Now testing which methods are also allowed for this endpoint we discover, that `PATH /api/products/1/price` responds not in 404, but in detailed error response. 

Following errors guidelines we can perform `PATH /api/products/1/price` with body `{"price": 0}` to change the product price and solve the lab

## Exploiting a mass assignment vulnerability

We can observe that accessing the cart with `GET /api/checkout` request, responds with:

```
{"chosen_discount":{"percentage":0},"chosen_products":[{"product_id":"4","name":"Vintage Neck Defender","quantity":1,"item_price":6604}]}
```

Submiting the basket is done with `POST /api/checkout` request with body:

```
{"chosen_products":[{"product_id":"4","quantity":1}]}
```

We can notice that response contains additional `chosen_discount` field and others are similar. 

Additional nice note from the solution: 
Change the `chosen_discount` value to the string `"x"`, then send the request. Observe that this results in an error message as the parameter value isn't a number. This may indicate that the user input is being processed. 

Now performing `POST /api/checkout` with body shown below instead, makes mass assignment and adds the 100% discount solving the lab.

```
{"chosen_discount":{"percentage":0},"chosen_products":[{"product_id":"4","name":"Vintage Neck Defender","quantity":1,"item_price":6604}]}
```

Making a `POST /api/checkout` with price set to 0 did not done the trick for me unfortunately.

## Exploiting server-side parameter pollution in a query string

`POST /forgot-password` takes `username` parameter in the body.

Trying to reset password for admin performs the request with `username=administrator` in the body.

We suspect that the backed may take all passed parameters and using them it performs another request to the backed API. During that process it will decode them, so because of that we can try to add other parameters to the backend API request.

Appending another `username` param URL encoded does not change anything regarding response: `username=administrator%26username%3dcarlosss`.

Appending different param, named for example `x`, to the request results in the error: `username=administrator%26x%3dcarlosss` -> `Parameter is not supported.`. 

All this means that we are able to inject different params to the request, but the first occurence is used always, which prevenst us from overwriting anything.

Appending URL encoded `#` results in `Field not specified`.

Now by adding `field` param with random value before the `#` results in `Invalid field` error. But specifing `field=email` results in the same response as original, so this must have been the default setting.

By making the request with `field=username` the username is retrieved, and by making it with `field=reset_token` (found in loaded in the page `forgotPassword.js` script) it responds with the reset token value for user, which allows us to reset the admin password and solve the lab.

Resulting `username` param ended up looking like this: `username=administrator%26field%3dreset_token%23`. URL decoded: `username=administrator&field=reset_token#`
