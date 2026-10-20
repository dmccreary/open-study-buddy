// Speed-Up Chooser - p5.js MicroSim
// CANVAS_HEIGHT: 555
// Recommend the simplest implementation whose worst-case pass time fits the
// frame budget minus the display reserve. limit = budget - reserve; an option
// fits when its time <= limit. The answer is the first option that fits in
// the order Plain Python, Viper, Assembly; if none fits, "None fits".
// All times are illustrative, not measurements of the kit. The 40 ms budget
// and 10 ms reserve are the values in Chapter 10, "The Real-Time Constraint
// and the Frame Overrun".

let canvasWidth = 800;
let drawHeight = 440;
let controlHeight = 115;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

const OPTIONS = ['Plain Python', 'Viper', 'Assembly'];
const SCENARIOS = [
  { budget: 40, reserve: 10, t: [120, 6, 4], answer: 'Viper',
    why: 'Plain Python is over the limit; viper and assembly both fit, and viper is the simpler.' },
  { budget: 40, reserve: 10, t: [18, 5, 3], answer: 'Plain Python',
    why: 'Plain Python already fits, so any faster option costs readability for nothing.' },
  { budget: 40, reserve: 10, t: [90, 34, 12], answer: 'Assembly',
    why: 'Viper at 34 ms is over the 30 ms limit; assembly at 12 ms fits.' },
  { budget: 40, reserve: 10, t: [200, 80, 45], answer: 'None fits',
    why: 'Even assembly at 45 ms is over the limit, so the work itself must be reduced.' },
  { budget: 20, reserve: 5, t: [60, 14, 7], answer: 'Viper',
    why: 'Viper at 14 ms is within the 15 ms limit, so assembly is not needed.' },
  { budget: 40, reserve: 10, t: [31, 12, 9], answer: 'Viper',
    why: 'Plain Python at 31 ms is just over the limit of 30 ms; viper at 12 ms fits.' }
];

let mode = 'explore';
let scIndex = 0;
let submitted = false;
let finished = false;
let results = [];
let feedback = '';
let feedbackCorrect = false;

let modeButton, choiceSelect, submitButton, nextButton;
let budgetSlider, reserveSlider, timeSliders = [];

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  modeButton = createButton('Start the 6 scenarios');
  modeButton.mousePressed(toggleMode);
  choiceSelect = createSelect();
  for (const o of ['choose', 'Plain Python', 'Viper', 'Assembly', 'None fits']) choiceSelect.option(o);
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next scenario');
  nextButton.mousePressed(nextScenario);
  for (const el of [modeButton, choiceSelect, submitButton, nextButton]) el.style('font-size', '16px');

  // the exploration panel opens on scenario 1's numbers
  budgetSlider = createSlider(10, 80, 40, 5);
  reserveSlider = createSlider(0, 20, 10, 5);
  const start = SCENARIOS[0].t;
  for (let i = 0; i < 3; i++) timeSliders.push(createSlider(1, 300, start[i], 1));

  positionControls();
  updateControlStates();

  describe('A frame budget bar split into the audio-work limit and the display reserve, above three horizontal bars for the worst-case pass times of Plain Python, Viper and Assembly, ordered from simplest to hardest. A dashed line marks the limit. Sliders set the budget, reserve and the three times; in the quiz the learner recommends the simplest option that fits, or None fits.', LABEL);
}

function currentNumbers() {
  if (mode === 'explore') {
    return { budget: Number(budgetSlider.value()), reserve: Number(reserveSlider.value()), t: timeSliders.map(s => Number(s.value())) };
  }
  return SCENARIOS[min(scIndex, SCENARIOS.length - 1)];
}

