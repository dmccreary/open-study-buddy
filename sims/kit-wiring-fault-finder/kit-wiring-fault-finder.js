// Kit Wiring Fault Finder MicroSim
// CANVAS_HEIGHT: 620
// Six wiring listings, each with exactly one line that does not match the
// chapter's Pin Assignment Table. The learner picks the faulty line from a
// menu and checks it (one attempt each). The table is always shown beside the
// listing. At the end the sim shows which mistakes raised an error message.

// ---- Canvas layout ----
let canvasWidth = 400;
let drawHeight = 540;
let controlHeight = 80;   // 2 control rows x 35 + 10
let canvasHeight = drawHeight + controlHeight;
let margin = 20;
let defaultTextSize = 16;

// ---- Controls ----
let lineSelect, checkButton, nextButton, restartButton;

// ---- Listings (spec order) ----
const listings = [
  { part: 'Microphone',
    lines: ['SCK to GP10', 'WS to GP11', 'SD to GP12', 'L/R to GND', 'VDD to VBUS (5 V)', 'GND to GND'],
    faulty: 'VDD to VBUS (5 V)', fix: 'VDD to 3V3', error: false, effect: 'no error, can damage the mic',
    symptom: 'The INMP441 is a 3.3 V part. A 5 V supply can damage it.' },
  { part: 'Microphone',
    lines: ['SCK to GP10', 'WS to GP13', 'SD to GP12', 'L/R to GND', 'VDD to 3V3', 'GND to GND'],
    faulty: 'WS to GP13', fix: 'WS to GP11', error: true, effect: 'error message from I2S()',
    symptom: 'I2S() raises "invalid ws (must be sck+1)", and GP13 is also the MODE button.' },
  { part: 'Amplifier',
    lines: ['BCLK to GP20', 'LRC to GP22', 'DIN to GP19', 'GAIN to GP18', 'VIN to VBUS', 'GND to GND'],
    faulty: 'LRC to GP22', fix: 'LRC to GP21', error: true, effect: 'error message from I2S()',
    symptom: 'I2S() raises an error because the left/right clock must be the pin right after the bit clock.' },
  { part: 'Button MODE',
    lines: ['One leg to GP13', 'Opposite leg to 3V3'],
    faulty: 'Opposite leg to 3V3', fix: 'Opposite leg to GND', error: false, effect: 'no error, button seems dead',
    symptom: 'With a pull-up, the pin always reads 1, so test 03 never reports a press.' },
  { part: 'Display',
    lines: ['SCL to GP2', 'SDA to GP3', 'RST to GP4', 'DC to GP5', 'CS to GP6', 'BL not connected', 'VCC to 3V3', 'GND to GND'],
    faulty: 'BL not connected', fix: 'BL to GP7', error: false, effect: 'no error, dark screen',
    symptom: 'The screen stays dark in test 04 because the backlight never turns on.' },
  { part: 'Amplifier',
    lines: ['BCLK to GP20', 'LRC to GP21', 'DIN to GP19', 'GAIN to GP18', 'VIN to VBUS', 'GND not connected'],
    faulty: 'GND not connected', fix: 'GND to GND', error: false, effect: 'no error, no sound',
    symptom: 'Test 05 is silent because the amplifier has no ground return.' }
];

// ---- The Pin Assignment Table from the chapter, grouped by part ----
// full: true entries take a whole row
const pinTable = [
  { part: 'Display', key: 'Display', entries: [
    ['SCL', 'GP2'], ['SDA', 'GP3'], ['RST', 'GP4'], ['DC', 'GP5'],
    ['CS', 'GP6'], ['BL', 'GP7'], ['VCC', '3V3'], ['GND', 'GND']] },
  { part: 'Microphone', key: 'Microphone', entries: [
    ['SCK', 'GP10'], ['WS', 'GP11'], ['SD', 'GP12'], ['L/R', 'GND'],
    ['VDD', '3V3'], ['GND', 'GND']] },
  { part: 'Buttons', key: 'Button MODE', entries: [
    ['MODE', 'GP13'], ['UP', 'GP14'], ['DOWN', 'GP15'], ['other legs', 'GND', true]] },
  { part: 'Amplifier', key: 'Amplifier', entries: [
    ['DIN', 'GP19'], ['BCLK', 'GP20'], ['LRC', 'GP21'], ['GAIN', 'GP18'],
    ['VIN', 'VBUS or 3V3', true], ['GND', 'GND', true]] }
];

// ---- State ----
let mode = 'quiz';      // 'quiz' | 'done'
let listingIndex = 0;
let score = 0;
let answered = false;
let chosen = -1;        // index of the line chosen in the menu
let feedback = '';
let feedbackKind = 'info';

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  // Every listing must contain its faulty line exactly once
  for (const L of listings) {
    if (L.lines.filter(x => x === L.faulty).length !== 1) console.warn('Bad listing', L);
  }

  // Create ALL controls first
  lineSelect = createSelect();
  lineSelect.attribute('aria-label', 'Choose the line that does not match the table');
  lineSelect.changed(() => {
    const v = lineSelect.value();
    chosen = v === '' ? -1 : Number(v);
  });
  checkButton = createButton('Check');
  checkButton.mousePressed(checkAnswer);
  nextButton = createButton('Next Listing');
  nextButton.mousePressed(nextListing);
  restartButton = createButton('Start Over');
  restartButton.mousePressed(startOver);

  // Then position them and load the first listing
  positionControls();
  loadListing();

  describe('Kit wiring fault finder. A wiring listing for one part of the kit is shown beside ' +
    'the pin assignment table. The learner chooses the one line that does not match the table ' +
    'from a menu and checks it. Feedback names the correct connection and what the builder would ' +
    'see. Six listings, scored n of 6.', LABEL);
}

