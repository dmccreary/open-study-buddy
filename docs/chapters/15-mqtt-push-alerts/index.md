---
title: "MQTT and Push Alerts"
description: "How a school pushes alerts to every desk device with MQTT: publish-subscribe versus request-response, a Mosquitto broker on a Raspberry Pi, topic design, QoS, retained messages, last will, keep-alive, non-blocking umqtt polling inside the audio loop, the alert format, and Home Assistant."
generated_by: claude skill chapter-content-generator
date: "2026-10-18 13:26:12"
version: 1.11
---

# MQTT and Push Alerts

## Summary

This chapter adds push alerts with MQTT. Students learn publish-subscribe messaging, run a Mosquitto broker on a school Raspberry Pi, and design topics, QoS levels, and retained messages. They use umqtt with non-blocking polling so alerts arrive without interrupting audio, and connect the device to open home-automation tools.

## Concepts Covered

This chapter covers the following 22 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| MQTT Protocol | 46 |
| umqtt Library | 2 |
| Request-Response Pattern | 33 |
| Publish-Subscribe Pattern | 32 |
| check_msg Polling | 1 |
| MQTT Broker | 11 |
| Publisher | 10 |
| Subscriber | 10 |
| Mosquitto | 2 |
| Topic | 8 |
| QoS Levels | 2 |
| Last Will | 1 |
| Keep-Alive | 1 |
| MQTT Authentication | 2 |
| Home Assistant | 2 |
| Topic Naming Scheme | 2 |
| Topic Wildcards | 1 |
| Retained Message | 1 |
| Broker on Raspberry Pi | 1 |
| Alert Message Format | 3 |
| Home Automation | 1 |
| Device Status Topic | 1 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 1: Personal Agents and the Open Study Buddy Architecture](../01-personal-agents-architecture/index.md)
- [Chapter 2: MicroPython Review for Embedded Systems](../02-micropython-review/index.md)
- [Chapter 7: Buttons, State Machines, and Device Modes](../07-buttons-and-device-modes/index.md)
- [Chapter 13: Wi-Fi, HTTP, and Connecting to the Agent](../13-wifi-http-agent-link/index.md)
- [Chapter 14: Streaming Speech, Security, and Network Resilience](../14-streaming-security-resilience/index.md)

---

## A Test Tomorrow, Delivered Now

Until now the Study Buddy has only spoken when spoken to: you ask, the server answers. A school needs the opposite too. When the algebra test moves to Tuesday, every desk device in the building should know within seconds, whether or not anyone asked. This chapter builds that push path with MQTT, a messaging protocol small enough for a Pico, and ends with a device that shows and beeps for an alert inside the 40 ms audio loop, with a test that tells you whether it still fits.

!!! mascot-welcome "Let the News Come to You"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    By the end of this chapter your device will show an alert and beep when the school server announces a test, all while it keeps listening. You will also run a message broker on a Raspberry Pi and watch your own alerts fly by. Let's listen closely!

## Two Ways to Ask a Question

In Chapter 13 the device asked the buddy server a question and waited for the reply. That is the **request-response pattern**: one side, the client, sends a request, and the other side, the server, sends exactly one response. Nothing happens unless the client starts it. If the server learns something new, such as "the test moved," it has no way to tell the client, because it can only answer when asked.

The **publish-subscribe pattern** turns this around. Senders do not talk to receivers at all. A sender publishes a message under a label, and a receiver that has told a go-between "I want everything with this label" gets a copy whenever one appears. The sender never learns who the receivers are, and the receivers never learn who the sender is. The go-between that holds the labels and copies the messages is the *broker*, and the labels are *topics*, both defined below.

Here is the same news, "Algebra II test tomorrow at 8," delivered three ways to a classroom of 30 desks. A device can wait for news by **polling**, which means asking again and again on a timer. If it asks every \( P \) seconds, a message published at a random moment waits on average \( P/2 \) seconds and at worst \( P \) seconds, and each desk makes \( 86{,}400 / P \) requests a day even when nothing happened.

| Method | Reaches the desk | Idle traffic per desk per day | Who tracks the desks |
|--------|------------------|-------------------------------|----------------------|
| HTTP poll every 60 s | average 30 s, worst 60 s | 1,440 requests | nobody; each desk asks |
| HTTP poll every 30 s | average 15 s, worst 30 s | 2,880 requests (86,400 for 30 desks) | nobody |
| HTTP poll every 5 s | average 2.5 s, worst 5 s | 17,280 requests (518,400 for 30 desks) | nobody |
| MQTT push | one trip through the broker | 5,760 two-byte pings at one every 15 s | the broker |
| WebSocket push | one trip to the connected desk | its own keep-alive pings | your server code |

The last two rows push, so the wait does not depend on a timer. Chapter 14's **WebSocket** is a long-lived two-way connection between one device and one server. It is the right tool for streaming audio, but for alerts you would have to write the server code that remembers which desk is connected, which room it is in, and what it missed while it was offline. MQTT gives you those pieces already built: topics for rooms, a broker that does the fan-out, messages that wait for a device that is offline, and a built-in way to notice when a device vanishes. How fast the push really is on your Wi-Fi is not a number this book can give you; test 08 measures it.

Notice that the pings in the MQTT row outnumber the requests in the 30-second poll row. The difference is cost: a ping is 2 bytes each way on an open connection, while a poll is a full HTTP request with headers, usually on a new connection. Compare the wait for the news, not the packet count.

!!! mascot-thinking "Who Starts the Conversation?"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Request-response puts the asker in charge of the timing, so news is only as fresh as the last question. Publish-subscribe puts the news in charge: the broker speaks up the moment something is published.

## MQTT in One Page

The **MQTT protocol** (Message Queuing Telemetry Transport) is a publish-subscribe protocol designed for small devices on unreliable networks. It runs over an ordinary TCP connection, usually on port 1883, and its messages have a tiny fixed header: the smallest packet, a ping, is 2 bytes. The Pico's `umqtt.simple` library speaks MQTT version 3.1.1, which is what this chapter uses; the library's CONNECT packet announces protocol level 4, the number for 3.1.1.

Three roles take part in every exchange. The **MQTT broker** is the server in the middle: it accepts connections, remembers who subscribed to what, and forwards each published message to every matching subscriber. A **publisher** is any client that sends a message to the broker, and a **subscriber** is any client that has asked the broker for messages. One program can be both. Your Study Buddy is a subscriber to alerts and a publisher of its own status, and the school's buddy server is a publisher of alerts.

