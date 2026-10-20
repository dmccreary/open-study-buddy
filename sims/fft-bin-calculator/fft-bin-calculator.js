// FFT Bin Calculator - p5.js MicroSim
// CANVAS_HEIGHT: 530
// Calculate FFT bins with the kit's values: sample rate 12,800 Hz and FFT
// size 512, so the bin width is 12,800 / 512 = 25 Hz and the useful bins are
// 0 to 255 (the Nyquist limit of 6,400 Hz would be bin 256).
// bin = frequency x 512 / 12,800 = frequency / 25
// nearest bin = bin rounded to the nearest whole number
// bin center = bin number x 25 Hz
// Values come from src/kits/study-buddy-base/config.py (MIC_SAMPLE_RATE, FFT_SIZE).

let canvasWidth = 800;
let drawHeight = 450;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let sliderLeftMargin = 230;
let defaultTextSize = 16;

const SAMPLE_RATE = 12800;
const FFT_SIZE = 512;
const BIN_HZ = SAMPLE_RATE / FFT_SIZE;   // 25 Hz
const USEFUL_BINS = FFT_SIZE / 2;        // 256 bins, numbered 0 to 255

const CHALLENGES = [
  { q: 'Nearest bin for a 1,000 Hz tone', kind: 'bin', f: 1000, answer: 40, why: '1,000 / 25 = 40.0, exactly on a bin center.' },
  { q: 'Nearest bin for a 440 Hz tone', kind: 'bin', f: 440, answer: 18, why: '440 / 25 = 17.6, which is closer to 18 than to 17.' },
  { q: 'Nearest bin for a 262 Hz tone', kind: 'bin', f: 262, answer: 10, why: '262 / 25 = 10.48, which is closer to 10 than to 11.' },
  { q: 'Nearest bin for a 3,300 Hz tone', kind: 'bin', f: 3300, answer: 132, why: '3,300 / 25 = 132.0, exactly on a bin center.' },
  { q: 'Center frequency of bin 100, in Hz', kind: 'center', bin: 100, answer: 2500, why: '100 x 25 = 2,500 Hz.' },
  { q: 'Center frequency of bin 255, in Hz', kind: 'center', bin: 255, answer: 6375, why: '255 x 25 = 6,375 Hz, the top bin; the Nyquist limit of 6,400 Hz would be bin 256.' }
];

let mode = 'explore';
let chIndex = 0;
let submitted = false;
let finished = false;
let results = [];
let feedback = '';
let feedbackCorrect = false;

let modeButton, answerInput, submitButton, nextButton, toneSlider;

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

  toneSlider = createSlider(0, 6400, 1000, 12.5);
  toneSlider.size(canvasWidth - sliderLeftMargin - margin);

  positionControls();
  updateControlStates();

  describe('A frequency axis from 0 to 6,400 hertz divided into 256 FFT bins of 25 hertz, with a zoomed row of eleven bins around a tone. A slider moves the tone; the sim shows the bin number as a decimal, the nearest bin, its center frequency, and the difference in hertz. A six-challenge quiz asks for nearest bins and bin center frequencies.', LABEL);
}

// what is on screen: a tone (explore and bin questions) or a bin (center questions)
function currentView() {
  if (mode === 'explore') return { kind: 'bin', f: Number(toneSlider.value()) };
  return CHALLENGES[min(chIndex, CHALLENGES.length - 1)];
}

function binInfo(f) {
  const b = f * FFT_SIZE / SAMPLE_RATE;
  const frac = b - Math.floor(b);
  const tie = Math.abs(frac - 0.5) < 1e-9;
  const nearest = Math.round(b);
  return { b: b, tie: tie, nearest: nearest, diff: f - nearest * BIN_HZ };
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
  text('FFT Bin Calculator', canvasWidth / 2, 10);
  textSize(16);
  fill('dimgray');
  let status;
  if (mode === 'explore') status = 'Explore: sample rate 12,800 Hz, FFT size 512, bin width 25 Hz';
  else if (finished) status = 'All 6 challenges done   |   Score: ' + countCorrect() + ' of 6';
  else status = 'Challenge ' + (chIndex + 1) + ' of 6   |   Score: ' + countCorrect() + ' of 6';
  text(status, canvasWidth / 2, 42);

  const v = currentView();
  const reveal = mode === 'explore' || submitted;
  const focusBin = v.kind === 'bin' ? binInfo(v.f).nearest : v.bin;
  drawOverview(v, reveal, 70);
  drawZoom(v, reveal, focusBin, 150);
  drawPanel(v, reveal, margin, 300, canvasWidth - 2 * margin, drawHeight - 310);

  noStroke();
  fill(mode === 'explore' ? 'black' : 'silver');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Tone frequency: ' + Number(toneSlider.value()).toLocaleString('en-US') + ' Hz', 10, drawHeight + 58);
}