function recommend(n) {
  const limit = n.budget - n.reserve;
  for (let i = 0; i < 3; i++) if (n.t[i] <= limit) return OPTIONS[i];
  return 'None fits';
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
  text('Speed-Up Chooser', canvasWidth / 2, 10);
  textSize(16);
  fill('dimgray');
  let status;
  if (mode === 'explore') status = 'Explore: all times are illustrative, not measured';
  else if (finished) status = 'All 6 scenarios done   |   Score: ' + countCorrect() + ' of 6';
  else status = 'Scenario ' + (scIndex + 1) + ' of 6 (illustrative, not measured)   |   Score: ' + countCorrect() + ' of 6';
  text(status, canvasWidth / 2, 42);

  const n = currentNumbers();
  const reveal = mode === 'explore' || submitted;
  drawBudgetBar(n, 72);
  drawBars(n, reveal, 150);
  drawPanel(n, margin, 340, canvasWidth - 2 * margin, drawHeight - 350);

  // slider labels
  noStroke();
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  fill(mode === 'explore' ? 'black' : 'silver');
  const half = canvasWidth / 2;
  text('Budget: ' + budgetSlider.value() + ' ms', 10, drawHeight + 58);
  text('Reserve: ' + reserveSlider.value() + ' ms', half + 10, drawHeight + 58);
  const third = canvasWidth / 3;
  const short = ['Plain', 'Viper', 'Asm'];
  for (let i = 0; i < 3; i++) text(short[i] + ': ' + timeSliders[i].value(), i * third + 10, drawHeight + 93);
}

// the frame: audio-work limit plus display reserve
function drawBudgetBar(n, y) {
  const x0 = 150;
  const x1 = canvasWidth - 30;
  const limit = n.budget - n.reserve;
  const w = x1 - x0;
  noStroke();
  fill('black');
  textAlign(RIGHT, CENTER);
  textSize(16);
  text('One frame', x0 - 10, y + 22);
  stroke('steelblue');
  fill('honeydew');
  rect(x0, y + 8, w * limit / n.budget, 28);
  fill('lavender');
  rect(x0 + w * limit / n.budget, y + 8, w * n.reserve / n.budget, 28);
  noStroke();
  fill('darkgreen');
  textAlign(CENTER, CENTER);
  textSize(15);
  if (limit > 0) text('audio work limit: ' + n.budget + ' - ' + n.reserve + ' = ' + limit + ' ms', x0 + w * limit / n.budget / 2, y + 22);
  fill('indigo');
  if (n.reserve > 0) text('display ' + n.reserve + ' ms', x0 + w * (limit + n.reserve / 2) / n.budget, y + 22);
  fill('dimgray');
  textAlign(RIGHT, TOP);
  textSize(14);
  text('frame budget ' + n.budget + ' ms', x1, y + 40);
}

// worst-case pass time of each option against the limit
function drawBars(n, reveal, y) {
  const x0 = 150;
  const x1 = canvasWidth - 140;
  const limit = n.budget - n.reserve;
  const xMax = n.budget * 2;
  const X = t => x0 + (x1 - x0) * min(t, xMax) / xMax;
  const bh = 34;
  const gap = 18;

  noStroke();
  fill('dimgray');
  textAlign(LEFT, TOP);
  textSize(14);
  text('worst-case pass time (ms), simplest at the top', x0, y - 36);

  for (let i = 0; i < 3; i++) {
    const yy = y + i * (bh + gap);
    const t = n.t[i];
    const fits = t <= limit;
    noStroke();
    fill('black');
    textAlign(RIGHT, CENTER);
    textSize(16);
    textStyle(BOLD);
    text(OPTIONS[i], x0 - 10, yy + bh / 2);
    textStyle(NORMAL);
    fill(reveal ? (fits ? 'seagreen' : 'indianred') : 'slategray');
    rect(x0, yy, X(t) - x0, bh, 0, 6, 6, 0);
    if (t > xMax) {
      // clipped bar: draw an arrow tip to show it continues
      triangle(X(xMax), yy - 4, X(xMax) + 14, yy + bh / 2, X(xMax), yy + bh + 4);
    }
    fill('black');
    textAlign(LEFT, CENTER);
    const lbl = t + ' ms' + (reveal ? (fits ? '  fits' : '  over') : '');
    text(lbl, t > xMax ? X(xMax) + 18 : X(t) + 8, yy + bh / 2);
  }
  const yb = y + 3 * (bh + gap) - gap;
  // limit and budget lines
  stroke('darkgreen');
  strokeWeight(2);
  drawingContext.setLineDash([6, 4]);
  line(X(limit), y - 6, X(limit), yb + 6);
  drawingContext.setLineDash([]);
  stroke('gray');
  strokeWeight(1);
  line(X(n.budget), y - 6, X(n.budget), yb + 6);
  noStroke();
  textSize(14);
  textAlign(CENTER, TOP);
  // limit label above the bars, budget label below, so they never collide
  fill('darkgreen');
  textAlign(CENTER, BOTTOM);
  text('limit ' + limit, X(limit), y - 7);
  textAlign(CENTER, TOP);
  fill('gray');
  text('budget ' + n.budget, X(n.budget), yb + 8);
  fill('dimgray');
  textAlign(RIGHT, TOP);
  text('axis to ' + xMax + ' ms; longer bars are cut', canvasWidth - 20, yb + 8);
}

