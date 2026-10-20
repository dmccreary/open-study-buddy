// Log Band Layout Explorer - p5.js MicroSim
// CANVAS_HEIGHT: 560
// Use a log-spaced band layout: bands from f_low to 6,400 Hz with a fixed
// ratio r = (6,400 / f_low)^(1 / bands) between neighboring edges.
// Edge i = round(f_low x r^i x 512 / 12,800), halves rounded to even; an edge
// that is not greater than the previous edge becomes the previous edge + 1.
// Band i holds bins edge[i] to edge[i+1] - 1, and a tone belongs to the band
// that holds its nearest bin. This reproduces dsp.log_band_edges(16, 100,
// 6400, 12800, 512) as printed by 03-bin-calculator.py.

let canvasWidth = 800;
let drawHeight = 480;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

const FS = 12800;
const N = 512;
const BIN_HZ = FS / N;     // 25 Hz
const F_HIGH = 6400;

const CHALLENGES = [
  { q: 'Which band contains a 1,000 Hz tone?', kind: 'tone', f: 1000, answer: 8, why: '1,000 / 25 = bin 40, and band 8 holds bins 32 to 40.' },
  { q: 'Which band contains a 440 Hz tone?', kind: 'tone', f: 440, answer: 5, why: '440 / 25 = 17.6, nearest bin 18, and band 5 holds bins 15 to 18.' },
  { q: 'Which band contains a 3,000 Hz tone?', kind: 'tone', f: 3000, answer: 13, why: '3,000 / 25 = bin 120, and band 13 holds bins 117 to 151.' },
  { q: 'How many bins are in band 10?', kind: 'count', band: 10, answer: 16, why: 'Band 10 holds bins 54 to 69, which is 69 - 54 + 1 = 16.' },
  { q: 'How many bins are in band 15?', kind: 'count', band: 15, answer: 59, why: 'Band 15 holds bins 197 to 255, which is 59.' },
  { q: 'How many bins are in band 0?', kind: 'count', band: 0, answer: 1, why: 'Band 0 holds only bin 4, because the band between 100 and 129.7 Hz is narrower than one 25 Hz bin and is stretched to one bin.' }
];

let mode = 'explore';
let chIndex = 0;
let submitted = false;
let finished = false;
let results = [];
let feedback = '';
let feedbackCorrect = false;

let modeButton, answerInput, submitButton, nextButton, bandsSlider, lowSlider;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  modeButton = createButton('Start the 6 challenges');
  modeButton.mousePressed(toggleMode);
  answerInput = createInput('', 'number');
  answerInput.size(100);
  answerInput.attribute('placeholder', 'number');
  answerInput.elt.addEventListener('keydown', e => { if (e.key === 'Enter') submitAnswer(); });
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next challenge');
  nextButton.mousePressed(nextChallenge);
  for (const el of [modeButton, answerInput, submitButton, nextButton]) el.style('font-size', '16px');

  bandsSlider = createSlider(4, 32, 16, 4);
  lowSlider = createSlider(50, 400, 100, 50);

  positionControls();
  updateControlStates();

  describe('A strip of the 256 FFT bins divided into log-spaced bands, above a table listing every band with its bin range, bin count and edges in hertz. Sliders set the number of bands (4 to 32) and the lowest frequency (50 to 400 hertz). In the quiz the default 16-band layout from 100 to 6,400 hertz is used to find the band of a tone and the bin count of a band.', LABEL);
}

// round half to even, like Python's round()
function roundHalfEven(x) {
  const f = Math.floor(x);
  const d = x - f;
  if (Math.abs(d - 0.5) < 1e-9) return f % 2 === 0 ? f : f + 1;
  return Math.round(x);
}

function bandEdges(bands, fLow) {
  const r = Math.pow(F_HIGH / fLow, 1 / bands);
  const e = [];
  for (let i = 0; i <= bands; i++) {
    let v = roundHalfEven(fLow * Math.pow(r, i) * N / FS);
    if (e.length && v <= e[e.length - 1]) v = e[e.length - 1] + 1;
    e.push(v);
  }
  return { edges: e, r: r };
}

function currentLayout() {
  if (mode === 'quiz') return { bands: 16, fLow: 100 };
  return { bands: Number(bandsSlider.value()), fLow: Number(lowSlider.value()) };
}

