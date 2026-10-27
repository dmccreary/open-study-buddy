// QoS Handshake Stepper - p5.js MicroSim
// CANVAS_HEIGHT: 550
// Infer how many copies of one alert the broker processes, for one hop from
// the publisher to the broker, under MQTT QoS 0, 1 and 2 (MQTT 3.1.1).
// QoS 0: PUBLISH only, never resent. QoS 1: PUBLISH, PUBACK; an unacknowledged
// PUBLISH is resent with the duplicate flag, and the broker processes every
// QoS 1 PUBLISH it receives. QoS 2: PUBLISH, PUBREC, PUBREL, PUBCOMP; the
// broker processes a packet number once however many times it arrives.
// A model of one hop; timing is not reproduced. Scenarios are illustrative.

let canvasWidth = 800;
let drawHeight = 470;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

// a packet: from 'P' (publisher) or 'B' (broker), name, lost?, note, copies after it
const P = (from, name, lost, note, copies) => ({ from: from, name: name, lost: lost, note: note, copies: copies });
const NO_LOSS = {
  0: [P('P', 'PUBLISH (id 7)', false, 'broker processes it: copy 1', 1)],
  1: [P('P', 'PUBLISH (id 7)', false, 'broker processes it: copy 1', 1),
      P('B', 'PUBACK (id 7)', false, 'publisher is done', 1)],
  2: [P('P', 'PUBLISH (id 7)', false, 'processed once; broker keeps id 7', 1),
      P('B', 'PUBREC (id 7)', false, 'received', 1),
      P('P', 'PUBREL (id 7)', false, 'release', 1),
      P('B', 'PUBCOMP (id 7)', false, 'complete: id 7 can be forgotten', 1)]
};
const SCENARIOS = [
  { text: 'QoS 0. Nothing is lost.', answer: 1, packets: NO_LOSS[0],
    why: 'The one PUBLISH arrives and is processed once.' },
  { text: 'QoS 0. The PUBLISH is lost.', answer: 0,
    packets: [P('P', 'PUBLISH (id 7)', true, 'lost; QoS 0 never resends', 0)],
    why: 'QoS 0 has no acknowledgement and no repeat, so the alert is gone.' },
  { text: 'QoS 1. Nothing is lost.', answer: 1, packets: NO_LOSS[1],
    why: 'The PUBLISH arrives, is processed once, and the PUBACK ends the exchange.' },
  { text: 'QoS 1. The PUBLISH is lost.', answer: 1,
    packets: [P('P', 'PUBLISH (id 7)', true, 'lost', 0),
              P('P', 'PUBLISH (id 7, DUP)', false, 'no PUBACK came, so it is resent: copy 1', 1),
              P('B', 'PUBACK (id 7)', false, 'publisher is done', 1)],
    why: 'No PUBACK comes back, so the publisher sends the PUBLISH again with the duplicate flag set. That second one arrives and is processed once.' },
  { text: 'QoS 1. The PUBLISH arrives but the PUBACK is lost.', answer: 2,
    packets: [P('P', 'PUBLISH (id 7)', false, 'broker processes it: copy 1', 1),
              P('B', 'PUBACK (id 7)', true, 'lost', 1),
              P('P', 'PUBLISH (id 7, DUP)', false, 'resent; QoS 1 processes it again: copy 2', 2),
              P('B', 'PUBACK (id 7)', false, 'publisher is done', 2)],
    why: 'The broker already processed the alert, but the publisher sees no PUBACK and sends it again, so the broker processes it a second time. This is why alerts carry an id.' },
  { text: 'QoS 2. The PUBREC is lost.', answer: 1,
    packets: [P('P', 'PUBLISH (id 7)', false, 'processed once; broker keeps id 7', 1),
              P('B', 'PUBREC (id 7)', true, 'lost', 1),
              P('P', 'PUBLISH (id 7, DUP)', false, 'broker knows id 7: not processed again', 1),
              P('B', 'PUBREC (id 7)', false, 'received', 1),
              P('P', 'PUBREL (id 7)', false, 'release', 1),
              P('B', 'PUBCOMP (id 7)', false, 'complete', 1)],
    why: 'The publisher repeats the PUBLISH, the broker recognizes the packet number and does not process it again, and the handshake continues to PUBCOMP.' }
];

