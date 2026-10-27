// Threat Model Sorter - p5.js MicroSim
// CANVAS_HEIGHT: 620
// Prioritize 10 classroom threats into fix order. Risk score = likelihood x
// impact (each 1 to 3). Order by score, highest first; equal scores put the
// lower effort to fix first (1 easy to 3 hard); equal score and effort put the
// lower threat number first, so the correct order is unique. The ratings are
// the judgments in src/chapters/17-privacy-responsible-listening/tools/threat_model.py:
// reasoned judgments for a classroom, not statistics.

let canvasWidth = 800;
let drawHeight = 540;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

// shown in this scrambled order
const THREATS = [
  { n: 7, d: 'Always-on listening turned on without approval', l: 1, i: 3, e: 1, why: "Score 3, effort 1, and its number is lower than T10's, so it comes ninth." },
  { n: 2, d: 'Eavesdropping on an unencrypted HTTP link', l: 2, i: 3, e: 2, why: 'Score 6 with effort 2: after the three effort-1 threats and T1, before T9.' },
  { n: 10, d: "Someone else's voice triggers the device", l: 3, i: 1, e: 1, why: 'Score 3 ties with T7 and effort ties too, so the higher number goes last.' },
  { n: 4, d: 'secrets.py committed to git', l: 2, i: 3, e: 1, why: "Score 6 with effort 1; its number is higher than T3's." },
  { n: 9, d: 'A cloud vendor keeps recordings', l: 2, i: 3, e: 3, why: 'Score 6 with the highest effort, so it is last of the score-6 group.' },
  { n: 1, d: 'Microphone left open with no indicator', l: 2, i: 3, e: 2, why: 'Score 6 with effort 2: after the effort-1 threats, before T2.' },
  { n: 6, d: 'Server logs keep audio or transcripts', l: 3, i: 2, e: 1, why: "Score 6 with effort 1; its number is higher than T4's." },
  { n: 5, d: 'Prompt injection in a calendar title', l: 2, i: 2, e: 2, why: 'Score 4 is below every score-6 threat; effort 2 and number 5 put it before T8.' },
  { n: 3, d: 'Exposed MQTT broker', l: 2, i: 3, e: 1, why: 'Score 6 with effort 1 and the lowest number among them, so it is first.' },
  { n: 8, d: 'Lost or stolen device', l: 2, i: 2, e: 2, why: 'Score 4 and effort 2 tie with T5, so the higher number goes after it.' }
];

let order = [];           // indexes into THREATS, first to fix at the top
let correctOrder = [];
let selected = 0;
let submitted = false;
let rowBoxes = [];

