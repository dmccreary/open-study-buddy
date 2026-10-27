// Polling Versus Interrupt Timeline
// CANVAS_HEIGHT: 480
// The learner predicts, for 6 illustrative button presses, whether a loop
// that checks the pin every P milliseconds sees the press. After the six
// predictions, an Interrupt display shows every press caught at its start.
//
// Rules (from the chapter spec):
//   * Checks occur at 0, P, 2P, ... up to 220 ms.
//   * A press is the interval [start, end) during which the pin reads 0.
//   * Polling sees the press when start <= kP < end for some integer k >= 0.
//   * In interrupt mode every press is seen at its start (the falling edge).
// The check times and results drawn are computed from these rules.

// ---------- canvas layout ----------
let canvasWidth = 400;
let drawHeight = 400;
let controlHeight = 80;      // 2 rows of controls: 2 x 35 + 10
let canvasHeight = drawHeight + controlHeight;
let margin = 25;
let defaultTextSize = 16;

const TIMELINE_END = 220;    // ms

// ---------- the six cases (Content table) ----------
const cases = [
  { P: 5,   start: 12, end: 22,  result: 'seen',   why: 'Two checks land inside the press.' },
  { P: 20,  start: 12, end: 22,  result: 'seen',   why: 'The check at 20 ms lands inside the press, by luck.' },
  { P: 20,  start: 22, end: 32,  result: 'missed', why: 'The press starts just after one check and ends before the next.' },
  { P: 100, start: 30, end: 80,  result: 'missed', why: 'A 50 ms press fits entirely between two checks 100 ms apart.' },
  { P: 100, start: 90, end: 210, result: 'seen',   why: 'A press longer than P always contains a check.' },
  { P: 50,  start: 55, end: 95,  result: 'missed', why: 'A press shorter than P can fall between two checks.' }
];

// All check times 0, P, 2P ... <= 220 ms
function checkTimes(P) {
  const t = [];
  for (let k = 0; k * P <= TIMELINE_END; k++) t.push(k * P);
  return t;
}

// Check times that land inside the press: start <= t < end
function checksInside(c) {
  return checkTimes(c.P).filter(t => c.start <= t && t < c.end);
}

function pollingResult(c) {
  return checksInside(c).length > 0 ? 'seen' : 'missed';
}

// ---------- state ----------
let caseIndex = 0;
let answers = [null, null, null, null, null, null];   // {prediction, correct, feedback}
let score = 0;
let quizDone = false;
let mode = 'polling';                                   // 'polling' or 'interrupt'

// ---------- controls ----------
let seenButton, missedButton, prevButton, nextButton, modeSelect;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  // Create every control first, then position them
  seenButton = createButton('Seen');
  seenButton.mousePressed(() => predict('seen'));
  missedButton = createButton('Missed');
  missedButton.mousePressed(() => predict('missed'));
  prevButton = createButton('Previous case');
  prevButton.mousePressed(previousCase);
  nextButton = createButton('Next case');
  nextButton.mousePressed(nextCase);
  modeSelect = createSelect();
  modeSelect.option('Polling loop', 'polling');
  modeSelect.option('Interrupt', 'interrupt');
  modeSelect.selected('polling');
  modeSelect.changed(() => { mode = modeSelect.value(); });

  for (const b of [seenButton, missedButton, prevButton, nextButton, modeSelect]) {
    b.style('font-size', '15px');
  }
  positionControls();
  updateControlStates();

  describe('A timeline from 0 to 220 milliseconds showing a button press as a low pulse on the pin and ' +
    'the times a polling loop checks the pin. The learner predicts whether the loop sees each of 6 presses, ' +
    'then switches to interrupt mode to see every press caught at its falling edge.', LABEL);
}

function positionControls() {
  placeRow([seenButton, missedButton, prevButton, nextButton], 10, drawHeight + 8);
  modeSelect.position(85, drawHeight + 45);
}

function placeRow(items, x, y) {
  for (const b of items) {
    b.position(x, y);
    x += (b.elt.offsetWidth || 100) + 10;
  }
}

function setEnabled(ctrl, on) {
  ctrl.elt.disabled = !on;
}

function updateControlStates() {
  const answered = answers[caseIndex] !== null;
  setEnabled(seenButton, !quizDone && !answered);
  setEnabled(missedButton, !quizDone && !answered);
  // During the quiz the cases go forward only, one answer each
  setEnabled(prevButton, quizDone && caseIndex > 0);
  setEnabled(nextButton, quizDone ? caseIndex < cases.length - 1 : (answered && caseIndex < cases.length - 1));
  // Interrupt mode unlocks after the six predictions
  setEnabled(modeSelect, quizDone);
}

