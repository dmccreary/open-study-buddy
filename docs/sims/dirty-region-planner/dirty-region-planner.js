// Dirty Region Planner - p5.js MicroSim
// CANVAS_HEIGHT: 550
// Apply the dirty-region rule: for each device event, choose exactly the
// display regions whose content changes, then compare the bytes sent with a
// full 259,200-byte frame. Region positions and byte sizes come from the
// Chapter 6 table "Region Layout". The six events are illustrative.

let canvasWidth = 800;
let drawHeight = 470;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

const FULL_FRAME = 259200;   // 360 x 360 pixels x 2 bytes (RGB565)
const ALL_FIVE = 50752;      // all five regions redrawn together

// Region Layout table (x, y, width, height in display pixels)
const REGIONS = [
  { name: 'Status bar',    x: 120, y: 30,  w: 120, h: 20, bytes: 4800 },
  { name: 'Time',          x: 130, y: 72,  w: 100, h: 32, bytes: 6400 },
  { name: 'Mascot',        x: 148, y: 112, w: 64,  h: 64, bytes: 8192 },
  { name: 'Spectrum',      x: 80,  y: 190, w: 200, h: 40, bytes: 16000 },
  { name: 'Agent message', x: 60,  y: 240, w: 240, h: 32, bytes: 15360 }
];

// The six events, in a fixed order. dirty = indexes into REGIONS.
const EVENTS = [
  { text: 'A new audio frame arrives and the spectrum values are different from the last frame.',
    dirty: [3], why: 'Only the spectrum content changed.' },
  { text: 'The clock minute changes from 12:34 to 12:35.',
    dirty: [1], why: 'Only the clock digits changed.' },
  { text: 'The Pico connects to Wi-Fi and the status icon changes.',
    dirty: [0], why: 'The icon lives in the status bar.' },
  { text: "The student presses Mode and the device enters Listening mode, which changes the mascot's pose and the status text.",
    dirty: [0, 2], why: 'Both the pose and the status text changed.' },
  { text: 'The agent replies "Test on Friday" and the mascot switches to a speaking pose.',
    dirty: [2, 4], why: 'The words and the pose changed.' },
  { text: 'A silent room produces an audio frame whose spectrum values equal the last frame.',
    dirty: [], why: 'Nothing changed, so nothing is sent.' }
];

// quiz state
let eventIndex = 0;
let submitted = false;
let finished = false;
let results = [];          // true/false for each event's first (only) attempt
let chosenSets = [];       // the learner's selection for each event
let feedback = '';
let feedbackCorrect = false;

// controls
let regionBoxes = [];
let submitButton, nextButton, restartButton;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  for (let i = 0; i < REGIONS.length; i++) {
    const cb = createCheckbox(' ' + REGIONS[i].name, false);
    cb.style('font-size', '16px');
    regionBoxes.push(cb);
  }
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next event');
  nextButton.mousePressed(nextEvent);
  restartButton = createButton('Start over');
  restartButton.mousePressed(restart);
  for (const b of [submitButton, nextButton, restartButton]) b.style('font-size', '16px');

  positionControls();
  updateControlStates();

  describe('A round 360 by 360 display divided into five regions: status bar, time, mascot, spectrum and agent message, each labeled with its size in bytes. For each of six events the learner ticks the regions that must be redrawn and submits; the sim then colors the correct regions and compares the bytes sent with a full 259,200-byte frame.', LABEL);
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
  text('Dirty Region Planner', canvasWidth / 2, 10);
  textSize(16);
  fill('dimgray');
  const shown = finished ? 'All 6 events done' : 'Event ' + (eventIndex + 1) + ' of 6 (illustrative)';
  text(shown + '   |   Score: ' + countCorrect() + ' of 6', canvasWidth / 2, 42);

  const leftW = max(230, canvasWidth * 0.45);
  const D = min(leftW - 30, drawHeight - 75 - 55);
  drawDisplay((leftW - D) / 2, 78, D);
  drawLegend(leftW / 2, 78 + D + 14);

  const px = leftW + 5;
  const pw = canvasWidth - px - margin;
  if (finished) drawSummary(px, 72, pw, drawHeight - 82);
  else drawEventPanel(px, 72, pw, drawHeight - 82);

  // control-region label
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Redraw:', 10, drawHeight + 20);
}

// ---------- drawing helpers ----------

function selectedSet() {
  const s = [];
  for (let i = 0; i < regionBoxes.length; i++) if (regionBoxes[i].checked()) s.push(i);
  return s;
}

function bytesOf(set) {
  return set.reduce((sum, i) => sum + REGIONS[i].bytes, 0);
}

