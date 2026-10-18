---
title: "Personal Agents and the Open Study Buddy Architecture"
description: "What a personal agent is, how open school-hosted agents differ from vendor cloud agents, and how the Open Study Buddy terminal, buddy server, and swappable brain fit together."
generated_by: claude skill chapter-content-generator
date: "2026-10-18 09:54:42"
version: 1.11
---

# Personal Agents and the Open Study Buddy Architecture

## Summary

This chapter explains what a personal agent is and how an open, school-hosted agent differs from a vendor-hosted cloud agent. It then introduces the Open Study Buddy device, which acts as an agent terminal that listens, shows, and speaks, and the buddy server behind it. By the end, students can trace the data flow from a spoken question to a spoken answer and describe the swappable-brain progression from a rule-based server to an LLM-backed agent.

## Concepts Covered

This chapter covers the following 22 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Personal Agent | 1329 |
| Chatbot Versus Agent | 1 |
| Cloud Agent | 192 |
| Open Hardware | 843 |
| Open Source Software | 7 |
| Edge Device | 5 |
| Self-Hosted Agent | 183 |
| Always-On Device | 4 |
| Open Study Buddy Device | 74 |
| Agent Terminal | 72 |
| Buddy Server | 70 |
| Request-Reply Contract | 10 |
| Rule-Based Agent | 12 |
| School-Hosted Agent | 34 |
| Agent Data Flow | 1 |
| Swappable Brain | 2 |
| LLM-Backed Agent | 6 |
| Agent Tools | 4 |
| Open-Source Agent Framework | 2 |
| Agent Memory | 1 |
| Agent Approval Rules | 2 |
| Agent Progression Levels | 1 |

## Prerequisites

This chapter assumes only the prerequisites listed in the [course description](../../course-description.md).

---

## A Desk Companion You Build Yourself

Picture a small round screen on your desk. You press a button and ask, "When is my next test?" A moment later the device answers out loud and shows a countdown on its display. It costs a few tens of dollars, you wired it yourself, and you wrote every line of code that runs on it.

That device is the **Open Study Buddy**, and this book teaches you to build it one feature at a time. Before we touch any wires, we need a shared vocabulary. This chapter defines the words that the rest of the book uses (agent, terminal, server, brain) and shows how they fit together.

!!! mascot-welcome "Hello, Builders! I'm Sage"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    I'm Sage, an owl who loves listening closely, and I'll be your guide through this book. Here is what I do, in the order you will usually meet me in a chapter:

    1. **Welcome:** I open a chapter and tell you what you will be able to build.
    2. **Think:** I mark a big idea that is worth a pause.
    3. **Tip:** I hand you a shortcut that saves time.
    4. **Warn:** I flag a common trap and show you the way out.
    5. **Encourage:** I cheer you on at a hard spot.
    6. **Celebrate:** I close a chapter by naming what you just learned.

    If I'm not doing one of those six things, I'm not in the chapter. Let's listen closely!

By the end of this chapter, you will be able to name every part of the device, explain which parts run on the desk and which run on a school computer, and trace one spoken question all the way to a spoken answer.

## What Is a Personal Agent?

A **personal agent** is software that carries out multi-step work on one person's behalf. Three traits set it apart from other programs:

- **It works for you.** It acts on your calendar, your homework, and your reminders, not on a generic task.
- **It takes several steps.** One request can trigger a chain of actions, such as looking something up, deciding, and then sending an alert.
- **It comes back when it needs a decision.** If an action affects you, the agent asks before it goes ahead.

To do those steps, an agent uses **tools**, which are small programs it is allowed to run, such as "read the school calendar" or "send an alert." We define tools carefully later in this chapter. For now, think of a tool as one thing the agent can do.

### A Worked Example: Getting Ready for Friday

Suppose Maya says, "Get me ready for Friday's test." A personal agent could handle that request in five steps:

1. It reads the school calendar and finds an event titled "TEST: Biology" on Friday.
2. It checks for other deadlines and finds "DUE: Lab report" on Thursday.
3. It builds a short plan: finish the lab report Thursday, review notes Thursday night.
4. It schedules a reminder for Thursday at 7 pm.
5. It asks Maya, "Should I move your study session to 6 pm?" and waits for her answer before changing anything.

Notice that Maya made one request, the agent did the multi-step work, and the agent came back with a question before it changed Maya's schedule. Those are the three traits in action.

### Chatbot Versus Agent

A **chatbot** answers one message at a time. You type, it replies, and then it waits for your next message. It does not read your calendar, it does not set reminders, and it does not act when you are away. A chatbot's reply is the whole job, while for an agent the reply is often just the last step.

The table below summarizes the difference using the traits we just defined.

| Question | Chatbot | Personal agent |
|----------|---------|----------------|
| Who starts each piece of work? | You, with every message | You for the first request, then the agent on its own |
| How many steps per request? | One reply | Several steps in a chain |
| Does it use tools? | Usually not | Yes, such as calendar and alerts |
| Does it act when you are away? | No | Yes, such as a morning reminder |
| Does it ask before acting? | Not needed, it only talks | Yes, before actions that affect you |

Many agents contain a chatbot-style language model inside, so the line can look blurry. The test is simple: if the software only produces a reply, it is a chatbot, and if it takes actions for you, it is acting as an agent.

The next activity lets you practice that test on ten described behaviors.

#### Diagram: Chatbot or Agent Sorter

<details markdown="1">
<summary>Chatbot or Agent Sorter</summary>
Type: microsim
**sim-id:** chatbot-or-agent-sorter<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Template:** https://github.com/dmccreary/conversational-ai/tree/main/docs/sims/chat-interface-anatomy<br/>
**Bloom Level:** Analyze<br/>
**Bloom Verb:** distinguish<br/>
**Learning Objective:** The learner will distinguish chatbot behaviors from personal-agent behaviors by classifying 10 described behaviors, with at least 8 of 10 correct on the first attempt.

