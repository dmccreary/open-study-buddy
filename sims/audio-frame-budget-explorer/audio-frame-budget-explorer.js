// Audio Frame Time Budget Explorer - p5.js MicroSim
// CANVAS_HEIGHT: 550
// Examine loop timings against the 40 ms audio-frame budget. One frame is
// 2,048 bytes (512 samples) and arrives every 40 ms. The ring holds
// 9.765625 frames (a depth measured on one test board). Each pass of the loop
// takes P ms of work and then reads one frame; a loop faster than 40 ms waits.
// Rules: T = max(P, 40). Backlog after n passes = n x (T/40 - 1) frames.
// The first sample is lost at the first whole n with backlog > 9.765625,
// at time n x T. This is a model, based on one board's measurement.

let canvasWidth = 800;
let drawHeight = 470;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let sliderLeftMargin = 250;
let defaultTextSize = 16;

const FRAME_MS = 40;
const RING_FRAMES = 9.765625;   // 40,000 bytes at 8 bytes per sample time
const TIMINGS = [
  { p: 30,  answer: 'never', why: 'The loop is faster than 40 ms, so it waits for each frame and the backlog stays at zero.' },
  { p: 40,  answer: 'never', why: 'The loop exactly matches the audio rate, so there is no growth.' },
  { p: 45,  answer: 3.56, why: 'Growth 0.125 frames per pass, so it passes 9.77 frames on pass 79, and 79 x 45 ms = 3.56 s.' },
  { p: 50,  answer: 2.0,  why: 'Growth 0.25 frames per pass, so it passes 9.77 on pass 40, and 40 x 50 ms = 2.0 s.' },
  { p: 60,  answer: 1.2,  why: 'Growth 0.5 frames per pass, so it passes 9.77 on pass 20, and 20 x 60 ms = 1.2 s.' },
  { p: 130, answer: 0.65, why: 'Growth 2.25 frames per pass, so it passes 9.77 on pass 5, and 5 x 130 ms = 0.65 s.' }
];

let mode = 'explore';
let timingIndex = 0;
let submitted = false;
let finished = false;
let results = [];
let feedback = '';
let feedbackCorrect = false;

let modeButton, answerInput, submitButton, nextButton, pSlider;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  modeButton = createButton('Start the 6 timings');
  modeButton.mousePressed(toggleMode);
  answerInput = createInput('');
  answerInput.size(140);
  answerInput.attribute('placeholder', 'seconds or never');
  answerInput.elt.addEventListener('keydown', e => { if (e.key === 'Enter') submitAnswer(); });
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next timing');
  nextButton.mousePressed(nextTiming);
  for (const el of [modeButton, answerInput, submitButton, nextButton]) el.style('font-size', '16px');

  pSlider = createSlider(10, 100, 40, 0.1);
  pSlider.size(canvasWidth - sliderLeftMargin - margin);

  positionControls();
  updateControlStates();

  describe('A pipeline of microphone, ring buffer and processing loop above a graph of the backlog in frames against time. A dashed line marks the ring capacity of 9.77 frames. A slider sets the time per loop pass from 10 to 100 milliseconds; when the pass is slower than 40 milliseconds the backlog rises in steps until it crosses the capacity, and the time of the first lost audio is marked.', LABEL);
}

// model: growth per pass, loss pass and loss time (s), or never.
// Named budgetModel because p5 already defines a global model() for 3D.
function budgetModel(p) {
  const T = max(p, FRAME_MS);
  const g = T / FRAME_MS - 1;
  if (g <= 1e-12) return { T: T, g: 0, never: true };
  const n = Math.floor(RING_FRAMES / g) + 1;   // first whole n with n*g > capacity
  return { T: T, g: g, never: false, n: n, t: Math.round(n * T / 10) / 100 };
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
  text('Audio Frame Time Budget Explorer', canvasWidth / 2, 10);
  textSize(16);
  fill('dimgray');
  let status;
  if (mode === 'explore') status = 'Explore: model, based on one board\'s measurement';
  else if (finished) status = 'All 6 timings done   |   Score: ' + countCorrect() + ' of 6';
  else status = 'Timing ' + (timingIndex + 1) + ' of 6: P = ' + TIMINGS[timingIndex].p + ' ms   |   Score: ' + countCorrect() + ' of 6';
  text(status, canvasWidth / 2, 42);

  const p = mode === 'explore' ? pSlider.value() : TIMINGS[min(timingIndex, 5)].p;
  const m = budgetModel(p);
  const showLine = mode === 'explore' || submitted;
  drawPipeline(p, 70);
  drawGraph(m, showLine, 70, 142, canvasWidth - 70 - 30, 175);
  drawInfoPanel(p, m, margin, 360, canvasWidth - 2 * margin, drawHeight - 370);

  noStroke();
  fill(mode === 'explore' ? 'black' : 'silver');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Time per pass P: ' + Number(pSlider.value()).toFixed(1) + ' ms', 10, drawHeight + 58);
}

