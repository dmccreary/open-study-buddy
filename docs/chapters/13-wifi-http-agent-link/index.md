---
title: "Wi-Fi, HTTP, and Connecting to the Agent"
description: "How the Pico joins the school Wi-Fi in station mode, gets an IP address on the local network, and sends JSON to the buddy server with an HTTP POST to a REST endpoint, by hand and with the requests library, and why plain HTTP is acceptable only on a trusted classroom network."
generated_by: claude skill chapter-content-generator
date: "2026-10-18 13:08:28"
version: 1.11
---

# Wi-Fi, HTTP, and Connecting to the Agent

## Summary

This chapter connects the Pico to the school network. Students join Wi-Fi, understand IP addresses and the local network, and exchange JSON with the buddy server using HTTP POST and the requests library. They also learn why plain HTTP is acceptable only on a trusted classroom network.

## Concepts Covered

This chapter covers the following 11 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| JSON | 18 |
| Wi-Fi Connection | 132 |
| Network Station Mode | 1 |
| IP Address | 128 |
| HTTP Protocol | 74 |
| Local Network | 7 |
| HTTP POST | 53 |
| REST Endpoint | 1 |
| Plain HTTP LAN Use | 1 |
| mDNS Discovery | 1 |
| requests Library | 8 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 2: MicroPython Review for Embedded Systems](../02-micropython-review/index.md)
- [Chapter 4: The Pico Kit Hardware and Wiring](../04-pico-kit-hardware/index.md)

---

## The Device Leaves Its Island

Until now everything ran on the Pico itself: the microphone, the display, the speaker. But the part that knows about tests and due dates, the buddy server, lives on another computer. This chapter builds the road between them: joining the school's Wi-Fi, finding the server, and sending it a question in a form it understands.

!!! mascot-welcome "Let's Make the Call"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    By the end of this chapter your Pico will join the school Wi-Fi, ask the buddy server "when is my next test?", and print the answer on the round display. Let's listen closely! A network is just two programs agreeing on what to say.

Here is the whole trip in seven steps, with the part that does each one. Every step is a section of this chapter.

| Step | What happens | Who does it | Section |
|------|--------------|-------------|---------|
| 1 | The Pico joins the Wi-Fi network and is given an address | Pico and the access point | Joining the Network |
| 2 | The Pico works out where the server is | Pico | IP Addresses |
| 3 | The question is written as JSON text | Pico | JSON: A Shape Both Sides Agree On |
| 4 | The Pico opens a connection and sends an HTTP POST | Pico | HTTP: The Language of the Question |
| 5 | The server reads the request and decides on a reply | Buddy server | The Buddy Server's Endpoint |
| 6 | The server sends the reply back | Buddy server | The Buddy Server's Endpoint |
| 7 | The Pico reads the reply, closes the connection, and shows the answer | Pico | Reading the Reply Safely |

## Joining the Network

A **Wi-Fi connection** is the link between the Pico's radio and an *access point*, the box (or ceiling unit) that the school's network hangs from. The Pico 2 W's radio is the separate wireless chip from Chapter 4. It speaks 2.4 GHz Wi-Fi only, so a network that offers only 5 GHz will never appear in a scan.

### Network Station Mode

**Network station mode** means the Pico joins somebody else's network, the way a phone or laptop does. MicroPython gives it a name, `network.STA_IF` ("station interface"). The other choice, `network.AP_IF`, makes the Pico an *access point* that other devices join. This book always uses station mode, because the buddy server is on the school's network, not on the Pico's.

```python
import network

wlan = network.WLAN(network.STA_IF)    # station mode
wlan.active(True)                      # switch the radio on
wlan.connect(ssid, password)           # start joining; this returns at once
```

`connect()` does not wait. It starts the join and returns, and the join takes anywhere from a fraction of a second to several seconds. A program that assumes it is finished on the next line sends its first request into nothing. Instead, poll `wlan.status()` and give up after a time limit. The helper module `wifi_link.py` in `src/chapters/13-wifi-http-agent-link/` does exactly this, and every other file in the chapter uses it.

```python
start = time.ticks_ms()
while True:
    code = wlan.status()
    if code == 3:                      # connected, with an IP address
        return wlan
    if code < 0:                       # a definite failure
        raise WifiError(code)
    if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
        raise WifiError(code, "gave up")
    time.sleep_ms(200)
```

The loop has three ways out: success, a definite failure, and the clock running out. The code is a number from the CYW43 wireless driver, and each value means something you can show on the display.

| `status()` | `network.STAT_` name | Meaning | What the device should do |
|-----------|----------------------|---------|---------------------------|
| 0 | `STAT_IDLE` | Not trying | Call `connect()` |
| 1 | `STAT_CONNECTING` | Joining | Wait, with the time limit running |
| 2 | (none) | Joined, no IP address yet | Wait; the address is on its way |
| 3 | `STAT_GOT_IP` | Connected | Carry on |
| -1 | `STAT_CONNECT_FAIL` | Failed, reason unknown | Show an error; retry later |
| -2 | `STAT_NO_AP_FOUND` | Network name not found | Check the name, the distance, and the 2.4 GHz rule |
| -3 | `STAT_WRONG_PASSWORD` | Wrong password | Stop and show it; retrying cannot help |