let mode = 'explore';
let scIndex = 0;
let step = 0;
let submitted = false;
let finished = false;
let results = [];
let feedback = '';
let feedbackCorrect = false;

let modeButton, copiesLabel, copiesSelect, submitButton, nextButton, qosLabel, qosSelect, stepButton, resetButton;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  modeButton = createButton('Start the 6 scenarios');
  modeButton.mousePressed(toggleMode);
  copiesLabel = createSpan('Copies processed:');
  copiesSelect = createSelect();
  for (const o of ['choose', '0', '1', '2']) copiesSelect.option(o);
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next scenario');
  nextButton.mousePressed(nextScenario);
  qosLabel = createSpan('QoS:');
  qosSelect = createSelect();
  for (const q of ['0', '1', '2']) qosSelect.option(q);
  qosSelect.selected('1');
  qosSelect.changed(() => { step = 0; updateControlStates(); });
  stepButton = createButton('Step');
  stepButton.mousePressed(() => { if (step < packets().length) step++; updateControlStates(); });
  resetButton = createButton('Back to start');
  resetButton.mousePressed(() => { step = 0; updateControlStates(); });
  for (const el of [modeButton, copiesLabel, copiesSelect, submitButton, nextButton, qosLabel, qosSelect, stepButton, resetButton]) {
    el.style('font-size', '16px');
  }

  positionControls();
  updateControlStates();

  describe('A sequence diagram with two lanes, the publisher on the left and the broker on the right. Each step draws one MQTT packet as an arrow between the lanes: PUBLISH, PUBACK, PUBREC, PUBREL or PUBCOMP, with lost packets crossed out and a counter of how many copies the broker has processed. The learner steps through the no-loss case of QoS 0, 1 or 2, then predicts the copy count for six scenarios.', LABEL);
}

function packets() {
  return mode === 'explore' ? NO_LOSS[qosSelect.value()] : SCENARIOS[min(scIndex, 5)].packets;
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
  text('QoS Handshake Stepper', canvasWidth / 2, 10);
  textSize(16);
  fill('dimgray');
  let status;
  if (mode === 'explore') status = 'Explore: QoS ' + qosSelect.value() + ', nothing lost (model of one hop)';
  else if (finished) status = 'All 6 scenarios done   |   Score: ' + countCorrect() + ' of 6';
  else status = 'Scenario ' + (scIndex + 1) + ' of 6 (illustrative)   |   Score: ' + countCorrect() + ' of 6';
  text(status, canvasWidth / 2, 42);
  if (mode === 'quiz' && !finished) {
    fill('black');
    textStyle(BOLD);
    text(SCENARIOS[scIndex].text, canvasWidth / 2, 64);
    textStyle(NORMAL);
  }

  const pk = packets();
  const shown = mode === 'quiz' && !submitted ? 0 : step;
  drawLanes(pk, shown, 90, 244);
  drawPanel(pk, shown, margin, 372, canvasWidth - 2 * margin, drawHeight - 380);
}

