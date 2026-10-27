// MQTT Topic Router - p5.js MicroSim
// CANVAS_HEIGHT: 560
// Apply the MQTT 3.1.1 wildcard rules: split filter and topic at "/".
// "+" matches exactly one level (any text, even empty). "#" is valid only as
// the last level and matches the remaining levels, including none. Any other
// level must equal the topic level exactly. Without "#", the level counts must
// be equal. A topic starting with "$" is not selected by a filter whose first
// level is "+" or "#". Same rules as 01-topic-matcher.py (Chapter 15).

let canvasWidth = 800;
let drawHeight = 480;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

const FILTERS = [
  ['S1', 'school/crhs/alert'],
  ['S2', 'school/crhs/class/214/alert'],
  ['S3', 'school/crhs/class/+/alert'],
  ['S4', 'school/crhs/device/+/status'],
  ['S5', 'school/crhs/#'],
  ['S6', 'school/+/alert'],
  ['S7', '#']
];
const TOPICS = [
  { t: 'school/crhs/alert', answer: ['S1', 'S5', 'S6', 'S7'],
    why: 'S1 is the exact name. S5 and S7 take everything below their prefix. S6\'s "+" is the one level "crhs". S3 needs a "class" level that is not there.' },
  { t: 'school/crhs/class/214/alert', answer: ['S2', 'S3', 'S5', 'S7'],
    why: 'S2 is exact and S3\'s "+" is the one level "214". S6 fails because "+" can match only one level, and three levels sit between "school" and "alert".' },
  { t: 'school/crhs/class/lab-130/alert', answer: ['S3', 'S5', 'S7'],
    why: 'S3\'s "+" matches "lab-130". S2 names room 214 only.' },
  { t: 'school/crhs/device/desk-07/status', answer: ['S4', 'S5', 'S7'],
    why: 'S4\'s "+" matches "desk-07". S3 fails on "device" versus "class".' },
  { t: 'school/crhs/device/desk-07/telemetry', answer: ['S5', 'S7'],
    why: 'S4 needs the last level to be "status". Only the "#" filters take it.' },
  { t: 'school/trhs/alert', answer: ['S6', 'S7'],
    why: 'S6\'s "+" matches "trhs". S1 and S5 name "crhs".' },
  { t: 'school/crhs', answer: ['S5', 'S7'],
    why: '"#" matches its parent level too, so "school/crhs/#" selects "school/crhs".' },
  { t: '$SYS/broker/uptime', answer: [],
    why: 'A filter that starts with a wildcard does not select a topic that starts with "$".' }
];

let mode = 'explore';
let tIndex = 0;
let submitted = false;
let finished = false;
let results = [];
let feedback = '';
let feedbackCorrect = false;

let boxes = [];
let submitButton, modeButton, nextButton, tryLabel, tryInput;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  for (const [id] of FILTERS) boxes.push(createCheckbox(' ' + id, false));
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  modeButton = createButton('Start the 8 topics');
  modeButton.mousePressed(toggleMode);
  nextButton = createButton('Next topic');
  nextButton.mousePressed(nextTopic);
  tryLabel = createSpan('Try a topic:');
  tryInput = createInput('school/crhs/alert');
  tryInput.size(230);
  for (const el of [...boxes, submitButton, modeButton, nextButton, tryLabel, tryInput]) el.style('font-size', '16px');

  positionControls();
  updateControlStates();

  describe('A topic split into its levels, above a list of seven MQTT subscription filters, each also split into levels. For a topic, each level of each filter is colored green when it matches and red where the match fails, and every filter says whether it selects the topic. In the quiz the learner ticks the filters that select each of eight topics, then sees the correct set.', LABEL);
}

// level-by-level match: { ok, marks } with a mark per filter level:
// 'eq' equal, 'plus' + matched, 'hash' # matched the rest, 'bad' failed, 'skip' not reached
function matchDetail(filter, topic) {
  const fl = filter.split('/');
  const tl = topic.split('/');
  const marks = fl.map(() => 'skip');
  if (tl[0].startsWith('$') && (fl[0] === '+' || fl[0] === '#')) {
    marks[0] = 'bad';
    return { ok: false, marks: marks, reason: 'a wildcard first level never selects a "$" topic' };
  }
  for (let i = 0; i < fl.length; i++) {
    if (fl[i] === '#') { marks[i] = 'hash'; return { ok: true, marks: marks }; }
    if (i >= tl.length) { marks[i] = 'bad'; return { ok: false, marks: marks, reason: 'the topic has fewer levels' }; }
    if (fl[i] === '+') marks[i] = 'plus';
    else if (fl[i] === tl[i]) marks[i] = 'eq';
    else { marks[i] = 'bad'; return { ok: false, marks: marks, reason: '"' + fl[i] + '" is not "' + tl[i] + '"' }; }
  }
  if (fl.length !== tl.length) return { ok: false, marks: marks, reason: 'the topic has more levels' };
  return { ok: true, marks: marks };
}

