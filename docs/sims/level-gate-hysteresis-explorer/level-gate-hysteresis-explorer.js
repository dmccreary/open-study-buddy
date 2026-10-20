// Level Gate Hysteresis Explorer - p5.js MicroSim
// CANVAS_HEIGHT: 585
// Calculate how many times two gates change state on a loudness trace.
// Single-threshold gate: open when bits >= open level.
// Hysteresis gate: starts closed, opens when bits >= open level, and closes
// only when bits < close level. A state change is any frame whose open/closed
// state differs from the frame before it (the state before frame 0 is closed).
// Same rules as levels.LevelGate in src/chapters/11-mic-calibration-push-to-talk.
// All traces are synthetic.

let canvasWidth = 800;
let drawHeight = 470;
let controlHeight = 115;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

const TRACES = {
  A: [14.8, 15.1, 14.9, 15.2, 14.7, 15.0, 14.9, 15.3, 14.6, 15.1, 15.4, 15.6, 15.2, 14.9, 15.1, 14.8, 14.2, 13.4, 13.2, 13.5],
  B: [13.0, 13.1, 15.6, 16.8, 17.2, 14.8, 16.9, 17.4, 15.2, 14.6, 16.5, 17.0, 16.2, 14.4, 13.2, 13.0, 13.1, 12.9, 13.0, 13.1],
  C: [13.0, 13.4, 14.2, 13.6, 14.9, 13.2, 15.1, 13.3, 14.7, 13.1, 14.4, 13.2, 14.8, 13.0, 13.3, 13.1, 13.0, 13.2, 13.1, 13.0]
};
const CHALLENGES = [
  { trace: 'A', open: 15.0, close: 14.5, single: 12, hyst: 2,
    why: 'The level crosses 15.0 twelve times, but it never falls below 14.5 until frame 16, so the gate opens at frame 1 and closes at frame 16.' },
  { trace: 'B', open: 15.0, close: 14.5, single: 6, hyst: 2,
    why: 'Dips to 14.8 and 14.6 inside the phrase flip the single threshold, but they stay above 14.5. The gate opens at frame 2 and closes at frame 13, when 14.4 is below 14.5.' },
  { trace: 'C', open: 14.5, close: 14.0, single: 8, hyst: 8,
    why: 'Each spike (14.9, 15.1, 14.7, 14.8) rises over 14.5 and then falls to 13.6 or lower, below the close level, so both gates open and close four times. Hysteresis helps only with wobble near the line.' }
];

let mode = 'explore';
let chIndex = 0;
let submitted = false;
let finished = false;
let answersRight = 0;     // out of 6 (two answers per challenge)
let feedback = '';
let feedbackCorrect = false;

let modeButton, singleLabel, singleInput, hystLabel, hystInput, submitButton, nextButton;
let traceLabel, traceSelect, openSlider, closeSlider;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  modeButton = createButton('Start the 3 challenges');
  modeButton.mousePressed(toggleMode);
  singleLabel = createSpan('Single changes:');
  singleInput = createInput('', 'number');
  singleInput.size(60);
  hystLabel = createSpan('Hysteresis changes:');
  hystInput = createInput('', 'number');
  hystInput.size(60);
  hystInput.elt.addEventListener('keydown', e => { if (e.key === 'Enter') submitAnswer(); });
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next challenge');
  nextButton.mousePressed(nextChallenge);
  traceLabel = createSpan('Trace:');
  traceSelect = createSelect();
  for (const t of ['A', 'B', 'C']) traceSelect.option(t);
  for (const el of [modeButton, singleLabel, singleInput, hystLabel, hystInput, submitButton, nextButton, traceLabel, traceSelect]) {
    el.style('font-size', '16px');
  }
  openSlider = createSlider(13.0, 18.0, 15.0, 0.1);
  closeSlider = createSlider(12.0, 18.0, 14.5, 0.1);
  // keep close <= open: a lower open level drags the close level down with it
  openSlider.input(() => { if (Number(closeSlider.value()) > Number(openSlider.value())) closeSlider.value(openSlider.value()); });
  closeSlider.input(() => { if (Number(closeSlider.value()) > Number(openSlider.value())) closeSlider.value(openSlider.value()); });

  positionControls();
  updateControlStates();

  describe('A line plot of loudness in bits over 20 frames, with an open level and a lower close level drawn as dashed lines. Below the plot two rows of cells show, frame by frame, when a single-threshold gate and a hysteresis gate are open, with each state change marked and counted. Sliders set the two levels; a three-challenge quiz asks for both change counts.', LABEL);
}

