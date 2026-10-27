// Frame Budget Scheduler Timeline - p5.js MicroSim
// CANVAS_HEIGHT: 585
// Examine one loop pass against the 40 ms frame. Total = the sum of the costs
// of the tasks that run; a pass overruns when Total > 40.0 ms. With the
// cooperative scheduler on, tasks are considered in order (earlier is more
// important) and a task is deferred when its budget is greater than 40.0
// minus the total so far. With the scheduler off, every due task runs.
// Costs are model inputs from Chapters 5, 6 and 8 and 08-scheduler-demo.py,
// not a measurement of your program.

let canvasWidth = 800;
let drawHeight = 470;
let controlHeight = 115;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

const FRAME = 40.0;
const TASKS = [
  { name: 'audio', cost: 10.0, budget: 12, color: 'steelblue' },
  { name: 'buttons', cost: 0.5, budget: 1, color: 'slategray' },
  { name: 'spectrum', cost: 8.5, budget: 9, color: 'mediumpurple' },
  { name: 'status', cost: 3.0, budget: 4, color: 'darkcyan' },
  { name: 'network', cost: 2.0, budget: 3, color: 'peru' },
  { name: 'time', cost: 3.8, budget: 4, color: 'olivedrab' },
  { name: 'redraw', cost: 129.4, budget: 140, color: 'indianred' },
  { name: 'slice', cost: 16.2, budget: 17, color: 'goldenrod' }
];
const PASSES = [
  { sched: false, due: ['audio', 'buttons', 'spectrum'], total: 19.0, over: false, why: '10.0 + 0.5 + 8.5 = 19.0, which leaves 21.0 ms.' },
  { sched: false, due: ['audio', 'buttons', 'spectrum', 'status', 'network', 'time'], total: 27.8, over: false, why: '19.0 + 3.0 + 2.0 + 3.8 = 27.8, which leaves 12.2 ms.' },
  { sched: false, due: ['audio', 'buttons', 'spectrum', 'redraw'], total: 148.4, over: true, why: '19.0 + 129.4 = 148.4, which is 108.4 ms over the frame.' },
  { sched: false, due: ['audio', 'buttons', 'spectrum', 'status', 'network', 'slice'], total: 40.2, over: true, why: '19.0 + 3.0 + 2.0 + 16.2 = 40.2, which is 0.2 ms over.' },
  { sched: true, due: ['audio', 'buttons', 'spectrum', 'status', 'network', 'slice'], total: 24.0, over: false, why: "After network the pass has used 24.0 ms, which leaves 16.0 ms. The slice's budget is 17 ms, which does not fit, so it is deferred." },
  { sched: false, due: ['audio', 'buttons', 'spectrum', 'slice'], total: 35.2, over: false, why: '19.0 + 16.2 = 35.2, which leaves 4.8 ms.' }
];

let mode = 'explore';
let passIndex = 0;
let submitted = false;
let finished = false;
let results = [];
let feedback = '';
let feedbackCorrect = false;

let modeButton, totalLabel, totalInput, overSelect, submitButton, nextButton, schedBox;
let taskBoxes = [];

// run one pass: which tasks run, which are deferred, and the total
function runPass(sched, due) {
  let total = 0;
  const ran = [];
  const deferred = [];
  for (const t of TASKS) {
    if (!due.includes(t.name)) continue;
    if (sched && t.budget > FRAME - total + 1e-9) { deferred.push(t); continue; }
    ran.push({ t: t, start: total });
    total += t.cost;
  }
  return { ran: ran, deferred: deferred, total: Math.round(total * 10) / 10 };
}