**Prerequisites:** personal agent, chatbot, tool, multi-step work (all defined in the section "What Is a Personal Agent?" above this block).

**Evidence of Mastery:** For each of the 10 behaviors, the learner commits to one of two bins, "Chatbot behavior" or "Agent behavior". A classification is correct when it matches the Correct bin column in Content. Mastery is 8 of 10 correct. Reading a behavior without committing is not evidence.

**Misconceptions:** (1) Any program that talks is an agent. (2) A chatbot that sounds smart is an agent. (3) An agent must be a robot or a physical device.

**Instructional Rationale:** Analyze-level distinguishing requires the learner to apply the three traits to new cases rather than recite them. A forced two-way choice on concrete behaviors makes the learner decide which trait is present, and the one-sentence reason after each answer names the trait.

**Content:**

The learner sees the behaviors one at a time in this fixed order:

| # | Behavior shown to the learner | Correct bin | Why (shown as feedback) |
|---|---|---|---|
| 1 | Answers one typed question, then waits for the next message. | Chatbot behavior | It replies to a single message and takes no further action. |
| 2 | Reads the school calendar, finds a test, and adds a reminder for the night before. | Agent behavior | It uses a tool and acts in several steps without being asked for each one. |
| 3 | Explains what a "TEST:" event is when asked, with no access to any calendar. | Chatbot behavior | It gives information only and takes no action for the person. |
| 4 | Asks "Should I move your study session to 6 pm?" before changing the schedule. | Agent behavior | It comes back for a decision before an action that affects the person. |
| 5 | Rewrites a paragraph that the student pastes in. | Chatbot behavior | One request produces one reply, and the work ends there. |
| 6 | Checks every morning for new due dates and announces them. | Agent behavior | It acts on its own over time on the person's behalf. |
| 7 | Tells a joke when asked. | Chatbot behavior | It produces a reply only. |
| 8 | Sends an alert to the student's desk device when a test is one day away. | Agent behavior | It takes an action through a tool, without being asked at that moment. |
| 9 | Remembers that the student prefers 7 pm reminders and schedules the next reminder for 7 pm. | Agent behavior | It uses what it remembers to take an action on the person's behalf. |
| 10 | Summarizes a news article that the student pastes in. | Chatbot behavior | One request produces one reply, and no action follows. |

**Provenance:** Illustrative behaviors written for this sim from the chapter section "What Is a Personal Agent?". The sim labels them "illustrative".

**Rules:** A behavior belongs in "Agent behavior" when it includes at least one of these: it uses a tool to take an action, it works in more than one step, it acts without being prompted at that moment, or it asks for approval before an action. Otherwise it belongs in "Chatbot behavior". The score is the count of correct classifications, from 0 to 10.

**Learner Activity:**

1. The learner reads behavior 1 and chooses a bin.
2. The sim shows whether the choice was correct and the reason from the Why column, then the learner continues to the next behavior.
3. After behavior 10, the sim shows the score and lists each missed behavior with its reason.
4. The learner can restart with the same 10 behaviors in a new random order. Only the first run counts as evidence.

**Feedback:** Ten items, fixed order on the first run, one attempt per item. Correct: "Correct: <Why>". Incorrect: "Not quite: <Why>". The correct bin is revealed immediately after each answer. A running score "n of 10" is shown after every answer.

**Starting State:** Behavior 1 is shown with the two bins and the question "Is this a chatbot behavior or an agent behavior?"

**Chapter Anchors:** A chatbot answers one message at a time. An agent uses tools, works in several steps, and comes back when it needs a decision.
</details>

## Where an Agent Lives

An agent is software, so it has to run on a computer somewhere. Where it runs decides who controls it, what it costs, and what happens to your data. This section defines the computing terms first and then compares the three places an agent can live.

### Edge Devices and Always-On Devices

An **edge device** is a small computer at the "edge" of the network, close to the person who uses it, instead of in a distant data center. Phones, smart speakers, and your Raspberry Pi Pico are all edge devices. Their strengths are speed and presence: a button press is handled right where you are.

The Pico has a catch. It has only about half a megabyte of working memory, thousands of times less than a typical phone. That is plenty for reading buttons and driving a display, but far too little to run a large AI model.

*Worked example.* When you press the volume button on your Study Buddy, the Pico changes the volume immediately, because that decision needs no network and no server. When you ask a question about your test schedule, the Pico cannot answer alone. It must pass the question to a bigger computer. Keep that split in mind, because it explains the whole architecture of this book.

An **always-on device** stays powered and ready to respond whenever you need it. Your desk Study Buddy is always on in this sense: it plugs into USB power and waits, so there is no boot time when you want an answer.

!!! mascot-warning "Two Phrases, Two Meanings"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    Watch out for mixing up "always-on" and "always-listening." Always-on means the device has power and is ready, while always-listening means its microphone is being processed all the time. This book's default is push-to-talk, and always-listening needs approval from a parent, teacher, or school first.

*Worked example.* Your Study Buddy sits on the desk all night, always on. Its microphone is not being processed until you switch it to listening. A different device with a wake word, such as "Hey Pico," would need to process sound continuously to hear it, which is why Chapters 12 and 17 treat that mode with extra care.

### Cloud Agents

A **cloud agent** is an agent that runs on a vendor's computers in a remote data center and that you reach over the Internet. The vendor owns the hardware, writes and updates the software, and usually charges a monthly subscription. Cloud agents are popular because they are easy to start: you sign up and begin.

The price of that ease is control. The vendor decides what the agent can do, what happens to the audio and text you send, and how long the service lasts.

