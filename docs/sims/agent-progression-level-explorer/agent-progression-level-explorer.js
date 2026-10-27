// Agent Progression Level Explorer - p5.js MicroSim
// CANVAS_HEIGHT: 610
// Part 1: the learner places eight abilities, one at a time, at the lowest
// agent progression level where each first appears (Level 1, 2, or 3).
// Each placement is scored once, explained, and drops onto the ladder.
// Part 2: the learner picks each level in turn to see its reply to the same
// question. The request and the reply fields never change between levels;
// only the reply text does. That is the swappable brain.
// Bloom level: Analyze (differentiate). Width responsive.

// ---------- canvas layout ----------
let canvasWidth = 400;          // replaced by the container width
let drawHeight = 560;           // drawing region (no controls here)
let controlHeight = 50;         // one row of controls
let canvasHeight = drawHeight + controlHeight;
let margin = 16;
let defaultTextSize = 16;

// ---------- content (from the chapter table and the specification) ----------
const levels = [
  { n: 1, brain: 'Rule-based buddy server (about 100 lines, no LLM)',
    adds: 'Fixed rules and tools that read the school calendar', fill: 'honeydew' },
  { n: 2, brain: 'The same server plus speech-to-text, text-to-speech, and one LLM call',
    adds: 'Spoken input and output, and free-form questions', fill: 'lightcyan' },
  { n: 3, brain: 'An optional open-source agent framework behind the same contract',
    adds: 'Ready-made planning loop, memory, and approval rules', fill: 'lavender' }
];

const abilities = [
  { n: 1, text: 'Matches the question text against fixed rules a person wrote.', level: 1,
    why: 'A rule-based server is made of exactly these rules.' },
  { n: 2, text: 'Reads events from the school calendar using a tool.', level: 1,
    why: 'Even the rule-based server calls tools when a rule says to.' },
  { n: 3, text: 'Answers a question worded in a way no rule anticipated.', level: 2,
    why: 'Interpreting free-form wording is what the LLM call adds.' },
  { n: 4, text: "Converts the student's speech to text and the reply back to speech.", level: 2,
    why: 'Level 2 adds speech-to-text and text-to-speech.' },
  { n: 5, text: 'Chooses for itself which tool to call for a new kind of request.', level: 2,
    why: 'An LLM-backed agent can choose tools instead of following a rule.' },
  { n: 6, text: 'Remembers a preferred reminder time between conversations using a ready-made memory feature.', level: 3,
    why: 'A framework supplies memory so you do not build it yourself.' },
  { n: 7, text: 'Asks for approval before a risky action using ready-made approval rules.', level: 3,
    why: 'A framework supplies approval rules that apply before an action.' },
  { n: 8, text: 'Runs a planning loop with tools, memory, and approvals supplied by a published toolkit.', level: 3,
    why: 'That combination is what an open-source agent framework provides.' }
];

// Part 2: the same question to all three levels
const sampleQuestion = 'Do I have anything big coming up this week?';
const replies = {
  1: { speak: 'Sorry, I only know about tests and due dates.',
       show: 'Tests and due dates only' },
  2: { speak: 'You have a lab report due Thursday and a Biology test on Friday.',
       show: 'Lab report Thu, Biology test Fri' },
  3: { speak: 'You have a lab report due Thursday and a Biology test on Friday. I can set a reminder for Thursday at 7 pm. Should I?',
       show: 'Lab report Thu, Biology test Fri. Reminder?' }
};

// ---------- state ----------
let current = 0;          // ability index
let answered = false;
let placements = {};      // ability number -> { choice, correct }
let score = 0;
let part = 1;             // 1 = placing abilities, 2 = comparing replies
let replyLevel = 0;       // level whose reply is shown in part 2 (0 = none yet)
let viewed = {};          // levels viewed in part 2

// ---------- controls ----------
let levelButtons = [];
let nextButton, restartButton;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  // Create every control first, then position them
  for (let k = 1; k <= 3; k++) {
    const b = createButton('Level ' + k);
    b.mousePressed(() => chooseLevel(k));
    levelButtons.push(b);
  }
  nextButton = createButton('Next');
  nextButton.mousePressed(nextAbility);
  restartButton = createButton('Restart');
  restartButton.mousePressed(restart);

  positionControls();
  restart();

  describe('Part 1: eight abilities are shown one at a time and the learner places each at Level 1, 2, ' +
    'or 3, the lowest level where it first appears, with feedback and a running score out of 8. ' +
    'Part 2: the learner chooses each level to see its reply to the same question, alongside a request ' +
    'and reply whose fields stay the same at every level.', LABEL);
}

