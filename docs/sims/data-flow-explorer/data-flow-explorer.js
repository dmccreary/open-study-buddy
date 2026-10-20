// Data Flow Explorer - p5.js MicroSim
// CANVAS_HEIGHT: 610
// Examine who can see each of the 8 hops of one spoken question, under two
// settings: network encryption (on or off) and services (school server or an
// outside vendor). Default visibility comes from the Chapter 17 table
// "Tracing One Question" (tools/data_flow.py). Encryption off adds "Anyone on
// the Wi-Fi" to hops 2, 6, 7 and 8; an outside vendor adds the vendor to hops
// 3, 4 and 5. The visibility matrix is a model, not a measurement of any school.

let canvasWidth = 800;
let drawHeight = 530;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

const OBSERVERS = {
  P: { name: 'Pico', color: 'seagreen' },
  A: { name: 'School server admin', color: 'royalblue' },
  V: { name: 'Outside vendor', color: 'darkorange' },
  W: { name: 'Anyone on the Wi-Fi', color: 'crimson' },
  B: { name: 'Broker admin and subscribers', color: 'purple' }
};
const HOPS = [
  { name: 'Microphone to Pico', sees: 'P', travels: 'Audio samples', who: 'The Pico only', stored: 'RAM, overwritten', kept: 'About 0.4 s in the ring, plus the recording buffer' },
  { name: 'Pico to server', sees: 'PA', travels: 'Audio chunks, after a press', who: 'Server admin; anyone on the Wi-Fi if the link is not encrypted', stored: 'Not stored by the network', kept: 'None' },
  { name: 'Speech-to-text', sees: 'A', travels: 'The audio, then the words', who: 'Server admin; the vendor if cloud', stored: 'Memory only', kept: '0 days for audio' },
  { name: 'The agent or LLM', sees: 'A', travels: 'The question, plus calendar items', who: 'Server admin; the vendor if cloud', stored: 'Transcript log: off by default', kept: 'At most 7 days if turned on' },
  { name: 'Text-to-speech', sees: 'A', travels: 'Reply text, then reply audio', who: 'Server admin; the vendor if cloud', stored: 'Memory only', kept: '0 days' },
  { name: 'Server to Pico', sees: 'PA', travels: 'Reply text and audio', who: 'Same as hop 2', stored: 'RAM', kept: 'None' },
  { name: 'MQTT alerts', sees: 'PB', travels: 'Text such as "TEST: Biology"', who: "Everyone subscribed; the broker's admin", stored: 'Retained on the broker', kept: 'Until replaced' },
  { name: 'Device status', sees: 'PB', travels: 'Online, volume, last wake time', who: "The broker's admin and subscribers", stored: 'Retained on the broker', kept: 'Until replaced' }
];
const QUESTIONS = [
  { q: 'With the default settings, how many hops can anyone on the Wi-Fi read?', enc: true, vendor: false, test: v => v.includes('W'), answer: 0,
    why: 'Encryption is on, so the Wi-Fi observer is added to no hop.' },
  { q: 'With encryption off, how many hops can anyone on the Wi-Fi read?', enc: false, vendor: false, test: v => v.includes('W'), answer: 4,
    why: 'Turning encryption off adds that observer to hops 2, 6, 7, and 8.' },
  { q: 'With services at an outside vendor, how many hops can the outside vendor see?', enc: true, vendor: true, test: v => v.includes('V'), answer: 3,
    why: 'The vendor is added to hops 3, 4, and 5: speech-to-text, the agent, and text-to-speech.' },
  { q: 'With the default settings, how many hops can the school server admin see?', enc: true, vendor: false, test: v => v.includes('A'), answer: 5,
    why: 'The admin sees hops 2, 3, 4, 5, and 6, because the server handles all of them.' },
  { q: 'With the default settings, how many hops can only the Pico see?', enc: true, vendor: false, test: v => v === 'P', answer: 1,
    why: 'Only hop 1 has the Pico as its single observer. Hops 7 and 8 also reach the broker.' },
  { q: 'With encryption off and services at an outside vendor, how many hops can at least three different observers see?', enc: false, vendor: true, test: v => v.length >= 3, answer: 4,
    why: 'Hops 2, 6, 7, and 8 each have the Pico, one more observer, and the Wi-Fi observer. Hops 3, 4, and 5 have two observers.' }
];

let mode = 'explore';
let qIndex = 0;
let submitted = false;
let finished = false;
let results = [];
let feedback = '';
let feedbackCorrect = false;
let selectedHop = -1;
let hopBoxes = [];

let modeButton, answerInput, submitButton, nextButton, encBox, vendorBox, hopLabel, hopSelect;

// observers who can see each hop under the two settings
function visibility(enc, vendor) {
  return HOPS.map((h, i) => {
    let v = h.sees;
    if (!enc && [1, 5, 6, 7].includes(i)) v += 'W';
    if (vendor && [2, 3, 4].includes(i)) v += 'V';
    return v;
  });
}

