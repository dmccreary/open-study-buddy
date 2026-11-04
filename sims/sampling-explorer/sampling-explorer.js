// Sampling Explorer
// CANVAS_HEIGHT: 545
// Shows a true sine tone, the sample dots taken at the sample rate, and the
// lowest-frequency wave those dots suggest. The learner explores, then
// calculates the apparent frequency for 6 challenge tones.
//
// Rules (from the chapter spec):
//   * Nyquist limit = fs / 2
//   * if f <= fs / 2 the apparent frequency is f
//   * if fs / 2 < f <= fs the apparent frequency is fs - f (folding)
//   * f exactly equal to fs / 2: "at the Nyquist limit" message, no apparent frequency
// Math note: for fs/2 < f < fs, sin(2*pi*f*n/fs) = -sin(2*pi*(fs - f)*n/fs) for every
// whole number n, so the suggested wave is drawn phase-inverted and passes exactly
// through every sample dot.

// ---------- canvas layout ----------
let canvasWidth = 400;
let drawHeight = 430;
let controlHeight = 115;     // 3 rows of controls: 3 x 35 + 10
let canvasHeight = drawHeight + controlHeight;
let margin = 25;
let sliderLeftMargin = 215;
let defaultTextSize = 16;
let infoTop = 240;           // set by drawPlot: where the info lines start
let panelTop = 288;          // set by drawInfo: where the text panel starts

const SAMPLE_RATES = [4000, 8000, 12800, 16000];

// ---------- challenge tones (Content table) ----------
const challenges = [
  { f: 1000, fs: 12800, answer: 1000, why: '1,000 is below 6,400, so it is captured correctly.' },
  { f: 6000, fs: 12800, answer: 6000, why: '6,000 is just below the limit, so it is captured correctly.' },
  { f: 7000, fs: 12800, answer: 5800, why: '7,000 is above 6,400, so it folds to 12,800 - 7,000 = 5,800.' },
  { f: 9000, fs: 12800, answer: 3800, why: '9,000 is above 6,400, so it folds to 12,800 - 9,000 = 3,800.' },
  { f: 3000, fs: 4000,  answer: 1000, why: '3,000 is above 2,000, so it folds to 4,000 - 3,000 = 1,000.' },
  { f: 5000, fs: 8000,  answer: 3000, why: '5,000 is above 4,000, so it folds to 8,000 - 5,000 = 3,000.' }
];

// ---------- sampling math ----------
// Returns {apparent, folded, atNyquist}
function apparentFrequency(f, fs) {
  const nyquist = fs / 2;
  if (f === nyquist) return { apparent: null, folded: false, atNyquist: true };
  if (f < nyquist) return { apparent: f, folded: false, atNyquist: false };
  return { apparent: fs - f, folded: true, atNyquist: false };   // nyquist < f <= fs
}

function fmt(n) {
  return Number(n).toLocaleString('en-US');
}

// ---------- state ----------
let trueFreq = 1000;
let sampleRate = 12800;
let challengeActive = false;
let challengeDone = false;
let cIndex = 0;
let revealed = false;        // the current challenge has been answered
let score = 0;
let feedback = '';
let feedbackColor = 'black';

// ---------- controls ----------
let freqSlider, rateSelect, challengeButton, answerInput, submitButton;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  // Create every control first, then position them
  freqSlider = createSlider(100, 9000, 1000, 100);
  freqSlider.input(() => { trueFreq = freqSlider.value(); });
  rateSelect = createSelect();
  for (const r of SAMPLE_RATES) rateSelect.option(fmt(r) + ' Hz', String(r));
  rateSelect.selected('12800');
  rateSelect.changed(changeRate);
  challengeButton = createButton('Start challenges');
  challengeButton.mousePressed(pressChallengeButton);
  answerInput = createInput('', 'text');
  answerInput.attribute('placeholder', 'Hz');
  answerInput.attribute('inputmode', 'numeric');
  answerInput.size(90);
  answerInput.elt.addEventListener('keydown', (e) => { if (e.key === 'Enter') submitAnswer(); });
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);

  for (const c of [rateSelect, challengeButton, answerInput, submitButton]) c.style('font-size', '15px');
  positionControls();
  updateControlStates();

  describe('A true sine tone drawn in gray, red sample dots taken at the sample rate, and a blue wave ' +
    'that the dots suggest. Tones above half the sample rate fold to a lower apparent frequency. ' +
    'Six challenges ask the learner to calculate the apparent frequency.', LABEL);
}

