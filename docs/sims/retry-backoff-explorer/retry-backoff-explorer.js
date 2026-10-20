// Retry and Backoff Timeline Explorer - p5.js MicroSim
// CANVAS_HEIGHT: 575
// Calculate the longest time a request can take. A request makes up to N
// attempts; each fails by timing out after T seconds. After each failed
// attempt except the last, the device waits; the ceiling of wait k
// (k = 0 for the first) is min(cap, base x 2^k) ms. Worst case:
//   N x T + (sum of the N - 1 ceilings) / 1000   seconds.
// With full jitter each real wait is a whole number of ms from 0 to its
// ceiling. Defaults are the chapter's backoff.py / buddy_config.py values.

let canvasWidth = 800;
let drawHeight = 460;
let controlHeight = 115;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

const SETTINGS = [
  { base: 500, cap: 8000, n: 4, t: 8, answer: 35.5, why: '4 x 8 = 32 s of timeouts, plus waits of 0.5 + 1 + 2 = 3.5 s.' },
  { base: 500, cap: 8000, n: 3, t: 5, answer: 16.5, why: '3 x 5 = 15 s, plus waits of 0.5 + 1 = 1.5 s.' },
  { base: 1000, cap: 4000, n: 5, t: 3, answer: 26, why: '5 x 3 = 15 s, plus waits of 1 + 2 + 4 + 4 = 11 s: the fourth wait would be 8 s but is capped at 4 s.' },
  { base: 500, cap: 2000, n: 4, t: 2, answer: 11.5, why: '4 x 2 = 8 s, plus waits of 0.5 + 1 + 2 = 3.5 s.' },
  { base: 250, cap: 8000, n: 6, t: 4, answer: 31.75, why: '6 x 4 = 24 s, plus waits of 0.25 + 0.5 + 1 + 2 + 4 = 7.75 s.' },
  { base: 500, cap: 8000, n: 1, t: 8, answer: 8, why: 'One attempt has no retry and no wait.' },
  { base: 500, cap: 8000, n: 7, t: 8, answer: 79.5, why: '7 x 8 = 56 s, plus waits of 0.5 + 1 + 2 + 4 + 8 + 8 = 23.5 s (the sixth would be 16 s but is capped at 8 s).' },
  { base: 100, cap: 800, n: 4, t: 1, answer: 4.7, why: '4 x 1 = 4 s, plus waits of 0.1 + 0.2 + 0.4 = 0.7 s.' }
];

let mode = 'explore';
let setIndex = 0;
let submitted = false;
let finished = false;
let results = [];
let feedback = '';
let feedbackCorrect = false;
let jitterWaits = null;     // one random run, made only when the learner asks
let jitterKey = '';

let modeButton, answerInput, submitButton, nextButton, jitterBox;
let baseSlider, capSlider, nSlider, tSlider;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  modeButton = createButton('Start the 8 settings');
  modeButton.mousePressed(toggleMode);
  answerInput = createInput('', 'number');
  answerInput.size(90);
  answerInput.attribute('step', '0.01');
  answerInput.attribute('placeholder', 'seconds');
  answerInput.elt.addEventListener('keydown', e => { if (e.key === 'Enter') submitAnswer(); });
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next setting');
  nextButton.mousePressed(nextSetting);
  jitterBox = createCheckbox(' One random run', false);
  jitterBox.changed(() => { jitterWaits = null; });
  for (const el of [modeButton, answerInput, submitButton, nextButton, jitterBox]) el.style('font-size', '16px');
  baseSlider = createSlider(100, 1000, 500, 50);
  capSlider = createSlider(800, 8000, 8000, 200);
  nSlider = createSlider(1, 7, 4, 1);
  tSlider = createSlider(1, 8, 8, 1);

  positionControls();
  updateControlStates();

  describe('A timeline of a request that keeps timing out: each attempt is a block of T seconds and each wait between attempts is a block whose ceiling doubles from the base up to the cap, with no wait after the last attempt. The worst-case total is labeled. Sliders set the base, cap, number of attempts and timeout, and a checkbox draws one randomly jittered run beneath. An eight-setting quiz asks for the worst-case total.', LABEL);
}

function ceilings(s) {
  const out = [];
  for (let k = 0; k < s.n - 1; k++) out.push(Math.min(s.cap, s.base * Math.pow(2, k)));
  return out;
}