function positionControls() {
  const y = drawHeight + 10;
  let x = 10;
  for (const b of [...levelButtons, nextButton]) {
    b.position(x, y);
    x += b.elt.offsetWidth + 10;
  }
  restartButton.position(max(x + 10, canvasWidth - restartButton.elt.offsetWidth - 10), y);
}

function restart() {
  current = 0;
  answered = false;
  placements = {};
  score = 0;
  part = 1;
  replyLevel = 0;
  viewed = {};
  updateButtons();
}

function chooseLevel(k) {
  if (part === 2) {              // part 2: show this level's reply
    replyLevel = k;
    viewed[k] = true;
    updateButtons();
    return;
  }
  if (answered) return;          // one attempt per ability
  const a = abilities[current];
  const correct = (k === a.level);
  if (correct) score++;
  placements[a.n] = { choice: k, correct: correct };
  answered = true;
  updateButtons();
}

function nextAbility() {
  if (part !== 1 || !answered) return;
  if (current < abilities.length - 1) {
    current++;
    answered = false;
  } else {
    part = 2;
  }
  updateButtons();
}

function updateButtons() {
  for (let i = 0; i < 3; i++) {
    const b = levelButtons[i];
    if (part === 1) {
      b.elt.disabled = answered;
      const p = placements[abilities[current].n];
      b.elt.classList.toggle('chosen', answered && p && p.choice === i + 1);
    } else {
      b.elt.disabled = false;
      b.elt.classList.toggle('chosen', replyLevel === i + 1);
    }
  }
  nextButton.elt.disabled = !(part === 1 && answered);
  nextButton.html(part === 1 && current === abilities.length - 1 ? 'Compare replies' : 'Next');
}

function draw() {
  updateCanvasSize();

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
  text('Agent Progression Level Explorer', canvasWidth / 2, 10);

  textSize(15);
  textAlign(LEFT, TOP);
  fill('dimgray');
  noStroke();
  text(part === 1 ? 'Part 1: place each ability on the ladder' : 'Part 2: compare the three replies', margin, 44);
  textAlign(RIGHT, TOP);
  fill('black');
  noStroke();
  text('Score: ' + score + ' of 8', canvasWidth - margin, 44);

  if (part === 1) {
    const bottom = drawAbilityCard();
    drawLadder(max(bottom + 12, 250), drawHeight - 10);
  } else {
    const bottom = drawScoreCard();
    const ladderBottom = bottom + 12 + 3 * 46;
    drawLadder(bottom + 12, ladderBottom);
    drawReplyPanel(ladderBottom + 10, drawHeight - 10);
  }
}

// Part 1 card: the ability, the question, and the feedback
function drawAbilityCard() {
  const a = abilities[current];
  const x = margin, y = 68, w = canvasWidth - 2 * margin, tx = x + 12, tw = w - 24;

  textSize(18);
  const aLines = wrapLines(a.text, tw);
  let msg = '', msgLines = [];
  if (answered) {
    const p = placements[a.n];
    msg = p.correct ? 'Correct: ' + a.why : 'Not quite. This first appears at Level ' + a.level + ': ' + a.why;
    textSize(defaultTextSize);
    msgLines = wrapLines(msg, tw);
  }
  const h = 34 + aLines.length * 24 + 10 + (answered ? msgLines.length * 21 + 4 : 46);

  let border = 'silver', bg = 'white';
  if (answered) {
    const ok = placements[a.n].correct;
    border = ok ? 'seagreen' : 'darkorange';
    bg = ok ? 'honeydew' : 'seashell';
  }
  stroke(border);
  strokeWeight(answered ? 2 : 1);
  fill(bg);
  rect(x, y, w, h, 10);
  strokeWeight(1);

  noStroke();
  textAlign(LEFT, TOP);
  fill('steelblue');
  textSize(14);
  text('ABILITY ' + (current + 1) + ' OF 8', tx, y + 10);
  fill('black');
  textSize(18);
  let ty = y + 34;
  for (const l of aLines) { noStroke(); text(l, tx, ty); ty += 24; }
  ty += 10;
  if (!answered) {
    textStyle(BOLD);
    textSize(17);
    noStroke();
    text('At which level does this ability first appear?', tx, ty, tw);
    textStyle(NORMAL);
    textSize(14);
    fill('dimgray');
    noStroke();
    text('Pick Level 1, 2, or 3 below. One attempt per ability.', tx, ty + 24, tw);
  } else {
    textSize(defaultTextSize);
    fill('black');
    for (const l of msgLines) { noStroke(); text(l, tx, ty); ty += 21; }
  }
  return y + h;
}

