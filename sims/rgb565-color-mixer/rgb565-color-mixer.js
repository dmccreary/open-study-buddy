// RGB565 Color Mixer MicroSim
// CANVAS_HEIGHT: 590
// The learner mixes red, green and blue strengths (0-255) and watches which
// bits each color keeps when the kit's color565() packs them into 16 bits.
// A challenge mode asks for the RGB565 hex value of 6 colors (two tries each).
// Packing rule (from src/kits/study-buddy-base/lib/gc9b72.py):
//   value = (R & 0xF8) << 8 | (G & 0xFC) << 3 | B >> 3

// ---- Canvas layout ----
let canvasWidth = 400;
let drawHeight = 440;
let controlHeight = 150;   // 4 control rows x 35 + 10
let canvasHeight = drawHeight + controlHeight;
let margin = 25;
let sliderLeftMargin = 120;
let defaultTextSize = 16;

// ---- Controls ----
let redSlider, greenSlider, blueSlider;
let modeButton, answerInput, checkButton, nextButton;

// ---- Challenge data (spec order) ----
const challenges = [
  { name: 'Red',    rgb: [255, 0, 0],       answer: 'F800', why: 'Red keeps its top 5 bits (11111) in the top of the number.' },
  { name: 'Green',  rgb: [0, 255, 0],       answer: '07E0', why: 'Green keeps its top 6 bits (111111) in the middle.' },
  { name: 'Blue',   rgb: [0, 0, 255],       answer: '001F', why: 'Blue keeps its top 5 bits (11111) in the bottom.' },
  { name: 'Yellow', rgb: [255, 255, 0],     answer: 'FFE0', why: 'Red 11111 and green 111111 together make FFE0.' },
  { name: 'Orange', rgb: [255, 128, 0],     answer: 'FC00', why: 'Green 128 keeps 100000, so the green bits are 0x0400 and red is 0xF800.' },
  { name: 'Gray',   rgb: [110, 110, 110],   answer: '6B6D', why: 'Red 01101, green 011011, and blue 01101 pack to 0110101101101101.' }
];

// ---- State ----
let mode = 'explore';   // 'explore' | 'challenge' | 'done'
let challengeIndex = 0;
let attempts = 0;
let score = 0;
let answered = false;
let feedback = '';
let feedbackKind = 'info'; // 'info' | 'good' | 'bad'

// The kit's packing function, computed for real (not looked up)
function color565(r, g, b) {
  return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3);
}

function toHex4(v) {
  return v.toString(16).toUpperCase().padStart(4, '0');
}

function toBin(v, n) {
  return v.toString(2).padStart(n, '0');
}

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  // Sanity check: the table answers must equal the computed packing
  for (const c of challenges) {
    const v = toHex4(color565(c.rgb[0], c.rgb[1], c.rgb[2]));
    if (v !== c.answer) console.warn('RGB565 table mismatch for ' + c.name + ': ' + v);
  }

  // Create ALL controls first
  redSlider = createSlider(0, 255, 255, 1);
  greenSlider = createSlider(0, 255, 128, 1);
  blueSlider = createSlider(0, 255, 0, 1);

  modeButton = createButton('Start Challenges');
  modeButton.mousePressed(toggleMode);

  answerInput = createInput('', 'text');
  answerInput.attribute('placeholder', 'hex, e.g. 1F2E');
  answerInput.attribute('aria-label', 'RGB565 value in hexadecimal');
  answerInput.size(95);
  answerInput.elt.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') checkAnswer();
  });

  checkButton = createButton('Check');
  checkButton.mousePressed(checkAnswer);

  nextButton = createButton('Next');
  nextButton.mousePressed(nextChallenge);

  // Then position them
  positionControls();
  showModeControls();

  describe('RGB565 color mixer. Three sliders set red, green and blue from 0 to 255. ' +
    'The sim shows the color, which top bits of each color are kept (5 red, 6 green, 5 blue), ' +
    'and the packed 16-bit value in binary and hexadecimal. A challenge mode asks for the ' +
    'hexadecimal RGB565 value of six colors.', LABEL);
}

