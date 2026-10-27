// ICS Line Parser Stepper - p5.js MicroSim
// CANVAS_HEIGHT: 600
// Execute the iCalendar parsing rules of Chapter 16 (server/ics_parser.py) on
// a small feed adapted from the Cedar Ridge calendar. Rules:
//  * a line that starts with a space or tab continues the line before it
//    (that one character is dropped), before any other rule applies;
//  * everything between BEGIN:VTIMEZONE and END:VTIMEZONE is skipped;
//  * a DTSTART with TZID is local time in that zone, converted to UTC;
//  * VALUE=DATE is an all-day date; an all-day DTEND is exclusive, so the
//    last day is the end date minus one day;
//  * a title starting TEST:, DUE: or NO SCHOOL: sets the category.

let canvasWidth = 800;
let drawHeight = 520;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

const ACTIONS = {
  A: 'Start skipping a time-zone definition',
  B: 'Skip: it is inside a time-zone definition',
  C: 'Stop skipping',
  D: 'Start a new event',
  E: 'Set the title',
  F: 'Join onto the line before it (a fold)',
  G: 'Set a timed start, converted to UTC',
  H: 'Set an all-day first day',
  I: 'Set the last day (the end date minus one day)',
  J: 'Set the location',
  K: 'Finish the event'
};
const FEED = [
  { line: 'BEGIN:VTIMEZONE', answer: 'A', why: 'Everything until the matching END belongs to a time-zone definition.' },
  { line: 'DTSTART:19701101T020000', answer: 'B', why: 'This DTSTART describes a rule of the zone, not an event, so it is skipped.' },
  { line: 'END:VTIMEZONE', answer: 'C', why: 'The zone definition is over; events count again.' },
  { line: 'BEGIN:VEVENT', answer: 'D', why: 'A new event starts with empty fields.' },
  { line: 'SUMMARY:TEST: Biology Unit 2 - Gene', answer: 'E', why: 'The title so far is "TEST: Biology Unit 2 - Gene". The second colon belongs to the value.' },
  { line: ' tics', answer: 'F', why: 'A line that starts with a space continues the line before it, and that one space is dropped, even in the middle of a word. The title becomes "TEST: Biology Unit 2 - Genetics".' },
  { line: 'DTSTART;TZID=America/Chicago:20261110T100200', answer: 'G', why: '10:02 in Chicago on Nov 10 is CST, UTC minus 6 hours, so 16:02 UTC.' },
  { line: 'LOCATION:Lab 130', answer: 'J', why: 'Plain text property.' },
  { line: 'END:VEVENT', answer: 'K', why: 'The event is complete. Its title begins "TEST:", so its category is test, and its course is Biology.' },
  { line: 'BEGIN:VEVENT', answer: 'D', why: 'A second event starts.' },
  { line: 'SUMMARY:NO SCHOOL: Thanksgiving Break', answer: 'E', why: 'The prefix "NO SCHOOL:" will make its category no-school.' },
  { line: 'DTSTART;VALUE=DATE:20261125', answer: 'H', why: 'VALUE=DATE means all-day: the date is Nov 25 with no time and no time zone.' },
  { line: 'DTEND;VALUE=DATE:20261128', answer: 'I', why: 'The end date is exclusive, so the last day is Nov 27.' },
  { line: 'END:VEVENT', answer: 'K', why: 'The event is complete: Nov 25 to Nov 27.' }
];
const COURSES = ['Algebra II', 'English 10', 'Biology', 'World History', 'Spanish II', 'Physical Computing'];

let states = [];          // parser state after each line (states[0] = before line 1)
let parserActions = [];   // the action the parser itself took on each line
let mode = 'explore';
let step = 0;             // lines processed
let submitted = false;
let finished = false;
let results = [];
let choices = [];
let feedback = '';
let feedbackCorrect = false;

let modeButton, actionLabel, actionSelect, submitButton, nextButton, stepButton, resetButton;

// ---------- the parser ----------

