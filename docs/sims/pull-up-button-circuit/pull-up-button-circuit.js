// Pull-Up Button Circuit MicroSim
// CANVAS_HEIGHT: 560
// A Pico input pin with an optional internal pull (pull-up, pull-down or none)
// and a push button whose other leg goes to GND or 3V3. The learner explores a
// sample circuit, then predicts what the pin reads for 6 illustrative circuits,
// then answers an unscored reality check about the RP2350 pull-down quirk.
// Rule: a pressed button connects the pin to its other leg (GND or 3V3), and
// that connection beats the weak internal pull. A released button leaves the
// pin at the pull's level; with no pull the pin floats (unpredictable).

// ---- Canvas layout ----
let canvasWidth = 400;
let drawHeight = 480;
let controlHeight = 80;   // 2 control rows x 35 + 10
let canvasHeight = drawHeight + controlHeight;
let margin = 25;
let defaultTextSize = 16;

// ---- Controls ----
let pressButton, choice1Button, choice0Button, choiceUButton;
let choiceAButton, choiceBButton, modeButton, nextButton;

// ---- Circuits (spec order, illustrative) ----
const circuits = [
  { pull: 'up',   leg: 'GND', pressed: false, answer: '1',
    why: 'Nothing pulls the pin down, so the pull-up holds it at 1.' },
  { pull: 'up',   leg: 'GND', pressed: true,  answer: '0',
    why: 'The button connects the pin to GND, which beats the weak pull-up.' },
  { pull: 'none', leg: 'GND', pressed: false, answer: 'unpredictable',
    why: 'With no pull and no connection, the pin picks up stray signals.' },
  { pull: 'up',   leg: '3V3', pressed: true,  answer: '1',
    why: 'Both the pull-up and the button push the pin toward 3.3 V.' },
  { pull: 'down', leg: '3V3', pressed: true,  answer: '1',
    why: 'The button connects the pin to 3V3, which beats the weak pull-down.' },
  { pull: 'down', leg: '3V3', pressed: false, wasLow: true, answer: '0',
    why: 'Nothing pulls the pin up, so the pull-down holds it at 0, as long as the pin was low before.' }
];

const sentenceA = 'Pull-ups and pull-downs behaved the same on the test board.';
const sentenceB = 'Pull-ups worked every time on the test board, and the pull-down did not.';

// ---- State ----
// 'explore' | 'challenge' | 'done' | 'reality'
let mode = 'explore';
let sample = { pull: 'up', leg: 'GND', pressed: false };
let challengeIndex = 0;
let score = 0;
let answered = false;
let feedback = '';
let feedbackKind = 'info';
let realityChoice = '';   // '' | 'A' | 'B'

// ---- The model: what the pin reads ----
// Returns '1', '0' or 'unpredictable'
function pinReads(c) {
  if (c.pressed) return c.leg === 'GND' ? '0' : '1';   // a connected path wins over a pull
  if (c.pull === 'up') return '1';
  if (c.pull === 'down') return c.wasLow ? '0' : '1';  // RP2350 quirk: only reliable if the pin was low
  return 'unpredictable';                               // floating
}

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  for (const c of circuits) {
    if (pinReads(c) !== c.answer) console.warn('Circuit table mismatch', c);
  }

  // Create ALL controls first
  pressButton = createButton('Press Button');
  pressButton.mousePressed(togglePress);
  choice1Button = createButton('reads 1');
  choice1Button.mousePressed(() => pick('1'));
  choice0Button = createButton('reads 0');
  choice0Button.mousePressed(() => pick('0'));
  choiceUButton = createButton('unpredictable');
  choiceUButton.mousePressed(() => pick('unpredictable'));
  choiceAButton = createButton('Choose A');
  choiceAButton.mousePressed(() => pickReality('A'));
  choiceBButton = createButton('Choose B');
  choiceBButton.mousePressed(() => pickReality('B'));
  modeButton = createButton('Start Challenges');
  modeButton.mousePressed(toggleMode);
  nextButton = createButton('Next');
  nextButton.mousePressed(nextStep);

  // Then position them
  positionControls();
  showModeControls();

  describe('Schematic of a Pico input pin with an internal pull resistor and a push button. ' +
    'The other leg of the button goes to GND or 3V3. A box shows what the pin reads: 1, 0, ' +
    'or unpredictable. The learner presses the button in a sample circuit, then predicts the ' +
    'reading for six circuits.', LABEL);
}

