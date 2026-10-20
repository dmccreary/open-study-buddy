// Device Mode State Machine - p5.js MicroSim
// CANVAS_HEIGHT: 580
// Use the Study Buddy's transition table to find the final mode and volume
// after a sequence of button events. The machine below is the Device class
// from Chapter 7 ("The State Machine" and "The Settings Screen"): five modes,
// a long press is 800 ms or more, a MODE hold under 0.2 s returns to CLOCK,
// and the volume starts at 40 and moves in steps of 10 between 0 and 100.
// Layout adapted from the state-machine-template MicroSim.

let canvasWidth = 800;
let drawHeight = 500;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

const MODES = ['CLOCK', 'LISTENING', 'THINKING', 'SPEAKING', 'SETTINGS'];
const LONG_MS = 800;
const MIN_MS = 200;
const ITEMS = ['Volume', 'Theme'];

// ---------- the Device class from the chapter ----------
class Device {
  constructor() { this.state = 'CLOCK'; this.volume = 40; this.item = 0; this.theme = 0; }
  go(s) { this.state = s; }
  stepVolume(dir) { this.volume = Math.max(0, Math.min(100, this.volume + 10 * dir)); }
  onButton(name, event, held) {
    const s = this.state;
    const step = name === 'up' ? 1 : -1;
    if (s === 'CLOCK') {
      if (name === 'mode' && event === 'press') this.go('LISTENING');
      else if (name === 'up' && event === 'long') this.go('SETTINGS');
      else if (name !== 'mode' && event === 'release' && held < LONG_MS) this.stepVolume(step);
    } else if (s === 'LISTENING') {
      if (name === 'mode' && event === 'release') this.go(held >= MIN_MS ? 'THINKING' : 'CLOCK');
    } else if (s === 'THINKING') {
      if (name === 'mode' && event === 'press') this.go('CLOCK');
    } else if (s === 'SPEAKING') {
      if (name === 'mode' && event === 'press') this.go('CLOCK');
      else if (name !== 'mode' && event === 'press') this.stepVolume(step);
    } else if (s === 'SETTINGS') {
      if (name === 'mode' && event === 'long') this.go('CLOCK');
      else if (name === 'mode' && event === 'release' && held < LONG_MS) this.item = (this.item + 1) % ITEMS.length;
      else if (name !== 'mode' && event === 'press') {
        if (this.item === 0) this.stepVolume(step); else this.theme = 1 - this.theme;
      }
    }
  }
  onInternal(what) {
    if (this.state === 'LISTENING' && what === 'full') this.go('THINKING');
    else if (this.state === 'THINKING' && what === 'reply') this.go('SPEAKING');
    else if (this.state === 'SPEAKING' && what === 'done') this.go('CLOCK');
  }
}

// ---------- event builders: one displayed line = one or more low-level events ----------
const press = n => ({ txt: n.toUpperCase() + ' pressed', ev: [[n, 'press', 0]] });
const release = (n, ms) => ({ txt: n.toUpperCase() + ' released after ' + ms / 1000 + ' s', ev: [[n, 'release', ms]] });
const tap = (n, ms) => ({ txt: n.toUpperCase() + ' pressed and released after ' + ms / 1000 + ' s', ev: [[n, 'press', 0], [n, 'release', ms]] });
const click = n => ({ txt: n.toUpperCase() + ' pressed', ev: [[n, 'press', 0], [n, 'release', 100]] });
const hold = (n, ms) => ({ txt: n.toUpperCase() + ' held for ' + ms / 1000 + ' s (a long press)', ev: [[n, 'press', 0], [n, 'long', 0], [n, 'release', ms]] });
const internal = (what, txt) => ({ txt: txt, ev: [['internal', what, 0]] });

const SAMPLE = [
  tap('up', 100), press('mode'), release('mode', 1200), click('up'),
  internal('reply', 'reply arrives'), click('down'), internal('done', 'speech finished')
];
const SEQUENCES = [
  { lines: [press('mode'), release('mode', 1500)], mode: 'THINKING', vol: 40,
    why: 'The hold is at least 0.2 s, so releasing sends the question and waits for the reply.' },
  { lines: [press('mode'), release('mode', 100)], mode: 'CLOCK', vol: 40,
    why: 'The hold is under 0.2 s, so it was a bump, and the device returns to the clock.' },
  { lines: [press('mode'), release('mode', 1500), internal('reply', 'reply arrives')], mode: 'SPEAKING', vol: 40,
    why: 'A reply in THINKING moves the device to SPEAKING.' },
  { lines: [hold('up', 1000), click('down'), tap('mode', 100)], mode: 'SETTINGS', vol: 30,
    why: 'The long press of UP opens SETTINGS, DOWN lowers the value of the first setting (volume) by 10, and a short MODE press only moves to the next setting.' },
  { lines: [press('mode'), release('mode', 1500), { txt: 'MODE pressed again', ev: [['mode', 'press', 0]] }], mode: 'CLOCK', vol: 40,
    why: 'A MODE press in THINKING cancels and returns to the clock.' },
  { lines: [tap('up', 100), tap('up', 100)], mode: 'CLOCK', vol: 60,
    why: 'Each short UP press in CLOCK raises the volume by 10, from 40 to 50 to 60.' }
];