function drawDisplay(x0, y0, D) {
  const s = D / 360;
  const cx = x0 + D / 2;
  const cy = y0 + D / 2;
  noStroke();
  fill('dimgray');
  circle(cx, cy, D + 14);
  fill('black');
  circle(cx, cy, D);
  // the safe circle of radius 168 around (180, 180)
  noFill();
  stroke('gray');
  drawingContext.setLineDash([4, 4]);
  circle(cx, cy, 2 * 168 * s);
  drawingContext.setLineDash([]);

  const sel = selectedSet();
  const dirty = EVENTS[eventIndex].dirty;
  for (let i = 0; i < REGIONS.length; i++) {
    const r = REGIONS[i];
    const isSel = sel.includes(i);
    const isDirty = dirty.includes(i);
    let fillCol = 'slategray';
    let textCol = 'white';
    let tag = '';
    if (!submitted || finished) {
      if (isSel && !finished) { fillCol = 'gold'; textCol = 'black'; }
    } else if (isDirty && isSel) { fillCol = 'seagreen'; tag = 'redraw'; }
    else if (isDirty) { fillCol = 'darkorange'; textCol = 'black'; tag = 'missed'; }
    else if (isSel) { fillCol = 'firebrick'; tag = 'not needed'; }
    stroke('white');
    strokeWeight(1);
    fill(fillCol);
    rect(x0 + r.x * s, y0 + r.y * s, r.w * s, r.h * s, 3);

    // label: name and bytes, sized to fit the rectangle
    noStroke();
    fill(textCol);
    textAlign(CENTER, CENTER);
    const ts = constrain(r.h * s * 0.6, 11, 14);
    textSize(ts);
    const rx = x0 + (r.x + r.w / 2) * s;
    const ry = y0 + (r.y + r.h / 2) * s;
    const bytesTxt = r.bytes.toLocaleString('en-US') + ' B';
    let line1 = r.name + ' ' + bytesTxt;
    if (tag) line1 = r.name + ': ' + tag;
    if (r.h * s >= 50) {
      text(r.name, rx, ry - ts * 0.7);
      text(tag || bytesTxt, rx, ry + ts * 0.7);
    } else if (textWidth(line1) < r.w * s - 4) {
      text(line1, rx, ry);
    } else {
      text(r.name, rx, ry);
    }
  }
}

function drawLegend(cx, y) {
  noStroke();
  textAlign(CENTER, TOP);
  textSize(14);
  fill('dimgray');
  if (submitted && !finished) {
    text('green: needed and chosen   orange: needed, missed', cx, y);
    text('red: chosen but not needed   gray: unchanged', cx, y + 18);
  } else {
    text('gold = regions you chose to redraw', cx, y);
    text('dashed circle = the visible (safe) area', cx, y + 18);
  }
}

function infoPanel(x, y, w, h) {
  fill(255, 255, 255, 235);
  stroke('silver');
  strokeWeight(1);
  rect(x, y, w, h, 10);
}