function positionControls() {
  freqSlider.position(sliderLeftMargin, drawHeight + 10);
  freqSlider.size(canvasWidth - sliderLeftMargin - margin);
  rateSelect.position(115, drawHeight + 44);
  layoutRow3();
}

let row3End = 0;              // right edge of the row 3 controls, so the score never overlaps them
function layoutRow3() {
  let x = 10;
  const y = drawHeight + 80;
  answerInput.size(canvasWidth < 500 ? 60 : 90);
  for (const c of [challengeButton, answerInput, submitButton]) {
    c.position(x, y);
    x += (c.elt.offsetWidth || 110) + 10;
  }
  row3End = x;
}

function setEnabled(ctrl, on) {
  ctrl.elt.disabled = !on;
}

function updateControlStates() {
  setEnabled(freqSlider, !challengeActive);
  setEnabled(rateSelect, !challengeActive);
  setEnabled(answerInput, challengeActive && !revealed);
  setEnabled(submitButton, challengeActive && !revealed);
  if (!challengeActive) {
    challengeButton.html(challengeDone ? 'Start challenges again' : 'Start challenges');
    setEnabled(challengeButton, true);
  } else {
    challengeButton.html(cIndex === challenges.length - 1 ? 'Show score' : 'Next challenge');
    setEnabled(challengeButton, revealed);
  }
  layoutRow3();
}

// Exploration rule: the true frequency must stay below the sample rate
function changeRate() {
  sampleRate = parseInt(rateSelect.value(), 10);
  const maxF = Math.min(9000, sampleRate - 100);   // largest allowed value below the rate
  freqSlider.elt.max = maxF;
  if (trueFreq > maxF) trueFreq = maxF;
  freqSlider.value(trueFreq);
}

// ---------- challenge actions ----------
function pressChallengeButton() {
  if (!challengeActive) {
    challengeActive = true;
    challengeDone = false;
    cIndex = 0;
    score = 0;
    loadChallenge();
  } else if (revealed) {
    if (cIndex === challenges.length - 1) {
      challengeActive = false;
      challengeDone = true;
      feedback = '';
      answerInput.value('');
    } else {
      cIndex++;
      loadChallenge();
    }
  }
  updateControlStates();
}

function loadChallenge() {
  const c = challenges[cIndex];
  revealed = false;
  feedback = '';
  answerInput.value('');
  // show the challenge's tone and rate on the (locked) controls
  rateSelect.selected(String(c.fs));
  sampleRate = c.fs;
  freqSlider.elt.max = Math.min(9000, c.fs - 100);
  freqSlider.value(c.f);
  trueFreq = c.f;
  updateControlStates();
  answerInput.elt.focus();
}

function submitAnswer() {
  if (!challengeActive || revealed) return;
  const raw = String(answerInput.value()).replace(/,/g, '').trim();
  if (!/^\d+(\.\d+)?$/.test(raw)) {
    feedback = 'Type the apparent frequency in hertz, for example 2500.';
    feedbackColor = 'dimgray';
    return;
  }
  const value = parseFloat(raw);
  const c = challenges[cIndex];
  const computed = apparentFrequency(c.f, c.fs).apparent;   // equals c.answer for every challenge
  if (Math.abs(value - computed) <= 1) {
    score++;
    feedback = 'Correct: ' + c.why;
    feedbackColor = 'darkgreen';
  } else {
    feedback = 'Not quite. The apparent frequency is ' + fmt(computed) + ' Hz: ' + c.why;
    feedbackColor = 'firebrick';
  }
  revealed = true;
  updateControlStates();
}

// ---------- drawing ----------
function draw() {
  updateCanvasSize();
  if (!challengeActive) trueFreq = freqSlider.value();

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
  text('Sampling Explorer', canvasWidth / 2, 10);
  textSize(canvasWidth < 560 ? 13 : 14);
  fill('dimgray');
  text('Illustrative tones. 12,800 Hz is the kit microphone rate and 16,000 Hz is the test 05 speaker rate.',
    10, 40, canvasWidth - 20, 36);

  const showSamples = !challengeActive || revealed;
  drawPlot(showSamples);
  drawInfo(showSamples);
  drawPanel();
  drawControlLabels();
}