function positionControls() {
  const y0 = drawHeight + 5;
  redSlider.position(sliderLeftMargin, y0);
  greenSlider.position(sliderLeftMargin, y0 + 35);
  blueSlider.position(sliderLeftMargin, y0 + 70);
  const w = canvasWidth - sliderLeftMargin - margin;
  redSlider.size(w);
  greenSlider.size(w);
  blueSlider.size(w);

  modeButton.position(10, y0 + 105);
  answerInput.position(165, y0 + 105);
  checkButton.position(272, y0 + 105);
  nextButton.position(335, y0 + 105);
}

function showModeControls() {
  const inChallenge = (mode === 'challenge');
  for (const s of [redSlider, greenSlider, blueSlider]) {
    if (inChallenge) s.attribute('disabled', '');
    else s.removeAttribute('disabled');
  }
  if (inChallenge) {
    modeButton.html('Back to Explore');
    answerInput.show();
    checkButton.show();
    if (answered) {
      nextButton.show();
      answerInput.attribute('disabled', '');
      checkButton.attribute('disabled', '');
    } else {
      nextButton.hide();
      answerInput.removeAttribute('disabled');
      checkButton.removeAttribute('disabled');
    }
  } else {
    modeButton.html(mode === 'done' ? 'Try Challenges Again' : 'Start Challenges');
    answerInput.hide();
    checkButton.hide();
    nextButton.hide();
  }
}

function toggleMode() {
  if (mode === 'challenge') {
    mode = 'explore';
    feedback = '';
    showModeControls();
  } else {
    startChallenges();
  }
}

function startChallenges() {
  mode = 'challenge';
  challengeIndex = 0;
  score = 0;
  loadChallenge();
}

function loadChallenge() {
  const c = challenges[challengeIndex];
  redSlider.value(c.rgb[0]);
  greenSlider.value(c.rgb[1]);
  blueSlider.value(c.rgb[2]);
  attempts = 0;
  answered = false;
  feedback = '';
  feedbackKind = 'info';
  answerInput.value('');
  showModeControls();
}

function checkAnswer() {
  if (mode !== 'challenge' || answered) return;
  const c = challenges[challengeIndex];
  const raw = answerInput.value().trim().replace(/\s+/g, '').replace(/^0x/i, '');
  if (raw === '') {
    feedback = 'Type the value in hexadecimal first, for example 1F2E.';
    feedbackKind = 'info';
    return;
  }
  if (!/^[0-9a-fA-F]{1,4}$/.test(raw)) {
    // Not a valid 4-digit hex number: do not use up an attempt
    feedback = 'That is not a 16-bit hexadecimal number. Use up to four digits 0-9 and A-F.';
    feedbackKind = 'info';
    return;
  }
  attempts++;
  const correct = parseInt(raw, 16) === parseInt(c.answer, 16);
  if (correct) {
    score++;
    answered = true;
    feedback = 'Correct: ' + c.why;
    feedbackKind = 'good';
  } else if (attempts === 1) {
    feedback = 'Not quite. Check which bits each color keeps (5, 6, 5). Try again.';
    feedbackKind = 'bad';
    answerInput.value('');
  } else {
    answered = true;
    feedback = 'The value is ' + c.answer + ': ' + c.why;
    feedbackKind = 'bad';
  }
  showModeControls();
}

function nextChallenge() {
  if (mode !== 'challenge' || !answered) return;
  challengeIndex++;
  if (challengeIndex >= challenges.length) {
    mode = 'done';
    const mastery = score >= 5 ? 'Mastery reached (5 of 6 needed).' : 'Mastery needs 5 of 6. Explore the bits and try again.';
    feedback = 'You scored ' + score + ' of 6. ' + mastery +
      ' Now drag a slider slowly: the 16-bit value only changes when a color crosses a multiple of 8 (or of 4 for green).';
    feedbackKind = score >= 5 ? 'good' : 'info';
    showModeControls();
  } else {
    loadChallenge();
  }
}