function currentPass() {
  if (mode === 'quiz') { const p = PASSES[min(passIndex, 5)]; return { sched: p.sched, due: p.due }; }
  return { sched: schedBox.checked(), due: TASKS.filter((t, i) => taskBoxes[i].checked()).map(t => t.name) };
}

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  modeButton = createButton('Start the 6 passes');
  modeButton.mousePressed(toggleMode);
  totalLabel = createSpan('Total ms:');
  totalInput = createInput('', 'number');
  totalInput.size(80);
  totalInput.attribute('step', '0.1');
  overSelect = createSelect();
  for (const o of ['choose', 'fits', 'overruns']) overSelect.option(o);
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next pass');
  nextButton.mousePressed(nextPass);
  schedBox = createCheckbox(' Scheduler on', false);
  for (const t of TASKS) taskBoxes.push(createCheckbox(' ' + t.name, ['audio', 'buttons', 'spectrum'].includes(t.name)));
  for (const el of [modeButton, totalLabel, totalInput, overSelect, submitButton, nextButton, schedBox, ...taskBoxes]) el.style('font-size', '16px');

  positionControls();
  updateControlStates();

  describe('A timeline of one loop pass: each task that runs is a colored block whose width is its cost in milliseconds, laid end to end against a 40 ms frame line, with any time past 40 ms shaded as an overrun. Tasks the cooperative scheduler defers are listed below. Checkboxes switch the eight tasks and the scheduler on and off; a six-pass quiz asks for the total time and whether the pass overruns.', LABEL);
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
  text('Frame Budget Scheduler Timeline', canvasWidth / 2, 10);
  const cp = currentPass();
  textSize(16);
  fill('dimgray');
  let status = 'Scheduler ' + (cp.sched ? 'on' : 'off') + ' (costs are model inputs, not a measurement of your program)';
  if (mode === 'quiz') status = (finished ? 'All 6 passes done' : 'Pass ' + (passIndex + 1) + ' of 6') + '   |   Score: ' + countCorrect() + ' of 6   |   scheduler ' + (cp.sched ? 'on' : 'off');
  textSize(mode === 'quiz' ? 16 : 14);
  text(status, canvasWidth / 2, 42);

  const res = runPass(cp.sched, cp.due);
  const reveal = mode === 'explore' || submitted;
  if (mode === 'quiz') drawDue(cp, 70);
  if (reveal) drawTimeline(res, mode === 'quiz' ? 108 : 78);
  else {
    noStroke();
    fill('dimgray');
    textAlign(CENTER, CENTER);
    textSize(16);
    text('The pass is drawn on the timeline after you submit.', canvasWidth / 2, 190);
  }
  drawTaskTable(margin, 270, canvasWidth - 2 * margin);
  drawPanel(res, margin, 364, canvasWidth - 2 * margin, drawHeight - 372);
}

function drawDue(cp, y) {
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(15);
  drawWrapped('Tasks due in this pass: ' + cp.due.join(', ') + '.', margin, y, canvasWidth - 2 * margin, 18);
}

function drawTimeline(res, y) {
  const x0 = 50;
  const x1 = canvasWidth - 25;
  const xMax = max(45, res.total * 1.05);
  const X = ms => x0 + (x1 - x0) * ms / xMax;
  const bh = 46;
  // overrun zone
  noStroke();
  fill(255, 0, 0, 30);
  rect(X(FRAME), y, x1 - X(FRAME), bh + 30);
  for (const r of res.ran) {
    const xa = X(r.start);
    const xb = X(r.start + r.t.cost);
    stroke('white');
    fill(r.t.color);
    rect(xa, y + 14, max(1, xb - xa), bh);
    noStroke();
    fill('white');
    textAlign(CENTER, CENTER);
    textSize(12);
    if (xb - xa > textWidth(r.t.name) + 4) {
      text(r.t.name, (xa + xb) / 2, y + 14 + bh / 2 - 8);
      text(r.t.cost.toFixed(1), (xa + xb) / 2, y + 14 + bh / 2 + 8);
    }
  }
  stroke('red');
  strokeWeight(2);
  drawingContext.setLineDash([6, 4]);
  line(X(FRAME), y, X(FRAME), y + bh + 30);
  drawingContext.setLineDash([]);
  strokeWeight(1);
  noStroke();
  fill('red');
  textAlign(LEFT, TOP);
  textSize(13);
  text('40 ms frame', X(FRAME) + 4, y);
  // axis
  stroke('black');
  line(x0, y + bh + 30, x1, y + bh + 30);
  const step = xMax > 100 ? 20 : 5;
  noStroke();
  fill('dimgray');
  textAlign(CENTER, TOP);
  for (let ms = 0; ms <= xMax; ms += step) text(ms, X(ms), y + bh + 34);
  textAlign(RIGHT, TOP);
  text('ms', x1, y + bh + 48);
  // total and deferred
  fill(res.total > FRAME ? 'firebrick' : 'darkgreen');
  textAlign(LEFT, TOP);
  textSize(15);
  textStyle(BOLD);
  const over = res.total > FRAME ? 'overruns by ' + (res.total - FRAME).toFixed(1) + ' ms' : 'fits, ' + (FRAME - res.total).toFixed(1) + ' ms left';
  text('Total ' + res.total.toFixed(1) + ' ms: ' + over, x0, y + bh + 66);
  textStyle(NORMAL);
  if (res.deferred.length) {
    fill('dimgray');
    text('Deferred by the scheduler: ' + res.deferred.map(t => t.name + ' (budget ' + t.budget + ' ms)').join(', '), x0 + 270, y + bh + 66);
  }
}

