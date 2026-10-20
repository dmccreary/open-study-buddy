// Template Score Explorer - p5.js MicroSim
// CANVAS_HEIGHT: 550
// Calculate a wake-word template score on a tiny window (3 frames x 2 bands):
// 1. mean subtraction: subtract each band's mean over the 3 frames;
// 2. unit normalization: length = square root of the sum of the 6 squares;
// 3. dot product with the template, divided by the length.
// Score = dot / length (0 if the length is below 0.000001).
// The template is already mean-subtracted and length 1. All windows are synthetic.

let canvasWidth = 800;
let drawHeight = 470;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

// windows are [frame][band]
const TEMPLATE = [[-0.5, 0.5], [0, 0], [0.5, -0.5]];
const WORKED = [[10, 2], [10, 4], [10, 6]];
const CHALLENGES = [
  { name: 'W1', w: [[3, 9], [4, 8], [5, 7]], score: 1.00,
    why: "Subtracting the band means leaves exactly the template's shape, so the angle is 0." },
  { name: 'W2', w: [[2, 12], [4, 10], [6, 8]], score: 1.00,
    why: 'Twice the strength, same shape: normalizing divides by 4 and gives the template, so strength does not matter.' },
  { name: 'W3', w: [[5, 7], [4, 8], [3, 9]], score: -1.00,
    why: 'The same band movements in the opposite order are the opposite pattern, so the score is -1.' },
  { name: 'W4', w: [[3, 6], [4, 8], [6, 7]], score: 0.39,
    why: 'Only partly the same shape: the dot product is 1.00 but the length is 2.58, so the score is 1.00 / 2.58.' }
];
const STAGE_NAMES = ['the window', '1. mean subtraction', '2. unit normalization', '3. dot product and score'];

let mode = 'explore';
let stage = 0;
let chIndex = 0;
let submitted = false;
let finished = false;
let results = [];
let feedback = '';
let feedbackCorrect = false;

let modeButton, answerInput, submitButton, nextButton, stageButton, resetButton;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  modeButton = createButton('Start the 4 challenges');
  modeButton.mousePressed(toggleMode);
  answerInput = createInput('', 'number');
  answerInput.size(90);
  answerInput.attribute('step', '0.01');
  answerInput.attribute('placeholder', 'score');
  answerInput.elt.addEventListener('keydown', e => { if (e.key === 'Enter') submitAnswer(); });
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next challenge');
  nextButton.mousePressed(nextChallenge);
  stageButton = createButton('Next stage');
  stageButton.mousePressed(() => { if (stage < 3) stage++; updateControlStates(); });
  resetButton = createButton('Back to start');
  resetButton.mousePressed(() => { stage = 0; updateControlStates(); });
  for (const el of [modeButton, answerInput, submitButton, nextButton, stageButton, resetButton]) el.style('font-size', '16px');

  positionControls();
  updateControlStates();

  describe('A tiny wake-word window of 3 frames and 2 bands shown as a grid of numbers next to the template grid. Stepping through three stages shows the band means subtracted, the length of the result, and the dot product with the template divided by the length, which is the score. A four-challenge quiz asks for the score of four windows.', LABEL);
}

// the three stages of the score, with every intermediate number
function scoreParts(w) {
  const means = [0, 1].map(b => (w[0][b] + w[1][b] + w[2][b]) / 3);
  const sub = w.map(f => f.map((v, b) => v - means[b]));
  let sq = 0;
  let dot = 0;
  const prods = [];
  for (let f = 0; f < 3; f++) {
    for (let b = 0; b < 2; b++) {
      sq += sub[f][b] * sub[f][b];
      prods.push(sub[f][b] * TEMPLATE[f][b]);
      dot += sub[f][b] * TEMPLATE[f][b];
    }
  }
  const len = Math.sqrt(sq);
  return { means: means, sub: sub, len: len, dot: dot, prods: prods, score: len < 1e-6 ? 0 : dot / len };
}

