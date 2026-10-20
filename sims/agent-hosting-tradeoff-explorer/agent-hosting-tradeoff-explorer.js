// Agent Hosting Trade-Off Explorer - p5.js MicroSim
// CANVAS_HEIGHT: 665
// The learner reads four illustrative scenarios. For each one the learner
// first recommends a hosting option (cloud, self-hosted, or school-hosted
// agent) and then names the deciding factor, A to D, from the chapter's four
// comparison questions. Only after both choices does the comparison table
// highlight the decisive cell and show the reason.
// Bloom level: Evaluate (recommend). Width responsive.

// ---------- canvas layout ----------
let canvasWidth = 400;          // replaced by the container width
let drawHeight = 580;           // drawing region (no controls here)
let controlHeight = 85;         // two rows of controls
let canvasHeight = drawHeight + controlHeight;
let margin = 16;
let defaultTextSize = 16;

// ---------- content (from the chapter table and the specification) ----------
const options = ['Cloud agent', 'Self-hosted agent', 'School-hosted agent'];

// factor letter, question, and each option's answer (chapter table
// "Comparing the Three Hosting Options")
const factors = [
  { letter: 'A', question: 'Who runs the computer?',
    answers: ['The vendor, in a data center', 'You or your group', 'The school'] },
  { letter: 'B', question: 'Who decides what data it can touch?',
    answers: ["The vendor's terms and settings", 'You', 'The school'] },
  { letter: 'C', question: 'What is the typical cost pattern?',
    answers: ['A recurring subscription fee', 'Hardware you already own, plus your own time',
      "Shared school hardware and staff time, used by every student's device"] },
  { letter: 'D', question: 'Who keeps it running?',
    answers: ['The vendor', 'You', 'School staff'] }
];

const scenarios = [
  { text: 'A student wants an agent today, with no setup, and the questions contain nothing private.',
    option: 'Cloud agent', factor: 'D',
    why: 'The vendor keeps it running, so the student has nothing to maintain.' },
  { text: "A coding club wants to learn how agents work by reading and changing the agent's code.",
    option: 'Self-hosted agent', factor: 'A',
    why: 'The club runs the computer, so it can open and change the software.' },
  { text: 'A school wants every classroom device to announce the school calendar, with the school deciding what is kept.',
    option: 'School-hosted agent', factor: 'B',
    why: 'One school server serves every device, and the school decides what data it touches.' },
  { text: 'A family wants an assistant whose audio never leaves their home network.',
    option: 'Self-hosted agent', factor: 'B',
    why: 'The family decides what data the agent touches, and nothing goes to a vendor.' }
];

// ---------- state ----------
let current = 0;          // scenario index
let optionChoice = '';    // learner's option for the current scenario
let factorChoice = '';    // learner's factor for the current scenario
let results = [];         // { option, factor, optionOk, factorOk } per scenario
let fullyCorrect = 0;
let finished = false;

// ---------- controls ----------
let optionButtons = [];
let factorButtons = [];
let nextButton, restartButton;
let row1End = 0;          // x where the first row of buttons ends

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  // Create every control first, then position them
  for (const o of options) {
    const b = createButton(o);
    b.mousePressed(() => chooseOption(o));
    optionButtons.push(b);
  }
  for (const f of factors) {
    const b = createButton(f.letter);
    b.mousePressed(() => chooseFactor(f.letter));
    factorButtons.push(b);
  }
  nextButton = createButton('Next scenario');
  nextButton.mousePressed(nextScenario);
  restartButton = createButton('Restart');
  restartButton.mousePressed(restart);

  positionControls();
  restart();

  describe('Four illustrative scenarios about where an agent should be hosted. For each, the learner ' +
    'recommends a cloud, self-hosted, or school-hosted agent, then picks the deciding factor A to D. ' +
    'The comparison table then highlights the decisive cell and the reason is shown, with a running ' +
    'count of fully correct scenarios out of 4.', LABEL);
}

