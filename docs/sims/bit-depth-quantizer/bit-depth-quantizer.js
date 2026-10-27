// Bit Depth Quantizer
// CANVAS_HEIGHT: 500
// One cycle of a sine wave and its quantized staircase. The learner moves the
// bit depth from 1 to 16 bits and sees the number of levels double with each
// bit, then answers 5 challenge questions (two attempts each).
//
// Rules (from the chapter spec):
//   * levels = 2 to the power n
//   * levels are evenly spaced from -1.0 to +1.0 with spacing 2 / (levels - 1)
//   * a sample is quantized to the nearest level; exactly halfway rounds up

// ---------- canvas layout ----------
let canvasWidth = 400;
let drawHeight = 420;
let controlHeight = 80;      // 2 rows of controls: 2 x 35 + 10
let canvasHeight = drawHeight + controlHeight;
let margin = 25;
let sliderLeftMargin = 150;
let defaultTextSize = 16;

// ---------- quantizer math ----------
function levelsFor(bits) {
  return Math.pow(2, bits);
}

function stepFor(levels) {
  return 2 / (levels - 1);
}

// Nearest level between -1 and +1; halfway rounds up (floor(v + 0.5))
function quantize(x, levels) {
  const step = stepFor(levels);
  const index = Math.floor((x + 1) / step + 0.5);
  return Math.min(1, Math.max(-1, -1 + index * step));
}

// ---------- challenge questions (Content table) ----------
const questions = [
  { q: 'How many levels does 3-bit audio have?', answer: 8, why: '2 x 2 x 2 = 8.' },
  { q: 'How many levels does 8-bit audio have?', answer: 256, why: '2 to the power 8 is 256.' },
  { q: "How many levels does the Pico's 12-bit ADC have?", answer: 4096, why: '2 to the power 12 is 4,096.' },
  { q: 'How many levels does 16-bit audio have?', answer: 65536, why: '2 to the power 16 is 65,536.' },
  { q: 'What is the smallest bit depth with at least 1,000 levels?', answer: 10,
    why: '2 to the power 9 is 512, which is too few, and 2 to the power 10 is 1,024.' }
];

// ---------- state ----------
let bitDepth = 4;
let challengeActive = false;
let challengeDone = false;
let qIndex = 0;
let attempts = 0;
let questionClosed = false;  // answered correctly or missed twice
let score = 0;
let feedback = '';
let feedbackColor = 'black';

// ---------- controls ----------
let bitSlider, challengeButton, answerInput, submitButton;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  // Create every control first, then position them
  bitSlider = createSlider(1, 16, 4, 1);
  challengeButton = createButton('Start challenges');
  challengeButton.mousePressed(pressChallengeButton);
  answerInput = createInput('', 'text');
  answerInput.attribute('placeholder', 'answer');
  answerInput.attribute('inputmode', 'numeric');
  answerInput.size(100);
  answerInput.elt.addEventListener('keydown', (e) => { if (e.key === 'Enter') submitAnswer(); });
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);

  for (const b of [challengeButton, answerInput, submitButton]) b.style('font-size', '15px');
  positionControls();
  updateControlStates();

  describe('One cycle of a sine wave drawn in gray with its quantized staircase in blue. ' +
    'A bit-depth slider from 1 to 16 bits changes the number of levels, which doubles with each bit. ' +
    'Five challenge questions ask the learner to calculate levels from bit depth.', LABEL);
}

function positionControls() {
  bitSlider.position(sliderLeftMargin, drawHeight + 10);
  bitSlider.size(canvasWidth - sliderLeftMargin - margin);
  layoutRow2();
}

// Row 2 is laid out from the rendered widths, because the button label changes
let row2End = 0;              // right edge of the row 2 controls, so the score never overlaps them
function layoutRow2() {
  let x = 10;
  const y = drawHeight + 45;
  answerInput.size(canvasWidth < 500 ? 65 : 100);
  for (const c of [challengeButton, answerInput, submitButton]) {
    c.position(x, y);
    x += (c.elt.offsetWidth || 110) + 10;
  }
  row2End = x;
}