function bandOfBin(edges, bin) {
  for (let i = 0; i < edges.length - 1; i++) if (bin >= edges[i] && bin < edges[i + 1]) return i;
  return -1;
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
  text('Log Band Layout Explorer', canvasWidth / 2, 10);

  const lay = currentLayout();
  const be = bandEdges(lay.bands, lay.fLow);
  textSize(16);
  fill('dimgray');
  let status = lay.bands + ' bands from ' + lay.fLow + ' Hz to 6,400 Hz, ratio ' + be.r.toFixed(4) + ' per band';
  if (mode === 'quiz') status = (finished ? 'All 6 challenges done' : 'Challenge ' + (chIndex + 1) + ' of 6') +
    '   |   Score: ' + countCorrect() + ' of 6   |   ' + status;
  text(status, canvasWidth / 2, 42);

  // which band is highlighted, and which tone is marked
  let hot = -1;
  let toneBin = null;
  if (mode === 'quiz' && submitted && !finished) {
    const c = CHALLENGES[chIndex];
    if (c.kind === 'tone') { toneBin = Math.round(c.f / BIN_HZ); hot = bandOfBin(be.edges, toneBin); }
    else hot = c.band;
  }
  drawStrip(be.edges, hot, toneBin, 70);
  drawTable(be.edges, hot, 140);
  drawPanel(be.edges, margin, 412, canvasWidth - 2 * margin, drawHeight - 420);

  // slider labels
  noStroke();
  fill(mode === 'explore' ? 'black' : 'silver');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Bands: ' + bandsSlider.value(), 10, drawHeight + 58);
  text('Lowest: ' + lowSlider.value() + ' Hz', canvasWidth / 2 + 10, drawHeight + 58);
}

// bins 0 to 256 on a linear axis, with band boundaries
function drawStrip(edges, hot, toneBin, y) {
  const x0 = 30;
  const x1 = canvasWidth - 30;
  const X = b => x0 + (x1 - x0) * b / 256;
  noStroke();
  fill('black');
  textSize(14);
  textAlign(LEFT, TOP);
  text('Bins 0 to 255, 25 Hz each. Each block is one band; the table gives bins (count) and Hz.', x0, y);
  // unused low bins
  fill('gainsboro');
  rect(X(0), y + 20, X(edges[0]) - X(0), 26);
  for (let i = 0; i < edges.length - 1; i++) {
    const xa = X(edges[i]);
    const xb = X(edges[i + 1]);
    stroke('white');
    fill(i === hot ? 'gold' : (i % 2 === 0 ? 'steelblue' : 'lightskyblue'));
    rect(xa, y + 20, xb - xa, 26);
    noStroke();
    fill(i === hot ? 'black' : (i % 2 === 0 ? 'white' : 'black'));
    textAlign(CENTER, CENTER);
    textSize(13);
    if (xb - xa > 16) text(i, (xa + xb) / 2, y + 33);
  }
  noStroke();
  fill('dimgray');
  textAlign(CENTER, TOP);
  textSize(13);
  for (let b = 0; b <= 256; b += 32) text(b, X(b), y + 50);
  if (toneBin !== null) {
    stroke('firebrick');
    strokeWeight(3);
    line(X(toneBin + 0.5), y + 14, X(toneBin + 0.5), y + 50);
    strokeWeight(1);
  }
}