function drawPipeline(p, y) {
  const boxes = [
    { t: 'Microphone', s: '1 frame (2,048 B) every 40 ms' },
    { t: 'Ring buffer', s: 'holds 9.77 frames (0.39 s)' },
    { t: 'Loop (P = ' + nf(p, 0, 1) + ' ms)', s: 'does P ms of work, reads 1 frame' }
  ];
  const gap = 34;
  const bw = (canvasWidth - 2 * margin - 2 * gap) / 3;
  for (let i = 0; i < 3; i++) {
    const x = margin + i * (bw + gap);
    stroke('steelblue');
    fill('white');
    rect(x, y, bw, 52, 8);
    noStroke();
    fill('navy');
    textAlign(CENTER, TOP);
    textStyle(BOLD);
    textSize(16);
    text(boxes[i].t, x + bw / 2, y + 6);
    textStyle(NORMAL);
    // shrink the subtitle until it fits inside the box
    let ts = 14;
    textSize(ts);
    while (textWidth(boxes[i].s) > bw - 10 && ts > 10) textSize(--ts);
    fill('black');
    text(boxes[i].s, x + bw / 2, y + 28);
    if (i < 2) {
      const ax = x + bw + 4;
      stroke('gray');
      strokeWeight(2);
      line(ax, y + 26, ax + gap - 10, y + 26);
      noStroke();
      fill('gray');
      triangle(ax + gap - 8, y + 26, ax + gap - 16, y + 21, ax + gap - 16, y + 31);
      strokeWeight(1);
    }
  }
}

function niceStep(range) {
  const target = range / 8;
  for (const s of [0.1, 0.2, 0.5, 1, 2, 5, 10, 20]) if (s >= target) return s;
  return 50;
}

function drawGraph(m, showLine, gx, gy, gw, gh) {
  const yMax = 12;
  let xMax = 4;
  if (showLine && !m.never) xMax = max(1, Math.ceil(m.t * 1.25 * 2) / 2);
  const X = s => gx + gw * s / xMax;
  const Y = f => gy + gh - gh * f / yMax;

  // grid and axes
  const xs = niceStep(xMax);
  textSize(14);
  for (let s = 0; s <= xMax + 1e-9; s += xs) {
    stroke('gainsboro');
    line(X(s), gy, X(s), gy + gh);
    noStroke();
    fill('dimgray');
    textAlign(CENTER, TOP);
    text(nf(s, 0, xs < 1 ? 1 : 0), X(s), gy + gh + 4);
  }
  for (let f = 0; f <= yMax; f += 2) {
    stroke('gainsboro');
    line(gx, Y(f), gx + gw, Y(f));
    noStroke();
    fill('dimgray');
    textAlign(RIGHT, CENTER);
    text(f, gx - 6, Y(f));
  }
  stroke('black');
  line(gx, gy, gx, gy + gh);
  line(gx, gy + gh, gx + gw, gy + gh);
  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  text('time since the loop started (s)', gx + gw / 2, gy + gh + 20);
  push();
  translate(gx - 42, gy + gh / 2);
  rotate(-HALF_PI);
  textAlign(CENTER, CENTER);
  text('backlog (frames)', 0, 0);
  pop();

  // ring capacity
  stroke('firebrick');
  strokeWeight(2);
  drawingContext.setLineDash([8, 5]);
  line(gx, Y(RING_FRAMES), gx + gw, Y(RING_FRAMES));
  drawingContext.setLineDash([]);
  strokeWeight(1);
  noStroke();
  fill('firebrick');
  textAlign(LEFT, BOTTOM);
  text('ring capacity 9.77 frames', gx + 6, Y(RING_FRAMES) - 3);

  if (!showLine) return;
  // backlog after each pass: a step line, one step per pass
  stroke('royalblue');
  strokeWeight(2.5);
  noFill();
  beginShape();
  vertex(X(0), Y(0));
  if (m.never) {
    vertex(X(xMax), Y(0));
  } else {
    const last = min(m.n, Math.floor(xMax * 1000 / m.T));
    let prev = 0;
    for (let k = 1; k <= last; k++) {
      const s = k * m.T / 1000;
      const b = min(k * m.g, yMax);
      vertex(X(s), Y(prev));
      vertex(X(s), Y(b));
      prev = b;
    }
  }
  endShape();
  strokeWeight(1);
  if (!m.never) {
    const lx = X(m.n * m.T / 1000);
    const ly = Y(min(m.n * m.g, yMax));
    const right = lx > gx + gw * 0.7;
    noStroke();
    fill('firebrick');
    circle(lx, ly, 12);
    textAlign(right ? RIGHT : LEFT, BOTTOM);
    textStyle(BOLD);
    text('first audio lost: pass ' + m.n + ', ' + m.t.toFixed(2) + ' s', lx + (right ? -10 : 10), ly - 6);
    textStyle(NORMAL);
  }
}

