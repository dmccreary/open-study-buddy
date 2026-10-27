// Heap Fragmentation Explorer
// CANVAS_HEIGHT: 545
// The learner predicts whether 6 allocation requests on an illustrative
// 16-cell heap succeed or raise MemoryError, and names the reason for each
// failure. Then the learner restarts the heap and compares two allocation orders.
//
// Rules (from the chapter spec):
//   * A request for n cells succeeds when the heap has a run of at least n
//     consecutive free cells, and it takes the lowest-numbered such run (first fit).
//   * "Collect garbage" frees only the cells of objects marked as garbage and
//     never moves any other object.
//   * "Restart" frees all 16 cells.
// Every result, reason, free total and longest run shown is computed from the
// heap model below, not hard-coded.

// ---------- canvas layout ----------
let canvasWidth = 400;
let drawHeight = 430;
let controlHeight = 115;     // 3 rows of controls: 3 x 35 + 10
let canvasHeight = drawHeight + controlHeight;
let margin = 25;
let defaultTextSize = 16;

// ---------- heap model ----------
const HEAP_SIZE = 16;
let heap = [];               // HEAP_SIZE entries: null (free) or {label, garbage, kind}
let trialCells = [];         // cells shown as a trial allocation for the current request
let trialFailed = false;     // true when the current request raised MemoryError

// State X: A to H in cells 1, 3, 5 ... 15; B, D, F, H are garbage
function makeStateX() {
  const h = new Array(HEAP_SIZE).fill(null);
  const labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
  const garbage = ['B', 'D', 'F', 'H'];
  for (let i = 0; i < labels.length; i++) {
    h[i * 2] = { label: labels[i], garbage: garbage.includes(labels[i]), kind: 'obj' };
  }
  return h;
}

// Collect garbage: free garbage cells, never move anything else
function collectGarbage(h) {
  return h.map(c => (c && c.garbage) ? null : c);
}

// State Y is exactly what collecting garbage does to state X
function makeStateY() {
  return collectGarbage(makeStateX());
}

// Lowest-numbered run of n free cells, or -1 (first fit)
function firstFit(h, n) {
  let run = 0;
  for (let i = 0; i < h.length; i++) {
    run = (h[i] === null) ? run + 1 : 0;
    if (run >= n) return i - n + 1;
  }
  return -1;
}

function freeTotal(h) {
  return h.filter(c => c === null).length;
}

function longestRun(h) {
  let best = 0, run = 0;
  for (const c of h) {
    run = (c === null) ? run + 1 : 0;
    best = Math.max(best, run);
  }
  return best;
}

const REASON_TOTAL = 'not enough free cells in total';
const REASON_GAP = 'no single gap is big enough';

// Attempt a request on a heap: {ok, start, reason}
function attempt(h, n) {
  const start = firstFit(h, n);
  if (start >= 0) return { ok: true, start: start, reason: null };
  return { ok: false, start: -1, reason: freeTotal(h) < n ? REASON_TOTAL : REASON_GAP };
}

// ---------- the six requests (Content table) ----------
const requests = [
  { state: 'X', n: 1,  result: 'succeeds',    reason: null,         why: 'Any free cell is a gap of at least 1.' },
  { state: 'X', n: 2,  result: 'MemoryError', reason: REASON_GAP,   why: '8 cells are free in total, but every gap is 1 cell wide.' },
  { state: 'X', n: 8,  result: 'MemoryError', reason: REASON_GAP,   why: '8 cells are free in total, which equals the request, but they are not together.' },
  { state: 'Y', n: 3,  result: 'succeeds',    reason: null,         why: 'Cells 2 to 4 form a run of 3.' },
  { state: 'Y', n: 4,  result: 'MemoryError', reason: REASON_GAP,   why: '12 cells are free, but the longest run is 3.' },
  { state: 'Y', n: 13, result: 'MemoryError', reason: REASON_TOTAL, why: 'Only 12 cells are free in total.' }
];

// ---------- quiz state ----------
let phase = 'quiz';          // 'quiz' or 'sandbox'
let reqIndex = 0;
let answered = false;
let awaitingReason = false;  // learner chose MemoryError and must pick a reason
let collected = false;       // garbage collected (state X -> Y) during the quiz
let score = 0;
let resultLine = '';
let feedback = '';
let feedbackCorrect = true;
let sandboxMessage = '';
let heapStateName = 'X';
let collectNote = '';      // shown on request 4 after garbage collection

