// VAD Boundary Finder - p5.js MicroSim
// CANVAS_HEIGHT: 635
// Execute the voice activity detection rules of Chapter 11 (vad.py, levels.py).
// The hysteresis gate opens at bits >= 15.0 and closes at bits < 14.5; a frame
// is loud when the gate is open. Speech starts after START_FRAMES (3) loud
// frames in a row and ends after END_FRAMES (15) quiet frames in a row.
// Start = first frame of the loud run that reached 3; End = the last loud frame.
// Kept frames: max(0, start - 4) to min(total - 1, end + 5).
// All traces are synthetic.

let canvasWidth = 800;
let drawHeight = 520;
let controlHeight = 115;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

const OPEN = 15.0;
const CLOSE = 14.5;
const PRE_ROLL = 4;
const HANG_OVER = 5;
const STATES = ['SILENCE', 'STARTING', 'SPEECH', 'ENDING'];

// each trace is runs of [frame count, bits]
const TRACES = [
  { runs: [[5, 13], [8, 17], [6, 13], [8, 17], [20, 13]], start: 5, end: 26,
    why: 'The 6 quiet frames in the middle are fewer than 15, so the two words are one utterance. The last loud frame is 26 (5 + 8 + 6 + 8 - 1), and the first is 5.' },
  { runs: [[10, 13], [1, 18], [30, 13]], start: null, end: null,
    why: 'One loud frame is fewer than 3 in a row, so the click never starts speech.' },
  { runs: [[6, 13], [2, 17], [1, 13], [2, 17], [1, 13], [2, 17], [30, 13]], start: null, end: null,
    why: 'Each loud run is 2 frames and a quiet frame resets the count, so the count never reaches 3.' },
  { runs: [[8, 13], [40, 17]], start: 8, end: 47,
    why: 'The speech is still going when the trace ends, so the end is the last loud frame, 47. The kept range stops at the last frame of the recording.' },
  { runs: [[3, 13], [10, 17], [14, 13], [10, 17], [25, 13]], start: 3, end: 36,
    why: 'A pause of 14 frames is one short of 15, so it does not end the speech. The pre-roll would start at frame -1, so it stops at frame 0.' }
];

let mode = 'explore';
let traceIndex = 0;
let step = 0;               // frames processed so far
let submitted = false;
let finished = false;
let results = [];
let feedback = '';
let feedbackCorrect = false;

let modeButton, startLabel, startInput, endLabel, endInput, submitButton, nextButton;
let stepButton, resetButton, runButton, startSlider, endSlider;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  modeButton = createButton('Start the 5 traces');
  modeButton.mousePressed(toggleMode);
  startLabel = createSpan('Start frame:');
  startInput = createInput('');
  startInput.size(70);
  startInput.attribute('placeholder', 'or none');
  endLabel = createSpan('End frame:');
  endInput = createInput('');
  endInput.size(70);
  endInput.attribute('placeholder', 'or none');
  endInput.elt.addEventListener('keydown', e => { if (e.key === 'Enter') submitAnswer(); });
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next trace');
  nextButton.mousePressed(nextTrace);
  stepButton = createButton('Step');
  stepButton.mousePressed(() => { if (step < frames().length) step++; updateControlStates(); });
  resetButton = createButton('Back to start');
  resetButton.mousePressed(() => { step = 0; updateControlStates(); });
  runButton = createButton('Run to end');
  runButton.mousePressed(() => { step = frames().length; updateControlStates(); });
  for (const el of [modeButton, startLabel, startInput, endLabel, endInput, submitButton, nextButton, stepButton, resetButton, runButton]) {
    el.style('font-size', '16px');
  }
  startSlider = createSlider(1, 6, 3, 1);
  endSlider = createSlider(5, 30, 15, 1);
  startSlider.input(() => { step = min(step, frames().length); });
  endSlider.input(() => { step = min(step, frames().length); });

  positionControls();
  updateControlStates();

  describe('A bar chart of loudness in bits for each frame of a recording, with the gate levels at 15.0 and 14.5 bits. Below it, a four-state machine (SILENCE, STARTING, SPEECH, ENDING) highlights the current state while the learner steps frame by frame, with the loud and quiet counts. The start and end frames and the kept range are marked once found.', LABEL);
}

function frames() {
  const out = [];
  for (const [n, b] of TRACES[traceIndex].runs) for (let i = 0; i < n; i++) out.push(b);
  return out;
}

function params() {
  if (mode === 'quiz') return { startN: 3, endN: 15 };
  return { startN: Number(startSlider.value()), endN: Number(endSlider.value()) };
}

