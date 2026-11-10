---
title: Teacher's Guide
description: Teacher's Guide for Open Study Buddy - how to teach with the chapters, kit labs, MicroSims, glossary, FAQ and learning graph, how to handle a listening device in a classroom, how to customize the book, and a Purchasing Guide for every kit part.
---

# Teacher's Guide

This guide is for teachers, club leaders and mentors who run *Open Study Buddy* with a group of
students. It explains every part of the book, how to use it in class, how to run a classroom
that builds a device with a microphone in it, and how to make your own copy. The
[Purchasing Guide](#purchasing-guide) at the end lists every part to order. No technical
background is assumed: each technical term is defined the first time it appears.

## About This Textbook

### What Is an Intelligent Textbook?

An **intelligent textbook** is a digital textbook that goes beyond text and pictures. It adds
interactive simulations, a searchable glossary, answers to common questions, and a map of how
the concepts depend on each other.

### The Five Levels of Intelligent Textbooks

Intelligent textbooks are grouped into five levels by how interactive and adaptive they are:

<iframe src="https://dmccreary.github.io/intelligent-textbooks/sims/book-levels/main.html" height="500px" width="100%" scrolling="no"
  style="overflow: hidden;"></iframe>

| Level | Name | Description | Example features |
|-------|------|-------------|------------------|
| **Level 1** | Static Digital | A PDF or basic web version of a print textbook | Text and images only |
| **Level 2** | Interactive | Adds simulations, self-checks and a searchable glossary | MicroSims, self-check questions, search |
| **Level 3** | Adaptive | Adjusts content to each student's performance | Personalized learning paths |
| **Level 4** | AI-Assisted | Adds an AI tutor that answers student questions | Chatbot, automated feedback |
| **Level 5** | Fully Adaptive AI | Learns from student interactions and adapts continuously | Real-time content generation |

**This book is a Level 2 intelligent textbook.** The device students build is a personal AI
agent, but the book itself does not track students or adapt to them.

### What Makes This Book Different

- **Students build a real device.** Over 18 chapters, students write every line of MicroPython
  for a desk companion that listens, shows what it heard on a round display, speaks answers
  aloud, and announces tests and due dates from the school calendar.
- **It is open from end to end.** The school, not a vendor, decides where the agent behind the
  device runs and which data it may touch. There is no subscription.
- **It teaches responsible listening.** A device with a microphone in a classroom raises real
  privacy questions, and the book treats them as part of the engineering (Chapter 17).
- **45 MicroSims** let students explore ideas such as sample rate, FFT bins and frame budgets
  in the browser, with no software to install.
- **A learning graph** maps how all 326 concepts in the book build on each other.
- **Sage the Owl**, a friendly guide character, appears in every chapter with tips, warnings
  and encouragement.
- **It is free.** The book is licensed under Creative Commons for non-commercial use.

## Before You Start

### Who the Book Is For

The main audience is high school students in grades 9–12. Motivated middle school students,
college undergraduates, coding clubs and hobbyists can also use it.

Students should already have finished the
[Learning MicroPython](https://dmccreary.github.io/learning-micropython/) course or have the
same experience. That means they can put MicroPython on a Raspberry Pi Pico, use Thonny, write
loops and functions, read a button and drive a display. Chapter 2 is a refresher, not a first
introduction. No signal-processing, networking or AI experience is needed.

### What You Need

| Item | When it is first needed | Notes |
|------|------------------------|-------|
| One Study Buddy base kit per student or pair | Chapter 4 | See the [Purchasing Guide](#purchasing-guide) |
| A computer per student or pair with Thonny installed | Chapter 2 | Windows, Mac, Linux or a Raspberry Pi all work |
| A Micro-USB **data** cable per kit | Chapter 2 | Charge-only cables look the same but cannot program the Pico |
| A Wi-Fi network the Pico can join | Chapter 13 | See the network note below |
| A Raspberry Pi or computer to run the class server | Chapters 15–16 | Runs the MQTT broker and the buddy server |
| Soldering iron, wire strippers, small screwdriver | Before Chapter 4 | Only if your microphone and amplifier boards come without headers soldered on |

!!! note "Check your school network early"
    The Pico 2 W joins ordinary password-protected Wi-Fi networks. Many school networks need a
    sign-in page or a separate login for each user, and a Pico cannot get past either. Before
    Chapter 13, ask your technology staff for a network the devices can join, or run a small
    classroom router that is not connected to the internet.

## Using the Chapters

### Chapter Sequence

The book has [18 chapters](../../chapters/index.md). Each chapter adds one idea and ends with a
working device feature, so students should work through them in order.

| Chapters | Topic area |
|----------|------------|
| 1–2 | Foundations: personal agents, the Study Buddy architecture, a MicroPython refresher |
| 3–4 | Sound basics and the kit hardware: sampling, wiring all five parts, power and ground |
| 5–7 | Display and buttons: pixels and color, redrawing only what changed, debouncing, device modes |
| 8–12 | Audio and signal processing: I2S recording and playback, the FFT, fast MicroPython, push-to-talk, wake words |
| 13–16 | Networking: Wi-Fi and HTTP, streaming and security, MQTT alerts, the school agent and calendar |
| 17–18 | Responsibility and integration: privacy and consent, testing, capstone projects |

### What Each Chapter Contains

1. **Summary**: what the chapter covers and what students will build.
2. **Concepts Covered**: the concepts from the learning graph that the chapter teaches.
3. **Prerequisites**: the earlier chapters it builds on.
4. **A welcome from Sage**: the chapter's goal in a sentence or two.
5. **Main content**: explanations, tables, code, and embedded MicroSims.
6. **A recap**, usually titled "Putting It All Together", with a list of key takeaways.
7. **Self-check questions**: two or more questions whose answers appear when clicked.
8. **A celebration from Sage**, then a one-line preview of the next chapter.

Below each MicroSim is a collapsed **specification** block. It lists the MicroSim's Bloom's
Taxonomy level, learning objective, common misconceptions, and how a student shows mastery.
These blocks are useful for lesson planning. Students can skip them.

### Suggested Classroom Use

- **Before class**: assign the reading. Ask students to try each MicroSim as they reach it.
- **During class**: put a MicroSim on the projector. Ask students to predict what a control will
  do before you change it, then test the prediction. Then move to the kits for the hands-on
  work.
- **After class**: use the self-check questions at the end of the chapter as an exit ticket or
  a review.
- **Pacing**: the chapters run from about 4,700 to 11,300 words, and most mix reading with
  hands-on work. As a planning estimate, allow about one week per chapter, which fits the
  book into one semester. Chapters 9, 10, 16 and 18 are the longest and may need more time.

## Using the Kit Labs

The [Study Buddy Base Kit](../../kits/study-buddy-base/index.md) section holds 19 short labs that
run on the kit. They work alongside the chapters.

- **Part 1, labs 01–07 ("Does It Work?")** has one test per part. Students wire one part, run
  its test, and only then add the next part. This finds wiring mistakes while there is only one
  place to look.
- **Part 2, labs 08–19 ("How Does It Work?")** teaches one idea per lab, from how the display
  mixes color to a memory game that uses the whole kit. Each lab says what a pass looks like
  and ends with "Try This" changes.

The table below suggests where each lab fits. It is a suggestion based on each lab's topic,
not a requirement.

| Labs | Topic | Fits with |
|------|-------|-----------|
| 01–07 | Wiring and testing each part | Chapter 4 |
| 08–10 | Color, angles to pixels, flicker-free text | Chapters 5–6 |
| 11–13 | Button bounce, one loop doing many jobs, state machines | Chapter 7 |
| 14–15 | How samples make sound, envelopes | Chapters 3 and 8 |
| 16–17 | Microphone oscilloscope, whistle tuner | Chapters 8–11 |
| 18 | Wi-Fi, IP, time, HTTP and JSON | Chapter 13 |
| 19 | Pattern memory game | Any time after Chapter 7 |

### Tips for Running the Labs

- **Work in pairs.** One student wires while the other checks each wire against the pin table,
  then they swap.
- **Keep the pin table on paper.** Most problems are a wire in the wrong row of the
  breadboard. The [Kit Wiring Fault Finder](../../sims/kit-wiring-fault-finder/index.md)
  MicroSim practises tracing these faults.
- **Run lab 02, the hardware probe, whenever something stops working.** It checks the parts it
  can see and reports wiring that breaks the rules.
- **Plan for sound.** Labs 05 and 07 and several later labs play sound. Run the quiet labs
  first, or provide earbuds or set a low volume if many kits share one room.

## Using the MicroSims

### What Is a MicroSim?

A **MicroSim** (short for micro-simulation) is a small interactive simulation that runs in a
web browser. Students change a value with a slider, button or menu and see the result at once.
MicroSims work on any device with a current browser, with nothing to install.

### MicroSims in This Book

The book has 45 MicroSims. Chapters embed them in **iframes**, which show one web page inside
another, so they load with the chapter. The full list is on the
[MicroSims page](../../sims/index.md).

| Technology | What it is good for | Examples |
|------------|--------------------|----------|
| **p5.js** (41 MicroSims) | Animations and controls students can change | [Sampling Explorer](../../sims/sampling-explorer/index.md), [FFT Bin Calculator](../../sims/fft-bin-calculator/index.md), [RGB565 Color Mixer](../../sims/rgb565-color-mixer/index.md) |
| **vis-network** (3 MicroSims) | Diagrams of connected parts | [Study Buddy Architecture Explorer](../../sims/study-buddy-architecture-explorer/index.md), [Kit Import Map](../../sims/kit-import-map/index.md), [Learning Graph Viewer](../../sims/graph-viewer/index.md) |

### The Colored Dots in the Navigation

Each MicroSim has a colored dot beside its name in the left navigation:

| Dot | Status | Meaning |
|-----|--------|---------|
| Red | Scaffold | The design is written but the MicroSim is not built yet |
| Orange | Built | The MicroSim works but the author has not reviewed it yet |
| Green | Approved | The author has tested it and approved it for students |

Most MicroSims are orange right now. Try an orange MicroSim yourself before you rely on it in a
lesson, and report anything that looks wrong (see [Feedback](#feedback)).

### Tips for Using MicroSims in Class

1. **Project them.** Ask the class to predict what will happen before you move a control.
2. **Then let students explore.** Give them 5–10 minutes on their own devices.
3. **Connect back to the text.** Each MicroSim sits next to the idea it shows. After using it,
   have students reread the paragraph above it.
4. **Plan for the internet.** MicroSims need a connection unless you run a local copy of the
   book (see [Customizing Your Own Copy](#customizing-your-own-copy)).

!!! tip "Put a MicroSim on any web page"
    You can show any MicroSim on a page you control, such as a Google Site, Canvas, Schoology or
    a plain HTML file, by pasting this HTML:

    ```html
    <iframe src="https://dmccreary.github.io/open-study-buddy/sims/kit-wiring-fault-finder/main.html"
        width="100%" height="622px" scrolling="no"></iframe>
    ```

    Replace `kit-wiring-fault-finder` with the name of any MicroSim from the
    [MicroSims page](../../sims/index.md). Each MicroSim's own page shows the right height.

## Using the Glossary

The [glossary](../../glossary.md) defines all 326 concepts in the book in alphabetical order.
Each definition is short, precise, and does not use the term to define itself.

- **Find a term** with Ctrl+F (Cmd+F on a Mac) on the glossary page, or with the search bar
  at the top of any page.
- **Preview vocabulary** by having students look up a chapter's concepts before reading it.
- **Ask students to write their own definitions** after a chapter, then compare them with the
  glossary.

## Using the FAQ

The [FAQ](../../faq.md) (Frequently Asked Questions) answers 90 questions students are likely to
ask. The questions are grouped into six categories: Getting Started, Core Concepts, Technical
Details, Common Challenges, Best Practices, and Advanced Topics. Each answer links to the chapter
that covers the idea.

- **Start a discussion** with two or three FAQ questions before you show the answers.
- **Send students to the Common Challenges questions** when they are stuck outside class.
- **Use it to review** before an assessment.

## Assessment

The book does not have separate quiz pages yet. It offers three kinds of assessment:

- **Self-check questions** at the end of every chapter. Students click a question to reveal
  its answer. They work as exit tickets or warm-ups.
- **Lab pass conditions.** Every kit lab says what a pass looks like, so a pass is a quick
  hands-on check you can sign off.
- **Capstone projects** in Chapter 18. Chapter 18 gives four starter projects and a 20-point
  rubric with six criteria: function, calibration, reliability, privacy, user testing, and code
  and notes. It also gives a user-testing method in which students watch three or more
  classmates use their device.

The MicroSim specification blocks give each MicroSim's **Bloom's Taxonomy** level. Bloom's
Taxonomy sorts thinking skills from simplest to most complex: Remember, Understand, Apply,
Analyze, Evaluate and Create. Use these levels to choose activities that match your goals.

## A Listening Device in Your Classroom

The Study Buddy has a microphone, so plan how you will handle privacy before the microphone
chapters. Chapter 17 teaches students to do this, and the same ideas apply to you.

- **Push-to-talk is the default.** The device listens only while a student holds a button.
- **Always-on listening needs approval.** The wake-word mode ("Hey Pico") listens all the
  time. The book treats it as an advanced option that should stay off until a parent or
  guardian, the student and the school have each agreed in writing. Chapter 17 explains who
  approves what and what records to keep.
- **Do not store audio.** The capstone rubric gives points for a device that keeps no
  recordings, and for one that tells people what it hears and keeps.
- **Use the synthetic schools for demos.** The [Schools](../../schools/index.md) section
  includes Cedar Ridge High School, an invented school with its own mascot and calendar. Demos
  can use it and never need real student or school data.
- **Talk to your school first.** Ask your school's technology or privacy staff before any
  device sends audio off the device, even on the school network.

This guide explains ideas, not the law. Your school's own policies and staff decide what is
allowed.

## Customizing the Buddy for Your School

Chapter 16 sets up the agent for one school: the school name, its mascot on the round display,
its voice, a custom wake phrase, and a calendar with `TEST:` and `DUE:` titles that become
spoken reminders. The [Schools](../../schools/index.md) section shows finished examples and
holds pages for real organizations that are piloting the kit. To add your school, contact the
author through the [contact page](../../contact.md).

## The Learning Graph

A **learning graph** is a map of how the book's concepts depend on each other. It is a
**directed acyclic graph** (DAG): each arrow points from a concept to one that builds on it,
and no chain of arrows loops back to where it started. This book's graph has 326 concepts.

- **Check prerequisites**: before you teach a concept, see which concepts it needs.
- **Find gaps**: when a student is stuck, trace back to the earlier concepts they need.
- **Compare with your syllabus**: see which concepts your course already covers.
- **Extend**: let advanced students follow the graph ahead of the class.

Open the [Learning Graph Viewer](../../sims/graph-viewer/index.md) to explore it.

## Sage the Owl: The Book's Guide Character

A **pedagogical agent** is a character who guides students through a textbook. Research has
found that such characters can raise students' interest and how much they feel they learned;
this is called the **persona effect**. This book's character is **Sage the Owl**, whose
catchphrase is "Let's listen closely!"

Sage appears in colored callout boxes called **admonitions**:

| Type | Purpose | How often |
|------|---------|-----------|
| Welcome | Introduces the chapter's goal | Once, at the start of each chapter |
| Thinking | Points out a key idea | A few times per chapter |
| Tip | Gives practical advice | Where the material calls for it |
| Warning | Warns about a common mistake | Where the material calls for it |
| Encourage | Supports students on a hard idea | Where students may struggle |
| Celebration | Marks what the chapter achieved | Once, at the end of each chapter |

Sage appears a handful of times in each chapter, never twice in a row.

- **Read Sage's boxes aloud.** They are written to be spoken.
- **Use the Thinking boxes as discussion prompts.** They mark the ideas that matter most.
- **Point frustrated students to the Encourage boxes.** They are placed where the material gets
  hard.

## Feedback

The book is developed in the open on **GitHub**, a website where people build software and
documents together. You do not need to program to report a problem.

A **GitHub issue** is like a support ticket: a numbered report that the author and others can
discuss. To open one:

1. Go to the book's [GitHub repository](https://github.com/dmccreary/open-study-buddy).
2. Click the **Issues** tab, then **New issue**.
3. Give it a clear title, such as "Lab 06 meter does not move" or "Broken link in Chapter 13".
4. Say which page or lab, what you expected, what happened, and your browser or kit if it matters.
5. Click **Submit new issue**.

Opening an issue needs a free GitHub account. If you would rather not make one, use the
[contact page](../../contact.md). Reports of typos, broken links, MicroSims that misbehave,
labs that fail on real hardware, and pages that are hard to read for students with
disabilities are all welcome.

## Understanding the License

A **license** says what others may do with a piece of work. A **Creative Commons (CC)
license** is a standard, plain-language license for creative and educational work. This book
uses **CC BY-NC-SA 4.0**:

| Code | Name | Meaning |
|------|------|---------|
| **BY** | Attribution | Give credit to the author, Dan McCreary |
| **NC** | Non-Commercial | Do not use it to make money |
| **SA** | Share-Alike | Share any changed version under the same license |
| **4.0** | Version | The current version of the license |

**You can:**

- copy the book or any chapter for your students
- share the link with teachers, students and parents
- print chapters for class
- change it: add examples, remove sections, reorder chapters
- translate it
- build your own version from it

**You cannot:**

- sell it or charge students for access
- remove the credit to the author
- share a changed version under a different license
- present it as your own work

The full legal text is on the [License](../../license.md) page.

## Customizing Your Own Copy

You can make your own version of the book, with your own examples, colors and school.

### Key Terms

- **Repository (repo)**: the folder on GitHub that holds all of a project's files.
- **Git**: a tool that records every change to the files, when and by whom.
- **Fork**: your own copy of a repository, kept in your GitHub account.
- **Clone**: a copy of a repository downloaded to your computer.
- **Markdown**: a simple text format. `**bold**` makes **bold**, `# Heading` makes a heading,
  and a line starting with `-` makes a bullet point.
- **MkDocs**: the program that turns the book's Markdown files into a website.
- **mkdocs.yml**: the settings file for the website: title, menu, colors and features.

### Step 1: Copy the Book

Make a free account at [github.com](https://github.com) if you do not have one. Then either:

- **Fork it** (easiest): open the [repository](https://github.com/dmccreary/open-study-buddy)
  and click **Fork** at the top right, or
- **Clone it** (to work on your computer): install [Git](https://git-scm.com/), open a
  terminal, and run:

```bash
git clone https://github.com/dmccreary/open-study-buddy.git
```

The kit's MicroPython code is in the `src/kits/study-buddy-base` folder. The book's pages are
Markdown files in the `docs` folder, and you can edit them in any text editor.

### Step 2: Change the Title, Colors and Logo

Open `mkdocs.yml`. The title and author are near the top:

```yaml
site_name: 'Open Study Buddy'
site_description: 'An interactive intelligent textbook to support the low-cost Open Study Buddy personal agent hardware for students.'
site_author: 'Dan McCreary'
```

The colors are in the `palette` section. This book uses amber and orange:

```yaml
    primary: 'amber'    # try blue, red, purple, teal, green, indigo...
    accent: 'orange'
```

The logo in the top-left corner is `docs/img/mascot/neutral.png`, set by the `logo:` line in
`mkdocs.yml`. Point that line at your own image to change it.

### Step 3: Preview Your Changes

1. Install Python 3.8 or newer from [python.org](https://www.python.org/).
2. Install MkDocs with the Material theme:

    ```bash
    pip install mkdocs-material
    ```

3. In a terminal, go to the project folder and start the preview:

    ```bash
    cd open-study-buddy
    mkdocs serve
    ```

4. Open `http://127.0.0.1:8000/open-study-buddy/` in your browser. The page reloads each time
   you save a file.

### Step 4: Publish Your Version

To publish your copy as a free website with GitHub Pages, run:

```bash
mkdocs gh-deploy
```

Your book appears at `https://YOUR-USERNAME.github.io/open-study-buddy/` within a few minutes.

## Analytics and Student Data

**Web analytics** measures how visitors use a site: which pages they read, for how long, and on
what devices. It can show which chapters students skip or spend the longest on.

### Adding Google Analytics to Your Copy

This book does not have Google Analytics turned on. To add it to your own copy:

1. Sign in at [analytics.google.com](https://analytics.google.com/) and create a **property**,
   Google's name for a site it tracks.
2. Google gives you a **Measurement ID** that looks like `G-XXXXXXXXXX`.
3. In `mkdocs.yml`, find the `analytics` lines near the end, remove the `#` at the start of
   each, and put in your ID:

    ```yaml
    extra:
      analytics:
        provider: google
        property: G-YOUR-MEASUREMENT-ID
    ```

4. Publish again. Data starts appearing within a day or two.

Google Analytics reports totals, such as page views and devices. It does not report what each
named student did.

### Tracking Individual Students (Advanced)

**xAPI** (the Experience API) is a standard for recording detailed learning events, such as
"this student moved this slider" or "this student passed lab 06". The records are kept in an
**LRS** (Learning Record Store), a database built for learning records.

Before you collect data about individual students, check these laws:

- **FERPA** (Family Educational Rights and Privacy Act): the U.S. law that protects student
  education records.
- **COPPA** (Children's Online Privacy Protection Act): the U.S. law with extra rules for
  children under 13.
- **State laws**: many U.S. states have their own student-privacy laws.
- **GDPR** (General Data Protection Regulation): the European Union law that applies to students
  in the EU.

Anonymous totals are the safest choice. If you want to track individual students, talk to your
school or district's data privacy officer first.

## Purchasing Guide

![The Study Buddy's 2.1-inch round GC9B72 display showing a clock and a two-day weather forecast, held on an acrylic stand](./round-display-gc9b72.jpg){ width="450" }

The whole book runs on one kit, the **Study Buddy base kit**: a Raspberry Pi Pico 2 WH, a
2.1-inch 360×360 round color display (GC9B72), an INMP441 I²S microphone, a MAX98357A I²S
amplifier with a small speaker, three push buttons, a breadboard and wiring. One kit costs about
**$28** at single-unit prices and about **$21 per student** for a class of 20. Every part except
the Pico ships from China in **8–12 days (median 9)** in our 2026 AliExpress orders, so order at
least three weeks before the hardware chapters start, and four to five weeks ahead for a full
classroom set.

!!! note "Prices checked October 2026"
    Component prices move, and marketplace listings turn over constantly. Treat every figure
    here as a planning estimate, not a quote. Each part shows the **low and high AliExpress
    prices** we found in web searches on October 20, 2026, with eBay and Amazon prices for
    comparison. Figures marked *estimate* could not be confirmed from a current listing, and each
    one says why.

!!! warning "Don't order the wrong one: a 360×360 SPI display with the GC9B72 controller"
    The kit's driver (`lib/gc9b72.py`) only works with the **2.1-inch, 360×360, 4-wire SPI**
    round display built on the **GC9B72** controller. Marketplaces list 2.1-inch round **480×480**
    panels (ST7701, RGB or MIPI interface) and 1.28-inch **GC9A01** round displays right beside
    it, with nearly identical photos. Neither will work. Look for "GC9B72" and "360x360" in the
    listing title.

### Summary of Parts List

**Required**

- [Raspberry Pi Pico 2 WH](#raspberry-pi-pico-2-wh) — runs MicroPython and connects to Wi-Fi — Study Buddy base kit (~$6.99)
- [2.1-inch Round Display (GC9B72, 360x360)](#21-inch-round-display-gc9b72-360x360) — the buddy's face — Study Buddy base kit (~$6.12)
- [INMP441 I2S Microphone](#inmp441-i2s-microphone) — the buddy's ear — Study Buddy base kit (~$3.00)
- [MAX98357A I2S Amplifier](#max98357a-i2s-amplifier) — drives the speaker from digital audio — Study Buddy base kit (~$1.53)
- [Speaker (3525, 8 ohm, 2 W)](#speaker-3525-8-ohm-2-w) — the buddy's voice — Study Buddy base kit (~$1.09)
- [Momentary Push Buttons (6x6 mm)](#momentary-push-buttons-6x6-mm) — Mode, Up and Down — Study Buddy base kit (~$0.15 for three)
- [Solderless Breadboard (830 Point)](#solderless-breadboard-830-point) — holds everything — Study Buddy base kit (~$2.00)
- [Male-to-Male Jumper Wires](#male-to-male-jumper-wires) — breadboard links — Study Buddy base kit (~$2.00)
- [Dupont Ribbon Cable (Male-to-Female, 20 cm)](#dupont-ribbon-cable-male-to-female-20-cm) — the display cable — Study Buddy base kit (~$2.95)
- [Micro-USB Data Cable](#micro-usb-data-cable) — power and the Thonny connection — Study Buddy base kit (~$2.50)

**Optional**

None. Every part above is used by the kit's tests, and the base kit has no battery, enclosure
or SD card yet.

**Price ranges and lead times at a glance:**

| Part | Qty | Price range | AliExpress lead time |
|------|-----|-------------|----------------------|
| Raspberry Pi Pico 2 WH | 1 | AliExpress $3.53–$31.09 (genuine "original" boards $20.75); eBay ~$15–$23; Amazon $13.99 (no headers)–$18.95 (WH); **Micro Center $6.99** | Not recommended from AliExpress. Micro Center: same-day pickup, or ships in 5–7 business days |
| 2.1-inch round display (GC9B72) | 1 | AliExpress $5.39–$6.12; eBay ~$8–$15 *(estimate)*; Amazon: no matching listing found | 8–12 days (median 9). Glass panel, so allow for a breakage spare |
| INMP441 microphone | 1 | AliExpress $0.99–$4.39; eBay ~$3–$8; Amazon $8.54–$9.99 per 3-pack ($2.85–$3.33 each) | 8–12 days (median 9) |
| MAX98357A amplifier | 1 | AliExpress $0.93–$1.53; eBay ~$2–$6 *(estimate)*; Amazon $6.88 per 2-pack to $11.99 per 6-pack ($2.00–$3.44 each) | 8–12 days (median 9) |
| Speaker, 3525 8 Ω 2 W | 1 | AliExpress $0.58–$2.80; eBay $1.47 + $3.50 shipping; Amazon $12.99 per 10-pack ($1.30 each) | 8–12 days (median 9). Small sealed speaker, no magnet or battery shipping rules |
| 6×6 mm push buttons | 3 | AliExpress ~$0.01–$0.03 each in 100-packs *(estimate)*; eBay ~$3–$6 per 100 *(estimate)*; Amazon $4.99 per 100 | 8–12 days (median 9) |
| 830-point breadboard | 1 | AliExpress $0.68–$2.61; eBay ~$2–$7 *(estimate)*; Amazon $19.99 per 10-pack ($2.00 each) | 8–12 days (median 9). Bulky for its weight: ten boards ship as a larger parcel |
| Male-to-male jumper set | 1 set | AliExpress/eBay/Amazon 65-piece sets $1.99–$5.50 | 8–12 days (median 9) |
| Dupont ribbon, 40-wire M-F 20 cm | 8 wires | AliExpress from ~$0.99; eBay ~$2–$4 *(estimate)*; PiShop US $2.95 | 8–12 days (median 9) |
| Micro-USB data cable | 1 | AliExpress ~$0.80–$2.00 *(estimate)*; eBay ~$2–$4 *(estimate)*; Amazon $7.49–$9.44 per 3-pack ($2.50–$3.15 each) | 8–12 days (median 9), or buy on Amazon |

**Estimated total per kit:**

| Kit | One kit | Per student, class of 20 |
|-----|---------|--------------------------|
| Study Buddy base kit | ~$28.33 | ~$21.12 |

The one-kit figure uses each part's single-unit price. If you are building just one kit, the real
out-of-pocket cost is higher (about $40) because buttons, cables and breadboards come in packs.
The class figure rounds each order up to the pack, and the Pico 2 WH stays at its fixed $6.99
retail price at any quantity.

### Raspberry Pi Pico 2 WH

<!-- TODO: replace with a Pico 2 W photo — see pico-2-w-image-description.md -->
![Raspberry Pi Pico W, which looks nearly identical to the Pico 2 W](./raspberry-pi-pico-w.jpg){ width="300" }

*Shown: the original Pico W, which looks nearly identical to the Pico 2 W. Photo by [SparkFun Electronics](https://commons.wikimedia.org/wiki/File:RPI_PICO_W_1.jpg), [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/).*

**Used in:** Study Buddy base kit (×1)

**Used for:** [Chapter 4: The Pico Kit Hardware and Wiring](../../chapters/04-pico-kit-hardware/index.md)
and every chapter after it, including Wi-Fi in
[Chapter 13: Wi-Fi, HTTP, and Connecting to the Agent](../../chapters/13-wifi-http-agent-link/index.md).
It runs the student's MicroPython and talks to every other part.

The Pico 2 W is Raspberry Pi's RP2350 microcontroller board with 2.4 GHz Wi-Fi and Bluetooth.
Buy the **WH** version, which has its header pins already soldered so it drops straight into the
breadboard. The plain "Pico 2 W" has bare pads.

**Requirements:** It must be a **Pico 2 W (RP2350)**. The older Pico W (RP2040) and the plain
Pico 2 (no Wi-Fi) look almost the same in listing photos. The book's audio, FFT and Wi-Fi
chapters assume the RP2350's 520 KB of RAM and the wireless chip. The radio is 2.4 GHz only, so
confirm with your school's IT team that a 2.4 GHz network is available.

**Prep work:** None for the WH. A plain Pico 2 W needs its headers soldered on (about 15
minutes).

**Cost:** ~$6.99 each in quantity 1 (Micro Center "Pico 2W with Header", SC1634) · ~$6.99 each in
a classroom order of 20+ · ~$6.99 at district scale (*estimate*: we assume the fixed retail price
holds). **Price range:** AliExpress $3.53–$31.09 (the low end is a promotional listing of
uncertain origin; listings titled "100% New Original" were $20.75); eBay about US$15–$23 (eBay
Australia listings at AU$23.75–AU$34.98; we could not load US eBay results); Amazon $13.99 for
the Pico 2 W without headers and $18.95 for a pre-soldered version.

**AliExpress lead time:** Not recommended. Marketplace Picos cost two to four times the Micro
Center price and are the boards most likely to be relabeled. Micro Center stores have it the same
day, and its online store lists "usually ships in 5–7 business days".

**Trusted sellers:** Micro Center, Adafruit, SparkFun, Digi-Key and PiShop.us. Genuine boards say
"Pico 2 W" on the silkscreen and carry an RP2350 chip.

**Search keywords:** `Raspberry Pi Pico 2 WH`, `Pico 2 W with header`, `SC1634`

**Where to buy:**

- [Search eBay for "Raspberry Pi Pico 2 WH"](https://www.ebay.com/sch/i.html?_nkw=Raspberry+Pi+Pico+2+WH)
- [Search AliExpress for "Raspberry Pi Pico 2 WH"](https://www.aliexpress.com/w/wholesale-raspberry-pi-pico-2-wh.html)
- [Search Amazon for "Raspberry Pi Pico 2 WH"](https://www.amazon.com/s?k=Raspberry+Pi+Pico+2+WH)
- [Search Micro Center for "Raspberry Pi Pico 2 WH"](https://www.microcenter.com/search/search_results.aspx?Ntt=Raspberry+Pi+Pico+2+WH)

---

### 2.1-inch Round Display (GC9B72, 360x360)

![The 2.1-inch round GC9B72 display showing a large clock and weather icons, with its 10-pin header at the bottom](./round-display-gc9b72.jpg){ width="400" }

**Used in:** Study Buddy base kit (×1)

**Used for:** [Chapter 5: Display Basics: Pixels, Color, and Frame Size](../../chapters/05-display-basics/index.md) and
[Chapter 6: Drawing Directly to Display Regions](../../chapters/06-display-regions-and-drawing/index.md),
then the face, text and level meter in every later chapter.

A 2.1-inch round IPS color screen with 360×360 pixels and a GC9B72 controller, driven over 4-wire
SPI at 3.3 V. The module has a 10-pin header (GND, VCC, SCL, SDA, RST, DC, CS, BL, SDO, TE). The
kit uses the first eight. GalaxyCore has never published a GC9B72 datasheet, so the book's
driver was ported from the one known-good public init sequence. That makes the exact controller
matter more than usual.

**Requirements:** It must say **GC9B72**, **360x360** and **SPI**. The 480×480 2.1-inch round
panels need an RGB or MIPI interface that the Pico does not have.

**Prep work:** None. The header comes soldered. Peel off an 8-wire strip of the ribbon cable for
it (see below).

**Cost:** ~$6.12 in quantity 1 (the AliExpress listing we bought from, US$6.12) · ~$5.39 each in a
classroom order of 20+ (the lowest current AliExpress search price) · no district tier found.
**Price range:** AliExpress $5.39–$6.12 (TZT's own store lists it at $3.45); eBay ~$8–$15
(*estimate*: we could not load current US eBay results); Amazon: no matching 360×360 GC9B72
listing found, only the 480×480 panels that will not work. A European marketplace lists it at
€14.64 plus shipping.

**AliExpress lead time:** 8–12 days (median 9), the same as our other AliExpress packages. The
glass panel ships in a bigger padded box, and a cracked screen means reordering and another 9
days, so buy one or two spares.

**Spotting a bad batch:** A blank screen with the backlight on usually means a wiring mistake, so
run test 04 first. A panel with a dead line or a dark sector after a correct test is a defect.
Set it aside and use a spare.

**Search keywords:** `GC9B72 2.1 inch round display 360x360`, `2.1 inch round TFT SPI GC9B72`

**Where to buy:**

- [Search eBay for "GC9B72 2.1 inch round display 360x360"](https://www.ebay.com/sch/i.html?_nkw=GC9B72+2.1+inch+round+display+360x360)
- [Search AliExpress for "GC9B72 2.1 inch round display 360x360"](https://www.aliexpress.com/w/wholesale-gc9b72-2-1-inch-round-display-360x360.html)
- [Search Amazon for "GC9B72 2.1 inch round display 360x360"](https://www.amazon.com/s?k=GC9B72+2.1+inch+round+display+360x360)

---

### INMP441 I2S Microphone

![INMP441 microphone breakout board, round, with a loose six-pin yellow header beside it](./inmp441-microphone.png){ width="350" }

**Used in:** Study Buddy base kit (×1)

**Used for:** [Chapter 8: I2S Audio: Recording and Playing Sound](../../chapters/08-i2s-audio/index.md),
[Chapter 11: Microphone Calibration and Push-to-Talk](../../chapters/11-mic-calibration-push-to-talk/index.md)
and [Chapter 12: Wake-Word Detection](../../chapters/12-wake-word-detection/index.md). It turns the
student's voice into 24-bit samples.

A digital MEMS microphone with its own ADC, sending samples straight to the Pico over I²S. Buy
the **INMP441** by name. The "INMP441-compatible" MS3625 and MS4030 boards are cheaper, but the
kit's calibration numbers were measured on the INMP441. It is a 3.3 V part: VDD goes to 3V3, never
to VBUS.

**Prep work:** Some minor soldering required. Most listings ship with the six-pin header
**loose**, as in the photo, and soldering it takes about 5 minutes per board. Listings sold as
"solderless" have the header fitted and are worth the extra few cents for a no-solder kit. Tie
the L/R pin to GND.

**Cost:** ~$3.00 in quantity 1 (AliExpress singles at $2.19–$4.39) · ~$1.00 each in a classroom
order of 20+ (AliExpress listings around $0.99) · ~$0.89 each at district scale (an Alibaba tiered
listing at $0.89 for 10–999 pieces). **Price range:** AliExpress $0.99–$4.39 (coin-deal listings
as low as $0.33 are for new shoppers only); eBay ~$3–$8 (UK listings at £5.82–£5.99, Germany
€2.28 plus €1.60 shipping); Amazon $8.54–$9.99 per 3-pack.

**AliExpress lead time:** 8–12 days (median 9).

**Spotting a bad batch:** A dead or badly soldered microphone reads as all zeros, which looks
exactly like the swapped-wire fault in the kit README. Check the wiring, then the solder joints,
then swap in a spare.

**Search keywords:** `INMP441 I2S microphone module`, `INMP441 MEMS omnidirectional`,
`INMP441 solderless`

**Where to buy:**

- [Search eBay for "INMP441 I2S microphone module"](https://www.ebay.com/sch/i.html?_nkw=INMP441+I2S+microphone+module)
- [Search AliExpress for "INMP441 I2S microphone module"](https://www.aliexpress.com/w/wholesale-inmp441-i2s-microphone-module.html)
- [Search Amazon for "INMP441 I2S microphone module"](https://www.amazon.com/s?k=INMP441+I2S+microphone+module)
- [Search Alibaba for "INMP441 I2S microphone module"](https://www.alibaba.com/trade/search?SearchText=INMP441+I2S+microphone+module)

---

### MAX98357A I2S Amplifier

![MAX98357A I2S amplifier breakout, top side](./amp-max98357a-top.jpg){ width="300" }
![MAX98357A I2S amplifier breakout, bottom side](./amp-max98357a-bottom.jpg){ width="300" }

**Used in:** Study Buddy base kit (×1)

**Used for:** [Chapter 7: Buttons, State Machines, and Device Modes](../../chapters/07-buttons-and-device-modes/index.md)
(the volume beep) and [Chapter 8: I2S Audio: Recording and Playing Sound](../../chapters/08-i2s-audio/index.md), then every
chapter where the buddy speaks. It turns I²S audio from the Pico into power for the speaker.

A digital-to-analog converter and a 3 W class-D amplifier on one small board, with seven pins
(LRC, BCLK, DIN, GAIN, SD, GND, VIN) and a two-screw output terminal. The kit drives its GAIN pin
from GP12 so software can pick 6, 9 or 12 dB. Buy the mono **MAX98357A** breakout, not the
analog PAM8403 boards or the larger stereo TDM boards that show up in the same searches.

**Prep work:** Some minor soldering required on most listings. The seven-pin header and the
screw terminal usually ship loose, which takes about 10 minutes per board. Some listings are sold
as "pre-soldered" for about the same price, and we recommend those for a no-solder kit.

**Cost:** ~$1.53 in quantity 1 · ~$0.99 each in a classroom order of 20+ (most AliExpress
listings) · no district tier found. **Price range:** AliExpress $0.93–$1.53 (pre-soldered
listings about $0.99); eBay ~$2–$6 (*estimate*: we could not load current US eBay results;
Adafruit's genuine breakout is $5.95); Amazon $6.88 for a 2-pack, $7.59 for 3, $8.54 for 4 and
$11.99 for 6 ($2.00–$3.44 each).

**AliExpress lead time:** 8–12 days (median 9).

**Spotting a bad batch:** No sound with test 05 is almost always the I²S pin rule (LRC must be
the pin right after BCLK) or a loose screw terminal. If test 02 reports no warnings and the
speaker is known good, swap the board.

**Search keywords:** `MAX98357A I2S amplifier module`, `MAX98357 I2S 3W class D pre-soldered`

**Where to buy:**

- [Search eBay for "MAX98357A I2S amplifier module"](https://www.ebay.com/sch/i.html?_nkw=MAX98357A+I2S+amplifier+module)
- [Search AliExpress for "MAX98357A I2S amplifier module"](https://www.aliexpress.com/w/wholesale-max98357a-i2s-amplifier-module.html)
- [Search Amazon for "MAX98357A I2S amplifier module"](https://www.amazon.com/s?k=MAX98357A+I2S+amplifier+module)

---

### Speaker (3525, 8 ohm, 2 W)

<!-- TODO: image needed — see speaker-3525-image-description.md -->
*Photo pending. See the [image brief](./speaker-3525-image-description.md).*

**Used in:** Study Buddy base kit (×1)

**Used for:** [Chapter 8: I2S Audio: Recording and Playing Sound](../../chapters/08-i2s-audio/index.md) and every chapter
where the buddy beeps, plays back a recording or speaks.

A small sealed "3525" cavity speaker, 35 × 25 mm, with a red and black lead ending in a 2-pin JST
PH 2.0 plug. The kit's speaker is the **8 Ω, 2 W** version: it was measured at 7.4 Ω DC
resistance. The same listings also sell a 4 Ω, 3 W version. Either works with the MAX98357A,
but the 8 Ω one is quieter and draws less current from the Pico's USB supply, so stay with it.

**Prep work:** About 2 minutes. Cut off the JST plug, strip 5 mm from each wire, and clamp the
wires in the amplifier's screw terminal (red to +).

**Cost:** ~$1.09 in quantity 1 · ~$0.58 each in a classroom order of 20+ (the lowest current
AliExpress search price) · no district tier found for this exact speaker. **Price range:**
AliExpress $0.58–$2.80 (the $2.80 listing is the one the prototype kit came from); eBay $1.47
plus $3.50 shipping (a UK listing); Amazon $12.99 for a 10-pack ($1.30 each).

**AliExpress lead time:** 8–12 days (median 9). The speaker is small and has no battery, so it
ships like any other small packet.

**Search keywords:** `3525 speaker 8 ohm 2W`, `3525 cavity speaker JST PH2.0`

**Where to buy:**

- [Search eBay for "3525 speaker 8 ohm 2W"](https://www.ebay.com/sch/i.html?_nkw=3525+speaker+8+ohm+2W)
- [Search AliExpress for "3525 speaker 8 ohm 2W"](https://www.aliexpress.com/w/wholesale-3525-speaker-8-ohm-2w.html)
- [Search Amazon for "3525 speaker 8 ohm 2W"](https://www.amazon.com/s?k=3525+speaker+8+ohm+2W)

---

### Momentary Push Buttons (6x6 mm)

![Momentary tactile push button with a round cap and four leads](./momentary-push-button.png){ width="250" }

**Used in:** Study Buddy base kit (×3: Mode, Up and Down)

**Used for:** [Chapter 7: Buttons, State Machines, and Device Modes](../../chapters/07-buttons-and-device-modes/index.md)
and push-to-talk in [Chapter 11](../../chapters/11-mic-calibration-push-to-talk/index.md).

Standard 6×6 mm, four-leg, through-hole tactile switches. Each one connects GP16, GP17 or GP18 to
GND and uses the Pico's internal pull-up, so no resistor is needed. Colored caps are optional but
help students tell Mode from Up and Down.

**Prep work:** None. They are breadboard-ready as shipped. Show students that the four legs are
two connected pairs, so a button wired with both wires on the same side reads "pressed" all the
time.

**Cost:** ~$0.15 for three in quantity 1 (a 100-pack is $4.99 on Amazon) · ~$0.05 each in a
classroom order of 20+ (one 100-pack covers 20 kits with 40 spares) · ~$0.04 each at district
scale (Alibaba switches at a 1,000-piece minimum order). **Price range:** AliExpress ~$0.01–$0.03
each in 100-packs (*estimate*: not re-checked this month); eBay ~$3–$6 per 100 (*estimate*);
Amazon $4.99 per 100.

**AliExpress lead time:** 8–12 days (median 9).

**Spotting a bad batch:** Legs bent too short to seat, or switches that never click. Discard the
odd bad one; the 100-pack has plenty of spares.

**Search keywords:** `6x6mm tactile push button 4 pin`, `tact switch 6x6x5 DIP`

**Where to buy:**

- [Search eBay for "6x6mm tactile push button 4 pin"](https://www.ebay.com/sch/i.html?_nkw=6x6mm+tactile+push+button+4+pin)
- [Search AliExpress for "6x6mm tactile push button 4 pin"](https://www.aliexpress.com/w/wholesale-6x6mm-tactile-push-button-4-pin.html)
- [Search Amazon for "6x6mm tactile push button 4 pin"](https://www.amazon.com/s?k=6x6mm+tactile+push+button+4+pin)
- [Search Alibaba for "6x6mm tactile push button 4 pin"](https://www.alibaba.com/trade/search?SearchText=6x6mm+tactile+push+button+4+pin)

---

### Solderless Breadboard (830 Point)

![Full-size 830-point solderless breadboard, transparent, with power rails along both edges](./breadboard-830.jpg){ width="450" }

*Photo: oomlout, [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0) via [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:BREB-02_(14335226011).jpg)*

**Used in:** Study Buddy base kit (×1)

**Used for:** [Chapter 4: The Pico Kit Hardware and Wiring](../../chapters/04-pico-kit-hardware/index.md)
and every wired test after it.

A full-size 830 tie-point breadboard ("MB-102"). Buy the full size: the Pico, microphone,
amplifier and three buttons do not fit on a 400-point half-size board, and the chapter's advice
to keep the microphone's wires away from the amplifier's needs the room.

**Prep work:** None. Optionally mark the 3V3 and GND rails with a permanent marker; the
microphone is damaged by 5 V.

**Cost:** ~$2.00 in quantity 1 (an Amazon 10-pack at $19.99) · ~$1.10 each in a classroom order
of 20+ · ~$0.40 each at district scale (Alibaba listings at $0.40 for 5–49 pieces, plus a flat
shipping charge). **Price range:** AliExpress $0.68–$2.61 (most around $0.99–$1.21); eBay ~$2–$7
(*estimate*; a single board is $6.94 from Circuit Specialists); Amazon $19.99 per 10-pack.

**AliExpress lead time:** 8–12 days (median 9). Breadboards are light but bulky, so a 20-board
order arrives as a larger parcel. Some sellers split it into several packages that arrive on
different days.

**Spotting a bad batch:** A rail or row clip that is not bent properly, so wires will not seat.
Test each board with a jumper on arrival and throw out the odd bad one.

**Search keywords:** `830 point solderless breadboard`, `MB-102 breadboard`

**Where to buy:**

- [Search eBay for "830 point solderless breadboard"](https://www.ebay.com/sch/i.html?_nkw=830+point+solderless+breadboard)
- [Search AliExpress for "830 point solderless breadboard"](https://www.aliexpress.com/w/wholesale-830-point-solderless-breadboard.html)
- [Search Amazon for "830 point solderless breadboard"](https://www.amazon.com/s?k=830+point+solderless+breadboard)
- [Search Alibaba for "830 point solderless breadboard"](https://www.alibaba.com/trade/search?SearchText=830+point+solderless+breadboard)

---

### Male-to-Male Jumper Wires

![A bundle of male-to-male breadboard jumper wires in assorted colors](./jumper-wires-male-to-male.png){ width="400" }

**Used in:** Study Buddy base kit (×1 set)

**Used for:** [Chapter 4](../../chapters/04-pico-kit-hardware/index.md): power and ground rails,
the buttons, and the microphone and amplifier wiring on the breadboard.

A mixed-length set of male-to-male jumpers. The kit needs about 20 wires, so a 65-piece set
leaves spares.

**Prep work:** None.

**Cost:** ~$2.00 per set in quantity 1 · ~$2.00 per set in a classroom order of 20+ · ~$1.00 per
set at district scale (*estimate*: no current bulk listing found). **Price range:** 65-piece sets
at $1.99–$5.50 across AliExpress, eBay and Amazon (October 2026 checks for our FFT kit; not
re-checked per site).

**AliExpress lead time:** 8–12 days (median 9).

**Spotting a bad batch:** Pin ends that wobble in their crimp cause intermittent faults that look
like code bugs. Throw out any jumper whose tip moves.

**Search keywords:** `breadboard jumper wires male to male`, `65 pcs jumper wire kit`

**Where to buy:**

- [Search eBay for "breadboard jumper wires male to male"](https://www.ebay.com/sch/i.html?_nkw=breadboard+jumper+wires+male+to+male)
- [Search AliExpress for "breadboard jumper wires male to male"](https://www.aliexpress.com/w/wholesale-breadboard-jumper-wires-male-to-male.html)
- [Search Amazon for "breadboard jumper wires male to male"](https://www.amazon.com/s?k=breadboard+jumper+wires+male+to+male)

---

### Dupont Ribbon Cable (Male-to-Female, 20 cm)

![A multicolored Dupont ribbon cable with male pins on one end and female sockets on the other](./dupont-ribbon-cable-m-f.png){ width="450" }

**Used in:** Study Buddy base kit (×8 wires, one-fifth of a 40-wire ribbon)

**Used for:** The display cable in [Chapter 5: Display Basics: Pixels, Color, and Frame Size](../../chapters/05-display-basics/index.md).

A 40-wire ribbon of Dupont jumpers with a female socket on one end and a male pin on the other.
Peel off an 8-wire strip for the display: the female ends push onto the display's header and the
male ends go into the breadboard. `config.py` records a color for each display wire (SCL orange,
SDA yellow, RST green, DC blue, CS purple, BL gray, VCC red), so peel the strip where those colors
line up. One ribbon makes cables for five kits.

**Prep work:** Peel the ribbon into 8-wire strips, about 1 minute per kit. Keep the strip intact:
it stays in pin order and is far harder to miswire than loose jumpers.

**Cost:** ~$2.95 per ribbon in quantity 1 (PiShop US) · ~$1.00 per ribbon in a classroom order of
20+ (AliExpress from about $0.99), about $0.20 per kit · ~$0.65 per ribbon at district scale (an
Alibaba listing). **Price range:** AliExpress from ~$0.99; eBay ~$2–$4 (*estimate*); PiShop $2.95.

**AliExpress lead time:** 8–12 days (median 9).

**Spotting a bad batch:** Female sockets too loose to grip a header pin. Test-fit one strip on
the display when the order arrives.

**Search keywords:** `dupont jumper wire 40 pin male to female 20cm`, `M-F dupont ribbon cable`

**Where to buy:**

- [Search eBay for "dupont jumper wire 40 pin male to female 20cm"](https://www.ebay.com/sch/i.html?_nkw=dupont+jumper+wire+40+pin+male+to+female+20cm)
- [Search AliExpress for "dupont jumper wire 40 pin male to female 20cm"](https://www.aliexpress.com/w/wholesale-dupont-jumper-wire-40-pin-male-to-female-20cm.html)
- [Search Amazon for "dupont jumper wire 40 pin male to female 20cm"](https://www.amazon.com/s?k=dupont+jumper+wire+40+pin+male+to+female+20cm)
- [Search Alibaba for "dupont jumper wire 40 pin male to female 20cm"](https://www.alibaba.com/trade/search?SearchText=dupont+jumper+wire+40+pin+male+to+female+20cm)

---

### Micro-USB Data Cable

![USB-A to Micro-USB cable, showing both plugs](./micro-usb-cable.jpg){ width="350" }

*Photo: Electronicgrup, [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0) via [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:USB_2.0_A_MACHO_-_MICRO_USB_B_MACHO.jpg)*

**Used in:** Study Buddy base kit (×1)

**Used for:** [Chapter 4](../../chapters/04-pico-kit-hardware/index.md) and every chapter after
it. It powers the kit and carries the Thonny connection.

The Pico 2 WH has a **Micro-USB** port, not USB-C. The cable must carry **data**: charge-only
cables look identical and are the most common reason a Pico "isn't detected" on day one. If your
laptops have only USB-C ports, buy USB-C to Micro-USB cables. A computer USB port supplies about
500 mA, which is enough for this kit at the volumes the tests use.

!!! tip "Confirm it says data or sync"
    Look for "data", "sync" or "480 Mbps" in the listing. A cable sold only as a "charging cord"
    may have no data wires at all.

**Prep work:** None. Test each cable with a Pico in Thonny on arrival and discard any that only
charge.

**Cost:** ~$2.50 in quantity 1 (Cable Matters 3-pack, $7.49 on Amazon) · ~$2.50 each in a
classroom order of 20+ (seven 3-packs) · ~$1.00 each at district scale (*estimate*). **Price
range:** AliExpress ~$0.80–$2.00 (*estimate*: not checked this month); eBay ~$2–$4 (*estimate*);
Amazon $7.49–$9.44 per 3-pack.

**AliExpress lead time:** 8–12 days (median 9). Cables are the easiest part to buy domestically
the week of the lab if a few are missing.

**Search keywords:** `micro USB data sync cable 3ft`, `USB-C to Micro-USB data cable`

**Where to buy:**

- [Search eBay for "micro USB data sync cable 3ft"](https://www.ebay.com/sch/i.html?_nkw=micro+USB+data+sync+cable+3ft)
- [Search AliExpress for "micro USB data sync cable 3ft"](https://www.aliexpress.com/w/wholesale-micro-usb-data-sync-cable-3ft.html)
- [Search Amazon for "micro USB data sync cable 3ft"](https://www.amazon.com/s?k=micro+USB+data+sync+cable+3ft)

---

### Purchasing Strategy

#### Ordering lead time

These figures are **based on our 2026 AliExpress orders to Minnesota**: 8 packages, measured from
order date to delivery.

| Source | Orders measured | Typical delivery | Notes |
|--------|-----------------|------------------|-------|
| AliExpress | 8 packages | 8–12 days (median 9) | Every 2026 package arrived within two weeks |
| Micro Center | — | same day in store; online "ships in 5–7 business days" | The place to buy the Pico 2 WH |
| Amazon | — | 1–3 days with Prime (*estimate*, not measured) | The fallback for cables, buttons and breadboards |

The per-part notes above flag the parts that ship differently: the display (fragile glass in a
larger padded box) and the breadboards (bulky, sometimes split into several packages). The kit
has no batteries, so no part is held up by lithium shipping rules. If a later version adds a
battery pack, expect it to ship separately and take longer.

**Our recommendation:** place AliExpress orders **at least three weeks** before you need the
parts, and **four to five weeks ahead for a full classroom set**. Eight packages is a small
sample, and the extra weeks mean a lost package or a cracked display can be reordered and still
arrive in time. Use Micro Center or Amazon for last-minute gaps. Expect longer delays around
Lunar New Year, when Chinese factories and shipping largely stop for two weeks or more.

**Buy one, then buy twenty.** Order a single display, microphone and amplifier from a seller
first, confirm they are the GC9B72 360×360 display, a genuine INMP441 and a mono MAX98357A, then
place the classroom order with the same sellers.

**Order spares.** Add 10–15% over the class count for the display, microphone, amplifier and
Pico. Two spares of each add about $30 to a class order.

**Watch the pack sizes.** Buttons come in hundreds, breadboards in tens and cables in threes.
Round the order up to the pack, not to the roster.

**Buy boards from authorized resellers.** Micro Center sells the genuine Pico 2 WH for less than
any marketplace listing we found.

**Expect the odd bad unit, not a bad order.** Test every part on arrival with the kit's numbered
tests (01–07) and discard the occasional dud.

**Check your district's purchasing rules first.** Many districts cannot reimburse AliExpress
orders and require a domestic vendor with a W-9. If so, the Amazon and Micro Center prices are
your real prices. The round display has no Amazon listing we could find, so a district with that
rule will need an exception for it or a different domestic seller.

### Classroom Order Worksheet

| Part | Required? | Used in kits | Qty per student | Qty for 20 students | Est. cost for 20 |
|------|-----------|--------------|-----------------|---------------------|------------------|
| Raspberry Pi Pico 2 WH | Required | Study Buddy base | 1 | 20 | $139.80 |
| 2.1-inch round display (GC9B72) | Required | Study Buddy base | 1 | 20 | $107.80 |
| INMP441 microphone | Required | Study Buddy base | 1 | 20 | $20.00 |
| MAX98357A amplifier | Required | Study Buddy base | 1 | 20 | $19.80 |
| Speaker, 3525 8 Ω 2 W | Required | Study Buddy base | 1 | 20 | $11.60 |
| 6×6 mm push buttons | Required | Study Buddy base | 3 | 100 (1 pack of 100) | $4.99 |
| 830-point breadboard | Required | Study Buddy base | 1 | 20 | $22.00 |
| Male-to-male jumper set | Required | Study Buddy base | 1 set | 20 sets | $40.00 |
| Dupont ribbon, 40-wire M-F 20 cm | Required | Study Buddy base | 1/5 ribbon | 4 ribbons | $4.00 |
| Micro-USB data cable | Required | Study Buddy base | 1 | 21 (7 three-packs) | $52.43 |
| **Total** | | | | | **$422.42** |

**Per student:** ~$21.12. Add about $30 for two spares each of the Pico, display, microphone and
amplifier.

#### Shared classroom tools

These are bought once and reused for years, so they are kept out of the per-student figure.

| Tool | Cost | How many |
|------|------|----------|
| Soldering iron and solder (for microphone and amplifier headers, unless you buy pre-soldered boards) | $15–40 | 1 per 4–6 students |
| Wire strippers (for the speaker leads) | $8–15 | 1 per table |
| Small flat screwdriver (for the amplifier's screw terminal) | $2–5 | 1 per table |
