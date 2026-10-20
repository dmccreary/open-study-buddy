// I2S Signal Reader - p5.js MicroSim
// CANVAS_HEIGHT: 540
// Interpret a simplified I2S waveform: three wires (bit clock, word select,
// serial data). A bit is sampled at each rising edge of the bit clock, most
// significant bit first. While word select is low the 8 bits belong to the
// left-channel word; while it is high they belong to the right-channel word.
// The value is a signed 8-bit number (two's complement). The 8-bit word length
// is a teaching simplification and the values are illustrative.

let canvasWidth = 800;
let drawHeight = 460;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

const BITS = 8;
const SLOTS = 2 * BITS;               // left word then right word
const EXAMPLE = '10110010';           // exploration example (not one of the six)
const WAVES = [
  { bits: '00000000', value: 0,    why: 'All bits are zero, so the value is 0.' },
  { bits: '01111111', value: 127,  why: 'The sign bit is 0 and all other bits are 1: 64+32+16+8+4+2+1 = 127.' },
  { bits: '10000000', value: -128, why: 'The sign bit is 1 and the rest are 0, the most negative value.' },
  { bits: '11111111', value: -1,   why: 'All ones in two\'s complement is -1.' },
  { bits: '00101101', value: 45,   why: '32 + 8 + 4 + 1 = 45.' },
  { bits: '11010011', value: -45,  why: 'The sign bit is 1. Flipping all bits gives 00101100, adding 1 gives 00101101 = 45, so the value is -45.' }
];
const RIGHT_WORD = '00000000';        // silent right channel
const WEIGHTS = [-128, 64, 32, 16, 8, 4, 2, 1];

let mode = 'explore';
let tick = 0;                         // rising edges seen so far (explore)
let waveIndex = 0;
let submitted = false;
let finished = false;
let results = [];
let feedback = '';
let feedbackCorrect = false;

let modeButton, answerInput, submitButton, nextButton, stepButton, resetButton;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  modeButton = createButton('Start the 6 waveforms');
  modeButton.mousePressed(toggleMode);
  answerInput = createInput('', 'number');
  answerInput.size(100);
  answerInput.attribute('placeholder', 'left value');
  answerInput.elt.addEventListener('keydown', e => { if (e.key === 'Enter') submitAnswer(); });
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next waveform');
  nextButton.mousePressed(nextWave);
  stepButton = createButton('Step one tick');
  stepButton.mousePressed(() => { if (tick < SLOTS) tick++; updateControlStates(); });
  resetButton = createButton('Back to start');
  resetButton.mousePressed(() => { tick = 0; updateControlStates(); });
  for (const el of [modeButton, answerInput, submitButton, nextButton, stepButton, resetButton]) el.style('font-size', '16px');

  positionControls();
  updateControlStates();

  describe('A simplified I2S timing diagram with three traces: the bit clock, the word select line, and the serial data line, across 16 bit-clock ticks. Word select is low for the 8-bit left-channel word and high for the right-channel word. In explore mode the learner steps one tick at a time and watches the bits collect into a register with two\'s-complement weights; in the quiz the learner reads the signed left-channel value.', LABEL);
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
  text('I2S Signal Reader', canvasWidth / 2, 10);
  textSize(16);
  fill('dimgray');
  let status;
  if (mode === 'explore') status = 'Explore: example waveform (illustrative), tick ' + tick + ' of ' + SLOTS;
  else if (finished) status = 'All 6 waveforms done   |   Score: ' + countCorrect() + ' of 6';
  else status = 'Waveform ' + (waveIndex + 1) + ' of 6 (illustrative)   |   Score: ' + countCorrect() + ' of 6';
  text(status, canvasWidth / 2, 42);

  const leftBits = mode === 'explore' ? EXAMPLE : WAVES[min(waveIndex, 5)].bits;
  const allBits = leftBits + RIGHT_WORD;
  // how many slots show their sampled digit / are "collected"
  const shown = mode === 'explore' ? tick : (submitted || finished ? SLOTS : 0);
  drawWaveform(allBits, shown, 72);
  drawRegister(leftBits, mode === 'explore' ? min(tick, BITS) : (submitted ? BITS : 0), 298);
  drawInfoPanel(allBits, margin, 368, canvasWidth - 2 * margin, drawHeight - 376);
}