function setEnabled(ctrl, on) {
  ctrl.elt.disabled = !on;
}

function updateControlStates() {
  // The slider shows the level count, so it is locked while a question is open
  setEnabled(bitSlider, !challengeActive);
  setEnabled(answerInput, challengeActive && !questionClosed);
  setEnabled(submitButton, challengeActive && !questionClosed);
  if (!challengeActive) {
    challengeButton.html(challengeDone ? 'Start challenges again' : 'Start challenges');
    setEnabled(challengeButton, true);
  } else {
    challengeButton.html(qIndex === questions.length - 1 ? 'Show score' : 'Next question');
    setEnabled(challengeButton, questionClosed);
  }
  layoutRow2();
}

// ---------- challenge actions ----------
function pressChallengeButton() {
  if (!challengeActive) {
    challengeActive = true;
    challengeDone = false;
    qIndex = 0;
    score = 0;
    startQuestion();
  } else if (questionClosed) {
    if (qIndex === questions.length - 1) {
      challengeActive = false;
      challengeDone = true;
      feedback = '';
      answerInput.value('');
    } else {
      qIndex++;
      startQuestion();
    }
  }
  updateControlStates();
}

function startQuestion() {
  attempts = 0;
  questionClosed = false;
  feedback = '';
  answerInput.value('');
  updateControlStates();
  answerInput.elt.focus();
}

function submitAnswer() {
  if (!challengeActive || questionClosed) return;
  const raw = String(answerInput.value()).trim();
  if (!/^\d+$/.test(raw)) {
    // Not a whole number: ask again without using an attempt
    feedback = 'Type a whole number without commas, for example 512.';
    feedbackColor = 'dimgray';
    return;
  }
  const value = parseInt(raw, 10);
  const q = questions[qIndex];
  attempts++;
  if (value === q.answer) {
    score++;
    feedback = 'Correct: ' + q.why;
    feedbackColor = 'darkgreen';
    questionClosed = true;
  } else if (attempts === 1) {
    feedback = 'Not quite. Think about doubling for each bit. Try again.';
    feedbackColor = 'firebrick';
    answerInput.value('');
  } else {
    feedback = 'The answer is ' + q.answer + ': ' + q.why;
    feedbackColor = 'firebrick';
    questionClosed = true;
  }
  updateControlStates();
}

// ---------- drawing ----------
function draw() {
  updateCanvasSize();
  bitDepth = bitSlider.value();

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
  text('Bit Depth Quantizer', canvasWidth / 2, 10);
  textSize(canvasWidth < 560 ? 13 : 14);
  fill('dimgray');
  text('One cycle of a sine wave (gray) and the staircase of its quantized values (blue).', 10, 40, canvasWidth - 20, 36);

  drawPlot();
  drawLevelInfo();
  drawPanel();
  drawControlLabels();
}

function drawPlot() {
  const left = margin + 30;
  const right = canvasWidth - margin;
  const top = 78;
  const bottom = 250;
  const levels = levelsFor(bitDepth);
  const yOf = v => map(v, -1, 1, bottom, top);

  // faint level lines when there are few enough to see
  if (levels <= 64) {
    stroke(200, 210, 230);
    strokeWeight(1);
    for (let i = 0; i < levels; i++) {
      const y = yOf(-1 + i * stepFor(levels));
      line(left, y, right, y);
    }
  }
  // axes
  stroke('dimgray');
  line(left, top, left, bottom);
  line(left, yOf(0), right, yOf(0));
  noStroke();
  fill('black');
  textSize(13);
  textAlign(RIGHT, CENTER);
  text('+1', left - 6, yOf(1));
  text('0', left - 6, yOf(0));
  text('-1', left - 6, yOf(-1));

  // true sine wave
  stroke('gray');
  strokeWeight(2);
  noFill();
  beginShape();
  for (let px = left; px <= right; px++) {
    const u = (px - left) / (right - left);
    vertex(px, yOf(Math.sin(TWO_PI * u)));
  }
  endShape();

  // quantized staircase: hold each level until the next one, then jump
  stroke('royalblue');
  strokeWeight(3);
  beginShape();
  let prevY = null;
  for (let px = left; px <= right; px++) {
    const u = (px - left) / (right - left);
    const y = yOf(quantize(Math.sin(TWO_PI * u), levels));
    if (prevY !== null && y !== prevY) vertex(px, prevY);
    vertex(px, y);
    prevY = y;
  }
  endShape();
  strokeWeight(1);
}