function positionControls() {
  const y0 = drawHeight + 5;
  pressButton.position(10, y0);
  choice1Button.position(10, y0);
  choice0Button.position(85, y0);
  choiceUButton.position(160, y0);
  choiceAButton.position(10, y0);
  choiceBButton.position(100, y0);
  modeButton.position(10, y0 + 35);
  nextButton.position(170, y0 + 35);
}

function showModeControls() {
  const all = [pressButton, choice1Button, choice0Button, choiceUButton,
    choiceAButton, choiceBButton, nextButton];
  for (const b of all) b.hide();
  if (mode === 'explore') {
    pressButton.show();
    pressButton.html(sample.pressed ? 'Release Button' : 'Press Button');
    modeButton.html('Start Challenges');
  } else if (mode === 'challenge') {
    for (const b of [choice1Button, choice0Button, choiceUButton]) {
      b.show();
      if (answered) b.attribute('disabled', '');
      else b.removeAttribute('disabled');
    }
    modeButton.html('Back to Sample');
    if (answered) {
      nextButton.html(challengeIndex === circuits.length - 1 ? 'See Score' : 'Next');
      nextButton.show();
    }
  } else if (mode === 'done') {
    modeButton.html('Back to Sample');
    nextButton.html('Reality Check');
    nextButton.show();
  } else if (mode === 'reality') {
    for (const b of [choiceAButton, choiceBButton]) {
      b.show();
      if (realityChoice) b.attribute('disabled', '');
      else b.removeAttribute('disabled');
    }
    modeButton.html('Back to Sample');
  }
}

function togglePress() {
  sample.pressed = !sample.pressed;
  showModeControls();
}

function toggleMode() {
  if (mode === 'explore') {
    mode = 'challenge';
    challengeIndex = 0;
    score = 0;
    answered = false;
    feedback = '';
  } else {
    mode = 'explore';
    sample.pressed = false;
    feedback = '';
    realityChoice = '';
  }
  showModeControls();
}

function pick(choice) {
  if (mode !== 'challenge' || answered) return;
  const c = circuits[challengeIndex];
  answered = true;
  if (choice === c.answer) {
    score++;
    feedback = 'Correct: ' + c.why;
    feedbackKind = 'good';
  } else {
    feedback = 'Not quite. The pin reads ' + c.answer + ': ' + c.why;
    feedbackKind = 'bad';
  }
  showModeControls();
}

function nextStep() {
  if (mode === 'challenge' && answered) {
    challengeIndex++;
    answered = false;
    feedback = '';
    if (challengeIndex >= circuits.length) {
      challengeIndex = circuits.length - 1;
      answered = true;
      mode = 'done';
      const mastery = score >= 5 ? 'Mastery reached (5 of 6 needed).' : 'Mastery needs 5 of 6. Try the sample circuit and the challenges again.';
      feedback = 'You scored ' + score + ' of 6. ' + mastery + ' Look back at circuit 4: with the ' +
        'other leg on 3V3 and a pull-up, the pin reads 1 whether or not you press, so the button seems dead.';
      feedbackKind = score >= 5 ? 'good' : 'info';
    }
  } else if (mode === 'done') {
    mode = 'reality';
    realityChoice = '';
    feedback = '';
  }
  showModeControls();
}

function pickReality(ch) {
  if (mode !== 'reality' || realityChoice) return;
  realityChoice = ch;
  if (ch === 'B') {
    feedback = 'Correct: ' + sentenceB;
    feedbackKind = 'good';
  } else {
    feedback = 'Not quite. The better explanation is: ' + sentenceB + ' Here are the readings.';
    feedbackKind = 'bad';
  }
  showModeControls();
}

