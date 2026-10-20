// Chunk-Size and Heap Explorer - p5.js MicroSim
// CANVAS_HEIGHT: 595
// Examine whether an upload design fits in the free heap. With S seconds of
// speech at 12,800 samples per second, R16 = S x 25,600 bytes (16-bit) and
// R32 = S x 51,200 bytes (32-bit microphone words). Total memory needed:
//   A join header + body:  2 x R16       B slices of K bytes:  R16 + K
//   C 32-bit, convert in place:  R32 + K  D stream 1,024-byte frames:  1,024
// A case fits when the total is at most F - 40,000 (code, display and network
// buffers). Sends = ceil(bytes to send / K) (1,024-byte frames for D).
// The reserve and free-heap values are illustrative.

let canvasWidth = 800;
let drawHeight = 480;
let controlHeight = 115;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

const RESERVE = 40000;
const CHUNKS = [512, 1024, 2048, 4096, 8192];
const DESIGNS = {
  A: 'Record 16-bit, join header and body into one bytes object, send once',
  B: 'Record 16-bit, send the header, then slices of K bytes',
  C: 'Record 32-bit, convert in place, send the first half in slices of K',
  D: 'Stream each 1,024-byte frame as it is converted, keep nothing'
};
const CASES = [
  { d: 'B', s: 3, k: 2048, f: 180000, fits: true, sends: 38, why: 'R16 is 76,800; plus 2,048 is 78,848, under 140,000. 76,800 / 2,048 is 37.5, rounded up to 38.' },
  { d: 'B', s: 5, k: 2048, f: 180000, fits: true, sends: 63, why: 'R16 is 128,000; plus 2,048 is 130,048, under 140,000. 128,000 / 2,048 is 62.5, rounded up to 63.' },
  { d: 'A', s: 5, k: null, f: 180000, fits: false, why: 'The join needs 128,000 + 128,000 = 256,000, over 140,000.' },
  { d: 'C', s: 5, k: 2048, f: 180000, fits: false, why: 'R32 is 256,000, over 140,000 by itself.' },
  { d: 'C', s: 3, k: 2048, f: 260000, fits: true, sends: 38, why: 'R32 is 153,600; plus 2,048 is 155,648, under 220,000. The first half to send is 76,800 bytes: 38 sends.' },
  { d: 'B', s: 10, k: 2048, f: 260000, fits: false, why: 'R16 is 256,000, over 220,000.' },
  { d: 'D', s: 10, k: 1024, f: 100000, fits: true, sends: 250, why: 'One 1,024-byte frame needs no recording. 10 s is 256,000 bytes: 256,000 / 1,024 is 250 frames.' },
  { d: 'B', s: 5, k: 8192, f: 180000, fits: true, sends: 16, why: 'R16 is 128,000; plus 8,192 is 136,192, under 140,000. 128,000 / 8,192 is 15.6, rounded up to 16.' }
];

let mode = 'explore';
let caseIndex = 0;
let submitted = false;
let finished = false;
let results = [];
let feedback = '';
let feedbackCorrect = false;

let modeButton, submitButton, nextButton, answerLabel, fitSelect, sendsLabel, sendsInput, chunkLabel, chunkSelect;
let lengthSlider, heapSlider;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  modeButton = createButton('Start the 8 cases');
  modeButton.mousePressed(toggleMode);
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next case');
  nextButton.mousePressed(nextCase);
  answerLabel = createSpan('Answer:');
  fitSelect = createSelect();
  for (const o of ['choose', 'fits', 'does not fit']) fitSelect.option(o);
  sendsLabel = createSpan('Sends (if it fits):');
  sendsInput = createInput('', 'number');
  sendsInput.size(80);
  sendsInput.elt.addEventListener('keydown', e => { if (e.key === 'Enter') submitAnswer(); });
  chunkLabel = createSpan('Chunk K:');
  chunkSelect = createSelect();
  for (const k of CHUNKS) chunkSelect.option(k.toLocaleString('en-US') + ' B', String(k));
  chunkSelect.selected('2048');
  for (const el of [modeButton, submitButton, nextButton, answerLabel, fitSelect, sendsLabel, sendsInput, chunkLabel, chunkSelect]) {
    el.style('font-size', '16px');
  }
  lengthSlider = createSlider(1, 10, 5, 1);
  heapSlider = createSlider(100000, 260000, 180000, 10000);

  positionControls();
  updateControlStates();

  describe('Four upload designs, labeled A to D, drawn as horizontal bars of the memory each needs, against a free-heap line with a 40,000-byte reserve shaded before it. Sliders set the speech length and the free heap, and a menu picks the chunk size; each bar says whether the design fits and how many sends it needs. An eight-case quiz asks whether one design fits and, if so, how many sends.', LABEL);
}