*Worked example.* Here is one alert as it travels. The school server publishes it, the broker forwards it, and each desk in room 214 receives it.

```text
buddy server   --PUBLISH school/crhs/class/214/alert (173-byte JSON)-->   broker
broker         --PUBLISH school/crhs/class/214/alert (same bytes)------>   desk-07
broker         --PUBLISH school/crhs/class/214/alert (same bytes)------>   desk-12
broker         (desk-31 is in room 220: its subscription does not match, so it gets nothing)
```

Counting the bytes shows why the protocol suits a Pico. With a 27-character topic and the 173-byte alert shown later in this chapter, the PUBLISH packet at QoS 0 is \( 1 + 2 + 2 + 27 + 173 = 205 \) bytes: one byte for the packet type and flags, two for the length of what follows (the length needs two bytes once it passes 127), two for the topic's length, then the topic and the message. At QoS 1 it grows to 207 bytes because a two-byte packet number is added, and the receiver answers with a 4-byte acknowledgement.

!!! mascot-tip "Test the Broker Before the Pico"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Before you debug any device code, run `server/watch.py` on your computer and publish with `server/publish_alert.py`. If the alert shows up there, the broker, the accounts, and the topic are all fine, and any remaining problem is on the Pico.

## Topics and How to Name Them

A **topic** is the label a message is published under: a text string whose levels are separated by slashes, like a folder path. Topics are case-sensitive, they need not be created in advance (the first publish creates one), and a publisher must name one exact topic. Topics that begin with `$` belong to the broker itself; Mosquitto publishes its statistics under `$SYS`.

Because a topic is just a string, a school with 40 classrooms and 1,000 devices needs a **topic naming scheme**: a rule for building names so that nobody has to look them up. A good scheme goes from general to specific, so that one subscription can pick out a whole branch. The scheme this book uses puts the school first, then says whether the message is about a classroom or a device:

| Topic | Published by | Read by |
|-------|--------------|---------|
| `school/<school>/alert` | buddy server | every device in the school |
| `school/<school>/class/<room>/alert` | buddy server | devices in that room |
| `school/<school>/device/<device>/status` | the device (and the broker, for its last will) | dashboards, the teacher |
| `school/<school>/device/<device>/telemetry` | the device | dashboards |
| `school/<school>/device/<device>/echo`, `.../echo-reply` | the device, then the server | the round-trip test |

Each choice has a reason. The school id comes first so that one broker can serve two schools and the access rules can be written per school. `alert` comes last so that a subscription to a room's alerts is a complete, exact name. Devices write only under `device/<their own id>/`, which is what lets the broker's access rules (below) stop a stolen or confused device from speaking for another. Every level is lowercase letters, digits, and hyphens: `topics.slug("Lab 130")` gives `lab-130`, because a space in a topic is legal but invites bugs. Keep names short too, because every topic costs RAM on the Pico and bytes in every packet.

A subscriber is not limited to exact names. **Topic wildcards** let a **subscription filter** match many topics. A filter may contain two wildcards, and only in subscriptions, never in a publish.

| Wildcard | Matches | Example filter | Selects |
|----------|---------|----------------|---------|
| `+` | exactly one level | `school/crhs/class/+/alert` | the alert topic of every classroom |
| `#` | its parent and everything below; last level only | `school/crhs/#` | everything about Cedar Ridge |

Two edge cases surprise people. `school/crhs/#` also matches `school/crhs` itself, because `#` includes its parent. And a filter that starts with a wildcard does not match topics beginning with `$`, so `#` does not flood you with the broker's `$SYS` statistics.

*Worked example.* A Study Buddy in room 214 subscribes to two exact topics, `school/crhs/alert` and `school/crhs/class/214/alert`, which `umqtt` does with two `subscribe()` calls because it takes one filter at a time. A teacher's dashboard subscribes to one filter, `school/crhs/device/+/status`, and sees every device. The table below was written by hand from the rules and is the answer key that `01-topic-matcher.py` checks `topics.topic_matches()` against. An `x` means the filter selects the topic.

| Topic | S1 | S2 | S3 | S4 | S5 | S6 | S7 |
|-------|----|----|----|----|----|----|----|
| `school/crhs/alert` | x | | | | x | x | x |
| `school/crhs/class/214/alert` | | x | x | | x | | x |
| `school/crhs/class/lab-130/alert` | | | x | | x | | x |
| `school/crhs/device/desk-07/status` | | | | x | x | | x |
| `school/crhs/device/desk-07/telemetry` | | | | | x | | x |
| `school/trhs/alert` | | | | | | x | x |
| `school/crhs` | | | | | x | | x |
| `$SYS/broker/uptime` | | | | | | | |

The filters are S1 `school/crhs/alert`, S2 `school/crhs/class/214/alert`, S3 `school/crhs/class/+/alert`, S4 `school/crhs/device/+/status`, S5 `school/crhs/#`, S6 `school/+/alert`, and S7 `#`. The matcher is one short function of plain Python in `topics.py`. It passes the examples in the MQTT specification, and on a computer with paho-mqtt installed, `server/test_topics.py` also compares it with paho's own matcher on 4,095 filter and topic pairs (every valid filter of up to three levels built from `a`, `b`, `$x`, `+`, and `#`, against every topic of up to three levels built from `a`, `b`, and `$x`). They agreed on all of them.

Now try the rules yourself, and then check them against the table.

#### Diagram: MQTT Topic Router


<iframe src="../../sims/mqtt-topic-router/main.html" width="100%" height="562px" scrolling="no"></iframe>
[Run MQTT Topic Router Fullscreen](../../sims/mqtt-topic-router/main.html)

<details markdown="1">
<summary>MQTT Topic Router</summary>
Type: microsim
**sim-id:** mqtt-topic-router<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** apply<br/>
**Learning Objective:** The learner will apply the "+" and "#" wildcard rules to decide which of 7 subscription filters select each of 8 topics, with at least 7 of the 8 selections exactly right.

**Prerequisites:** topic, topic level, subscription filter, "+" wildcard, "#" wildcard, topics beginning with "$" (all defined in the section "Topics and How to Name Them" above this block).