function positionControls() {
  const y0 = drawHeight + 5;
  lineSelect.position(10, y0);
  checkButton.position(230, y0);
  nextButton.position(298, y0);
  restartButton.position(10, y0 + 35);
}

function loadListing() {
  const L = listings[listingIndex];
  // Rebuild the menu for this listing
  lineSelect.elt.innerHTML = '';
  lineSelect.option('Choose a line...', '');
  L.lines.forEach((ln, i) => lineSelect.option((i + 1) + '. ' + ln, String(i)));
  lineSelect.selected('');
  chosen = -1;
  answered = false;
  feedback = '';
  feedbackKind = 'info';
  updateControls();
}

function updateControls() {
  if (mode === 'done') {
    lineSelect.hide();
    checkButton.hide();
    nextButton.hide();
    restartButton.show();
    return;
  }
  lineSelect.show();
  checkButton.show();
  restartButton.show();
  if (answered) {
    lineSelect.attribute('disabled', '');
    checkButton.attribute('disabled', '');
    nextButton.html(listingIndex === listings.length - 1 ? 'See Score' : 'Next Listing');
    nextButton.show();
  } else {
    lineSelect.removeAttribute('disabled');
    checkButton.removeAttribute('disabled');
    nextButton.hide();
  }
}

function checkAnswer() {
  if (mode !== 'quiz' || answered) return;
  if (chosen < 0) {
    feedback = 'Choose a line from the menu first.';
    feedbackKind = 'info';
    return;
  }
  const L = listings[listingIndex];
  answered = true;
  if (L.lines[chosen] === L.faulty) {
    score++;
    feedback = 'Correct: ' + L.symptom;
    feedbackKind = 'good';
  } else {
    feedback = 'Not quite. The faulty line is ' + L.faulty + ': ' + L.symptom;
    feedbackKind = 'bad';
  }
  updateControls();
}

function nextListing() {
  if (!answered) return;
  if (listingIndex === listings.length - 1) {
    mode = 'done';
    updateControls();
    return;
  }
  listingIndex++;
  loadListing();
}

function startOver() {
  mode = 'quiz';
  listingIndex = 0;
  score = 0;
  loadListing();
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
  text('Kit Wiring Fault Finder', canvasWidth / 2, 8);

  textSize(defaultTextSize);
  textAlign(LEFT, TOP);
  textStyle(BOLD);
  noStroke();
  if (mode === 'done') {
    text('All six listings checked', margin, 40);
  } else {
    text('Listing ' + (listingIndex + 1) + ' of 6: ' + listings[listingIndex].part, margin, 40);
  }
  textStyle(NORMAL);
  textAlign(RIGHT, TOP);
  noStroke();
  text('Score: ' + score + ' of 6', canvasWidth - margin, 40);

  if (mode === 'done') {
    drawSummary();
    return;
  }

  const split = floor(canvasWidth * (canvasWidth < 560 ? 0.44 : 0.48));
  drawListing(margin, 68, split - margin - 8);
  const tableBottom = drawPinTable(split + 4, 66, canvasWidth - split - 4 - margin);
  if (feedback) drawFeedbackBox(max(tableBottom, listingBottom) + 10);
}

let listingBottom = 0;

function drawListing(x, y, w) {
  const L = listings[listingIndex];
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(defaultTextSize);
  textStyle(BOLD);
  y = wrapText('Which line does not match the table?', x, y, w, 20);
  textStyle(NORMAL);
  y += 6;
  const fs = canvasWidth < 560 ? 14 : 16;
  const lh = fs + 10;
  for (let i = 0; i < L.lines.length; i++) {
    const isFaulty = L.lines[i] === L.faulty;
    let bg = 'white';
    if (!answered && i === chosen) bg = 'lightyellow';
    if (answered && isFaulty) bg = 'mistyrose';
    if (answered && i === chosen && !isFaulty) bg = 'gainsboro';
    stroke(answered && isFaulty ? 'crimson' : 'silver');
    strokeWeight(answered && isFaulty ? 2 : 1);
    fill(bg);
    rect(x, y, w, lh - 3, 4);
    noStroke();
    fill('black');
    textSize(fs);
    textAlign(LEFT, CENTER);
    text((i + 1) + '. ' + L.lines[i], x + 6, y + (lh - 3) / 2);
    if (i === chosen && canvasWidth >= 560) {
      textAlign(RIGHT, CENTER);
      fill('dimgray');
      textSize(12);
      text(answered ? 'your pick' : 'chosen', x + w - 5, y + (lh - 3) / 2);
    }
    y += lh;
    if (answered && isFaulty) {
      noStroke();
      fill('seagreen');
      textSize(fs);
      textAlign(LEFT, TOP);
      textStyle(BOLD);
      text('Fix: ' + L.fix, x + 6, y);
      textStyle(NORMAL);
      y += lh - 4;
    }
  }
  // The three rules that hold the table together
  y += 6;
  noStroke();
  fill('dimgray');
  textAlign(LEFT, TOP);
  textSize(13);
  y = wrapText('Rules: each GP pin is used once; I2S clock pairs are neighbors; 3.3 V parts use 3V3.', x, y, w, 16);
  listingBottom = y;
}

