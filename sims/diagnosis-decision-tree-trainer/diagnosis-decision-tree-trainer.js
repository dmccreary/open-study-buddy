// Diagnosis Decision Tree Trainer - p5.js MicroSim
// CANVAS_HEIGHT: 640
// Differentiate the likely cause of a reported kit failure. Each tree is the
// flat decision table of Chapter 18 ("Diagnosing the Three Classic Failures",
// tools/diagnose.py): ask each row's yes-or-no question in order; yes ends the
// walk at that row's cause, no goes to the next row; the last row is reached
// when every answer is no. The six cases are illustrative.

let canvasWidth = 800;
let drawHeight = 560;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

const TREES = {
  mic: { name: 'Silent microphone', rows: [
    ['M1', 'An error at start, and it says "must be sck+1"?', 'WS is not on the pin after SCK', 'Compare with the table: SCK GP10, WS GP11', 'Move the wire back. Do not edit config.py: SCK on GP12 would need WS on GP13, the MODE button'],
    ['M2', 'An error at start, with another message?', 'A previous run left the I2S block open, or memory is short (likely)', 'Ctrl-D, run again, print gc.mem_free()', 'Close the microphone in a finally block'],
    ['M3', 'No error, but the spread is 0, a flat line?', 'Swapped SCK, WS, or SD wires; no power; or the mute switch is on', 'In order: SCK, WS, SD; VDD on 3V3, not 5 V; GND and L/R on GND; the mute switch', 'Re-seat the wires. A swapped microphone starts with no error and sends zeros'],
    ['M4', 'The loudness barely changes when you talk next to it?', 'L/R is on 3V3, so the microphone answers in the right slot while the program reads the left', 'Look at where L/R goes', 'Move L/R to GND'],
    ['M5', 'The meter is pinned at the top?', 'The 32-bit samples were not shifted right by 8, so values are 256 times too big; or the room or SD wire is noisy', 'Print a few samples before and after >> config.MIC_SAMPLE_SHIFT', 'Shift by MIC_SAMPLE_SHIFT and subtract the frame\'s DC offset'],
    ['M6', null, 'The microphone works; the level you chose is the problem', 'Probe 03: does a clap jump several bits?', 'Calibrate the noise floor first; for quiet playback raise PLAYBACK_GAIN']
  ] },
  audio: { name: 'Distorted audio', rows: [
    ['A1', 'Is the speaker silent, not distorted?', 'No power or ground at the amplifier, or a signal wire is wrong', 'Probe 04; VIN and GND, then BCLK GP20, LRC GP21, DIN GP19', 'Fix the wire. If I2S() raises an error, LRC must be right after BCLK'],
    ['A2', 'Does it crackle only when loud?', 'The samples clip: peaks are cut flat', 'Lower VOLUME; the crackle should go', 'Reduce VOLUME (test 05) or PLAYBACK_GAIN (test 07)'],
    ['A3', 'Is the pitch wrong?', 'The playback sample rate is not the recording rate', 'Print both rates', 'Use MIC_SAMPLE_RATE for both'],
    ['A4', 'Does it stutter or have gaps?', 'The loop takes longer than one 40 ms frame: a frame overrun', 'Wrap the microphone in OverrunCounter; read the summary', 'Redraw only changed regions, or slice big jobs'],
    ['A5', 'Is the start clicky, or the end cut off?', 'deinit() ran before the buffer drained; or a WAV header was played as sound', 'Listen with and without f.seek(44); lengthen the tail', 'Write silence and wait the buffer\'s length; skip the 44-byte header; fade 10 ms'],
    ['A6', 'Is there hiss or buzz even when nothing plays?', 'Power or ground noise: loose grounds, long wires', 'Re-seat every GND; keep microphone and amplifier wires apart', 'Shorter wires and one solid ground rail'],
    ['A7', null, 'No cause matched', 'Play the 05 tone and a 07 recording separately', 'Fix the path that distorts']
  ] },
  display: { name: 'Blank display', rows: [
    ['D1', 'Is the screen completely dark, with no light?', 'The backlight is off: BL not wired, VCC or GND missing, or set_backlight(True) never ran', 'Check BL to GP7, VCC to 3V3, GND', 'Wire BL to GP7 and call config.set_backlight(True)'],
    ['D2', 'Did the program stop with an error before drawing?', 'A kit file is missing: config.py, lib/gc9b72.py, or a font', 'Self-test "Files", or 02-probe.py section 4', 'Run upload-chapter.sh'],
    ['D3', 'Is it lit but only black or random noise?', 'A control wire is wrong: SCL GP2, SDA GP3, RST GP4, DC GP5, or CS GP6', '07-wiring-check.py; touch each wire', 'Fix the wire; the colors are in config.py'],
    ['D4', 'Is the picture speckled or torn?', 'The SPI speed is too fast for the wiring', 'Print the SPI object to see the rate you got', 'BAUDRATE = 12_000_000 (nothing exists between 12 and 24 MHz)'],
    ['D5', 'Is part of what you drew missing?', 'It was drawn outside the visible circle: corners and edge are hidden', 'Chapter 4\'s 04-display-visible-area.py', 'Stay inside SAFE_RADIUS, 168 pixels from the center'],
    ['D6', 'Is the picture rotated or mirrored?', 'The driver\'s rotation argument', 'Try 0, 1, 2, 3 in config.init_display()', 'Choose the one that matches'],
    ['D7', 'Are old letters left over, or is the picture sheared or striped?', 'Text was not padded to a fixed width, or a buffer is not width x height x 2 bytes', 'Print len(buffer) and compare', 'Pad with .center(width); size buffers exactly'],
    ['D8', null, 'A program from an earlier kit may be running as main.py', 'mpremote fs ls', 'mpremote fs rm main.py']
  ] }
};
// each case: symptoms, tree, correct row, the other candidates and what separates each from the answer
const CASES = [
  { tree: 'mic', text: 'The microphone test stops at once with: invalid ws (must be sck+1).', correct: 'M1',
    others: { M3: 'the error at start: M3 is for a program that starts with no error', M4: 'the error at start: M4 is a quiet signal from a microphone that runs', M5: 'the error at start: a pinned meter needs the program to run' } },
  { tree: 'mic', text: 'No error. The probe says every sample is 12345 and the spread is 0.', correct: 'M3',
    others: { M1: '"No error": M1 always stops with the sck+1 message', M4: 'the spread of 0: in M4 the loudness still changes a little', M6: 'the spread of 0: M6 means the microphone works, but a flat line means no real samples arrive' } },
  { tree: 'display', text: 'The screen is completely dark. The program runs and prints no errors.', correct: 'D1',
    others: { D2: '"prints no errors": D2 is a program that stops with an error before drawing', D3: '"completely dark": D3 is a screen that is lit but black or noisy', D4: '"completely dark": D4 is a lit screen with a speckled picture' } },
  { tree: 'display', text: 'The screen is lit and shows the right picture, but it is speckled, on long wires.', correct: 'D4',
    others: { D3: '"the right picture": D3 shows only black or random noise', D5: '"speckled": D5 is part of the picture missing at the edge', D7: '"speckled on long wires": D7 is left-over letters or a sheared picture from a wrong buffer size' } },
  { tree: 'audio', text: 'A recording I made plays back higher and faster than I spoke.', correct: 'A3',
    others: { A2: '"higher and faster": A2 is a crackle only when loud, with the pitch still right', A4: '"higher and faster": A4 is stutters and gaps, not a change of pitch', A6: '"higher and faster": A6 is hiss or buzz even when nothing plays' } },
  { tree: 'audio', text: 'The sound stutters. The overrun counter reports many passes longer than 40 ms.', correct: 'A4',
    others: { A1: '"the sound stutters": A1 is a silent speaker', A3: 'the overrun counter: A3 is a wrong pitch from mismatched sample rates', A5: 'the overrun counter: A5 is a click at the start or a cut-off end, not gaps all through' } }
];
const LETTERS = ['A', 'B', 'C', 'D'];