// Run the VAD over the trace; rec[i] is the state after frame i.
function runVad(tr, startN, endN) {
  let gate = false;
  let state = 'SILENCE';
  let loud = 0;
  let quiet = 0;
  let runStart = null;
  let start = null;
  let end = null;
  let last = null;
  let done = false;
  const rec = [];
  tr.forEach((b, i) => {
    if (!gate && b >= OPEN) gate = true;
    else if (gate && b < CLOSE) gate = false;
    let signal = '';
    if (!done) {
      if (state === 'SILENCE') {
        if (gate) { loud = 1; runStart = i; state = 'STARTING'; }
      } else if (state === 'STARTING') {
        if (gate) loud++;
        else { loud = 0; state = 'SILENCE'; }
      } else if (state === 'SPEECH') {
        if (gate) last = i;
        else { quiet = 1; state = 'ENDING'; }
      } else if (state === 'ENDING') {
        if (gate) { quiet = 0; last = i; state = 'SPEECH'; }
        else quiet++;
      }
      if (state === 'STARTING' && loud >= startN) {
        state = 'SPEECH'; start = runStart; last = i; signal = 'start (first loud frame ' + runStart + ')';
      }
      if (state === 'ENDING' && quiet >= endN) {
        state = 'SILENCE'; end = last; done = true; signal = 'end (last loud frame ' + last + ')';
      }
    }
    rec.push({ bits: b, gate: gate, state: state, loud: state === 'STARTING' || state === 'SPEECH' ? loud : 0, quiet: state === 'ENDING' ? quiet : 0, signal: signal });
  });
  if (start !== null && end === null) end = last;
  const kept = start === null ? null : [max(0, start - PRE_ROLL), min(tr.length - 1, end + HANG_OVER)];
  return { rec: rec, start: start, end: end, kept: kept };
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
  text('VAD Boundary Finder', canvasWidth / 2, 10);
  const p = params();
  textSize(16);
  fill('dimgray');
  let status = 'Trace ' + (traceIndex + 1) + ' (synthetic): START_FRAMES ' + p.startN + ', END_FRAMES ' + p.endN;
  if (mode === 'quiz') status = (finished ? 'All 5 traces done' : 'Trace ' + (traceIndex + 1) + ' of 5 (synthetic)') +
    '   |   Score: ' + countCorrect() + ' of 5';
  text(status, canvasWidth / 2, 42);

  const tr = frames();
  const res = runVad(tr, p.startN, p.endN);
  const showMachine = mode === 'explore' || submitted;
  drawBars(tr, res, showMachine, 84, 160);
  if (showMachine) drawMachine(res, 280);
  else drawHiddenMachine(280);
  drawPanel(tr, res, margin, 410, canvasWidth - 2 * margin, drawHeight - 418);

  noStroke();
  fill(mode === 'explore' ? 'black' : 'silver');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  const half = canvasWidth / 2;
  text('START: ' + startSlider.value(), 10, drawHeight + 98);
  text('END: ' + endSlider.value(), half + 10, drawHeight + 98);
}