function drawEventPanel(x, y, w, h) {
  infoPanel(x, y, w, h);
  const pad = 12;
  const tw = w - 2 * pad;
  let yy = y + pad;
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(16);
  textStyle(BOLD);
  text('Event ' + (eventIndex + 1) + ' (illustrative)', x + pad, yy);
  textStyle(NORMAL);
  yy += 24;
  yy = drawWrapped(EVENTS[eventIndex].text, x + pad, yy, tw, 21);
  yy += 6;
  fill('navy');
  textStyle(ITALIC);
  text('Which regions must be redrawn?', x + pad, yy);
  textStyle(NORMAL);
  yy += 28;

  const sel = submitted ? chosenSets[eventIndex] : selectedSet();
  const bytes = bytesOf(sel);
  fill('black');
  yy = drawWrapped('Your choice: ' + setName(sel), x + pad, yy, tw, 21);
  text('Bytes sent: ' + bytes.toLocaleString('en-US') + ' (' + pct(bytes) + '% of a full frame)', x + pad, yy);
  yy += 30;
  yy = drawBytesBar(x + pad, yy, tw, bytes);
  yy += 8;

  if (submitted) {
    fill(feedbackCorrect ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    yy = drawWrapped(feedback, x + pad, yy, tw, 21);
    textStyle(NORMAL);
    fill('black');
    const ans = bytesOf(EVENTS[eventIndex].dirty);
    drawWrapped('Saving versus a full frame: ' + (FULL_FRAME - ans).toLocaleString('en-US') + ' bytes.', x + pad, yy + 4, tw, 21);
  } else {
    fill('dimgray');
    drawWrapped('Tick the regions below (none is allowed), then press Submit. You get one attempt per event.', x + pad, yy, tw, 21);
  }
}

// bar comparing bytes sent with the full frame and with all five regions
function drawBytesBar(x, y, w, bytes) {
  const bh = 18;
  stroke('silver');
  fill('whitesmoke');
  rect(x, y, w, bh);
  noStroke();
  fill(submitted ? 'steelblue' : 'gold');
  rect(x, y, w * bytes / FULL_FRAME, bh);
  // marker for all five regions
  const mx = x + w * ALL_FIVE / FULL_FRAME;
  stroke('black');
  strokeWeight(2);
  line(mx, y - 4, mx, y + bh + 4);
  strokeWeight(1);
  noStroke();
  fill('dimgray');
  textSize(14);
  textAlign(LEFT, TOP);
  text('all five regions: 50,752', mx + 4, y + bh + 3);
  textAlign(RIGHT, TOP);
  text('full frame: 259,200', x + w, y + bh + 3);
  textAlign(LEFT, TOP);
  textSize(16);
  return y + bh + 24;
}

function drawSummary(x, y, w, h) {
  infoPanel(x, y, w, h);
  const pad = 12;
  let yy = y + pad;
  const score = countCorrect();
  noStroke();
  textAlign(LEFT, TOP);
  textSize(18);
  textStyle(BOLD);
  fill(score >= 5 ? 'darkgreen' : 'firebrick');
  text('Score: ' + score + ' of 6 on the first attempt', x + pad, yy);
  textStyle(NORMAL);
  yy += 26;
  textSize(16);
  fill('black');
  yy = drawWrapped(score >= 5 ? 'Mastery reached (5 of 6 or better).' :
    'Mastery is 5 of 6. Press Start over to try the events again.', x + pad, yy, w - 2 * pad, 21);
  yy += 8;
  textStyle(BOLD);
  text('Event   Bytes sent   Your answer', x + pad, yy);
  textStyle(NORMAL);
  yy += 24;
  for (let i = 0; i < EVENTS.length; i++) {
    const b = bytesOf(EVENTS[i].dirty);
    fill(results[i] ? 'darkgreen' : 'firebrick');
    text('  ' + (i + 1), x + pad, yy);
    fill('black');
    text(b.toLocaleString('en-US'), x + pad + 70, yy);
    fill(results[i] ? 'darkgreen' : 'firebrick');
    text(results[i] ? 'correct' : 'not quite', x + pad + 175, yy);
    yy += 22;
  }
  yy += 8;
  fill('navy');
  drawWrapped('Which event sent nothing? Which cost the most, and how does it compare with 259,200 bytes?', x + pad, yy, w - 2 * pad, 21);
}

// draws word-wrapped text from (x, y) and returns the y below the last line
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

function setName(set) {
  if (set.length === 0) return 'none';
  return set.map(i => REGIONS[i].name).join(' and ');
}

function pct(bytes) {
  return (100 * bytes / FULL_FRAME).toFixed(1);
}

function countCorrect() {
  return results.filter(r => r).length;
}

// ---------- quiz logic ----------

function submitAnswer() {
  if (submitted || finished) return;
  const sel = selectedSet();
  const ev = EVENTS[eventIndex];
  const correct = sel.length === ev.dirty.length && ev.dirty.every(i => sel.includes(i));
  results[eventIndex] = correct;
  chosenSets[eventIndex] = sel;
  const bytes = bytesOf(ev.dirty);
  feedbackCorrect = correct;
  feedback = correct
    ? 'Correct: ' + ev.why + ' (' + bytes.toLocaleString('en-US') + ' bytes, ' + pct(bytes) + '% of a full frame)'
    : 'Not quite. The dirty regions are ' + setName(ev.dirty) + ': ' + ev.why;
  submitted = true;
  updateControlStates();
}

function nextEvent() {
  if (!submitted) return;
  if (eventIndex === EVENTS.length - 1) {
    finished = true;
  } else {
    eventIndex++;
    submitted = false;
    for (const cb of regionBoxes) cb.checked(false);
  }
  updateControlStates();
}

function restart() {
  eventIndex = 0;
  submitted = false;
  finished = false;
  results = [];
  chosenSets = [];
  for (const cb of regionBoxes) cb.checked(false);
  updateControlStates();
}

function setEnabled(el, on) {
  const input = el.elt.querySelector('input');
  (input || el.elt).disabled = !on;
}

function updateControlStates() {
  for (const cb of regionBoxes) setEnabled(cb, !submitted && !finished);
  setEnabled(submitButton, !submitted && !finished);
  setEnabled(nextButton, submitted && !finished);
  nextButton.html(eventIndex === EVENTS.length - 1 ? 'See score' : 'Next event');
  positionControls();
}

// place a row of controls left to right, using each element's real width
function layoutRow(elems, x, y, gap) {
  for (const el of elems) {
    el.position(x, y);
    x += el.elt.offsetWidth + gap;
  }
  return x;
}

function positionControls() {
  layoutRow(regionBoxes, 80, drawHeight + 9, 14);
  layoutRow([submitButton, nextButton, restartButton], 10, drawHeight + 44, 10);
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