// ---------- controls ----------
let succeedsButton, errorButton;
let reasonTotalButton, reasonGapButton;
let nextButton, collectButton, restartButton;
let orderBufferFirstButton, orderSpacedFirstButton;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  // Create every control first, then position them
  succeedsButton = createButton('Succeeds');
  succeedsButton.mousePressed(() => answer('succeeds', null));
  errorButton = createButton('MemoryError');
  errorButton.mousePressed(chooseMemoryError);

  reasonTotalButton = createButton('Not enough free cells in total');
  reasonTotalButton.mousePressed(() => answer('MemoryError', REASON_TOTAL));
  reasonGapButton = createButton('No single gap is big enough');
  reasonGapButton.mousePressed(() => answer('MemoryError', REASON_GAP));

  nextButton = createButton('Next request');
  nextButton.mousePressed(nextRequest);
  collectButton = createButton('Collect garbage');
  collectButton.mousePressed(pressCollect);
  restartButton = createButton('Restart');
  restartButton.mousePressed(pressRestart);

  orderBufferFirstButton = createButton('Buffer first, then A to H');
  orderBufferFirstButton.mousePressed(runBufferFirst);
  orderSpacedFirstButton = createButton('A to H spaced first, then buffer');
  orderSpacedFirstButton.mousePressed(runSpacedFirst);

  for (const b of [succeedsButton, errorButton, reasonTotalButton, reasonGapButton, nextButton,
    collectButton, restartButton, orderBufferFirstButton, orderSpacedFirstButton]) {
    b.style('font-size', '15px');
    b.style('white-space', 'nowrap');
  }
  positionControls();

  heap = makeStateX();
  heapStateName = 'X';
  updateControlStates();

  describe('A row of 16 heap cells, some holding objects A to H and some free. ' +
    'The learner predicts whether each of 6 allocation requests succeeds or raises MemoryError, ' +
    'picks the reason for each failure, collects garbage, and compares two allocation orders.', LABEL);
}

function positionControls() {
  const row1 = drawHeight + 8;
  const row2 = drawHeight + 43;
  const row3 = drawHeight + 78;
  // Place buttons left to right using their rendered widths so they never overlap
  placeRow([succeedsButton, errorButton], 10, row1);
  placeRow([orderBufferFirstButton, orderSpacedFirstButton], 10, row1);
  placeReasonRow();
  placeRow([nextButton, collectButton, restartButton], 10, row3);
}

// The two reason buttons are wide. When they do not fit after the "Reason:"
// label (narrow screens), drop the label and use a smaller font so the row
// stays on the canvas. Hidden buttons measure 0 wide, so this runs again
// whenever the reason buttons are shown.
let reasonRowX = 80;
function placeReasonRow() {
  const row2 = drawHeight + 43;
  for (const b of [reasonTotalButton, reasonGapButton]) b.style('font-size', '15px');
  const w = reasonTotalButton.elt.offsetWidth + reasonGapButton.elt.offsetWidth + 10;
  if (w > 0 && 80 + w > canvasWidth - 5) {
    reasonRowX = 10;
    if (10 + w > canvasWidth - 5) {
      for (const b of [reasonTotalButton, reasonGapButton]) b.style('font-size', '12px');
    }
  } else {
    reasonRowX = 80;
  }
  placeRow([reasonTotalButton, reasonGapButton], reasonRowX, row2);
}

function placeRow(buttons, x, y) {
  for (const b of buttons) {
    b.position(x, y);
    // a hidden button measures 0 wide, so reuse its last measured width
    if (b.elt.offsetWidth) b.lastWidth = b.elt.offsetWidth;
    x += (b.lastWidth || 120) + 10;
  }
}

function setEnabled(ctrl, on) {
  ctrl.elt.disabled = !on;
}