function drawPlot(showSamples) {
  const f = trueFreq;
  const fs = sampleRate;
  const a = apparentFrequency(f, fs);
  // window: about 2.5 cycles of the apparent wave, between 16 and 40 samples.
  // Before a challenge answer is revealed, size it from the true tone instead,
  // so the window does not hint at the apparent frequency.
  const basis = showSamples ? a.apparent : f;
  let nSamples = (showSamples && a.atNyquist) ? 16 : Math.ceil(2.5 * fs / basis);
  nSamples = Math.max(16, Math.min(40, nSamples));
  const T = nSamples / fs;                     // seconds shown
  const left = margin + 10;
  const right = canvasWidth - margin;
  const top = 82;
  const bottom = 206;
  const mid = (top + bottom) / 2;
  const amp = (bottom - top) / 2 - 4;
  const xOf = t => left + (t / T) * (right - left);

  // zero line and frame
  stroke('lightsteelblue');
  line(left, mid, right, mid);
  stroke('silver');
  noFill();
  rect(left, top - 6, right - left, bottom - top + 12);

  // true wave, drawn with several points per pixel so fast tones stay accurate
  stroke('gray');
  strokeWeight(1.5);
  beginShape();
  const steps = Math.ceil((right - left) * 3);
  for (let i = 0; i <= steps; i++) {
    const t = (i / steps) * T;
    vertex(xOf(t), mid - amp * Math.sin(TWO_PI * f * t));
  }
  endShape();

  if (showSamples) {
    // the wave the dots suggest (lowest-frequency sine through the samples)
    if (!a.atNyquist) {
      const sign = a.folded ? -1 : 1;
      stroke('royalblue');
      strokeWeight(3);
      beginShape();
      for (let i = 0; i <= steps; i++) {
        const t = (i / steps) * T;
        vertex(xOf(t), mid - amp * sign * Math.sin(TWO_PI * a.apparent * t));
      }
      endShape();
    }
    // sample dots at t = n / fs
    noStroke();
    fill('crimson');
    for (let n = 0; n <= nSamples; n++) {
      const t = n / fs;
      circle(xOf(t), mid - amp * Math.sin(TWO_PI * f * t), 9);
    }
  }
  strokeWeight(1);

  // time axis labels in milliseconds
  noStroke();
  fill('black');
  textSize(13);
  textAlign(LEFT, TOP);
  text('0 ms', left, bottom + 10);
  textAlign(RIGHT, TOP);
  text((T * 1000).toFixed(2) + ' ms' + (showSamples ? ' (' + nSamples + ' samples)' : ''), right, bottom + 10);

  // legend: inline with the axis labels on wide screens, on its own row when narrow
  textAlign(LEFT, TOP);
  let x = left + 50;
  let y = bottom + 10;
  infoTop = 240;
  if (canvasWidth <= 620) {
    x = left;
    y = bottom + 28;
    infoTop = 254;
  }
  const items = [['gray', 'true wave'], ['crimson', 'samples'], ['royalblue', 'wave the dots suggest']];
  for (const [col, lab] of items) {
    fill(col);
    rect(x, y + 4, 14, 6);
    fill('black');
    text(lab, x + 18, y);
    x += 18 + textWidth(lab) + 16;
  }
}

function drawInfo(showSamples) {
  const a = apparentFrequency(trueFreq, sampleRate);
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  let info = 'True frequency: ' + fmt(trueFreq) + ' Hz    Sample rate: ' + fmt(sampleRate) + ' Hz';
  if (showSamples) {
    info += '    Nyquist limit: ' + fmt(sampleRate / 2) + ' Hz';
  }
  const w = canvasWidth - 2 * margin;
  textStyle(BOLD);
  fitTextSize(info, w, 16, 11);
  if (textWidth(info) > w) {
    // narrow screens: shorter wording so the line is not clipped
    info = 'True: ' + fmt(trueFreq) + ' Hz   Rate: ' + fmt(sampleRate) + ' Hz' +
      (showSamples ? '   Nyquist: ' + fmt(sampleRate / 2) + ' Hz' : '');
    fitTextSize(info, w, 16, 10);
  }
  text(info, margin, infoTop);
  textStyle(NORMAL);
  panelTop = infoTop + 48;
  if (showSamples) {
    let line2;
    if (a.atNyquist) line2 = 'Apparent frequency: at the Nyquist limit: the samples cannot show this tone reliably';
    else line2 = 'Apparent frequency: ' + fmt(a.apparent) + ' Hz';
    fill(a.atNyquist ? 'darkorange' : (a.folded ? 'crimson' : 'royalblue'));
    textStyle(BOLD);
    fitTextSize(line2, w, 16, 11);
    if (textWidth(line2) > w) {
      // the Nyquist message is long: wrap it onto two lines and push the panel down
      textSize(13);
      panelTop += drawWrapped(line2, margin, infoTop + 22, w, 16) - 16;
    } else {
      text(line2, margin, infoTop + 22);
    }
    textStyle(NORMAL);
  }
}