function need(d, s, k) {
  const r16 = s * 25600;
  const r32 = s * 51200;
  if (d === 'A') return 2 * r16;
  if (d === 'B') return r16 + k;
  if (d === 'C') return r32 + k;
  return 1024;
}

function sendsFor(d, s, k) {
  return d === 'D' ? Math.ceil(s * 25600 / 1024) : Math.ceil(s * 25600 / k);
}

function currentView() {
  if (mode === 'quiz') {
    const c = CASES[min(caseIndex, 7)];
    return { s: c.s, k: c.k || 2048, f: c.f, only: c.d };
  }
  return { s: Number(lengthSlider.value()), k: Number(chunkSelect.value()), f: Number(heapSlider.value()), only: null };
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
  text('Chunk-Size and Heap Explorer', canvasWidth / 2, 10);
  const v = currentView();
  textSize(16);
  fill('dimgray');
  let status = 'S = ' + v.s + ' s, K = ' + v.k.toLocaleString('en-US') + ' B, free heap F = ' + v.f.toLocaleString('en-US') + ' B (illustrative)';
  if (mode === 'quiz') {
    const c = CASES[min(caseIndex, 7)];
    status = (finished ? 'All 8 cases done' : 'Case ' + (caseIndex + 1) + ' of 8') + '   |   Score: ' + countCorrect() + ' of 8   |   design ' + c.d +
      ', S = ' + c.s + ' s, K = ' + (c.k ? c.k.toLocaleString('en-US') : 'not used') + ', F = ' + c.f.toLocaleString('en-US');
  }
  textSize(mode === 'quiz' ? 14 : 16);
  text(status, canvasWidth / 2, 42);

  drawDesigns(v, 68);
  drawBars(v, 186);
  drawPanel(v, margin, 372, canvasWidth - 2 * margin, drawHeight - 380);

  noStroke();
  fill(mode === 'explore' ? 'black' : 'silver');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  const half = canvasWidth / 2;
  text('Length S: ' + lengthSlider.value() + ' s', 10, drawHeight + 98);
  text('Free F: ' + Number(heapSlider.value()).toLocaleString('en-US'), half + 10, drawHeight + 98);
}

function drawDesigns(v, y) {
  noStroke();
  textAlign(LEFT, TOP);
  textSize(14);
  let i = 0;
  for (const d of ['A', 'B', 'C', 'D']) {
    const on = !v.only || v.only === d;
    fill(on ? 'black' : 'silver');
    textStyle(BOLD);
    text(d, margin, y + i * 26);
    textStyle(NORMAL);
    drawWrapped(DESIGNS[d], margin + 18, y + i * 26, canvasWidth - 2 * margin - 18, 16);
    i++;
  }
}

function drawBars(v, y) {
  const x0 = 50;
  const x1 = canvasWidth - 30;
  const usable = v.f - RESERVE;
  const xMax = max(v.f * 1.1, need('C', v.s, v.k) * 1.05, 300000);
  const X = b => x0 + (x1 - x0) * min(b, xMax) / xMax;
  const bh = 26;
  const gap = 12;
  const hBars = 4 * (bh + gap) - gap;
  // reserve between usable and F
  noStroke();
  fill(255, 160, 122, 70);
  rect(X(usable), y - 6, X(v.f) - X(usable), hBars + 12);
  const reveal = mode === 'explore' || submitted;
  let i = 0;
  for (const d of ['A', 'B', 'C', 'D']) {
    const yy = y + i * (bh + gap);
    i++;
    noStroke();
    fill('black');
    textAlign(RIGHT, CENTER);
    textSize(16);
    textStyle(BOLD);
    text(d, x0 - 10, yy + bh / 2);
    textStyle(NORMAL);
    if (v.only && v.only !== d) continue;
    if (!reveal) {
      fill('dimgray');
      textAlign(LEFT, CENTER);
      textSize(14);
      text('memory need hidden until you submit', x0 + 6, yy + bh / 2);
      continue;
    }
    const n = need(d, v.s, v.k);
    const fits = n <= usable;
    fill(fits ? 'seagreen' : 'indianred');
    rect(x0, yy, max(2, X(n) - x0), bh, 0, 5, 5, 0);
    const lbl = n.toLocaleString('en-US') + ' B, ' + (fits ? 'fits, ' + sendsFor(d, v.s, v.k) + ' sends' : 'does not fit');
    textSize(14);
    const lw = textWidth(lbl);
    const inside = X(n) - x0 > lw + 16;
    fill(inside ? 'white' : 'black');
    textAlign(inside ? RIGHT : LEFT, CENTER);
    text(lbl, inside ? X(n) - 8 : X(n) + 6, yy + bh / 2);
  }
  // usable and free-heap lines
  const yb = y + hBars;
  stroke('darkgreen');
  strokeWeight(2);
  drawingContext.setLineDash([6, 4]);
  line(X(usable), y - 10, X(usable), yb + 8);
  drawingContext.setLineDash([]);
  stroke('gray');
  line(X(v.f), y - 10, X(v.f), yb + 8);
  strokeWeight(1);
  noStroke();
  textSize(13);
  fill('darkgreen');
  textAlign(RIGHT, TOP);
  text('usable F - 40,000 = ' + usable.toLocaleString('en-US'), X(usable) - 4, yb + 10);
  fill('gray');
  textAlign(LEFT, TOP);
  text('free heap F', X(v.f) + 4, yb + 10);
  fill('dimgray');
  textAlign(LEFT, TOP);
  text('shaded: 40,000-byte reserve', x0, yb + 28);
}