// ---------- actions ----------
function predict(choice) {
  if (quizDone || answers[caseIndex] !== null) return;
  const c = cases[caseIndex];
  const computed = pollingResult(c);   // equals c.result for every case in the table
  const correct = (choice === c.result);
  if (correct) score++;
  const feedback = correct
    ? 'Correct: ' + c.why
    : 'Not quite. The polling loop ' + (computed === 'seen' ? 'saw' : 'missed') + ' this press: ' +
      c.why.charAt(0).toLowerCase() + c.why.slice(1);
  answers[caseIndex] = { prediction: choice, correct: correct, feedback: feedback };
  if (caseIndex === cases.length - 1) quizDone = true;
  updateControlStates();
}

function nextCase() {
  if (caseIndex < cases.length - 1) caseIndex++;
  updateControlStates();
}

function previousCase() {
  if (caseIndex > 0) caseIndex--;
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
  text('Polling Versus Interrupt Timeline', canvasWidth / 2, 10);
  textSize(canvasWidth < 560 ? 13 : 14);
  fill('dimgray');
  text('Illustrative numbers. A poll sees a press only if a check lands inside it.', 10, 40, canvasWidth - 20, 36);

  drawCaseInfo();
  drawTimeline();
  drawPanel();
  drawControlLabels();
}

function timeToX(t) {
  const left = margin + 40;
  const right = canvasWidth - margin - 10;
  return left + (t / TIMELINE_END) * (right - left);
}

function drawCaseInfo() {
  const c = cases[caseIndex];
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  const narrow = canvasWidth < 560;
  textSize(narrow ? 14 : 16);
  let info;
  if (mode === 'polling') {
    info = 'Case ' + (caseIndex + 1) + ' of 6: the loop checks the pin every P = ' + c.P + ' ms. ' +
      'Press: ' + c.start + ' ms to ' + c.end + ' ms (' + (c.end - c.start) + ' ms long).';
  } else if (narrow) {
    // shorter wording so it stays on two lines above the ISR marker
    info = 'Case ' + (caseIndex + 1) + ' of 6, interrupt on the falling edge. ' +
      'Press: ' + c.start + ' ms to ' + c.end + ' ms.';
  } else {
    info = 'Case ' + (caseIndex + 1) + ' of 6, interrupt mode: the pin is wired to an interrupt on the falling edge. ' +
      'Press: ' + c.start + ' ms to ' + c.end + ' ms.';
  }
  text(info, margin, 78, canvasWidth - 2 * margin, 44);
}

function drawTimeline() {
  const c = cases[caseIndex];
  const yHigh = 145;
  const yLow = 190;
  const yAxis = 232;
  const answered = answers[caseIndex] !== null;
  const xs = timeToX(c.start);
  const xe = timeToX(c.end);

  // press band
  noStroke();
  fill(255, 182, 193, 140);
  rect(xs, yHigh - 12, xe - xs, yLow - yHigh + 24);

  // pin labels
  fill('black');
  textSize(14);
  textAlign(RIGHT, CENTER);
  text('Pin 1', timeToX(0) - 6, yHigh);
  text('Pin 0', timeToX(0) - 6, yLow);

  // pin signal: high, falling edge at start, low until end, rising edge
  stroke('black');
  strokeWeight(3);
  noFill();
  beginShape();
  vertex(timeToX(0), yHigh);
  vertex(xs, yHigh);
  vertex(xs, yLow);
  vertex(xe, yLow);
  vertex(xe, yHigh);
  vertex(timeToX(TIMELINE_END), yHigh);
  endShape();
  strokeWeight(1);

  // time axis
  stroke('dimgray');
  line(timeToX(0), yAxis, timeToX(TIMELINE_END), yAxis);
  textSize(13);
  for (let t = 0; t <= TIMELINE_END; t += 20) {
    const x = timeToX(t);
    stroke('dimgray');
    line(x, yAxis - 4, x, yAxis + 4);
    noStroke();
    fill('black');
    textAlign(CENTER, TOP);
    // skip some labels when narrow
    if (canvasWidth >= 520 || t % 40 === 0) text(t, x, yAxis + 6);
  }
  noStroke();
  textAlign(RIGHT, TOP);
  text('time (ms)', timeToX(TIMELINE_END), yAxis + 20);

  if (mode === 'polling') {
    // polling checks: a tick and a dot where the loop reads the pin
    const inside = checksInside(c);
    for (const t of checkTimes(c.P)) {
      const x = timeToX(t);
      const hit = answered && inside.includes(t);
      const pinValue = (c.start <= t && t < c.end) ? yLow : yHigh;
      stroke(hit ? 'green' : 'royalblue');
      strokeWeight(hit ? 2 : 1);
      line(x, yAxis - 18, x, yAxis - 4);
      // after the answer, show what each check read from the pin
      if (answered) {
        noStroke();
        fill(hit ? 'green' : 'royalblue');
        circle(x, pinValue, hit ? 12 : 7);
      }
    }
    strokeWeight(1);
    noStroke();
    fill('royalblue');
    textAlign(LEFT, TOP);
    // keep the caption clear of the "time (ms)" label on narrow screens
    textSize(13);
    const room = timeToX(TIMELINE_END) - textWidth('time (ms)') - 12 - timeToX(0);
    const options = answered
      ? ['dots: what each check read (green = inside the press)', 'dots: pin at each check (green = inside)']
      : ['blue ticks: polling check times'];
    let caption = options[options.length - 1];
    for (const opt of options) {
      fitTextSize(opt, room, 13, 11);
      if (textWidth(opt) <= room) { caption = opt; break; }
    }
    fitTextSize(caption, room, 13, 10);
    text(caption, timeToX(0), yAxis + 20);
  } else {
    // interrupt: the hardware reacts at the falling edge
    // the marker starts just above the pin so its label clears the case text
    const yTop = yHigh - 18;
    stroke('darkorange');
    strokeWeight(3);
    line(xs, yTop, xs, yLow + 4);
    fill('darkorange');
    noStroke();
    triangle(xs - 7, yLow - 6, xs + 7, yLow - 6, xs, yLow + 6);
    circle(xs, yTop, 10);
    strokeWeight(1);
    textSize(13);
    textAlign(xs > canvasWidth * 0.6 ? RIGHT : LEFT, BOTTOM);
    text('ISR runs at ' + c.start + ' ms (falling edge)', xs + (xs > canvasWidth * 0.6 ? -8 : 8), yTop);
  }
}