let mode = 'explore';
let exploreTree = null;
let answers = [];          // yes/no answers so far in the explore walk
let caseIndex = 0;
let submitted = false;
let finished = false;
let results = [];
let chosen = -1;
let candidates = [];
let feedback = '';
let feedbackCorrect = false;

let modeButton, choiceButtons = [], nextButton, symptomLabel, symptomSelect, yesButton, noButton, restartButton;

function rowOf(tree, id) {
  return TREES[tree].rows.find(r => r[0] === id);
}

// candidate order shuffled with a fixed seed per case
function shuffledCandidates(k) {
  const c = CASES[k];
  const list = [c.correct, ...Object.keys(c.others)];
  let seed = 1000 + 17 * (k + 1);
  const rnd = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
  for (let i = list.length - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [list[i], list[j]] = [list[j], list[i]];
  }
  return list;
}

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  modeButton = createButton('Start the 6 cases');
  modeButton.mousePressed(toggleMode);
  for (let i = 0; i < 4; i++) {
    const b = createButton('Cause ' + LETTERS[i]);
    b.mousePressed(() => choose(i));
    choiceButtons.push(b);
  }
  nextButton = createButton('Next case');
  nextButton.mousePressed(nextCase);
  symptomLabel = createSpan('Symptom:');
  symptomSelect = createSelect();
  symptomSelect.option('choose', '');
  for (const k of Object.keys(TREES)) symptomSelect.option(TREES[k].name, k);
  symptomSelect.changed(() => { exploreTree = symptomSelect.value() || null; answers = []; updateControlStates(); });
  yesButton = createButton('Yes');
  yesButton.mousePressed(() => answer(true));
  noButton = createButton('No');
  noButton.mousePressed(() => answer(false));
  restartButton = createButton('Restart tree');
  restartButton.mousePressed(() => { answers = []; updateControlStates(); });
  for (const el of [modeButton, ...choiceButtons, nextButton, symptomLabel, symptomSelect, yesButton, noButton, restartButton]) el.style('font-size', '16px');

  positionControls();
  updateControlStates();

  describe('Three flat decision trees for the kit\'s classic failures: a silent microphone, distorted audio and a blank display. Each row asks a yes-or-no question; yes ends at that row\'s likely cause, quick test and fix. In explore mode the learner answers the questions one at a time. In the quiz the learner reads a reported failure, chooses its cause from four candidates, and then sees the tree walked to the right row.', LABEL);
}

