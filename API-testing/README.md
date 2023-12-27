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
