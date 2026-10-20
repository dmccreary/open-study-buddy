// Q15 Calculator - p5.js MicroSim
// CANVAS_HEIGHT: 530
// Calculate Q15 fixed-point products. A Q15 integer q stands for the real
// value q / 32768, so 16384 is 0.5 and the range -32768 to 32767 covers
// -1.0 up to just under +1.0. The product of two Q15 numbers is
// result = (a x b) >> 15, where >> is an arithmetic shift right that keeps
// the sign and rounds toward minus infinity: result = floor(a x b / 32768).
// A result fits in 16 bits when -32768 <= result <= 32767.
// The six pairs are the table in Chapter 10 "Fixed-Point Math"
// (src/chapters/10-high-performance-micropython/08-q15-fixed-point.py).

let canvasWidth = 800;
let drawHeight = 450;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

const Q = 32768;
const MIN16 = -32768;
const MAX16 = 32767;
const PAIRS = [
  { a: 16384, b: 16384, answer: 8192, fits: true, why: '16384 x 16384 = 268,435,456, and 268,435,456 >> 15 = 8192.' },
  { a: 32767, b: 32767, answer: 32766, fits: true, why: '32767 x 32767 = 1,073,676,289, and >> 15 gives 32766.' },
  { a: -16384, b: 16384, answer: -8192, fits: true, why: 'The product -268,435,456 >> 15 is -8192.' },
  { a: 3, b: 3, answer: 0, fits: true, why: '3 x 3 = 9, and 9 >> 15 is 0: the result is smaller than one Q15 step.' },
  { a: -3, b: 3, answer: -1, fits: true, why: '-9 >> 15 rounds toward minus infinity, giving -1, not 0.' },
  { a: -32768, b: -32768, answer: 32768, fits: false, askFit: true, why: 'The product is +1,073,741,824, and >> 15 gives 32768, one more than the largest 16-bit value.' }
];

let mode = 'explore';
let pairIndex = 0;
let submitted = false;
let finished = false;
let results = [];
let feedback = '';
let feedbackCorrect = false;

let modeButton, resultLabel, answerInput, fitSelect, submitButton, nextButton;
let aLabel, aInput, bLabel, bInput;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  modeButton = createButton('Start the 6 pairs');
  modeButton.mousePressed(toggleMode);
  resultLabel = createSpan('Result:');
  answerInput = createInput('', 'number');
  answerInput.size(100);
  answerInput.elt.addEventListener('keydown', e => { if (e.key === 'Enter') submitAnswer(); });
  fitSelect = createSelect();
  for (const o of ['choose', 'Fits in 16 bits', 'Does not fit']) fitSelect.option(o);
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next pair');
  nextButton.mousePressed(nextPair);
  aLabel = createSpan('Explore  a:');
  aInput = createInput('16384', 'number');
  bLabel = createSpan('b:');
  bInput = createInput('16384', 'number');
  for (const inp of [aInput, bInput]) {
    inp.size(100);
    inp.attribute('min', String(MIN16));
    inp.attribute('max', String(MAX16));
    inp.attribute('step', '1');
  }
  for (const el of [modeButton, resultLabel, answerInput, fitSelect, submitButton, nextButton, aLabel, aInput, bLabel, bInput]) {
    el.style('font-size', '16px');
  }

  positionControls();
  updateControlStates();

  describe('A Q15 fixed-point calculator. Two Q15 integers a and b are multiplied; the sim shows the full product, the product shifted right by 15 bits, the real values each integer stands for, and whether the result fits in a signed 16-bit number, with a number line from -1 to +1. A six-pair quiz asks for the shifted result.', LABEL);
}

// read an explore input as a whole number in the Q15 range
function readQ(inp) {
  let v = Math.round(Number(inp.value()));
  if (isNaN(v)) v = 0;
  return { v: constrain(v, MIN16, MAX16), clamped: v < MIN16 || v > MAX16 || String(inp.value()).trim() === '' };
}

