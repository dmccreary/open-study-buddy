// Chatbot or Agent Sorter - p5.js MicroSim
// CANVAS_HEIGHT: 562
// The learner reads ten illustrative behaviors, one at a time, and sorts each
// into "Chatbot behavior" or "Agent behavior". Each answer is scored once and
// followed by a one-sentence reason that names the trait involved.
// The first run uses the fixed order from the specification and is the only
// run that counts as evidence. Restart gives the same ten behaviors in a new
// random order as practice.
// Bloom level: Analyze (distinguish). Width responsive.

// ---------- canvas layout ----------
let canvasWidth = 400;          // replaced by the container width
let drawHeight = 512;           // drawing region (no controls here)
let controlHeight = 50;         // one row of controls
let canvasHeight = drawHeight + controlHeight;
let margin = 20;
let defaultTextSize = 16;

// ---------- content (from the specification) ----------
const CHATBOT = 'Chatbot behavior';
const AGENT = 'Agent behavior';

const behaviors = [
  { n: 1, text: 'Answers one typed question, then waits for the next message.',
    bin: CHATBOT, why: 'It replies to a single message and takes no further action.' },
  { n: 2, text: 'Reads the school calendar, finds a test, and adds a reminder for the night before.',
    bin: AGENT, why: 'It uses a tool and acts in several steps without being asked for each one.' },
  { n: 3, text: 'Explains what a "TEST:" event is when asked, with no access to any calendar.',
    bin: CHATBOT, why: 'It gives information only and takes no action for the person.' },
  { n: 4, text: 'Asks "Should I move your study session to 6 pm?" before changing the schedule.',
    bin: AGENT, why: 'It comes back for a decision before an action that affects the person.' },
  { n: 5, text: 'Rewrites a paragraph that the student pastes in.',
    bin: CHATBOT, why: 'One request produces one reply, and the work ends there.' },
  { n: 6, text: 'Checks every morning for new due dates and announces them.',
    bin: AGENT, why: "It acts on its own over time on the person's behalf." },
  { n: 7, text: 'Tells a joke when asked.',
    bin: CHATBOT, why: 'It produces a reply only.' },
  { n: 8, text: "Sends an alert to the student's desk device when a test is one day away.",
    bin: AGENT, why: 'It takes an action through a tool, without being asked at that moment.' },
  { n: 9, text: 'Remembers that the student prefers 7 pm reminders and schedules the next reminder for 7 pm.',
    bin: AGENT, why: "It uses what it remembers to take an action on the person's behalf." },
  { n: 10, text: 'Summarizes a news article that the student pastes in.',
    bin: CHATBOT, why: 'One request produces one reply, and no action follows.' }
];

// ---------- state ----------
let order = [];          // indexes into behaviors for this run
let current = 0;         // position in order
let answered = false;    // has the learner answered the current item?
let lastChoice = '';     // the bin the learner chose for the current item
let score = 0;
let results = [];        // { item, choice, correct } for each answered item
let runNumber = 1;       // only run 1 counts as evidence
let finished = false;

// ---------- controls ----------
let chatbotButton, agentButton, nextButton, restartButton;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  // Create every control first, then position them
  chatbotButton = createButton(CHATBOT);
  chatbotButton.mousePressed(() => choose(CHATBOT));
  agentButton = createButton(AGENT);
  agentButton.mousePressed(() => choose(AGENT));
  nextButton = createButton('Next');
  nextButton.mousePressed(nextItem);
  restartButton = createButton('Restart');
  restartButton.mousePressed(restartRun);

  positionControls();
  startRun(false);

  describe('A sorting quiz with ten illustrative behaviors. For each behavior the learner ' +
    'chooses Chatbot behavior or Agent behavior, sees whether the choice was correct and why, ' +
    'and a running score out of 10. Answered behaviors appear as numbered chips in two bins.', LABEL);
}

// Position the row of buttons inside the control region
function positionControls() {
  const y = drawHeight + 10;
  let x = 10;
  for (const b of [chatbotButton, agentButton, nextButton]) {
    b.position(x, y);
    x += b.elt.offsetWidth + 10;
  }
  // Restart sits at the right edge when there is room, otherwise after Next
  const rw = restartButton.elt.offsetWidth;
  restartButton.position(max(x + 10, canvasWidth - rw - 10), y);
}

function startRun(shuffleOrder) {
  order = behaviors.map((b, i) => i);
  if (shuffleOrder) order = shuffle(order);
  current = 0;
  answered = false;
  lastChoice = '';
  score = 0;
  results = [];
  finished = false;
  updateButtons();
}

function choose(bin) {
  if (answered || finished) return;   // one attempt per item
  const item = behaviors[order[current]];
  answered = true;
  lastChoice = bin;
  const correct = (bin === item.bin);
  if (correct) score++;
  results.push({ item: item, choice: bin, correct: correct });
  updateButtons();
}