*Worked example.* A student mistypes the password in `secrets.py`. The loop starts at status 1, and after the access point rejects the password the driver reports -3. `wifi_link.connect()` raises `WifiError` with the text "wrong password", and the display's status region says so, instead of spinning for ever. A student whose school network is 5 GHz only gets -2, "network not found", even though the name is correct. The two fixes are very different, which is why the code keeps the numbers apart. `01-wifi-connect.py` prints each state with the milliseconds since the join began, so you can see how long your network takes. That is a measurement for you to make; the book does not know your access point.

!!! mascot-tip "Check the Signal First"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    When a connection is flaky, print `wlan.status("rssi")` before suspecting your code. It returns the signal strength in dBm, a negative number that gets more negative as the signal weakens. As a rule of thumb, a reading much weaker than -80 dBm is a poor link.

The Wi-Fi name and password come from `secrets.py` on the Pico (`wifi_ssid` and `wifi_pass`), the same file the kit's other programs use. It is listed in the repository's `.gitignore` so it is never committed.

!!! mascot-warning "Never Print the Password"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    A `print(secrets.wifi_pass)` left in a program ends up in screenshots, forum posts, and shared logs. Print the network *name* only, as `01-wifi-connect.py` does, and keep `secrets.py` out of every commit.

## IP Addresses

Once the Pico is connected it has an **IP address**, the number that identifies it on the network, in the way a house number identifies a house on a street. An IPv4 address is four numbers from 0 to 255 separated by dots, such as `192.168.1.23`. That is 32 bits, packed as four bytes. The Pico does not choose its address. A *DHCP server*, usually built into the school's router, hands one out for a limited time (a *lease*) when the Pico joins.

`wlan.ifconfig()` returns four values, always in this order.

| Position | Name | Example | What it is |
|----------|------|---------|------------|
| 0 | IP address | `192.168.1.23` | This Pico's address |
| 1 | Netmask | `255.255.255.0` | Says which part of an address names the network |
| 2 | Gateway | `192.168.1.1` | The router: the way out of this network |
| 3 | DNS server | `192.168.1.1` | Turns names like `example.com` into numbers |

### The Netmask

Part of every address names the *network* and part names the *device on it*. The **netmask** says where the line falls. Write the address and the mask in binary, and keep only the bits where the mask has a 1. The result, the **network address**, is the same for every device on the same network.

*Worked example.* The Pico is `192.168.1.23` and the server is `192.168.1.50`, both with mask `255.255.255.0`. The mask keeps the first three numbers and throws away the last one.

| Device | Address | Mask | Kept (network address) |
|--------|---------|------|------------------------|
| Pico | 192.168.1.**23** | 255.255.255.0 | 192.168.1.0 |
| Server | 192.168.1.**50** | 255.255.255.0 | 192.168.1.0 |
| Another room's device | 192.168.**2**.50 | 255.255.255.0 | 192.168.2.0 |

The Pico and the server have the same network address, so they are on the **same network** and can talk directly. The third device keeps `192.168.2.0`, a different network, so a message to it must go through the gateway.

Masks do not always fall between whole numbers. Take `255.255.240.0`, where the third number of the mask is `240`, which is `11110000` in binary. It keeps the top 4 bits of the third number and drops the bottom 4. Then `172.16.5.5` and `172.16.15.1` both keep `172.16.0.0`, because 5 and 15 are both below 16, while `172.16.16.1` keeps `172.16.16.0` and is on a different network. The number of host bits left over sets the size of the network: with \( h \) host bits, there are \( 2^h - 2 \) usable device addresses, because the all-zeros address names the network and the all-ones address is for broadcasting.

| Netmask | Host bits \( h \) | Usable addresses \( 2^h - 2 \) | Typical use |
|---------|---------|-------------------------|-------------|
| 255.255.255.0 | 8 | 254 | One classroom or lab |
| 255.255.255.128 | 7 | 126 | Half a classroom subnet |
| 255.255.240.0 | 12 | 4,094 | A school wing |
| 255.255.0.0 | 16 | 65,534 | A whole campus |

`02-ip-and-subnet.py` does the arithmetic with shifts and masks, runs on your computer or the Pico, and on the Pico also checks whether your `BUDDY_HOST` is on the Pico's own network. If it is not, the first thing to suspect is a wrong address in `buddy_config.py`, or a server on a separate guest network.

### The Local Network

A **local network** (LAN, local area network) is a group of devices that can reach each other directly, without going through the internet. A classroom's Wi-Fi network is one. Local networks use *private* address ranges that internet routers refuse to forward, defined by a standard called RFC 1918.