let threatLabel, threatSelect, upButton, downButton, submitButton, restartButton, likeSlider, impactSlider;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  correctOrder = THREATS.map((t, k) => k).sort((a, b) => {
    const A = THREATS[a];
    const B = THREATS[b];
    return (B.l * B.i - A.l * A.i) || (A.e - B.e) || (A.n - B.n);
  });
  order = THREATS.map((t, k) => k);

  threatLabel = createSpan('Selected:');
  threatSelect = createSelect();
  THREATS.forEach((t, k) => threatSelect.option('T' + t.n, String(k)));
  threatSelect.changed(() => { selected = order.indexOf(Number(threatSelect.value())); });
  upButton = createButton('Move up');
  upButton.mousePressed(() => move(-1));
  downButton = createButton('Move down');
  downButton.mousePressed(() => move(1));
  submitButton = createButton('Submit order');
  submitButton.mousePressed(submitOrder);
  restartButton = createButton('Start over');
  restartButton.mousePressed(restart);
  for (const el of [threatLabel, threatSelect, upButton, downButton, submitButton, restartButton]) el.style('font-size', '16px');
  likeSlider = createSlider(1, 3, 2, 1);
  impactSlider = createSlider(1, 3, 2, 1);
  syncSelect();

  positionControls();
  updateControlStates();

  describe('A table of ten classroom threats with their likelihood, impact and effort to fix, which the learner reorders from first to fix to last to fix by selecting a row and moving it up or down, then submits once. The correct order, each threat\'s risk score and the reason for any misplaced threat are then shown. A small example lets the learner change a likelihood and impact and see the score.', LABEL);
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
  text('Threat Model Sorter', canvasWidth / 2, 10);
  textSize(15);
  fill('dimgray');
  text(submitted ? 'Score: ' + countCorrect() + ' of 10 in the correct position' :
    'Ratings are reasoned judgments for a classroom, not statistics', canvasWidth / 2, 42);

  fill(255, 255, 255, 235);
  stroke('silver');
  rect(margin, 64, canvasWidth - 2 * margin, 26, 6);
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(14);
  text('Fix order: risk score = likelihood x impact, highest first. Ties: lower effort first, then lower threat number.', margin + 8, 77);

  drawTable(margin, 98, canvasWidth - 2 * margin);
  drawExample(margin, 438, canvasWidth - 2 * margin);
  drawPanel(margin, 470, canvasWidth - 2 * margin, drawHeight - 478);

  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  const half = canvasWidth / 2;
  text('Example likelihood: ' + likeSlider.value(), 10, drawHeight + 60);
  text('Example impact: ' + impactSlider.value(), half + 10, drawHeight + 60);
}

function drawTable(x, y, w) {
  const rh = 31;
  const cols = { pos: x + 6, id: x + 44, desc: x + 90, l: x + w - 190, i: x + w - 158, e: x + w - 126, s: x + w - 84, fix: x + w - 36 };
  noStroke();
  fill('black');
  textSize(13);
  textStyle(BOLD);
  textAlign(LEFT, CENTER);
  text('Pos', cols.pos, y + 8);
  text('Threat', cols.id, y + 8);
  text('Description', cols.desc, y + 8);
  textStyle(NORMAL);
  fill('dimgray');
  textAlign(RIGHT, CENTER);
  text('L likelihood, I impact, E effort (1 to 3)', cols.l - 18, y + 8);
  fill('black');
  textStyle(BOLD);
  textAlign(CENTER, CENTER);
  text('L', cols.l, y + 8);
  text('I', cols.i, y + 8);
  text('E', cols.e, y + 8);
  if (submitted) { text('Score', cols.s, y + 8); text('Fix', cols.fix, y + 8); }
  textStyle(NORMAL);
  rowBoxes = [];
  for (let p = 0; p < order.length; p++) {
    const t = THREATS[order[p]];
    const yy = y + 18 + p * rh;
    rowBoxes.push({ y: yy, h: rh - 3 });
    const right = submitted && correctOrder[p] === order[p];
    let bg = p % 2 ? 'whitesmoke' : 'white';
    if (submitted) bg = right ? 'honeydew' : 'mistyrose';
    stroke(p === selected && !submitted ? 'navy' : 'gainsboro');
    strokeWeight(p === selected && !submitted ? 2 : 1);
    fill(p === selected && !submitted ? 'lightcyan' : bg);
    rect(x, yy, w, rh - 3, 4);
    strokeWeight(1);
    noStroke();
    fill('black');
    textSize(14);
    textAlign(LEFT, CENTER);
    text(p + 1, cols.pos + 6, yy + rh / 2 - 1);
    textStyle(BOLD);
    text('T' + t.n, cols.id, yy + rh / 2 - 1);
    textStyle(NORMAL);
    let d = t.d;
    while (textWidth(d) > cols.l - 22 - cols.desc && d.length > 6) d = d.slice(0, -1);
    if (d !== t.d) d = d.trim() + '...';
    text(d, cols.desc, yy + rh / 2 - 1);
    textAlign(CENTER, CENTER);
    text(t.l, cols.l, yy + rh / 2 - 1);
    text(t.i, cols.i, yy + rh / 2 - 1);
    text(t.e, cols.e, yy + rh / 2 - 1);
    if (submitted) {
      text(t.l * t.i, cols.s, yy + rh / 2 - 1);
      fill(right ? 'darkgreen' : 'firebrick');
      textStyle(BOLD);
      text(correctOrder.indexOf(order[p]) + 1, cols.fix, yy + rh / 2 - 1);
      textStyle(NORMAL);
    }
  }
}