*Worked example.* Suppose you ask a cloud agent about your test. Your question travels over the Internet to the vendor's data center and is processed there, under the vendor's rules about storage and use. If you stop paying, or the vendor changes the service, your agent changes or disappears. None of this is bad by itself, but you should know it is happening, and you cannot inspect or change the software.

### Self-Hosted Agents

A **self-hosted agent** is an agent that runs on a computer you or your organization controls, such as a laptop, a spare Raspberry Pi, or a school server. You choose the software, you decide which data it may touch, and you can read and change how it works. The price of control is responsibility: you keep it updated and secure.

*Worked example.* Alex's coding club runs a small agent on a spare Raspberry Pi in the lab. The hardware cost is paid once, the club decides what the agent can read, and members can change how it answers. The trade-off is time. When a software update arrives, someone in the club has to install it.

### School-Hosted Agents

A **school-hosted agent** is a self-hosted agent that a school runs for its students. One school computer runs the agent, and every student's device connects to it. The school configures it for school needs: which calendar it reads, what voice and mascot it uses, and how long it keeps any data.

*Worked example.* A school sets up one agent that reads the school calendar. Every classroom device asks that one server for the next event. When the calendar contains "TEST: Biology" for Friday, every device can announce it, and the school decides whether any request is saved or deleted. This is the setup the Open Study Buddy is designed for.

!!! mascot-thinking "The Real Question: Who Controls It?"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Notice that "cloud or not" matters less than "who controls it." Ask who can see your requests, who can change the agent's behavior, and who can switch it off.

### Comparing the Three Hosting Options

With the three terms defined, the table below summarizes how they differ.

| Question | Cloud agent | Self-hosted agent | School-hosted agent |
|----------|-------------|-------------------|---------------------|
| Who runs the computer? | The vendor, in a data center | You or your group | The school |
| Who decides what data it can touch? | The vendor's terms and settings | You | The school |
| Typical cost pattern | A recurring subscription fee | Hardware you already own, plus your own time | Shared school hardware and staff time, used by every student's device |
| Who keeps it running? | The vendor | You | School staff |

The next activity asks you to choose an option for four situations and name the deciding factor.

#### Diagram: Agent Hosting Trade-Off Explorer

<details markdown="1">
<summary>Agent Hosting Trade-Off Explorer</summary>
Type: microsim
**sim-id:** agent-hosting-tradeoff-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Evaluate<br/>
**Bloom Verb:** recommend<br/>
**Learning Objective:** The learner will recommend one of three hosting options (cloud agent, self-hosted agent, school-hosted agent) for each of four scenarios and identify the deciding factor, with at least 3 of 4 scenarios fully correct.

**Prerequisites:** cloud agent, self-hosted agent, school-hosted agent, and the four comparison questions (all defined in the section "Where an Agent Lives" above this block).

**Evidence of Mastery:** For each scenario, the learner first commits to a hosting option and then commits to the deciding factor from four choices. A scenario is fully correct when both choices match the Correct columns in Content. Mastery is 3 of 4 scenarios fully correct. Reading the comparison table is exploration, not evidence.

**Misconceptions:** (1) A cloud agent is always the best choice because it is easiest. (2) Self-hosting is only for experts. (3) Hosting only affects cost, not who sees the data.

**Instructional Rationale:** Evaluate-level recommending requires the learner to weigh criteria against a situation. Choosing the option and then naming the one factor that decides it makes the learner justify the choice, and committing before the table is highlighted prevents simply reading the answer off.

**Content:**

The learner sees the four comparison questions as the factors, labeled A to D:

| Factor | Question |
|---|---|
| A | Who runs the computer? |
| B | Who decides what data it can touch? |
| C | What is the typical cost pattern? |
| D | Who keeps it running? |

The three options and their answers to the four factors are exactly the values in the chapter table "Comparing the Three Hosting Options". The learner sees four scenarios in this fixed order:

| # | Scenario shown to the learner | Correct option | Correct factor | Why (shown as feedback) |
|---|---|---|---|---|
| 1 | A student wants an agent today, with no setup, and the questions contain nothing private. | Cloud agent | D | The vendor keeps it running, so the student has nothing to maintain. |
| 2 | A coding club wants to learn how agents work by reading and changing the agent's code. | Self-hosted agent | A | The club runs the computer, so it can open and change the software. |
| 3 | A school wants every classroom device to announce the school calendar, with the school deciding what is kept. | School-hosted agent | B | One school server serves every device, and the school decides what data it touches. |
| 4 | A family wants an assistant whose audio never leaves their home network. | Self-hosted agent | B | The family decides what data the agent touches, and nothing goes to a vendor. |

**Provenance:** The options and factors come from the chapter section "Where an Agent Lives". The four scenarios are illustrative, written for this sim, and the sim labels them "illustrative".

**Rules:** An option answer is correct when it equals the Correct option for that scenario. A factor answer is correct when it equals the Correct factor. A scenario is fully correct only when both are correct. The score is the number of fully correct scenarios, from 0 to 4.

**Learner Activity:**

1. The learner reads scenario 1 and chooses one of the three options.
2. The learner chooses the deciding factor, A to D.
3. The sim then highlights the matching cells of the comparison table and shows the Why text.
4. The learner continues through scenarios 2 to 4 in the same way.
5. After scenario 4 the sim shows the score and the cells of the comparison table that were decisive in each scenario.

**Feedback:** Four scenarios, fixed order, one attempt for the option and one for the factor. Correct: "Correct: <Why>". Incorrect option: "Not quite: <Why>". Incorrect factor with a correct option: "Right option. The deciding factor is <factor letter and question>: <Why>". The correct answers are revealed after both choices are made. A running count "Scenarios fully correct: n of 4" is shown.