function updateControlStates() {
  if (phase === 'quiz') {
    succeedsButton.show();
    errorButton.show();
    orderBufferFirstButton.hide();
    orderSpacedFirstButton.hide();
    setEnabled(succeedsButton, !answered && !awaitingReason);
    setEnabled(errorButton, !answered && !awaitingReason);
    if (awaitingReason) { reasonTotalButton.show(); reasonGapButton.show(); placeReasonRow(); }
    else { reasonTotalButton.hide(); reasonGapButton.hide(); }
    nextButton.show();
    // After request 3 the learner must collect garbage before request 4
    const needCollect = (reqIndex === 2 && answered && !collected);
    setEnabled(nextButton, answered && !needCollect);
    nextButton.html(reqIndex === requests.length - 1 ? 'Finish' : 'Next request');
    setEnabled(collectButton, needCollect);
    setEnabled(restartButton, false);
  } else {
    succeedsButton.hide();
    errorButton.hide();
    reasonTotalButton.hide();
    reasonGapButton.hide();
    nextButton.hide();
    orderBufferFirstButton.show();
    orderSpacedFirstButton.show();
    const empty = freeTotal(heap) === HEAP_SIZE;
    setEnabled(orderBufferFirstButton, empty);
    setEnabled(orderSpacedFirstButton, empty);
    setEnabled(collectButton, heap.some(c => c && c.garbage));
    setEnabled(restartButton, true);
  }
}

// ---------- quiz actions ----------
function chooseMemoryError() {
  if (answered) return;
  awaitingReason = true;
  updateControlStates();
}

function answer(prediction, reason) {
  if (answered || phase !== 'quiz') return;
  const req = requests[reqIndex];
  const outcome = attempt(heap, req.n);
  // The computed outcome drives the heap picture; the Content table drives scoring.
  trialCells = [];
  trialFailed = !outcome.ok;
  if (outcome.ok) {
    for (let i = 0; i < req.n; i++) trialCells.push(outcome.start + i);
  }
  let correct = (prediction === req.result);
  if (correct && req.result === 'MemoryError') correct = (reason === req.reason);
  if (correct) score++;
  feedbackCorrect = correct;
  feedback = (correct ? 'Correct: ' : 'Not quite. ') + req.why;
  if (outcome.ok) {
    const first = outcome.start + 1;
    const last = outcome.start + req.n;
    resultLine = 'Result: succeeds, using ' + (req.n === 1 ? 'cell ' + first : 'cells ' + first + ' to ' + last) +
      ' (trial allocation, released before the next request).';
  } else {
    resultLine = 'Result: MemoryError (' + outcome.reason + ').';
  }
  answered = true;
  awaitingReason = false;
  collectNote = '';
  updateControlStates();
}

function nextRequest() {
  if (!answered) return;
  if (reqIndex === requests.length - 1) {
    // Quiz finished: move to the allocation-order sandbox
    phase = 'sandbox';
    trialCells = [];
    trialFailed = false;
    sandboxMessage = 'Press Restart to free all 16 cells, then try both allocation orders.';
    updateControlStates();
    return;
  }
  reqIndex++;
  answered = false;
  awaitingReason = false;
  trialCells = [];
  trialFailed = false;
  resultLine = '';
  feedback = '';
  // The heap shown is the state each request names (X or Y)
  heap = requests[reqIndex].state === 'X' ? makeStateX() : makeStateY();
  heapStateName = requests[reqIndex].state;
  updateControlStates();
}

function pressCollect() {
  const before = { free: freeTotal(heap), run: longestRun(heap) };
  heap = collectGarbage(heap);
  trialCells = [];
  trialFailed = false;
  if (phase === 'quiz') {
    collected = true;
    // Go straight to request 4, which uses state Y (the collected heap)
    reqIndex++;
    answered = false;
    awaitingReason = false;
    heapStateName = 'Y';
    resultLine = '';
    feedback = '';
    collectNote = 'Garbage collected: B, D, F and H were freed, and A, C, E and G did not move. Free cells went from ' +
      before.free + ' to ' + freeTotal(heap) + ', but the longest run only grew from ' + before.run + ' to ' +
      longestRun(heap) + '.';
  }
  updateControlStates();
}

// ---------- sandbox actions ----------
function pressRestart() {
  heap = new Array(HEAP_SIZE).fill(null);
  heapStateName = 'empty';
  trialCells = [];
  trialFailed = false;
  sandboxMessage = 'Restart: all 16 cells are free. Choose an allocation order.';
  updateControlStates();
}

