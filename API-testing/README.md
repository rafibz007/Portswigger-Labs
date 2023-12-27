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