function drawTaskTable(x, y, w) {
  fill(255, 255, 255, 235);
  stroke('silver');
  rect(x, y, w, 86, 8);
  noStroke();
  textAlign(LEFT, TOP);
  textSize(13);
  fill('black');
  textStyle(BOLD);
  text('Task (in scheduler order): cost / budget in ms', x + 8, y + 5);
  textStyle(NORMAL);
  const cw = (w - 16) / 4;
  TASKS.forEach((t, i) => {
    const cx = x + 8 + (i % 4) * cw;
    const cy = y + 26 + Math.floor(i / 4) * 26;
    fill(t.color);
    rect(cx, cy + 2, 12, 12);
    fill('black');
    text((i + 1) + ' ' + t.name + ': ' + t.cost.toFixed(1) + ' / ' + t.budget, cx + 16, cy);
  });
}

function drawPanel(res, x, y, w, h) {
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
    text('How much of the 40 ms is left?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Turn tasks on and off and flip the scheduler. Try status, network and slice together, with the scheduler off and then on.', x + pad, yy + 22, tw, 20);
    return;
  }
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 5 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 6. ' + (sc >= 5 ? 'Mastery reached.' : 'Mastery is 5 of 6.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('Passes 4 and 5 held the same tasks. What did the scheduler do differently, and what did it cost?', x + pad, yy + 24, tw, 20);
    return;
  }
  if (!submitted) {
    fill('navy');
    textStyle(ITALIC);
    text('How long does this pass take, and does it overrun?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Add the costs of the tasks that run (with the scheduler on, check each budget against what is left). Type the total (within 0.1 ms), choose fits or overruns, and Submit.', x + pad, yy + 22, tw, 20);
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
    passIndex = 0;
    results = [];
    submitted = false;
    finished = false;
  } else {
    mode = 'explore';
  }
  totalInput.value('');
  overSelect.selected('choose');
  updateControlStates();
}

function submitAnswer() {
  if (mode !== 'quiz' || submitted || finished) return;
  const raw = totalInput.value().trim();
  const o = overSelect.value();
  if (raw === '' || isNaN(Number(raw)) || o === 'choose') return;
  const p = PASSES[passIndex];
  const correct = abs(Number(raw) - p.total) <= 0.1 + 1e-9 && (o === 'overruns') === p.over;
  results[passIndex] = correct;
  feedbackCorrect = correct;
  feedback = correct ? 'Correct: ' + p.why : 'Not quite. The total is ' + p.total.toFixed(1) + ' ms and it ' + (p.over ? 'overruns' : 'fits') + ': ' + p.why;
  submitted = true;
  updateControlStates();
}

function nextPass() {
  if (!submitted) return;
  if (passIndex === PASSES.length - 1) finished = true;
  else { passIndex++; submitted = false; }
  totalInput.value('');
  overSelect.selected('choose');
  updateControlStates();
}

function setEnabled(el, on) {
  const input = el.elt.querySelector('input');
  (input || el.elt).disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  const answering = quiz && !submitted && !finished;
  modeButton.html(quiz ? 'Back to explore' : 'Start the 6 passes');
  setEnabled(totalInput, answering);
  setEnabled(overSelect, answering);
  setEnabled(submitButton, answering);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(passIndex === PASSES.length - 1 ? 'See score' : 'Next pass');
  for (const el of [schedBox, ...taskBoxes]) setEnabled(el, !quiz);
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
  layoutRow([modeButton, totalLabel, totalInput, overSelect, submitButton, nextButton], 10, drawHeight + 8, 8);
  layoutRow([schedBox, ...taskBoxes.slice(0, 4)], 10, drawHeight + 46, 14);
  layoutRow(taskBoxes.slice(4), 10, drawHeight + 82, 14);
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