// ---------- gate rules ----------

function singleGate(tr, open) {
  return tr.map(v => v >= open - 1e-9);
}

function hysteresisGate(tr, open, close) {
  let st = false;
  return tr.map(v => {
    if (!st && v >= open - 1e-9) st = true;
    else if (st && v < close - 1e-9) st = false;
    return st;
  });
}

function changeFrames(states) {
  const out = [];
  let prev = false;
  states.forEach((s, i) => { if (s !== prev) out.push(i); prev = s; });
  return out;
}

function currentView() {
  if (mode === 'quiz') {
    const c = CHALLENGES[min(chIndex, 2)];
    return { trace: c.trace, open: c.open, close: c.close };
  }
  return { trace: traceSelect.value(), open: Number(openSlider.value()), close: Number(closeSlider.value()) };
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
  text('Level Gate Hysteresis Explorer', canvasWidth / 2, 10);
  const v = currentView();
  textSize(16);
  fill('dimgray');
  let status = 'Trace ' + v.trace + ' (synthetic), open ' + v.open.toFixed(1) + ', close ' + v.close.toFixed(1);
  if (mode === 'quiz') status = (finished ? 'All 3 challenges done' : 'Challenge ' + (chIndex + 1) + ' of 3') +
    '   |   Score: ' + answersRight + ' of 6   |   ' + status;
  text(status, canvasWidth / 2, 42);

  const tr = TRACES[v.trace];
  const s = singleGate(tr, v.open);
  const h = hysteresisGate(tr, v.open, v.close);
  const reveal = mode === 'explore' || submitted;
  const x0 = 150;
  const x1 = canvasWidth - 25;
  drawPlot(tr, v, x0, x1, 72, 200);
  drawGateRow('Single threshold', s, reveal, x0, x1, 312);
  drawGateRow('Hysteresis gate', h, reveal, x0, x1, 344);
  drawPanel(s, h, margin, 382, canvasWidth - 2 * margin, drawHeight - 390);

  noStroke();
  fill(mode === 'explore' ? 'black' : 'silver');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  const half = canvasWidth / 2;
  text('Open: ' + Number(openSlider.value()).toFixed(1), 10, drawHeight + 98);
  text('Close: ' + Number(closeSlider.value()).toFixed(1), half + 10, drawHeight + 98);
}

function drawPlot(tr, v, x0, x1, top, h) {
  const lo = 12;
  const hi = 18;
  const cw = (x1 - x0) / tr.length;
  const X = i => x0 + (i + 0.5) * cw;
  const Y = b => top + h - h * (b - lo) / (hi - lo);
  textSize(14);
  for (let b = lo; b <= hi; b++) {
    stroke('gainsboro');
    line(x0, Y(b), x1, Y(b));
    noStroke();
    fill('dimgray');
    textAlign(RIGHT, CENTER);
    text(b, x0 - 6, Y(b));
  }
  textAlign(RIGHT, CENTER);
  fill('black');
  text('loudness', x0 - 30, top + h / 2 - 9);
  text('(bits)', x0 - 30, top + h / 2 + 9);
  for (let i = 0; i < tr.length; i += 1) {
    fill('dimgray');
    noStroke();
    textAlign(CENTER, TOP);
    if (i % 2 === 0) text(i, X(i), top + h + 4);
  }
  textAlign(LEFT, TOP);
  text('frame', x1 - 40, top + h + 20);
  // the two levels
  drawLevel(Y(v.open), x0, x1, 'seagreen', 'open ' + v.open.toFixed(1), -1);
  drawLevel(Y(v.close), x0, x1, 'darkorange', 'close ' + v.close.toFixed(1), 1);
  // the trace
  stroke('navy');
  strokeWeight(2);
  noFill();
  beginShape();
  tr.forEach((b, i) => vertex(X(i), Y(b)));
  endShape();
  strokeWeight(1);
  noStroke();
  fill('navy');
  tr.forEach((b, i) => circle(X(i), Y(b), 7));
}

function drawLevel(y, x0, x1, col, lbl, side) {
  stroke(col);
  strokeWeight(2);
  drawingContext.setLineDash([7, 5]);
  line(x0, y, x1, y);
  drawingContext.setLineDash([]);
  strokeWeight(1);
  noStroke();
  fill(col);
  textSize(14);
  textAlign(RIGHT, side < 0 ? BOTTOM : TOP);
  text(lbl, x1, y + side * 2);
}

