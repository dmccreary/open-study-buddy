// Agent Data Flow Step-Through - p5.js MicroSim
// CANVAS_HEIGHT: 580
// The learner follows one spoken question, "When is my next test?", through
// the eight steps of the agent data flow. Before each of steps 2 to 8 is
// revealed, the learner predicts which part performs it: Terminal, Network,
// or Server. The sim then reveals the owner, the step, the concrete data at
// that step, and the reason. Revealed steps collect as numbered chips under
// the part that performed them, so the final screen groups steps by owner.
// Bloom level: Understand (explain). Step-through, no animation.

// ---------- canvas layout ----------
let canvasWidth = 400;          // replaced by the container width
let drawHeight = 530;           // drawing region (no controls here)
let controlHeight = 50;         // one row of controls
let canvasHeight = drawHeight + controlHeight;
let margin = 16;
let defaultTextSize = 16;

// ---------- content (from the specification) ----------
// job: a neutral statement of what must happen next, shown before the
// prediction so the learner reasons about the job without being told the owner
const steps = [
  { n: 1, owner: 'Student', job: 'The question must be asked.',
    what: 'The student speaks.',
    data: 'The spoken words "When is my next test?"',
    why: 'Shown to start the scenario, and not predicted.' },
  { n: 2, owner: 'Terminal', job: 'The sound must be captured as digital numbers.',
    what: 'The microphone captures sound as digital numbers.',
    data: 'Sample values (illustrative): 12, -40, 85, 130, 60, -25',
    why: 'The microphone is wired to the Pico, so the terminal captures the sound.' },
  { n: 3, owner: 'Network', job: 'The request must get from the desk to the other computer.',
    what: 'The request travels to the server.',
    data: 'Request fields: device = desk-07, kind = question, plus the sound numbers',
    why: 'The Wi-Fi link only carries the request. It does not read or change it.' },
  { n: 4, owner: 'Server', job: 'The recorded speech must be turned into written words.',
    what: 'The server converts speech to text.',
    data: 'Text: "when is my next test"',
    why: 'Speech-to-text needs more memory than the Pico has, so the server does it.' },
  { n: 5, owner: 'Server', job: 'Something must decide what the reply is.',
    what: 'The brain decides the reply.',
    data: 'Event found: "TEST: Biology, Friday". Reply text: "Your next test is Biology on Friday."',
    why: 'The calendar and the decision logic live on the server.' },
  { n: 6, owner: 'Server', job: 'The reply must be turned into speech and packaged.',
    what: 'The server converts the reply to speech and packages it.',
    data: 'Reply fields: speak = the sentence as audio, show = "Biology test: Friday"',
    why: 'Text-to-speech also needs more memory than the Pico has.' },
  { n: 7, owner: 'Network', job: 'The reply must get back to the desk.',
    what: 'The reply travels back to the terminal.',
    data: 'The same reply fields, moving from the server to desk-07',
    why: 'The Wi-Fi link only carries the reply.' },
  { n: 8, owner: 'Terminal', job: 'The reply must be shown and heard.',
    what: 'The terminal shows and plays the reply.',
    data: 'Display shows "Biology test: Friday". Speaker says "Your next test is Biology on Friday."',
    why: 'The display and speaker are wired to the Pico, so the terminal outputs the reply.' }
];

// the four parts drawn as columns, left to right
const parts = [
  { name: 'Student', sub: 'speaks and listens', fill: 'mistyrose' },
  { name: 'Terminal', sub: 'desk-07: Pico, microphone, display, speaker', fill: 'lightcyan' },
  { name: 'Network', sub: 'Wi-Fi link on the school network', fill: 'lemonchiffon' },
  { name: 'Server', sub: 'buddy server on a school computer', fill: 'lavender' }
];

// ---------- state ----------
let stepIndex = 1;       // index into steps of the step being predicted (1..7)
let revealed = false;    // has the current step been predicted and revealed?
let predictions = {};    // step number -> { choice, correct }
let score = 0;
let finished = false;