function drawPanel(n, x, y, w, h) {
  fill(255, 255, 255, 235);
  stroke('silver');
  rect(x, y, w, h, 10);
  const pad = 10;
  const tw = w - 2 * pad;
  const yy = y + 8;
  const limit = n.budget - n.reserve;
  noStroke();
  textAlign(LEFT, TOP);
  textSize(16);
  if (mode === 'explore') {
    fill('navy');
    textStyle(ITALIC);
    text('Which is the simplest option that fits?', x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    const r = recommend(n);
    drawWrapped('Limit = ' + n.budget + ' - ' + n.reserve + ' = ' + limit + ' ms.  Simplest option that fits: ' + r +
      '.  Try raising the reserve: can a fitting option stop fitting?', x + pad, yy + 22, tw, 20);
    return;
  }
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 5 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 6. ' + (sc >= 5 ? 'Mastery reached.' : 'Mastery is 5 of 6.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('In scenario 2 the fastest option was not the right one. What rule did you use to choose, and when is no option good enough?', x + pad, yy + 24, tw, 20);
    return;
  }
  if (!submitted) {
    fill('navy');
    textStyle(ITALIC);
    text('Which is the simplest option that fits?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Budget ' + n.budget + ' ms, reserve ' + n.reserve + ' ms. Work out the limit, compare each worst-case time, and choose below. One attempt.', x + pad, yy + 22, tw, 20);
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
    scIndex = 0;
    results = [];
    submitted = false;
    finished = false;
  } else {
    mode = 'explore';
  }
  choiceSelect.selected('choose');
  updateControlStates();
}

function submitAnswer() {
  if (mode !== 'quiz' || submitted || finished) return;
  const c = choiceSelect.value();
  if (c === 'choose') return;
  const s = SCENARIOS[scIndex];
  const correct = c === s.answer;
  results[scIndex] = correct;
  feedbackCorrect = correct;
  feedback = correct ? 'Correct: ' + s.why : 'Not quite. The answer is ' + s.answer + ': ' + s.why;
  submitted = true;
  updateControlStates();
}

function nextScenario() {
  if (!submitted) return;
  if (scIndex === SCENARIOS.length - 1) finished = true;
  else { scIndex++; submitted = false; }
  choiceSelect.selected('choose');
  updateControlStates();
}

function setEnabled(el, on) {
  el.elt.disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  modeButton.html(quiz ? 'Back to explore' : 'Start the 6 scenarios');
  setEnabled(choiceSelect, quiz && !submitted && !finished);
  setEnabled(submitButton, quiz && !submitted && !finished);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(scIndex === SCENARIOS.length - 1 ? 'See score' : 'Next scenario');
  for (const s of [budgetSlider, reserveSlider, ...timeSliders]) setEnabled(s, !quiz);
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
  layoutRow([modeButton, choiceSelect, submitButton, nextButton], 10, drawHeight + 8, 10);
  const half = canvasWidth / 2;
  budgetSlider.position(130, drawHeight + 48);
  budgetSlider.size(half - 130 - 20);
  reserveSlider.position(half + 135, drawHeight + 48);
  reserveSlider.size(half - 135 - margin);
  const third = canvasWidth / 3;
  for (let i = 0; i < 3; i++) {
    timeSliders[i].position(i * third + 95, drawHeight + 83);
    timeSliders[i].size(third - 95 - 15);
  }
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
