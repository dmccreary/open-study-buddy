// Same-Subnet Checker - p5.js MicroSim
// CANVAS_HEIGHT: 595
// Calculate whether two IPv4 addresses are on the same network. The network
// address is the bitwise AND of each of the four numbers of an address with
// the matching number of the netmask; two addresses are on the same network
// when their network addresses are equal. The addresses are illustrative.

let canvasWidth = 800;
let drawHeight = 480;
let controlHeight = 115;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

const MASKS = ['255.255.255.0', '255.255.255.128', '255.255.240.0', '255.255.0.0'];
const CASES = [
  { a: '192.168.1.23', m: '255.255.255.0', b: '192.168.1.50', same: true, net: '192.168.1.0',
    why: 'The mask keeps the first three numbers, and both start 192.168.1.' },
  { a: '192.168.1.23', m: '255.255.255.0', b: '192.168.2.50', same: false, net: '192.168.1.0',
    why: 'The third numbers, 1 and 2, differ and the mask keeps them.' },
  { a: '10.4.7.88', m: '255.255.0.0', b: '10.4.200.9', same: true, net: '10.4.0.0',
    why: 'The mask keeps only 10.4, and both start 10.4.' },
  { a: '10.4.7.88', m: '255.255.255.0', b: '10.4.200.9', same: false, net: '10.4.7.0',
    why: 'The same two addresses, but this mask also keeps the third number, 7 and 200.' },
  { a: '172.16.5.5', m: '255.255.240.0', b: '172.16.15.1', same: true, net: '172.16.0.0',
    why: '240 is 11110000, so only the top 4 bits of the third number are kept; 5 and 15 are both 0000.' },
  { a: '172.16.5.5', m: '255.255.240.0', b: '172.16.16.1', same: false, net: '172.16.0.0',
    why: '16 is 00010000, so its kept bits are 0001, not 0000.' },
  { a: '192.168.1.200', m: '255.255.255.128', b: '192.168.1.20', same: false, net: '192.168.1.128',
    why: '128 is 10000000: 200 keeps the top bit (1) and 20 keeps 0.' },
  { a: '192.168.1.130', m: '255.255.255.128', b: '192.168.1.200', same: true, net: '192.168.1.128',
    why: '130 and 200 are both 128 or more, so both keep the top bit 1.' }
];

let mode = 'explore';
let caseIndex = 0;
let submitted = false;
let finished = false;
let results = [];
let feedback = '';
let feedbackCorrect = false;
let exploreA = [192, 168, 1, 23];
let exploreB = [192, 168, 1, 50];

let modeButton, submitButton, nextButton, answerLabel, sameSelect, netLabel, netInput;
let aLabel, aInput, bLabel, bInput, maskLabel, maskSelect;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  modeButton = createButton('Start the 8 cases');
  modeButton.mousePressed(toggleMode);
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next case');
  nextButton.mousePressed(nextCase);
  answerLabel = createSpan('Answer:');
  sameSelect = createSelect();
  for (const o of ['choose', 'same network', 'different networks']) sameSelect.option(o);
  netLabel = createSpan('Network address of the first:');
  netInput = createInput('');
  netInput.size(130);
  netInput.attribute('placeholder', 'a.b.c.d');
  netInput.elt.addEventListener('keydown', e => { if (e.key === 'Enter') submitAnswer(); });
  aLabel = createSpan('First:');
  aInput = createInput('192.168.1.23');
  aInput.size(120);
  aInput.input(() => { const v = parseAddr(aInput.value()); if (v) exploreA = v; });
  bLabel = createSpan('Second:');
  bInput = createInput('192.168.1.50');
  bInput.size(120);
  bInput.input(() => { const v = parseAddr(bInput.value()); if (v) exploreB = v; });
  maskLabel = createSpan('Mask:');
  maskSelect = createSelect();
  for (const m of MASKS) maskSelect.option(m);
  for (const el of [modeButton, submitButton, nextButton, answerLabel, sameSelect, netLabel, netInput, aLabel, aInput, bLabel, bInput, maskLabel, maskSelect]) {
    el.style('font-size', '16px');
  }

  positionControls();
  updateControlStates();

  describe('Two IPv4 addresses and a netmask shown as four decimal numbers and as 32 bits in four groups of eight. The bits the mask keeps are highlighted, and the network address of each address (the bitwise AND with the mask) is shown below with the verdict same network or different networks. An eight-case quiz asks for the verdict and the first network address.', LABEL);
}

// four whole numbers from 0 to 255, or null (an invalid change is ignored)
function parseAddr(s) {
  const parts = s.trim().split('.');
  if (parts.length !== 4) return null;
  const n = parts.map(p => (/^\d{1,3}$/.test(p) ? Number(p) : NaN));
  return n.every(v => v >= 0 && v <= 255) ? n : null;
}

function andMask(a, m) {
  return a.map((v, i) => v & m[i]);
}