// ---------- waveform ----------

function slotGeom() {
  const x0 = 150;
  const x1 = canvasWidth - margin - 10;
  return { x0: x0, sw: (x1 - x0) / SLOTS };
}

function drawWaveform(allBits, shown, top) {
  const g = slotGeom();
  const sx = i => g.x0 + i * g.sw;
  const rows = [
    { name: 'Bit clock (BCLK)', y: top + 64 },
    { name: 'Word select (WS)', y: top + 122 },
    { name: 'Serial data (SD)', y: top + 180 }
  ];
  const amp = 30;

  // left / right word brackets; the left word is highlighted after a submission
  noStroke();
  if (mode === 'quiz' && submitted) {
    fill(255, 215, 0, 90);
    rect(sx(0), top, BITS * g.sw, 212, 6);
  }
  fill('navy');
  textAlign(CENTER, TOP);
  textSize(14);
  text('LEFT word (WS low)', sx(BITS / 2), top + 2);
  text('RIGHT word (WS high)', sx(BITS + BITS / 2), top + 2);
  stroke('navy');
  line(sx(0) + 4, top + 20, sx(BITS) - 4, top + 20);
  line(sx(BITS) + 4, top + 20, sx(SLOTS) - 4, top + 20);

  // highlight the slot of the current tick in explore
  if (mode === 'explore' && tick > 0) {
    noStroke();
    fill(135, 206, 250, 110);
    rect(sx(tick - 1), top + 24, g.sw, 188);
  }

  // trace labels
  noStroke();
  fill('black');
  textAlign(RIGHT, CENTER);
  textSize(15);
  for (const r of rows) text(r.name, g.x0 - 10, r.y - amp / 2);

  // sampling instants: rising edges of the bit clock (middle of each slot)
  for (let i = 0; i < SLOTS; i++) {
    const xm = sx(i) + g.sw / 2;
    stroke(i < shown ? 'seagreen' : 'gainsboro');
    drawingContext.setLineDash([3, 4]);
    line(xm, rows[0].y - amp - 4, xm, rows[2].y + 6);
    drawingContext.setLineDash([]);
  }

  strokeWeight(2.5);
  noFill();
  // bit clock: low for the first half of each slot, high for the second
  stroke('dimgray');
  beginShape();
  for (let i = 0; i < SLOTS; i++) {
    vertex(sx(i), rows[0].y);
    vertex(sx(i) + g.sw / 2, rows[0].y);
    vertex(sx(i) + g.sw / 2, rows[0].y - amp);
    vertex(sx(i + 1), rows[0].y - amp);
  }
  vertex(sx(SLOTS), rows[0].y);
  endShape();
  // word select: low for the left word, high for the right word
  stroke('darkorange');
  beginShape();
  vertex(sx(0), rows[1].y);
  vertex(sx(BITS), rows[1].y);
  vertex(sx(BITS), rows[1].y - amp);
  vertex(sx(SLOTS), rows[1].y - amp);
  endShape();
  // serial data: one bit per slot, changing on the falling edge
  stroke('navy');
  beginShape();
  for (let i = 0; i < SLOTS; i++) {
    const y = allBits[i] === '1' ? rows[2].y - amp : rows[2].y;
    vertex(sx(i), y);
    vertex(sx(i + 1), y);
  }
  endShape();
  strokeWeight(1);

  // sampled digits under the data line
  noStroke();
  textAlign(CENTER, TOP);
  textSize(16);
  for (let i = 0; i < shown; i++) {
    fill(i < BITS ? 'navy' : 'gray');
    text(allBits[i], sx(i) + g.sw / 2, rows[2].y + 8);
  }
}