**Starting State:** The comparison table is visible without highlights, scenario 1 is shown, and the question on screen is "Which option would you recommend?"

**Chapter Anchors:** The chapter table "Comparing the Three Hosting Options" has four questions and three options with the exact values used in the Content. The chapter states that a cloud agent is run by a vendor, and that a school-hosted agent is a self-hosted agent run by a school.
</details>

## What "Open" Means Here

The Open Study Buddy is open in two senses: its hardware and its software. These two ideas look similar but mean different things.

### Open Hardware

**Open hardware** is hardware whose design is published, so anyone can study it, build it, repair it, and change it. The kit is open in a practical way too: it uses common, documented parts that you can buy from many sellers, instead of a sealed box that only one company can service.

*Worked example.* Suppose your speaker cracks. Because the speaker connects through a standard amplifier board, you can unplug it and wire in another small speaker that suits that amplifier. You do not need the vendor's permission, a special part number, or a replacement for the whole device. Chapter 4 shows the wiring for each part.

The table below contrasts the two approaches.

| Question | Closed hardware | Open hardware |
|----------|-----------------|---------------|
| Can you see how it is built? | No | Yes, the design is published |
| Can you replace a broken part? | Often only with the maker's part | Yes, with any compatible part |
| Can you add a feature? | Only if the maker allows it | Yes, you can modify it |
| Who can repair it? | Usually the maker | You, your club, or your school |

### Open Source Software

**Open source software** is software whose source code is published under a license that lets you read it, run it, change it, and share it. MicroPython, the language you will use throughout this book, is open source, and so is the code you will write for the buddy server.

*Worked example.* Open the buddy server's rule file and find the line that says "Sorry, I only know about tests and due dates." If you want a friendlier message, you can change that sentence and restart the server. With closed software, the same change would mean filing a request and waiting.

Two cautions keep "open" honest. Open source does not mean free of work, because someone still has to maintain it. It also does not mean automatically safe, because anyone can publish code, including code with mistakes.

!!! mascot-tip "Read Before You Run"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Before you run code someone else wrote, search it for network calls and see where it sends data. That one check tells you what leaves your device.

## The Open Study Buddy Device

Now we can describe the device itself. The **Open Study Buddy device** is a desk-sized hardware kit built around a Raspberry Pi Pico 2 W microcontroller, which is a small, low-cost computer on a single chip, with Wi-Fi built in. It has five groups of parts:

| Part | Its job on the desk |
|------|---------------------|
| Raspberry Pi Pico 2 W | Runs your MicroPython program and connects to Wi-Fi |
| Round color display (360 × 360 pixels) | Shows the clock, the agent's words, and status |
| INMP441 microphone | Turns sound into digital numbers the Pico can read |
| MAX98357A amplifier and a small speaker | Turns digital audio numbers back into sound |
| Mode, Up, and Down buttons | Let you change modes, move through menus, and adjust values |

*Worked example.* Here is a day in the life of one device. You press the Mode button to switch from the clock to listening, and ask your question. The display shows a "thinking" message while the answer is prepared, then the speaker reads the answer aloud. Afterward you press Up and Down to adjust the volume. Every step in that story uses one of the five groups of parts.

The whole kit costs a few tens of dollars, and Chapter 4 lists every part and its wiring.

### The Agent Terminal

The Pico cannot think like a large AI system, so the Study Buddy does not try to. It works as an **agent terminal**, a device that gives an agent ears, a voice, and a face, but not its brain. The terminal collects your input from the microphone and buttons, shows output on the display and speaker, and sends your requests to the computer where the agent actually runs.

An everyday comparison is a walkie-talkie. The walkie-talkie lets you speak and listen, but the helpful person you are talking to is in another room. Keeping the terminal "thin" has two benefits. It fits within the Pico's small memory, and you can upgrade the agent's brain without rewriting the device's code.

*Worked example.* When you ask for your next test, the terminal does three things: it captures your voice, it sends the request to the server, and it plays the reply it receives. It does not search the calendar or write the answer. If the school changes the calendar, nothing on the terminal needs to change.

### The Buddy Server

The **buddy server** is the program that receives the terminal's requests, decides on a reply, and sends it back. It runs on a nearby computer, such as a Raspberry Pi that the school keeps on its network. The buddy server holds the school's configuration, the calendar data, and the agent's decision logic.

One buddy server can serve many terminals at once.

*Worked example.* Three students in the same classroom ask for the next test at the same moment. Each device sends its own request with its own device name. The buddy server answers each request separately and sends each reply back to the device that asked, so three students hear three answers at the same time.

!!! mascot-thinking "Ears and Voice Here, Brain There"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Here is the big mental shift: the device on your desk is not where the thinking happens. It is the face, ears, and voice, and the brain can live in another room.

The next activity lets you explore the parts of the system and test yourself on each one's job.

#### Diagram: Study Buddy Architecture Explorer

<details markdown="1">
<summary>Study Buddy Architecture Explorer</summary>
Type: graph-model
**sim-id:** study-buddy-architecture-explorer<br/>
**Library:** vis-network<br/>
**Status:** Specified<br/>
**Template:** https://github.com/dmccreary/bioinformatics/tree/main/docs/sims/profile-hmm-architecture<br/>
**Bloom Level:** Remember<br/>
**Bloom Verb:** identify<br/>
**Learning Objective:** The learner will identify the job of each of the five kit parts and of the buddy server by matching six described jobs to the correct part, with at least 5 of 6 correct.

**Prerequisites:** Open Study Buddy device, agent terminal, buddy server, and the five kit parts (all defined in the section "The Open Study Buddy Device" above this block).

