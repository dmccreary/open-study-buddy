// Threshold Trade-Off Explorer - p5.js MicroSim
// CANVAS_HEIGHT: 560
// Judge which detection threshold, if any, meets stated error limits.
// False reject = a "Hey Pico" score below the threshold.
// False accept = an other-sound score at or above the threshold.
// The 2,000 synthetic scores are regenerated here with the same fixed-seed
// generator (seed 77) as src/chapters/12-wake-word-detection/01-detector-math-test.py:
// wake ~ min(1, 0.80 + 0.08 g), other ~ min(1, 0.35 + 0.15 g), g = sum of 12 uniforms - 6.

let canvasWidth = 800;
let drawHeight = 480;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let sliderLeftMargin = 170;
let defaultTextSize = 16;

const THRESHOLDS = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90];
const SCENARIOS = [
  { text: 'A quiet bedroom where missing the phrase is annoying', limits: 'False rejects at most 5%', maxFr: 5, maxFa: null, answer: '0.65',
    why: '0.50 to 0.65 meet the limit; 0.65 has the fewest false accepts of them (2.4%).' },
  { text: 'A busy classroom where a false wake-up is disruptive', limits: 'False accepts at most 1%', maxFr: null, maxFa: 1, answer: '0.70',
    why: '0.70 and higher meet the limit; 0.70 has the fewest false rejects of them (11.2%).' },
  { text: 'A demo that must almost never miss and almost never wake by mistake', limits: 'False rejects at most 10% and false accepts at most 1%', maxFr: 10, maxFa: 1, answer: 'none',
    why: 'At 0.65 false accepts are 2.4% (too many) and at 0.70 false rejects are 11.2% (too many). No threshold meets both; the detector needs to be better, not retuned.' },
  { text: 'A shared class device with a patient user', limits: 'False rejects at most 25% and false accepts at most 1%', maxFr: 25, maxFa: 1, answer: '0.70',
    why: '0.70 gives 11.2% and 0.8%. 0.75 has false rejects of 26.2%, which is over the limit.' }
];

let wake = [];
let other = [];
let mode = 'explore';
let scIndex = 0;
let submitted = false;
let finished = false;
let results = [];
let chosen = null;
let feedback = '';
let feedbackCorrect = false;

let modeButton, choiceSelect, submitButton, nextButton, thresholdSlider;

// the detector's tiny linear congruential generator (synth.Rng)
function makeRng(seed) {
  let state = seed >>> 0;
  const uniform = () => {
    state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
    return (state >>> 8) / 16777216.0;
  };
  return { gauss: () => { let s = 0; for (let i = 0; i < 12; i++) s += uniform(); return s - 6.0; } };
}

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  const rng = makeRng(77);
  for (let i = 0; i < 1000; i++) wake.push(Math.min(1.0, 0.80 + 0.08 * rng.gauss()));
  for (let i = 0; i < 1000; i++) other.push(Math.min(1.0, 0.35 + 0.15 * rng.gauss()));

  modeButton = createButton('Start the 4 scenarios');
  modeButton.mousePressed(toggleMode);
  choiceSelect = createSelect();
  choiceSelect.option('choose');
  for (const t of THRESHOLDS) choiceSelect.option(t.toFixed(2));
  choiceSelect.option('none');
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next scenario');
  nextButton.mousePressed(nextScenario);
  for (const el of [modeButton, choiceSelect, submitButton, nextButton]) el.style('font-size', '16px');
  thresholdSlider = createSlider(0.50, 0.90, 0.70, 0.05);
  thresholdSlider.size(canvasWidth - sliderLeftMargin - margin);

  positionControls();
  updateControlStates();

  describe('Two overlapping histograms of 1,000 wake-phrase scores and 1,000 other-sound scores, with a movable threshold line. The wake scores below the line are false rejects and the other scores at or above it are false accepts; both percentages are shown, next to a table for nine thresholds. A four-scenario quiz asks which threshold meets stated limits, or none.', LABEL);
}

// percentages for one threshold (computed from the scores, not looked up)
function rates(t) {
  const tt = t - 1e-9;
  const fr = 100 * wake.filter(s => s < tt).length / wake.length;
  const fa = 100 * other.filter(s => s >= tt).length / other.length;
  return { fr: fr, fa: fa };
}