**Evidence of Mastery:** For each of the 8 topics, in the fixed order of the Content table, the learner marks which of the filters S1 to S7 select it, then submits. A selection is correct when the marked set equals the Answer column exactly (a missing filter or an extra filter makes it wrong). Mastery is 7 of 8 correct on the first submission of each topic. Typing topics of the learner's own into the exploration box is exploration, not evidence.

**Misconceptions:** (1) "+" matches any number of levels. (2) "school/crhs/#" does not select "school/crhs". (3) "#" selects every topic, including those starting with "$".

**Instructional Rationale:** Applying a rule needs practice on cases that the rule treats differently. Each topic is built to separate two filters that look alike, and the learner commits a set of marks before the answer is shown, so a wrong rule shows up as a wrong set.

**Content:**

The 7 subscription filters, always shown:

| Id | Filter |
|----|--------|
| S1 | school/crhs/alert |
| S2 | school/crhs/class/214/alert |
| S3 | school/crhs/class/+/alert |
| S4 | school/crhs/device/+/status |
| S5 | school/crhs/# |
| S6 | school/+/alert |
| S7 | # |

The 8 topics, in order, with the filters that select each and the reason shown as feedback:

| # | Topic | Answer (filters that select it) | Why (shown as feedback) |
|---|-------|--------------------------------|-------------------------|
| 1 | school/crhs/alert | S1, S5, S6, S7 | S1 is the exact name. S5 and S7 take everything below their prefix. S6's "+" is the one level "crhs". S3 needs a "class" level that is not there. |
| 2 | school/crhs/class/214/alert | S2, S3, S5, S7 | S2 is exact and S3's "+" is the one level "214". S6 fails because "+" can match only one level, and three levels sit between "school" and "alert". |
| 3 | school/crhs/class/lab-130/alert | S3, S5, S7 | S3's "+" matches "lab-130". S2 names room 214 only. |
| 4 | school/crhs/device/desk-07/status | S4, S5, S7 | S4's "+" matches "desk-07". S3 fails on "device" versus "class". |
| 5 | school/crhs/device/desk-07/telemetry | S5, S7 | S4 needs the last level to be "status". Only the "#" filters take it. |
| 6 | school/trhs/alert | S6, S7 | S6's "+" matches "trhs". S1 and S5 name "crhs". |
| 7 | school/crhs | S5, S7 | "#" matches its parent level too, so "school/crhs/#" selects "school/crhs". |
| 8 | $SYS/broker/uptime | none | A filter that starts with a wildcard does not select a topic that starts with "$". |

**Provenance:** The scheme and the 7 filters come from the chapter section "Topics and How to Name Them" and from `src/chapters/15-mqtt-push-alerts/01-topic-matcher.py`, whose answers were written by hand and agree with the MQTT 3.1.1 specification's rules and with the paho-mqtt matcher.

**Rules:** Split a filter and a topic at "/" into levels. A filter level equal to "+" matches exactly one topic level, of any text, including empty text. A filter level equal to "#" is valid only as the last level and matches the topic's remaining levels, including none. Any other filter level must equal the topic level exactly, with case mattering. Without "#", the filter and the topic must have the same number of levels. A topic whose first level starts with "$" is not selected by a filter whose first level is "+" or "#".

**Learner Activity:**

1. The learner reads the 7 filters, then types one topic of their own into the exploration box. The sim lists which filters select it and highlights the levels that matched, so the learner can try "school/crhs" or "$SYS/x" freely.
2. The learner starts the 8 topics. Topic 1 is shown with the 7 filters unmarked.
3. The learner marks the filters that they think select the topic and submits.
4. The sim shows the correct set, the levels each filter matched, and the Why text. The learner moves to the next topic.
5. After topic 8, the sim shows the score. The learner should notice that topics 5 and 7 are the two that most often cost a point.

**Feedback:** 8 topics, fixed order, one submission each. Correct: "Correct: <Why>". Incorrect: "Not quite. The filters that select it are <answer>: <Why>", naming each filter that was wrongly marked or missed. The answer is revealed right after each submission, and a running score "n of 8" is shown.

**Starting State:** The 7 filters are shown with the exploration box empty and the question "Which subscribers would receive a message on this topic?"

**Chapter Anchors:** The chapter's table of 8 topics against filters S1 to S7 has the same answers. The chapter states that "school/crhs/#" selects "school/crhs", that "#" does not select "$SYS/broker/uptime", and that "+" matches exactly one level.
</details>

!!! mascot-warning "Two Devices, One Client ID"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    Every MQTT client needs an id that is unique on the broker, and the broker disconnects an older client when a new one connects with the same id. If you copy `secrets.py` between devices, two Picos will kick each other off in a loop. Give each device its own `device_id`, and use it as its user name too.

## Mosquitto on a School Raspberry Pi

**Mosquitto** is the open-source MQTT broker from the Eclipse project, small enough to run on a Raspberry Pi and widely used in home automation. A **broker on a Raspberry Pi** gives a school one machine that sits on the classroom network, keeps the messages inside the building, and can also host the buddy server of Chapters 13 and 16. Install and start it on Raspberry Pi OS with:

```bash
sudo apt install mosquitto mosquitto-clients
sudo systemctl enable --now mosquitto
```

With no configuration at all, current Mosquitto (version 2 or later) accepts connections from the Pi itself only. To let the desks connect, you must say which network address to listen on, and from that moment the connection needs **MQTT authentication**: a user name and password that the broker checks against a password file, plus an access-control list (ACL) that says which topics each account may read or write. The book's `server/mosquitto.conf` is a complete example, shown here.

```text
listener 1883 192.168.1.50
allow_anonymous false
password_file /etc/mosquitto/study-buddy.passwd
acl_file /etc/mosquitto/study-buddy.acl
message_size_limit 1024
```

The first line makes the broker listen on port 1883 on the Pi's LAN address only, not on every interface, so a second network card or a VPN cannot expose it by accident. Give the Pi a fixed address (a DHCP reservation on the router), because Mosquitto cannot listen on an address the Pi does not have. The next two lines turn off anonymous access and name the password file. `message_size_limit` protects the Pico: `umqtt` reads a whole message into RAM before your code sees it, so a giant message from a mistaken or hostile client could crash the device, and the broker can refuse to forward anything over 1,024 bytes. Create the accounts, one for the server, one for a dashboard, and one per device whose user name is the device id:

```bash
sudo mosquitto_passwd -c /etc/mosquitto/study-buddy.passwd buddy-server
sudo mosquitto_passwd /etc/mosquitto/study-buddy.passwd dashboard
sudo mosquitto_passwd /etc/mosquitto/study-buddy.passwd desk-07
sudo systemctl restart mosquitto
```

Each command asks for that account's password. Use `-c` only for the first account, since it creates the file and overwrites any existing one. A lost device is retired with `mosquitto_passwd -D <file> <user>`, which is why each device has its own account instead of sharing one password. The ACL file, `server/study-buddy.acl`, lets the server publish anywhere under the school's branch, lets a dashboard read it, and gives every device read access to the alert topics and write access to only its own `device/<name>/` topics. It does this with the line `pattern write school/crhs/device/%u/status`, where `%u` is replaced by the account name of whoever is connected. These settings follow Mosquitto's documentation; they have not been run on a Pi for this book, so test them (with `watch.py` and `publish_alert.py`, as below) before relying on them.

Test it from your computer before touching a Pico (the Pico tests are in the README):

```bash
python3 server/watch.py                        # terminal 1: prints everything under school/crhs
python3 server/publish_alert.py --room 214 --type test --title "Algebra II test" \
    --when "Tomorrow 8:00 AM" --text "Algebra II test tomorrow at 8 AM."   # terminal 2
```

`watch.py` is the tiny subscriber and `publish_alert.py` the server-side publisher; both use the Python library paho-mqtt and read the broker address and account from environment variables so that no password lands in a file. `publish_alert.py --dry-run` shows what would be sent without connecting. Here is a real dry run from this book's test machine (no broker involved):

```text
$ python3 server/publish_alert.py --room "Lab 130" --type test --title "Algebra II test" \
      --when "Tomorrow 8:00 AM" --text "Algebra II test tomorrow at 8 AM." --dry-run
topic  : school/crhs/class/lab-130/alert
payload: {"id":"20261018-125323","type":"test","title":"Algebra II test","when":"Tomorrow 8:00 AM","text":"Algebra II test tomorrow at 8 AM."} (133 bytes)
dry run: nothing was sent
```

Mosquitto's own command-line tools do the same job once you are on the Pi: `mosquitto_sub -h 192.168.1.50 -u dashboard -P ... -t 'school/crhs/#' -v` and `mosquitto_pub -t school/crhs/alert -m '...' -q 1`.

Passwords alone are not a complete defense, because plain MQTT on port 1883 sends the user name and password unencrypted, as plain HTTP does in Chapter 13. On a school LAN that you control, that is a defensible trade-off: it is the same trust you gave plain HTTP. It stops being defensible the moment the broker is reachable from outside. A broker open to the internet invites anyone to publish a fake "No school Friday" alert to every desk, to read which devices are online and when, and to fill the Pi's memory with retained messages. The fixes are layered: keep the listener on the LAN address, keep the router from forwarding the port, keep anonymous access off, restrict accounts with the ACL, cap the message size, and if remote access is ever needed, use a VPN into the school network rather than opening port 1883. Encrypted MQTT (TLS, usually on port 8883) is possible with the `ssl` option of `umqtt` and Chapter 14's certificate handling, but this chapter's code and the broker settings above do not use it and it is untested here. Chapter 17 puts the broker exposure risk into the school's threat model and weighs these defenses.

!!! mascot-warning "A Firewall Is a Second Lock"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    The `listener` line is one lock, and a firewall on the Pi is a second. If you use `ufw`, allow only your school's subnet, for example `sudo ufw allow from 192.168.1.0/24 to any port 1883 proto tcp`, then check from a phone on cellular data that the port does not answer.

## Delivery Promises: QoS, Retained Messages, and Last Will

A network can drop a packet, and a device can be switched off when a message goes by. MQTT gives you four tools for dealing with that, and each one is a promise you choose per message or per connection.

### QoS Levels

The **QoS level** (quality of service) is the delivery promise for one message.

| QoS | Promise | Packets | A lost packet means |
|-----|---------|---------|---------------------|
| 0 | At most once | PUBLISH | the message is gone |
| 1 | At least once | PUBLISH, PUBACK | the sender repeats it, so the receiver may see it twice |
| 2 | Exactly once | PUBLISH, PUBREC, PUBREL, PUBCOMP | the four-step handshake prevents a repeat, at the cost of a second round trip |

QoS applies on each hop separately. The publisher and the broker agree on one QoS, and the broker and the subscriber agree on another, and a message is delivered to a subscriber at the *lower* of the QoS it was published with and the QoS that the subscriber asked for in `subscribe()`. A QoS 1 alert reaches a desk at QoS 1 only if the desk subscribed at QoS 1; the book's code does.

The `umqtt.simple` library supports QoS 0 and 1 for both publishing and subscribing, and not QoS 2, which keeps its code small. Its `publish(..., qos=1)` waits until the broker's acknowledgement arrives; it does not resend if the connection breaks, so a failed publish raises `OSError` and the program must decide what to do. The library `umqtt.robust` resends, but as the next section shows it does so by blocking.

Here is how the book assigns levels, with the reason for each. The choice follows one rule: pay for a stronger promise only where losing or repeating the message matters.

| Message | QoS | Retain | Why |
|---------|-----|--------|-----|
| Alert (server to desk) | 1 | no by default | Losing a test notice is worse than seeing it twice, and a repeat is harmless because the `id` lets the device ignore it. QoS 2 would cost extra round trips for a guarantee the `id` already provides. |
| Online and offline status | 1 | yes | One message per connection; the last one must be right. |
| Telemetry (volume, uptime) | 0 | no | The next report replaces it in 30 seconds. |
| Echo test | 0 | no | We want to time the bare trip. |