**Evidence of Mastery:** In quiz mode the sim shows one job description and the learner clicks the part that does that job. A click is correct when it matches the Correct part column in Content. Mastery is 5 of 6 correct on the first attempt. Hovering and clicking in explore mode is exploration, not evidence.

**Misconceptions:** (1) The speaker and the amplifier are the same thing. (2) The buddy server is part of the desk device. (3) The Pico sends sound straight to the display.

**Instructional Rationale:** Remember-level identification needs retrieval, so the learner first explores each part and then retrieves the matching part from a job description. Showing the connections reveals which parts talk to the Pico and which talk across the network, which is the structure the chapter describes.

**Content:**

Six nodes, in two groups. The group "Agent terminal (the desk device)" contains five nodes, and the group "School network" contains one node. Each node shows this text when hovered or clicked:

| Node | Group | Job text revealed |
|---|---|---|
| Raspberry Pi Pico 2 W | Agent terminal | Runs the terminal program, reads the microphone and buttons, drives the display and speaker, and talks to the buddy server over Wi-Fi. |
| Round color display | Agent terminal | Shows the clock, the agent's words, and status as a 360 by 360 pixel round picture. |
| INMP441 microphone | Agent terminal | Turns sound into digital numbers that the Pico can read. |
| MAX98357A amplifier and speaker | Agent terminal | Turns digital audio numbers into sound that the student hears. |
| Mode, Up, and Down buttons | Agent terminal | Let the student change modes, move through menus, and adjust values by hand. |
| Buddy server | School network | Receives requests, decides on a reply, and sends it back. It runs on a school computer and is not part of the desk device. |

Five edges. The meaning of each edge is shown when either of its two nodes is selected:

| From | To | Meaning |
|---|---|---|
| INMP441 microphone | Raspberry Pi Pico 2 W | Sends digital sound numbers to the Pico. |
| Mode, Up, and Down buttons | Raspberry Pi Pico 2 W | Send button presses to the Pico. |
| Raspberry Pi Pico 2 W | Round color display | Sends text and pictures to show. |
| Raspberry Pi Pico 2 W | MAX98357A amplifier and speaker | Sends digital audio numbers to play. |
| Raspberry Pi Pico 2 W | Buddy server | Sends requests and receives replies over Wi-Fi on the school network. |

Quiz questions, in this fixed order:

| # | Job description shown | Correct part |
|---|---|---|
| 1 | Turns sound into digital numbers. | INMP441 microphone |
| 2 | Turns digital audio numbers into sound the student hears. | MAX98357A amplifier and speaker |
| 3 | Shows the clock and the agent's words as a round picture. | Round color display |
| 4 | Runs the terminal program and connects to Wi-Fi. | Raspberry Pi Pico 2 W |
| 5 | Lets the student change modes and adjust values by hand. | Mode, Up, and Down buttons |
| 6 | Decides on a reply and sends it back, from a school computer. | Buddy server |

**Provenance:** From the chapter section "The Open Study Buddy Device" and the table of five kit parts there. The sim labels the quiz wording "written for this sim".

**Rules:** A quiz answer is correct when the clicked node equals the Correct part. The score is the number of correct answers, from 0 to 6. Selecting a node in explore mode highlights that node and every edge connected to it.

**Learner Activity:**

1. In explore mode, the learner hovers or clicks each of the six nodes to read its job text.
2. The learner selects a node and sees its connected edges and their meanings.
3. The learner answers the question: "Which part must the Pico talk to over Wi-Fi?" (answer: the buddy server).
4. The learner switches to quiz mode and clicks the matching part for each of the six job descriptions.
5. After question 6 the sim shows the score and lists each missed part with its job text.

**Feedback:** Six questions, fixed order, one attempt per question. Correct: "Correct: <job text>". Incorrect: "Not quite. The part that does this is <correct part>: <job text>". The correct part is revealed immediately after each answer, and a running score "n of 6" is shown.

**Starting State:** All six nodes and five edges are visible with no node selected, in explore mode, with the instruction "Click a part to learn its job."

**Chapter Anchors:** The device has five groups of parts. The buddy server is not part of the desk device. The terminal talks to the buddy server over Wi-Fi on the school network.
</details>

## How the Terminal and Server Talk

The terminal and the buddy server are separate programs on separate computers, so they need an agreement about how to talk. That agreement has a name, and it makes the rest of the architecture possible.

### The Request-Reply Contract

The **request-reply contract** is the agreed format of what the terminal sends (the request) and what the server returns (the reply). The terminal does not need to know how the server decides its answer. It only needs to know what to send and what shape of reply to expect.

Before we look at an example, one definition: **JSON** is a plain-text format for labeled values, written as names and values inside curly braces. Chapter 13 teaches it properly. In the example below, the names `device`, `kind`, and `text` are illustrative, because the real contract is defined in Chapter 13. The request says which device is asking, what kind of request it is, and what the student said, already converted to text.

```json
{
  "device": "desk-07",
  "kind": "question",
  "text": "when is my next test"
}
```

The reply says what to speak, what to show on the display, and which mode the device should go to next:

```json
{
  "speak": "Your next test is Biology on Friday.",
  "show": "Biology test: Friday",
  "next_mode": "clock"
}
```

*Worked example.* Notice what the terminal does with this reply. It sends the `speak` text to the speaker, puts the `show` text on the display, and switches to the mode in `next_mode`. It never needed to know that the reply came from a calendar lookup. If a different server sent an identical reply shape, the terminal would work the same way.

### The Agent Data Flow

The **agent data flow** is the path one request takes from the student's voice to the spoken answer. Here are the eight steps, with the part that does each step in brackets. We use two new terms. **Speech-to-text** is a service that turns recorded speech into written words, and **text-to-speech** is a service that turns written words into speech. Chapter 14 shows how both are used.

