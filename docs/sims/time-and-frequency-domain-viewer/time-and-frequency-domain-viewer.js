// Time and Frequency Domain Viewer
// CANVAS_HEIGHT: 575
// Shows one sound two ways: the time-domain waveform over a 20 ms window and
// the frequency-domain bar chart. The learner explores two sine components,
// then matches 6 spectra to one of three waveforms.
//
// Rules (from the chapter spec):
//   * a waveform is the sum of its components, each a sine of its frequency and
//     amplitude, plotted over a 20 ms window
//   * the spectrum has one bar per component, at its frequency, with height
//     proportional to its amplitude; amplitude 0 has no bar
// The bars are not copied from the component list: they are measured with a
// discrete Fourier transform (DFT) of the 20 ms waveform. Every frequency used
// here is a multiple of 50 Hz, so each component lands exactly on a DFT bin and
// the measured amplitude equals the component amplitude. Two components at the
// same frequency add together into one bar, as they would in a real spectrum.

// ---------- canvas layout ----------
let canvasWidth = 400;
let drawHeight = 460;
let controlHeight = 115;     // 3 rows of controls: 3 x 35 + 10
let canvasHeight = drawHeight + controlHeight;
let margin = 25;
let defaultTextSize = 16;

const WINDOW_S = 0.020;      // 20 ms time window
const DFT_RATE = 20000;      // samples per second used for the DFT (well above 2 x 1,000 Hz)
const DFT_N = Math.round(WINDOW_S * DFT_RATE);   // 400 samples -> 50 Hz bin spacing
const MAX_FREQ = 1000;       // frequency axis 0 to 1,000 Hz

// ---------- challenges (Content table) ----------
// components are [frequency Hz, amplitude 0..1]
const challenges = [
  { spectrum: [[200, 1.0]],
    choices: [[[200, 1.0]], [[400, 1.0]], [[200, 0.5]]], correct: 0,
    why: 'The bar is at 200 Hz and full height.' },
  { spectrum: [[400, 1.0]],
    choices: [[[200, 1.0]], [[400, 1.0]], [[400, 0.5]]], correct: 1,
    why: 'The bar position gives the frequency: 400 Hz.' },
  { spectrum: [[200, 0.5]],
    choices: [[[200, 1.0]], [[400, 0.5]], [[200, 0.5]]], correct: 2,
    why: 'The bar height gives the amplitude: half.' },
  { spectrum: [[200, 1.0], [600, 0.5]],
    choices: [[[200, 1.0]], [[200, 1.0], [600, 0.5]], [[600, 1.0], [200, 0.5]]], correct: 1,
    why: 'Two bars mean two components, with the heights shown.' },
  { spectrum: [[300, 0.75], [900, 0.75]],
    choices: [[[300, 0.75], [900, 0.75]], [[300, 0.75]], [[900, 0.75], [300, 0.25]]], correct: 0,
    why: 'Both bars are the same height, at 300 and 900 Hz.' },
  { spectrum: [[100, 1.0], [300, 0.5], [500, 0.25]],
    choices: [[[100, 1.0], [300, 0.25], [500, 0.5]], [[100, 0.25], [300, 0.5], [500, 1.0]],
      [[100, 1.0], [300, 0.5], [500, 0.25]]], correct: 2,
    why: 'The bars fall in height from left to right: 1.0, 0.5, 0.25.' }
];
const LETTERS = ['A', 'B', 'C'];

// ---------- signal math ----------
// Value of the summed sine components at time t (seconds)
function waveValue(components, t) {
  let v = 0;
  for (const [f, a] of components) v += a * Math.sin(TWO_PI * f * t);
  return v;
}

// DFT of the 20 ms window: returns [{freq, amp}] for bins 50 Hz .. 1,000 Hz with amp > 0.005
function measureSpectrum(components) {
  const samples = [];
  for (let n = 0; n < DFT_N; n++) samples.push(waveValue(components, n / DFT_RATE));
  const bars = [];
  const binHz = DFT_RATE / DFT_N;   // 50 Hz
  for (let k = 1; k * binHz <= MAX_FREQ; k++) {
    let re = 0, im = 0;
    for (let n = 0; n < DFT_N; n++) {
      const angle = TWO_PI * k * n / DFT_N;
      re += samples[n] * Math.cos(angle);
      im -= samples[n] * Math.sin(angle);
    }
    const amp = 2 * Math.sqrt(re * re + im * im) / DFT_N;   // single-sided amplitude
    if (amp > 0.005) bars.push({ freq: k * binHz, amp: amp });
  }
  return bars;
}

