// Frame Size and Update Time Calculator MicroSim
// CANVAS_HEIGHT: 620
// The learner sets a rectangle of pixels, the bytes per pixel and the SPI baud
// rate, and sees the bytes, bits and wire time. A challenge mode asks for 6
// answers (4 byte counts, 2 times) with one attempt each.
// Rules (from the chapter):
//   bytes = width x height x bytes per pixel
//   bits  = bytes x 8
//   time in seconds = bits / baud rate;  milliseconds = seconds x 1000
// Command bytes and Python overhead are NOT included (wire time only).

// ---- Canvas layout ----
let canvasWidth = 400;
let drawHeight = 470;
let controlHeight = 150;   // 4 control rows x 35 + 10
let canvasHeight = drawHeight + controlHeight;
let margin = 25;
let sliderLeftMargin = 140;
let defaultTextSize = 16;

// ---- Controls ----
let widthSlider, heightSlider, bppSelect, baudSelect;
let modeButton, answerInput, checkButton, nextButton;

// ---- Challenges (spec order) ----
// w, h, bpp, baud set the exploration controls to match each question
const challenges = [
  { q: 'Bytes in a full 360 by 360 frame at 2 bytes per pixel', unit: 'bytes',
    w: 360, h: 360, bpp: 2, baud: 24000000, answer: 259200, shown: '259200', tol: 0,
    why: '360 x 360 x 2 = 259,200.' },
  { q: 'Bytes in the 100 by 30 clock-digit box at 2 bytes per pixel', unit: 'bytes',
    w: 100, h: 30, bpp: 2, baud: 24000000, answer: 6000, shown: '6000', tol: 0,
    why: '100 x 30 x 2 = 6,000.' },
  { q: 'Bytes in a full 360 by 360 frame at 3 bytes per pixel', unit: 'bytes',
    w: 360, h: 360, bpp: 3, baud: 24000000, answer: 388800, shown: '388800', tol: 0,
    why: '360 x 360 x 3 = 388,800.' },
  { q: 'Bytes in the 200 by 22 level meter at 2 bytes per pixel', unit: 'bytes',
    w: 200, h: 22, bpp: 2, baud: 24000000, answer: 8800, shown: '8800', tol: 0,
    why: '200 x 22 x 2 = 8,800.' },
  { q: 'Milliseconds to send the 100 by 30 box at 24,000,000 bits per second', unit: 'ms',
    w: 100, h: 30, bpp: 2, baud: 24000000, answer: 2.0, shown: '2.0', tol: 0.1,
    why: '6,000 bytes x 8 = 48,000 bits, divided by 24,000,000 is 0.002 s.' },
  { q: 'Milliseconds to send a full 2-byte frame at 12,000,000 bits per second', unit: 'ms',
    w: 360, h: 360, bpp: 2, baud: 12000000, answer: 172.8, shown: '172.8', tol: 0.1,
    why: '259,200 x 8 = 2,073,600 bits, divided by 12,000,000 is 0.1728 s.' }
];

// ---- State ----
let mode = 'explore';   // 'explore' | 'challenge' | 'done'
let challengeIndex = 0;
let score = 0;
let answered = false;
let feedback = '';
let feedbackKind = 'info';

// ---- The model: real calculations ----
function frameBytes(w, h, bpp) { return w * h * bpp; }
function frameBits(bytes) { return bytes * 8; }
function wireMs(bits, baud) { return bits / baud * 1000; }

function fmt(n) { return n.toLocaleString('en-US'); }

// Milliseconds with 2 decimals, or 3 significant digits for tiny times
function fmtMs(ms) { return ms >= 1 ? nf(ms, 1, 2) : String(Number(ms.toPrecision(3))); }