// ---------------- Drawing ----------------

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
  text('Pull-Up Button Circuit', canvasWidth / 2, 8);

  // Status line + running score
  textSize(defaultTextSize);
  textAlign(LEFT, TOP);
  textStyle(BOLD);
  let status = 'Sample circuit';
  if (mode === 'challenge') status = 'Circuit ' + (challengeIndex + 1) + ' of 6 (illustrative)';
  if (mode === 'done') status = 'Challenges finished';
  if (mode === 'reality') status = 'Reality check (not scored)';
  noStroke();
  text(status, margin, 40);
  textStyle(NORMAL);
  if (mode !== 'explore') {
    textAlign(RIGHT, TOP);
    noStroke();
    text('Score: ' + score + ' of 6', canvasWidth - margin, 40);
  }

  if (mode === 'reality') {
    drawReality();
    return;
  }

  // Circuit to draw and whether its reading is visible
  let c, reveal;
  if (mode === 'explore') { c = sample; reveal = true; }
  else { c = circuits[challengeIndex]; reveal = answered; }

  const sw = 460, sh = 230;
  const s = min(1, (canvasWidth - 2 * margin) / sw);
  const ox = (canvasWidth - sw * s) / 2;
  const oy = 66;
  push();
  translate(ox, oy);
  scale(s);
  drawSchematic(c, reveal);
  pop();

  // Text under the schematic
  let y = oy + sh * s + 12;
  const tw = canvasWidth - 2 * margin;
  noStroke();
  fill('black');
  textSize(defaultTextSize);
  textAlign(LEFT, TOP);
  const pullName = { up: 'pull-up', down: 'pull-down', none: 'no pull (floating)' }[c.pull];
  let desc = 'Pin pull: ' + pullName + (c.wasLow ? ' (pin was low before)' : '') +
    '.  Other leg: ' + c.leg + '.  Button: ' + (c.pressed ? 'pressed' : 'released') + '.';
  y = wrapText(desc, margin, y, tw, 20);
  y += 4;
  if (mode === 'explore') {
    textStyle(BOLD);
    y = wrapText('What will the pin read when the button is pressed?', margin, y, tw, 20);
    textStyle(NORMAL);
    fill('dimgray');
    y += 4;
    const note = c.pressed
      ? 'Pressed: the button connects the pin to GND, which beats the weak pull-up, so the pin reads 0.'
      : 'Released: nothing pulls the pin down, so the pull-up holds it at 1. Press the button to test your prediction.';
    y = wrapText(note, margin, y, tw, 20);
  } else if (mode === 'challenge' && !answered) {
    textStyle(BOLD);
    y = wrapText('What does the pin read? Pick an answer below.', margin, y, tw, 20);
    textStyle(NORMAL);
  }
  if (feedback) drawFeedbackBox(y + 8);
}

// Word-wrap text inside width w; returns the y after the last line
function wrapText(str, x, y, w, lh) {
  const words = str.split(' ');
  let line = '';
  for (const word of words) {
    const test = line ? line + ' ' + word : word;
    if (textWidth(test) > w && line) {
      text(line, x, y);
      y += lh;
      line = word;
    } else {
      line = test;
    }
  }
  if (line) { text(line, x, y); y += lh; }
  return y;
}

function drawFeedbackBox(y) {
  const x = margin;
  const w = canvasWidth - 2 * margin;
  textSize(15);
  // measure the height first
  const lines = countLines(feedback, w - 12);
  const h = lines * 19 + 12;
  stroke(feedbackKind === 'good' ? 'seagreen' : (feedbackKind === 'bad' ? 'darkorange' : 'silver'));
  strokeWeight(1);
  fill(feedbackKind === 'good' ? 'honeydew' : (feedbackKind === 'bad' ? 'seashell' : 'white'));
  rect(x - 6, y, w + 12, h, 8);
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  wrapText(feedback, x, y + 6, w - 12, 19);
  return y + h;
}

function countLines(str, w) {
  const words = str.split(' ');
  let line = '', n = 0;
  for (const word of words) {
    const test = line ? line + ' ' + word : word;
    if (textWidth(test) > w && line) { n++; line = word; }
    else line = test;
  }
  return n + (line ? 1 : 0);
}