// Largest absolute value of the waveform over the window
function peakOf(components) {
  let p = 0;
  for (let i = 0; i <= 2000; i++) p = Math.max(p, Math.abs(waveValue(components, (i / 2000) * WINDOW_S)));
  return p;
}

// ---------- state ----------
let challengeActive = false;
let challengeDone = false;
let cIndex = 0;
let pick = null;             // index of the learner's pick for the current challenge
let score = 0;
let feedback = '';
let exploreCache = { key: '', bars: [] };
let challengeCache = [];     // measured spectra and peaks per challenge

// ---------- controls ----------
let freq1Slider, amp1Slider, freq2Slider, amp2Slider;
let challengeButton, choiceButtons = [];

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  // Create every control first, then position them
  freq1Slider = createSlider(100, 1000, 200, 50);
  amp1Slider = createSlider(0, 1, 1.0, 0.25);
  freq2Slider = createSlider(100, 1000, 600, 50);
  amp2Slider = createSlider(0, 1, 0.5, 0.25);
  challengeButton = createButton('Start challenges');
  challengeButton.mousePressed(pressChallengeButton);
  for (let i = 0; i < 3; i++) {
    const b = createButton(LETTERS[i]);
    b.mousePressed(() => choose(i));
    choiceButtons.push(b);
  }
  for (const b of [challengeButton, ...choiceButtons]) b.style('font-size', '15px');

  // Pre-measure the challenge spectra once
  for (const c of challenges) {
    challengeCache.push({
      bars: measureSpectrum(c.spectrum),
      scale: Math.max(1, ...c.choices.map(peakOf))
    });
  }

  positionControls();
  updateControlStates();

  describe('Two views of one sound: a time-domain waveform over 20 milliseconds and a frequency-domain ' +
    'bar chart from 0 to 1,000 hertz. Sliders set the frequency and amplitude of two sine components. ' +
    'Six challenges ask the learner to pick the waveform that matches a bar chart.', LABEL);
}

function positionControls() {
  const half = canvasWidth / 2;
  freq1Slider.position(130, drawHeight + 10);
  amp1Slider.position(half + 100, drawHeight + 10);
  freq2Slider.position(130, drawHeight + 45);
  amp2Slider.position(half + 100, drawHeight + 45);
  sizeSliders();
  layoutRow3();
}

function sizeSliders() {
  const half = canvasWidth / 2;
  const leftW = Math.max(40, half - 130 - 15);
  const rightW = Math.max(40, canvasWidth - (half + 100) - margin);
  freq1Slider.size(leftW);
  freq2Slider.size(leftW);
  amp1Slider.size(rightW);
  amp2Slider.size(rightW);
}

function layoutRow3() {
  let x = 10;
  const y = drawHeight + 80;
  for (const c of [challengeButton, ...choiceButtons]) {
    c.position(x, y);
    x += (c.elt.offsetWidth || 40) + 10;
  }
}

function setEnabled(ctrl, on) {
  ctrl.elt.disabled = !on;
}

function updateControlStates() {
  for (const s of [freq1Slider, amp1Slider, freq2Slider, amp2Slider]) setEnabled(s, !challengeActive);
  for (const b of choiceButtons) {
    if (challengeActive) b.show(); else b.hide();
    setEnabled(b, challengeActive && pick === null);
  }
  if (!challengeActive) {
    challengeButton.html(challengeDone ? 'Start challenges again' : 'Start challenges');
    setEnabled(challengeButton, true);
  } else {
    challengeButton.html(cIndex === challenges.length - 1 ? 'Show score' : 'Next challenge');
    setEnabled(challengeButton, pick !== null);
  }
  layoutRow3();
}

// ---------- challenge actions ----------
function pressChallengeButton() {
  if (!challengeActive) {
    challengeActive = true;
    challengeDone = false;
    cIndex = 0;
    score = 0;
    pick = null;
    feedback = '';
  } else if (pick !== null) {
    if (cIndex === challenges.length - 1) {
      challengeActive = false;
      challengeDone = true;
    } else {
      cIndex++;
      pick = null;
      feedback = '';
    }
  }
  updateControlStates();
}

function choose(i) {
  if (!challengeActive || pick !== null) return;
  pick = i;
  const c = challenges[cIndex];
  if (i === c.correct) {
    score++;
    feedback = 'Correct: ' + c.why;
  } else {
    feedback = 'Not quite. ' + c.why;
  }
  updateControlStates();
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
  text('Time and Frequency Domain Viewer', canvasWidth / 2, 10);
  textSize(canvasWidth < 560 ? 13 : 14);
  fill('dimgray');
  text(canvasWidth < 560 ? 'Illustrative components.' :
    'Illustrative components. Bar position is frequency; bar height is amplitude.', 10, 40, canvasWidth - 20, 36);

  if (challengeActive) drawChallenge();
  else drawExplorer();
  drawControlLabels();
}