function worst(s) {
  return s.n * s.t + ceilings(s).reduce((a, b) => a + b, 0) / 1000;
}

function currentSetting() {
  if (mode === 'quiz') return SETTINGS[min(setIndex, 7)];
  return { base: Number(baseSlider.value()), cap: Number(capSlider.value()), n: Number(nSlider.value()), t: Number(tSlider.value()) };
}

function fmtS(v) {
  return String(Math.round(v * 1000) / 1000);
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
  text('Retry and Backoff Timeline Explorer', canvasWidth / 2, 10);
  const s = currentSetting();
  textSize(16);
  fill('dimgray');
  let status = 'base ' + s.base + ' ms, cap ' + s.cap.toLocaleString('en-US') + ' ms, ' + s.n + ' attempts, timeout ' + s.t + ' s';
  if (mode === 'quiz') status = (finished ? 'All 8 settings done' : 'Setting ' + (setIndex + 1) + ' of 8') + '   |   Score: ' + countCorrect() + ' of 8   |   ' + status;
  else status = (setIndex === 0 && s.base === 500 && s.cap === 8000 && s.n === 4 && s.t === 8 ? 'Default: ' : 'Explore: ') + status;
  textSize(mode === 'quiz' ? 14 : 16);
  text(status, canvasWidth / 2, 42);

  const reveal = mode === 'explore' || submitted;
  if (reveal) {
    const ws = ceilings(s);
    const total = worst(s);
    let jw = null;
    if (jitterBox.checked()) {
      const key = JSON.stringify(s);
      if (!jitterWaits || jitterKey !== key) {
        jitterWaits = ws.map(c => Math.floor(random(c + 1)));
        jitterKey = key;
      }
      jw = jitterWaits;
    }
    drawTimeline(s, ws, jw, total, 80);
  } else {
    noStroke();
    fill('dimgray');
    textAlign(CENTER, CENTER);
    textSize(16);
    text('The timeline is drawn after you submit.', canvasWidth / 2, 170);
  }
  drawPanel(s, margin, 300, canvasWidth - 2 * margin, drawHeight - 308);

  noStroke();
  fill(mode === 'explore' ? 'black' : 'silver');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  const half = canvasWidth / 2;
  text('Base: ' + baseSlider.value() + ' ms', 10, drawHeight + 58);
  text('Cap: ' + Number(capSlider.value()).toLocaleString('en-US') + ' ms', half + 10, drawHeight + 58);
  text('Attempts N: ' + nSlider.value(), 10, drawHeight + 96);
  text('Timeout T: ' + tSlider.value() + ' s', half + 10, drawHeight + 96);
}

function drawTimeline(s, ws, jw, total, y) {
  const x0 = 30;
  const x1 = canvasWidth - 30;
  const X = sec => x0 + (x1 - x0) * sec / total;
  const bh = 40;
  const rows = [{ label: 'Worst case: every attempt times out, every wait takes its full ceiling', waits: ws, y: y + 22 }];
  if (jw) rows.push({ label: 'One random run (jittered waits; attempts still time out)', waits: jw, y: y + 22 + bh + 46 });
  for (const r of rows) {
    noStroke();
    fill('black');
    textAlign(LEFT, BOTTOM);
    textSize(14);
    text(r.label, x0, r.y - 4);
    let tt = 0;
    for (let i = 0; i < s.n; i++) {
      drawSeg(X(tt), X(tt + s.t), r.y, bh, 'indianred', 'try ' + (i + 1), s.t + ' s');
      tt += s.t;
      if (i < s.n - 1) {
        const wsec = r.waits[i] / 1000;
        drawSeg(X(tt), X(tt + wsec), r.y, bh, 'gold', 'wait', fmtS(wsec) + ' s');
        tt += wsec;
      }
    }
    noStroke();
    fill('black');
    textAlign(LEFT, TOP);
    textSize(14);
    text('ends at ' + fmtS(tt) + ' s', min(X(tt), x1 - 90), r.y + bh + 4);
  }
  // time axis
  const ay = rows[rows.length - 1].y + bh + 26;
  stroke('black');
  line(x0, ay, x1, ay);
  const step = [1, 2, 5, 10, 20].find(v => total / v <= 10) || 20;
  noStroke();
  fill('dimgray');
  textSize(13);
  textAlign(CENTER, TOP);
  for (let sec = 0; sec <= total + 1e-9; sec += step) {
    stroke('black');
    line(X(sec), ay - 3, X(sec), ay + 3);
    noStroke();
    text(sec, X(sec), ay + 5);
  }
  textAlign(RIGHT, TOP);
  text('seconds', x1, ay + 20);
}