function runBufferFirst() {
  // Step 1: one 8-cell buffer, first fit
  const bufStart = firstFit(heap, 8);
  if (bufStart < 0) { sandboxMessage = 'MemoryError: the 8-cell buffer does not fit.'; return; }
  for (let i = 0; i < 8; i++) heap[bufStart + i] = { label: 'buf', garbage: false, kind: 'buf' };
  // Step 2: the eight 1-cell objects A to H, first fit
  const placed = [];
  for (const L of ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']) {
    const s = firstFit(heap, 1);
    if (s < 0) { sandboxMessage = 'MemoryError while allocating ' + L + '.'; updateControlStates(); return; }
    heap[s] = { label: L, garbage: false, kind: 'obj' };
    placed.push(s + 1);
  }
  heapStateName = 'buffer first';
  sandboxMessage = 'The buffer took cells ' + (bufStart + 1) + ' to ' + (bufStart + 8) + ', then A to H took cells ' +
    placed[0] + ' to ' + placed[placed.length - 1] + '. Everything fits. Press Restart to try the other order.';
  updateControlStates();
}

function runSpacedFirst() {
  // Step 1: A to H one cell apart (short-lived objects between them were freed)
  const labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
  for (let i = 0; i < labels.length; i++) heap[i * 2] = { label: labels[i], garbage: false, kind: 'obj' };
  // Step 2: the 8-cell buffer, first fit
  const out = attempt(heap, 8);
  heapStateName = 'objects first';
  if (out.ok) {
    for (let i = 0; i < 8; i++) heap[out.start + i] = { label: 'buf', garbage: false, kind: 'buf' };
    sandboxMessage = 'The buffer fit.';
  } else {
    trialFailed = true;
    sandboxMessage = 'A to H sit one cell apart. ' + freeTotal(heap) + ' cells are free, but the longest run is ' +
      longestRun(heap) + ', so the 8-cell buffer raises MemoryError (' + out.reason + '). Allocate the biggest buffer first.';
  }
  updateControlStates();
}

// ---------- drawing ----------
function draw() {
  updateCanvasSize();

  // drawing region
  stroke('silver');
  strokeWeight(1);
  fill('aliceblue');
  rect(0, 0, canvasWidth, drawHeight);
  // control region
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  // title
  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(24);
  text('Heap Fragmentation Explorer', canvasWidth / 2, 10);
  textSize(canvasWidth < 560 ? 13 : 14);
  fill('dimgray');
  text('Illustrative 16-cell heap. The collector frees objects but never moves them.',
    10, 40, canvasWidth - 20, 36);

  drawHeap();
  drawLegend();
  drawPanel();
  drawControlLabels();
}

function drawHeap() {
  const cellW = (canvasWidth - 2 * margin) / HEAP_SIZE;
  const top = 94;
  const h = 56;
  textAlign(CENTER, CENTER);
  for (let i = 0; i < HEAP_SIZE; i++) {
    const x = margin + i * cellW;
    // cell number
    noStroke();
    fill('black');
    textSize(cellW < 28 ? 11 : 14);
    text(i + 1, x + cellW / 2, top - 12);
    // cell body
    const c = heap[i];
    const isTrial = trialCells.includes(i);
    stroke('dimgray');
    strokeWeight(1);
    if (isTrial) fill('orange');
    else if (c === null) fill('white');
    else if (c.kind === 'buf') fill('mediumpurple');
    else if (c.garbage) fill('lightgray');
    else fill('steelblue');
    rect(x, top, cellW, h);
    // label
    noStroke();
    textSize(cellW < 28 ? 12 : 18);
    if (isTrial) {
      fill('black');
      fitTextSize('new', cellW - 4, cellW < 28 ? 12 : 18, 8);
      text('new', x + cellW / 2, top + h / 2);
    } else if (c !== null) {
      fill(c.garbage ? 'dimgray' : 'white');
      text(c.kind === 'buf' ? 'b' : c.label, x + cellW / 2, top + h / 2);
    }
  }
  // MemoryError outline
  if (trialFailed) {
    noFill();
    stroke('crimson');
    strokeWeight(3);
    rect(margin - 3, top - 3, cellW * HEAP_SIZE + 6, h + 6);
    strokeWeight(1);
  }
  // stats computed from the model
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(16);
  const label = (heapStateName === 'X' || heapStateName === 'Y') ? 'Heap state ' + heapStateName : 'Heap: ' + heapStateName;
  const stats = label + '     Free cells: ' + freeTotal(heap) + '     Longest free run: ' + longestRun(heap);
  fitTextSize(stats, canvasWidth - 2 * margin, 16, 11);
  text(stats, margin, top + h + 12);
}