function q15(a, b) {
  const product = a * b;                  // exact: |a x b| <= 2**30
  const result = Math.floor(product / Q); // arithmetic shift right by 15
  return { product: product, result: result, fits: result >= MIN16 && result <= MAX16 };
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
  text('Q15 Calculator', canvasWidth / 2, 10);
  textSize(16);
  fill('dimgray');
  let status;
  if (mode === 'explore') status = 'Explore: type any two Q15 integers from -32768 to 32767';
  else if (finished) status = 'All 6 pairs done   |   Score: ' + countCorrect() + ' of 6';
  else status = 'Pair ' + (pairIndex + 1) + ' of 6   |   Score: ' + countCorrect() + ' of 6';
  text(status, canvasWidth / 2, 42);

  // formula banner
  fill('white');
  stroke('steelblue');
  rect(margin, 70, canvasWidth - 2 * margin, 40, 8);
  noStroke();
  fill('navy');
  textAlign(CENTER, CENTER);
  textSize(18);
  text('result = (a x b) >> 15     (>> keeps the sign and rounds toward minus infinity)', canvasWidth / 2, 90);

  let a;
  let b;
  let warn = '';
  if (mode === 'explore') {
    const ra = readQ(aInput);
    const rb = readQ(bInput);
    a = ra.v;
    b = rb.v;
    if (ra.clamped || rb.clamped) warn = 'Inputs are whole numbers from -32768 to 32767; out-of-range values are clamped.';
  } else {
    a = PAIRS[min(pairIndex, 5)].a;
    b = PAIRS[min(pairIndex, 5)].b;
  }
  const reveal = mode === 'explore' || submitted;
  drawSteps(a, b, reveal, warn, margin, 120, canvasWidth - 2 * margin, 160);
  drawNumberLine(a, b, reveal, 322);
  drawPanel(margin, 362, canvasWidth - 2 * margin, drawHeight - 372);
}

function fmt(n) {
  return n.toLocaleString('en-US');
}

function realTxt(q) {
  return (q / Q).toFixed(5).replace(/0+$/, '').replace(/\.$/, '.0');
}

function drawSteps(a, b, reveal, warn, x, y, w, h) {
  fill(255, 255, 255, 235);
  stroke('silver');
  rect(x, y, w, h, 10);
  const c = q15(a, b);
  const lx = x + 14;
  noStroke();
  textAlign(LEFT, TOP);
  textSize(17);
  fill('black');
  text('a = ' + fmt(a) + '   (stands for ' + realTxt(a) + ')        b = ' + fmt(b) + '   (stands for ' + realTxt(b) + ')', lx, y + 12);
  if (!reveal) {
    fill('dimgray');
    textSize(16);
    drawWrapped('Multiply, then shift right by 15 (divide by 32,768 and round toward minus infinity). The steps appear after you submit.', lx, y + 48, w - 28, 22);
    return;
  }
  text('1.  full product  a x b = ' + fmt(c.product), lx, y + 44);
  text('2.  shift  ' + fmt(c.product) + ' >> 15 = floor(' + fmt(c.product) + ' / 32,768) = ' + fmt(c.result), lx, y + 72);
  text('3.  real values  ' + realTxt(a) + ' x ' + realTxt(b) + ' = ' + (a * b / Q / Q).toFixed(6).replace(/0+$/, '').replace(/\.$/, '.0') +
    ',   result ' + fmt(c.result) + ' / 32,768 = ' + (c.result / Q).toFixed(6).replace(/0+$/, '').replace(/\.$/, '.0'), lx, y + 100);
  fill(c.fits ? 'darkgreen' : 'firebrick');
  textStyle(BOLD);
  text('4.  fits in 16 bits (-32,768 to 32,767)?  ' + (c.fits ? 'yes' : 'NO: ' + fmt(c.result) + ' is too large'), lx, y + 128);
  textStyle(NORMAL);
  if (warn) {
    fill('darkorange');
    textSize(14);
    textAlign(RIGHT, TOP);
    text(warn, x + w - 12, y + h - 20);
  }
}