// Seconds to 4 significant digits, e.g. 0.0864
function fmtSec(s) { return String(Number(s.toPrecision(4))); }

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  // Sanity check: the challenge answers must equal the computed values
  for (const c of challenges) {
    const bytes = frameBytes(c.w, c.h, c.bpp);
    const v = c.unit === 'bytes' ? bytes : wireMs(frameBits(bytes), c.baud);
    if (Math.abs(v - c.answer) > 1e-9) console.warn('Answer mismatch: ' + c.q + ' computed ' + v);
  }

  // Create ALL controls first
  widthSlider = createSlider(1, 360, 360, 1);
  heightSlider = createSlider(1, 360, 360, 1);

  bppSelect = createSelect();
  bppSelect.option('1', '1');
  bppSelect.option('2', '2');
  bppSelect.option('3', '3');
  bppSelect.selected('2');

  baudSelect = createSelect();
  baudSelect.option('8,000,000', '8000000');
  baudSelect.option('12,000,000', '12000000');
  baudSelect.option('24,000,000', '24000000');
  baudSelect.selected('24000000');

  modeButton = createButton('Start Challenges');
  modeButton.mousePressed(toggleMode);

  answerInput = createInput('', 'text');
  answerInput.attribute('placeholder', 'your answer');
  answerInput.attribute('aria-label', 'Your answer as a number');
  answerInput.size(95);
  answerInput.elt.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') checkAnswer();
  });

  checkButton = createButton('Check');
  checkButton.mousePressed(checkAnswer);

  nextButton = createButton('Next');
  nextButton.mousePressed(nextChallenge);

  // Then position them
  positionControls();
  showModeControls();

  describe('Frame size and update time calculator. Sliders set the width and height of a ' +
    'rectangle of pixels on the 360 by 360 round display, and menus set the bytes per pixel ' +
    'and the SPI baud rate. The sim shows bytes = width x height x bytes per pixel, bits = ' +
    'bytes x 8, and the wire time in milliseconds. A challenge mode asks six questions.', LABEL);
}

function positionControls() {
  const y0 = drawHeight + 5;
  widthSlider.position(sliderLeftMargin, y0);
  heightSlider.position(sliderLeftMargin, y0 + 35);
  const w = canvasWidth - sliderLeftMargin - margin;
  widthSlider.size(w);
  heightSlider.size(w);
  bppSelect.position(135, y0 + 70);
  baudSelect.position(272, y0 + 70);
  modeButton.position(10, y0 + 105);
  answerInput.position(165, y0 + 105);
  checkButton.position(272, y0 + 105);
  nextButton.position(335, y0 + 105);
}

function setControlsDisabled(disabled) {
  for (const c of [widthSlider, heightSlider, bppSelect, baudSelect]) {
    if (disabled) c.attribute('disabled', '');
    else c.removeAttribute('disabled');
  }
}

function showModeControls() {
  if (mode === 'challenge') {
    setControlsDisabled(true);
    modeButton.html('Back to Explore');
    answerInput.show();
    checkButton.show();
    if (answered) {
      nextButton.show();
      answerInput.attribute('disabled', '');
      checkButton.attribute('disabled', '');
    } else {
      nextButton.hide();
      answerInput.removeAttribute('disabled');
      checkButton.removeAttribute('disabled');
    }
  } else {
    setControlsDisabled(false);
    modeButton.html(mode === 'done' ? 'Try Challenges Again' : 'Start Challenges');
    answerInput.hide();
    checkButton.hide();
    nextButton.hide();
  }
}

function setParams(w, h, bpp, baud) {
  widthSlider.value(w);
  heightSlider.value(h);
  bppSelect.selected(String(bpp));
  baudSelect.selected(String(baud));
}

function toggleMode() {
  if (mode === 'challenge') {
    mode = 'explore';
    feedback = '';
    setParams(360, 360, 2, 24000000);
    showModeControls();
  } else {
    mode = 'challenge';
    challengeIndex = 0;
    score = 0;
    loadChallenge();
  }
}

function loadChallenge() {
  const c = challenges[challengeIndex];
  setParams(c.w, c.h, c.bpp, c.baud);
  answered = false;
  feedback = '';
  feedbackKind = 'info';
  answerInput.value('');
  showModeControls();
}