function exploreComponents() {
  return [[freq1Slider.value(), amp1Slider.value()], [freq2Slider.value(), amp2Slider.value()]];
}

function drawExplorer() {
  const comps = exploreComponents();
  const key = JSON.stringify(comps);
  if (key !== exploreCache.key) {
    exploreCache = { key: key, bars: measureSpectrum(comps) };
  }
  const left = margin + 30;
  const right = canvasWidth - margin;

  sectionLabel('Time domain: the waveform over 20 ms', left, 70);
  drawWaveform(comps, left, 90, right, 210, 2, true, 'steelblue');

  sectionLabel('Frequency domain: one bar per frequency', left, 240);
  const maxAmp = Math.max(1, ...exploreCache.bars.map(b => b.amp));
  drawSpectrum(exploreCache.bars, left, 262, right, 380, maxAmp, true);

  // panel
  const px = margin, py = 404, pw = canvasWidth - 2 * margin, ph = drawHeight - py - 8;
  stroke(200);
  fill(255, 255, 255, 230);
  rect(px, py, pw, ph, 10);
  noStroke();
  textSize(canvasWidth < 560 ? 14 : 16);
  const lineH = canvasWidth < 560 ? 17 : 20;
  fill('black');
  textStyle(BOLD);
  let title, body;
  if (challengeDone) {
    title = 'Challenges done. Score: ' + score + ' of 6' + (score >= 5 ? ' (mastery reached)' : ' (mastery is 5 of 6)');
    body = 'Bar position is frequency and bar height is amplitude.';
  } else {
    title = 'Which bars belong to which part of the wave?';
    body = 'Move the sliders and watch both views change together.';
  }
  const used = drawWrapped(title, px + 12, py + 6, pw - 24, lineH);
  textStyle(NORMAL);
  fill('dimgray');
  drawWrapped(body, px + 12, py + 8 + used, pw - 24, lineH);
}

