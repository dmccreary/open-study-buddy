// Allocation Classifier - p5.js MicroSim
// CANVAS_HEIGHT: 480
// Distinguish MicroPython statements that allocate heap memory from those
// that do not. Rule: a statement allocates when it creates a new object that
// is not a small integer. A small integer is a whole number from -2**30 to
// 2**30 - 1 on a 32-bit port, and storing into an existing buffer never
// allocates. The answers are predictions from the MicroPython object model on
// the Pico's 32-bit port (ports/rp2/mpconfigport.h), labeled "expected" until
// 03-allocation-and-floats.py has been run on the kit.

let canvasWidth = 800;
let drawHeight = 430;
let controlHeight = 50;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

const ALLOC = 'Allocates';
const NO_ALLOC = 'Does not allocate';
// heap: what the statement creates on the heap ('' for nothing)
// place: where the work happens when nothing is created
const STATEMENTS = [
  { code: 'x = x + 1', note: 'x is a small whole number', answer: NO_ALLOC,
    why: 'A small integer lives inside the value itself.', heap: '', place: 'the small integer 1 + x is stored inside the value x' },
  { code: 'y = y * 1.0001', note: 'y is a float', answer: ALLOC,
    why: 'The float result is a new heap object.', heap: 'new float object (y * 1.0001)' },
  { code: 'arr_f[3] = arr_f[3] * 1.0001', note: "arr_f is array('f')", answer: ALLOC,
    why: 'Reading an element makes a float object, and so does the product.', heap: 'float object for arr_f[3]  +  float object for the product' },
  { code: 'arr_h[3] = (arr_h[3] * 3) >> 1', note: "arr_h is array('h')", answer: NO_ALLOC,
    why: 'Every value is a small integer.', heap: '', place: 'small integers only, written back into the existing array' },
  { code: 'part = buf[0:8]', note: 'buf is a bytearray', answer: ALLOC,
    why: 'A slice of a bytearray is a new bytearray.', heap: 'new 8-byte bytearray (a copy)' },
  { code: 'part = view[0:8]', note: 'view is a memoryview', answer: ALLOC,
    why: 'A memoryview slice is a new, small memoryview object, though it copies no data.', heap: 'new small memoryview object (no data copied)' },
  { code: 't = [0] * 16', note: '', answer: ALLOC,
    why: 'A new list is created.', heap: 'new list of 16 items' },
  { code: 't = struct.unpack("<4i", words)', note: '', answer: ALLOC,
    why: 'A new tuple holds the four results.', heap: 'new tuple of 4 results' },
  { code: 'struct.pack_into("<i", words, 0, 7)', note: '', answer: NO_ALLOC,
    why: 'It writes into memory the program already owns.', heap: '', place: '4 bytes written into the existing buffer words' },
  { code: 's = "%d" % 12345', note: '', answer: ALLOC,
    why: 'A new string is built.', heap: 'new string "12345"' },
  { code: 'z = big + 1', note: 'big is 2**30 (on a 64-bit computer this would not allocate)', answer: ALLOC,
    why: '2**30 does not fit a 31-bit small integer on a 32-bit chip, so the value is a big-integer object.', heap: 'big-integer object for 2**30 + 1' },
  { code: 'buf[5] = 77', note: 'buf is a bytearray', answer: NO_ALLOC,
    why: 'It stores into a byte of an existing bytearray.', heap: '', place: 'one byte written into the existing bytearray buf' }
];

let index = 0;
let answered = false;
let finished = false;
let results = [];
let choices = [];
let feedback = '';
let feedbackCorrect = false;

let allocButton, noAllocButton, nextButton, restartButton;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  allocButton = createButton(ALLOC);
  allocButton.mousePressed(() => choose(ALLOC));
  noAllocButton = createButton(NO_ALLOC);
  noAllocButton.mousePressed(() => choose(NO_ALLOC));
  nextButton = createButton('Next statement');
  nextButton.mousePressed(nextStatement);
  restartButton = createButton('Start over');
  restartButton.mousePressed(restart);
  for (const b of [allocButton, noAllocButton, nextButton, restartButton]) b.style('font-size', '16px');

  positionControls();
  updateControlStates();

  describe('One MicroPython statement at a time in a code card, with two buttons: Allocates and Does not allocate. After each choice a small picture shows either the new object created on the heap or the existing value or buffer that was written, with the reason. Twelve statements in a fixed order, then a list of the statements answered incorrectly.', LABEL);
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
  text('Allocation Classifier', canvasWidth / 2, 10);
  textSize(16);
  fill('dimgray');
  const head = finished ? 'All 12 statements done' : 'Statement ' + (index + 1) + ' of 12 (answers expected for the Pico\'s 32-bit port)';
  text(head + '   |   Score: ' + countCorrect() + ' of 12', canvasWidth / 2, 42);

  if (finished) drawSummary(margin, 72, canvasWidth - 2 * margin, drawHeight - 82);
  else {
    drawCodeCard(STATEMENTS[index], margin, 72, canvasWidth - 2 * margin);
    drawMemory(STATEMENTS[index], margin, 182, canvasWidth - 2 * margin, 120);
    drawFeedback(margin, 312, canvasWidth - 2 * margin, drawHeight - 322);
  }
}

function drawCodeCard(st, x, y, w) {
  fill('white');
  stroke('steelblue');
  rect(x, y, w, 96, 10);
  noStroke();
  fill('midnightblue');
  textFont('monospace');     // code needs a fixed-width font
  textSize(22);
  textAlign(LEFT, TOP);
  text(st.code, x + 16, y + 12);
  textFont('sans-serif');
  textSize(16);
  fill('dimgray');
  if (st.note) text('(' + st.note + ')', x + 16, y + 44);
  fill('navy');
  textStyle(ITALIC);
  text('Does this line create a new object?', x + 16, y + 68);
  textStyle(NORMAL);
}