function draw() {
  updateCanvasSize();

  // Drawing region and control region backgrounds
  stroke('silver');
  strokeWeight(1);
  fill('aliceblue');
  rect(0, 0, canvasWidth, drawHeight);
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  const r = redSlider.value();
  const g = greenSlider.value();
  const b = blueSlider.value();
  const value = color565(r, g, b);
  // In challenge mode, the bits stay hidden until the answer is revealed
  const reveal = (mode !== 'challenge') || answered;

  // Title
  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(24);
  text('RGB565 Color Mixer', canvasWidth / 2, 8);

  // Status line: question or challenge number, plus running score
  textSize(defaultTextSize);
  textAlign(LEFT, TOP);
  noStroke();
  fill('black');
  let status;
  if (mode === 'challenge') {
    const c = challenges[challengeIndex];
    status = 'Challenge ' + (challengeIndex + 1) + ' of 6: ' + c.name + ' (' + c.rgb.join(', ') + ')';
  } else if (mode === 'done') {
    status = 'Challenges finished';
  } else {
    status = 'Which bits does each color keep?';
  }
  textStyle(BOLD);
  text(status, margin, 40);
  textStyle(NORMAL);
  if (mode !== 'explore') {
    textAlign(RIGHT, TOP);
    noStroke();
    text('Score: ' + score + ' of 6', canvasWidth - margin, 40);
  }

  drawSwatches(r, g, b, reveal);
  drawBitRows(r, g, b, reveal);
  drawPackedRow(value, reveal);
  drawFeedback();
  drawControlLabels(r, g, b);
}

// Two swatches: the full 24-bit color and the color the display can really show
function drawSwatches(r, g, b, reveal) {
  const x = margin;
  const y = 66;
  const s = 66;
  stroke('dimgray');
  strokeWeight(1);
  fill(r, g, b);
  rect(x, y, s, s, 6);

  // Expand the kept bits back to 8 bits to show the display's color
  const r5 = r >> 3, g6 = g >> 2, b5 = b >> 3;
  const rd = (r5 << 3) | (r5 >> 2);
  const gd = (g6 << 2) | (g6 >> 4);
  const bd = (b5 << 3) | (b5 >> 2);
  if (reveal) fill(rd, gd, bd);
  else fill('gainsboro');
  rect(x + s + 12, y, s, s, 6);
  if (!reveal) {
    noStroke();
    fill('dimgray');
    textAlign(CENTER, CENTER);
    textSize(28);
    text('?', x + s + 12 + s / 2, y + s / 2);
  }

  noStroke();
  fill('black');
  textSize(14);
  textAlign(CENTER, TOP);
  text('24-bit', x + s / 2, y + s + 3);
  text('RGB565', x + s + 12 + s / 2, y + s + 3);

  // Values and the packing rule to the right of the swatches
  const tx = x + 2 * s + 30;
  textAlign(LEFT, TOP);
  textSize(defaultTextSize);
  noStroke();
  fill('black');
  text('R = ' + r + ',  G = ' + g + ',  B = ' + b, tx, y);
  textSize(14);
  fill('dimgray');
  text('value = (R & 0xF8) << 8', tx, y + 26);
  text('  | (G & 0xFC) << 3 | B >> 3', tx, y + 44);
  if (mode === 'challenge' && !answered) {
    fill('darkblue');
    text('Type the 16-bit value in hex below.', tx, y + 64);
  }
}

// One row per color: the 8 input bits, with kept bits colored and dropped bits struck out
function drawBitRows(r, g, b, reveal) {
  const rows = [
    { label: 'Red', v: r, keep: 5, edge: 'crimson', tint: 'mistyrose' },
    { label: 'Green', v: g, keep: 6, edge: 'seagreen', tint: 'honeydew' },
    { label: 'Blue', v: b, keep: 5, edge: 'royalblue', tint: 'lavender' }
  ];
  const x0 = margin + 95;
  const avail = canvasWidth - x0 - margin;
  const showNote = avail > 8 * 28 + 120;
  const bs = constrain(floor((showNote ? avail - 120 : avail) / 8), 16, 28);
  let y = 166;
  for (const row of rows) {
    noStroke();
    fill('black');
    textSize(defaultTextSize);
    textAlign(LEFT, CENTER);
    text(row.label + ' ' + row.v, margin, y + bs / 2);
    const bits = toBin(row.v, 8);
    for (let i = 0; i < 8; i++) {
      const kept = i < row.keep;
      const bx = x0 + i * bs;
      strokeWeight(kept ? 2 : 1);
      stroke(kept ? row.edge : 'silver');
      fill(kept ? row.tint : 'gainsboro');
      rect(bx, y, bs - 2, bs);
      noStroke();
      fill(kept ? 'black' : 'gray');
      textAlign(CENTER, CENTER);
      textSize(bs >= 24 ? 16 : 13);
      text(reveal ? bits[i] : '?', bx + (bs - 2) / 2, y + bs / 2);
      if (!kept && reveal) {
        stroke('gray');
        strokeWeight(1);
        line(bx + 3, y + bs - 4, bx + bs - 5, y + 4);
      }
    }
    if (showNote) {
      noStroke();
      fill(row.edge);
      textSize(14);
      textAlign(LEFT, CENTER);
      text('keeps top ' + row.keep + ', drops ' + (8 - row.keep), x0 + 8 * bs + 8, y + bs / 2);
    }
    y += 36;
  }
}

