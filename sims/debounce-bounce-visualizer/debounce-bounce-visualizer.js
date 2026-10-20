// Button Bounce and Debounce Visualizer - p5.js MicroSim
// CANVAS_HEIGHT: 520
// Execute the debounce rule on recorded pin traces. The pin is sampled every
// 5 ms (1 = released, 0 = down). A change is accepted only when the state
// differs from the accepted state AND more than the debounce time has passed
// since the last accepted change; a change to "pressed" counts one press.
// This is the logic of the debounce in src/kits/study-buddy-base/03-buttons.py.
// The traces are illustrative.

let canvasWidth = 800;
let drawHeight = 440;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 20;
let sliderLeftMargin = 230;
let defaultTextSize = 16;

const SAMPLE_MS = 5;
const TRACES = {
  A: { s: [1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1], d: 'A clean press' },
  B: { s: [1,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0], d: 'Press with 20 ms of bounce' },
  C: { s: [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1,1,1,1,1,1,1,1,1], d: 'Clean press, then a bouncy release' },
  D: { s: [1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1], d: 'Two real presses 40 ms apart' },
  E: { s: [1,0,1,0,1,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0], d: 'A noisy switch that chatters for 55 ms' }
};
const ITEMS = [
  { trace: 'A', deb: 30,  answer: 1, why: 'A clean press has no bounce, so one press is counted.' },
  { trace: 'B', deb: 0,   answer: 3, why: 'With no debounce every flicker to 0 counts: at 10, 20, and 30 ms.' },
  { trace: 'B', deb: 30,  answer: 1, why: 'The press is accepted at 10 ms and the flicker up to 30 ms is ignored.' },
  { trace: 'D', deb: 100, answer: 1, why: 'The release at 50 ms is ignored because it is within 100 ms of the press at 10 ms, so the second press is never separate.' },
  { trace: 'E', deb: 30,  answer: 2, why: 'The chatter lasts 55 ms, which is longer than 30 ms, so a later flicker is counted as a second press at 75 ms.' },
  { trace: 'C', deb: 10,  answer: 2, why: 'The bounce on release lasts longer than 10 ms, so the release is accepted and a second press is counted at 90 ms.' }
];

let mode = 'explore';       // 'explore' or 'quiz'
let itemIndex = 0;
let submitted = false;
let finished = false;
let results = [];
let feedback = '';
let feedbackCorrect = false;

let modeButton, answerInput, submitButton, nextButton, debounceSlider;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  modeButton = createButton('Start the 6 items');
  modeButton.mousePressed(toggleMode);
  answerInput = createInput('', 'number');
  answerInput.size(70);
  answerInput.attribute('min', '0');
  answerInput.attribute('placeholder', '?');
  answerInput.elt.addEventListener('keydown', e => { if (e.key === 'Enter') submitAnswer(); });
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next item');
  nextButton.mousePressed(nextItem);
  for (const el of [modeButton, answerInput, submitButton, nextButton]) el.style('font-size', '16px');

  debounceSlider = createSlider(0, 100, 30, 10);
  debounceSlider.size(canvasWidth - sliderLeftMargin - margin);

  positionControls();
  updateControlStates();

  describe('A pin trace sampled every 5 milliseconds, drawn as a square wave of 1 (released) and 0 (down). Accepted presses and releases are marked on the trace with the debounce window shaded after each one. In explore mode a slider sets the debounce time from 0 to 100 milliseconds; in the six-item quiz the learner types how many presses the rule counts.', LABEL);
}

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
  text('Button Bounce and Debounce Visualizer', canvasWidth / 2, 10);

  const view = currentView();
  textSize(16);
  fill('dimgray');
  let status;
  if (mode === 'explore') status = 'Explore: trace B (illustrative), debounce ' + view.deb + ' ms';
  else if (finished) status = 'All 6 items done   |   Score: ' + countCorrect() + ' of 6';
  else status = 'Item ' + (itemIndex + 1) + ' of 6: trace ' + view.trace + ' (illustrative), debounce ' + view.deb +
    ' ms   |   Score: ' + countCorrect() + ' of 6';
  text(status, canvasWidth / 2, 42);

  drawRule(margin, 68, canvasWidth - 2 * margin);
  const showMarks = mode === 'explore' || submitted;
  const run = runRule(TRACES[view.trace].s, view.deb);
  drawTrace(view, run, showMarks, 150, 190);
  drawBottomPanel(view, run, showMarks, margin, 352, canvasWidth - 2 * margin, drawHeight - 362);

  // control labels
  noStroke();
  fill(mode === 'explore' ? 'black' : 'silver');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Debounce time: ' + debounceSlider.value() + ' ms', 10, drawHeight + 58);
}