function drawGateRow(label, states, reveal, x0, x1, y) {
  const cw = (x1 - x0) / states.length;
  noStroke();
  fill('black');
  textAlign(RIGHT, CENTER);
  textSize(15);
  text(label, x0 - 8, y + 12);
  const changes = changeFrames(states);
  for (let i = 0; i < states.length; i++) {
    stroke('silver');
    fill(reveal ? (states[i] ? 'seagreen' : 'white') : 'gainsboro');
    rect(x0 + i * cw + 1, y, cw - 2, 24, 3);
    if (reveal && changes.includes(i)) {
      noStroke();
      fill('crimson');
      triangle(x0 + i * cw + cw / 2 - 5, y - 8, x0 + i * cw + cw / 2 + 5, y - 8, x0 + i * cw + cw / 2, y - 1);
    }
  }
  if (!reveal) {
    noStroke();
    fill('dimgray');
    textAlign(CENTER, CENTER);
    textSize(14);
    text('hidden until you submit', (x0 + x1) / 2, y + 12);
  }
}

function drawPanel(s, h, x, y, w, ph) {
  fill(255, 255, 255, 235);
  stroke('silver');
  rect(x, y, w, ph, 10);
  const pad = 10;
  const tw = w - 2 * pad;
  const yy = y + 8;
  noStroke();
  textAlign(LEFT, TOP);
  textSize(16);
  const ns = changeFrames(s).length;
  const nh = changeFrames(h).length;
  if (mode === 'explore') {
    fill('navy');
    textStyle(ITALIC);
    text('Which gate flutters?', x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('Green = open, red mark = a change. Single threshold: ' + ns + ' changes. Hysteresis: ' + nh +
      ' changes. Raise the close level up to the open level and compare the rows.', x + pad, yy + 22, tw, 20);
    return;
  }
  if (finished) {
    fill(answersRight >= 5 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + answersRight + ' of 6. ' + (answersRight >= 5 ? 'Mastery reached.' : 'Mastery is 5 of 6.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('In challenge 3 hysteresis did not help. What kind of noise does it remove, and what kind does it let through?', x + pad, yy + 24, tw, 20);
    return;
  }
  if (!submitted) {
    fill('navy');
    textStyle(ITALIC);
    text('How many times does each gate change state?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Trace both gates frame by frame (the state before frame 0 is closed). Type the two counts below and press Submit. One attempt.', x + pad, yy + 22, tw, 20);
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

// ---------- quiz logic ----------

function toggleMode() {
  if (mode === 'explore') {
    mode = 'quiz';
    chIndex = 0;
    answersRight = 0;
    submitted = false;
    finished = false;
  } else {
    mode = 'explore';
  }
  singleInput.value('');
  hystInput.value('');
  updateControlStates();
}

function submitAnswer() {
  if (mode !== 'quiz' || submitted || finished) return;
  const a = singleInput.value().trim();
  const b = hystInput.value().trim();
  if (a === '' || b === '' || isNaN(Number(a)) || isNaN(Number(b))) return;
  const c = CHALLENGES[chIndex];
  const okA = Number(a) === c.single;
  const okB = Number(b) === c.hyst;
  answersRight += (okA ? 1 : 0) + (okB ? 1 : 0);
  feedbackCorrect = okA && okB;
  feedback = feedbackCorrect ? 'Correct: ' + c.why :
    'Not quite. The counts are ' + c.single + ' and ' + c.hyst + ': ' + c.why;
  submitted = true;
  updateControlStates();
}

function nextChallenge() {
  if (!submitted) return;
  if (chIndex === CHALLENGES.length - 1) finished = true;
  else { chIndex++; submitted = false; }
  singleInput.value('');
  hystInput.value('');
  updateControlStates();
}

function setEnabled(el, on) {
  el.elt.disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  const answering = quiz && !submitted && !finished;
  modeButton.html(quiz ? 'Back to explore' : 'Start the 3 challenges');
  setEnabled(singleInput, answering);
  setEnabled(hystInput, answering);
  setEnabled(submitButton, answering);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(chIndex === CHALLENGES.length - 1 ? 'See score' : 'Next challenge');
  for (const el of [traceSelect, openSlider, closeSlider]) setEnabled(el, !quiz);
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
  layoutRow([modeButton, submitButton, nextButton, traceLabel, traceSelect], 10, drawHeight + 8, 10);
  layoutRow([singleLabel, singleInput, hystLabel, hystInput], 10, drawHeight + 46, 8);
  const half = canvasWidth / 2;
  openSlider.position(100, drawHeight + 88);
  openSlider.size(half - 100 - 20);
  closeSlider.position(half + 100, drawHeight + 88);
  closeSlider.size(half - 100 - margin);
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