// two boxes: values/buffers the program already owns, and the heap
function drawMemory(st, x, y, w, h) {
  const gap = 16;
  const bw = (w - gap) / 2;
  const boxes = [{ t: 'Existing values and buffers', x: x }, { t: 'Heap: new objects', x: x + bw + gap }];
  for (const b of boxes) {
    fill(255, 255, 255, 220);
    stroke('silver');
    rect(b.x, y, bw, h, 10);
    noStroke();
    fill('black');
    textAlign(LEFT, TOP);
    textStyle(BOLD);
    textSize(16);
    text(b.t, b.x + 10, y + 8);
    textStyle(NORMAL);
  }
  textSize(15);
  if (!answered) {
    fill('dimgray');
    textAlign(CENTER, CENTER);
    text('?', boxes[0].x + bw / 2, y + h / 2 + 10);
    text('?', boxes[1].x + bw / 2, y + h / 2 + 10);
    return;
  }
  if (st.heap) {
    stroke('firebrick');
    fill('mistyrose');
    rect(boxes[1].x + 10, y + 36, bw - 20, h - 48, 8);
    noStroke();
    fill('firebrick');
    textAlign(LEFT, TOP);
    drawWrapped('NEW: ' + st.heap, boxes[1].x + 20, y + 46, bw - 40, 19);
    fill('dimgray');
    textAlign(CENTER, CENTER);
    text('(the result is a new object)', boxes[0].x + bw / 2, y + h / 2 + 10);
  } else {
    stroke('seagreen');
    fill('honeydew');
    rect(boxes[0].x + 10, y + 36, bw - 20, h - 48, 8);
    noStroke();
    fill('darkgreen');
    textAlign(LEFT, TOP);
    drawWrapped(st.place, boxes[0].x + 20, y + 46, bw - 40, 19);
    fill('dimgray');
    textAlign(CENTER, CENTER);
    text('nothing new: no garbage to collect', boxes[1].x + bw / 2, y + h / 2 + 10);
  }
}

function drawFeedback(x, y, w, h) {
  fill(255, 255, 255, 235);
  stroke('silver');
  rect(x, y, w, h, 10);
  noStroke();
  textAlign(LEFT, TOP);
  textSize(16);
  if (!answered) {
    fill('dimgray');
    drawWrapped('Choose Allocates or Does not allocate below. You get one attempt per statement; the answer and the reason appear right after.', x + 10, y + 10, w - 20, 20);
    return;
  }
  fill(feedbackCorrect ? 'darkgreen' : 'firebrick');
  textStyle(BOLD);
  drawWrapped(feedback, x + 10, y + 10, w - 20, 20);
  textStyle(NORMAL);
}

function drawSummary(x, y, w, h) {
  fill(255, 255, 255, 235);
  stroke('silver');
  rect(x, y, w, h, 10);
  const sc = countCorrect();
  noStroke();
  textAlign(LEFT, TOP);
  textSize(18);
  textStyle(BOLD);
  fill(sc >= 10 ? 'darkgreen' : 'firebrick');
  text('Score: ' + sc + ' of 12 on the first attempt. ' + (sc >= 10 ? 'Mastery reached.' : 'Mastery is 10 of 12.'), x + 12, y + 10);
  textStyle(NORMAL);
  textSize(16);
  fill('black');
  const wrong = [];
  for (let i = 0; i < STATEMENTS.length; i++) if (!results[i]) wrong.push(i);
  let yy = y + 42;
  if (wrong.length === 0) {
    text('No statements wrong.', x + 12, yy);
    yy += 26;
  } else {
    text('Statements to review:', x + 12, yy);
    yy += 26;
    textFont('monospace');
    for (const i of wrong) {
      fill('firebrick');
      text((i + 1) + '. ' + STATEMENTS[i].code, x + 24, yy);
      fill('dimgray');
      text('-> ' + STATEMENTS[i].answer, x + 24 + min(w * 0.55, 420), yy);
      yy += 22;
    }
    textFont('sans-serif');
  }
  yy += 10;
  fill('navy');
  drawWrapped('Look at the statements that do not allocate: what do they have in common? (Think about small integers and buffers the program already owns.)', x + 12, yy, w - 24, 20);
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

function choose(choice) {
  if (answered || finished) return;
  const st = STATEMENTS[index];
  const correct = choice === st.answer;
  results[index] = correct;
  choices[index] = choice;
  feedbackCorrect = correct;
  feedback = correct ? 'Correct: ' + st.why : 'Not quite. ' + st.answer + ': ' + st.why;
  answered = true;
  updateControlStates();
}

function nextStatement() {
  if (!answered) return;
  if (index === STATEMENTS.length - 1) finished = true;
  else { index++; answered = false; }
  updateControlStates();
}

function restart() {
  index = 0;
  answered = false;
  finished = false;
  results = [];
  choices = [];
  updateControlStates();
}

function setEnabled(el, on) {
  el.elt.disabled = !on;
}

function updateControlStates() {
  setEnabled(allocButton, !answered && !finished);
  setEnabled(noAllocButton, !answered && !finished);
  setEnabled(nextButton, answered && !finished);
  nextButton.html(index === STATEMENTS.length - 1 ? 'See results' : 'Next statement');
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
  layoutRow([allocButton, noAllocButton, nextButton, restartButton], 10, drawHeight + 10, 12);
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
