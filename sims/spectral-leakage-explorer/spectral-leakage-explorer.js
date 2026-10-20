// Spectral Leakage Explorer - p5.js MicroSim
// CANVAS_HEIGHT: 550
// Compare the magnitude spectrum of a test tone with no window and with the
// Hann window. The model is a sine wave of amplitude 1,000 sampled at
// 12,800 Hz for 512 samples. The "no window" spectrum is the magnitude of the
// 512-point DFT; the Hann spectrum multiplies the samples by
// w[i] = 0.5 - 0.5 cos(2 pi i / 512) first. The sim counts bins 0 to 255 whose
// magnitude is at least 10% of the largest magnitude in that spectrum, the
// same rule as src/chapters/09-signal-processing-fft/04-leakage-hann.py.

let canvasWidth = 800;
let drawHeight = 470;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let sliderLeftMargin = 400;
let defaultTextSize = 16;

const N = 512;
const FS = 12800;
const BIN_HZ = FS / N;        // 25 Hz
const VIEW_LO = 30;           // bins drawn in the charts
const VIEW_HI = 50;
const THRESHOLD = 0.1;

const TONES = [
  { f: 1000,    answer: 'No window',   why: 'The tone is exactly on a bin, so there is no leakage to remove, and the window adds a three-bin peak.' },
  { f: 1006.25, answer: 'Hann window', why: 'The tone is a quarter bin off center, so the plain spectrum leaks into 5 bins and Hann holds it to 3.' },
  { f: 1012.5,  answer: 'Hann window', why: 'Halfway between bins is the worst case without a window: 10 bins.' },
  { f: 1018.75, answer: 'Hann window', why: 'A quarter bin off center on the other side, the mirror image of tone 2.' },
  { f: 1037.5,  answer: 'Hann window', why: 'Another halfway case, between bins 41 and 42.' },
  { f: 1050,    answer: 'No window',   why: 'Exactly on bin 42, so the window can only widen the peak.' }
];

let cosTable = [];
let sinTable = [];
let cache = {};

let mode = 'explore';
let toneIndex = 0;
let submitted = false;
let finished = false;
let results = [];
let feedback = '';
let feedbackCorrect = false;

let modeButton, predictSelect, submitButton, nextButton, windowLabel, windowSelect, toneSlider;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  for (let i = 0; i < N; i++) {
    cosTable.push(Math.cos(2 * Math.PI * i / N));
    sinTable.push(Math.sin(2 * Math.PI * i / N));
  }

  modeButton = createButton('Start the 6 tones');
  modeButton.mousePressed(toggleMode);
  predictSelect = createSelect();
  for (const o of ['choose', 'No window', 'Hann window', 'The same']) predictSelect.option(o);
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next tone');
  nextButton.mousePressed(nextTone);
  windowLabel = createSpan('Window:');
  windowSelect = createSelect();
  windowSelect.option('No window');
  windowSelect.option('Hann window');
  for (const el of [modeButton, predictSelect, submitButton, nextButton, windowLabel, windowSelect]) el.style('font-size', '16px');

  toneSlider = createSlider(900, 1100, 1000, 6.25);
  toneSlider.size(canvasWidth - sliderLeftMargin - margin);

  positionControls();
  updateControlStates();

  describe('A bar chart of FFT magnitudes for bins 30 to 50, scaled to the loudest bin, with a dashed line at 10 percent. Bars at or above 10 percent are dark. A slider moves the test tone from 900 to 1,100 hertz and a menu picks no window or the Hann window. In the quiz the learner predicts which window gives the narrower peak, then both spectra are drawn side by side with their counts.', LABEL);
}