// Part 2 card: final score and mastery
function drawScoreCard() {
  const x = margin, y = 68, w = canvasWidth - 2 * margin, tx = x + 12, tw = w - 24;
  textSize(15);
  const mastery = score >= 7 ? 'Mastery reached (7 of 8 needed).' :
    'Mastery needs 7 of 8. Reread "Agent Progression Levels" and press Restart.';
  const mLines = wrapLines(mastery, tw);
  const h = 38 + mLines.length * 20 + 8;
  stroke('silver');
  fill('white');
  rect(x, y, w, h, 10);
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textStyle(BOLD);
  textSize(19);
  text('You placed ' + score + ' of 8 abilities correctly.', tx, y + 10);
  textStyle(NORMAL);
  textSize(15);
  fill(score >= 7 ? 'seagreen' : 'darkorange');
  let ty = y + 38;
  for (const l of mLines) { noStroke(); text(l, tx, ty); ty += 20; }
  return y + h;
}

// The three-rung ladder, Level 3 on top. Placed abilities appear as chips
// on the rung of their correct level.
function drawLadder(top, bottom) {
  const x = margin, w = canvasWidth - 2 * margin;
  const gap = 6;
  const rungH = (bottom - top - 2 * gap) / 3;
  const labelW = 74;
  const chipD = min(30, rungH - 12);
  const chipsW = 3 * (chipD + 6) + 6;
  const textW = w - labelW - chipsW - 12;
  const compact = rungH < 70;   // part 2 uses short rungs

  for (let i = 0; i < 3; i++) {
    const lv = levels[2 - i];
    const ry = top + i * (rungH + gap);
    const lit = (part === 2 && replyLevel === lv.n) ||
                (part === 1 && answered && abilities[current].level === lv.n);
    stroke(lit ? 'royalblue' : 'silver');
    strokeWeight(lit ? 3 : 1);
    fill(lv.fill);
    rect(x, ry, w, rungH, 8);
    strokeWeight(1);

    noStroke();
    fill('black');
    textStyle(BOLD);
    textSize(17);
    textAlign(LEFT, CENTER);
    text('Level ' + lv.n, x + 10, ry + rungH / 2);
    textStyle(NORMAL);

    // brain and what it adds; shrink to fit the rung
    const desc = compact ? lv.adds : lv.brain + '. Adds: ' + lv.adds + '.';
    let size;
    let lines;
    for (size = 15; size >= 11; size--) {
      textSize(size);
      lines = wrapLines(desc, textW);
      if (lines.length * (size + 4) <= rungH - 8) break;
    }
    fill('dimgray');
    textAlign(LEFT, TOP);
    const ty = ry + (rungH - lines.length * (size + 4)) / 2;
    for (let k = 0; k < lines.length; k++) {
      noStroke();
      text(lines[k], x + labelW, ty + k * (size + 4));
    }

    // chips for abilities whose correct level is this one
    const placed = abilities.filter(a => a.level === lv.n && placements[a.n]);
    for (let k = 0; k < placed.length; k++) {
      const p = placements[placed[k].n];
      const cx = x + w - chipsW + 6 + k * (chipD + 6) + chipD / 2;
      const cy = ry + rungH / 2;
      stroke(p.correct ? 'seagreen' : 'darkorange');
      strokeWeight(3);
      fill(p.correct ? 'palegreen' : 'peachpuff');
      circle(cx, cy, chipD);
      strokeWeight(1);
      noStroke();
      fill('black');
      textSize(14);
      textAlign(CENTER, CENTER);
      text(placed[k].n, cx, cy);
    }
  }
}