function drawPanel() {
  const px = margin;
  const py = panelTop;
  const pw = canvasWidth - 2 * margin;
  const ph = drawHeight - py - 8;
  stroke(200);
  fill(255, 255, 255, 230);
  rect(px, py, pw, ph, 10);
  noStroke();
  const narrow = canvasWidth < 560;
  textSize(narrow ? 14 : 16);
  const lineH = narrow ? 17 : 20;
  fill('black');

  let title, body, bodyColor;
  if (challengeActive) {
    const c = challenges[cIndex];
    title = 'Challenge ' + (cIndex + 1) + ' of 6: a ' + fmt(c.f) + ' Hz tone sampled at ' + fmt(c.fs) +
      ' Hz appears at what frequency?';
    body = revealed ? feedback : (feedback || 'Type your answer in hertz and press Submit to see the samples.');
    bodyColor = revealed ? feedbackColor : 'dimgray';
  } else if (challengeDone) {
    title = 'Challenges done. Score: ' + score + ' of 6' + (score >= 5 ? ' (mastery reached)' : ' (mastery is 5 of 6)');
    body = 'Tones 3 to 6 reappeared at lower frequencies, never at higher ones.';
    bodyColor = 'dimgray';
  } else {
    title = 'What wave do these dots suggest?';
    const a = apparentFrequency(trueFreq, sampleRate);
    const ny = sampleRate / 2;
    if (a.atNyquist) body = fmt(trueFreq) + ' Hz is exactly half the sample rate, so every sample lands on the zero line.';
    else if (!a.folded) body = fmt(trueFreq) + ' Hz is below the Nyquist limit of ' + fmt(ny) + ' Hz, so the dots trace the true tone.';
    else body = fmt(trueFreq) + ' Hz is above ' + fmt(ny) + ' Hz, so it folds to ' + fmt(sampleRate) + ' - ' +
      fmt(trueFreq) + ' = ' + fmt(a.apparent) + ' Hz.';
    bodyColor = 'dimgray';
  }
  textStyle(BOLD);
  const used = drawWrapped(title, px + 12, py + 8, pw - 24, lineH);
  textStyle(NORMAL);
  if (body) {
    fill(bodyColor);
    drawWrapped(body, px + 12, py + 12 + used, pw - 24, lineH);
  }
}

function drawControlLabels() {
  noStroke();
  fill(challengeActive ? 'gray' : 'black');
  textSize(defaultTextSize);
  textAlign(LEFT, CENTER);
  text('True frequency: ' + fmt(trueFreq) + ' Hz', 10, drawHeight + 20);
  text('Sample rate:', 10, drawHeight + 55);
  if (challengeActive) {
    fill('black');
    textAlign(RIGHT, CENTER);
    const scoreText = 'Score: ' + score + ' of 6';
    fitTextSize(scoreText, canvasWidth - 10 - row3End, defaultTextSize, 11);
    text(scoreText, canvasWidth - 10, drawHeight + 93);
  }
}

// Draw word-wrapped text line by line and return the height used
function drawWrapped(str, x, y, w, lineH) {
  const words = String(str).split(' ');
  const lines = [];
  let line = '';
  for (const word of words) {
    const trial = line ? line + ' ' + word : word;
    if (textWidth(trial) > w && line) {
      lines.push(line);
      line = word;
    } else {
      line = trial;
    }
  }
  if (line) lines.push(line);
  textAlign(LEFT, TOP);
  for (let i = 0; i < lines.length; i++) text(lines[i], x, y + i * lineH);
  return lines.length * lineH;
}

// Shrink the text size until the string fits the width (for narrow screens)
function fitTextSize(str, maxWidth, largest, smallest) {
  let size = largest;
  textSize(size);
  while (size > smallest && textWidth(str) > maxWidth) {
    size--;
    textSize(size);
  }
}

// ---------- responsive layout ----------
function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  positionControls();
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    canvasWidth = Math.floor(container.getBoundingClientRect().width);
  }
}