// Schematic in a 460 x 230 local space
function drawSchematic(c, reveal) {
  const hot = 'darkorange';
  const reading = pinReads(c);
  // Which path wins, shown only after the reading is revealed
  const pathButton = reveal && c.pressed;
  const pathPull = reveal && !c.pressed && c.pull !== 'none';

  // Pico boundary (dashed)
  stroke('steelblue');
  strokeWeight(2);
  noFill();
  drawingContext.setLineDash([8, 6]);
  rect(0, 10, 230, 210, 10);
  drawingContext.setLineDash([]);
  noStroke();
  fill('steelblue');
  textAlign(LEFT, TOP);
  textSize(16);
  textStyle(BOLD);
  text('Pico', 10, 18);
  textStyle(NORMAL);
  textSize(13);
  text('inside the chip', 10, 38);

  // Wire from junction J(160,120) to the pin pad P(230,120)
  wire(160, 120, 230, 120, pathButton || pathPull);
  // Wire from junction to the input reader
  wire(110, 120, 160, 120, reveal && reading !== 'unpredictable');
  // Junction dot
  noStroke();
  fill('black');
  circle(160, 120, 7);

  // Pin pad on the boundary
  stroke('black');
  strokeWeight(1);
  fill('gold');
  rect(224, 113, 12, 14);
  noStroke();
  fill('black');
  // Label sits just outside the dashed Pico boundary so the boundary line does not cross it
  textAlign(LEFT, TOP);
  textSize(14);
  text('GP pin', 240, 126);

  // Internal pull resistor
  if (c.pull === 'up') {
    wire(160, 120, 160, 100, pathPull);
    resistor(160, 100, 64, pathPull);
    wire(160, 64, 160, 48, pathPull);
    railUp(160, 48, pathPull);
    labelLeft('pull-up', 172, 82);
  } else if (c.pull === 'down') {
    wire(160, 120, 160, 140, pathPull);
    resistor(160, 140, 176, pathPull);
    wire(160, 176, 160, 188, pathPull);
    ground(160, 188, pathPull);
    labelLeft('pull-down', 172, 158);
  } else {
    noStroke();
    fill('gray');
    textAlign(CENTER, CENTER);
    textSize(14);
    text('no pull', 160, 80);
  }

  // Input reader: a buffer triangle and the reading box
  stroke('black');
  strokeWeight(2);
  fill('white');
  triangle(110, 104, 110, 136, 80, 120);
  wire(66, 120, 80, 120, false);
  // Reading box
  let shown = '?';
  if (reveal) {
    if (reading === 'unpredictable') shown = (floor(frameCount / 25) % 2) ? '1' : '0';
    else shown = reading;
  }
  stroke('black');
  strokeWeight(2);
  if (!reveal) fill('white');
  else if (reading === 'unpredictable') fill('plum');
  else fill(shown === '1' ? 'khaki' : 'lightsteelblue');
  rect(14, 96, 52, 48, 6);
  noStroke();
  fill('black');
  textAlign(CENTER, CENTER);
  textSize(30);
  textStyle(BOLD);
  text(shown, 40, 121);
  textStyle(NORMAL);
  textSize(14);
  textAlign(CENTER, BOTTOM);
  text('reads', 40, 93);
  if (reveal && reading === 'unpredictable') {
    textAlign(CENTER, TOP);
    textSize(12);
    fill('purple');
    text('floating', 40, 148);
  }

  // Button outside the Pico: contacts at (280,120) and (340,120)
  wire(236, 120, 280, 120, pathButton);
  stroke(pathButton ? hot : 'black');
  strokeWeight(pathButton ? 4 : 2);
  if (c.pressed) {
    line(280, 120, 340, 120);     // contacts joined
    line(310, 120, 310, 100);     // plunger
    line(300, 100, 320, 100);
  } else {
    line(280, 120, 334, 88);
    line(310, 102, 310, 82);
    line(300, 82, 320, 82);
  }
  noStroke();
  fill('black');
  textAlign(CENTER, BOTTOM);
  textSize(14);
  text('button: ' + (c.pressed ? 'pressed' : 'released'), 310, 74);

  // Other leg to GND or 3V3
  wire(340, 120, 400, 120, pathButton);
  if (c.leg === 'GND') {
    wire(400, 120, 400, 160, pathButton);
    ground(400, 160, pathButton);
  } else {
    wire(400, 120, 400, 72, pathButton);
    railUp(400, 72, pathButton);
  }
  // Button contacts drawn last so wires do not cover them
  noStroke();
  fill('black');
  circle(280, 120, 9);
  circle(340, 120, 9);
}