// ---------- controls ----------
let terminalButton, networkButton, serverButton, nextButton, restartButton;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  // Create every control first, then position them
  terminalButton = createButton('Terminal');
  terminalButton.mousePressed(() => predict('Terminal'));
  networkButton = createButton('Network');
  networkButton.mousePressed(() => predict('Network'));
  serverButton = createButton('Server');
  serverButton.mousePressed(() => predict('Server'));
  nextButton = createButton('Next');
  nextButton.mousePressed(nextStep);
  restartButton = createButton('Restart');
  restartButton.mousePressed(restart);

  positionControls();
  restart();

  describe('A step-through of the eight steps that carry the spoken question "When is my next test?" ' +
    'to the spoken answer. Before each of steps 2 to 8 the learner predicts whether the Terminal, the ' +
    'Network, or the Server performs it, then sees the owner, the data at that step, the reason, and a ' +
    'running score out of 7. Revealed steps collect under the part that performed them.', LABEL);
}

function positionControls() {
  const y = drawHeight + 10;
  let x = 10;
  for (const b of [terminalButton, networkButton, serverButton, nextButton]) {
    b.position(x, y);
    x += b.elt.offsetWidth + 10;
  }
  restartButton.position(max(x + 10, canvasWidth - restartButton.elt.offsetWidth - 10), y);
}

function restart() {
  stepIndex = 1;
  revealed = false;
  predictions = {};
  score = 0;
  finished = false;
  updateButtons();
}

function predict(choice) {
  if (revealed || finished) return;   // one attempt per step
  const s = steps[stepIndex];
  const correct = (choice === s.owner);
  if (correct) score++;
  predictions[s.n] = { choice: choice, correct: correct };
  revealed = true;
  updateButtons();
}

function nextStep() {
  if (!revealed) return;              // Next requires a prediction first
  if (stepIndex < steps.length - 1) {
    stepIndex++;
    revealed = false;
  } else {
    finished = true;
  }
  updateButtons();
}

function updateButtons() {
  const choosing = !revealed && !finished;
  for (const b of [terminalButton, networkButton, serverButton]) {
    b.elt.disabled = !choosing;
    const p = predictions[steps[stepIndex].n];
    b.elt.classList.toggle('chosen', revealed && !finished && p && p.choice === b.html());
  }
  nextButton.elt.disabled = !(revealed && !finished);
  nextButton.html(stepIndex === steps.length - 1 ? 'See summary' : 'Next');
}

// has step n been revealed yet?
function isRevealed(n) {
  if (n === 1) return true;
  return predictions[n] !== undefined;
}

function draw() {
  updateCanvasSize();

  stroke('silver');
  strokeWeight(1);
  fill('aliceblue');
  rect(0, 0, canvasWidth, drawHeight);
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  // title
  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(24);
  text('Agent Data Flow Step-Through', canvasWidth / 2, 10);

  textSize(defaultTextSize);
  textAlign(LEFT, TOP);
  fill('dimgray');
  noStroke();
  text('Question: "When is my next test?"', margin, 44);
  textAlign(RIGHT, TOP);
  fill('black');
  noStroke();
  text('Score: ' + score + ' of 7', canvasWidth - margin, 44);

  drawParts();
  if (finished) {
    drawSummary();
  } else {
    drawStepCard();
  }
}

