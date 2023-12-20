# Race conditions

- https://portswigger.net/web-security/race-conditions
- https://portswigger.net/research/smashing-the-state-machine
- https://www.youtube.com/watch?v=tKJzsaB1ZvI
- https://github.com/PortSwigger/turbo-intruder/blob/master/resources/examples/default.py
- https://github.com/PortSwigger/turbo-intruder/blob/master/resources/examples/race-single-packet-attack.py

## Limit overrun race conditions

While making a purchase we are able to submit a coupon for 20% discount. 

`POST /cart/coupon` request applying the coupon can be intercepted and once we do that we can perform `single-packet-attack` using Burp Turbo Intruder, which makes use of HTTP2 streaming, stacking multiple requests in one connection, `Nagle's algorithm` and `last byte synchronization`. This send 20-30 request without their last byte, each in different stream. Then in the single frame send the ending of each frame in different streams, causing the server to accept and start calculating them all in nearly the same time.

Performing this attack for that requests reveals that there is not well handled time difference between accepting the coupon and devalidating it, which causes to apply the same coupon multiple times, solving the lab.