// the trace and debounce time currently on screen
function currentView() {
  if (mode === 'explore') return { trace: 'B', deb: debounceSlider.value() };
  const it = ITEMS[min(itemIndex, ITEMS.length - 1)];
  return { trace: it.trace, deb: it.deb };
}

// Execute the debounce rule exactly as in 03-buttons.py.
// Returns accepted changes, the status of every sample and the press count.
function runRule(samples, deb) {
  let pressed = false;
  let lastChange = -1e9;      // "long before 0 ms"
  let presses = 0;
  const accepted = [];
  const status = [];
  for (let k = 0; k < samples.length; k++) {
    const t = k * SAMPLE_MS;
    const isDown = samples[k] === 0;
    if (isDown !== pressed && t - lastChange > deb) {
      pressed = isDown;
      lastChange = t;
      if (isDown) presses++;
      accepted.push({ t: t, k: k, down: isDown, n: presses });
      status.push('accepted');
    } else if (isDown !== pressed) {
      status.push('ignored');
    } else {
      status.push('same');
    }
  }
  return { accepted: accepted, status: status, presses: presses };
}

function drawRule(x, y, w) {
  fill(255, 255, 255, 235);
  stroke('silver');
  rect(x, y, w, 72, 10);
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(16);
  textStyle(BOLD);
  text('Rule:', x + 10, y + 8);
  textStyle(NORMAL);
  drawWrapped('accept a change only if the pin state differs from the accepted state AND more than the debounce time has passed since the last accepted change. Each accepted change to "down" is one press.',
    x + 58, y + 8, w - 70, 20);
}

function drawTrace(view, run, showMarks, top, h) {
  const samples = TRACES[view.trace].s;
  const n = samples.length;
  const x0 = 70;
  const x1 = canvasWidth - margin - 10;
  const maxT = 160;                         // fixed time axis so traces compare
  const tx = t => x0 + (x1 - x0) * t / maxT;
  const yHigh = top + 40;
  const yLow = top + 120;

  // axis and time ticks
  stroke('silver');
  line(x0, yLow + 30, x1, yLow + 30);
  noStroke();
  fill('dimgray');
  textSize(14);
  textAlign(CENTER, TOP);
  for (let t = 0; t <= maxT; t += 20) {
    stroke('silver');
    line(tx(t), yLow + 26, tx(t), yLow + 34);
    noStroke();
    text(t, tx(t), yLow + 36);
  }
  textAlign(LEFT, TOP);
  text('time (ms)', x1 - 60, yLow + 54);
  textAlign(RIGHT, CENTER);
  textSize(15);
  fill('black');
  text('1 up', x0 - 10, yHigh);
  text('0 down', x0 - 10, yLow);

  // debounce windows: changes are ignored here
  if (showMarks && view.deb > 0) {
    noStroke();
    fill(255, 215, 0, 90);
    for (const a of run.accepted) {
      const xa = tx(a.t);
      const xb = tx(min(a.t + view.deb, maxT));
      rect(xa, yHigh - 22, xb - xa, yLow - yHigh + 44);
    }
  }

  // square wave (sample and hold)
  stroke('navy');
  strokeWeight(3);
  noFill();
  beginShape();
  for (let k = 0; k < n; k++) {
    const y = samples[k] === 1 ? yHigh : yLow;
    vertex(tx(k * SAMPLE_MS), y);
    vertex(tx((k + 1) * SAMPLE_MS), y);
  }
  endShape();
  strokeWeight(1);

  // sample dots: orange = a change the rule ignored
  for (let k = 0; k < n; k++) {
    const y = samples[k] === 1 ? yHigh : yLow;
    noStroke();
    if (showMarks && run.status[k] === 'ignored') fill('darkorange');
    else fill('navy');
    circle(tx(k * SAMPLE_MS), y, showMarks && run.status[k] === 'ignored' ? 10 : 6);
  }

  // accepted changes
  if (showMarks) {
    for (const a of run.accepted) {
      const x = tx(a.t);
      stroke(a.down ? 'green' : 'royalblue');
      strokeWeight(2);
      line(x, yHigh - 30, x, yLow + 20);
      strokeWeight(1);
      noStroke();
      fill(a.down ? 'green' : 'royalblue');
      textAlign(CENTER, BOTTOM);
      textSize(14);
      text(a.down ? 'press ' + a.n : 'release', x, yHigh - 30);
    }
  }
}