// Four columns: Student, Terminal, Network, Server, with arrows between them.
// Revealed steps appear as numbered chips under their owner.
function drawParts() {
  const top = 72, h = 178, gap = 22;
  const colW = (canvasWidth - 2 * margin - 3 * gap) / 4;
  const currentOwner = (revealed && !finished) ? steps[stepIndex].owner : '';

  for (let i = 0; i < parts.length; i++) {
    const p = parts[i];
    const x = margin + i * (colW + gap);
    const lit = (p.name === currentOwner);
    stroke(lit ? 'royalblue' : 'silver');
    strokeWeight(lit ? 4 : 1);
    fill(p.fill);
    rect(x, top, colW, h, 10);
    strokeWeight(1);

    noStroke();
    fill('black');
    textStyle(BOLD);
    textSize(17);
    textAlign(CENTER, TOP);
    text(p.name, x + colW / 2, top + 8);
    textStyle(NORMAL);
    textSize(13);
    fill('dimgray');
    noStroke();
    const subLines = wrapLines(p.sub, colW - 12);
    for (let k = 0; k < subLines.length && k < 4; k++) {
      text(subLines[k], x + colW / 2, top + 30 + k * 16);
    }

    // chips for revealed steps owned by this part
    const owned = steps.filter(s => s.owner === p.name && isRevealed(s.n));
    const chipD = min(34, (colW - 16) / 3 - 6);
    const per = max(1, floor((colW - 8) / (chipD + 6)));
    for (let k = 0; k < owned.length; k++) {
      const s = owned[k];
      const cx = x + 8 + chipD / 2 + (k % per) * (chipD + 6);
      const cy = top + 104 + floor(k / per) * (chipD + 6) + chipD / 2;
      const pr = predictions[s.n];
      stroke(!pr ? 'gray' : (pr.correct ? 'seagreen' : 'darkorange'));
      strokeWeight(3);
      fill(!pr ? 'gainsboro' : (pr.correct ? 'palegreen' : 'peachpuff'));
      circle(cx, cy, chipD);
      strokeWeight(1);
      noStroke();
      fill('black');
      textSize(15);
      textAlign(CENTER, CENTER);
      text(s.n, cx, cy);
    }

    // request arrow (to the right, upper) and reply arrow (to the left, lower)
    if (i < parts.length - 1) {
      const ax1 = x + colW + 2, ax2 = x + colW + gap - 2, ay = top + h / 2;
      stroke('slategray');
      strokeWeight(2);
      line(ax1, ay - 8, ax2, ay - 8);
      line(ax2, ay - 8, ax2 - 6, ay - 13);
      line(ax2, ay - 8, ax2 - 6, ay - 3);
      line(ax1, ay + 8, ax2, ay + 8);
      line(ax1, ay + 8, ax1 + 6, ay + 3);
      line(ax1, ay + 8, ax1 + 6, ay + 13);
      strokeWeight(1);
    }
  }

  noStroke();
  fill('dimgray');
  textSize(13);
  textAlign(LEFT, TOP);
  text('Chips are step numbers: green = correct, orange = missed, gray = not predicted',
    margin, top + h + 4, canvasWidth - 2 * margin);
}