function nextItem() {
  if (!answered) return;              // Next requires an answer first
  if (current < order.length - 1) {
    current++;
    answered = false;
    lastChoice = '';
  } else {
    finished = true;
  }
  updateButtons();
}

function restartRun() {
  runNumber++;
  startRun(true);
}

// Enable or disable controls to match the state
function updateButtons() {
  setEnabled(chatbotButton, !answered && !finished);
  setEnabled(agentButton, !answered && !finished);
  setEnabled(nextButton, answered && !finished);
  nextButton.html(current === order.length - 1 ? 'See results' : 'Next');
  chatbotButton.elt.classList.toggle('chosen', answered && !finished && lastChoice === CHATBOT);
  agentButton.elt.classList.toggle('chosen', answered && !finished && lastChoice === AGENT);
}

function setEnabled(btn, on) {
  btn.elt.disabled = !on;
}

function draw() {
  updateCanvasSize();

  // drawing region and control region backgrounds
  stroke('silver');
  strokeWeight(1);
  fill('aliceblue');
  rect(0, 0, canvasWidth, drawHeight);
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  // title
  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(24);
  text('Chatbot or Agent Sorter', canvasWidth / 2, 10);

  // run label and running score
  textSize(defaultTextSize);
  textAlign(LEFT, TOP);
  fill('dimgray');
  noStroke();
  const runLabel = runNumber === 1 ? 'First run (counts as evidence)' : 'Practice run ' + runNumber + ' (new order)';
  text(runLabel, margin, 44);
  textAlign(RIGHT, TOP);
  fill('black');
  noStroke();
  text('Score: ' + score + ' of 10', canvasWidth - margin, 44);

  if (finished) {
    if (drawSummary()) drawBins(drawHeight - 96, 84, true);
  } else {
    drawQuestion();
    drawBins(290, drawHeight - 290 - 14, false);
  }
}

// The behavior card, the question, and the feedback
function drawQuestion() {
  const item = behaviors[order[current]];
  const cardX = margin, cardY = 72, cardW = canvasWidth - 2 * margin;

  // card
  stroke('silver');
  fill('white');
  rect(cardX, cardY, cardW, 108, 10);

  noStroke();
  fill('steelblue');
  textSize(14);
  textAlign(LEFT, TOP);
  text('BEHAVIOR ' + (current + 1) + ' OF 10  (illustrative)', cardX + 14, cardY + 10);

  fill('black');
  textSize(18);
  noStroke();
  drawWrapped(item.text, cardX + 14, cardY + 34, cardW - 28, 24);

  // question or feedback
  const fy = cardY + 122;
  textSize(defaultTextSize);
  if (!answered) {
    fill('black');
    noStroke();
    textStyle(BOLD);
    drawWrapped('Is this a chatbot behavior or an agent behavior?', cardX, fy, cardW, 22);
    textStyle(NORMAL);
    fill('dimgray');
    noStroke();
    drawWrapped('Choose a bin with the buttons below. Each behavior gets one attempt.', cardX, fy + 26, cardW, 22);
  } else {
    const last = results[results.length - 1];
    const msg = last.correct ? 'Correct: ' + item.why : 'Not quite: ' + item.why;
    stroke(last.correct ? 'seagreen' : 'darkorange');
    strokeWeight(2);
    fill(last.correct ? 'honeydew' : 'seashell');
    rect(cardX, fy - 4, cardW, 74, 8);
    strokeWeight(1);
    noStroke();
    fill('black');
    textStyle(BOLD);
    text('The answer is: ' + item.bin, cardX + 12, fy + 4);
    textStyle(NORMAL);
    noStroke();
    drawWrapped(msg, cardX + 12, fy + 28, cardW - 24, 20);
  }
}