function drawBars(tr, res, showMarks, top, h) {
  const x0 = 60;
  const x1 = canvasWidth - 20;
  const cw = (x1 - x0) / tr.length;
  const lo = 12;
  const hi = 19;
  const Y = b => top + h - h * (b - lo) / (hi - lo);
  // kept range
  const known = showMarks && (mode === 'quiz' || step >= tr.length || (res.end !== null && stepPast(res, 'end')));
  if (known && res.kept) {
    noStroke();
    fill(255, 215, 0, 80);
    rect(x0 + res.kept[0] * cw, top - 4, (res.kept[1] - res.kept[0] + 1) * cw, h + 8);
  }
  textSize(13);
  for (let b = 13; b <= 18; b++) {
    stroke('gainsboro');
    line(x0, Y(b), x1, Y(b));
    noStroke();
    fill('dimgray');
    textAlign(RIGHT, CENTER);
    text(b, x0 - 6, Y(b));
  }
  push();
  translate(16, top + h / 2);
  rotate(-HALF_PI);
  textAlign(CENTER, CENTER);
  fill('black');
  text('loudness (bits)', 0, 0);
  pop();
  for (let i = 0; i < tr.length; i++) {
    const loudFrame = res.rec[i].gate;
    noStroke();
    fill(loudFrame ? 'royalblue' : 'lightsteelblue');
    rect(x0 + i * cw + 0.5, Y(tr[i]), max(1, cw - 1), Y(lo) - Y(tr[i]));
    if (i % 5 === 0) {
      fill('dimgray');
      textAlign(CENTER, TOP);
      text(i, x0 + (i + 0.5) * cw, top + h + 4);
    }
  }
  textAlign(RIGHT, TOP);
  text('frame', x0 - 8, top + h + 4);
  stroke('seagreen');
  drawingContext.setLineDash([6, 4]);
  line(x0, Y(OPEN), x1, Y(OPEN));
  stroke('darkorange');
  line(x0, Y(CLOSE), x1, Y(CLOSE));
  drawingContext.setLineDash([]);
  noStroke();
  textSize(13);
  fill('seagreen');
  textAlign(LEFT, BOTTOM);
  text('open 15.0', x0 + 4, Y(OPEN) - 1);
  fill('darkorange');
  textAlign(LEFT, TOP);
  text('close 14.5', x0 + 4, Y(CLOSE) + 1);
  // start and end markers
  if (showMarks) {
    const marks = [];
    if (res.start !== null && (mode === 'quiz' || stepPast(res, 'start'))) marks.push([res.start, 'start ' + res.start]);
    if (res.end !== null && known) marks.push([res.end, 'end ' + res.end]);
    for (const [f, lbl] of marks) {
      const mx = x0 + (f + 0.5) * cw;
      stroke('crimson');
      strokeWeight(2);
      line(mx, top - 2, mx, top + h);
      strokeWeight(1);
      noStroke();
      fill('crimson');
      textAlign(CENTER, BOTTOM);
      textSize(13);
      text(lbl, mx, top - 3);
    }
    // stepping cursor
    if (step > 0 && step <= tr.length && !(mode === 'quiz' && step === tr.length)) {
      const cx = x0 + (step - 0.5) * cw;
      stroke('black');
      strokeWeight(2);
      line(cx, top + h + 2, cx, top + h + 16);
      strokeWeight(1);
    }
  }
}

// has the stepping reached the frame at which this boundary was signaled?
function stepPast(res, which) {
  for (let i = 0; i < min(step, res.rec.length); i++) if (res.rec[i].signal.startsWith(which)) return true;
  return false;
}

function drawMachine(res, y) {
  const n = STATES.length;
  const gap = 34;
  const bw = (canvasWidth - 2 * margin - (n - 1) * gap) / n;
  const cur = step > 0 ? res.rec[min(step, res.rec.length) - 1] : null;
  const curState = cur ? cur.state : 'SILENCE';
  const labels = ['loud', '3rd loud in a row', 'quiet', ''];
  for (let i = 0; i < n; i++) {
    const x = margin + i * (bw + gap);
    const hot = STATES[i] === curState;
    stroke(hot ? 'navy' : 'steelblue');
    strokeWeight(hot ? 3 : 1);
    fill(hot ? 'royalblue' : 'lavender');
    rect(x, y, bw, 38, 8);
    strokeWeight(1);
    noStroke();
    fill(hot ? 'white' : 'black');
    textAlign(CENTER, CENTER);
    textSize(15);
    textStyle(BOLD);
    text(STATES[i], x + bw / 2, y + 19);
    textStyle(NORMAL);
    if (i < n - 1) {
      stroke('gray');
      line(x + bw + 3, y + 19, x + bw + gap - 5, y + 19);
      noStroke();
      fill('gray');
      triangle(x + bw + gap - 3, y + 19, x + bw + gap - 10, y + 15, x + bw + gap - 10, y + 23);
      textSize(12);
      textAlign(CENTER, BOTTOM);
      fill('dimgray');
      if (labels[i]) text(labels[i], x + bw + gap / 2, y + 2);
    }
  }
  noStroke();
  fill('dimgray');
  textSize(13);
  textAlign(LEFT, TOP);
  const yInfo = drawWrapped('Back arrows: a quiet frame sends STARTING back to SILENCE; a loud frame sends ENDING back to SPEECH; the END-th quiet frame in a row ends the speech.',
    margin, y + 44, canvasWidth - 2 * margin, 16);
  fill('black');
  textSize(15);
  const info = cur ? 'Frame ' + (step - 1) + ': ' + cur.bits.toFixed(1) + ' bits, gate ' + (cur.gate ? 'open (loud)' : 'closed (quiet)') +
    ', loud count ' + cur.loud + ', quiet count ' + cur.quiet + ', state ' + cur.state + (cur.signal ? '. Signal: ' + cur.signal : '') :
    'Before frame 0: state SILENCE, both counts 0.';
  drawWrapped(info, margin, yInfo + 4, canvasWidth - 2 * margin, 18);
}

