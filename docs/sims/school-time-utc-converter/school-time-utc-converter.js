// Time Zone and UTC Converter - p5.js MicroSim
// CANVAS_HEIGHT: 595
// Calculate the UTC time of a school-local time. US daylight saving: daylight
// time (CDT, UTC-5 / EDT, UTC-4) from the second Sunday in March at 2:00 AM
// until the first Sunday in November at 2:00 AM; standard time (CST, UTC-6 /
// EST, UTC-5) the rest of the year. Two rules for awkward times:
//  1. a local time that does not exist is read with the offset before the gap;
//  2. a local time that happens twice is read as its first occurrence.
// UTC = local time minus the offset. These match Python's zoneinfo with fold=0.

let canvasWidth = 800;
let drawHeight = 480;
let controlHeight = 115;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

const ZONES = {
  'America/Chicago': { std: -6, stdName: 'CST', dstName: 'CDT' },
  'America/New_York': { std: -5, stdName: 'EST', dstName: 'EDT' }
};
const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const ITEMS = [
  { zone: 'America/Chicago', date: '2026-10-20', time: '08:00', ans: ['2026-10-20', '13:00'], why: 'October 20 is before the first Sunday in November, so CDT applies: 8 + 5 = 13.' },
  { zone: 'America/Chicago', date: '2026-12-01', time: '08:00', ans: ['2026-12-01', '14:00'], why: 'December is CST: 8 + 6 = 14. The same wall-clock hour is one hour later in UTC than in October.' },
  { zone: 'America/Chicago', date: '2026-11-01', time: '01:30', ans: ['2026-11-01', '06:30'], why: '1:30 AM happens twice that morning. Rule 2 takes the first, which is CDT: 1:30 + 5 = 6:30.' },
  { zone: 'America/Chicago', date: '2026-11-01', time: '02:30', ans: ['2026-11-01', '08:30'], why: 'After the clocks fall back at 2:00 AM CDT the zone is CST, and 2:30 AM happens once: 2:30 + 6 = 8:30.' },
  { zone: 'America/Chicago', date: '2027-03-14', time: '01:30', ans: ['2027-03-14', '07:30'], why: 'Before the 2:00 AM jump it is still CST: 1:30 + 6 = 7:30.' },
  { zone: 'America/Chicago', date: '2027-03-14', time: '02:30', ans: ['2027-03-14', '08:30'], why: '2:30 AM does not exist that day. Rule 1 uses the offset from before the gap, CST: 2:30 + 6 = 8:30.' },
  { zone: 'America/Chicago', date: '2027-03-14', time: '03:30', ans: ['2027-03-14', '08:30'], why: 'After the jump it is CDT: 3:30 + 5 = 8:30, the same instant as item 6.' },
  { zone: 'America/New_York', date: '2026-10-20', time: '09:00', ans: ['2026-10-20', '13:00'], why: 'New York is on EDT: 9 + 4 = 13. It is the same instant as item 1: the same instant is a different wall-clock time in a different zone.' }
];

let mode = 'explore';
let itemIndex = 0;
let submitted = false;
let finished = false;
let results = [];
let feedback = '';
let feedbackCorrect = false;

let modeButton, submitButton, nextButton, uDateLabel, uDateInput, uTimeLabel, uTimeInput;
let zoneLabel, zoneSelect, lDateLabel, lDateInput, lTimeLabel, lTimeInput;

// ---------- the zone rules ----------

const pad2 = n => String(n).padStart(2, '0');
function dayNum(s) {
  const [y, m, d] = s.split('-').map(Number);
  return Date.UTC(y, m - 1, d) / 86400000;
}
function ymd(dn) {
  const d = new Date(dn * 86400000);
  return d.getUTCFullYear() + '-' + pad2(d.getUTCMonth() + 1) + '-' + pad2(d.getUTCDate());
}
function nthSunday(y, m, n) {
  const first = Date.UTC(y, m - 1, 1) / 86400000;
  const dow = new Date(first * 86400000).getUTCDay();
  return first + ((7 - dow) % 7) + 7 * (n - 1);
}