function fmt(v) {
  const r = Math.round(v * 100) / 100;
  return (Object.is(r, -0) ? 0 : r).toFixed(2).replace(/\.00$/, '');
}

// negative terms in brackets, so (-2)² is not read as -(2²)
function paren(v) {
  const s = fmt(v);
  return s.startsWith('-') ? '(' + s + ')' : s;
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
  text('Template Score Explorer', canvasWidth / 2, 10);
  textSize(16);
  fill('dimgray');
  let status;
  const name = mode === 'explore' ? 'E' : CHALLENGES[min(chIndex, 3)].name;
  if (mode === 'explore') status = 'Explore: worked window E (synthetic), stage: ' + STAGE_NAMES[stage];
  else if (finished) status = 'All 4 challenges done   |   Score: ' + countCorrect() + ' of 4';
  else status = 'Challenge ' + (chIndex + 1) + ' of 4: window ' + name + ' (synthetic)   |   Score: ' + countCorrect() + ' of 4';
  text(status, canvasWidth / 2, 42);

  const w = mode === 'explore' ? WORKED : CHALLENGES[min(chIndex, 3)].w;
  const shown = mode === 'explore' ? stage : (submitted || finished ? 3 : 0);
  const p = scoreParts(w);

  // three grids side by side: window, after subtraction, template
  const gw = min(190, (canvasWidth - 2 * margin - 40) / 3);
  const gx = [margin + 5, margin + 5 + gw + 20, margin + 5 + 2 * (gw + 20)];
  drawGrid('Window ' + name, w, gx[0], 76, gw, false);
  if (shown >= 1) drawGrid('After subtraction', p.sub, gx[1], 76, gw, true);
  else drawPlaceholder('After subtraction', gx[1], 76, gw);
  drawGrid('Template', TEMPLATE, gx[2], 76, gw, true);

  drawStages(p, shown, margin, 196, canvasWidth - 2 * margin);
  drawPanel(margin, 374, canvasWidth - 2 * margin, drawHeight - 382);
}

// 2 rows (bands) x 3 columns (frames), colored by sign
function drawGrid(title, g, x, y, w, signed) {
  const cw = (w - 56) / 3;
  const ch = 30;
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(15);
  textStyle(BOLD);
  text(title, x, y);
  textStyle(NORMAL);
  textSize(13);
  fill('dimgray');
  textAlign(RIGHT, TOP);
  text('frame', x + 52, y + 20);
  for (let f = 0; f < 3; f++) {
    textAlign(CENTER, TOP);
    text(f, x + 56 + (f + 0.5) * cw, y + 20);
  }
  for (let b = 0; b < 2; b++) {
    noStroke();
    fill('dimgray');
    textAlign(RIGHT, CENTER);
    textSize(13);
    text('band ' + b, x + 52, y + 50 + b * ch);
    for (let f = 0; f < 3; f++) {
      const v = g[f][b];
      let c = 'white';
      if (signed && v > 1e-9) c = color(255, 200 - min(150, v * 60), 200 - min(150, v * 60));
      if (signed && v < -1e-9) c = color(200 - min(150, -v * 60), 215 - min(150, -v * 60), 255);
      stroke('silver');
      fill(c);
      rect(x + 56 + f * cw, y + 36 + b * ch, cw - 2, ch - 2, 3);
      noStroke();
      fill('black');
      textAlign(CENTER, CENTER);
      textSize(15);
      text(fmt(v), x + 56 + f * cw + cw / 2, y + 36 + b * ch + ch / 2 - 1);
    }
  }
}

function drawPlaceholder(title, x, y, w) {
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(15);
  textStyle(BOLD);
  text(title, x, y);
  textStyle(NORMAL);
  stroke('silver');
  fill('whitesmoke');
  rect(x + 56, y + 36, w - 58, 58, 3);
  noStroke();
  fill('dimgray');
  textAlign(CENTER, CENTER);
  textSize(14);
  text('stage 1', x + 56 + (w - 58) / 2, y + 65);
}