function drawHiddenMachine(y) {
  noStroke();
  fill('dimgray');
  textAlign(CENTER, CENTER);
  textSize(15);
  text('The state machine is shown after you submit.', canvasWidth / 2, y + 30);
}

function drawPanel(tr, res, x, y, w, h) {
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
    text('Where does the speech start and where does it end?', x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    let s = 'Press Step to process one frame. ';
    if (step >= tr.length) s = res.start === null ? 'End of trace: no speech found. ' :
      'End of trace: start ' + res.start + ', end ' + res.end + ', kept frames ' + res.kept[0] + ' to ' + res.kept[1] + '. ';
    drawWrapped(s + 'Notice the start is signaled START-1 frames after the first loud frame, and the end END frames after the last.', x + pad, yy + 22, tw, 19);
    return;
  }
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 4 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 5. ' + (sc >= 4 ? 'Mastery reached.' : 'Mastery is 4 of 5.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('Traces 1 and 5 both had a pause in the middle. Why did neither pause end the speech?', x + pad, yy + 24, tw, 19);
    return;
  }
  if (!submitted) {
    fill('navy');
    textStyle(ITALIC);
    text('Where does the speech start and where does it end?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Count the runs of loud and quiet frames (START 3, END 15). Type the start and end frames, or none for both, then Submit.', x + pad, yy + 22, tw, 19);
    return;
  }
  fill(feedbackCorrect ? 'darkgreen' : 'firebrick');
  textStyle(BOLD);
  const yy2 = drawWrapped(feedback, x + pad, yy, tw, 19);
  textStyle(NORMAL);
  fill('dimgray');
  drawWrapped(res.kept ? 'Kept (gold): frames ' + res.kept[0] + ' to ' + res.kept[1] + '. Back to start and Step replay it.' :
    'Nothing is kept. Back to start and Step replay it.', x + pad, yy2 + 2, tw, 19);
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
    traceIndex = 0;
    results = [];
    submitted = false;
    finished = false;
  } else {
    mode = 'explore';
    traceIndex = 0;
  }
  step = 0;
  startInput.value('');
  endInput.value('');
  updateControlStates();
}

// a frame number, or 'none'; null when unreadable
function readFrame(raw) {
  const s = raw.trim().toLowerCase();
  if (s === 'none') return 'none';
  if (s === '' || isNaN(Number(s))) return null;
  return Number(s);
}

function submitAnswer() {
  if (mode !== 'quiz' || submitted || finished) return;
  const a = readFrame(startInput.value());
  const b = readFrame(endInput.value());
  if (a === null || b === null) return;
  const t = TRACES[traceIndex];
  const want = v => (v === null ? 'none' : v);
  const correct = a === want(t.start) && b === want(t.end);
  results[traceIndex] = correct;
  feedbackCorrect = correct;
  feedback = correct ? 'Correct: ' + t.why : 'Not quite. Start ' + want(t.start) + ', end ' + want(t.end) + ': ' + t.why;
  submitted = true;
  step = frames().length;
  updateControlStates();
}

function nextTrace() {
  if (!submitted) return;
  if (traceIndex === TRACES.length - 1) finished = true;
  else { traceIndex++; submitted = false; step = 0; }
  startInput.value('');
  endInput.value('');
  updateControlStates();
}

function setEnabled(el, on) {
  el.elt.disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  const answering = quiz && !submitted && !finished;
  modeButton.html(quiz ? 'Back to explore' : 'Start the 5 traces');
  setEnabled(startInput, answering);
  setEnabled(endInput, answering);
  setEnabled(submitButton, answering);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(traceIndex === TRACES.length - 1 ? 'See score' : 'Next trace');
  const canStep = !quiz || (submitted && !finished);
  const n = frames().length;
  setEnabled(stepButton, canStep && step < n);
  setEnabled(runButton, canStep && step < n);
  setEnabled(resetButton, canStep && step > 0);
  setEnabled(startSlider, !quiz);
  setEnabled(endSlider, !quiz);
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
  layoutRow([modeButton, startLabel, startInput, endLabel, endInput], 10, drawHeight + 8, 8);
  layoutRow([submitButton, nextButton, stepButton, resetButton, runButton], 10, drawHeight + 44, 10);
  const half = canvasWidth / 2;
  startSlider.position(100, drawHeight + 88);
  startSlider.size(half - 100 - 20);
  endSlider.position(half + 90, drawHeight + 88);
  endSlider.size(half - 90 - margin);
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