// edges of the diagram: [from, to, label, where the label sits along the edge
// (default 0.5), which side of the edge (default: the side of the offset)].
// Both CLOCK-LISTENING labels go on the outer side, spread along the edge.
const EDGES = [
  ['CLOCK', 'LISTENING', 'MODE press', 0.72, -1],
  ['LISTENING', 'CLOCK', 'release < 0.2 s', 0.72],
  ['LISTENING', 'THINKING', 'release >= 0.2 s\nor buffer full'],
  ['THINKING', 'SPEAKING', 'reply arrives'],
  ['THINKING', 'CLOCK', 'MODE press (cancel)'],
  ['SPEAKING', 'CLOCK', 'MODE press or speech done'],
  ['CLOCK', 'SETTINGS', 'UP long press'],
  ['SETTINGS', 'CLOCK', 'MODE long press']
];

let mode = 'explore';
let seqIndex = 0;
let step = 0;            // lines executed so far in the shown sequence
let submitted = false;
let finished = false;
let results = [];
let feedback = '';
let feedbackCorrect = false;

let modeButton, modeLabel, modeSelect, volLabel, volSelect, submitButton, nextButton, stepButton, replayButton;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  modeButton = createButton('Start the 6 sequences');
  modeButton.mousePressed(toggleMode);
  modeLabel = createSpan('Final mode:');
  modeSelect = createSelect();
  modeSelect.option('choose');
  for (const m of MODES) modeSelect.option(m);
  volLabel = createSpan('Volume:');
  volSelect = createSelect();
  volSelect.option('choose');
  for (const v of [30, 40, 50, 60]) volSelect.option(String(v));
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next sequence');
  nextButton.mousePressed(nextSequence);
  stepButton = createButton('Step');
  stepButton.mousePressed(stepForward);
  replayButton = createButton('Back to start');
  replayButton.mousePressed(() => { step = 0; updateControlStates(); });
  for (const el of [modeButton, modeLabel, modeSelect, volLabel, volSelect, submitButton, nextButton, stepButton, replayButton]) {
    el.style('font-size', '16px');
  }

  positionControls();
  updateControlStates();

  describe('A state diagram of the five Study Buddy modes: CLOCK in the center, with LISTENING, THINKING, SPEAKING and SETTINGS around it and arrows labeled with the button events that move between them. A list on the right shows a sequence of button events; the learner steps through it, or predicts the final mode and volume and then sees the mode after each event.', LABEL);
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
  text('Device Mode State Machine', canvasWidth / 2, 10);
  textSize(16);
  fill('dimgray');
  let status;
  if (mode === 'explore') status = 'Explore: step through a sample sequence (illustrative)';
  else if (finished) status = 'All 6 sequences done   |   Score: ' + countCorrect() + ' of 6';
  else status = 'Sequence ' + (seqIndex + 1) + ' of 6 (illustrative)   |   Score: ' + countCorrect() + ' of 6';
  text(status, canvasWidth / 2, 42);

  const lines = currentLines();
  const trace = runLines(lines);
  const shownStep = (mode === 'quiz' && !submitted) ? 0 : step;
  const st = trace[shownStep];
  const lastEdge = shownStep > 0 && trace[shownStep - 1].state !== st.state ? [trace[shownStep - 1].state, st.state] : null;

  const dw = canvasWidth * 0.56;
  drawDiagram(margin, 70, dw - margin, drawHeight - 80, st, lastEdge);
  drawSequencePanel(dw + 5, 70, canvasWidth - dw - 5 - margin, drawHeight - 80, lines, trace, shownStep);
}

function currentLines() {
  return mode === 'explore' ? SAMPLE : SEQUENCES[min(seqIndex, SEQUENCES.length - 1)].lines;
}

// run every line on a fresh device; trace[i] is the state after i lines
function runLines(lines) {
  const d = new Device();
  const trace = [{ state: d.state, volume: d.volume, item: d.item }];
  for (const ln of lines) {
    for (const [name, ev, held] of ln.ev) {
      if (name === 'internal') d.onInternal(ev); else d.onButton(name, ev, held);
    }
    trace.push({ state: d.state, volume: d.volume, item: d.item });
  }
  return trace;
}

// ---------- diagram ----------