function drawChallenge() {
  const c = challenges[cIndex];
  const cache = challengeCache[cIndex];
  const left = margin + 30;
  const right = canvasWidth - margin;

  sectionLabel('Challenge ' + (cIndex + 1) + ' of 6: which waveform has this spectrum?', margin, 68);
  drawSpectrum(cache.bars, left, 92, right, 172, 1, true);

  // three waveform choices sharing one vertical scale
  const rowTop = 200;
  const rowH = 62;
  for (let i = 0; i < 3; i++) {
    const top = rowTop + i * (rowH + 6);
    const bottom = top + rowH;
    // highlight after the pick
    if (pick !== null && (i === c.correct || i === pick)) {
      stroke(i === c.correct ? 'green' : 'crimson');
      strokeWeight(3);
      noFill();
      rect(margin - 4, top - 3, canvasWidth - 2 * margin + 8, rowH + 6, 6);
      strokeWeight(1);
    }
    noStroke();
    fill('black');
    textSize(20);
    textStyle(BOLD);
    textAlign(LEFT, CENTER);
    text(LETTERS[i], margin + 2, (top + bottom) / 2);
    textStyle(NORMAL);
    drawWaveform(c.choices[i], left, top, right, bottom, cache.scale, false, 'steelblue');
    if (pick !== null && i === c.correct) {
      noStroke();
      fill('green');
      textSize(14);
      textAlign(RIGHT, TOP);
      text('matches the spectrum', right - 4, top + 2);
    }
  }

  // feedback
  const fy = rowTop + 3 * (rowH + 6) + 4;
  noStroke();
  textSize(canvasWidth < 560 ? 14 : 16);
  const lineH = canvasWidth < 560 ? 17 : 20;
  if (pick === null) {
    fill('dimgray');
    drawWrapped('Pick A, B or C below.', margin, fy, canvasWidth - 2 * margin, lineH);
  } else {
    fill(pick === c.correct ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    drawWrapped(feedback, margin, fy, canvasWidth - 2 * margin, lineH);
    textStyle(NORMAL);
  }
}

function sectionLabel(str, x, y, reserve) {
  noStroke();
  fill('black');
  textStyle(BOLD);
  fitTextSize(str, canvasWidth - x - margin - (reserve || 0), 16, 10);
  textAlign(LEFT, TOP);
  text(str, x, y);
  textStyle(NORMAL);
}

// Plot the summed waveform between (left, top) and (right, bottom).
// scale is the amplitude at the top edge; dashed lines mark +1 and -1.
function drawWaveform(comps, left, top, right, bottom, scale, showAxis, col) {
  const mid = (top + bottom) / 2;
  const half = (bottom - top) / 2 - 2;
  noStroke();
  fill('white');
  rect(left, top, right - left, bottom - top);
  // +1 / -1 reference lines
  stroke('lightsteelblue');
  drawingContext.setLineDash([4, 4]);
  line(left, mid - half / scale, right, mid - half / scale);
  line(left, mid + half / scale, right, mid + half / scale);
  drawingContext.setLineDash([]);
  stroke('silver');
  line(left, mid, right, mid);
  noFill();
  rect(left, top, right - left, bottom - top);
  noStroke();
  fill('dimgray');
  textSize(12);
  textAlign(RIGHT, CENTER);
  text('+1', left - 4, mid - half / scale);
  text('-1', left - 4, mid + half / scale);
  // waveform
  stroke(col);
  strokeWeight(2);
  noFill();
  beginShape();
  const steps = Math.ceil((right - left) * 2);
  for (let i = 0; i <= steps; i++) {
    const t = (i / steps) * WINDOW_S;
    vertex(left + (i / steps) * (right - left), mid - (waveValue(comps, t) / scale) * half);
  }
  endShape();
  strokeWeight(1);
  if (showAxis) {
    noStroke();
    fill('black');
    textSize(13);
    for (let ms = 0; ms <= 20; ms += 5) {
      const x = left + (ms / 20) * (right - left);
      textAlign(ms === 20 ? RIGHT : (ms === 0 ? LEFT : CENTER), TOP);
      text(ms + (ms === 20 ? ' ms' : ''), x, bottom + 3);
    }
  }
}

// Bar chart from 0 to 1,000 Hz; maxAmp is the amplitude at the top edge
function drawSpectrum(bars, left, top, right, bottom, maxAmp, showLabels) {
  noStroke();
  fill('white');
  rect(left, top, right - left, bottom - top);
  stroke('silver');
  noFill();
  rect(left, top, right - left, bottom - top);
  const xOf = f => left + (f / MAX_FREQ) * (right - left);
  // frequency axis ticks
  noStroke();
  fill('black');
  textSize(12);
  for (let f = 0; f <= MAX_FREQ; f += 100) {
    stroke('silver');
    line(xOf(f), bottom, xOf(f), bottom + 4);
    noStroke();
    textAlign(f === MAX_FREQ ? RIGHT : (f === 0 ? LEFT : CENTER), TOP);
    if (canvasWidth >= 560 || f % 200 === 0) text(f === MAX_FREQ ? '1,000' : f, xOf(f), bottom + 5);
  }
  // axis unit, above the top-right corner of the chart
  fill('dimgray');
  textAlign(RIGHT, TOP);
  text('frequency (Hz)', right - 4, top + 3);
  // amplitude reference at 1.0
  stroke('lightsteelblue');
  drawingContext.setLineDash([4, 4]);
  const y1 = bottom - (1 / maxAmp) * (bottom - top - 18);
  line(left, y1, right, y1);
  drawingContext.setLineDash([]);
  noStroke();
  fill('dimgray');
  textAlign(RIGHT, CENTER);
  text('1.0', left - 4, y1);
  text('0', left - 4, bottom);
  // bars
  const barW = Math.max(6, (right - left) / 60);
  for (const b of bars) {
    const h = (b.amp / maxAmp) * (bottom - top - 18);
    noStroke();
    fill('darkorange');
    rect(xOf(b.freq) - barW / 2, bottom - h, barW, h);
    if (showLabels) {
      fill('black');
      textSize(12);
      textAlign(CENTER, BOTTOM);
      text(b.freq + ' Hz, ' + b.amp.toFixed(2), xOf(b.freq), bottom - h - 2);
    }
  }
}

function drawControlLabels() {
  const half = canvasWidth / 2;
  noStroke();
  fill(challengeActive ? 'gray' : 'black');
  textAlign(LEFT, CENTER);
  fitTextSize('Freq 1: 1,000 Hz', 115, defaultTextSize, 12);
  text('Freq 1: ' + freq1Slider.value().toLocaleString('en-US') + ' Hz', 10, drawHeight + 20);
  text('Freq 2: ' + freq2Slider.value().toLocaleString('en-US') + ' Hz', 10, drawHeight + 55);
  fitTextSize('Amp 1: 0.00', 85, defaultTextSize, 12);
  text('Amp 1: ' + amp1Slider.value().toFixed(2), half + 10, drawHeight + 20);
  text('Amp 2: ' + amp2Slider.value().toFixed(2), half + 10, drawHeight + 55);
  if (challengeActive) {
    fill('black');
    textSize(defaultTextSize);
    textAlign(RIGHT, CENTER);
    text('Score: ' + score + ' of 6', canvasWidth - 10, drawHeight + 93);
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