| Range | Netmask length | Where you meet it |
|-------|----------------|-------------------|
| 10.0.0.0 to 10.255.255.255 | 10.0.0.0/8 | Schools, campuses |
| 172.16.0.0 to 172.31.255.255 | 172.16.0.0/12 | Some school districts |
| 192.168.0.0 to 192.168.255.255 | 192.168.0.0/16 | Homes, small labs |

Notice that `172.32.0.9` is *not* private even though it starts with `172`; the range stops at 172.31. If `ifconfig()` shows an address outside these ranges, the Pico is probably not on a classroom network at all.

Because the Pico gets its address from DHCP, the *server's* address can change when the router restarts, which would silently break `BUDDY_HOST`. The fix is a **DHCP reservation** on the router (the router always hands the server the same address), or a fixed address outside the router's DHCP range. Ask the school's network administrator, who will want to know the server's MAC address.

#### Diagram: Same-Subnet Checker

<details markdown="1">
<summary>Same-Subnet Checker</summary>
Type: microsim
**sim-id:** same-subnet-checker<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** calculate<br/>
**Learning Objective:** The learner will calculate whether two IPv4 addresses are on the same network, given a netmask, in 8 cases, with at least 7 of 8 correct.

**Prerequisites:** IP address, netmask, network address, same network, binary form of a number from 0 to 255 (all defined in this chapter above this block; binary numbers are in Chapter 3).

**Evidence of Mastery:** For each of the 8 cases the learner chooses "same network" or "different networks", then types the network address of the first device. A case is correct when both answers match the Answer columns in Content. Mastery is 7 of 8 correct on the first attempt. Using the explorer (typing any addresses and watching the binary AND) is exploration, not evidence.

**Misconceptions:** (1) Addresses that start with the same number are always on the same network. (2) A mask can only fall between whole numbers. (3) The all-zeros and all-ones device addresses can be given to a device.

**Instructional Rationale:** Apply-level calculation requires the learner to carry out the mask-and-compare procedure on new numbers. Showing the two addresses and the mask in binary, with the mask's 1 bits highlighted, ties the procedure to what the mask keeps, and asking for the network address as well as the yes/no answer shows the work.

**Content:**

The explorer shows an address, a second address, and a netmask. Each is shown as four numbers and as four groups of 8 bits. The sim computes the network address of each as the bitwise AND of the address and the mask. The two addresses are on the same network when the two network addresses are equal.

| # | First address | Netmask | Second address | Same network? | Network address of the first | Why (shown as feedback) |
|---|---|---|---|---|---|---|
| 1 | 192.168.1.23 | 255.255.255.0 | 192.168.1.50 | same | 192.168.1.0 | The mask keeps the first three numbers, and both start 192.168.1. |
| 2 | 192.168.1.23 | 255.255.255.0 | 192.168.2.50 | different | 192.168.1.0 | The third numbers, 1 and 2, differ and the mask keeps them. |
| 3 | 10.4.7.88 | 255.255.0.0 | 10.4.200.9 | same | 10.4.0.0 | The mask keeps only 10.4, and both start 10.4. |
| 4 | 10.4.7.88 | 255.255.255.0 | 10.4.200.9 | different | 10.4.7.0 | The same two addresses, but this mask also keeps the third number, 7 and 200. |
| 5 | 172.16.5.5 | 255.255.240.0 | 172.16.15.1 | same | 172.16.0.0 | 240 is 11110000, so only the top 4 bits of the third number are kept; 5 and 15 are both 0000. |
| 6 | 172.16.5.5 | 255.255.240.0 | 172.16.16.1 | different | 172.16.0.0 | 16 is 00010000, so its kept bits are 0001, not 0000. |
| 7 | 192.168.1.200 | 255.255.255.128 | 192.168.1.20 | different | 192.168.1.128 | 128 is 10000000: 200 keeps the top bit (1) and 20 keeps 0. |
| 8 | 192.168.1.130 | 255.255.255.128 | 192.168.1.200 | same | 192.168.1.128 | 130 and 200 are both 128 or more, so both keep the top bit 1. |

For exploration the learner can type any two addresses (each number 0 to 255) and choose a netmask from 255.255.255.0, 255.255.255.128, 255.255.240.0 or 255.255.0.0. The default is 192.168.1.23, 255.255.255.0 and 192.168.1.50.

**Provenance:** The arithmetic is the chapter sections "The Netmask" and "The Local Network", and the same cases (1 to 6) are in the table printed by `02-ip-and-subnet.py`. The addresses are illustrative, and the sim labels them "illustrative."

**Rules:** The network address is the bitwise AND of each of the four numbers of the address with the matching number of the mask. Two addresses are on the same network when their network addresses are equal. If the learner types a number outside 0 to 255, the sim ignores the change and keeps the previous value.

**Learner Activity:**