function settings() {
  if (mode === 'quiz') { const q = QUESTIONS[min(qIndex, 5)]; return { enc: q.enc, vendor: q.vendor }; }
  return { enc: encBox.checked(), vendor: vendorBox.checked() };
}

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  modeButton = createButton('Start the 6 questions');
  modeButton.mousePressed(toggleMode);
  answerInput = createInput('', 'number');
  answerInput.size(70);
  answerInput.attribute('min', '0');
  answerInput.attribute('max', '8');
  answerInput.attribute('placeholder', 'hops');
  answerInput.elt.addEventListener('keydown', e => { if (e.key === 'Enter') submitAnswer(); });
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next question');
  nextButton.mousePressed(nextQuestion);
  encBox = createCheckbox(' Network encryption on', true);
  vendorBox = createCheckbox(' Services at an outside vendor', false);
  hopLabel = createSpan('Show hop:');
  hopSelect = createSelect();
  hopSelect.option('none', '-1');
  HOPS.forEach((h, i) => hopSelect.option('Hop ' + (i + 1), String(i)));
  hopSelect.changed(() => { selectedHop = Number(hopSelect.value()); });
  for (const el of [modeButton, answerInput, submitButton, nextButton, encBox, vendorBox, hopLabel, hopSelect]) el.style('font-size', '16px');

  positionControls();
  updateControlStates();

  describe('The eight hops of one spoken question, from microphone to device status, drawn as boxes in two rows. Each box shows colored badges for the observers who can see that hop: the Pico, the school server admin, an outside vendor, anyone on the Wi-Fi, and the broker admin and subscribers. Checkboxes turn network encryption off and move the services to an outside vendor, and the badges change. Clicking a hop shows what travels, who can see it, where it is stored and for how long.', LABEL);
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
  text('Data Flow Explorer', canvasWidth / 2, 10);
  const st = settings();
  textSize(16);
  fill('dimgray');
  let status = 'Encryption ' + (st.enc ? 'on' : 'off') + ', services at ' + (st.vendor ? 'an outside vendor' : 'the school server') + ' (model, not a measurement)';
  if (mode === 'quiz') status = (finished ? 'All 6 questions done' : 'Question ' + (qIndex + 1) + ' of 6') + '   |   Score: ' + countCorrect() + ' of 6   |   ' +
    'encryption ' + (st.enc ? 'on' : 'off') + ', ' + (st.vendor ? 'vendor' : 'school server');
  textSize(mode === 'quiz' ? 15 : 14);
  text(status, canvasWidth / 2, 42);

  const vis = visibility(st.enc, st.vendor);
  const counted = mode === 'quiz' && submitted && !finished ? vis.map(v => QUESTIONS[qIndex].test(v)) : vis.map(() => false);
  drawHops(vis, counted, 68);
  drawLegend(282);
  drawHopInfo(vis, margin, 324, canvasWidth - 2 * margin, 104);
  drawPanel(margin, 436, canvasWidth - 2 * margin, drawHeight - 444);
}

function drawHops(vis, counted, y) {
  const gap = 10;
  const bw = (canvasWidth - 2 * margin - 3 * gap) / 4;
  const bh = 96;
  hopBoxes = [];
  for (let i = 0; i < 8; i++) {
    const r = Math.floor(i / 4);
    const c = i % 4;
    const x = margin + c * (bw + gap);
    const yy = y + r * (bh + 16);
    hopBoxes.push({ x: x, y: yy, w: bw, h: bh });
    stroke(counted[i] ? 'goldenrod' : (i === selectedHop ? 'navy' : 'steelblue'));
    strokeWeight(counted[i] || i === selectedHop ? 3 : 1);
    fill(counted[i] ? 'lightyellow' : 'white');
    rect(x, yy, bw, bh, 8);
    strokeWeight(1);
    noStroke();
    fill('black');
    textAlign(LEFT, TOP);
    textSize(14);
    textStyle(BOLD);
    drawWrapped((i + 1) + ' ' + HOPS[i].name, x + 8, yy + 6, bw - 14, 17);
    textStyle(NORMAL);
    // observer badges
    let bx = x + 8;
    for (const k of vis[i]) {
      fill(OBSERVERS[k].color);
      circle(bx + 12, yy + bh - 20, 24);
      fill('white');
      textAlign(CENTER, CENTER);
      textSize(13);
      textStyle(BOLD);
      text(k, bx + 12, yy + bh - 20);
      textStyle(NORMAL);
      bx += 28;
    }
    if (i % 4 < 3) {
      stroke('gray');
      line(x + bw + 1, yy + bh / 2, x + bw + gap - 1, yy + bh / 2);
    }
  }
}