// the whole range: 0 to 6,400 Hz with bin ticks
function drawOverview(v, reveal, y) {
  const x0 = 40;
  const x1 = canvasWidth - 40;
  const X = f => x0 + (x1 - x0) * f / 6400;
  noStroke();
  fill('black');
  textSize(14);
  textAlign(LEFT, TOP);
  text('Whole spectrum in Hz: 256 useful bins (0 to 255), 25 Hz each', x0, y);
  stroke('silver');
  fill('white');
  rect(x0, y + 22, x1 - x0, 20);
  stroke('lightsteelblue');
  for (let k = 0; k <= USEFUL_BINS; k += 4) line(X(k * BIN_HZ), y + 22, X(k * BIN_HZ), y + 42);
  noStroke();
  fill('dimgray');
  textAlign(CENTER, TOP);
  for (let f = 0; f <= 6400; f += 800) text(f.toLocaleString('en-US'), X(f), y + 46);
  if (reveal) {
    const f = v.kind === 'bin' ? v.f : v.bin * BIN_HZ;
    stroke('firebrick');
    strokeWeight(3);
    line(X(f), y + 18, X(f), y + 46);
    strokeWeight(1);
  }
}

// a row of 11 bins around the focus bin
function drawZoom(v, reveal, focus, y) {
  const n = 11;
  const start = constrain(focus - 5, 0, USEFUL_BINS + 1 - n);
  const x0 = 40;
  const cw = (canvasWidth - 80) / n;
  noStroke();
  fill('black');
  textSize(14);
  textAlign(LEFT, TOP);
  text('Zoom: bins ' + start + ' to ' + (start + n - 1) + ' (each cell is one bin; the center line is the bin center)', x0, y);
  // a tone exactly halfway between two bins has no single nearest bin
  const tie = v.kind === 'bin' && binInfo(v.f).tie;
  for (let i = 0; i < n; i++) {
    const k = start + i;
    const x = x0 + i * cw;
    const outside = k >= USEFUL_BINS;
    const hot = reveal && k === focus && !outside && !tie;
    stroke('steelblue');
    fill(outside ? 'gainsboro' : (hot ? 'gold' : 'white'));
    rect(x, y + 22, cw, 54);
    stroke('lightsteelblue');
    drawingContext.setLineDash([3, 3]);
    line(x + cw / 2, y + 22, x + cw / 2, y + 76);
    drawingContext.setLineDash([]);
  }
  // tone position (drawn before the labels so the labels stay readable):
  // bin b sits at the center of cell b
  if (reveal && v.kind === 'bin') {
    const b = v.f / BIN_HZ;
    const tx = x0 + (b - start + 0.5) * cw;
    if (tx >= x0 && tx <= x0 + n * cw) {
      stroke('firebrick');
      strokeWeight(3);
      line(tx, y + 16, tx, y + 82);
      strokeWeight(1);
      noStroke();
      fill('firebrick');
      textAlign(CENTER, TOP);
      textSize(14);
      text('tone', tx, y + 96);
    }
  }
  for (let i = 0; i < n; i++) {
    const k = start + i;
    const x = x0 + i * cw;
    const outside = k >= USEFUL_BINS;
    const hot = reveal && k === focus && !outside && !tie;
    const numTxt = outside ? '256?' : String(k);
    const hzTxt = (k * BIN_HZ).toLocaleString('en-US');
    noStroke();
    textAlign(CENTER, TOP);
    // small backing so a tone line passing through never hides the label
    textSize(16);
    textStyle(hot ? BOLD : NORMAL);
    fill(outside ? 'gainsboro' : (hot ? 'gold' : 'white'));
    rect(x + cw / 2 - textWidth(numTxt) / 2 - 2, y + 27, textWidth(numTxt) + 4, 19);
    fill(outside ? 'gray' : 'navy');
    text(numTxt, x + cw / 2, y + 28);
    textStyle(NORMAL);
    textSize(13);
    fill(outside ? 'gainsboro' : (hot ? 'gold' : 'white'));
    rect(x + cw / 2 - textWidth(hzTxt) / 2 - 2, y + 53, textWidth(hzTxt) + 4, 16);
    fill('dimgray');
    text(hzTxt, x + cw / 2, y + 54);
  }
  noStroke();
  fill('dimgray');
  textAlign(LEFT, TOP);
  textSize(13);
  text('bin number (top) and bin center in Hz (bottom)', x0, y + 82);
}

