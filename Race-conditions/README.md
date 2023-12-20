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

## Multi-endpoint race conditions

In this lab, the key is to align processing time of different endpoints. This can be done by warming up the connection, sending multiple requests to add a delay in processing all of them etc.

This time the app has a logic flaw, which allow adding items to the basket after payment validation.

Using Burp Repeater group requests we can construct a group of requests and send them in sequence or as `single-packet attack`.

Here we will add 1 gift card to the basket via `POST /cart` request and then create a group of requests with 1 `POST /cart/checkout` request for submiting the payment and 19 `POST /cart` requests, but this time with `productId` pointing to the jacket, not the giftcard.

This required a couple of tries, but each time we could observe strange app behaviours, like not all products added to the basket (for example I was able to submit the basket successfull as first request, but only 4 of 19 jackets were added to the basket afterwards), not always errors regarding empty basket etc.

After 5th try I was able to successful buy a jacket and be left with -1200$ in the account.

## Single-endpoint race conditions

To identify differences between email change requests I've used email template system shown below, with `i` as a request number in Turbo Intruder

```
"wiener+"+str(i)+"@exploit-0abf00d004864ba3832818bb01fe0013.exploit-server.net"
```

By performing multiple change email address requests sequencialy we cannot observe any strange behaviour, we receive a couple of emails one by one for each requested email change. Email recipent match with email content and verification link.

Once we perform multiple email change requests in parrarel (using `single-packet attak`), we can see that the behaviour differs. Now some of the emails with recipent identifier `8` received validation links for email with identifier `6`. It seems like all recipents received the email, but not all of them for their account, so we may conclude that the email changing fucntion is receiving the email that the mail should be sent to as a parameter, but email contant may be drawn from some shared space.

Now we can try to perform `single-paket attack` sending 10 packets with email change for `carlos@ginandjuice.shop` and 10 for `wiener@exploit-0a2a005504941a6a821cff27015b0015.exploit-server.net`. This can be done via Turbo Intruder or grouped requests in the Repeater sent in parrarel.

After that we can check the email and try to confirm verification token for `carlos@ginandjuice.shop` email, which will successfully change our email and grant us admin privillages.

## Exploiting time-sensitive vulnerabilities

PHP's native session handler module only processes one request per session at a time, so in order to test race conditions I was required to create multiple sessions with different csrf tokens.

By performing a few sequential forgot password requests we do not see anything strange about the app behaviour. 

But when performing a couple of those requests in parrarel, we can observe two received emails with the same token.   

Once we test to reset our password one time providing our email and one time the username, we sometime see two email with the same token and some time with different once. We can assume, that the generated token maybe randomized only by the timestamp.

Now using the script below, we can try to activate password change functionality for us `wiener` and for `carlos`, hoping to hit the same timestamp and receive the same token, which will allow change the user for other user.

```
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
    
    for session_id, csrf, uname in [('fpU9eJNCrVPH1oGBJsgUGkXcsCu9aTb7', 'CGsdoO0mHBv98drRzyCqwc5iyQ7yCkGb', 'wiener'), ('Y63zivWxO89NXZIm3TzV3HfDDVPQ7E5g', 'KLSRuP8v1GeQFZ3XkUKVSlfbb5LsrWxU', 'carlos')]:
        engine.queue(target.req, [session_id, csrf, uname], gate='race1')

    # once every 'race1' tagged request has been queued
    # invoke engine.openGate() to send them in sync
    engine.openGate('race1')


def handleResponse(req, interesting):
    table.add(req)
```

After couple of tries we are able to access `carlos` password change with the same token we received in the email.