// The card for the current step: prediction prompt or the revealed details
function drawStepCard() {
  const s = steps[stepIndex];
  const x = margin, y = 276, w = canvasWidth - 2 * margin, h = drawHeight - y - 10;
  stroke('silver');
  fill('white');
  rect(x, y, w, h, 10);
  const tx = x + 14, tw = w - 28;
  let ty = y + 10;

  noStroke();
  textAlign(LEFT, TOP);
  textSize(14);
  fill('steelblue');
  text('STEP ' + s.n + ' OF 8' + (revealed ? '  -  performed by the ' + s.owner : '  -  make your prediction'), tx, ty);
  ty += 24;

  if (!revealed) {
    // context: the step that was just revealed
    const prev = steps[stepIndex - 1];
    textSize(15);
    fill('dimgray');
    noStroke();
    ty += drawWrapped('Previous step ' + prev.n + ' (' + prev.owner + '): ' + prev.what + ' Data: ' + prev.data, tx, ty, tw, 20);
    ty += 10;
    textSize(defaultTextSize);
    fill('black');
    noStroke();
    ty += drawWrapped('Next job: ' + s.job, tx, ty, tw, 22);
    ty += 8;
    textStyle(BOLD);
    textSize(18);
    noStroke();
    ty += drawWrapped('Which part performs step ' + s.n + '?', tx, ty, tw, 24);
    textStyle(NORMAL);
    textSize(15);
    fill('dimgray');
    noStroke();
    drawWrapped('Choose Terminal, Network, or Server below. Each step gets one prediction.', tx, ty + 4, tw, 20);
    return;
  }

  // revealed: what happens, the data, and the feedback
  textStyle(BOLD);
  textSize(18);
  fill('black');
  noStroke();
  ty += drawWrapped(s.what, tx, ty, tw, 24);
  textStyle(NORMAL);
  ty += 6;

  // data box
  textSize(15);
  const dataLines = wrapLines('Data at this step: ' + s.data, tw - 20);
  const dataH = dataLines.length * 20 + 14;
  stroke('lightsteelblue');
  fill('ghostwhite');
  rect(tx, ty, tw, dataH, 6);
  noStroke();
  fill('midnightblue');
  for (let k = 0; k < dataLines.length; k++) {
    noStroke();
    text(dataLines[k], tx + 10, ty + 7 + k * 20);
  }
  ty += dataH + 10;

  // feedback
  const pr = predictions[s.n];
  const msg = pr.correct ? 'Correct: ' + s.owner + '. ' + s.why :
    'Not quite. The ' + s.owner + ' does this step. ' + s.why;
  textSize(defaultTextSize);
  const fbLines = wrapLines(msg, tw - 20);
  const fbH = fbLines.length * 21 + 14;
  stroke(pr.correct ? 'seagreen' : 'darkorange');
  strokeWeight(2);
  fill(pr.correct ? 'honeydew' : 'seashell');
  rect(tx, ty, tw, fbH, 6);
  strokeWeight(1);
  noStroke();
  fill('black');
  for (let k = 0; k < fbLines.length; k++) {
    noStroke();
    text(fbLines[k], tx + 10, ty + 7 + k * 21);
  }
}

// Final screen: score, mastery, and the steps grouped by owner
function drawSummary() {
  const x = margin, y = 276, w = canvasWidth - 2 * margin, h = drawHeight - y - 10;
  stroke('silver');
  fill('white');
  rect(x, y, w, h, 10);
  const tx = x + 14, tw = w - 28;

  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textStyle(BOLD);
  textSize(20);
  text('You predicted ' + score + ' of 7 correctly.', tx, y + 10);
  textStyle(NORMAL);
  textSize(15);
  fill(score >= 6 ? 'seagreen' : 'darkorange');
  noStroke();
  const mastery = score >= 6 ? 'Mastery reached (6 of 7 needed).' :
    'Mastery needs 6 of 7. Reread "The Agent Data Flow" and press Restart.';
  let ty = y + 38 + drawWrapped(mastery, tx, y + 38, tw, 20) + 6;

  // grouped list; shrink the text if it does not fit
  const groups = parts.map(p => {
    const owned = steps.filter(s => s.owner === p.name);
    return p.name + ' (' + owned.map(s => s.n).join(', ') + '): ' + owned.map(s => s.what).join(' ');
  });
  let size;
  for (size = 15; size > 11; size--) {
    textSize(size);
    let lines = 0;
    for (const g of groups) lines += wrapLines(g, tw).length;
    if (lines * (size + 5) + groups.length * 3 <= y + h - ty - 8) break;
  }
  fill('black');
  textSize(size);
  for (const g of groups) {
    noStroke();
    ty += drawWrapped(g, tx, ty, tw, size + 5) + 3;
  }
}

// ---------- text helpers ----------
// Break a string into lines that fit maxW at the current text size
function wrapLines(str, maxW) {
  const words = str.split(' ');
  const lines = [];
  let line = '';
  for (const w of words) {
    const test = line ? line + ' ' + w : w;
    if (textWidth(test) > maxW && line) {
      lines.push(line);
      line = w;
    } else {
      line = test;
    }
  }
  if (line) lines.push(line);
  return lines;
}

// Draw wrapped text with top-left alignment; returns the height used
function drawWrapped(str, x, y, maxW, leading) {
  const lines = wrapLines(str, maxW);
  textAlign(LEFT, TOP);
  noStroke();
  for (let i = 0; i < lines.length; i++) {
    text(lines[i], x, y + i * leading);
  }
  return lines.length * leading;
}

// ---------- responsive design ----------
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