// offset in hours for a local date (day number) and minute of the day,
// with a note when the time does not exist or happens twice
function offsetFor(zone, dn, mins) {
  const z = ZONES[zone];
  const y = new Date(dn * 86400000).getUTCFullYear();
  const start = nthSunday(y, 3, 2);
  const end = nthSunday(y, 11, 1);
  const dst = { off: z.std + 1, name: z.dstName, note: '' };
  const std = { off: z.std, name: z.stdName, note: '' };
  if (dn > start && dn < end) return dst;
  if (dn === start) {
    if (mins < 120) return std;
    if (mins < 180) return { off: z.std, name: z.stdName, note: 'gap' };
    return dst;
  }
  if (dn === end) {
    if (mins < 60) return dst;
    if (mins < 120) return { off: z.std + 1, name: z.dstName, note: 'twice' };
    return std;
  }
  return std;
}

function toUtc(zone, dateStr, timeStr) {
  const dn = dayNum(dateStr);
  const [h, m] = timeStr.split(':').map(Number);
  const mins = h * 60 + m;
  const o = offsetFor(zone, dn, mins);
  const u = dn * 1440 + mins - o.off * 60;
  const ud = Math.floor(u / 1440);
  const um = u - ud * 1440;
  return { date: ymd(ud), time: pad2(Math.floor(um / 60)) + ':' + pad2(um % 60), o: o, dn: dn, mins: mins };
}

function currentInput() {
  if (mode === 'quiz') return ITEMS[min(itemIndex, 7)];
  return { zone: zoneSelect.value(), date: lDateInput.value() || '2026-10-20', time: lTimeInput.value() || '08:00' };
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
  text('Time Zone and UTC Converter', canvasWidth / 2, 10);
  textSize(16);
  fill('dimgray');
  let status;
  if (mode === 'explore') status = 'Explore: pick a zone, a local date and a local time';
  else if (finished) status = 'All 8 items done   |   Score: ' + countCorrect() + ' of 8';
  else status = 'Item ' + (itemIndex + 1) + ' of 8   |   Score: ' + countCorrect() + ' of 8';
  text(status, canvasWidth / 2, 42);

  const inp = currentInput();
  const r = toUtc(inp.zone, inp.date, inp.time);
  const reveal = mode === 'explore' || submitted;
  drawCards(inp, r, reveal, 72);
  drawDayStrip(inp.zone, r.dn, r.mins, reveal, 196);
  drawRules(margin, 270, canvasWidth - 2 * margin);
  drawPanel(r, reveal, margin, 368, canvasWidth - 2 * margin, drawHeight - 376);
}

function drawCards(inp, r, reveal, y) {
  const gap = 60;
  const cw = (canvasWidth - 2 * margin - gap) / 2;
  const wd = WEEKDAYS[new Date(r.dn * 86400000).getUTCDay()];
  const cards = [
    { x: margin, title: 'Local time', l1: wd + ' ' + inp.date + '  ' + inp.time, l2: inp.zone },
    { x: margin + cw + gap, title: 'UTC', l1: reveal ? r.date + '  ' + r.time : '?', l2: reveal ? 'offset ' + r.o.name + ' (UTC' + (r.o.off < 0 ? '' : '+') + r.o.off + ')' : 'hidden until you submit' }
  ];
  for (const c of cards) {
    fill('white');
    stroke('steelblue');
    rect(c.x, y, cw, 100, 10);
    noStroke();
    fill('navy');
    textAlign(LEFT, TOP);
    textSize(15);
    textStyle(BOLD);
    text(c.title, c.x + 12, y + 8);
    textStyle(NORMAL);
    fill('black');
    textSize(22);
    text(c.l1, c.x + 12, y + 32);
    fill('dimgray');
    textSize(15);
    text(c.l2, c.x + 12, y + 68);
  }
  stroke('gray');
  strokeWeight(2);
  const ax = margin + cw + 8;
  line(ax, y + 50, ax + gap - 18, y + 50);
  noStroke();
  fill('gray');
  triangle(ax + gap - 14, y + 50, ax + gap - 24, y + 44, ax + gap - 24, y + 56);
  strokeWeight(1);
}