function nodePositions(x, y, w, h) {
  return {
    CLOCK:     { x: x + w * 0.5,  y: y + h * 0.47 },
    LISTENING: { x: x + w * 0.2,  y: y + h * 0.12 },
    THINKING:  { x: x + w * 0.8,  y: y + h * 0.12 },
    SPEAKING:  { x: x + w * 0.8,  y: y + h * 0.80 },
    SETTINGS:  { x: x + w * 0.2,  y: y + h * 0.80 }
  };
}

function drawDiagram(x, y, w, h, st, lastEdge) {
  fill(255, 255, 255, 200);
  stroke('silver');
  rect(x, y, w, h, 10);
  const P = nodePositions(x, y + 10, w, h - 70);
  const nw = min(118, w * 0.27);
  const nh = 42;

  for (const [a, b, lbl, at, side] of EDGES) {
    const pair = EDGES.some(e => e[0] === b && e[1] === a);
    const hot = lastEdge && lastEdge[0] === a && lastEdge[1] === b;
    drawEdge(P[a], P[b], nw, nh, pair ? 9 : 0, lbl, hot, at === undefined ? 0.5 : at, side);
  }
  for (const m of MODES) {
    const p = P[m];
    const cur = st.state === m;
    stroke(cur ? 'navy' : 'steelblue');
    strokeWeight(cur ? 3 : 1.5);
    fill(cur ? 'royalblue' : 'lavender');
    rect(p.x - nw / 2, p.y - nh / 2, nw, nh, 10);
    strokeWeight(1);
    noStroke();
    fill(cur ? 'white' : 'black');
    textAlign(CENTER, CENTER);
    textSize(15);
    textStyle(BOLD);
    text(m, p.x, p.y - (m === 'SETTINGS' ? 7 : 0));
    textStyle(NORMAL);
    if (m === 'SETTINGS') {
      textSize(13);
      text('item: ' + ITEMS[st.item], p.x, p.y + 11);
    }
  }

  // volume gauge
  const gy = y + h - 42;
  const gx = x + 20;
  const gw = w - 40;
  noStroke();
  fill('black');
  textAlign(LEFT, BOTTOM);
  textSize(16);
  text('Volume: ' + st.volume + '   (0 to 100, steps of 10)', gx, gy - 4);
  stroke('silver');
  fill('whitesmoke');
  rect(gx, gy, gw, 16, 4);
  noStroke();
  fill('seagreen');
  rect(gx, gy, gw * st.volume / 100, 16, 4);
}

function drawEdge(p, q, nw, nh, offset, lbl, hot, at, sideOverride) {
  const dx = q.x - p.x;
  const dy = q.y - p.y;
  const len = sqrt(dx * dx + dy * dy);
  const ux = dx / len;
  const uy = dy / len;
  const ox = -uy * offset;
  const oy = ux * offset;
  // distance from a node center to its border along the direction
  const cut = (vx, vy) => min(abs(vx) > 1e-6 ? (nw / 2 + 4) / abs(vx) : 1e9, abs(vy) > 1e-6 ? (nh / 2 + 4) / abs(vy) : 1e9);
  const c = cut(ux, uy);
  const x1 = p.x + ux * c + ox;
  const y1 = p.y + uy * c + oy;
  const x2 = q.x - ux * c + ox;
  const y2 = q.y - uy * c + oy;
  const col = hot ? 'royalblue' : 'gray';
  stroke(col);
  strokeWeight(hot ? 3 : 1.5);
  line(x1, y1, x2, y2);
  noStroke();
  fill(col);
  const ah = 10;
  triangle(x2, y2, x2 - ux * ah - uy * ah * 0.5, y2 - uy * ah + ux * ah * 0.5,
    x2 - ux * ah + uy * ah * 0.5, y2 - uy * ah - ux * ah * 0.5);
  strokeWeight(1);

  // label at the middle, pushed to the side of the offset
  const parts = lbl.split('\n');
  const side = sideOverride !== undefined ? sideOverride : (offset === 0 ? 1 : Math.sign(offset));
  const push = 14 + (parts.length - 1) * 9;
  const mx = x1 + (x2 - x1) * at - uy * push * side;
  const my = y1 + (y2 - y1) * at + ux * push * side;
  textSize(13);
  const tw = max(...parts.map(s => textWidth(s))) + 6;
  const th = 18 * parts.length;
  fill(255, 255, 255, 220);
  rect(mx - tw / 2, my - th / 2, tw, th, 4);
  fill(hot ? 'navy' : 'dimgray');
  textAlign(CENTER, CENTER);
  for (let i = 0; i < parts.length; i++) text(parts[i], mx, my - th / 2 + 9 + 18 * i);
}

// ---------- sequence list, question and feedback ----------