function drawLanes(pk, shown, top, h) {
  const px = canvasWidth * 0.14;
  const bx = canvasWidth * 0.56;
  const noteX = bx + 14;
  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(16);
  textStyle(BOLD);
  text('Publisher', px, top);
  text('Broker', bx, top);
  textStyle(NORMAL);
  stroke('gray');
  strokeWeight(2);
  line(px, top + 24, px, top + h);
  line(bx, top + 24, bx, top + h);
  strokeWeight(1);
  const rowH = min(40, (h - 40) / 6);
  for (let i = 0; i < shown; i++) {
    const p = pk[i];
    const y = top + 40 + i * rowH;
    const fromX = p.from === 'P' ? px : bx;
    const toX = p.from === 'P' ? bx : px;
    // a lost packet stops 60% of the way; its label sits nearer the sender
    const endX = p.lost ? fromX + (toX - fromX) * 0.6 : toX;
    const labelX = p.lost ? fromX + (toX - fromX) * 0.28 : (px + bx) / 2;
    const dir = Math.sign(toX - fromX);
    stroke(p.lost ? 'firebrick' : 'navy');
    strokeWeight(2);
    line(fromX, y, endX - dir * 6, y);
    strokeWeight(1);
    noStroke();
    fill(p.lost ? 'firebrick' : 'navy');
    if (p.lost) {
      textAlign(CENTER, CENTER);
      textSize(22);
      text('X', endX, y);
    } else {
      triangle(endX, y, endX - dir * 10, y - 5, endX - dir * 10, y + 5);
    }
    textSize(14);
    textAlign(CENTER, BOTTOM);
    text(p.name + (p.lost ? ' (lost)' : ''), labelX, y - 3);
    fill(i === shown - 1 ? 'black' : 'dimgray');
    textAlign(LEFT, CENTER);
    drawWrapped(p.note, noteX, y - 8, canvasWidth - noteX - margin, 16);
  }
  // processed counter
  const copies = shown > 0 ? pk[shown - 1].copies : 0;
  fill('white');
  stroke('steelblue');
  rect(bx - 70, top + h + 6, 140, 28, 6);
  noStroke();
  fill('navy');
  textAlign(CENTER, CENTER);
  textSize(15);
  text(mode === 'quiz' && !submitted ? 'copies: ?' : 'copies processed: ' + copies, bx, top + h + 20);
}

function drawPanel(pk, shown, x, y, w, h) {
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
    text('What will the broker do if an acknowledgement goes missing?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped(shown < pk.length ? 'Press Step to send the next packet. Try QoS 0, 1 and 2 and count the packets each needs.' :
      'Done: QoS ' + qosSelect.value() + ' needs ' + pk.length + ' packet' + (pk.length > 1 ? 's' : '') + ' when nothing is lost. Now predict what a loss does.', x + pad, yy + 22, tw, 20);
    return;
  }
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 5 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 6. ' + (sc >= 5 ? 'Mastery reached.' : 'Mastery is 5 of 6.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('Only one scenario gave 2 copies. Was it the message or the acknowledgement that was lost, and how does an alert id help?', x + pad, yy + 24, tw, 20);
    return;
  }
  if (!submitted) {
    fill('navy');
    textStyle(ITALIC);
    text('How many copies of the alert does the broker process?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Think through the packets: what does the publisher do when an acknowledgement does not come back? Choose 0, 1 or 2 and Submit.', x + pad, yy + 22, tw, 20);
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
  step = 0;
  copiesSelect.selected('choose');
  updateControlStates();
}

function submitAnswer() {
  if (mode !== 'quiz' || submitted || finished) return;
  const c = copiesSelect.value();
  if (c === 'choose') return;
  const s = SCENARIOS[scIndex];
  const correct = Number(c) === s.answer;
  results[scIndex] = correct;
  feedbackCorrect = correct;
  feedback = correct ? 'Correct: ' + s.why :
    'Not quite. The broker processes ' + s.answer + (s.answer === 1 ? ' copy: ' : ' copies: ') + s.why;
  submitted = true;
  step = packets().length;   // reveal every packet; Back to start and Step replay them
  updateControlStates();
}

function nextScenario() {
  if (!submitted) return;
  if (scIndex === SCENARIOS.length - 1) finished = true;
  else { scIndex++; submitted = false; step = 0; }
  copiesSelect.selected('choose');
  updateControlStates();
}

function setEnabled(el, on) {
  el.elt.disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  const answering = quiz && !submitted && !finished;
  modeButton.html(quiz ? 'Back to explore' : 'Start the 6 scenarios');
  setEnabled(copiesSelect, answering);
  setEnabled(submitButton, answering);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(scIndex === SCENARIOS.length - 1 ? 'See score' : 'Next scenario');
  setEnabled(qosSelect, !quiz);
  const canStep = !quiz || (submitted && !finished);
  setEnabled(stepButton, canStep && step < packets().length);
  setEnabled(resetButton, canStep && step > 0);
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
  layoutRow([modeButton, copiesLabel, copiesSelect, submitButton, nextButton], 10, drawHeight + 8, 8);
  layoutRow([qosLabel, qosSelect, stepButton, resetButton], 10, drawHeight + 44, 10);
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