// the 24 hours of the local day, colored by the offset in force
function drawDayStrip(zone, dn, mins, reveal, y) {
  const x0 = margin;
  const w = canvasWidth - 2 * margin;
  const cw = w / 24;
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(14);
  text('The local day, hour by hour (offset in force at each hour)', x0, y);
  for (let hh = 0; hh < 24; hh++) {
    const o = offsetFor(zone, dn, hh * 60);
    let col = o.name.endsWith('DT') ? 'moccasin' : 'lightsteelblue';
    if (o.note === 'gap') col = 'whitesmoke';
    if (o.note === 'twice') col = 'plum';
    stroke('white');
    fill(col);
    rect(x0 + hh * cw, y + 20, cw, 26);
    noStroke();
    fill('black');
    textAlign(CENTER, CENTER);
    textSize(11);
    text(hh, x0 + (hh + 0.5) * cw, y + 33);
  }
  if (reveal || mode === 'explore') {
    const mx = x0 + (mins / 60) * cw;
    stroke('crimson');
    strokeWeight(3);
    line(mx, y + 16, mx, y + 50);
    strokeWeight(1);
  }
  noStroke();
  textAlign(LEFT, TOP);
  textSize(13);
  const z = ZONES[zone];
  const keys = [['moccasin', z.dstName + ' (daylight)'], ['lightsteelblue', z.stdName + ' (standard)'], ['plum', 'happens twice'], ['whitesmoke', 'does not exist']];
  let lx = x0;
  for (const [c, t] of keys) {
    fill(c);
    stroke('silver');
    rect(lx, y + 52, 12, 12);
    noStroke();
    fill('dimgray');
    text(t, lx + 16, y + 51);
    lx += textWidth(t) + 34;
  }
}

function drawRules(x, y, w) {
  fill(255, 255, 255, 235);
  stroke('silver');
  rect(x, y, w, 90, 8);
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(14);
  let yy = y + 6;
  yy = drawWrapped('Rule 1: a local time that does not exist is read with the offset in force before the gap. Rule 2: a local time that happens twice is read as its first occurrence.', x + 8, yy, w - 16, 17);
  fill('dimgray');
  drawWrapped('Chicago: CDT (UTC-5) from the second Sunday in March, 2:00 AM, to the first Sunday in November, 2:00 AM; otherwise CST (UTC-6). New York: EDT (UTC-4) and EST (UTC-5) on the same dates.', x + 8, yy + 2, w - 16, 17);
}

function drawPanel(r, reveal, x, y, w, h) {
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
    text('What time is this in UTC?', x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    let note = '';
    if (r.o.note === 'gap') note = ' This local time does not exist (the clocks jump from 2:00 to 3:00), so rule 1 uses the standard offset from before the gap.';
    if (r.o.note === 'twice') note = ' This local time happens twice (the clocks fall back from 2:00 to 1:00), so rule 2 takes the first, daylight, one.';
    drawWrapped('Offset ' + r.o.name + ' (UTC' + r.o.off + '): UTC = local + ' + (-r.o.off) + ' hours = ' + r.date + ' ' + r.time + '.' + note, x + pad, yy + 22, tw, 20);
    return;
  }
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 7 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 8. ' + (sc >= 7 ? 'Mastery reached.' : 'Mastery is 7 of 8.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('Items 6 and 7 are two different local times that are the same instant. How can that happen?', x + pad, yy + 24, tw, 20);
    return;
  }
  if (!submitted) {
    fill('navy');
    textStyle(ITALIC);
    text('What time is this in UTC?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Decide which offset is in force on that date (check the rules for awkward times), then type the UTC date (YYYY-MM-DD) and time (24-hour HH:MM) and Submit.', x + pad, yy + 22, tw, 20);
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
    itemIndex = 0;
    results = [];
    submitted = false;
    finished = false;
  } else {
    mode = 'explore';
  }
  uDateInput.value('');
  uTimeInput.value('');
  updateControlStates();
}