// one line of observer badges, wrapping to a second line when narrow
function drawLegend(y) {
  let x = margin;
  noStroke();
  textSize(13);
  for (const k of Object.keys(OBSERVERS)) {
    if (x + 20 + textWidth(OBSERVERS[k].name) > canvasWidth - margin) { x = margin; y += 20; }
    fill(OBSERVERS[k].color);
    circle(x + 8, y + 8, 16);
    fill('white');
    textAlign(CENTER, CENTER);
    textSize(11);
    text(k, x + 8, y + 8);
    fill('black');
    textAlign(LEFT, CENTER);
    textSize(13);
    text(OBSERVERS[k].name, x + 20, y + 8);
    x += textWidth(OBSERVERS[k].name) + 36;
  }
}

function drawHopInfo(vis, x, y, w, h) {
  fill('honeydew');
  stroke('seagreen');
  rect(x, y, w, h, 8);
  noStroke();
  textAlign(LEFT, TOP);
  textSize(14);
  if (selectedHop < 0) {
    fill('dimgray');
    drawWrapped('Click a hop (or use Show hop) to read its row of the table "Tracing One Question".', x + 10, y + 10, w - 20, 18);
    return;
  }
  const hp = HOPS[selectedHop];
  fill('darkgreen');
  textStyle(BOLD);
  text('Hop ' + (selectedHop + 1) + ': ' + hp.name, x + 10, y + 6);
  textStyle(NORMAL);
  fill('black');
  let yy = drawWrapped('What travels: ' + hp.travels + '.  Who can see it (default design): ' + hp.who + '.', x + 10, y + 26, w - 20, 17);
  yy = drawWrapped('Stored: ' + hp.stored + '.  Kept: ' + hp.kept + '.', x + 10, yy, w - 20, 17);
  fill('dimgray');
  drawWrapped('With these settings: ' + vis[selectedHop].split('').map(k => OBSERVERS[k].name).join(', ') + '.', x + 10, yy, w - 20, 17);
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
  textSize(16);
  if (mode === 'explore') {
    fill('navy');
    textStyle(ITALIC);
    text('Who can see hop 2?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Flip the two settings and watch which badges appear. One change adds the same observer to several hops at once.', x + pad, yy + 22, tw, 20);
    return;
  }
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 5 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 6. ' + (sc >= 5 ? 'Mastery reached.' : 'Mastery is 5 of 6.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('Which single setting change exposed the most hops, and to whom?', x + pad, yy + 24, tw, 20);
    return;
  }
  const q = QUESTIONS[qIndex];
  fill('black');
  textStyle(BOLD);
  yy = drawWrapped(q.q, x + pad, yy, tw, 20);
  textStyle(NORMAL);
  if (!submitted) {
    fill('dimgray');
    drawWrapped('The settings for this question are already applied. Count the hops, type a whole number from 0 to 8, and Submit.', x + pad, yy + 2, tw, 20);
    return;
  }
  fill(feedbackCorrect ? 'darkgreen' : 'firebrick');
  textStyle(BOLD);
  drawWrapped(feedback, x + pad, yy + 2, tw, 20);
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

// clicking a hop box shows its details (the same as the Show hop menu)
function mousePressed() {
  for (let i = 0; i < hopBoxes.length; i++) {
    const b = hopBoxes[i];
    if (mouseX >= b.x && mouseX <= b.x + b.w && mouseY >= b.y && mouseY <= b.y + b.h) {
      selectedHop = i;
      hopSelect.selected(String(i));
    }
  }
}

// ---------- quiz logic ----------

function toggleMode() {
  if (mode === 'explore') {
    mode = 'quiz';
    qIndex = 0;
    results = [];
    submitted = false;
    finished = false;
  } else {
    mode = 'explore';
  }
  answerInput.value('');
  updateControlStates();
}

function submitAnswer() {
  if (mode !== 'quiz' || submitted || finished) return;
  const raw = answerInput.value().trim();
  if (raw === '' || isNaN(Number(raw))) return;
  const q = QUESTIONS[qIndex];
  const correct = Number(raw) === q.answer;
  results[qIndex] = correct;
  feedbackCorrect = correct;
  feedback = correct ? 'Correct: ' + q.why : 'Not quite. The answer is ' + q.answer + ': ' + q.why;
  submitted = true;
  updateControlStates();
}

function nextQuestion() {
  if (!submitted) return;
  if (qIndex === QUESTIONS.length - 1) finished = true;
  else { qIndex++; submitted = false; }
  answerInput.value('');
  updateControlStates();
}

function setEnabled(el, on) {
  const input = el.elt.querySelector('input');
  (input || el.elt).disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  modeButton.html(quiz ? 'Back to explore' : 'Start the 6 questions');
  setEnabled(answerInput, quiz && !submitted && !finished);
  setEnabled(submitButton, quiz && !submitted && !finished);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(qIndex === QUESTIONS.length - 1 ? 'See score' : 'Next question');
  setEnabled(encBox, !quiz);
  setEnabled(vendorBox, !quiz);
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
  layoutRow([modeButton, answerInput, submitButton, nextButton], 10, drawHeight + 8, 8);
  layoutRow([encBox, vendorBox, hopLabel, hopSelect], 10, drawHeight + 46, 16);
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