// Two bins along the bottom of the drawing region. Each answered behavior
// becomes a numbered chip in its correct bin: green if the learner sorted it
// correctly, orange if not.
function drawBins(binY, binH, compact) {
  const gap = 16;
  const binW = (canvasWidth - 2 * margin - gap) / 2;
  const bins = [CHATBOT, AGENT];
  const highlight = answered && !finished ? behaviors[order[current]].bin : '';

  for (let i = 0; i < 2; i++) {
    const bx = margin + i * (binW + gap);
    stroke(highlight === bins[i] ? 'royalblue' : 'silver');
    strokeWeight(highlight === bins[i] ? 3 : 1);
    fill(i === 0 ? 'lavender' : 'lightcyan');
    rect(bx, binY, binW, binH, 10);
    strokeWeight(1);

    noStroke();
    fill('black');
    textSize(18);
    textStyle(BOLD);
    textAlign(CENTER, TOP);
    text(bins[i], bx + binW / 2, binY + 10);
    textStyle(NORMAL);
    if (!compact) {
      textSize(14);
      fill('dimgray');
      noStroke();
      const hint = i === 0 ? 'replies only' : 'acts, uses tools, asks first';
      text(hint, bx + binW / 2, binY + 34);
    }

    // chips for answered items whose correct bin is this one
    const step = min(44, (binW - 28) / 5);    // five chips fit on one row
    const chipR = min(17, step / 2 - 3);
    let cx = bx + 14 + chipR, cy = binY + (compact ? 54 : 78);
    for (const r of results) {
      if (r.item.bin !== bins[i]) continue;
      stroke(r.correct ? 'seagreen' : 'darkorange');
      strokeWeight(3);
      fill(r.correct ? 'palegreen' : 'peachpuff');
      circle(cx, cy, chipR * 2);
      strokeWeight(1);
      noStroke();
      fill('black');
      textSize(16);
      textAlign(CENTER, CENTER);
      text(r.item.n, cx, cy);
      cx += step;
      if (cx > bx + binW - chipR - 4) { cx = bx + 14 + chipR; cy += step; }
    }
  }

  // chip legend
  noStroke();
  fill('dimgray');
  textSize(14);
  textAlign(LEFT, TOP);
  text('Chips are behavior numbers: green = correct, orange = missed', margin, binY - 20);
}

// End-of-run summary: score, mastery, and every missed behavior with its reason.
// The compact bins stay visible below the card unless the missed list needs
// that room (many misses on a narrow screen); returns true when bins fit.
function drawSummary() {
  const x = margin, y = 72, w = canvasWidth - 2 * margin;
  const missed = results.filter(r => !r.correct);

  // measure the header block
  textSize(defaultTextSize);
  const mastery = score >= 8 ? 'Mastery reached (8 of 10 needed).' :
    'Mastery needs 8 of 10. Reread "Chatbot Versus Agent" and try a practice run.';
  const masteryLines = wrapLines(mastery, w - 28);
  const listTop = y + 38 + masteryLines.length * 20 + 30;

  // fit the missed list: first with the bins shown, then without them
  let showBins = true, size = 15, lines = [];
  const fit = (cardH) => {
    for (size = 15; size >= 11; size--) {
      textSize(size);
      lines = [];
      for (const r of missed) {
        lines.push(...wrapLines(r.item.n + '. ' + r.item.text + ' Answer: ' + r.item.bin + '. ' + r.item.why, w - 28));
      }
      if (lines.length * (size + 5) + missed.length * 4 <= y + cardH - listTop - 8) return true;
    }
    return false;
  };
  let cardH = drawHeight - 96 - 26 - y;
  if (!fit(cardH)) {
    showBins = false;
    cardH = drawHeight - 10 - y;
    fit(cardH);
  }

  stroke('silver');
  fill('white');
  rect(x, y, w, cardH, 10);

  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(20);
  textStyle(BOLD);
  text('You sorted ' + score + ' of 10 correctly.', x + 14, y + 10);
  textStyle(NORMAL);
  textSize(defaultTextSize);
  fill(score >= 8 ? 'seagreen' : 'darkorange');
  drawWrapped(mastery, x + 14, y + 38, w - 28, 20);

  fill('black');
  noStroke();
  if (missed.length === 0) {
    drawWrapped('No missed behaviors. Press Restart for a practice run in a new order.', x + 14, listTop - 22, w - 28, 20);
    return showBins;
  }
  textSize(15);
  textStyle(BOLD);
  text('Missed behaviors:', x + 14, listTop - 22);
  textStyle(NORMAL);

  // draw each missed behavior as its own wrapped paragraph
  textSize(size);
  let ly = listTop;
  for (const r of missed) {
    const ls = wrapLines(r.item.n + '. ' + r.item.text + ' Answer: ' + r.item.bin + '. ' + r.item.why, w - 28);
    for (const ln of ls) {
      noStroke();
      text(ln, x + 14, ly);
      ly += size + 5;
    }
    ly += 4;
  }
  return showBins;
}

// ---------- text helpers ----------
// Break a string into lines that fit maxW at the current text size
function wrapLines(str, maxW) {
  const words = str.split(' ');
  const lines = [];
  let line = '';
  for (const w of words) {
    const test = line ? line + ' ' + w : w;
    if (textWidth(test) > maxW && line) {
      lines.push(line);
      line = w;
    } else {
      line = test;
    }
  }
  if (line) lines.push(line);
  return lines;
}

// Draw wrapped text with top-left alignment; returns the height used
function drawWrapped(str, x, y, maxW, leading) {
  const lines = wrapLines(str, maxW);
  textAlign(LEFT, TOP);
  noStroke();
  for (let i = 0; i < lines.length; i++) {
    text(lines[i], x, y + i * leading);
  }
  return lines.length * leading;
}

// ---------- responsive design ----------
function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  positionControls();
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    canvasWidth = Math.floor(container.getBoundingClientRect().width);
  }
}