function drawSeg(xa, xb, y, h, col, top, bottom) {
  stroke('white');
  fill(col);
  rect(xa, y, max(1, xb - xa), h);
  noStroke();
  fill('black');
  textAlign(CENTER, CENTER);
  textSize(12);
  if (xb - xa > max(textWidth(top), textWidth(bottom)) + 4) {
    text(top, (xa + xb) / 2, y + h / 2 - 8);
    text(bottom, (xa + xb) / 2, y + h / 2 + 8);
  }
}

function drawPanel(s, x, y, w, h) {
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
    const ws = ceilings(s);
    fill('navy');
    textStyle(ITALIC);
    text('What is the longest this request can take?', x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('Wait ceilings: ' + (ws.length ? ws.map(v => v.toLocaleString('en-US')).join(', ') + ' ms' : 'none (one attempt)') +
      '. Worst case = ' + s.n + ' x ' + s.t + ' s + ' + fmtS(ws.reduce((a, b) => a + b, 0) / 1000) + ' s = ' + fmtS(worst(s)) +
      ' s. Turn on One random run: can it ever be longer than the worst case?', x + pad, yy + 22, tw, 20);
    return;
  }
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 7 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 8. ' + (sc >= 7 ? 'Mastery reached.' : 'Mastery is 7 of 8.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('In settings 3 and 7 the cap made the later waits equal, and setting 6 had no wait at all. Which term of the formula did each one change?', x + pad, yy + 24, tw, 20);
    return;
  }
  if (!submitted) {
    fill('navy');
    textStyle(ITALIC);
    text('What is the longest this request can take?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Add N x T to the N - 1 wait ceilings, each min(cap, base x 2^k). Type the total in seconds (within 0.05 s counts) and Submit.', x + pad, yy + 22, tw, 20);
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
    setIndex = 0;
    results = [];
    submitted = false;
    finished = false;
  } else {
    mode = 'explore';
    setIndex = 0;
  }
  jitterWaits = null;
  answerInput.value('');
  updateControlStates();
}

function submitAnswer() {
  if (mode !== 'quiz' || submitted || finished) return;
  const raw = answerInput.value().trim();
  if (raw === '' || isNaN(Number(raw))) return;
  const st = SETTINGS[setIndex];
  const correct = abs(Number(raw) - st.answer) <= 0.05 + 1e-9;
  results[setIndex] = correct;
  feedbackCorrect = correct;
  feedback = correct ? 'Correct: ' + st.why : 'Not quite. The worst case is ' + st.answer + ' s: ' + st.why;
  submitted = true;
  updateControlStates();
}

function nextSetting() {
  if (!submitted) return;
  if (setIndex === SETTINGS.length - 1) finished = true;
  else { setIndex++; submitted = false; }
  jitterWaits = null;
  answerInput.value('');
  updateControlStates();
}

function setEnabled(el, on) {
  const input = el.elt.querySelector('input');
  (input || el.elt).disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  modeButton.html(quiz ? 'Back to explore' : 'Start the 8 settings');
  setEnabled(answerInput, quiz && !submitted && !finished);
  setEnabled(submitButton, quiz && !submitted && !finished);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(setIndex === SETTINGS.length - 1 ? 'See score' : 'Next setting');
  for (const el of [baseSlider, capSlider, nSlider, tSlider]) setEnabled(el, !quiz);
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
  layoutRow([modeButton, answerInput, submitButton, nextButton, jitterBox], 10, drawHeight + 8, 10);
  const half = canvasWidth / 2;
  baseSlider.position(120, drawHeight + 48);
  baseSlider.size(half - 120 - 20);
  capSlider.position(half + 130, drawHeight + 48);
  capSlider.size(half - 130 - margin);
  nSlider.position(120, drawHeight + 86);
  nSlider.size(half - 120 - 20);
  tSlider.position(half + 130, drawHeight + 86);
  tSlider.size(half - 130 - margin);
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