function drawInfoPanel(p, m, x, y, w, h) {
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
    fill('black');
    let s = 'T = max(P, 40) = ' + nf(m.T, 0, 1) + ' ms.   Growth per pass = T / 40 - 1 = ' + nf(m.g, 0, 4) + ' frames.   ';
    if (m.never) s += p < FRAME_MS ? 'The loop waits for each frame, so the backlog stays at 0: audio is never lost.' :
      'The loop matches the audio rate exactly: no growth, never lost.';
    else s += 'The backlog passes 9.77 frames on pass ' + m.n + ', so the first audio is lost at ' + m.n + ' x ' + nf(m.T, 0, 1) + ' ms = ' + m.t.toFixed(2) + ' s.';
    drawWrapped(s, x + pad, yy, tw, 20);
    return;
  }
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 5 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 6. ' + (sc >= 5 ? 'Mastery reached.' : 'Mastery is 5 of 6.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('Timing 3 was only 5 ms too slow. How long did it last before losing audio, and does a "big" ring buffer fix a loop that is slightly too slow?', x + pad, yy + 24, tw, 20);
    return;
  }
  if (!submitted) {
    fill('navy');
    textStyle(ITALIC);
    text('How long can this loop run before audio is lost?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Each pass takes P = ' + p + ' ms. Type the seconds until the first sample is lost (within 0.1 s), or type never. One attempt.', x + pad, yy + 22, tw, 20);
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
    timingIndex = 0;
    results = [];
    submitted = false;
    finished = false;
  } else {
    mode = 'explore';
  }
  answerInput.value('');
  updateControlStates();
}

// "never" or a number of seconds (an optional trailing "s" is allowed)
function parseAnswer(raw) {
  const s = raw.trim().toLowerCase();
  if (s === 'never') return 'never';
  const v = parseFloat(s.replace(/s$/, ''));
  return isNaN(v) ? null : v;
}

function submitAnswer() {
  if (mode !== 'quiz' || submitted || finished) return;
  const ans = parseAnswer(answerInput.value());
  if (ans === null) return;
  const tm = TIMINGS[timingIndex];
  const correct = tm.answer === 'never' ? ans === 'never' :
    (ans !== 'never' && abs(ans - tm.answer) <= 0.1 + 1e-9);
  results[timingIndex] = correct;
  feedbackCorrect = correct;
  const shown = tm.answer === 'never' ? 'never' : tm.answer + ' s';
  feedback = correct ? 'Correct: ' + tm.why : 'Not quite. The answer is ' + shown + ': ' + tm.why;
  submitted = true;
  updateControlStates();
}

function nextTiming() {
  if (!submitted) return;
  if (timingIndex === TIMINGS.length - 1) finished = true;
  else { timingIndex++; submitted = false; }
  answerInput.value('');
  updateControlStates();
}

function setEnabled(el, on) {
  el.elt.disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  modeButton.html(quiz ? 'Back to explore' : 'Start the 6 timings');
  setEnabled(answerInput, quiz && !submitted && !finished);
  setEnabled(submitButton, quiz && !submitted && !finished);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(timingIndex === TIMINGS.length - 1 ? 'See score' : 'Next timing');
  setEnabled(pSlider, !quiz);
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
  pSlider.position(sliderLeftMargin, drawHeight + 48);
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  pSlider.size(canvasWidth - sliderLeftMargin - margin);
  positionControls();
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = Math.floor(container.getBoundingClientRect().width);
}