function drawStages(p, shown, x, y, w) {
  fill(255, 255, 255, 235);
  stroke('silver');
  rect(x, y, w, 170, 10);
  noStroke();
  textAlign(LEFT, TOP);
  textSize(16);
  const lx = x + 12;
  const rows = [
    ['1. Mean subtraction', 'band means ' + fmt(p.means[0]) + ' and ' + fmt(p.means[1]) + '; subtract each band\'s mean from its 3 values'],
    ['2. Unit normalization', 'length = sqrt(' + p.sub.flat().map(v => paren(v) + '\u00b2').join(' + ') + ') = ' + p.len.toFixed(2)],
    ['3. Dot product', 'dot = ' + p.prods.map(v => paren(v)).join(' + ') + ' = ' + fmt(p.dot)],
    ['   Score', 'dot / length = ' + fmt(p.dot) + ' / ' + p.len.toFixed(2) + ' = ' + p.score.toFixed(2)]
  ];
  let yy = y + 10;
  for (let i = 0; i < rows.length; i++) {
    const on = shown >= min(i + 1, 3);
    fill(on ? 'black' : 'silver');
    textStyle(BOLD);
    text(rows[i][0], lx, yy);
    textStyle(NORMAL);
    fill(on ? (i === 3 ? 'navy' : 'black') : 'silver');
    yy = drawWrapped(on ? rows[i][1] : '...', lx + 200, yy, w - 224, 19) + 8;
  }
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
    fill('navy');
    textStyle(ITALIC);
    text('What does this window score against the template?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped(stage < 3 ? 'Press Next stage to see each step. Watch band 0 of E: it never moves, so what does it add?' :
      'Band 0 of E never moved, so after subtraction it is all 0 and adds nothing. The score is -0.71.', x + pad, yy + 22, tw, 20);
    return;
  }
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 3 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 4. ' + (sc >= 3 ? 'Mastery reached.' : 'Mastery is 3 of 4.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('W1 and W2 differ in strength but score the same, and W3 has W1\'s numbers in a different order. What does the score really measure?', x + pad, yy + 24, tw, 20);
    return;
  }
  if (!submitted) {
    fill('navy');
    textStyle(ITALIC);
    text('What does window ' + CHALLENGES[chIndex].name + ' score against the template?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Subtract the band means, find the length, take the dot product with the template, then divide. Type the score (2 decimals; within 0.02 counts) and Submit.', x + pad, yy + 22, tw, 20);
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
    chIndex = 0;
    results = [];
    submitted = false;
    finished = false;
  } else {
    mode = 'explore';
    stage = 0;
  }
  answerInput.value('');
  updateControlStates();
}

function submitAnswer() {
  if (mode !== 'quiz' || submitted || finished) return;
  const raw = answerInput.value().trim();
  if (raw === '' || isNaN(Number(raw))) return;
  const c = CHALLENGES[chIndex];
  const correct = abs(Number(raw) - c.score) <= 0.02 + 1e-9;
  results[chIndex] = correct;
  feedbackCorrect = correct;
  feedback = correct ? 'Correct: ' + c.why : 'Not quite. The score is ' + c.score.toFixed(2) + ': ' + c.why;
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
  modeButton.html(quiz ? 'Back to explore' : 'Start the 4 challenges');
  setEnabled(answerInput, quiz && !submitted && !finished);
  setEnabled(submitButton, quiz && !submitted && !finished);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(chIndex === CHALLENGES.length - 1 ? 'See score' : 'Next challenge');
  setEnabled(stageButton, !quiz && stage < 3);
  setEnabled(resetButton, !quiz && stage > 0);
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
  layoutRow([stageButton, resetButton], 10, drawHeight + 44, 10);
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