function currentTopic() {
  return mode === 'quiz' ? TOPICS[min(tIndex, 7)].t : tryInput.value().trim();
}

// ---------- drawing ----------

function draw() {
  updateCanvasSize();
  stroke('silver');
  strokeWeight(1);
  fill('aliceblue');
  rect(0, 0, canvasWidth, drawHeight);
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(24);
  text('MQTT Topic Router', canvasWidth / 2, 10);
  textSize(16);
  fill('dimgray');
  let status;
  if (mode === 'explore') status = 'Explore: type any topic below';
  else if (finished) status = 'All 8 topics done   |   Score: ' + countCorrect() + ' of 8';
  else status = 'Topic ' + (tIndex + 1) + ' of 8   |   Score: ' + countCorrect() + ' of 8';
  text(status, canvasWidth / 2, 42);

  const topic = currentTopic();
  const reveal = mode === 'explore' || submitted;
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(16);
  textStyle(BOLD);
  text('Topic', margin, 88);
  textStyle(NORMAL);
  drawLevels(topic.split('/'), null, 90, 76, 'topic');

  let y = 118;
  const answer = mode === 'quiz' ? TOPICS[min(tIndex, 7)].answer : null;
  for (let i = 0; i < FILTERS.length; i++) {
    const [id, f] = FILTERS[i];
    const d = matchDetail(f, topic);
    const marked = boxes[i].checked();
    noStroke();
    if (mode === 'quiz' && submitted && marked !== answer.includes(id)) {
      fill(255, 228, 225);
      rect(margin - 4, y - 2, canvasWidth - 2 * margin + 8, 32, 6);
    }
    fill('black');
    textAlign(LEFT, CENTER);
    textStyle(BOLD);
    text(id, margin, y + 14);
    textStyle(NORMAL);
    const endX = drawLevels(f.split('/'), reveal ? d.marks : null, 50, y + 2, 'filter');
    if (reveal) {
      fill(d.ok ? 'darkgreen' : 'firebrick');
      textAlign(LEFT, CENTER);
      textSize(14);
      const verdict = d.ok ? 'selects it' : 'no: ' + d.reason;
      text(verdict, min(endX + 10, canvasWidth - margin - textWidth(verdict)), y + 14);
    } else if (mode === 'quiz') {
      fill(marked ? 'navy' : 'silver');
      textAlign(LEFT, CENTER);
      textSize(14);
      text(marked ? 'you marked it' : '', endX + 10, y + 14);
    }
    y += 36;
  }
  drawPanel(margin, 380, canvasWidth - 2 * margin, drawHeight - 388);
}

// draws levels as boxes; returns the x after the last box
function drawLevels(levels, marks, x, y, kind) {
  textSize(14);
  textFont('monospace');
  for (let i = 0; i < levels.length; i++) {
    const s = levels[i] === '' ? ' ' : levels[i];
    const w = textWidth(s) + 12;
    let bg = kind === 'topic' ? 'lightcyan' : 'white';
    if (marks) {
      const m = marks[i];
      if (m === 'eq' || m === 'plus' || m === 'hash') bg = 'palegreen';
      if (m === 'bad') bg = 'mistyrose';
      if (m === 'skip') bg = 'whitesmoke';
    }
    stroke('silver');
    fill(bg);
    rect(x, y, w, 24, 4);
    noStroke();
    fill('black');
    textAlign(CENTER, CENTER);
    text(s, x + w / 2, y + 12);
    x += w;
    if (i < levels.length - 1) {
      fill('gray');
      text('/', x + 6, y + 12);
      x += 12;
    }
  }
  textFont('sans-serif');
  return x;
}