1. The student speaks. *(Student)*
2. The microphone captures the sound as digital numbers. *(Terminal)*
3. The request travels from the terminal to the server over Wi-Fi. *(Network)*
4. The server converts the speech to text: "when is my next test". *(Server)*
5. The brain decides on the reply: "Your next test is Biology on Friday." *(Server)*
6. The server converts the reply to speech and packages the reply. *(Server)*
7. The reply travels back to the terminal over Wi-Fi. *(Network)*
8. The terminal shows the text on the display and plays the speech. *(Terminal)*

Step 1 is yours. Two steps happen on the terminal, three happen on the server, and two happen on the network between them. The word "brain" in step 5 means whatever logic decides the reply, and we examine it in the next section.

!!! mascot-tip "Check the Signal First"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    When your buddy stays silent, test the steps in order: microphone, Wi-Fi, server, then reply. Finding the first silent step is much faster than guessing.

The next activity walks through the eight steps and asks you to predict who does each one.

#### Diagram: Agent Data Flow Step-Through

<details markdown="1">
<summary>Agent Data Flow Step-Through</summary>
Type: microsim
**sim-id:** agent-data-flow-step-through<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Template:** https://github.com/dmccreary/conversational-ai/tree/main/docs/sims/response-generation-architecture<br/>
**Bloom Level:** Understand<br/>
**Bloom Verb:** explain<br/>
**Learning Objective:** The learner will explain which of three parts (terminal, network, server) performs each of the eight steps that carry a spoken question to a spoken answer, by predicting the owner of steps 2 to 8 with at least 6 of 7 correct.

**Prerequisites:** agent terminal, buddy server, request-reply contract, speech-to-text, text-to-speech (all defined in the section "How the Terminal and Server Talk" above this block).

**Evidence of Mastery:** Before each of steps 2 to 8 is revealed, the learner commits to the part that performs it: Terminal, Network, or Server. A prediction is correct when it matches the Owner column in Content. Mastery is 6 of 7 correct. Pressing Next without predicting is not allowed.

**Misconceptions:** (1) The Pico decides the answer. (2) The microphone sends sound straight to the speaker. (3) The Wi-Fi link understands the question.

**Instructional Rationale:** Understand-level explanation needs the learner to trace the process with concrete data. Step-through with prediction before reveal makes the learner reason about which part has the memory and the job, and the concrete values shown at each step prevent a vague answer. There is no animation, because animation would hide the data at each step.

**Content:**

The scenario is the question "When is my next test?" The learner sees these eight steps in order, with the data shown at each step:

| Step | What happens | Data shown | Owner | Why the owner (shown as feedback) |
|---|---|---|---|---|
| 1 | The student speaks | The spoken words "When is my next test?" | Student | Shown to start the scenario, and not predicted. |
| 2 | The microphone captures sound as digital numbers | Illustrative sample values: 12, -40, 85, 130, 60, -25 | Terminal | The microphone is wired to the Pico, so the terminal captures the sound. |
| 3 | The request travels to the server | The request fields: device = desk-07, kind = question, plus the sound numbers | Network | The Wi-Fi link only carries the request. It does not read or change it. |
| 4 | The server converts speech to text | The text "when is my next test" | Server | Speech-to-text needs more memory than the Pico has, so the server does it. |
| 5 | The brain decides the reply | Event found: "TEST: Biology, Friday". Reply text: "Your next test is Biology on Friday." | Server | The calendar and the decision logic live on the server. |
| 6 | The server converts the reply to speech and packages it | The reply fields: speak = the sentence as audio, show = "Biology test: Friday" | Server | Text-to-speech also needs more memory than the Pico has. |
| 7 | The reply travels back to the terminal | The same reply fields moving from the server to desk-07 | Network | The Wi-Fi link only carries the reply. |
| 8 | The terminal shows and plays the reply | The display shows "Biology test: Friday". The speaker says "Your next test is Biology on Friday." | Terminal | The display and speaker are wired to the Pico, so the terminal outputs the reply. |

**Provenance:** An illustrative scenario written for this sim from the chapter section "How the Terminal and Server Talk". The sample values are illustrative and the sim labels them "illustrative".

**Rules:** There are eight steps and three owners. The prediction applies to steps 2 to 8, which is 7 predictions. A prediction is correct when it equals the Owner of that step. The score is the number of correct predictions, from 0 to 7. The correct owner is always revealed after the prediction, and the data for that step is then shown.

**Learner Activity:**

1. Step 1 is shown. The learner sees the spoken question.
2. For step 2 the learner chooses Terminal, Network, or Server.
3. The sim reveals the correct owner, the step description, and the data shown for that step, with the reason if the prediction was wrong.
4. The learner presses Next and repeats for steps 3 to 8.
5. After step 8, the sim shows a summary that groups the eight steps by owner and shows the score.

**Feedback:** Seven predictions, fixed order, one attempt each. Correct: "Correct: <Owner>. <Why the owner>". Incorrect: "Not quite. The <Owner> does this step. <Why the owner>". The owner is revealed immediately after each prediction. A running score "n of 7" is shown.

**Starting State:** Step 1 is shown with the spoken question, the terminal and the server shown as separate parts, and the question "Which part performs step 2?"

**Chapter Anchors:** There are eight steps. Step 1 is the student's, two steps happen on the terminal (2 and 8), three happen on the server (4, 5, 6), and two happen on the network (3 and 7). The example question is "When is my next test?" and the example reply is "Your next test is Biology on Friday."
</details>

## The Swappable Brain

Look again at step 5 of the data flow. Because the request-reply contract keeps the terminal separate from the decision logic, you can replace the logic without touching the terminal. That property is the **swappable brain**: the same device can talk to a very simple brain today and a much more capable brain next month.