const pad2 = n => String(n).padStart(2, '0');
function ymd(dn) {
  const d = new Date(dn * 86400000);
  return d.getUTCFullYear() + '-' + pad2(d.getUTCMonth() + 1) + '-' + pad2(d.getUTCDate());
}
function dayNumOf(y, m, d) { return Date.UTC(y, m - 1, d) / 86400000; }
// the n-th Sunday (1-based) of a month, as a day number
function nthSunday(y, m, n) {
  const first = dayNumOf(y, m, 1);
  const dow = new Date(first * 86400000).getUTCDay();
  return first + ((7 - dow) % 7) + 7 * (n - 1);
}
// America/Chicago offset in hours for a local date and minute of the day
function chicagoOffset(dn, mins) {
  const y = new Date(dn * 86400000).getUTCFullYear();
  const start = nthSunday(y, 3, 2);
  const end = nthSunday(y, 11, 1);
  if (dn > start && dn < end) return -5;
  if (dn === start) return mins >= 180 ? -5 : -6;
  if (dn === end) return mins < 120 ? -5 : -6;
  return -6;
}

function categoryOf(title) {
  const m = title.match(/^\s*(TEST|DUE|NO\s+SCHOOL)\s*:/i);
  if (!m) return 'event';
  const k = m[1].toUpperCase().replace(/\s+/g, ' ');
  return k === 'TEST' ? 'test' : k === 'DUE' ? 'due' : 'no-school';
}
function courseOf(title) {
  const rest = title.replace(/^\s*(TEST|DUE|NO\s+SCHOOL)\s*:\s*/i, '');
  return COURSES.slice().sort((a, b) => b.length - a.length).find(c => rest.toLowerCase().startsWith(c.toLowerCase())) || null;
}

function copyState(s) {
  return { inZone: s.inZone, cur: s.cur ? Object.assign({}, s.cur) : null, lastKey: s.lastKey, done: s.done.map(e => Object.assign({}, e)) };
}

function runParser() {
  let s = { inZone: false, cur: null, lastKey: null, done: [] };
  states = [copyState(s)];
  parserActions = [];
  for (const f of FEED) {
    s = copyState(s);
    const ln = f.line;
    let act;
    if (ln.startsWith(' ') || ln.startsWith('\t')) {
      act = 'F';
      if (s.cur && s.lastKey === 'SUMMARY') s.cur.title += ln.slice(1);
    } else if (s.inZone) {
      if (ln === 'END:VTIMEZONE') { s.inZone = false; act = 'C'; } else act = 'B';
    } else if (ln === 'BEGIN:VTIMEZONE') { s.inZone = true; act = 'A'; }
    else if (ln === 'BEGIN:VEVENT') { s.cur = {}; act = 'D'; }
    else if (ln === 'END:VEVENT') {
      const e = s.cur;
      e.category = categoryOf(e.title);
      e.course = courseOf(e.title);
      s.done.push(e);
      s.cur = null;
      act = 'K';
    } else {
      const colon = ln.indexOf(':');
      const head = ln.slice(0, colon).split(';');
      const name = head[0];
      const params = head.slice(1);
      const value = ln.slice(colon + 1);
      s.lastKey = name;
      if (name === 'SUMMARY') { s.cur.title = value; act = 'E'; }
      else if (name === 'LOCATION') { s.cur.location = value; act = 'J'; }
      else if (params.includes('VALUE=DATE')) {
        const dn = dayNumOf(+value.slice(0, 4), +value.slice(4, 6), +value.slice(6, 8));
        if (name === 'DTSTART') { s.cur.first = ymd(dn); act = 'H'; }
        else { s.cur.last = ymd(dn - 1); act = 'I'; }
      } else if (params.some(p => p.startsWith('TZID='))) {
        const dn = dayNumOf(+value.slice(0, 4), +value.slice(4, 6), +value.slice(6, 8));
        const mins = +value.slice(9, 11) * 60 + +value.slice(11, 13);
        const off = chicagoOffset(dn, mins);
        const utc = dn * 1440 + mins - off * 60;
        const ud = Math.floor(utc / 1440);
        const um = utc - ud * 1440;
        s.cur.startUtc = ymd(ud) + ' ' + pad2(Math.floor(um / 60)) + ':' + pad2(um % 60) + ' UTC';
        s.cur.local = pad2(Math.floor(mins / 60)) + ':' + pad2(mins % 60) + ' ' + (off === -6 ? 'CST' : 'CDT');
        act = 'G';
      }
    }
    if (act === 'D' || act === 'K') s.lastKey = null;   // a fold never continues BEGIN or END
    parserActions.push(act);
    states.push(s);
  }
}