function drawSequencePanel(x, y, w, h, lines, trace, shownStep) {
  fill(255, 255, 255, 235);
  stroke('silver');
  rect(x, y, w, h, 10);
  const pad = 12;
  const tw = w - 2 * pad;
  let yy = y + pad;
  noStroke();
  textAlign(LEFT, TOP);
  textSize(16);
  fill('black');
  textStyle(BOLD);
  text(mode === 'explore' ? 'Sample sequence' : 'Sequence ' + (min(seqIndex, 5) + 1), x + pad, yy);
  textStyle(NORMAL);
  yy += 22;
  fill('dimgray');
  text('Start: CLOCK, volume 40', x + pad, yy);
  yy += 26;

  const reveal = mode === 'explore' ? shownStep : (submitted ? lines.length : 0);
  for (let i = 0; i < lines.length; i++) {
    const active = (mode === 'explore' || submitted) && i === shownStep - 1;
    fill(active ? 'navy' : 'black');
    textStyle(active ? BOLD : NORMAL);
    yy = drawWrapped((i + 1) + '. ' + lines[i].txt, x + pad, yy, tw, 20);
    textStyle(NORMAL);
    if (i < reveal) {
      const t = trace[i + 1];
      fill('seagreen');
      text('    -> ' + t.state + ', volume ' + t.volume, x + pad, yy);
      yy += 20;
    }
    yy += 6;
  }
  yy += 6;

  if (mode === 'explore') {
    fill('dimgray');
    drawWrapped(shownStep < lines.length ? 'Predict what the next event will do, then press Step.' :
      'End of the sample. Notice how UP and DOWN acted differently in CLOCK, THINKING and SPEAKING.', x + pad, yy, tw, 20);
    return;
  }
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 5 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    yy = drawWrapped('Score: ' + sc + ' of 6. ' + (sc >= 5 ? 'Mastery reached.' : 'Mastery is 5 of 6.'), x + pad, yy, tw, 20);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('The same MODE press did different things in CLOCK, THINKING and SETTINGS. Which row of the table explains each?', x + pad, yy + 4, tw, 20);
    return;
  }
  if (!submitted) {
    fill('navy');
    textStyle(ITALIC);
    text('Where does the device end up?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Choose the final mode and volume below, then Submit. One attempt.', x + pad, yy + 22, tw, 20);
    return;
  }
  fill(feedbackCorrect ? 'darkgreen' : 'firebrick');
  textStyle(BOLD);
  yy = drawWrapped(feedback, x + pad, yy, tw, 20);
  textStyle(NORMAL);
  fill('dimgray');
  drawWrapped('Use Back to start and Step to replay it on the diagram.', x + pad, yy + 4, tw, 20);
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

// ---------- controls and quiz logic ----------

function stepForward() {
  if (step < currentLines().length) step++;
  updateControlStates();
}

function toggleMode() {
  if (mode === 'explore') {
    mode = 'quiz';
    seqIndex = 0;
    results = [];
    finished = false;
  } else {
    mode = 'explore';
  }
  submitted = false;
  step = 0;
  modeSelect.selected('choose');
  volSelect.selected('choose');
  updateControlStates();
}

function submitAnswer() {
  if (mode !== 'quiz' || submitted || finished) return;
  const m = modeSelect.value();
  const v = volSelect.value();
  if (m === 'choose' || v === 'choose') return;
  const sq = SEQUENCES[seqIndex];
  const correct = m === sq.mode && Number(v) === sq.vol;
  results[seqIndex] = correct;
  feedbackCorrect = correct;
  feedback = correct ? 'Correct: ' + sq.why :
    'Not quite. The device ends in ' + sq.mode + ' at volume ' + sq.vol + ': ' + sq.why;
  submitted = true;
  step = sq.lines.length;
  updateControlStates();
}

function nextSequence() {
  if (!submitted) return;
  if (seqIndex === SEQUENCES.length - 1) finished = true;
  else { seqIndex++; submitted = false; step = 0; }
  modeSelect.selected('choose');
  volSelect.selected('choose');
  updateControlStates();
}

function setEnabled(el, on) {
  el.elt.disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  const answering = quiz && !submitted && !finished;
  modeButton.html(quiz ? 'Back to explore' : 'Start the 6 sequences');
  setEnabled(modeSelect, answering);
  setEnabled(volSelect, answering);
  setEnabled(submitButton, answering);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(seqIndex === SEQUENCES.length - 1 ? 'See score' : 'Next sequence');
  const canStep = !quiz || submitted;
  setEnabled(stepButton, canStep && step < currentLines().length);
  setEnabled(replayButton, canStep && step > 0);
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
  layoutRow([modeButton, modeLabel, modeSelect, volLabel, volSelect], 10, drawHeight + 8, 8);
  layoutRow([submitButton, nextButton, stepButton, replayButton], 10, drawHeight + 44, 10);
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