!!! mascot-encourage "Delivery Guarantees Feel Slippery"
    ![Sage encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    "At least once" and "at most once" are easy to mix up, and most people need to see the packets move to keep them straight. Step through the handshake below, predicting the answer each time, and the pattern will stick.

#### Diagram: QoS Handshake Stepper


<iframe src="../../sims/mqtt-qos-handshake-stepper/main.html" width="100%" height="552px" scrolling="no"></iframe>
[Run QoS Handshake Stepper Fullscreen](../../sims/mqtt-qos-handshake-stepper/main.html)

<details markdown="1">
<summary>QoS Handshake Stepper</summary>
Type: microsim
**sim-id:** mqtt-qos-handshake-stepper<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Understand<br/>
**Bloom Verb:** infer<br/>
**Learning Objective:** The learner will infer, for 6 scenarios of a publisher sending one alert to a broker, how many copies of the alert the broker processes, with at least 5 of the 6 inferences right.

**Prerequisites:** publisher, broker, QoS 0, QoS 1, QoS 2, PUBLISH, PUBACK, PUBREC, PUBREL, PUBCOMP, duplicate (all defined in the section "Delivery Promises" above this block).

**Evidence of Mastery:** For each scenario the learner chooses 0, 1, or 2 as the number of copies the broker processes, before the packets are stepped through. A choice is correct when it equals the Answer column. Mastery is 5 of 6 correct on the first choice for each scenario. Stepping through the packets after the answer, and the exploration mode, are not evidence.

**Misconceptions:** (1) QoS 0 retries until the message gets through. (2) QoS 1 guarantees exactly one copy. (3) A lost acknowledgement means the message was lost. (4) QoS 2 never sends a packet twice.

**Instructional Rationale:** Inference at the Understand level requires the learner to reason from the packet sequence to the outcome rather than recall a definition. Committing to a count first, and then stepping through the packets, shows where the extra or missing copy comes from.

**Content:**

The sim shows one hop only, from the publisher to the broker, drawn as two lanes with packets moving between them. The packet sequences when nothing is lost:

| QoS | Packets in order | Who sends each |
|-----|------------------|----------------|
| 0 | PUBLISH | publisher |
| 1 | PUBLISH, PUBACK | publisher, broker |
| 2 | PUBLISH, PUBREC, PUBREL, PUBCOMP | publisher, broker, publisher, broker |

The 6 scenarios, in order. "Lost" means that packet never arrives and the sender never learns why.

| # | Scenario | Answer (copies processed) | Why (shown as feedback) |
|---|----------|---------------------------|-------------------------|
| 1 | QoS 0. Nothing is lost. | 1 | The one PUBLISH arrives and is processed once. |
| 2 | QoS 0. The PUBLISH is lost. | 0 | QoS 0 has no acknowledgement and no repeat, so the alert is gone. |
| 3 | QoS 1. Nothing is lost. | 1 | The PUBLISH arrives, is processed once, and the PUBACK ends the exchange. |
| 4 | QoS 1. The PUBLISH is lost. | 1 | No PUBACK comes back, so the publisher sends the PUBLISH again with the duplicate flag set. That second one arrives and is processed once. |
| 5 | QoS 1. The PUBLISH arrives but the PUBACK is lost. | 2 | The broker already processed the alert, but the publisher sees no PUBACK and sends it again, so the broker processes it a second time. This is why alerts carry an id. |
| 6 | QoS 2. The PUBREC is lost. | 1 | The publisher repeats the PUBLISH, the broker recognizes the packet number and does not process it again, and the handshake continues to PUBCOMP. |

**Provenance:** The packet sequences and the behavior of each QoS level come from the MQTT 3.1.1 specification and the chapter section "QoS Levels". The scenarios are illustrative, and the sim labels them "illustrative". The sim is a model of one hop and does not reproduce timing.

**Rules:** The publisher resends an unacknowledged PUBLISH (QoS 1) or PUBLISH and PUBREL (QoS 2) after a loss, with the duplicate flag set, until the acknowledgement arrives. The broker processes every QoS 1 PUBLISH it receives, including repeats. For QoS 2 the broker processes a packet number once, however many times the PUBLISH arrives. QoS 0 is never resent. In a scenario, exactly one packet is lost, once; the resend then arrives.

**Learner Activity:**

1. The learner opens the exploration mode, chooses QoS 0, 1, or 2, and steps through the packets of the no-loss case one at a time. The sim names each packet and who sent it.
2. The learner starts the 6 scenarios. Scenario 1 is shown with the packet lanes empty.
3. The learner chooses 0, 1, or 2 as the number of copies processed and submits.
4. The sim steps through the scenario's packets, marks the lost one, and shows the Why text.
5. After scenario 6, the sim shows the score. The learner should notice that only one scenario gives more than one copy and that it is the one where the acknowledgement, not the message, was lost.

**Feedback:** 6 scenarios, fixed order, one choice each. Correct: "Correct: <Why>". Incorrect: "Not quite. The broker processes <answer> copy or copies: <Why>". The answer is revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** The exploration mode is shown with QoS 1 selected and no packets sent, with the question "What will the broker do if an acknowledgement goes missing?"

**Chapter Anchors:** The chapter states that QoS 0 is at most once, QoS 1 is at least once and may deliver a repeat, QoS 2 is exactly once with a four-packet handshake, that `umqtt.simple` supports QoS 0 and 1 only, and that alerts carry an id so repeats can be ignored.
</details>

### Retained Messages

A **retained message** is a message that the broker keeps, one per topic, and delivers to every new subscriber of that topic immediately on subscribing. You set the retain flag when you publish. Without it, a device that was switched off when an alert went by never hears it. With it, the device hears the latest message the moment it connects.

Retention is a good fit for state ("this device is online") and a risky fit for events ("the test is tomorrow"), because a retained event stays after the event is over. A device that boots on Thursday would receive a retained "test tomorrow" from Monday. There are two safe ways to handle that: publish the retained alert with an expiry you check on the server and *clear* it afterward, or don't retain alerts at all. To clear a retained message, publish a zero-length retained message to the same topic; the broker deletes the stored one. `publish_alert.py` does this with `--clear`, and `--retain` is an explicit choice, not a default. A device must also ignore the zero-length message when it is delivered, and `decode_alert()` does.

*Worked example.* The principal wants "Early dismissal Friday" visible on every desk, including those that reboot during the week. The server publishes it to `school/crhs/alert` with `--retain`. Every desk that connects or reconnects receives it immediately, which is why the device must remember the ids it has seen: without that, each reconnect would beep again. On Friday evening the server runs `publish_alert.py --all --clear` and the topic goes quiet.

!!! mascot-thinking "Retained State, Fresh Events"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Ask whether the message describes how things are or something that happened. State is worth retaining, because the newest value is the right one for a late arrival. An event usually isn't, because a late arrival would treat old news as new.

### Last Will and Keep-Alive

A device that is unplugged cannot announce that it is gone. The **last will** solves this: when a client connects, it hands the broker a message and a topic, and the broker publishes that message for the client if the client disappears without saying goodbye. A clean `disconnect()` does not trigger the will, because the client said goodbye; a crash, a pulled cable, a dead Wi-Fi link, or a missed keep-alive does. In `umqtt` you set it before connecting:

```python
client.set_last_will(STATUS_TOPIC, b"offline", retain=True, qos=1)
client.connect(True)
```

How does the broker know a silent client is gone, since a dead TCP connection can look idle for a long time? That is the job of **keep-alive**. In its CONNECT packet the client promises a number of seconds, here 30, and promises to send *something* at least that often. The broker waits one and a half times the interval, 45 seconds here, and if it has heard nothing it treats the client as dead, closes the connection, and publishes the will. A client with nothing to say sends a ping, the 2-byte PINGREQ that the broker answers with a 2-byte PINGRESP.

`umqtt.simple` does not send pings by itself. Its `keepalive` argument only fills in the number the broker is told, and the default, 0, tells the broker never to time the client out. Pinging is your job, and the chapter's code pings at half the interval, every 15 seconds, so one lost ping does not look like a dead device. Any packet counts as traffic, so each publish also resets the clock.

*Worked example.* Suppose you forget `ping()` and the device is quiet. At 45 seconds the broker closes the connection and publishes `offline`, though the Pico is happily running. The dashboard shows a false outage every 45 seconds. Test 02 has `SEND_PINGS = False` for exactly this experiment. A test run of the book's code against a small test broker with a 1-second keep-alive reproduced the effect: the will fired about 1.7 seconds after the last packet (1.5 times the interval, plus polling), and a client pinging every half interval stayed connected.

The other direction needs care too. If the Wi-Fi drops silently, the Pico's `check_msg()` just finds nothing waiting, and the Pico cannot tell "no news" from "no connection". The `Link` class in `mqtt_common.py` therefore records the time anything last arrived from the broker; a healthy broker answers each ping within a moment, so if nothing has arrived for 45 seconds, the same limit the broker uses, `Link` declares the connection dead and reconnects.

### The Device Status Topic

The **device status topic** is where a device tells the world whether it is alive. It is `school/<school>/device/<device>/status`, and it holds exactly one of two words, `online` or `offline`. Three pieces of MQTT cooperate to keep it truthful. The device publishes `online` with the retain flag as soon as it connects, so a dashboard that starts later reads the current state immediately. The last will, also retained, replaces it with `offline` if the device vanishes. And a polite shutdown publishes `offline` itself, because a clean disconnect would not fire the will.

| Event | What the broker holds on the status topic |
|-------|-------------------------------------------|
| Device connects | `online` (published by the device, retained) |
| Device runs normally | `online` |
| Device calls `disconnect()` | `offline` (the device published it just before) |
| Cable pulled | `online` until about 45 s later, then `offline` (published by the broker) |
| Broker restarts | whatever it saved, if persistence is on (Mosquitto's package default is to persist, but check yours) |

Richer data goes on a separate topic, `.../telemetry`, as one small JSON object published at QoS 0 every 30 seconds, for example `{"up":86400,"vol":40,"heap":123456,"wake":null,"conn":1}`: uptime in seconds, volume, free memory, seconds since the last wake word (null until Chapter 12's detector reports one), and how many times the link has connected. Keeping the status word plain means a dashboard such as Home Assistant can use it directly as an availability topic, whose defaults are `online` and `offline`. Test 07 publishes both.

## The umqtt Library and Polling Without Blocking

The **umqtt library** is MicroPython's standard MQTT client, from the micropython-lib collection. It comes as two small modules: `umqtt.simple`, which has the calls you need, and `umqtt.robust`, which adds automatic reconnecting. Install it once from your computer, with the Pico connected by USB and a MicroPython release of 1.20 or newer, which includes the `mip` installer:

```bash
mpremote mip install umqtt.simple
```

Alternatively, run `import mip; mip.install("umqtt.simple")` at the Pico's REPL while it is on Wi-Fi. The API maps one-to-one onto MQTT operations, and the whole source is about 230 lines, short enough to read in an evening.

| Call | What it does |
|------|--------------|
| `MQTTClient(client_id, server, port, user, password, keepalive)` | Makes the client object; nothing is sent yet. |
| `set_callback(f)` | `f(topic, msg)` runs for each incoming message; both arguments are `bytes`. |
| `set_last_will(topic, msg, retain, qos)` | Must be called before `connect()`. |
| `connect(clean_session, timeout)` | Opens the TCP connection and sends CONNECT. `timeout` exists in the current library; an older copy may lack it. |
| `subscribe(topic, qos)` | One filter per call. The callback must already be set. |
| `publish(topic, msg, retain, qos)` | QoS 0 returns at once; QoS 1 waits for the acknowledgement. |
| `ping()` | Sends a PINGREQ. |
| `check_msg()` / `wait_msg()` | Process one incoming packet. |
| `disconnect()` | Sends DISCONNECT and closes the socket. |

Incoming messages do not arrive by themselves. They sit in the network connection until your code reads them, and two calls do the reading. `wait_msg()` **blocks**: it waits until a packet arrives, which is right for a program that does nothing else. `check_msg()` is the **check_msg polling** call: it looks once, and if nothing is waiting it returns immediately, so you can call it in the middle of a loop that has other work to do. When something is waiting, it reads the packet, runs your callback if it is a published message, and returns. A QoS 1 message is acknowledged automatically after the callback returns.

Three details in the library's source matter for a device that must also keep up with a microphone. First, `check_msg()` is only non-blocking for the *first byte*. Once a byte has arrived, the library switches the socket to blocking mode to read the rest of the packet, so a packet cut off halfway by a Wi-Fi failure can stall the loop. Second, `connect()` can block for as long as its `timeout` (the library sets no limit unless you pass one). Third, `umqtt.robust` handles a lost connection by looping: it calls `connect()` and then `time.sleep(2)` over and over until it succeeds, so one broker outage freezes your audio loop completely. For a device that must keep listening, the book's `Link` class replaces that loop with a state machine that never sleeps.

!!! mascot-warning "Never Draw or Beep Inside the Callback"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    The callback runs inside `check_msg()`, and for QoS 1 publishes it can run inside `publish()` and `subscribe()` too. A slow callback holds up everything, and drawing from it can start before the display is ready. Have the callback only put the alert on a short queue, and let the main loop show it.

The callback and the polling step are the heart of `mqtt_common.Link`. This excerpt shows the callback and one call to `service()`, which runs once per pass of the main loop.

```python
def _on_msg(self, topic, msg):                 # queue only: never draw or play sound here
    alert = alerts.decode_alert(msg)
    if alert is None:
        self.bad += 1                          # empty, oversized, not JSON, or invalid
    elif not self.seen.is_new(alert["id"]):
        self.dupes += 1                        # a repeat: ignore it
    elif len(self.pending) >= MAX_PENDING:
        self.overflow += 1
    else:
        self.pending.append(alert)

def service(self):
    ...                                        # if down: retry only when next_try has passed
    self.client.check_msg()                    # may call _on_msg
    if ticks_diff(now, self.last_ping) >= PING_MS:
        self.client.ping()
    if ticks_diff(now, self.last_rx) > DEAD_MS:
        raise OSError("broker silent ...")     # caught below: mark down, schedule a retry
```

`decode_alert()` returns `None` for anything the device should not trust: an empty payload, one over 512 bytes, text that is not valid JSON, or JSON missing a field. The `Seen` class holds the last 8 alert ids in a small list, and `is_new()` is `True` once per id. Three situations make repeats normal, and all three must not beep twice: QoS 1 can deliver a message twice, a retained alert is delivered again after every reconnect, and a server job may be run twice.

### The Frame Budget

Chapter 8 set the rule: a pass of the audio loop has 40 ms, and a loop that takes longer loses microphone audio once the ring buffer, measured at about 9.8 frames (0.4 s) deep, is full. Adding MQTT to that loop is safe only if five things stay true.

1. `link.service()` never sleeps and never waits for the network, except during a connect attempt (point 5).
2. The callback only parses and queues. It does not touch the display or the speaker.
3. The main loop takes at most one alert per pass, so a burst of alerts spreads across passes instead of landing in one.
4. An alert redraws only the message region, which is 15,360 bytes (Chapter 6). At the 24 MHz display clock that is at least \( 15{,}360 \times 8 / 24{,}000 = 5.1 \) ms of wire time for the background and at most the same again for 60 characters of text, so about 10 ms in the best case. It happens once per alert, not once per frame.
5. A connect attempt blocks the loop for at most `CONNECT_TIMEOUT_S` seconds. A broker that refuses a connection fails quickly, but a broker that is simply unreachable makes the attempt wait out the whole timeout.

Point 5 is the one that can break the budget, and arithmetic shows how much. A blocked loop misses \( t / 0.04 \) frames, and the ring absorbs the first 9.8, so the audio lost is \( (t / 0.04 - 9.77) \times 0.04 \) seconds. This uses the ring depth Chapter 8 measured on one board and is a model, not a measurement.

| Connect timeout \( t \) | Frames missed | Frames beyond the ring | Audio lost |
|-----------------|---------------|------------------------|------------|
| 0.3 s | 7.5 | 0 | none |
| 1 s | 25 | 15.2 | 0.61 s |
| 2 s (the book's default) | 50 | 40.2 | 1.61 s |

The default favors patience over perfection, since a reconnect attempt happens at most every 30 seconds after the first few failures, and the Chapter 7 state machine can choose to retry only in clock mode, when nothing is being recorded. If your device must listen without gaps, set `CONNECT_TIMEOUT_S = 0.3` and accept more failed attempts on a slow network. What an idle `check_msg()` costs, and how long the slowest pass takes when a message arrives, are not known until test 04 and test 06 have run on a board. The chapter expects them to be small next to 40 ms, because the idle call does one non-blocking read and returns, and this expectation is exactly what the tests are for.

## The Alert Message Format

An **alert message format** is the agreement about what is inside an alert. It must be small, because the Pico reads the whole message into RAM, and plain, because a school, a classroom app, and a dashboard all read it. The format is one JSON object of strings:

```json
{"id":"20261019-crhs-018-d1","type":"test","title":"Algebra II test","when":"Tomorrow 8:00 AM","text":"Algebra II test tomorrow at 8 AM. Room 118.","at":"2026-10-20T13:00Z"}
```

| Field | Limit | Meaning |
|-------|-------|---------|
| `id` | 40 characters | Unique per alert. The device ignores an id it has seen. |
| `type` | one of `test`, `due`, `event`, `notice`, `briefing` | Chooses the color and the sound. |
| `title` | 30 characters | Line 1 on the display. |
| `when` | 30 characters | Line 2, already formatted by the server so the Pico never does calendar math. |
| `text` | 120 characters (300 for type `briefing`) | What a speaker would say; Chapter 14's text-to-speech can turn it into audio. |
| `at` | optional, UTC | For dashboards. The Pico ignores it. |

The limits come from the screen: the message region holds two lines of 30 characters of the 8-pixel-wide font. The whole object may not exceed 512 bytes, and this sample is 173. (The longest legal alert, a briefing with every field at its limit, is 483 bytes.) The id makes duplicate-handling possible, and the book builds it from the date, the school, the calendar event, and how many days ahead the reminder is: `20261019-crhs-018-d1` is the one-day-ahead reminder for event `crhs-018` created on October 19. Chapter 16 generates those from the real calendar, and running the same job twice produces the same id, which the device then drops.

`alerts.py` builds, checks, and decodes the format, and runs on both the server and the Pico. The server calls `make_alert()`, which raises `ValueError` for a title of 31 characters, and `encode_alert()`; the device calls `decode_alert()`.

### Showing and Sounding an Alert

`alert_view.show_alert()` draws an alert into the message region: a background color chosen by the type, the title on the first line and `when` on the second, each centered. The color is a second cue; the words carry the meaning, so a color-blind student loses nothing. Test 05 shows six Cedar Ridge alerts, including one title that is too long on purpose, which `fit()` ends with `...`, and prints how long each draw took.

The beep follows Chapter 8's rules. The speaker is created only when needed, a short 880 Hz tone of 120 ms is written (3,072 bytes, which fits in the 8,192-byte speaker buffer so `write()` returns quickly), and the speaker is closed after the buffer drains. During the beep and for the quiet tail afterward, the loop keeps reading microphone frames so the ring does not fill, but throws them away: the half-duplex strategy of Chapter 8, and the reason a device that listens for "Hey Pico" does not wake itself with its own alert. The arithmetic is \( 120 + 50 + 120 = 290 \) ms, about 7 frames, during which the wake-word detector would be blind. The 120 ms tail is Chapter 8's measured value for one board.

*Worked example.* Test 06 is the whole device loop. In each pass it reads one frame (which paces the loop at 40 ms), calls `link.service()`, takes at most one alert, draws and beeps if there is one, and runs Chapter 8's loudness calculation on the frame unless the device is deaf. Once a second it prints the frames per second, the deaf frames, the worst time the pass spent working, and the number of overruns (passes over 40 ms). On the book's fake-Pico test layer with a test broker, a new alert was drawn and beeped once, a repeat of it was ignored (`dupes` went from 0 to 1), and 7 microphone frames were skipped for the beep, which matches the arithmetic. That checks the logic only. On a real board the number to watch is `worst work`, and the book does not know it yet.

### Reconnecting

When the link drops, `Link` marks itself down, waits, and tries again, and each failed attempt raises the ceiling on the wait: 2, 4, 8, 16, and then 30 seconds. The wait itself is a random number from 0 up to that ceiling ("full jitter"), so a whole classroom does not return at the same instant after a broker restart. The helper is Chapter 14's `backoff.py`, copied into this chapter's folder, with a longer cap than Chapter 14's 8 seconds because a broker outage can last minutes. The waiting never sleeps: it is a deadline that `service()` checks each pass. `Link` reconnects Wi-Fi first if the radio has dropped, resubscribes (a clean session starts empty), and announces `online` again. Tests of this logic on the fake layer covered a broker that closed every connection, one that stopped answering without closing (detected after the 45-second silence limit, with a fast-forwarded clock), and a Wi-Fi link that went away and came back.

## Home Automation and Home Assistant

**Home automation** is software that watches and controls things around a building: lights, thermostats, door sensors, and so on. Many open home-automation systems use MQTT as their common language, because a device only needs to publish its state to a topic and read commands from another. That makes a school's MQTT broker useful beyond the Study Buddy.

**Home Assistant** is the best-known open-source home-automation platform. It can connect to your broker as a subscriber and a publisher, and show the Study Buddy on a dashboard: a sensor for `online`/`offline`, a gauge for volume, a history of alerts. It can also publish into your topics. A Home Assistant automation could, for example, send the "homework time" notice to room 214 at 3:30 each afternoon.

Two ways to introduce a device are shown in `server/home-assistant.yaml` and `server/ha_discovery.py`. In the first you write the sensors by hand in `configuration.yaml`, naming the `state_topic`, and using `payload_on: "online"` for a connectivity sensor. In the second, **MQTT discovery**, the device (or a helper) publishes a JSON description to a topic of the form `homeassistant/<component>/<object_id>/config`, and Home Assistant creates the entities by itself. `ha_discovery.py --device desk-07` prints both descriptions:

```json
{ "name": "Online", "unique_id": "osb_crhs_desk_07_online",
  "state_topic": "school/crhs/device/desk-07/status",
  "payload_on": "online", "payload_off": "offline", "device_class": "connectivity", ... }
```

Be clear about what is checked and what is not. The key names and topic format come from Home Assistant's MQTT documentation, and the files are valid YAML and JSON. They have not been tried against a running Home Assistant. Its documentation also says that retained discovery messages can cause stale ("ghost") entities, and recommends republishing discovery when Home Assistant announces that it has started, which this book's script does not do, and that its MQTT integration expects a broker that supports MQTT 5; Mosquitto 2 does, and your Study Buddy still speaks 3.1.1 to it. Check the current Home Assistant documentation before relying on any of this.

## Putting It All Together

The school server publishes a small JSON alert with a unique id to the classroom's topic at QoS 1. A Mosquitto broker on a Raspberry Pi, listening only on the LAN and checking passwords and an access list, forwards it to every subscribed desk. Each desk's `check_msg()` call, made once per audio frame, reads it; a callback validates, de-duplicates, and queues it; and the main loop draws it and beeps once while the microphone ignores the beep. If a desk goes quiet, the keep-alive and the last will tell the dashboard within 45 seconds.

Key takeaways:

- Request-response waits for the client to ask; publish-subscribe lets a broker push news to every subscriber as soon as it is published.
- A topic is a slash-separated name. Design the scheme from general to specific, put the school first, and let devices write only under their own `device/<id>/`.
- `+` matches one level and `#` matches the parent and everything below it, only as the last level; neither is allowed in a publish.
- QoS 0 is at most once, QoS 1 at least once, QoS 2 exactly once. `umqtt.simple` supports 0 and 1; use QoS 1 for alerts with an id to ignore repeats.
- Retain state ("online"), not events; clear a retained message by publishing an empty retained one.
- A last will needs a keep-alive. `umqtt` does not ping for you, so call `ping()` every half interval.
- Poll with `check_msg()` once per frame, never draw or beep in the callback, and bound every connect attempt.
- A broker on the internet invites fake alerts and spying: keep it on the LAN, with passwords, an ACL, and a message size limit.

Test yourself with these three questions, and click each one to reveal its answer.

??? question "Which of the filters `school/+/alert`, `school/crhs/#`, and `#` select the topic `school/crhs/alert`, and which select `school/crhs`? Click to expand"
    All three select `school/crhs/alert`. For `school/crhs`, `school/+/alert` fails (it needs a third level), while `school/crhs/#` selects it because `#` includes its parent level, and `#` selects it too.

??? question "The publisher gets no PUBACK for a QoS 1 alert, so it sends the alert again. What does the desk need to avoid beeping twice? Click to expand"
    A unique `id` in each alert and a record of the ids already seen. QoS 1 promises at least once, not exactly once, so a repeat is part of the contract. The `Seen` class in `alerts.py` drops an alert whose id it already holds.

??? question "A dashboard shows desk-07 as offline every 45 seconds even though the Pico is running. What is the most likely cause? Click to expand"
    The device is not pinging. With a keep-alive of 30 seconds the broker waits 45 seconds for any packet, then closes the connection and publishes the last will. `umqtt.simple` does not ping for you, so call `ping()` every 15 seconds, or publish something at least that often.

!!! mascot-celebration "Alerts, Pushed and Handled"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You just learned the publish-subscribe pattern, a topic scheme with wildcards, QoS levels, retained messages, the last will and keep-alive, and how to poll with `check_msg()` inside the 40 ms audio loop. A school server can now push a test alert to every desk, and your device shows it and beeps without missing the microphone.

In Chapter 16 the school server builds those alerts from a real school calendar.