function drawPanel() {
  const c = cases[caseIndex];
  const a = answers[caseIndex];
  const px = margin;
  const py = 272;
  const pw = canvasWidth - 2 * margin;
  const ph = drawHeight - py - 10;
  stroke(200);
  fill(255, 255, 255, 230);
  rect(px, py, pw, ph, 10);
  noStroke();
  textAlign(LEFT, TOP);
  // title and body flow one after the other so a wrapped title never overlaps the body
  const narrow = canvasWidth < 560;
  textSize(narrow ? 14 : 16);
  const lineH = narrow ? 17 : 20;
  let title, titleColor, body, bodyColor;
  if (mode === 'interrupt') {
    title = 'Interrupt: seen at ' + c.start + ' ms';
    titleColor = 'darkorange';
    body = 'The hardware notices the falling edge, so the ISR runs at the start of the press no matter how short it is. ' +
      'Polling every ' + c.P + ' ms: ' + pollingResult(c) + '.';
    bodyColor = 'black';
  } else if (a === null) {
    title = 'Will the polling loop see this press?';
    titleColor = 'black';
    body = 'Choose Seen or Missed.';
    bodyColor = 'dimgray';
  } else {
    const inside = checksInside(c);
    const computed = pollingResult(c);
    title = 'Polling result: ' + computed + '. Checks inside the press: ' +
      (inside.length ? inside.map(t => t + ' ms').join(', ') : 'none');
    titleColor = computed === 'seen' ? 'darkgreen' : 'crimson';
    body = a.feedback;
    bodyColor = a.correct ? 'darkgreen' : 'firebrick';
  }
  fill(titleColor);
  textStyle(BOLD);
  const used = drawWrapped(title, px + 12, py + 8, pw - 24, lineH);
  textStyle(NORMAL);
  fill(bodyColor);
  drawWrapped(body, px + 12, py + 12 + used, pw - 24, lineH);

  // running score and completion message
  textAlign(RIGHT, BOTTOM);
  fill('black');
  textSize(16);
  let s = 'Score: ' + score + ' of 6';
  if (quizDone) s += score >= 5 ? '  (mastery reached)' : '  (mastery is 5 of 6)';
  text(s, px + pw - 12, py + ph - 8);
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
  fill(quizDone ? 'black' : 'gray');
  textSize(defaultTextSize);
  textAlign(LEFT, CENTER);
  text('Display:', 10, drawHeight + 57);
  if (!quizDone) {
    textSize(14);
    text('(Interrupt unlocks after case 6)', 210, drawHeight + 57);
  } else if (mode === 'polling') {
    // hint lives beside the selector so it never collides with the score line
    textSize(14);
    fill('dimgray');
    text('Now try Display: Interrupt.', 210, drawHeight + 57);
  }
}

// ---------- responsive layout ----------
function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    canvasWidth = Math.floor(container.getBoundingClientRect().width);
  }
}