// The packed 16-bit value: 5 red bits, 6 green bits, 5 blue bits
function drawPackedRow(value, reveal) {
  const x0 = margin + 95;
  const avail = canvasWidth - x0 - margin;
  const bs = constrain(floor(avail / 16), 14, 28);
  const y = 284;
  noStroke();
  fill('black');
  textSize(defaultTextSize);
  textAlign(LEFT, CENTER);
  text('16 bits', margin, y + bs / 2);
  const bits = toBin(value, 16);
  for (let i = 0; i < 16; i++) {
    let edge, tint;
    if (i < 5) { edge = 'crimson'; tint = 'mistyrose'; }
    else if (i < 11) { edge = 'seagreen'; tint = 'honeydew'; }
    else { edge = 'royalblue'; tint = 'lavender'; }
    const bx = x0 + i * bs;
    stroke(edge);
    strokeWeight(2);
    fill(tint);
    rect(bx, y, bs - 2, bs);
    noStroke();
    fill('black');
    textAlign(CENTER, CENTER);
    textSize(bs >= 24 ? 16 : 12);
    text(reveal ? bits[i] : '?', bx + (bs - 2) / 2, y + bs / 2);
  }
  // Group labels under the packed bits
  noStroke();
  textSize(13);
  textAlign(CENTER, TOP);
  fill('crimson');
  text('red 5', x0 + 2.5 * bs, y + bs + 3);
  fill('seagreen');
  text('green 6', x0 + 8 * bs, y + bs + 3);
  fill('royalblue');
  text('blue 5', x0 + 13.5 * bs, y + bs + 3);

  // Hex value and the two bytes sent on the wire (high byte first)
  const hex = toHex4(value);
  noStroke();
  fill('black');
  textSize(defaultTextSize);
  textAlign(LEFT, TOP);
  if (reveal) {
    textStyle(BOLD);
    text('Hex: 0x' + hex, margin, 340);
    textStyle(NORMAL);
    text('Bytes sent: ' + hex.substring(0, 2) + ' ' + hex.substring(2), margin + 140, 340);
  } else {
    text('Hex: 0x????', margin, 340);
  }
}

function drawFeedback() {
  if (!feedback) return;
  const x = margin;
  const y = 368;
  const w = canvasWidth - 2 * margin;
  const h = drawHeight - y - 8;
  stroke(feedbackKind === 'good' ? 'seagreen' : (feedbackKind === 'bad' ? 'darkorange' : 'silver'));
  strokeWeight(1);
  fill(feedbackKind === 'good' ? 'honeydew' : (feedbackKind === 'bad' ? 'seashell' : 'white'));
  rect(x - 6, y - 4, w + 12, h + 4, 8);
  noStroke();
  fill('black');
  textSize(15);
  textAlign(LEFT, TOP);
  text(feedback, x, y, w, h);
}

function drawControlLabels(r, g, b) {
  noStroke();
  fill('black');
  textSize(defaultTextSize);
  textAlign(LEFT, CENTER);
  text('Red: ' + r, 10, drawHeight + 15);
  text('Green: ' + g, 10, drawHeight + 50);
  text('Blue: ' + b, 10, drawHeight + 85);
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
  if (typeof redSlider !== 'undefined') {
    const w = canvasWidth - sliderLeftMargin - margin;
    redSlider.size(w);
    greenSlider.size(w);
    blueSlider.size(w);
  }
}