// "13:00" or "9:05" as HH:MM; null when unreadable
function readTime(s) {
  const m = s.trim().match(/^(\d{1,2}):(\d{2})$/);
  return m && Number(m[1]) < 24 && Number(m[2]) < 60 ? pad2(Number(m[1])) + ':' + m[2] : null;
}

function submitAnswer() {
  if (mode !== 'quiz' || submitted || finished) return;
  const d = uDateInput.value().trim();
  const t = readTime(uTimeInput.value());
  if (!/^\d{4}-\d{2}-\d{2}$/.test(d) || !t) return;
  const it = ITEMS[itemIndex];
  const correct = d === it.ans[0] && t === it.ans[1];
  results[itemIndex] = correct;
  feedbackCorrect = correct;
  feedback = correct ? 'Correct: ' + it.why : 'Not quite. The UTC time is ' + it.ans[0] + ' ' + it.ans[1] + ': ' + it.why;
  submitted = true;
  updateControlStates();
}

function nextItem() {
  if (!submitted) return;
  if (itemIndex === ITEMS.length - 1) finished = true;
  else { itemIndex++; submitted = false; }
  uDateInput.value('');
  uTimeInput.value('');
  updateControlStates();
}

// ---------- setup and controls ----------

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  modeButton = createButton('Start the 8 items');
  modeButton.mousePressed(toggleMode);
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next item');
  nextButton.mousePressed(nextItem);
  uDateLabel = createSpan('UTC date:');
  uDateInput = createInput('');
  uDateInput.size(120);
  uDateInput.attribute('placeholder', 'YYYY-MM-DD');
  uTimeLabel = createSpan('UTC time:');
  uTimeInput = createInput('');
  uTimeInput.size(70);
  uTimeInput.attribute('placeholder', 'HH:MM');
  uTimeInput.elt.addEventListener('keydown', e => { if (e.key === 'Enter') submitAnswer(); });
  zoneLabel = createSpan('Zone:');
  zoneSelect = createSelect();
  for (const z of Object.keys(ZONES)) zoneSelect.option(z);
  lDateLabel = createSpan('Local date:');
  lDateInput = createInput('2026-10-20', 'date');
  lTimeLabel = createSpan('Local time:');
  lTimeInput = createInput('08:00', 'time');
  for (const el of [modeButton, submitButton, nextButton, uDateLabel, uDateInput, uTimeLabel, uTimeInput, zoneLabel, zoneSelect, lDateLabel, lDateInput, lTimeLabel, lTimeInput]) {
    el.style('font-size', '16px');
  }

  positionControls();
  updateControlStates();

  describe('Two cards: a school-local date and time in a chosen time zone, and the same instant in UTC with the offset in force. Below them, the 24 hours of the local day are colored by offset, showing on daylight-saving change days the hour that does not exist or happens twice. Rules for those awkward times are always shown. An eight-item quiz asks for the UTC date and time of eight local times.', LABEL);
}

function setEnabled(el, on) {
  el.elt.disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  const answering = quiz && !submitted && !finished;
  modeButton.html(quiz ? 'Back to explore' : 'Start the 8 items');
  setEnabled(uDateInput, answering);
  setEnabled(uTimeInput, answering);
  setEnabled(submitButton, answering);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(itemIndex === ITEMS.length - 1 ? 'See score' : 'Next item');
  for (const el of [zoneSelect, lDateInput, lTimeInput]) setEnabled(el, !quiz);
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
  layoutRow([uDateLabel, uDateInput, uTimeLabel, uTimeInput], 10, drawHeight + 44, 8);
  layoutRow([zoneLabel, zoneSelect, lDateLabel, lDateInput, lTimeLabel, lTimeInput], 10, drawHeight + 80, 8);
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