// magnitude of bins 0..255 for a tone and window; cached
function spectrum(f, hann) {
  const key = f + (hann ? 'h' : 'n');
  if (cache[key]) return cache[key];
  const x = new Array(N);
  for (let i = 0; i < N; i++) {
    const w = hann ? 0.5 - 0.5 * cosTable[i] : 1;
    x[i] = 1000 * Math.sin(2 * Math.PI * f * i / FS) * w;
  }
  const mag = new Array(N / 2);
  let maxMag = 0;
  for (let k = 0; k < N / 2; k++) {
    let re = 0;
    let im = 0;
    for (let i = 0; i < N; i++) {
      const idx = (k * i) % N;
      re += x[i] * cosTable[idx];
      im -= x[i] * sinTable[idx];
    }
    mag[k] = Math.sqrt(re * re + im * im);
    if (mag[k] > maxMag) maxMag = mag[k];
  }
  let count = 0;
  for (let k = 0; k < N / 2; k++) if (mag[k] >= THRESHOLD * maxMag) count++;
  cache[key] = { mag: mag, max: maxMag, count: count };
  return cache[key];
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
  text('Spectral Leakage Explorer', canvasWidth / 2, 10);
  textSize(16);
  fill('dimgray');
  let status;
  if (mode === 'explore') status = 'Explore: 512 samples at 12,800 Hz, bin width 25 Hz';
  else if (finished) status = 'All 6 tones done   |   Score: ' + countCorrect() + ' of 6';
  else status = 'Tone ' + (toneIndex + 1) + ' of 6   |   Score: ' + countCorrect() + ' of 6';
  text(status, canvasWidth / 2, 42);

  const top = 72;
  const ch = 260;
  if (mode === 'explore') {
    const f = Number(toneSlider.value());
    const hann = windowSelect.value() === 'Hann window';
    drawChart(f, hann, 60, top, canvasWidth - 60 - 25, ch);
  } else {
    const f = TONES[min(toneIndex, 5)].f;
    if (submitted || finished) {
      const half = (canvasWidth - 40) / 2;
      drawChart(f, false, 55, top, half - 55, ch);
      drawChart(f, true, 40 + half + 25, top, half - 40, ch);
    } else {
      drawHidden(f, 60, top, canvasWidth - 60 - 25, ch);
    }
  }
  drawPanel(margin, 368, canvasWidth - 2 * margin, drawHeight - 378);

  noStroke();
  fill(mode === 'explore' ? 'black' : 'silver');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Tone: ' + nf(Number(toneSlider.value()), 0, 2) + ' Hz', 230, drawHeight + 58);
}

function drawChart(f, hann, x, y, w, h) {
  const sp = spectrum(f, hann);
  const plotTop = y + 44;
  const plotH = h - 44 - 40;
  const nBins = VIEW_HI - VIEW_LO + 1;
  const bw = w / nBins;
  const Y = p => plotTop + plotH - plotH * p;

  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(16);
  textStyle(BOLD);
  text(hann ? 'Hann window' : 'No window', x, y);
  textStyle(NORMAL);
  fill('navy');
  text(sp.count + (sp.count === 1 ? ' bin' : ' bins') + ' at least 10% of the loudest (bins 0 to 255)', x, y + 20);

  // axes and grid
  textSize(13);
  for (const p of [0, 0.25, 0.5, 0.75, 1]) {
    stroke('gainsboro');
    line(x, Y(p), x + w, Y(p));
    noStroke();
    fill('dimgray');
    textAlign(RIGHT, CENTER);
    text(Math.round(p * 100) + '%', x - 4, Y(p));
  }
  // 10% threshold
  stroke('firebrick');
  drawingContext.setLineDash([6, 4]);
  line(x, Y(THRESHOLD), x + w, Y(THRESHOLD));
  drawingContext.setLineDash([]);

  // bars
  for (let k = VIEW_LO; k <= VIEW_HI; k++) {
    const p = sp.mag[k] / sp.max;
    const bx = x + (k - VIEW_LO) * bw;
    noStroke();
    fill(p >= THRESHOLD ? 'royalblue' : 'lightsteelblue');
    rect(bx + bw * 0.15, Y(p), bw * 0.7, plotTop + plotH - Y(p));
    if ((k - VIEW_LO) % 2 === 0) {
      fill('dimgray');
      textAlign(CENTER, TOP);
      text(k, bx + bw / 2, plotTop + plotH + 4);
    }
  }
  // tone position
  const tx = x + (f / BIN_HZ - VIEW_LO + 0.5) * bw;
  stroke('darkorange');
  strokeWeight(2);
  drawingContext.setLineDash([3, 3]);
  line(tx, plotTop - 4, tx, plotTop + plotH);
  drawingContext.setLineDash([]);
  strokeWeight(1);
  noStroke();
  fill('dimgray');
  textAlign(CENTER, TOP);
  text('bin number (orange line = the tone, bin ' + (f / BIN_HZ).toFixed(2) + ')', x + w / 2, plotTop + plotH + 20);
}