function positionControls() {
  // Row 1: the three hosting options
  let x = 10, y = drawHeight + 8;
  for (const b of optionButtons) {
    b.position(x, y);
    x += b.elt.offsetWidth + 10;
  }
  row1End = x;
  // Row 2: factors A to D, Next, Restart
  x = 10;
  y = drawHeight + 45;
  for (const b of factorButtons) {
    b.position(x, y);
    x += b.elt.offsetWidth + 8;
  }
  x += 12;
  nextButton.position(x, y);
  x += nextButton.elt.offsetWidth + 10;
  restartButton.position(max(x + 10, canvasWidth - restartButton.elt.offsetWidth - 10), y);
}

function restart() {
  current = 0;
  optionChoice = '';
  factorChoice = '';
  results = [];
  fullyCorrect = 0;
  finished = false;
  updateButtons();
}

function chooseOption(o) {
  if (optionChoice || finished) return;     // one attempt for the option
  optionChoice = o;
  updateButtons();
}

function chooseFactor(letter) {
  if (!optionChoice || factorChoice || finished) return;  // option first, one attempt
  factorChoice = letter;
  const s = scenarios[current];
  const r = { option: optionChoice, factor: factorChoice,
    optionOk: optionChoice === s.option, factorOk: factorChoice === s.factor };
  results.push(r);
  if (r.optionOk && r.factorOk) fullyCorrect++;
  updateButtons();
}

function nextScenario() {
  if (!factorChoice) return;
  if (current < scenarios.length - 1) {
    current++;
    optionChoice = '';
    factorChoice = '';
  } else {
    finished = true;
  }
  updateButtons();
}

function updateButtons() {
  for (let i = 0; i < optionButtons.length; i++) {
    optionButtons[i].elt.disabled = !!optionChoice || finished;
    optionButtons[i].elt.classList.toggle('chosen', !finished && optionChoice === options[i]);
  }
  for (let i = 0; i < factorButtons.length; i++) {
    factorButtons[i].elt.disabled = !optionChoice || !!factorChoice || finished;
    factorButtons[i].elt.classList.toggle('chosen', !finished && factorChoice === factors[i].letter);
  }
  nextButton.elt.disabled = !factorChoice || finished;
  nextButton.html(current === scenarios.length - 1 ? 'See results' : 'Next scenario');
}

function factorByLetter(letter) {
  return factors.find(f => f.letter === letter);
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
  text('Agent Hosting Trade-Off Explorer', canvasWidth / 2, 10);

  textSize(15);
  textAlign(LEFT, TOP);
  fill('dimgray');
  noStroke();
  text(finished ? 'All four scenarios done' : 'Scenario ' + (current + 1) + ' of 4 (illustrative)', margin, 44);
  textAlign(RIGHT, TOP);
  fill('black');
  noStroke();
  text('Scenarios fully correct: ' + fullyCorrect + ' of 4', canvasWidth - margin, 44);

  const cardBottom = finished ? drawSummaryCard() : drawScenarioCard();
  drawTable(cardBottom + 10, drawHeight - 10);

  // control row labels are the buttons themselves; add a small cue
  if (canvasWidth - row1End > 170) {
    noStroke();
    fill('dimgray');
    textSize(14);
    textAlign(RIGHT, CENTER);
    text('Row 1: option. Row 2: factor.', canvasWidth - 12, drawHeight + 22);
  }
}