// Draws the reference table; returns its bottom y.
// Entries flow left to right in a grid; a long entry spans extra columns.
function drawPinTable(x, y, w) {
  const L = listings[listingIndex];
  const fs = canvasWidth < 560 ? 13 : 15;
  const rowH = fs + 5;
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(fs + 1);
  textStyle(BOLD);
  text(w < 200 ? 'Pin Table' : 'Pin Assignment Table', x, y);
  textStyle(NORMAL);
  y += rowH + 4;
  textSize(fs);
  const cols = w >= 330 ? 3 : 2;
  const colW = (w - 10) / cols;
  for (const block of pinTable) {
    // Lay out the entries first: [label, col, row]
    const placed = [];
    let col = 0, row = 0;
    for (const e of block.entries) {
      const label = e[0] + ' \u2192 ' + e[1];
      const span = min(cols, ceil((textWidth(label) + 4) / colW));
      if (col + span > cols) { col = 0; row++; }
      placed.push([label, col, row]);
      col += span;
      if (col >= cols) { col = 0; row++; }
    }
    const rows = col === 0 ? row : row + 1;
    const h = rowH + rows * rowH + 6;
    const current = block.key === L.part;
    stroke(current ? 'goldenrod' : 'silver');
    strokeWeight(current ? 2 : 1);
    fill(current ? 'lightyellow' : 'white');
    rect(x, y, w, h, 4);
    noStroke();
    fill('black');
    textAlign(LEFT, TOP);
    textSize(fs);
    textStyle(BOLD);
    text(block.part, x + 5, y + 3);
    textStyle(NORMAL);
    for (const p of placed) {
      text(p[0], x + 8 + p[1] * colW, y + 3 + rowH + p[2] * rowH);
    }
    y += h + 4;
  }
  return y;
}

function drawSummary() {
  const x = margin;
  const w = canvasWidth - 2 * margin;
  let y = 70;
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(defaultTextSize);
  const mastery = score >= 5 ? 'Mastery reached (5 of 6 needed).' : 'Mastery needs 5 of 6. Press Start Over to try again.';
  textStyle(BOLD);
  y = wrapText('You scored ' + score + ' of 6. ' + mastery, x, y, w, 20);
  textStyle(NORMAL);
  y += 8;
  y = wrapText('Which mistakes produced an error message?', x, y, w, 20);
  y += 6;
  const fs = canvasWidth < 560 ? 13 : 15;
  textSize(fs);
  const c1 = 28, c2 = w * 0.45;
  const rows = [['#', 'Wrong line', 'What you would see']];
  listings.forEach((L, i) => rows.push([String(i + 1), L.faulty, L.effect]));
  for (let i = 0; i < rows.length; i++) {
    const n = max(countLines(rows[i][1], c2 - c1 - 10), countLines(rows[i][2], w - c2 - 10));
    const h = n * (fs + 4) + 8;
    stroke('silver');
    strokeWeight(1);
    let bg = i === 0 ? 'gainsboro' : (listings[i - 1].error ? 'honeydew' : 'seashell');
    fill(bg);
    rect(x, y, w, h);
    noStroke();
    fill('black');
    if (i === 0) textStyle(BOLD);
    text(rows[i][0], x + 6, y + 4);
    wrapText(rows[i][1], x + c1 + 4, y + 4, c2 - c1 - 10, fs + 4);
    wrapText(rows[i][2], x + c2 + 4, y + 4, w - c2 - 10, fs + 4);
    textStyle(NORMAL);
    y += h;
  }
  y += 10;
  textSize(defaultTextSize);
  fill('black');
  wrapText('Only 2 of the 6 mistakes raised an error message. The other four failed silently, ' +
    'so a missing error does not mean the wiring is right. Check every line against the table.', x, y, w, 20);
}

function drawFeedbackBox(y) {
  const x = margin;
  const w = canvasWidth - 2 * margin;
  textSize(15);
  const lines = countLines(feedback, w - 12);
  const h = lines * 19 + 12;
  stroke(feedbackKind === 'good' ? 'seagreen' : (feedbackKind === 'bad' ? 'darkorange' : 'silver'));
  strokeWeight(1);
  fill(feedbackKind === 'good' ? 'honeydew' : (feedbackKind === 'bad' ? 'seashell' : 'white'));
  rect(x - 4, y, w + 8, h, 8);
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  wrapText(feedback, x + 2, y + 6, w - 12, 19);
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