// every band: number, bins, count, and edges in Hz
function drawTable(edges, hot, y) {
  const bands = edges.length - 1;
  const rows = min(bands, 8);
  const cols = Math.ceil(bands / 8);
  const x0 = margin;
  const cw = (canvasWidth - 2 * margin) / cols;
  const rh = 33;
  // dense tables (more than 16 bands) drop the word "bin(s)" to fit the cell
  const binTxt = i => {
    const lo = edges[i];
    const hi = edges[i + 1] - 1;
    const range = lo === hi ? String(lo) : lo + '-' + hi;
    return (cols > 2 ? range : (lo === hi ? 'bin ' : 'bins ') + range) + ' (' + (hi - lo + 1) + ')';
  };
  const hzTxt = i => (edges[i] * BIN_HZ).toLocaleString('en-US') + ' to ' +
    (edges[i + 1] * BIN_HZ).toLocaleString('en-US') + ' Hz';
  // one decision for the whole table: one line per band if the widest row fits,
  // otherwise the bins above the Hz edges
  const labelSize = cols > 2 ? 14 : 16;
  textStyle(BOLD);
  textSize(labelSize);
  const labelW = textWidth('Band ' + (bands - 1)) + 10;
  textStyle(NORMAL);
  let widest = 0;
  for (let i = 0; i < bands; i++) {
    textSize(16);
    const a = textWidth(binTxt(i));
    textSize(14);
    widest = max(widest, a + 16 + textWidth(hzTxt(i)));
  }
  const oneLine = cols <= 2 && 6 + labelW + widest < cw - 12;

  for (let i = 0; i < bands; i++) {
    const c = Math.floor(i / rows);
    const r = i % rows;
    const x = x0 + c * cw;
    const yy = y + r * rh;
    stroke('silver');
    fill(i === hot ? 'gold' : (r % 2 === 0 ? 'white' : 'whitesmoke'));
    rect(x, yy, cw - 4, rh - 2, 4);
    noStroke();
    fill('black');
    textAlign(LEFT, TOP);
    textSize(labelSize);
    textStyle(BOLD);
    text('Band ' + i, x + 6, yy + (oneLine ? 2 : 1));
    textStyle(NORMAL);
    const bx = x + 6 + labelW;
    if (oneLine) {
      textSize(16);
      text(binTxt(i), bx, yy + 2);
      fill('dimgray');
      textSize(14);
      textAlign(RIGHT, TOP);
      text(hzTxt(i), x + cw - 12, yy + 3);
    } else {
      textSize(14);
      text(binTxt(i), bx, yy + 1);
      fill('dimgray');
      textSize(12);
      text(hzTxt(i), bx, yy + 17);
    }
  }
}

function drawPanel(edges, x, y, w, h) {
  fill(255, 255, 255, 235);
  stroke('silver');
  rect(x, y, w, h, 10);
  const pad = 10;
  const tw = w - 2 * pad;
  const yy = y + 6;
  noStroke();
  textAlign(LEFT, TOP);
  textSize(16);
  if (mode === 'explore') {
    fill('navy');
    textStyle(ITALIC);
    text('Which band holds this tone?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Change the sliders and watch the lowest bands: do they ever hold more than one or two bins? Then start the challenges (16 bands, 100 Hz).', x + pad, yy + 20, tw, 19);
    return;
  }
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 5 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 6. ' + (sc >= 5 ? 'Mastery reached.' : 'Mastery is 5 of 6.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('Band 0 had 1 bin and band 15 had 59. Why does the same ratio give such different widths?', x + pad, yy + 22, tw, 19);
    return;
  }
  const c = CHALLENGES[chIndex];
  fill('black');
  textStyle(BOLD);
  text(c.q, x + pad, yy);
  textStyle(NORMAL);
  if (!submitted) {
    fill('dimgray');
    drawWrapped('Use the table (16 bands, 100 Hz). For a tone, find its nearest bin first (frequency / 25). Type a whole number and Submit.', x + pad, yy + 20, tw, 19);
    return;
  }
  fill(feedbackCorrect ? 'darkgreen' : 'firebrick');
  textStyle(BOLD);
  drawWrapped(feedback, x + pad, yy + 20, tw, 19);
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
    chIndex = 0;
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
  const c = CHALLENGES[chIndex];
  const correct = Number(raw) === c.answer;
  results[chIndex] = correct;
  feedbackCorrect = correct;
  feedback = correct ? 'Correct: ' + c.why : 'Not quite. The answer is ' + c.answer + ': ' + c.why;
  submitted = true;
  updateControlStates();
}

function nextChallenge() {
  if (!submitted) return;
  if (chIndex === CHALLENGES.length - 1) finished = true;
  else { chIndex++; submitted = false; }
  answerInput.value('');
  updateControlStates();
}

function setEnabled(el, on) {
  el.elt.disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  modeButton.html(quiz ? 'Back to explore' : 'Start the 6 challenges');
  setEnabled(answerInput, quiz && !submitted && !finished);
  setEnabled(submitButton, quiz && !submitted && !finished);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(chIndex === CHALLENGES.length - 1 ? 'See score' : 'Next challenge');
  setEnabled(bandsSlider, !quiz);
  setEnabled(lowSlider, !quiz);
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
  const half = canvasWidth / 2;
  bandsSlider.position(110, drawHeight + 48);
  bandsSlider.size(half - 110 - 20);
  lowSlider.position(half + 140, drawHeight + 48);
  lowSlider.size(half - 140 - margin);
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