// Scenario text plus the prompt or the feedback; returns the card's bottom y
function drawScenarioCard() {
  const s = scenarios[current];
  const x = margin, y = 68, w = canvasWidth - 2 * margin, tx = x + 12, tw = w - 24;

  // measure contents
  textSize(17);
  const sLines = wrapLines(s.text, tw);
  let body = [];   // [text, size, style, color]
  if (!optionChoice) {
    body.push(['Which option would you recommend?', 17, BOLD, 'black']);
    body.push(['Choose one of the three options in the first row of buttons.', 15, NORMAL, 'dimgray']);
  } else if (!factorChoice) {
    body.push(['You chose: ' + optionChoice + '. What is the deciding factor?', 17, BOLD, 'black']);
    body.push(['Choose A, B, C, or D in the second row. The letters match the table rows.', 15, NORMAL, 'dimgray']);
  } else {
    const r = results[current];
    const f = factorByLetter(s.factor);
    let msg;
    if (!r.optionOk) msg = 'Not quite: ' + s.why;
    else if (!r.factorOk) msg = 'Right option. The deciding factor is ' + f.letter + ', "' + f.question + '": ' + s.why;
    else msg = 'Correct: ' + s.why;
    body.push(['Recommended: ' + s.option + '. Deciding factor: ' + f.letter + ', "' + f.question + '"', 16, BOLD, 'black']);
    body.push([msg, 16, NORMAL, 'black']);
  }
  let h = 10 + sLines.length * 22 + 8;
  const bodyLines = body.map(b => { textSize(b[1]); textStyle(b[2]); const l = wrapLines(b[0], tw); textStyle(NORMAL); return l; });
  for (let i = 0; i < body.length; i++) h += bodyLines[i].length * (body[i][1] + 5) + 4;
  h += 8;

  // card background, tinted with the feedback color once answered
  let border = 'silver', bg = 'white';
  if (factorChoice) {
    const r = results[current];
    const ok = r.optionOk && r.factorOk;
    border = ok ? 'seagreen' : 'darkorange';
    bg = ok ? 'honeydew' : 'seashell';
  }
  stroke(border);
  strokeWeight(factorChoice ? 2 : 1);
  fill(bg);
  rect(x, y, w, h, 10);
  strokeWeight(1);

  let ty = y + 10;
  noStroke();
  fill('black');
  textSize(17);
  textAlign(LEFT, TOP);
  for (const l of sLines) { noStroke(); text(l, tx, ty); ty += 22; }
  ty += 8;
  for (let i = 0; i < body.length; i++) {
    textSize(body[i][1]);
    textStyle(body[i][2]);
    fill(body[i][3]);
    for (const l of bodyLines[i]) { noStroke(); text(l, tx, ty); ty += body[i][1] + 5; }
    textStyle(NORMAL);
    ty += 4;
  }
  return y + h;
}

// Final card: score, mastery, and each scenario's answer
function drawSummaryCard() {
  const x = margin, y = 68, w = canvasWidth - 2 * margin, tx = x + 12, tw = w - 24;
  const mastery = fullyCorrect >= 3 ? 'Mastery reached (3 of 4 needed).' :
    'Mastery needs 3 of 4. Reread "Comparing the Three Hosting Options" and press Restart.';
  const rows = scenarios.map((s, i) => {
    const r = results[i];
    const ok = r.optionOk && r.factorOk;
    return (i + 1) + '. ' + s.option + ', factor ' + s.factor + (ok ? '  (you: correct)' :
      '  (you: ' + r.option + ', factor ' + r.factor + ')');
  });
  textSize(15);
  const mLines = wrapLines(mastery, tw);
  const rLines = rows.map(r => wrapLines(r, tw));
  let h = 10 + 26 + mLines.length * 20 + 6 + 20;
  for (const l of rLines) h += l.length * 20;
  h += 10;

  stroke('silver');
  fill('white');
  rect(x, y, w, h, 10);
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textStyle(BOLD);
  textSize(20);
  text(fullyCorrect + ' of 4 scenarios fully correct.', tx, y + 10);
  textStyle(NORMAL);
  textSize(15);
  let ty = y + 36;
  fill(fullyCorrect >= 3 ? 'seagreen' : 'darkorange');
  for (const l of mLines) { noStroke(); text(l, tx, ty); ty += 20; }
  ty += 6;
  fill('black');
  textStyle(BOLD);
  noStroke();
  text('Decisive cells (numbered in the table):', tx, ty);
  textStyle(NORMAL);
  ty += 20;
  for (let i = 0; i < rLines.length; i++) {
    const ok = results[i].optionOk && results[i].factorOk;
    fill(ok ? 'darkgreen' : 'saddlebrown');
    for (const l of rLines[i]) { noStroke(); text(l, tx, ty); ty += 20; }
  }
  return y + h;
}