function drawHidden(f, x, y, w, h) {
  fill(255, 255, 255, 200);
  stroke('silver');
  rect(x, y + 10, w, h - 20, 10);
  noStroke();
  fill('black');
  textAlign(CENTER, CENTER);
  textSize(22);
  text('Tone ' + (toneIndex + 1) + ': ' + nf(f, 0, 2) + ' Hz  =  bin ' + (f / BIN_HZ).toFixed(2), x + w / 2, y + h / 2 - 30);
  textSize(16);
  fill('dimgray');
  text('The two spectra are drawn after you submit your prediction.', x + w / 2, y + h / 2 + 10);
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
    const f = Number(toneSlider.value());
    const b = f / BIN_HZ;
    fill('navy');
    textStyle(ITALIC);
    text('Which window makes this peak narrower?', x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    const off = b - Math.round(b);
    drawWrapped('The tone is bin ' + b.toFixed(2) + (abs(off) < 1e-9 ? ', exactly on a bin center.' :
      ', ' + abs(off).toFixed(2) + ' of a bin from the nearest center.') +
      ' Switch the window and count the dark bars. Try 1,000 Hz and 1,050 Hz, then a tone between them.', x + pad, yy + 22, tw, 20);
    return;
  }
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 5 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 6. ' + (sc >= 5 ? 'Mastery reached.' : 'Mastery is 5 of 6.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('Tones 1 and 6 sat exactly on a bin. Does a window always make the peak narrower? What decides it?', x + pad, yy + 24, tw, 20);
    return;
  }
  if (!submitted) {
    fill('navy');
    textStyle(ITALIC);
    text('Which window gives fewer bins at 10% or more of the loudest bin?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Look at where the tone sits relative to the bin centers. Choose No window, Hann window or The same, then Submit. One attempt.', x + pad, yy + 22, tw, 20);
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
    toneIndex = 0;
    results = [];
    submitted = false;
    finished = false;
  } else {
    mode = 'explore';
  }
  predictSelect.selected('choose');
  updateControlStates();
}

function submitAnswer() {
  if (mode !== 'quiz' || submitted || finished) return;
  const choice = predictSelect.value();
  if (choice === 'choose') return;
  const t = TONES[toneIndex];
  const correct = choice === t.answer;
  results[toneIndex] = correct;
  feedbackCorrect = correct;
  const a = spectrum(t.f, false).count;
  const b = spectrum(t.f, true).count;
  const counts = ' (no window: ' + a + ', Hann: ' + b + ')';
  feedback = (correct ? 'Correct: ' : 'Not quite. ') + t.why + counts;
  submitted = true;
  updateControlStates();
}

function nextTone() {
  if (!submitted) return;
  if (toneIndex === TONES.length - 1) finished = true;
  else { toneIndex++; submitted = false; }
  predictSelect.selected('choose');
  updateControlStates();
}

function setEnabled(el, on) {
  el.elt.disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  modeButton.html(quiz ? 'Back to explore' : 'Start the 6 tones');
  setEnabled(predictSelect, quiz && !submitted && !finished);
  setEnabled(submitButton, quiz && !submitted && !finished);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(toneIndex === TONES.length - 1 ? 'See score' : 'Next tone');
  setEnabled(windowSelect, !quiz);
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
  layoutRow([modeButton, predictSelect, submitButton, nextButton], 10, drawHeight + 8, 10);
  layoutRow([windowLabel, windowSelect], 10, drawHeight + 46, 6);
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