// the explore walk: index of the row being asked, and the row reached (or -1)
function walkState(tree) {
  const rows = TREES[tree].rows;
  let i = 0;
  for (const a of answers) {
    if (a) return { asking: -1, reached: i };
    i++;
  }
  if (rows[i][1] === null) return { asking: -1, reached: i };
  return { asking: i, reached: -1 };
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
  text('Diagnosis Decision Tree Trainer', canvasWidth / 2, 10);
  textSize(16);
  fill('dimgray');
  let status;
  if (mode === 'explore') status = 'Explore: walk one tree, cheapest question first';
  else if (finished) status = 'All 6 cases done   |   Score: ' + countCorrect() + ' of 6';
  else status = 'Case ' + (caseIndex + 1) + ' of 6 (illustrative)   |   Score: ' + countCorrect() + ' of 6';
  text(status, canvasWidth / 2, 42);

  const split = canvasWidth * 0.5;
  if (mode === 'explore') {
    if (exploreTree) {
      const ws = walkState(exploreTree);
      drawTree(exploreTree, answers.length, ws.reached, ws.asking, margin, 70, split - margin - 8);
      drawExploreRight(exploreTree, ws, split + 4, 70, canvasWidth - split - 4 - margin);
    } else {
      drawChooser(margin, 70, canvasWidth - 2 * margin);
    }
  } else {
    const c = CASES[min(caseIndex, 5)];
    const idx = TREES[c.tree].rows.findIndex(r => r[0] === c.correct);
    if (submitted || finished) drawTree(c.tree, idx, idx, -1, margin, 70, split - margin - 8);
    else drawHiddenTree(c.tree, margin, 70, split - margin - 8);
    drawCase(c, split + 4, 70, canvasWidth - split - 4 - margin);
  }
  drawPanel(margin, 432, canvasWidth - 2 * margin, drawHeight - 440);
}

function drawChooser(x, y, w) {
  noStroke();
  fill('navy');
  textAlign(CENTER, TOP);
  textSize(18);
  textStyle(ITALIC);
  text('Which one are you diagnosing?', x + w / 2, y + 60);
  textStyle(NORMAL);
  fill('black');
  textSize(16);
  let yy = y + 100;
  for (const k of Object.keys(TREES)) {
    text(TREES[k].name + ' (' + TREES[k].rows.length + ' rows: ' + TREES[k].rows[0][0] + ' to ' + TREES[k].rows[TREES[k].rows.length - 1][0] + ')', x + w / 2, yy);
    yy += 28;
  }
  fill('dimgray');
  text('Pick a symptom in the menu below.', x + w / 2, yy + 12);
}