// The comparison table. Highlights appear only after both choices.
function drawTable(top, bottom) {
  const x = margin, w = canvasWidth - 2 * margin;
  const firstW = w * 0.27;
  const colW = (w - firstW) / 3;
  const pad = 6;

  // which cells to highlight
  let hiOption = -1, hiFactor = -1;
  if (!finished && factorChoice) {
    hiOption = options.indexOf(scenarios[current].option);
    hiFactor = factors.findIndex(f => f.letter === scenarios[current].factor);
  }

  // choose the largest font that fits the available height
  let size, rowH;
  for (size = 15; size >= 10; size--) {
    textSize(size);
    rowH = factors.map(f => {
      let lines = wrapLines(f.letter + '. ' + f.question, firstW - 2 * pad).length;
      for (const a of f.answers) lines = max(lines, wrapLines(a, colW - 2 * pad).length);
      return lines * (size + 4) + 2 * pad;
    });
    const total = (size + 4) * 2 + 2 * pad + rowH.reduce((a, b) => a + b, 0);
    if (total <= bottom - top) break;
  }
  textStyle(BOLD);
  const headLines = max(options.map(o => wrapLines(o, colW - 2 * pad).length));
  textStyle(NORMAL);
  const headH = (size + 4) * headLines + 2 * pad;

  // header row
  stroke('silver');
  fill('lightsteelblue');
  rect(x, top, w, headH);
  noStroke();
  fill('black');
  textStyle(BOLD);
  textSize(size);
  drawWrapped('Factor', x + pad, top + pad, firstW - 2 * pad, size + 4);
  for (let c = 0; c < 3; c++) {
    const cx = x + firstW + c * colW;
    if (c === hiOption) {
      stroke('goldenrod');
      strokeWeight(3);
      noFill();
      rect(cx + 1, top + 1, colW - 2, headH - 2);
      strokeWeight(1);
    }
    noStroke();
    fill('black');
    drawWrapped(options[c], cx + pad, top + pad, colW - 2 * pad, size + 4);
  }
  textStyle(NORMAL);

  // factor rows
  let ry = top + headH;
  for (let r = 0; r < factors.length; r++) {
    const f = factors[r];
    stroke('silver');
    fill(r === hiFactor ? 'lightyellow' : (r % 2 ? 'whitesmoke' : 'white'));
    rect(x, ry, w, rowH[r]);
    noStroke();
    fill('black');
    textStyle(BOLD);
    textSize(size);
    drawWrapped(f.letter + '. ' + f.question, x + pad, ry + pad, firstW - 2 * pad, size + 4);
    textStyle(NORMAL);
    for (let c = 0; c < 3; c++) {
      const cx = x + firstW + c * colW;
      stroke('silver');
      line(cx, ry, cx, ry + rowH[r]);
      if (r === hiFactor && c === hiOption) {
        stroke('goldenrod');
        strokeWeight(3);
        fill('gold');
        rect(cx + 2, ry + 2, colW - 4, rowH[r] - 4, 4);
        strokeWeight(1);
      }
      noStroke();
      fill('black');
      textSize(size);
      drawWrapped(f.answers[c], cx + pad, ry + pad, colW - 2 * pad, size + 4);
    }
    // summary badges: scenario numbers in their decisive cells
    if (finished) {
      for (let i = 0; i < scenarios.length; i++) {
        const s = scenarios[i];
        if (s.factor !== f.letter) continue;
        const c = options.indexOf(s.option);
        const ok = results[i].optionOk && results[i].factorOk;
        const bx = x + firstW + (c + 1) * colW - 16, by = ry + rowH[r] - 15;
        stroke(ok ? 'seagreen' : 'darkorange');
        strokeWeight(3);
        fill(ok ? 'palegreen' : 'peachpuff');
        circle(bx, by, 24);
        strokeWeight(1);
        noStroke();
        fill('black');
        textSize(14);
        textAlign(CENTER, CENTER);
        text(i + 1, bx, by);
        textAlign(LEFT, TOP);
      }
    }
    ry += rowH[r];
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