!!! mascot-encourage "A Lot of Words at Once"
    ![Sage encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    If eight new terms in a row feels like a lot, that is normal. You will build the simplest level first, and it uses only two of them: rules and tools. Come back to this section when each term shows up in code.

This section introduces the possible brains and the ideas around them, starting with the simplest.

### Rule-Based Agents

A **rule-based agent** decides using rules that a person wrote in advance, such as "if the question mentions a test, look up the next test event." It is small, predictable, and needs no AI model. It can run comfortably on a Raspberry Pi. Its weakness is that it only handles what its rules anticipated.

Before we look at code, here is what the example does. It lowercases the question text so that capital letters do not matter, checks for the word "test" or "due," and falls back to an apology otherwise. The helper `next_event_with_prefix` is illustrative, and Chapter 16 builds the real ones.

```python
def decide(text, events):
    words = text.lower()
    if "test" in words:
        event = next_event_with_prefix(events, "TEST:")
        return f"Your next test is {event.title} on {event.day}."
    if "due" in words:
        event = next_event_with_prefix(events, "DUE:")
        return f"{event.title} is due on {event.day}."
    return "Sorry, I only know about tests and due dates."
```

*Worked example.* The question "When is my next test?" matches the first rule and gets a correct answer. The question "Do I have anything big coming up this week?" contains neither word, so the agent falls through to the apology, even though the answer is sitting in the calendar. That gap is exactly what the next kind of brain tries to close.

### LLM-Backed Agents

A **large language model**, or **LLM**, is an AI program trained on huge amounts of text that predicts and writes text. An **LLM-backed agent** uses an LLM to interpret questions phrased in many different ways and to write natural answers. The LLM does not run on the Pico, and usually not on a small buddy server either. It runs on a more powerful computer or a vendor's service.

*Worked example.* Ask the LLM-backed agent, "Do I have anything big coming up this week?" It can interpret "big" to mean tests and project deadlines, find "TEST: Biology" on Friday and "DUE: Lab report" on Thursday, and answer, "You have a lab report due Thursday and a Biology test on Friday." No rule was written for that phrasing.

The trade-offs are real. An LLM-backed agent needs more computing power. If the LLM is hosted by a vendor, your text leaves your school network. And an LLM can produce a confident answer that is wrong.

### Agent Tools

**Agent tools** are the functions an agent is allowed to call to fetch facts or take actions, such as "list upcoming events" or "send an alert." A rule-based agent calls a tool when a rule says to. An LLM-backed agent can choose which tool to call for a request it has never seen before.

Tools matter for two reasons. They give the agent real facts to work from, and they set limits, because the agent can only do what its tools allow.

*Worked example.* For "When is my next test?" the agent calls a tool named something like `get_events` with the filter "TEST:". The tool returns the real list from the school calendar, and the agent turns the first item into a sentence. The date came from the calendar, not from the model's imagination.

!!! mascot-warning "Confident Is Not Correct"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    An LLM can sound sure and still be wrong about a date. Make the agent read dates through a tool, and show the source on the display so you can check it.

### Agent Memory

**Agent memory** is information an agent keeps between requests, such as your preferred reminder time or the topic of the last question. Short-term memory covers the current conversation, while long-term memory is stored and survives restarts. Memory is also data, so the privacy chapter treats it carefully.

### Agent Approval Rules

**Agent approval rules** state which actions an agent may take on its own and which need a human "yes" first. For example: reading the calendar is allowed, sending a message to a classmate needs approval, and deleting an event is never allowed. These rules are how you apply the third trait of an agent, coming back for a decision.

### Open-Source Agent Frameworks

An **open-source agent framework** is a published, reusable toolkit that supplies the common pieces of an agent, such as a loop that plans steps, tool calling, memory, and approval rules, so you do not write them from scratch. A school can self-host one and put it behind the same request-reply contract. This book treats frameworks as optional and does not teach a specific product, because the landscape changes quickly.

### Agent Progression Levels

Putting the pieces together gives a three-step ladder. The **agent progression levels** are the stages through which the buddy server grows, and each level keeps the same terminal and the same contract.

| Level | Brain | What it adds |
|-------|-------|--------------|
| 1 | Rule-based buddy server (about 100 lines, no LLM) | Fixed rules and tools that read the school calendar |
| 2 | The same server plus speech-to-text, text-to-speech, and one LLM call | Spoken input and output, and free-form questions |
| 3 | An optional open-source agent framework behind the same contract | Ready-made planning loop, memory, and approval rules |

*Worked example.* Take the question "Do I have anything big coming up this week?" At Level 1 the server replies, "Sorry, I only know about tests and due dates." At Level 2 it replies, "You have a lab report due Thursday and a Biology test on Friday." At Level 3 it can add, "I can set a reminder for Thursday at 7 pm. Should I?" which uses the approval rules before it acts. The terminal code is identical at all three levels.

The last activity asks you to place abilities on the ladder.

#### Diagram: Agent Progression Level Explorer

<details markdown="1">
<summary>Agent Progression Level Explorer</summary>
Type: microsim
**sim-id:** agent-progression-level-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Template:** https://github.com/dmccreary/ai-strategy-for-education/tree/main/docs/sims/ai-agent-anatomy<br/>
**Bloom Level:** Analyze<br/>
**Bloom Verb:** differentiate<br/>
**Learning Objective:** The learner will differentiate the three agent progression levels by placing 8 abilities at the lowest level where each first appears, with at least 7 of 8 correct.

**Prerequisites:** rule-based agent, LLM-backed agent, agent tools, agent memory, agent approval rules, open-source agent framework, and the three levels (all defined in the section "The Swappable Brain" above this block).

**Evidence of Mastery:** For each of the 8 abilities, the learner commits to Level 1, Level 2, or Level 3. A placement is correct when it matches the Correct level column in Content. Mastery is 7 of 8 on the first attempt. Comparing the three replies in the second part is exploration, not evidence.

**Misconceptions:** (1) Only Level 3 can use tools. (2) A higher level needs a different terminal. (3) An LLM always gives a correct answer.

**Instructional Rationale:** Analyze-level differentiation requires the learner to tell which capability comes from which kind of brain. Placing each ability on the ladder after predicting, and then comparing the replies of all three levels to the same question, shows that the abilities differ while the request-reply contract stays the same.

**Content:**

The three levels are the values in the chapter table "Agent Progression Levels". The learner sees the abilities one at a time in this fixed order:

| # | Ability shown to the learner | Correct level | Why (shown as feedback) |
|---|---|---|---|
| 1 | Matches the question text against fixed rules a person wrote. | Level 1 | A rule-based server is made of exactly these rules. |
| 2 | Reads events from the school calendar using a tool. | Level 1 | Even the rule-based server calls tools when a rule says to. |
| 3 | Answers a question worded in a way no rule anticipated. | Level 2 | Interpreting free-form wording is what the LLM call adds. |
| 4 | Converts the student's speech to text and the reply back to speech. | Level 2 | Level 2 adds speech-to-text and text-to-speech. |
| 5 | Chooses for itself which tool to call for a new kind of request. | Level 2 | An LLM-backed agent can choose tools instead of following a rule. |
| 6 | Remembers a preferred reminder time between conversations using a ready-made memory feature. | Level 3 | A framework supplies memory so you do not build it yourself. |
| 7 | Asks for approval before a risky action using ready-made approval rules. | Level 3 | A framework supplies approval rules that apply before an action. |
| 8 | Runs a planning loop with tools, memory, and approvals supplied by a published toolkit. | Level 3 | That combination is what an open-source agent framework provides. |

After the eight placements, the learner compares replies. The question is "Do I have anything big coming up this week?" and the learner chooses a level to see its reply:

| Level | Reply shown |
|---|---|
| 1 | "Sorry, I only know about tests and due dates." |
| 2 | "You have a lab report due Thursday and a Biology test on Friday." |
| 3 | "You have a lab report due Thursday and a Biology test on Friday. I can set a reminder for Thursday at 7 pm. Should I?" |

For every level the sim also shows the same request and the same reply shape, with the fields `device`, `kind`, and `text` in the request and `speak`, `show`, and `next_mode` in the reply.

**Provenance:** The levels and the replies come from the chapter sections "Agent Progression Levels" and "The Swappable Brain". The calendar events are illustrative, and the sim labels them "illustrative".

**Rules:** A placement is correct when it equals the Correct level for that ability. The score is the number of correct placements, from 0 to 8. The request and reply fields are identical for all three levels. Only the reply text differs.

**Learner Activity:**

1. The learner reads ability 1 and chooses Level 1, 2, or 3.
2. The sim shows whether it was correct and the Why text, then the learner continues through ability 8.
3. After ability 8, the sim shows the score.
4. The learner chooses a level and reads its reply to the sample question, and does the same for the other two levels.
5. The learner should notice that the request and reply fields never change between levels.

**Feedback:** Eight abilities, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. This first appears at <correct level>: <Why>". The correct level is revealed immediately after each answer, and a running score "n of 8" is shown.

**Starting State:** Ability 1 is shown with the three levels, and the question "At which level does this ability first appear?"

**Chapter Anchors:** There are three levels. Level 1 is about 100 lines and uses no LLM. Level 2 adds speech-to-text, text-to-speech, and one LLM call. Level 3 is an optional open-source agent framework. The terminal and the request-reply contract do not change between levels.
</details>

## Putting It All Together

You now have the full picture. A personal agent is software that works for you in several steps and comes back for decisions. It can live in a vendor's cloud, on a computer you control, or on a school server. Your Open Study Buddy is a thin agent terminal, built from open hardware, that sends requests to a buddy server over a request-reply contract. The decision logic behind the server is a swappable brain that can grow from simple rules to an LLM to a full framework.

Key takeaways:

- A chatbot replies, and an agent acts for you, uses tools, and asks before it changes something.
- Cloud, self-hosted, and school-hosted agents differ mainly in who runs the computer and who decides what data it touches.
- Open hardware and open source software let you study, repair, and change the whole system.
- The Open Study Buddy device is an agent terminal with a Pico, a round display, a microphone, an amplifier with a speaker, and three buttons.
- The buddy server receives requests, decides on a reply, and returns it, and one server can serve many terminals.
- One spoken question travels through eight steps: one is yours, two happen on the terminal, three on the server, and two on the network.
- Because of the request-reply contract, the brain can be swapped from rules to an LLM to a framework without changing the terminal.

Test yourself with these two questions, and click each one to reveal its answer.

??? question "A student asks a question worded in a way that no written rule anticipated. Which agent progression level first handles it? Click to expand"
    Level 2. An LLM-backed agent can interpret free-form wording, while a Level 1 rule-based server only handles questions that match its rules.

??? question "Which steps of the data flow does the terminal perform, and why does the server do the rest of the work? Click to expand"
    The terminal captures the sound (step 2) and later shows and plays the reply (step 8). The server does speech-to-text, the brain's decision, and text-to-speech (steps 4 to 6) because those jobs need far more memory than the Pico has, and the Wi-Fi link only carries the request and the reply (steps 3 and 7).

!!! mascot-celebration "Vocabulary Unlocked"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You just learned the vocabulary of a personal agent and traced one question from your voice to an answer on the display. From here on, when you read terminal, server, or brain, you will know exactly which job each one does.

In Chapter 2 we refresh the MicroPython skills you will use to program the terminal.