// tree rows; rows before `done` answered no, row `reached` answered yes
function drawTree(tree, done, reached, asking, x, y, w) {
  const rows = TREES[tree].rows;
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(15);
  textStyle(BOLD);
  text(TREES[tree].name + ' tree', x, y);
  textStyle(NORMAL);
  const rh = min(42, 330 / rows.length);
  rows.forEach((r, i) => {
    const yy = y + 24 + i * rh;
    let bg = 'white';
    let tag = '';
    if (i === reached) { bg = 'gold'; tag = r[1] ? 'yes' : 'reached'; }
    else if (i < done) { bg = 'whitesmoke'; tag = 'no'; }
    if (i === asking) bg = 'lightcyan';
    stroke(i === asking ? 'navy' : 'silver');
    fill(bg);
    rect(x, yy, w, rh - 4, 5);
    noStroke();
    fill(i < done && i !== reached ? 'gray' : 'black');
    textSize(13);
    textStyle(BOLD);
    text(r[0], x + 6, yy + 4);
    textStyle(NORMAL);
    drawWrapped(r[1] || 'None of the above', x + 34, yy + 4, w - 80, 15);
    if (tag) {
      fill(tag === 'no' ? 'firebrick' : 'darkgreen');
      textAlign(RIGHT, TOP);
      textStyle(BOLD);
      text(tag, x + w - 6, yy + 4);
      textStyle(NORMAL);
      textAlign(LEFT, TOP);
    }
  });
}

function drawHiddenTree(tree, x, y, w) {
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(15);
  textStyle(BOLD);
  text(TREES[tree].name + ' tree', x, y);
  textStyle(NORMAL);
  fill('dimgray');
  textSize(14);
  drawWrapped('The tree is walked for this case after you choose a cause.', x, y + 30, w, 18);
}

function drawExploreRight(tree, ws, x, y, w) {
  noStroke();
  textAlign(LEFT, TOP);
  if (ws.asking >= 0) {
    const r = TREES[tree].rows[ws.asking];
    fill('navy');
    textSize(15);
    textStyle(BOLD);
    text('Row ' + r[0] + ' asks:', x, y);
    textStyle(NORMAL);
    fill('black');
    textSize(17);
    drawWrapped(r[1], x, y + 26, w, 22);
    fill('dimgray');
    textSize(14);
    drawWrapped('Answer Yes or No below. Yes ends the walk at this row\'s cause; No goes to the next row.', x, y + 110, w, 18);
    return;
  }
  drawCause(TREES[tree].rows[ws.reached], x, y, w);
}

function drawCause(r, x, y, w) {
  fill('honeydew');
  stroke('seagreen');
  rect(x, y, w, 330, 8);
  noStroke();
  textAlign(LEFT, TOP);
  let yy = y + 8;
  const parts = [['Likely cause (' + r[0] + ')', r[2]], ['Quick test', r[3]], ['Fix', r[4]]];
  for (const [h, t] of parts) {
    fill('darkgreen');
    textSize(14);
    textStyle(BOLD);
    text(h, x + 10, yy);
    textStyle(NORMAL);
    fill('black');
    textSize(14);
    yy = drawWrapped(t, x + 10, yy + 18, w - 20, 17) + 8;
  }
}

function drawCase(c, x, y, w) {
  noStroke();
  textAlign(LEFT, TOP);
  fill('black');
  textSize(15);
  textStyle(BOLD);
  text('Reported:', x, y);
  textStyle(NORMAL);
  textStyle(ITALIC);
  let yy = drawWrapped('"' + c.text + '"', x, y + 22, w, 19) + 8;
  textStyle(NORMAL);
  fill('navy');
  textSize(15);
  text('Which is the likely cause?', x, yy);
  yy += 22;
  candidates.forEach((id, i) => {
    const r = rowOf(c.tree, id);
    let col = 'black';
    if (submitted && id === c.correct) col = 'darkgreen';
    else if (submitted && i === chosen) col = 'firebrick';
    fill(col);
    textSize(14);
    textStyle(submitted && (id === c.correct || i === chosen) ? BOLD : NORMAL);
    yy = drawWrapped(LETTERS[i] + '.  ' + r[2] + (submitted ? '  (' + id + ')' : ''), x, yy, w, 17) + 6;
    textStyle(NORMAL);
  });
}