function drawPanel(v, reveal, x, y, w, h) {
  fill(255, 255, 255, 235);
  stroke('silver');
  rect(x, y, w, h, 10);
  const pad = 10;
  const tw = w - 2 * pad;
  let yy = y + 8;
  noStroke();
  textAlign(LEFT, TOP);
  textSize(16);

  if (finished) {
    const sc = countCorrect();
    fill(sc >= 5 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 6. ' + (sc >= 5 ? 'Mastery reached.' : 'Mastery is 5 of 6.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('A tone between two bins was not lost: it was assigned to the nearer one. Which challenges landed exactly on a bin center?', x + pad, yy + 24, tw, 20);
    return;
  }
  if (mode === 'quiz') {
    fill('black');
    textStyle(BOLD);
    text(v.q, x + pad, yy);
    textStyle(NORMAL);
    yy += 24;
  }
  if (!reveal) {
    fill('navy');
    textStyle(ITALIC);
    text(v.kind === 'bin' ? 'Which bin does this tone land in?' : 'What frequency sits at the center of this bin?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Use bin = frequency / 25 or bin center = bin number x 25. Type a whole number and press Submit. One attempt.', x + pad, yy + 22, tw, 20);
    return;
  }

  fill('black');
  if (v.kind === 'bin') {
    const bi = binInfo(v.f);
    const fTxt = v.f.toLocaleString('en-US');
    text('bin = ' + fTxt + ' / 25 = ' + bi.b.toFixed(2), x + pad, yy);
    let near;
    if (bi.b >= USEFUL_BINS) near = 'bin 256 is outside the 256 useful bins (0 to 255): this is the Nyquist limit';
    else if (bi.tie) near = 'halfway between bins ' + Math.floor(bi.b) + ' and ' + (Math.floor(bi.b) + 1) + ': a tie';
    else near = 'nearest bin = ' + bi.nearest + ', center = ' + bi.nearest + ' x 25 = ' + (bi.nearest * BIN_HZ).toLocaleString('en-US') + ' Hz';
    text(near, x + pad, yy + 22);
    if (bi.b < USEFUL_BINS && !bi.tie) {
      text('difference from the bin center = ' + (bi.diff >= 0 ? '+' : '') + nf(bi.diff, 0, 1) + ' Hz' +
        (abs(bi.diff) < 1e-9 ? ' (exactly on a bin center)' : ''), x + pad, yy + 44);
    }
  } else {
    text('bin center = ' + v.bin + ' x 25 = ' + (v.bin * BIN_HZ).toLocaleString('en-US') + ' Hz', x + pad, yy);
  }
  if (mode === 'quiz') {
    fill(feedbackCorrect ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    drawWrapped(feedback, x + pad, yy + (v.kind === 'bin' ? 70 : 26), tw, 20);
    textStyle(NORMAL);
  }
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
  const raw = answerInput.value().trim().replace(/,/g, '');
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
  setEnabled(toneSlider, !quiz);
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
  toneSlider.position(sliderLeftMargin, drawHeight + 48);
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  toneSlider.size(canvasWidth - sliderLeftMargin - margin);
  positionControls();
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = Math.floor(container.getBoundingClientRect().width);
}