function drawLevelInfo() {
  const levels = levelsFor(bitDepth);
  const step = stepFor(levels);
  noStroke();
  textAlign(LEFT, TOP);
  fill('black');
  textSize(18);
  textStyle(BOLD);
  if (challengeActive) {
    fill('dimgray');
    text('Level count hidden during the challenges', margin, 260);
  } else {
    text(bitDepth + (bitDepth === 1 ? ' bit' : ' bits') + ': ' + levels.toLocaleString('en-US') + ' levels', margin, 260);
  }
  textStyle(NORMAL);
  fill('black');
  if (!challengeActive) {
    let info = 'Step between levels = 2 / (' + levels.toLocaleString('en-US') + ' - 1) = ' + formatSmall(step) +
      '    Largest rounding error = ' + formatSmall(step / 2);
    fitTextSize(info, canvasWidth - 2 * margin, 15, 11);
    if (textWidth(info) > canvasWidth - 2 * margin) {
      // narrow screens: shorter wording so the line is not clipped
      info = 'Step = 2 / (' + levels.toLocaleString('en-US') + ' - 1) = ' + formatSmall(step) +
        '   Max error = ' + formatSmall(step / 2);
      fitTextSize(info, canvasWidth - 2 * margin, 15, 10);
    }
    text(info, margin, 286);
  }
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

function formatSmall(v) {
  return v >= 0.001 ? v.toFixed(4) : v.toExponential(2);
}

function drawPanel() {
  const px = margin;
  const py = 312;
  const pw = canvasWidth - 2 * margin;
  const ph = drawHeight - py - 8;
  stroke(200);
  fill(255, 255, 255, 230);
  rect(px, py, pw, ph, 10);
  noStroke();
  textAlign(LEFT, TOP);
  textSize(canvasWidth < 560 ? 15 : 16);
  fill('black');

  let title, body, bodyColor;
  if (challengeActive) {
    title = 'Question ' + (qIndex + 1) + ' of 5: ' + questions[qIndex].q;
    body = feedback;
    bodyColor = feedbackColor;
  } else if (challengeDone) {
    title = 'Challenges done. Score: ' + score + ' of 5' + (score === 5 ? ' (mastery reached)' : ' (mastery is 5 of 5)');
    body = 'Notice that adding one bit always doubles the number of levels.';
    bodyColor = 'dimgray';
  } else {
    title = 'What happens to the staircase as you add bits?';
    body = 'Move the bit-depth slider, then press Start challenges.';
    bodyColor = 'dimgray';
  }
  textStyle(BOLD);
  const used = drawWrapped(title, px + 12, py + 8, pw - 24, 20);
  textStyle(NORMAL);
  if (body) {
    fill(bodyColor);
    drawWrapped(body, px + 12, py + 12 + used, pw - 24, 20);
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

function drawControlLabels() {
  noStroke();
  fill(challengeActive ? 'gray' : 'black');
  textSize(defaultTextSize);
  textAlign(LEFT, CENTER);
  text('Bit depth: ' + bitDepth + (bitDepth === 1 ? ' bit' : ' bits'), 10, drawHeight + 20);
  // running score at the right end of row 2
  if (challengeActive) {
    fill('black');
    textAlign(RIGHT, CENTER);
    const scoreText = 'Score: ' + score + ' of 5';
    fitTextSize(scoreText, canvasWidth - 10 - row2End, defaultTextSize, 11);
    text(scoreText, canvasWidth - 10, drawHeight + 58);
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