function drawPanel(x, y, w, h) {
  fill(255, 255, 255, 235);
  stroke('silver');
  rect(x, y, w, h, 10);
  const pad = 10;
  const tw = w - 2 * pad;
  let yy = y + 8;
  noStroke();
  textAlign(LEFT, TOP);
  textSize(15);
  if (mode === 'explore') {
    fill('dimgray');
    drawWrapped('Each tree asks the cheapest question first: a one-second look rules out a whole branch. Walk each tree, then press Start the 6 cases.', x + pad, yy, tw, 19);
    return;
  }
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 5 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 6. ' + (sc >= 5 ? 'Mastery reached.' : 'Mastery is 5 of 6.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('Which symptom details let you rule out the other three candidates quickly in each case?', x + pad, yy + 24, tw, 19);
    return;
  }
  if (!submitted) {
    fill('dimgray');
    drawWrapped('Read the reported symptoms and pick the candidate cause that fits every detail, with Cause A, B, C or D. One attempt.', x + pad, yy, tw, 19);
    return;
  }
  const r = rowOf(CASES[caseIndex].tree, CASES[caseIndex].correct);
  fill(feedbackCorrect ? 'darkgreen' : 'firebrick');
  textStyle(BOLD);
  yy = drawWrapped(feedback, x + pad, yy, tw, 19);
  textStyle(NORMAL);
  fill('black');
  yy = drawWrapped('Quick test: ' + r[3] + '.', x + pad, yy + 2, tw, 19);
  drawWrapped('Fix: ' + r[4] + '.', x + pad, yy, tw, 19);
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

// ---------- logic ----------

function answer(yes) {
  if (mode !== 'explore' || !exploreTree) return;
  if (walkState(exploreTree).asking < 0) return;
  answers.push(yes);
  updateControlStates();
}

function toggleMode() {
  if (mode === 'explore') {
    mode = 'quiz';
    caseIndex = 0;
    results = [];
    submitted = false;
    finished = false;
    candidates = shuffledCandidates(0);
  } else {
    mode = 'explore';
  }
  chosen = -1;
  updateControlStates();
}

function choose(i) {
  if (mode !== 'quiz' || submitted || finished) return;
  const c = CASES[caseIndex];
  chosen = i;
  const id = candidates[i];
  const correct = id === c.correct;
  results[caseIndex] = correct;
  feedbackCorrect = correct;
  const right = rowOf(c.tree, c.correct)[2];
  // lower-case the first word mid-sentence, but keep names such as WS or L/R
  const mid = /^[A-Z][a-z]/.test(right) ? right[0].toLowerCase() + right.slice(1) : right;
  feedback = correct ? 'Correct: ' + right + '.' : 'Not quite. The likely cause is ' + mid + ' (' + c.correct + '): look at ' + c.others[id] + '.';
  submitted = true;
  updateControlStates();
}

function nextCase() {
  if (!submitted) return;
  if (caseIndex === CASES.length - 1) finished = true;
  else { caseIndex++; submitted = false; chosen = -1; candidates = shuffledCandidates(caseIndex); }
  updateControlStates();
}

function setEnabled(el, on) {
  el.elt.disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  modeButton.html(quiz ? 'Back to explore' : 'Start the 6 cases');
  for (const b of choiceButtons) setEnabled(b, quiz && !submitted && !finished);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(caseIndex === CASES.length - 1 ? 'See score' : 'Next case');
  const asking = !quiz && exploreTree && walkState(exploreTree).asking >= 0;
  setEnabled(symptomSelect, !quiz);
  setEnabled(yesButton, asking);
  setEnabled(noButton, asking);
  setEnabled(restartButton, !quiz && exploreTree && answers.length > 0);
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
  layoutRow([modeButton, ...choiceButtons, nextButton], 10, drawHeight + 8, 8);
  layoutRow([symptomLabel, symptomSelect, yesButton, noButton, restartButton], 10, drawHeight + 44, 10);
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