// ---------- setup and drawing ----------

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);
  runParser();

  modeButton = createButton('Start the 14 lines');
  modeButton.mousePressed(toggleMode);
  actionLabel = createSpan('Action:');
  actionSelect = createSelect();
  actionSelect.option('choose');
  for (const k of Object.keys(ACTIONS)) actionSelect.option(k + ': ' + ACTIONS[k], k);
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next line');
  nextButton.mousePressed(nextLine);
  stepButton = createButton('Step');
  stepButton.mousePressed(() => { if (step < FEED.length) step++; updateControlStates(); });
  resetButton = createButton('Back to start');
  resetButton.mousePressed(() => { step = 0; updateControlStates(); });
  for (const el of [modeButton, actionLabel, actionSelect, submitButton, nextButton, stepButton, resetButton]) el.style('font-size', '16px');

  positionControls();
  updateControlStates();

  describe('Fourteen lines of an iCalendar feed listed on the left, a list of eleven parser actions A to K on the right, and the parser state below it: whether it is inside a time-zone definition, the event being built, and the finished events. The learner steps through the parse, or chooses the action for each line in turn and sees the state update.', LABEL);
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
  text('ICS Line Parser Stepper', canvasWidth / 2, 10);
  textSize(16);
  fill('dimgray');
  let status;
  if (mode === 'explore') status = 'Explore: a feed adapted from the Cedar Ridge feed, ' + step + ' of 14 lines parsed';
  else if (finished) status = 'All 14 lines done   |   Score: ' + countCorrect() + ' of 14';
  else status = 'Line ' + (step + 1) + ' of 14   |   Score: ' + countCorrect() + ' of 14';
  text(status, canvasWidth / 2, 42);

  const split = canvasWidth * 0.56;
  drawFeed(margin, 70, split - margin - 10);
  drawActions(split, 70, canvasWidth - split - margin);
  drawState(states[step], split, 284, canvasWidth - split - margin, 140);
  drawPanel(margin, 434, canvasWidth - 2 * margin, drawHeight - 442);
}

function drawFeed(x, y, w) {
  const rh = 25;
  textFont('monospace');
  let ts = 14;
  textSize(ts);
  while (textWidth(FEED[6].line) > w - 62 && ts > 10) textSize(--ts);
  for (let i = 0; i < FEED.length; i++) {
    const yy = y + i * rh;
    const current = i === step && !(mode === 'quiz' && finished);
    if (current) {
      noStroke();
      fill('lightyellow');
      stroke('gold');
      rect(x - 2, yy - 2, w + 4, rh - 2, 4);
    }
    noStroke();
    // the action tag, once a line is done
    if (i < step) {
      let tag = parserActions[i];
      let col = 'dimgray';
      if (mode === 'quiz') { tag = choices[i]; col = results[i] ? 'darkgreen' : 'firebrick'; }
      fill(col);
      circle(x + 10, yy + rh / 2 - 1, 20);
      fill('white');
      textAlign(CENTER, CENTER);
      text(tag, x + 10, yy + rh / 2 - 1);
      if (mode === 'quiz' && !results[i]) {
        fill('darkgreen');
        textAlign(LEFT, CENTER);
        text(parserActions[i], x + 22, yy + rh / 2 - 1);
      }
    }
    fill('dimgray');
    textAlign(RIGHT, CENTER);
    text(i + 1, x + 52, yy + rh / 2 - 1);
    fill(i < step ? 'black' : (current ? 'midnightblue' : 'gray'));
    textAlign(LEFT, CENTER);
    const shown = FEED[i].line.startsWith(' ') ? '\u2423' + FEED[i].line.slice(1) : FEED[i].line;
    text(shown, x + 60, yy + rh / 2 - 1);
  }
  textFont('sans-serif');
}

function drawActions(x, y, w) {
  fill(255, 255, 255, 235);
  stroke('silver');
  rect(x, y, w, 206, 8);
  noStroke();
  textAlign(LEFT, TOP);
  textSize(14);
  fill('black');
  textStyle(BOLD);
  text('Actions', x + 8, y + 5);
  textStyle(NORMAL);
  textSize(12);
  let yy = y + 24;
  for (const k of Object.keys(ACTIONS)) {
    let t = k + '  ' + ACTIONS[k];
    while (textWidth(t) > w - 14 && t.length > 6) t = t.slice(0, -1);
    text(t, x + 8, yy);
    yy += 16.5;
  }
}