// Part 2: the same request, and the selected level's reply
function drawReplyPanel(top, bottom) {
  const x = margin, w = canvasWidth - 2 * margin;
  const tx = x + 12;
  stroke('silver');
  fill('white');
  rect(x, top, w, bottom - top, 10);

  // question and calendar lines wrap at narrow widths; the boxes start below them
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(15);
  textStyle(BOLD);
  let hy = top + 8;
  for (const l of wrapLines('Question: "' + sampleQuestion + '"', w - 24)) { noStroke(); text(l, tx, hy); hy += 19; }
  textStyle(NORMAL);
  textSize(13);
  fill('dimgray');
  hy += 1;
  for (const l of wrapLines('Calendar (illustrative): DUE: Lab report, Thursday. TEST: Biology, Friday.', w - 24)) {
    noStroke(); text(l, tx, hy); hy += 17;
  }

  const boxTop = hy + 5;
  const boxH = bottom - boxTop - 32;
  const colGap = 10;
  const colW = (w - 24 - colGap) / 2;

  // request box: identical at every level
  const req = ['{', '  "device": "desk-07",', '  "kind": "question",',
    '  "text": "do i have anything big coming up this week"', '}'];
  drawJsonBox('Request (same at every level)', req, tx, boxTop, colW, boxH, '');

  // reply box: same fields, level-specific text
  let rep;
  if (replyLevel === 0) {
    rep = ['Choose Level 1, 2, or 3 below', 'to see that level\'s reply.'];
  } else {
    const r = replies[replyLevel];
    rep = ['{', '  "speak": "' + r.speak + '",', '  "show": "' + r.show + '",', '  "next_mode": "clock"', '}'];
  }
  drawJsonBox(replyLevel ? 'Reply from Level ' + replyLevel : 'Reply', rep, tx + colW + colGap, boxTop, colW, boxH,
    replyLevel ? 'changes' : '');

  // viewed checklist and the key observation
  const seen = [1, 2, 3].map(k => 'Level ' + k + (viewed[k] ? ' seen' : ' not yet')).join('   ');
  textSize(14);
  textAlign(LEFT, TOP);
  noStroke();
  if (viewed[1] && viewed[2] && viewed[3]) {
    fill('darkgreen');
    text('Notice: the request and the reply fields were the same at all three levels. Only the reply text changed.',
      tx, bottom - 28, w - 24);
  } else {
    fill('dimgray');
    text(seen, tx, bottom - 24, w - 24);
  }
}

// A titled box of JSON-like lines; long lines wrap with an indent.
// When mark is 'changes', the text values of speak and show are colored.
function drawJsonBox(title, lines, x, y, w, h, mark) {
  stroke('lightsteelblue');
  fill('ghostwhite');
  rect(x, y, w, h, 6);
  noStroke();
  fill('black');
  textStyle(BOLD);
  textSize(14);
  textAlign(LEFT, TOP);
  const titleLines = wrapLines(title, w - 16);   // wraps in narrow boxes
  for (let i = 0; i < titleLines.length; i++) { noStroke(); text(titleLines[i], x + 8, y + 6 + i * 18); }
  textStyle(NORMAL);
  const bodyTop = y + 10 + titleLines.length * 18;

  // fit the text into the box
  let size, wrapped;
  for (size = 14; ; size--) {
    textSize(size);
    wrapped = [];
    for (const l of lines) {
      const indent = l.match(/^ */)[0];          // keep JSON indentation
      const parts = wrapLines(l.trim(), w - 22 - textWidth(indent + '    '));
      parts.forEach((p, i) => wrapped.push({ t: indent + (i ? '    ' : '') + p, src: l }));
    }
    if (wrapped.length * (size + 4) <= y + h - bodyTop - 4 || size <= 10) break;
  }
  let ly = bodyTop;
  for (const ln of wrapped) {
    const changing = mark === 'changes' && (ln.src.indexOf('"speak"') >= 0 || ln.src.indexOf('"show"') >= 0);
    fill(changing ? 'firebrick' : 'midnightblue');
    noStroke();
    text(ln.t, x + 8, ly);
    ly += size + 4;
  }
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