function meets(sc, r) {
  return (sc.maxFr === null || r.fr <= sc.maxFr + 1e-9) && (sc.maxFa === null || r.fa <= sc.maxFa + 1e-9);
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
  text('Threshold Trade-Off Explorer', canvasWidth / 2, 10);
  textSize(16);
  fill('dimgray');
  let status;
  if (mode === 'explore') status = 'Explore: 2,000 synthetic scores';
  else if (finished) status = 'All 4 scenarios done   |   Score: ' + countCorrect() + ' of 4';
  else status = 'Scenario ' + (scIndex + 1) + ' of 4   |   Score: ' + countCorrect() + ' of 4';
  text(status, canvasWidth / 2, 42);

  const t = mode === 'explore' ? Number(thresholdSlider.value()) :
    (submitted && chosen !== null && chosen !== 'none' ? Number(chosen) : null);
  const tableX = canvasWidth * 0.64;
  drawHistograms(t, 30, 100, tableX - 30 - 20, 185);
  drawTable(t, tableX, 74, canvasWidth - tableX - margin);
  drawPanel(t, margin, 334, canvasWidth - 2 * margin, drawHeight - 342);

  noStroke();
  fill(mode === 'explore' ? 'black' : 'silver');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Threshold: ' + Number(thresholdSlider.value()).toFixed(2), 10, drawHeight + 58);
}

function drawHistograms(t, x, y, w, h) {
  const nb = 40;
  const binOf = s => Math.min(nb - 1, Math.floor(s * nb));
  const cw = new Array(nb).fill(0);
  const co = new Array(nb).fill(0);
  wake.forEach(s => cw[binOf(s)]++);
  other.forEach(s => { if (s >= 0) co[binOf(s)]++; });
  const top = max(...cw, ...co);
  const X = s => x + w * s;
  const Y = c => y + h - h * c / top;
  const bw = w / nb;
  for (let i = 0; i < nb; i++) {
    const lo = i / nb;
    // brighter bars are errors at this threshold
    const errO = t !== null && lo >= t - 1e-9;
    const errW = t !== null && lo + 1 / nb <= t + 1e-9;
    noStroke();
    fill(70, 130, 180, errO ? 230 : 110);
    rect(X(lo) + 0.5, Y(co[i]), bw - 1, y + h - Y(co[i]));
    fill(255, 140, 0, errW ? 230 : 110);
    rect(X(lo) + 0.5, Y(cw[i]), bw - 1, y + h - Y(cw[i]));
  }
  stroke('black');
  line(x, y + h, x + w, y + h);
  noStroke();
  fill('dimgray');
  textSize(13);
  textAlign(CENTER, TOP);
  for (let s = 0; s <= 1.0001; s += 0.2) text(s.toFixed(1), X(s), y + h + 4);
  text('score', x + w / 2, y + h + 20);
  // legend, above the plot
  textAlign(LEFT, TOP);
  fill(70, 130, 180);
  rect(x, y - 24, 12, 12);
  fill(255, 140, 0);
  rect(x + 110, y - 24, 12, 12);
  fill('black');
  text('other sounds', x + 16, y - 25);
  text('"Hey Pico"', x + 126, y - 25);
  if (t !== null) {
    fill('dimgray');
    textAlign(RIGHT, TOP);
    text('bright bars = errors', x + w, y - 25);
    stroke('black');
    strokeWeight(2);
    line(X(t), y - 4, X(t), y + h + 2);
    strokeWeight(1);
    // threshold value on a white backing beside the line
    noStroke();
    fill(255, 255, 255, 220);
    rect(X(t) + 3, y - 2, textWidth(t.toFixed(2)) + 6, 17, 3);
    fill('black');
    textAlign(LEFT, TOP);
    text(t.toFixed(2), X(t) + 6, y);
  }
}