function drawState(s, x, y, w, h) {
  fill('honeydew');
  stroke('seagreen');
  rect(x, y, w, h, 8);
  noStroke();
  textAlign(LEFT, TOP);
  textSize(14);
  fill('darkgreen');
  textStyle(BOLD);
  text('Parser state', x + 8, y + 5);
  textStyle(NORMAL);
  fill('black');
  textSize(13);
  let yy = y + 24;
  yy = drawWrapped('In a time-zone definition: ' + (s.inZone ? 'yes, skipping' : 'no'), x + 8, yy, w - 16, 16);
  if (s.cur) {
    const c = s.cur;
    const bits = ['title "' + (c.title || '') + '"'];
    if (c.startUtc) bits.push('start ' + c.startUtc + ' (' + c.local + ')');
    if (c.first) bits.push('all-day from ' + c.first);
    if (c.last) bits.push('last day ' + c.last);
    if (c.location) bits.push('location ' + c.location);
    yy = drawWrapped('Building: ' + bits.join('; '), x + 8, yy + 2, w - 16, 16);
  } else {
    yy = drawWrapped('Building: no event', x + 8, yy + 2, w - 16, 16);
  }
  for (const e of s.done) {
    const when = e.startUtc ? e.startUtc : 'all-day ' + e.first + ' to ' + e.last;
    yy = drawWrapped('Done: ' + e.title + ', ' + e.category + (e.course ? ', ' + e.course : '') + ', ' + when + (e.location ? ', ' + e.location : ''),
      x + 8, yy + 2, w - 16, 16);
  }
}

function drawPanel(x, y, w, h) {
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
    text('What does the parser do with this line?', x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped(step === 0 ? 'Press Step to parse one line. The circle shows the action taken, and the state box on the right updates.' :
      'Line ' + step + ' (' + parserActions[step - 1] + ': ' + ACTIONS[parserActions[step - 1]] + '): ' + FEED[step - 1].why, x + pad, yy + 22, tw, 19);
    return;
  }
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 12 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 14. ' + (sc >= 12 ? 'Mastery reached.' : 'Mastery is 12 of 14.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('Lines 2 and 6 look like an event and a new property, but are not. What tells the parser so?', x + pad, yy + 24, tw, 19);
    return;
  }
  if (!submitted) {
    fill('navy');
    textStyle(ITALIC);
    text('What does the parser do with this line?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Read the highlighted line and the parser state, choose an action from the menu, then Submit. One attempt per line.', x + pad, yy + 22, tw, 19);
    return;
  }
  fill(feedbackCorrect ? 'darkgreen' : 'firebrick');
  textStyle(BOLD);
  drawWrapped(feedback, x + pad, yy, tw, 19);
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
    results = [];
    choices = [];
    submitted = false;
    finished = false;
  } else {
    mode = 'explore';
  }
  step = 0;
  actionSelect.selected('choose');
  updateControlStates();
}

function submitAnswer() {
  if (mode !== 'quiz' || submitted || finished) return;
  const c = actionSelect.value();
  if (c === 'choose') return;
  const f = FEED[step];
  const correct = c === f.answer;
  results[step] = correct;
  choices[step] = c;
  feedbackCorrect = correct;
  feedback = correct ? 'Correct: ' + f.why : 'Not quite. The parser does this: ' + f.answer + ', ' + ACTIONS[f.answer].toLowerCase() + '. ' + f.why;
  submitted = true;
  step++;            // the parser applies the correct action
  updateControlStates();
}

function nextLine() {
  if (!submitted) return;
  if (step >= FEED.length) finished = true;
  submitted = false;
  actionSelect.selected('choose');
  updateControlStates();
}

function setEnabled(el, on) {
  el.elt.disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  const answering = quiz && !submitted && !finished;
  modeButton.html(quiz ? 'Back to explore' : 'Start the 14 lines');
  setEnabled(actionSelect, answering);
  setEnabled(submitButton, answering);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(step >= FEED.length ? 'See score' : 'Next line');
  setEnabled(stepButton, !quiz && step < FEED.length);
  setEnabled(resetButton, !quiz && step > 0);
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
  layoutRow([modeButton, actionLabel, actionSelect], 10, drawHeight + 8, 8);
  layoutRow([submitButton, nextButton, stepButton, resetButton], 10, drawHeight + 44, 10);
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