function drawPanel(x, y, w, h) {
  fill(255, 255, 255, 235);
  stroke('silver');
  rect(x, y, w, h, 10);
  const pad = 10;
  const tw = w - 2 * pad;
  const yy = y + 8;
  noStroke();
  textAlign(LEFT, TOP);
  textSize(16);
  if (mode === 'explore') {
    fill('navy');
    textStyle(ITALIC);
    text('Which subscribers would receive a message on this topic?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Green levels matched, red is where a filter fails. Try school/crhs, school/crhs/class/214/alert and $SYS/x.', x + pad, yy + 22, tw, 20);
    return;
  }
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 7 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 8. ' + (sc >= 7 ? 'Mastery reached.' : 'Mastery is 7 of 8.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('Topics 5 and 7 cost the most points. Which rule does each one test: the one-level "+" or the parent-level "#"?', x + pad, yy + 24, tw, 20);
    return;
  }
  if (!submitted) {
    fill('navy');
    textStyle(ITALIC);
    text('Which filters select this topic?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Tick every filter, S1 to S7, that selects the topic (it may be none), then Submit. One submission per topic.', x + pad, yy + 22, tw, 20);
    return;
  }
  fill(feedbackCorrect ? 'darkgreen' : 'firebrick');
  textStyle(BOLD);
  drawWrapped(feedback, x + pad, yy, tw, 20);
  textStyle(NORMAL);
}

function drawWrapped(str, x, y, maxW, lineH) {
  const words = str.split(' ');
  let lineTxt = '';
  let yy = y;
  noStroke();
  for (const word of words) {
    const test = lineTxt ? lineTxt + ' ' + word : word;
    if (textWidth(test) > maxW && lineTxt) {
      text(lineTxt, x, yy);
      lineTxt = word;
      yy += lineH;
    } else {
      lineTxt = test;
    }
  }
  if (lineTxt) { text(lineTxt, x, yy); yy += lineH; }
  return yy;
}

function countCorrect() {
  return results.filter(r => r).length;
}

// ---------- quiz logic ----------

function toggleMode() {
  if (mode === 'explore') {
    mode = 'quiz';
    tIndex = 0;
    results = [];
    submitted = false;
    finished = false;
  } else {
    mode = 'explore';
  }
  for (const b of boxes) b.checked(false);
  updateControlStates();
}

function submitAnswer() {
  if (mode !== 'quiz' || submitted || finished) return;
  const t = TOPICS[tIndex];
  const marked = FILTERS.filter((f, i) => boxes[i].checked()).map(f => f[0]);
  const extra = marked.filter(id => !t.answer.includes(id));
  const missed = t.answer.filter(id => !marked.includes(id));
  const correct = extra.length === 0 && missed.length === 0;
  results[tIndex] = correct;
  feedbackCorrect = correct;
  const names = t.answer.length ? t.answer.join(', ') : 'none';
  let detail = '';
  if (extra.length) detail += ' You marked ' + extra.join(', ') + ', which ' + (extra.length > 1 ? 'do' : 'does') + ' not select it.';
  if (missed.length) detail += ' You missed ' + missed.join(', ') + '.';
  feedback = correct ? 'Correct: ' + t.why : 'Not quite. The filters that select it are ' + names + ': ' + t.why + detail;
  submitted = true;
  updateControlStates();
}

function nextTopic() {
  if (!submitted) return;
  if (tIndex === TOPICS.length - 1) finished = true;
  else { tIndex++; submitted = false; }
  for (const b of boxes) b.checked(false);
  updateControlStates();
}

function setEnabled(el, on) {
  const input = el.elt.querySelector('input');
  (input || el.elt).disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  const answering = quiz && !submitted && !finished;
  for (const b of boxes) setEnabled(b, answering);
  setEnabled(submitButton, answering);
  modeButton.html(quiz ? 'Back to explore' : 'Start the 8 topics');
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(tIndex === TOPICS.length - 1 ? 'See score' : 'Next topic');
  setEnabled(tryInput, !quiz);
  positionControls();
}

function layoutRow(elems, x, y, gap) {
  for (const el of elems) {
    el.position(x, y);
    x += el.elt.offsetWidth + gap;
  }
  return x;
}

function positionControls() {
  layoutRow([...boxes, submitButton], 10, drawHeight + 9, 12);
  layoutRow([modeButton, nextButton, tryLabel, tryInput], 10, drawHeight + 44, 10);
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  positionControls();
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = Math.floor(container.getBoundingClientRect().width);
}