function drawTable(t, x, y, w) {
  const rh = 22;
  const sc = mode === 'quiz' && submitted ? SCENARIOS[scIndex] : null;
  noStroke();
  textSize(14);
  fill('black');
  textStyle(BOLD);
  textAlign(LEFT, TOP);
  text('Threshold', x + 6, y);
  textAlign(RIGHT, TOP);
  text('False rej.', x + w * 0.66, y);
  text('False acc.', x + w - 6, y);
  textStyle(NORMAL);
  THRESHOLDS.forEach((th, i) => {
    const r = rates(th);
    const yy = y + 22 + i * rh;
    let bg = i % 2 ? 'whitesmoke' : 'white';
    if (sc && meets(sc, r)) bg = 'honeydew';
    if (sc && sc.answer === th.toFixed(2)) bg = 'gold';
    if (t !== null && abs(th - t) < 1e-6 && !sc) bg = 'lightyellow';
    stroke('gainsboro');
    fill(bg);
    rect(x, yy - 2, w, rh);
    noStroke();
    fill('black');
    textAlign(LEFT, TOP);
    text(th.toFixed(2) + (sc && meets(sc, r) ? '  meets' : ''), x + 6, yy + 1);
    textAlign(RIGHT, TOP);
    text(r.fr.toFixed(1) + '%', x + w * 0.66, yy + 1);
    text(r.fa.toFixed(1) + '%', x + w - 6, yy + 1);
  });
}

function drawPanel(t, x, y, w, h) {
  fill(255, 255, 255, 235);
  stroke('silver');
  rect(x, y, w, h, 10);
  const pad = 10;
  const tw = w - 2 * pad;
  let yy = y + 8;
  noStroke();
  textAlign(LEFT, TOP);
  textSize(16);
  if (mode === 'explore') {
    const r = rates(t);
    fill('navy');
    textStyle(ITALIC);
    text('How many of each error would you accept?', x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('At ' + t.toFixed(2) + ': false rejects ' + r.fr.toFixed(1) + '% (wake scores below the line), false accepts ' +
      r.fa.toFixed(1) + '% (other scores at or above it). Move the threshold: do the two numbers ever fall together?', x + pad, yy + 22, tw, 20);
    return;
  }
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 3 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 4. ' + (sc >= 3 ? 'Mastery reached.' : 'Mastery is 3 of 4.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('Scenario 3 had no answer. Why can moving the threshold never fix it, and what would?', x + pad, yy + 24, tw, 20);
    return;
  }
  const s = SCENARIOS[scIndex];
  fill('black');
  textStyle(BOLD);
  yy = drawWrapped(s.text + '. Limits: ' + s.limits + '.', x + pad, yy, tw, 20);
  textStyle(NORMAL);
  if (!submitted) {
    fill('dimgray');
    drawWrapped('Test each threshold in the table against the limits. Among those that meet them all, choose the one with the smallest sum of the two errors, or none. Then Submit.', x + pad, yy + 4, tw, 20);
    return;
  }
  fill(feedbackCorrect ? 'darkgreen' : 'firebrick');
  textStyle(BOLD);
  drawWrapped(feedback, x + pad, yy + 4, tw, 20);
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
  chosen = null;
  choiceSelect.selected('choose');
  updateControlStates();
}

function submitAnswer() {
  if (mode !== 'quiz' || submitted || finished) return;
  const c = choiceSelect.value();
  if (c === 'choose') return;
  const s = SCENARIOS[scIndex];
  chosen = c;
  const correct = c === s.answer;
  results[scIndex] = correct;
  feedbackCorrect = correct;
  let at = '';
  if (c !== 'none') {
    const r = rates(Number(c));
    at = ' (Your ' + c + ': ' + r.fr.toFixed(1) + '% false rejects, ' + r.fa.toFixed(1) + '% false accepts.)';
  }
  feedback = correct ? 'Correct: ' + s.why : 'Not quite. The answer is ' + s.answer + ': ' + s.why + at;
  submitted = true;
  updateControlStates();
}

function nextScenario() {
  if (!submitted) return;
  if (scIndex === SCENARIOS.length - 1) finished = true;
  else { scIndex++; submitted = false; }
  chosen = null;
  choiceSelect.selected('choose');
  updateControlStates();
}

function setEnabled(el, on) {
  el.elt.disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  modeButton.html(quiz ? 'Back to explore' : 'Start the 4 scenarios');
  setEnabled(choiceSelect, quiz && !submitted && !finished);
  setEnabled(submitButton, quiz && !submitted && !finished);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(scIndex === SCENARIOS.length - 1 ? 'See score' : 'Next scenario');
  setEnabled(thresholdSlider, !quiz);
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
  thresholdSlider.position(sliderLeftMargin, drawHeight + 48);
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  thresholdSlider.size(canvasWidth - sliderLeftMargin - margin);
  positionControls();
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = Math.floor(container.getBoundingClientRect().width);
}