// register with two's-complement weights for the left word
function drawRegister(leftBits, filled, y) {
  const g = slotGeom();
  const bw = min(46, g.sw * 1.1);
  const x0 = g.x0;
  noStroke();
  fill('black');
  textAlign(RIGHT, CENTER);
  textSize(15);
  text('Left word', x0 - 10, y + 16);
  text('weight', x0 - 10, y + 48);
  for (let i = 0; i < BITS; i++) {
    const x = x0 + i * (bw + 4);
    stroke('steelblue');
    fill(i < filled ? 'lightcyan' : 'white');
    rect(x, y, bw, 32, 4);
    noStroke();
    textAlign(CENTER, CENTER);
    textSize(18);
    fill('navy');
    if (i < filled) text(leftBits[i], x + bw / 2, y + 16);
    textSize(14);
    fill(i === 0 ? 'firebrick' : 'dimgray');
    text(WEIGHTS[i], x + bw / 2, y + 48);
  }
  const rx = x0 + BITS * (bw + 4) + 12;
  noStroke();
  textAlign(LEFT, CENTER);
  textSize(16);
  fill('black');
  if (filled === BITS) {
    const n = parseInt(leftBits, 2);
    const v = n >= 128 ? n - 256 : n;
    text('unsigned n = ' + n, rx, y + 8);
    text(n >= 128 ? 'signed = n - 256 = ' + v : 'signed = ' + v, rx, y + 30);
  } else {
    fill('dimgray');
    text(filled + ' of 8 bits collected', rx, y + 8);
    text('(MSB first)', rx, y + 30);
  }
}

// ---------- text panel ----------

function drawInfoPanel(allBits, x, y, w, h) {
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
    if (tick === 0) {
      fill('navy');
      textStyle(ITALIC);
      text('Which wire says whose sample this is?', x + pad, yy);
      textStyle(NORMAL);
      fill('dimgray');
      drawWrapped('Press "Step one tick". At each rising edge of the bit clock (green dashed line) one data bit is sampled: watch which wire changes and which bit is collected.', x + pad, yy + 22, tw, 20);
    } else {
      const i = tick - 1;
      const left = i < BITS;
      fill('black');
      drawWrapped('Tick ' + tick + ': the bit clock rises, so SD is sampled: bit = ' + allBits[i] + '. WS is ' +
        (left ? 'low, so this is bit ' + (i + 1) + ' of the LEFT word.' : 'high, so this is bit ' + (i - BITS + 1) + ' of the RIGHT word.'),
        x + pad, yy, tw, 20);
      fill('seagreen');
      if (tick > BITS) drawWrapped('The word select line changed, not the data line: WS says whose sample the bits are (low = left, high = right).', x + pad, yy + 44, tw, 20);
    }
    return;
  }
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 5 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 6. ' + (sc >= 5 ? 'Mastery reached.' : 'Mastery is 5 of 6.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('Waveforms 5 and 6 gave 45 and -45. Compare their bits: how do you get one from the other?', x + pad, yy + 24, tw, 20);
    return;
  }
  if (!submitted) {
    fill('navy');
    textStyle(ITALIC);
    text('What is the signed value of the left-channel word?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Read the 8 data bits while WS is low, MSB first, at each rising edge. Type a whole number from -128 to 127 and press Submit.', x + pad, yy + 22, tw, 20);
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
    waveIndex = 0;
    results = [];
    submitted = false;
    finished = false;
  } else {
    mode = 'explore';
    tick = 0;
  }
  answerInput.value('');
  updateControlStates();
}

function submitAnswer() {
  if (mode !== 'quiz' || submitted || finished) return;
  const raw = answerInput.value().trim();
  if (raw === '' || isNaN(Number(raw))) return;
  const wv = WAVES[waveIndex];
  const correct = Number(raw) === wv.value;
  results[waveIndex] = correct;
  feedbackCorrect = correct;
  feedback = correct ? 'Correct: ' + wv.why : 'Not quite. The left value is ' + wv.value + ': ' + wv.why;
  submitted = true;
  updateControlStates();
}

function nextWave() {
  if (!submitted) return;
  if (waveIndex === WAVES.length - 1) finished = true;
  else { waveIndex++; submitted = false; }
  answerInput.value('');
  updateControlStates();
}

function setEnabled(el, on) {
  el.elt.disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  modeButton.html(quiz ? 'Back to explore' : 'Start the 6 waveforms');
  setEnabled(answerInput, quiz && !submitted && !finished);
  setEnabled(submitButton, quiz && !submitted && !finished);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(waveIndex === WAVES.length - 1 ? 'See score' : 'Next waveform');
  setEnabled(stepButton, !quiz && tick < SLOTS);
  setEnabled(resetButton, !quiz && tick > 0);
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
  layoutRow([stepButton, resetButton], 10, drawHeight + 44, 10);
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