function drawPanel(v, x, y, w, h) {
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
    text('Does this fit in the free heap, and how many sends does it need?', x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('R16 = ' + (v.s * 25600).toLocaleString('en-US') + ' B, R32 = ' + (v.s * 51200).toLocaleString('en-US') +
      ' B. Move the length to 5 s: which designs stop fitting, and which one fits at any length?', x + pad, yy + 22, tw, 20);
    return;
  }
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 7 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 8. ' + (sc >= 7 ? 'Mastery reached.' : 'Mastery is 7 of 8.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('At 5 s designs A and C failed where B fitted, and D fitted at any length. Which designs move the memory problem, and which remove it?', x + pad, yy + 24, tw, 20);
    return;
  }
  if (!submitted) {
    fill('navy');
    textStyle(ITALIC);
    text('Does this fit in the free heap, and how many sends does it need?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Work out the total need for design ' + CASES[caseIndex].d + ' and compare it with F - 40,000. If it fits, sends = bytes to send / K, rounded up.', x + pad, yy + 22, tw, 20);
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
    caseIndex = 0;
    results = [];
    submitted = false;
    finished = false;
  } else {
    mode = 'explore';
  }
  fitSelect.selected('choose');
  sendsInput.value('');
  updateControlStates();
}

function submitAnswer() {
  if (mode !== 'quiz' || submitted || finished) return;
  const f = fitSelect.value();
  if (f === 'choose') return;
  const raw = sendsInput.value().trim();
  if (f === 'fits' && (raw === '' || isNaN(Number(raw)))) return;
  const c = CASES[caseIndex];
  const correct = (f === 'fits') === c.fits && (!c.fits || Number(raw) === c.sends);
  results[caseIndex] = correct;
  feedbackCorrect = correct;
  feedback = correct ? 'Correct: ' + c.why :
    'Not quite. It ' + (c.fits ? 'fits, with ' + c.sends + ' sends' : 'does not fit') + ': ' + c.why;
  submitted = true;
  updateControlStates();
}

function nextCase() {
  if (!submitted) return;
  if (caseIndex === CASES.length - 1) finished = true;
  else { caseIndex++; submitted = false; }
  fitSelect.selected('choose');
  sendsInput.value('');
  updateControlStates();
}

function setEnabled(el, on) {
  el.elt.disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  const answering = quiz && !submitted && !finished;
  modeButton.html(quiz ? 'Back to explore' : 'Start the 8 cases');
  setEnabled(fitSelect, answering);
  setEnabled(sendsInput, answering);
  setEnabled(submitButton, answering);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(caseIndex === CASES.length - 1 ? 'See score' : 'Next case');
  for (const el of [chunkSelect, lengthSlider, heapSlider]) setEnabled(el, !quiz);
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
  layoutRow([modeButton, submitButton, nextButton, chunkLabel, chunkSelect], 10, drawHeight + 8, 10);
  layoutRow([answerLabel, fitSelect, sendsLabel, sendsInput], 10, drawHeight + 44, 8);
  const half = canvasWidth / 2;
  lengthSlider.position(130, drawHeight + 88);
  lengthSlider.size(half - 130 - 20);
  heapSlider.position(half + 145, drawHeight + 88);
  heapSlider.size(half - 145 - margin);
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