function drawBottomPanel(view, run, showMarks, x, y, w, h) {
  fill(255, 255, 255, 235);
  stroke('silver');
  rect(x, y, w, h, 10);
  noStroke();
  textAlign(LEFT, TOP);
  textSize(16);
  const pad = 10;
  let yy = y + 8;
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 5 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 6 on the first attempt. ' + (sc >= 5 ? 'Mastery reached.' : 'Mastery is 5 of 6.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('Items 4 (trace D, 100 ms) and 5 (trace E, 30 ms) break the rule in opposite ways. Which debounce time was too long, and which was too short?',
      x + pad, yy + 24, w - 2 * pad, 20);
    return;
  }
  if (mode === 'explore') {
    fill('black');
    text('Presses counted: ' + run.presses, x + pad, yy);
    fill('dimgray');
    drawWrapped('Green = accepted press, blue = accepted release, gold = debounce window, orange dot = change ignored. Move the slider, then press "Start the 6 items".',
      x + pad, yy + 22, w - 2 * pad, 20);
    return;
  }
  if (!submitted) {
    fill('navy');
    textStyle(ITALIC);
    text('How many presses does the rule count?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Step through the samples by hand, type a whole number below, and press Submit. One attempt per item.',
      x + pad, yy + 22, w - 2 * pad, 20);
    return;
  }
  fill(feedbackCorrect ? 'darkgreen' : 'firebrick');
  textStyle(BOLD);
  drawWrapped(feedback, x + pad, yy, w - 2 * pad, 20);
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
    itemIndex = 0;
    results = [];
    submitted = false;
    finished = false;
  } else {
    mode = 'explore';
  }
  answerInput.value('');
  updateControlStates();
}

function submitAnswer() {
  if (mode !== 'quiz' || submitted || finished) return;
  const raw = answerInput.value().trim();
  if (raw === '' || isNaN(Number(raw))) return;
  const it = ITEMS[itemIndex];
  const correct = Number(raw) === it.answer;
  results[itemIndex] = correct;
  feedbackCorrect = correct;
  feedback = correct ? 'Correct: ' + it.why : 'Not quite. The rule counts ' + it.answer + ': ' + it.why;
  submitted = true;
  updateControlStates();
}

function nextItem() {
  if (!submitted) return;
  if (itemIndex === ITEMS.length - 1) finished = true;
  else { itemIndex++; submitted = false; }
  answerInput.value('');
  updateControlStates();
}

function setEnabled(el, on) {
  el.elt.disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  modeButton.html(quiz ? 'Back to explore' : 'Start the 6 items');
  setEnabled(answerInput, quiz && !submitted && !finished);
  setEnabled(submitButton, quiz && !submitted && !finished);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(itemIndex === ITEMS.length - 1 ? 'See score' : 'Next item');
  setEnabled(debounceSlider, !quiz);
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
  layoutRow([modeButton, answerInput, submitButton, nextButton], 10, drawHeight + 8, 10);
  debounceSlider.position(sliderLeftMargin, drawHeight + 48);
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  debounceSlider.size(canvasWidth - sliderLeftMargin - margin);
  positionControls();
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = Math.floor(container.getBoundingClientRect().width);
}