function drawExample(x, y, w) {
  const l = Number(likeSlider.value());
  const im = Number(impactSlider.value());
  noStroke();
  fill('dimgray');
  textAlign(LEFT, TOP);
  textSize(14);
  drawWrapped('Example (not one of the 10): a guest phone joins the class Wi-Fi. Likelihood ' + l + ' x impact ' + im + ' = risk score ' + (l * im) + '.',
    x, y, w, 17);
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
  textSize(15);
  if (!submitted) {
    fill('navy');
    textStyle(ITALIC);
    text('Which threat should you fix first, and why?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Click a row (or pick it in Selected) and move it with Move up / Move down until the list runs from first to fix to last. Submit once.', x + pad, yy + 20, tw, 18);
    return;
  }
  const t = THREATS[order[selected]];
  const right = correctOrder[selected] === order[selected];
  const sc = countCorrect();
  fill(sc >= 8 ? 'darkgreen' : 'firebrick');
  textStyle(BOLD);
  text('Score: ' + sc + ' of 10. ' + (sc >= 8 ? 'Mastery reached.' : 'Mastery is 8 of 10.') + ' Six threats tie at 6: what decided their order?', x + pad, yy);
  textStyle(NORMAL);
  fill(right ? 'darkgreen' : 'firebrick');
  drawWrapped((right ? 'T' + t.n + ' is in the right place: ' : 'Not quite. T' + t.n + ' belongs in position ' + (correctOrder.indexOf(order[selected]) + 1) + ': ') + t.why +
    ' (Click any row to read its reason.)', x + pad, yy + 22, tw, 18);
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
  return order.filter((k, p) => correctOrder[p] === k).length;
}

// clicking a row selects it
function mousePressed() {
  if (mouseX < margin || mouseX > canvasWidth - margin) return;
  rowBoxes.forEach((b, p) => {
    if (mouseY >= b.y && mouseY <= b.y + b.h) { selected = p; syncSelect(); updateControlStates(); }
  });
}

function syncSelect() {
  threatSelect.selected(String(order[selected]));
}

function move(dir) {
  if (submitted) return;
  const to = selected + dir;
  if (to < 0 || to >= order.length) return;
  [order[selected], order[to]] = [order[to], order[selected]];
  selected = to;
  syncSelect();
  updateControlStates();
}

function submitOrder() {
  if (submitted) return;
  submitted = true;
  // show the first misplaced threat's reason first
  const firstWrong = order.findIndex((k, p) => correctOrder[p] !== k);
  selected = firstWrong >= 0 ? firstWrong : 0;
  syncSelect();
  updateControlStates();
}

function restart() {
  order = THREATS.map((t, k) => k);
  selected = 0;
  submitted = false;
  syncSelect();
  updateControlStates();
}

function setEnabled(el, on) {
  el.elt.disabled = !on;
}

function updateControlStates() {
  setEnabled(upButton, !submitted && selected > 0);
  setEnabled(downButton, !submitted && selected < order.length - 1);
  setEnabled(submitButton, !submitted);
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
  layoutRow([threatLabel, threatSelect, upButton, downButton, submitButton, restartButton], 10, drawHeight + 8, 8);
  const half = canvasWidth / 2;
  likeSlider.position(180, drawHeight + 50);
  likeSlider.size(half - 180 - 20);
  impactSlider.position(half + 160, drawHeight + 50);
  impactSlider.size(half - 160 - margin);
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