function drawLegend() {
  const items = [
    ['steelblue', 'Live object'],
    ['lightgray', 'Garbage (not yet collected)'],
    ['white', 'Free'],
    ['orange', 'New allocation'],
    ['mediumpurple', '8-cell buffer (b)']
  ];
  let x = margin;
  let y = 194;
  textSize(14);
  textAlign(LEFT, CENTER);
  for (const [col, lab] of items) {
    const w = 18 + 6 + textWidth(lab) + 16;
    if (x + w > canvasWidth - margin) { x = margin; y += 22; }
    stroke('dimgray');
    fill(col);
    rect(x, y - 8, 16, 16);
    noStroke();
    fill('black');
    text(lab, x + 22, y);
    x += w;
  }
}

function drawPanel() {
  const px = margin;
  const py = 240;
  const pw = canvasWidth - 2 * margin;
  const ph = drawHeight - py - 10;
  stroke(200);
  fill(255, 255, 255, 230);
  rect(px, py, pw, ph, 10);
  noStroke();
  textAlign(LEFT, TOP);
  fill('black');

  if (phase === 'quiz') {
    const req = requests[reqIndex];
    textStyle(BOLD);
    const header = 'Request ' + (reqIndex + 1) + ' of 6: allocate ' + req.n + (req.n === 1 ? ' cell' : ' cells') +
      ' (heap state ' + req.state + ')';
    fitTextSize(header, pw - 24, 18, 13);
    text(header, px + 12, py + 10);
    textStyle(NORMAL);
    // prompt and feedback flow one after the other so long text never clips
    const narrow = canvasWidth < 560;
    textSize(narrow ? 14 : 16);
    const lineH = narrow ? 17 : 20;
    let prompt;
    if (!answered && !awaitingReason) prompt = 'Will this request succeed?';
    else if (awaitingReason) prompt = 'Why will it fail? Pick a reason below.';
    else prompt = resultLine;
    fill(answered ? (trialFailed ? 'crimson' : 'darkgreen') : 'black');
    const used = drawWrapped(prompt, px + 12, py + 36, pw - 24, lineH);
    if (feedback) {
      fill(feedbackCorrect ? 'darkgreen' : 'firebrick');
      drawWrapped(feedback, px + 12, py + 42 + used, pw - 24, lineH);
    } else if (collectNote) {
      fill('dimgray');
      drawWrapped(collectNote, px + 12, py + 42 + used, pw - 24, lineH);
    }
    if (reqIndex === 2 && answered && !collected) {
      textAlign(LEFT, BOTTOM);
      fill('black');
      textStyle(BOLD);
      text('Next: press Collect garbage.', px + 12, py + ph - 8);
      textStyle(NORMAL);
    }
  } else {
    textSize(18);
    textStyle(BOLD);
    const mastery = score >= 5 ? ' (mastery reached)' : ' (mastery is 5 of 6)';
    text('All 6 requests done. Score: ' + score + ' of 6' + mastery, px + 12, py + 10, pw - 24, 50);
    textStyle(NORMAL);
    textSize(16);
    fill('black');
    text(sandboxMessage, px + 12, py + 62, pw - 24, ph - 70);
  }
  // running score
  if (phase === 'quiz') {
    textAlign(RIGHT, BOTTOM);
    textSize(16);
    fill('black');
    text('Score: ' + score + ' of 6', px + pw - 12, py + ph - 8);
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

function drawControlLabels() {
  noStroke();
  fill('black');
  textSize(defaultTextSize);
  textAlign(LEFT, CENTER);
  if (phase === 'quiz' && awaitingReason && reasonRowX > 10) {
    text('Reason:', 10, drawHeight + 55);
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