function checkAnswer() {
  if (mode !== 'challenge' || answered) return;
  const c = challenges[challengeIndex];
  const raw = answerInput.value().trim().replace(/[,_\s]/g, '');
  const v = Number(raw);
  if (raw === '' || !isFinite(v)) {
    // Not a number: does not use up the one attempt
    feedback = 'Type a number first, without units (for example 1234 or 5.6).';
    feedbackKind = 'info';
    return;
  }
  const correct = Math.abs(v - c.answer) <= c.tol + 1e-9;
  answered = true;
  if (correct) {
    score++;
    feedback = 'Correct: ' + c.why;
    feedbackKind = 'good';
  } else {
    feedback = 'Not quite. The answer is ' + c.shown + ': ' + c.why;
    feedbackKind = 'bad';
  }
  showModeControls();
}

function nextChallenge() {
  if (mode !== 'challenge' || !answered) return;
  challengeIndex++;
  if (challengeIndex >= challenges.length) {
    mode = 'done';
    setParams(360, 360, 2, 24000000);
    const mastery = score >= 5 ? 'Mastery reached (5 of 6 needed).' : 'Mastery needs 5 of 6. Explore and try again.';
    feedback = 'You scored ' + score + ' of 6. ' + mastery + ' Notice: a full frame takes about 86 ms of ' +
      'wire time at 24 MHz, while the 100 by 30 box takes about 2 ms. The calculator leaves out ' +
      'command bytes and Python overhead.';
    feedbackKind = score >= 5 ? 'good' : 'info';
    showModeControls();
  } else {
    loadChallenge();
  }
}

function draw() {
  updateCanvasSize();

  stroke('silver');
  strokeWeight(1);
  fill('aliceblue');
  rect(0, 0, canvasWidth, drawHeight);
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  const w = widthSlider.value();
  const h = heightSlider.value();
  const bpp = Number(bppSelect.value());
  const baud = Number(baudSelect.value());
  const bytes = frameBytes(w, h, bpp);
  const bits = frameBits(bytes);
  const ms = wireMs(bits, baud);
  const reveal = (mode !== 'challenge') || answered;

  // Title
  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(canvasWidth < 480 ? 20 : 24);
  text('Frame Size and Update Time', canvasWidth / 2, 8);

  // Status line
  textSize(defaultTextSize);
  textAlign(LEFT, TOP);
  textStyle(BOLD);
  noStroke();
  let status = 'How long does it take to send this?';
  if (mode === 'challenge') status = 'Challenge ' + (challengeIndex + 1) + ' of 6';
  if (mode === 'done') status = 'Challenges finished';
  text(status, margin, 40);
  textStyle(NORMAL);
  if (mode !== 'explore') {
    textAlign(RIGHT, TOP);
    noStroke();
    text('Score: ' + score + ' of 6', canvasWidth - margin, 40);
  }

  // Screen picture
  const S = canvasWidth < 480 ? 130 : 150;
  drawScreen(margin, 68, S, w, h);

  // Panel to the right of the screen
  const px = margin + S + 20;
  const pw = canvasWidth - px - margin;
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  if (mode === 'challenge') {
    const c = challenges[challengeIndex];
    textStyle(BOLD);
    textSize(defaultTextSize);
    text(c.q + '?', px, 70, pw, 90);
    textStyle(NORMAL);
    fill('darkblue');
    textSize(15);
    text(answered ? '' : 'Type your answer in ' + (c.unit === 'bytes' ? 'bytes' : 'milliseconds') + ' below.',
      px, 165, pw, 40);
  } else {
    textSize(defaultTextSize);
    text('Rectangle: ' + w + ' x ' + h + ' pixels', px, 70, pw, 22);
    text('Bytes per pixel: ' + bpp, px, 94, pw, 22);
    text('Baud: ' + fmt(baud) + ' bits/s', px, 118, pw, 22);
    textStyle(BOLD);
    textSize(26);
    fill('darkblue');
    text(fmtMs(ms) + ' ms', px, 148, pw, 34);
    textStyle(NORMAL);
    textSize(14);
    fill('dimgray');
    text('of wire time', px, 182, pw, 20);
  }

  // Formula lines (full width under the screen)
  drawFormulas(w, h, bpp, baud, bytes, bits, ms, reveal);
  drawFeedback();
  drawControlLabels(w, h);
}

