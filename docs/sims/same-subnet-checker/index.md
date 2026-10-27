---
title: "Same-Subnet Checker"
description: "AND two IPv4 addresses with a netmask to find their network addresses and check whether the Pico and server can talk directly."
status: built
library: p5.js
bloom_level: Apply
image: /sims/same-subnet-checker/same-subnet-checker.png
og:image: /sims/same-subnet-checker/same-subnet-checker.png
twitter:image: /sims/same-subnet-checker/same-subnet-checker.png
social:
   cards: false
quality_score: 95
---

# Same-Subnet Checker

<iframe src="main.html" width="100%" height="597px" scrolling="no"></iframe>

[Run the Same-Subnet Checker MicroSim Fullscreen](main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/same-subnet-checker/main.html" width="100%" height="597px" scrolling="no"></iframe>
```

## Description

The Pico can talk directly to the buddy server only when both are on the same network. To check, AND each of the four numbers of an address with the matching number of the netmask; the result is the network address, and two addresses are on the same network when their network addresses are equal.

Each address and the mask are shown as four numbers and as 32 bits. The mask's 1 bits are gold, and only the address bits above them are kept; the two network addresses are shown below, with differing kept bits in red. In explore mode you type any two addresses and pick one of four masks. In the quiz you decide same or different and give the first network address for eight cases. The addresses are illustrative.

## How to Use

The MicroSim opens in its starting state and nothing moves until you act.

- **Start the 8 cases / Back to explore**: Switch between the explorer and the quiz.
- **Answer menu, Network address box, Submit**: Choose same or different and type the first network address. One attempt per case.
- **Next case / See score**: Move on after the feedback.
- **First, Second and Mask**: Explore only: two addresses (each number 0 to 255; invalid changes are ignored) and a mask.

## Lesson Plan

### Learning Objective

The learner will calculate whether two IPv4 addresses are on the same network, given a netmask, in 8 cases, with at least 7 of 8 correct.

**Bloom's Taxonomy level:** Apply (calculate)

### Audience and Duration

High school students (grades 9-12) building the Open Study Buddy; about 15 minutes.

### Prerequisites

IP address, netmask, network address, same network, binary form of a number from 0 to 255 (all defined in this chapter above this block; binary numbers are in Chapter 3).

### Activities

1. **Exploration (5 min):** With 192.168.1.23 and 192.168.1.50, switch the mask from 255.255.255.0 to 255.255.0.0, then change the third number of the second address.
2. **Guided practice (5 min):** For case 5, write 5, 15 and 240 in binary and keep only the top 4 bits of each.
3. **Assessment (5 min):** Complete all eight cases. Mastery is 7 of 8 fully correct on the first attempt.

### Common Misconceptions Addressed

(1) Addresses that start with the same number are always on the same network. (2) A mask can only fall between whole numbers. (3) The all-zeros and all-ones device addresses can be given to a device.

### Discussion Questions

1. Are addresses that start with the same number always on the same network?
2. Why can a mask such as 255.255.240.0 split the third number?
3. Why can no device use the all-zeros or all-ones host address?

### Assessment

The quiz inside the MicroSim is the evidence of mastery: each item is scored on the first attempt only, the correct answer and its reason are shown after every submission, and the final screen reports the score against the mastery threshold.

## Specification

<details markdown="1">
<summary>Full specification from Chapter 13</summary>

```text
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
```

</details>

## References

1. [Subnet](https://en.wikipedia.org/wiki/Subnet) - Wikipedia - Netmasks and network addresses.
2. [Bitwise operation](https://en.wikipedia.org/wiki/Bitwise_operation) - Wikipedia - How AND keeps only the masked bits.
3. [IPv4](https://en.wikipedia.org/wiki/IPv4) - Wikipedia - The four-number address format.

## Related Resources

- [Chapter 13: Wi-Fi, HTTP, and Connecting to the Agent](../../chapters/13-wifi-http-agent-link/index.md)