function currentView() {
  if (mode === 'quiz') {
    const c = CASES[min(caseIndex, 7)];
    return { a: parseAddr(c.a), m: parseAddr(c.m), b: parseAddr(c.b) };
  }
  return { a: exploreA, m: parseAddr(maskSelect.value()), b: exploreB };
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
  text('Same-Subnet Checker', canvasWidth / 2, 10);
  textSize(16);
  fill('dimgray');
  let status;
  if (mode === 'explore') status = 'Explore: type any two addresses (illustrative) and pick a mask';
  else if (finished) status = 'All 8 cases done   |   Score: ' + countCorrect() + ' of 8';
  else status = 'Case ' + (caseIndex + 1) + ' of 8 (illustrative)   |   Score: ' + countCorrect() + ' of 8';
  text(status, canvasWidth / 2, 42);

  const v = currentView();
  const reveal = mode === 'explore' || submitted;
  const na = andMask(v.a, v.m);
  const nb = andMask(v.b, v.m);
  const rows = [
    { label: 'First address', n: v.a, kind: 'addr' },
    { label: 'Netmask', n: v.m, kind: 'mask' },
    { label: 'Second address', n: v.b, kind: 'addr' }
  ];
  let y = 80;
  for (const r of rows) { drawRow(r.label, r.n, v.m, r.kind, reveal, null, y); y += 40; }
  y += 6;
  stroke('gray');
  line(margin, y - 6, canvasWidth - margin, y - 6);
  if (reveal) {
    drawRow('First network', na, v.m, 'net', true, nb, y);
    drawRow('Second network', nb, v.m, 'net', true, na, y + 40);
  } else {
    noStroke();
    fill('dimgray');
    textAlign(CENTER, CENTER);
    textSize(15);
    text('The network addresses (address AND mask) are shown after you submit.', canvasWidth / 2, y + 36);
  }
  drawPanel(v, na, nb, margin, 340, canvasWidth - 2 * margin, drawHeight - 348);
}

// one row: label, dotted decimal, then 32 bits in 4 groups
function drawRow(label, n, m, kind, reveal, compare, y) {
  const bitX = 290;
  const gw = (canvasWidth - margin - bitX) / 4;
  const bw = (gw - 8) / 8;
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(15);
  text(label, margin, y + 13);
  textStyle(BOLD);
  text(n.join('.'), 140, y + 13);
  textStyle(NORMAL);
  textFont('monospace');
  textSize(min(15, bw * 1.3));
  for (let g = 0; g < 4; g++) {
    for (let k = 0; k < 8; k++) {
      const bit = (n[g] >> (7 - k)) & 1;
      const kept = ((m[g] >> (7 - k)) & 1) === 1;
      const x = bitX + g * gw + k * bw;
      let bg = 'white';
      if (kind === 'mask' && bit) bg = 'gold';
      if (kind === 'addr' && reveal && kept) bg = 'lightyellow';
      if (kind === 'net' && compare && kept && bit !== ((compare[g] >> (7 - k)) & 1)) bg = 'mistyrose';
      stroke('gainsboro');
      fill(bg);
      rect(x, y, bw - 1, 26, 2);
      noStroke();
      fill(kind === 'addr' && reveal && !kept ? 'silver' : 'black');
      textAlign(CENTER, CENTER);
      text(bit, x + bw / 2, y + 13);
    }
  }
  textFont('sans-serif');
}

function drawPanel(v, na, nb, x, y, w, h) {
  fill(255, 255, 255, 235);
  stroke('silver');
  rect(x, y, w, h, 10);
  const pad = 10;
  const tw = w - 2 * pad;
  const yy = y + 8;
  noStroke();
  textAlign(LEFT, TOP);
  textSize(16);
  const same = na.join('.') === nb.join('.');
  if (mode === 'explore') {
    fill('navy');
    textStyle(ITALIC);
    text('Are these two on the same network?', x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('Gold bits are the mask\'s 1s; only the address bits above them are kept. ' + na.join('.') + ' and ' + nb.join('.') +
      (same ? ' are equal: same network.' : ' differ: different networks.') + ' Try the mask 255.255.0.0, and change the last number of the second address.',
      x + pad, yy + 22, tw, 20);
    return;
  }
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 7 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 8. ' + (sc >= 7 ? 'Mastery reached.' : 'Mastery is 7 of 8.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('Cases 3 and 4 used the same two addresses with opposite answers. What changed, and what does a mask decide?', x + pad, yy + 24, tw, 20);
    return;
  }
  if (!submitted) {
    fill('navy');
    textStyle(ITALIC);
    text('Are these two on the same network?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('AND each number of the first address with the mask. Choose same or different, type the first network address (like 192.168.1.0), then Submit.', x + pad, yy + 22, tw, 20);
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
    caseIndex = 0;
    results = [];
    submitted = false;
    finished = false;
  } else {
    mode = 'explore';
  }
  sameSelect.selected('choose');
  netInput.value('');
  updateControlStates();
}

function submitAnswer() {
  if (mode !== 'quiz' || submitted || finished) return;
  const s = sameSelect.value();
  const n = parseAddr(netInput.value());
  if (s === 'choose' || !n) return;
  const c = CASES[caseIndex];
  const correct = (s === 'same network') === c.same && n.join('.') === c.net;
  results[caseIndex] = correct;
  feedbackCorrect = correct;
  feedback = correct ? 'Correct: ' + c.why : 'Not quite. They are ' + (c.same ? 'on the same network' : 'on different networks') +
    ', and the network address is ' + c.net + ': ' + c.why;
  submitted = true;
  updateControlStates();
}

function nextCase() {
  if (!submitted) return;
  if (caseIndex === CASES.length - 1) finished = true;
  else { caseIndex++; submitted = false; }
  sameSelect.selected('choose');
  netInput.value('');
  updateControlStates();
}

function setEnabled(el, on) {
  el.elt.disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  const answering = quiz && !submitted && !finished;
  modeButton.html(quiz ? 'Back to explore' : 'Start the 8 cases');
  setEnabled(sameSelect, answering);
  setEnabled(netInput, answering);
  setEnabled(submitButton, answering);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(caseIndex === CASES.length - 1 ? 'See score' : 'Next case');
  for (const el of [aInput, bInput, maskSelect]) setEnabled(el, !quiz);
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
  layoutRow([modeButton, submitButton, nextButton], 10, drawHeight + 8, 10);
  layoutRow([answerLabel, sameSelect, netLabel, netInput], 10, drawHeight + 44, 8);
  layoutRow([aLabel, aInput, bLabel, bInput, maskLabel, maskSelect], 10, drawHeight + 80, 8);
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