// The 360 x 360 frame with the visible circle and the chosen rectangle at the center
function drawScreen(x, y, S, w, h) {
  const k = S / 360;
  stroke('dimgray');
  strokeWeight(1);
  fill('gainsboro');
  rect(x, y, S, S);
  fill('black');
  circle(x + S / 2, y + S / 2, S);
  // Rectangle centered at pixel (180, 180)
  const rx = x + (180 - w / 2) * k;
  const ry = y + (180 - h / 2) * k;
  stroke('darkorange');
  strokeWeight(2);
  fill(255, 165, 0, 150);
  rect(rx, ry, max(1, w * k), max(1, h * k));
  noStroke();
  fill('black');
  textSize(13);
  textAlign(CENTER, TOP);
  text('orange = pixels sent', x + S / 2, y + S + 3);
}

function drawFormulas(w, h, bpp, baud, bytes, bits, ms, reveal) {
  const x = margin;
  let y = canvasWidth < 480 ? 232 : 252;
  const lw = canvasWidth - 2 * margin;
  const lh = 22;
  noStroke();
  textAlign(LEFT, TOP);
  textSize(canvasWidth < 480 ? 14 : 16);
  fill('black');
  // In challenge mode the time formula appears after the first challenge
  const showTime = (mode !== 'challenge') || challengeIndex > 0 || answered;
  if (reveal) {
    text('bytes = ' + w + ' x ' + h + ' x ' + bpp + ' = ' + fmt(bytes), x, y, lw, lh);
    y += lh;
    if (showTime) {
      text('bits = ' + fmt(bytes) + ' x 8 = ' + fmt(bits), x, y, lw, lh);
      y += lh;
      text('time = ' + fmt(bits) + ' / ' + fmt(baud) + ' s', x, y, lw, lh);
      y += lh;
      text('     = ' + fmtSec(bits / baud) + ' s = ' + fmtMs(ms) + ' ms', x, y, lw, lh);
      y += lh;
    }
  } else {
    text('bytes = width x height x bytes per pixel', x, y, lw, lh);
    y += lh;
    if (showTime) {
      text('bits = bytes x 8', x, y, lw, lh);
      y += lh;
      text('milliseconds = bits / baud rate x 1000', x, y, lw, lh);
      y += lh;
    }
  }
  fill('dimgray');
  textSize(13);
  text('Wire time only: command bytes and Python overhead are not included.', x, y + 4, lw, 36);
}

function drawFeedback() {
  if (!feedback) return;
  const x = margin;
  const y = 386;
  const w = canvasWidth - 2 * margin;
  const h = drawHeight - y - 8;
  stroke(feedbackKind === 'good' ? 'seagreen' : (feedbackKind === 'bad' ? 'darkorange' : 'silver'));
  strokeWeight(1);
  fill(feedbackKind === 'good' ? 'honeydew' : (feedbackKind === 'bad' ? 'seashell' : 'white'));
  rect(x - 6, y - 4, w + 12, h + 4, 8);
  noStroke();
  fill('black');
  textSize(15);
  textAlign(LEFT, TOP);
  text(feedback, x, y, w, h);
}

function drawControlLabels(w, h) {
  noStroke();
  fill('black');
  textSize(defaultTextSize);
  textAlign(LEFT, CENTER);
  text('Width: ' + w + ' px', 10, drawHeight + 15);
  text('Height: ' + h + ' px', 10, drawHeight + 50);
  text('Bytes per pixel:', 10, drawHeight + 85);
  text('Baud rate:', 192, drawHeight + 85);
}

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
  if (typeof widthSlider !== 'undefined') {
    const w = canvasWidth - sliderLeftMargin - margin;
    widthSlider.size(w);
    heightSlider.size(w);
  }
}