// real-value number line from -1 to +1 showing a, b and the result
function drawNumberLine(a, b, reveal, y) {
  const x0 = 60;
  const x1 = canvasWidth - 60;
  const X = r => x0 + (x1 - x0) * (r + 1) / 2;
  stroke('black');
  strokeWeight(2);
  line(x0, y, x1, y);
  strokeWeight(1);
  noStroke();
  textSize(14);
  textAlign(CENTER, TOP);
  for (const r of [-1, -0.5, 0, 0.5, 1]) {
    stroke('black');
    line(X(r), y - 5, X(r), y + 5);
    noStroke();
    fill('dimgray');
    text(r === 1 ? '+1.0 (not in Q15)' : r.toFixed(1), X(r), y + 8);
  }
  // the gap at +1.0: Q15 cannot hold it
  fill('firebrick');
  circle(X(1), y, 8);
  const dots = [{ v: a, c: 'royalblue', t: 'a' }, { v: b, c: 'darkorange', t: 'b' }];
  if (reveal) dots.push({ v: q15(a, b).result, c: q15(a, b).fits ? 'seagreen' : 'firebrick', t: 'result' });
  for (let i = 0; i < dots.length; i++) {
    const d = dots[i];
    const px = X(constrain(d.v / Q, -1.05, 1.05));
    fill(d.c);
    noStroke();
    circle(px, y, 12);
    textAlign(CENTER, BOTTOM);
    text(d.t, px, y - 8 - i * 12);
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
    text('What do you get when you multiply two Q15 numbers?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Type values for a and b below. Try 32767 x 32767 and then -32768 x -32768: one fits in 16 bits and one does not.', x + pad, yy + 22, tw, 20);
    return;
  }
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 5 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 6. ' + (sc >= 5 ? 'Mastery reached.' : 'Mastery is 5 of 6.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('Pairs 4 and 5 differ only in sign. Why is one result 0 and the other -1?', x + pad, yy + 24, tw, 20);
    return;
  }
  const p = PAIRS[pairIndex];
  if (!submitted) {
    fill('navy');
    textStyle(ITALIC);
    text('What is (' + fmt(p.a) + ' x ' + fmt(p.b) + ') >> 15?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Type the whole-number result' + (p.askFit ? ' and choose whether it fits in 16 bits' : '') + ', then Submit. One attempt.', x + pad, yy + 22, tw, 20);
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
    pairIndex = 0;
    results = [];
    submitted = false;
    finished = false;
  } else {
    mode = 'explore';
  }
  answerInput.value('');
  fitSelect.selected('choose');
  updateControlStates();
}

function submitAnswer() {
  if (mode !== 'quiz' || submitted || finished) return;
  const raw = answerInput.value().trim().replace(/,/g, '');
  if (raw === '' || isNaN(Number(raw))) return;
  const p = PAIRS[pairIndex];
  if (p.askFit && fitSelect.value() === 'choose') return;
  let correct = Number(raw) === p.answer;
  if (p.askFit) correct = correct && ((fitSelect.value() === 'Fits in 16 bits') === p.fits);
  results[pairIndex] = correct;
  feedbackCorrect = correct;
  const ans = fmt(p.answer) + (p.askFit ? (p.fits ? ', which fits' : ', which does not fit in 16 bits') : '');
  feedback = correct ? 'Correct: ' + p.why : 'Not quite. The answer is ' + ans + ': ' + p.why;
  submitted = true;
  updateControlStates();
}

function nextPair() {
  if (!submitted) return;
  if (pairIndex === PAIRS.length - 1) finished = true;
  else { pairIndex++; submitted = false; }
  answerInput.value('');
  fitSelect.selected('choose');
  updateControlStates();
}

function setEnabled(el, on) {
  el.elt.disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  const answering = quiz && !submitted && !finished;
  modeButton.html(quiz ? 'Back to explore' : 'Start the 6 pairs');
  setEnabled(answerInput, answering);
  setEnabled(submitButton, answering);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(pairIndex === PAIRS.length - 1 ? 'See score' : 'Next pair');
  // the fit question is part of pair 6 only
  if (quiz && !finished && PAIRS[pairIndex].askFit) fitSelect.show(); else fitSelect.hide();
  setEnabled(fitSelect, answering);
  setEnabled(aInput, !quiz);
  setEnabled(bInput, !quiz);
  positionControls();
}

function layoutRow(elems, x, y, gap) {
  for (const el of elems) {
    if (el.elt.style.display === 'none') continue;
    el.position(x, y);
    x += el.elt.offsetWidth + gap;
  }
  return x;
}

function positionControls() {
  layoutRow([modeButton, resultLabel, answerInput, fitSelect, submitButton, nextButton], 10, drawHeight + 8, 8);
  layoutRow([aLabel, aInput, bLabel, bInput], 10, drawHeight + 46, 8);
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