1. The learner opens the explorer and changes the second address's last number, watching its bits and the kept bits change.
2. The learner changes the netmask from 255.255.255.0 to 255.255.0.0 and notices which cases flip from different to same.
3. The learner starts the 8 cases. Case 1 is shown.
4. The learner chooses same or different, types the first address's network address, and submits.
5. The sim highlights the kept bits of both addresses and shows the Why text.
6. After case 8, the sim shows the score. The learner should notice that cases 3 and 4 use the same two addresses and have opposite answers.

**Feedback:** 8 cases, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. They are <same or different>, and the network address is <network address>: <Why>". The answer is revealed right after each submission, and a running score "n of 8" is shown.

**Starting State:** The explorer shows 192.168.1.23 and 192.168.1.50 with 255.255.255.0, with the question "Are these two on the same network?"

**Chapter Anchors:** The chapter states that the netmask keeps the network part of an address, that 255.255.240.0 keeps the top 4 bits of the third number, that 172.16.5.5 and 172.16.15.1 are on the same network under that mask while 172.16.16.1 is not, and that a network with \( h \) host bits has \( 2^h - 2 \) usable addresses.
</details>

!!! mascot-encourage "Binary Makes Masks Click"
    ![Sage encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    Netmasks that fall inside a number, like 240, feel strange the first time. If the AND is slippery, write the two numbers out in eight bits, as you did for sample values in Chapter 3, and cross out the bits the mask throws away.

## JSON: A Shape Both Sides Agree On

The Pico and the server are different programs in different places, so they need a shared way to write down a question. **JSON** (JavaScript Object Notation) is a plain-text format for labeled values. It has objects in curly braces `{ }` holding name and value pairs, lists in square brackets `[ ]`, strings in double quotes, numbers, `true`, `false`, and `null`. MicroPython reads and writes it with the same `json` module as a computer.

```python
import json

request = {"device": "desk-07", "kind": "question", "text": "when is my next test"}
text = json.dumps(request)      # dict -> text, ready to send
back = json.loads(text)         # text -> dict again
```

This is the Chapter 1 request-reply contract, now defined for real. A request has exactly three fields, and a reply has exactly three.

| Direction | Field | Type | Meaning |
|-----------|-------|------|---------|
| Request | `device` | string | Which desk device is asking (`DEVICE_ID`) |
| Request | `kind` | string | `"question"` in this chapter |
| Request | `text` | string | What the student said, already as text |
| Reply | `speak` | string | The sentence to say aloud |
| Reply | `show` | string | A short line for the display, 30 characters or fewer |
| Reply | `next_mode` | string | One of `clock`, `listening`, `thinking`, `speaking`, `settings` (Chapter 7's modes) |

Three habits keep JSON from causing trouble. First, **count bytes, not characters**: the text `{"device": "desk-07", "kind": "question", "text": "when is my next test"}` is 73 bytes, and HTTP will need that number. An accented letter such as the `é` in "café" takes two bytes in UTF-8, so call `.encode()` before you count. Second, **expect bad input**: single quotes, a trailing comma, or a missing brace all make `json.loads` raise `ValueError`, and a Pico must catch it instead of crashing on a bad reply. Third, **do not rely on formatting**: MicroPython's `json.dumps` has no `indent` option, so the output is always one line.

`03-json-contract.py` runs these checks on your computer or the Pico: the request is 73 bytes, the reply `{"speak": "Your next test is Biology on Friday.", "show": "Biology test: Friday", "next_mode": "clock"}` is 103, and four malformed texts are all rejected.

## HTTP: The Language of the Question

An address finds the server's computer, but a computer may run many programs. A **port** is a number that picks one: the buddy server listens on port 8080. The pair (address, port) is where the conversation happens.

The **HTTP protocol** (HyperText Transfer Protocol) is the set of rules for what is said on that connection. It is a request and a reply, and the client always speaks first. The Pico is the *client*: it opens a TCP connection to the server, sends a request, and waits. The buddy server is the *server*: it answers one request and (in our version) closes the connection. HTTP is *stateless*: the server remembers nothing between requests, which is why every request carries `device`.

An HTTP request is plain text with four parts, always in this order.

| Part | Example | Job |
|------|---------|-----|
| Request line | `POST /v1/ask HTTP/1.0` | Method (what to do), path (where), HTTP version |
| Header lines | `Content-Length: 73` | Facts about the request, one `Name: value` per line |
| Blank line | (just `\r\n`) | Marks the end of the headers |
| Body | `{"device": ...}` | The data itself (empty for some methods) |

Each line ends with two characters, carriage return and line feed, written `\r\n`. Here is exactly what `04-raw-http-post.py` builds for the default settings. The `<CRLF>` marks are not sent as text; they show where `\r\n` goes.

```text
POST /v1/ask HTTP/1.0<CRLF>
Host: 192.168.1.50:8080<CRLF>
Content-Type: application/json<CRLF>
Content-Length: 73<CRLF>
Connection: close<CRLF>
<CRLF>
{"device": "desk-07", "kind": "question", "text": "when is my next test"}
```

That is 121 bytes of head (119 for the five lines and 2 for the blank line) plus the 73-byte body, 194 bytes in all. The reply has the same shape, with a *status line* in place of the request line.

```text
HTTP/1.0 200 OK<CRLF>
Content-Type: application/json; charset=utf-8<CRLF>
Content-Length: 103<CRLF>
<CRLF>
{"speak": "Your next test is Biology on Friday.", "show": "Biology test: Friday", "next_mode": "clock"}
```

The three-digit **status code** tells the client how things went, by its first digit: 2 means success, 4 means the *client* made a mistake, and 5 means the *server* failed.

| Code | Name | When the buddy server sends it |
|------|------|--------------------------------|
| 200 | OK | The request fit the contract and here is the reply |
| 400 | Bad Request | The body is not valid JSON, or fields are missing or wrong |
| 404 | Not Found | No such path |
| 405 | Method Not Allowed | `GET` sent to a path that wants `POST` |
| 411 | Length Required | No `Content-Length` header |
| 413 | Content Too Large | The body is bigger than the server allows (2,048 bytes) |
| 500, 503 | Server error, busy | The server failed; trying again later may work |

!!! mascot-thinking "A Request Is Just Text"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Notice how little magic there is: a web request is a few lines of text that you could type by hand. Once you can read one, a failed request stops being mysterious, because the status code and the headers tell you which side made the mistake.

### HTTP POST

HTTP has several *methods*. **HTTP GET** asks for something and sends no body. **HTTP POST** sends data for the server to act on, with the data in the body. The buddy server needs the student's words, so the Pico uses POST. (A GET could carry the words in the URL, but URLs end up in logs and are limited in length, so the question belongs in the body.)

The one number a POST must get right is `Content-Length`: the count of bytes in the body. The server reads that many and stops. Get it wrong and one of two things happens.

| Header says | Body really has | What the buddy server does |
|-------------|-----------------|----------------------------|
| 73 | 73 | Reads all of it and answers 200 |
| 60 | 73 | Reads 60 bytes, finds the JSON cut off, and answers 400 |
| 90 | 73 | Waits for the 17 missing bytes while the Pico waits for an answer. Nothing happens until a timeout |

The third row is why every socket on the Pico needs a time limit, which Chapter 14 builds in properly.

`rawhttp.py` builds the request. It encodes the body first, so the number it writes is a byte count.

```python
def build_post(host, port, path, payload, extra_headers=None):
    body = json.dumps(payload).encode("utf-8")
    lines = [
        "POST {} HTTP/1.0".format(path),
        "Host: {}:{}".format(host, port),
        "Content-Type: application/json",
        "Content-Length: {}".format(len(body)),
        "Connection: close",
    ]
    head = "\r\n".join(lines) + "\r\n\r\n"
    return head.encode("utf-8") + body
```

`"\r\n".join(lines)` puts the line break between lines, and the extra `"\r\n\r\n"` ends the last header and adds the blank line. We say `HTTP/1.0` and `Connection: close` on purpose: the server closes the connection after its reply, so the Pico never has to work out where one reply ends and the next begins.

*Worked example.* Sending it with only a socket takes eight steps, and `05-socket-post.py` does all of them.

```python
addr = socket.getaddrinfo(host, port)[0][-1]   # ask for the (address, port) pair
sock = socket.socket()
sock.settimeout(8)                              # every wait gives up after 8 seconds
try:
    sock.connect(addr)
    sock.send(raw)                              # the 194 bytes above
    status, headers, body = rawhttp.read_response(sock, 2048)
finally:
    sock.close()                                # always, even after an error
```

`read_response` reads until it sees the blank line, splits the head into a status code and headers, then reads exactly `Content-Length` more bytes. It refuses a reply whose `Content-Length` is above 2,048, so a wrong server cannot fill the Pico's memory.

#### Diagram: HTTP Request Reader

<details markdown="1">
<summary>HTTP Request Reader</summary>
Type: microsim
**sim-id:** http-request-reader<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Understand<br/>
**Bloom Verb:** interpret<br/>
**Learning Objective:** The learner will interpret the parts of an HTTP POST request and its reply by answering 8 questions about the request text, with at least 7 of 8 correct.

**Prerequisites:** HTTP protocol, request line, header, blank line, body, Content-Length, status code, HTTP POST (all defined in this chapter above this block).

**Evidence of Mastery:** For each of the 8 questions the learner chooses one of three answers. An answer is correct when it matches the Correct answer column in Content. Mastery is 7 of 8 correct on the first attempt. Hovering over a line of the request to read its label is exploration, not evidence.

**Misconceptions:** (1) The blank line is optional decoration. (2) A wrong Content-Length is harmless. (3) A 4xx status means the server is broken. (4) The body can be longer than Content-Length says.

**Instructional Rationale:** Understand-level interpretation requires the learner to explain what a part of the message means in a concrete example, not to name it. Choosing the effect of a changed or wrong value makes the learner use the meaning of each part.

**Content:**

The request shown on screen, with its lines numbered:

| Line | Text |
|---|---|
| L1 | `POST /v1/ask HTTP/1.0` |
| L2 | `Host: 192.168.1.50:8080` |
| L3 | `Content-Type: application/json` |
| L4 | `Content-Length: 73` |
| L5 | `Connection: close` |
| L6 | (blank line) |
| L7 | `{"device": "desk-07", "kind": "question", "text": "when is my next test"}` |

The 8 questions, each with three choices:

| # | Question | Choices | Correct answer | Why (shown as feedback) |
|---|---|---|---|---|
| 1 | Which line says what the client wants done, and where? | L1, L2, L7 | L1 | The request line holds the method (POST), the path (/v1/ask) and the HTTP version. |
| 2 | Which line tells the server how many bytes of body to read? | L3, L4, L5 | L4 | Content-Length counts the body's bytes. |
| 3 | What does the blank line L6 do? | It ends the headers, so the body starts after it; it is optional; it separates two requests | It ends the headers, so the body starts after it | Without it the server would keep reading header lines. |
| 4 | Content-Length says 60 but the body is 73 bytes. What does the buddy server do? | Reads 60 bytes and answers 400 because the JSON is cut off; reads all 73 and answers 200; waits for 13 more bytes | Reads 60 bytes and answers 400 because the JSON is cut off | The server trusts the header, so it stops at 60 and the JSON is incomplete. |
| 5 | Content-Length says 90 but the body is 73 bytes. What happens? | The server answers 200; the server answers 400; the server waits for 17 more bytes, and the Pico's timeout ends it | The server waits for 17 more bytes, and the Pico's timeout ends it | The server is still reading and the Pico is waiting for the reply, so neither moves. |
| 6 | Which line tells the server the body is JSON? | L2, L3, L5 | L3 | Content-Type names the format of the body. |
| 7 | The reply starts with HTTP/1.0 400 Bad Request. Whose mistake is it? | The client's request was wrong; the server is broken; the Wi-Fi dropped | The client's request was wrong | A first digit of 4 means the client made the mistake; 5 means the server did. |
| 8 | The reply has Content-Length: 103. How many body bytes should the Pico read? | 73, 103, as many as arrive until a timeout | 103 | The reply's Content-Length counts the reply's body, and the Pico stops there. |

**Provenance:** The request is the one printed by `src/chapters/13-wifi-http-agent-link/04-raw-http-post.py` with the default `buddy_config.py`. The reply length 103 is the length of the Chapter 1 reply as JSON. The server behaviors in questions 4 and 5 are those of `server/buddy_server.py`.

**Rules:** Question order is fixed and the choices of each question are shown in the order in the table. Each question has one attempt. The score is the number of correct answers.

**Learner Activity:**

1. The learner hovers over each of the lines L1 to L7 to read what it is called.
2. The learner starts the 8 questions. Question 1 is shown.
3. The learner picks an answer and submits.
4. The sim shows the correct answer and the Why text, and highlights the lines involved in the request.
5. After question 8, the sim shows the score. The learner should notice that questions 4 and 5 differ only in whether the header number is smaller or larger than the real body.

**Feedback:** 8 questions, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The answer is <answer>: <Why>". The answer is revealed right after each submission, and a running score "n of 8" is shown.

**Starting State:** The request is shown with numbered lines and nothing selected, with the question "Which line says what the client wants done, and where?"

**Chapter Anchors:** The chapter states that the request is 194 bytes in all, 121 of head and 73 of body; that the reply is 103 bytes of body; that a Content-Length smaller than the body gives a 400 and a larger one makes the server wait; and that a first status digit of 4 means the client's mistake.
</details>

## The Buddy Server's Endpoint

A **REST endpoint** is a path on a server that does one named job when it receives a request, such as `POST /v1/ask`. The `/v1/` is a version number: if the contract ever changes, `/v2/ask` can exist beside it and old devices keep working. The buddy server has two endpoints in this chapter.

| Method and path | Job | Success |
|-----------------|-----|---------|
| `POST /v1/ask` | Run the brain on a question | 200 and the three-field reply |
| `GET /v1/health` | Say that the server is up | 200 and `{"ok": true, ...}` |

The server is `server/buddy_server.py`, about 190 lines of Python's standard library, so there is nothing to install. It runs on your computer, not on the Pico.

```bash
cd src/chapters/13-wifi-http-agent-link/server
python3 buddy_server.py
```

It prints the address that other devices on the network should use, and that address goes into `BUDDY_HOST` in `buddy_config.py`. The brain is Chapter 1's `decide()` function. The server asks it for an answer, and puts the answer into the three-field reply. That one function is the only place where "the brain" lives, so Chapter 16 can replace it with a school calendar and Chapter 14 can feed it transcribed speech without the Pico noticing.

```python
def make_reply(text, events):
    speak, show = decide(text, events)
    return {"speak": speak, "show": show[:30], "next_mode": "clock"}
```

Before it calls the brain the server checks the request against the contract, and answers with a status code and a JSON body `{"error": "..."}` when something is wrong. `python3 server/test_server.py` runs 13 checks with no Pico, including a body that is not JSON (400), a missing field (400), an oversize body (413), and a `GET` where a `POST` belongs (405).

## Reading the Reply Safely

A request is not finished when the bytes leave the Pico. Two rules apply to the reply, and both protect the Pico's small memory (Chapter 2).

**Read a bounded amount.** The reply says how big its body is in `Content-Length`. The code compares that number with `MAX_REPLY_BYTES` (2,048) before reading anything, and never reads more. The whole exchange here is 194 bytes out and a little over 100 bytes of body back, tiny next to the Pico's heap. The danger is not these messages. It is the day a wrong server sends a megabyte.

**Always close the socket.** An open connection holds memory and one of the network stack's small, fixed number of sockets. If a program forgets to close one on every path, including the paths where an error was raised, it works for a while and then fails with an error that looks unrelated. That is why `socket.close()` is in a `finally` block, the same rule as `mic.deinit()` in Chapter 2.

## The requests Library

Writing `build_post` and `read_response` once teaches you what HTTP is, but you should not hand-write it in every program. The **requests library** wraps the same steps, and its call looks like this.

```python
import requests

response = requests.post(
    "http://192.168.1.50:8080/v1/ask",
    json={"device": "desk-07", "kind": "question", "text": "when is my next test"},
    timeout=8)
try:
    reply = response.json()
    print(response.status_code, reply["show"])
finally:
    response.close()
```

`json=` turns the dictionary into JSON, sets `Content-Type`, and works out `Content-Length`. `timeout=` sets the socket time limit. `response.json()` reads the whole body and parses it. `response.close()` closes the socket, and is the line people forget.

Whether the library is on your Pico depends on the firmware. The Raspberry Pi Pico 2 W builds of MicroPython do not include it as a built-in module, as far as the port's file list shows. Install it once, while connected to Wi-Fi.

```python
import mip
mip.install("requests")
```

`mip` downloads the package from the `micropython-lib` collection into the `lib` folder on the Pico, and `06-requests-post.py` runs this for you if the import fails. At the time of writing, `micropython-lib` lists the package as `requests` version 1.1.1. Older firmware called it `urequests`, which has no `timeout` argument, so `06-requests-post.py` says so if it hits that. Which version `mip` gave your Pico is a fact to write down.

There is one more thing to know about this library, and it matters in Chapter 14. When a web address begins with `https://`, the library as we read it turns off certificate checking. For `http://` on a classroom network that does not matter. For `https://` it means the connection is encrypted but would also connect to an impostor, and Chapter 14 shows how to do better.

| | By hand (`05-socket-post.py`) | `requests` (`06-requests-post.py`) |
|---|---|---|
| Lines of your code | About 12 | About 5 |
| You see the raw text | Yes | No |
| Content-Length | You count it | Done for you |
| Timeout | `sock.settimeout()` | `timeout=` (newer versions) |
| Needs installing | No | Yes, with `mip` |
| Closes for you | No: use `finally` | No: call `response.close()` |

## Showing the Link on the Display

A device that fails silently feels broken. The status region from Chapter 6 (the top bar, 15 characters wide) is the right place to say what the link is doing, and the agent message region (30 characters) shows the answer. `07-ask-buddy-display.py` ties it together: the status bar walks through "joining", "online", "asking...", and "ok" with the elapsed milliseconds, and an error word if anything goes wrong.

```python
def put(region, text, color):
    x, y, width = region
    display.text(SMALL, text[:width].ljust(width), x, y, color, config.BLACK)
```

The function cuts the text to the region's width and pads it with spaces to exactly that width, so the new text covers the old without redrawing the screen. A full-screen fill takes at least 86 ms (Chapter 5), while a 15-character status redraw is \( 15 \times 8 \times 16 \times 2 = 3{,}840 \) bytes. Each press of MODE sends the next question and shows the server's `show` field. Because the code catches `OSError`, `ValueError` and `KeyError`, stopping the server makes the status say "error" and the device carries on.

## Finding the Server by Name: mDNS

Typing `192.168.1.50` into a file is awkward if it changes. **mDNS discovery** (multicast DNS) lets a device find another by a name ending in `.local` instead, such as `buddy.local`. The device asks the whole local network "who is buddy.local?" and the owner answers with its address. No DNS server is needed. A Raspberry Pi running school software is usually reachable this way, and most laptops answer to their own `.local` names.

Two different things hide behind "mDNS support", and the Pico's support for them differs.

| Job | Meaning | Status for the Pico 2 W |
|-----|---------|-------------------------|
| Announcing | The Pico answers to `study-buddy-07.local` | MicroPython's `network.hostname()` is documented as sent to DHCP and, if the port supports it, to mDNS. Reports from the project's issue tracker suggest the RP2 port gained this in 2025, and that it does not work in every mode. **Unconfirmed on the kit.** |
| Resolving | The Pico looks up `buddy.local` and gets a number | We found no documentation that `socket.getaddrinfo()` on the Pico sends mDNS queries; it uses the DNS server from `ifconfig()`. **Unconfirmed, and probably not available.** |

Because it is uncertain, the book's default does not depend on it. `08-mdns-check.py` tries to resolve each name in a list and prints the answer or the failure, with `sys.version`, and then states the fallback: the fixed address in `buddy_config.py`, protected by a DHCP reservation. If `buddy.local` does work on your firmware, you can set `BUDDY_HOST = "buddy.local"`, but keep the IP address in a comment beside it.

## Why Plain HTTP Is Acceptable Here, and Only Here

Everything in this chapter uses `http://`, and every byte of it travels unencrypted. **Plain HTTP LAN use** means using unencrypted HTTP only on a network the school controls. Anyone who can capture traffic on that network can read the questions in the 194-byte request. On a classroom network that is a small group of people the school manages, the questions are not secrets, and there are no passwords in the exchange, so the risk is low and the simplicity is worth it. The device also never sends anything the student did not just say.

Plain HTTP is *not* acceptable when the data crosses the internet, or any network the school does not control, such as a public hotspot or a student's home network where a stranger's laptop could be connected. It is also not acceptable the moment the exchange carries a password or a login token, because someone watching the network would learn it and could use it. Chapter 14 adds a token and HTTPS, Chapter 17 asks which data should leave the room at all, and the buddy server's startup message reminds you every time: "plain HTTP, no login: trusted classroom network only."

!!! mascot-warning "Do Not Port-Forward This"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    It is tempting to make the server reachable from home by opening a port on the router. Do not do this with the Chapter 13 server: it has no login and no encryption, so anyone on the internet could ask it questions. Keep it on the classroom network, and use Chapter 14 before anything else.

## Putting It All Together

You can now describe a request from end to end. The Pico joins Wi-Fi in station mode with a time limit, and gets an IP address, a netmask, a gateway and a DNS server from DHCP. It checks that the server's address is on its own local network. It writes the question as JSON, wraps it in an HTTP POST with the right `Content-Length`, and sends it to `/v1/ask`. The server's brain returns a three-field JSON reply, the Pico reads a bounded amount of it, closes the connection in a `finally` block, and draws the answer in the message region.

Key takeaways:

- Station mode joins someone else's network; `connect()` returns at once, so poll `status()` with a time limit and treat -3 and -2 differently.
- An IP address is four bytes given by DHCP; the netmask picks out the network part, and two devices are on the same network when their network addresses match.
- The local network uses RFC 1918 private ranges; keep the server's address stable with a DHCP reservation.
- JSON is the shared shape: three fields in, three fields out, and count the bytes.
- An HTTP request is plain text: request line, headers, a blank line, then the body; the status code's first digit says whose mistake it was.
- A POST must say the right `Content-Length`; too small gives a 400 and too large makes the server wait.
- A REST endpoint is a path that does one job; `POST /v1/ask` carries the Chapter 1 contract.
- Read a bounded reply and close the socket in `finally`; `requests` helps, but you still call `close()`.
- `.local` names are uncertain on the Pico, so keep a fixed address as the fallback.
- Plain HTTP is for a trusted classroom network only, never the internet and never with a password.

Test yourself with these two questions, and click each one to reveal its answer.

??? question "The Pico's address is 10.4.7.88 with netmask 255.255.255.0 and the server is at 10.4.200.9. Why does the request fail, and what is the fix? Click to expand"
    The mask keeps the first three numbers, so the Pico is on `10.4.7.0` and the server is on `10.4.200.0`: different networks, and the request must go through the gateway, which may not forward it. Check that `BUDDY_HOST` is right and that both devices are on the same network, or ask the network administrator to allow the traffic.

??? question "Your program prints the status code 200 but then fails with a memory error after about a dozen requests. What did you forget? Click to expand"
    Most likely the program never closed the response or the socket, so each request left a connection open. Put `response.close()` (or `sock.close()`) in a `finally` block so it runs on every path, and read at most `MAX_REPLY_BYTES` of the body.

!!! mascot-celebration "Your Pico Is on the Network"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You just joined a Wi-Fi network in station mode, read an IP address and netmask, wrote the Chapter 1 contract as JSON, and sent it as an HTTP POST to a REST endpoint. Your Pico can now ask the buddy server a question and show the answer.

In Chapter 14 we make the link carry real speech, lock it with a token, and survive a network that drops.