function wire(x1, y1, x2, y2, isHot) {
  stroke(isHot ? 'darkorange' : 'black');
  strokeWeight(isHot ? 4 : 2);
  line(x1, y1, x2, y2);
}

// Vertical zigzag resistor from y1 to y2 at x
function resistor(x, y1, y2, isHot) {
  stroke(isHot ? 'darkorange' : 'black');
  strokeWeight(isHot ? 3 : 2);
  noFill();
  const n = 6;
  const step = (y2 - y1) / n;
  beginShape();
  vertex(x, y1);
  for (let i = 0; i < n; i++) {
    vertex(x + (i % 2 === 0 ? 8 : -8), y1 + step * (i + 0.5));
  }
  vertex(x, y2);
  endShape();
}

function ground(x, y, isHot) {
  stroke(isHot ? 'darkorange' : 'black');
  strokeWeight(isHot ? 3 : 2);
  line(x - 16, y, x + 16, y);
  line(x - 10, y + 6, x + 10, y + 6);
  line(x - 4, y + 12, x + 4, y + 12);
  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(14);
  text('GND', x, y + 16);
}

function railUp(x, y, isHot) {
  stroke(isHot ? 'darkorange' : 'black');
  strokeWeight(isHot ? 3 : 2);
  line(x - 16, y, x + 16, y);
  noStroke();
  fill('crimson');
  textAlign(CENTER, BOTTOM);
  textSize(14);
  text('3V3', x, y - 3);
}

function labelLeft(str, x, y) {
  noStroke();
  fill('dimgray');
  textAlign(LEFT, CENTER);
  textSize(13);
  text(str, x, y);
}

function drawReality() {
  const x = margin;
  const w = canvasWidth - 2 * margin;
  let y = 68;
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(defaultTextSize);
  y = wrapText('On the test board, a pin set to pull-down after it had been driven high still read 1 ' +
    '(GP16 and GP17), while a pull-up read 1 every time.', x, y, w, 20);
  y += 6;
  textStyle(BOLD);
  y = wrapText('Which sentence explains why the kit uses pull-ups?', x, y, w, 20);
  textStyle(NORMAL);
  y += 6;
  fill(realityChoice === 'A' ? 'darkorange' : 'black');
  y = wrapText('A: ' + sentenceA, x, y, w, 20);
  y += 4;
  fill(realityChoice ? 'seagreen' : 'black');
  y = wrapText('B: ' + sentenceB, x, y, w, 20);
  if (!realityChoice) return;
  y = drawFeedbackBox(y + 8);
  drawReadingsTable(x, y + 10, w);
}

function drawReadingsTable(x, y, w) {
  const rows = [
    ['Test on GP16', 'Readings (40 each)'],
    ['Pull-up', '40 ones'],
    ['Pull-down, pin driven low first', '40 zeros'],
    ['Pull-down, pin driven high first', '40 ones (did not pull low)']
  ];
  const c1 = w * 0.56;
  textSize(14);
  textAlign(LEFT, TOP);
  for (let i = 0; i < rows.length; i++) {
    const n = max(countLines(rows[i][0], c1 - 10), countLines(rows[i][1], w - c1 - 10));
    const h = n * 17 + 8;
    stroke('silver');
    strokeWeight(1);
    fill(i === 0 ? 'gainsboro' : 'white');
    rect(x, y, c1, h);
    rect(x + c1, y, w - c1, h);
    noStroke();
    fill('black');
    if (i === 0) textStyle(BOLD);
    wrapText(rows[i][0], x + 5, y + 4, c1 - 10, 17);
    wrapText(rows[i][1], x + c1 + 5, y + 4, w - c1 - 10, 17);
    textStyle(NORMAL);
    y += h;
  }
}

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
