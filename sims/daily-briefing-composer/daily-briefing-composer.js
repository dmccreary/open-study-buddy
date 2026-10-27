// Daily Briefing Composer - p5.js MicroSim
// CANVAS_HEIGHT: 635
// Apply the daily briefing rules of Chapter 16 to the Cedar Ridge calendar.
// The composer below is a port of compose.daily_briefing() and query.py in
// src/chapters/16-school-agent-calendar/server, with agent.toml's wording:
//   Today: today's test, due, event, sports or academic events, up to max_items
//   Next test: the first test after today that starts within upcoming_days
//   Due soon: due events after today within upcoming_days, up to max_items
// Weekends and no-school days get no briefing. The briefing is composed at
// 7:30 AM school time. Events are the real Cedar Ridge 2026-2027 calendar
// (docs/schools/cedar-ridge-high-school/events.json).

let canvasWidth = 800;
let drawHeight = 520;
let controlHeight = 115;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

// [id, title, category, first day, last day, start, end, location, course]
const EVENTS_RAW = [
  ["001", "First Day of School", "academic", "2026-08-25", "2026-08-25", null, null, null, null],
  ["002", "DUE: Physical Computing signed lab-safety form", "due", "2026-08-28", "2026-08-28", null, null, null, "Physical Computing"],
  ["003", "NO SCHOOL: Labor Day", "no-school", "2026-09-07", "2026-09-07", null, null, null, null],
  ["004", "Back-to-School Night", "event", "2026-09-10", "2026-09-10", "18:30", "20:00", "Auditorium", null],
  ["005", "Homecoming Week", "event", "2026-09-14", "2026-09-18", null, null, null, null],
  ["006", "TEST: Algebra II Unit 1 - Linear Review", "test", "2026-09-15", "2026-09-15", "08:00", null, null, "Algebra II"],
  ["007", "Homecoming Football vs. Lakeside Lions", "sports", "2026-09-18", "2026-09-18", "19:00", "21:00", "Griffin Field", null],
  ["008", "Homecoming Dance", "event", "2026-09-19", "2026-09-19", "19:00", "22:00", "Main Gym", null],
  ["009", "TEST: Biology Unit 1 - Cells", "test", "2026-09-22", "2026-09-22", "08:00", null, null, "Biology"],
  ["010", "DUE: World History river-valley map project", "due", "2026-09-25", "2026-09-25", null, null, null, "World History"],
  ["011", "TEST: Algebra II Unit 2 - Functions", "test", "2026-09-29", "2026-09-29", "08:00", null, null, "Algebra II"],
  ["012", "DUE: Spanish II vocabulary portfolio", "due", "2026-10-02", "2026-10-02", null, null, null, "Spanish II"],
  ["013", "TEST: Spanish II Unit 2 oral quiz", "test", "2026-10-06", "2026-10-06", "12:39", null, null, "Spanish II"],
  ["014", "TEST: World History Unit 1 - Ancient River Valleys", "test", "2026-10-08", "2026-10-08", "11:03", null, null, "World History"],
  ["015", "Fall Picture Day", "event", "2026-10-09", "2026-10-09", null, null, "Library", null],
  ["016", "NO SCHOOL: Fall Break", "no-school", "2026-10-15", "2026-10-16", null, null, null, null],
  ["017", "Picture Retake Day", "event", "2026-10-19", "2026-10-19", null, null, "Library", null],
  ["018", "TEST: Algebra II Unit 3 - Quadratics", "test", "2026-10-20", "2026-10-20", "08:00", null, null, "Algebra II"],
  ["019", "DUE: English 10 personal narrative draft", "due", "2026-10-21", "2026-10-21", null, null, null, "English 10"],
  ["020", "DUE: Biology osmosis lab report", "due", "2026-10-22", "2026-10-22", null, null, null, "Biology"],
  ["021", "Football vs. Eastbrook Eagles", "sports", "2026-10-23", "2026-10-23", "19:00", "21:00", "Griffin Field", null],
  ["022", "Maker Club: Study Buddy Build Night", "event", "2026-10-26", "2026-10-26", "15:30", "17:00", "Room 214", null],
  ["023", "PSAT 10", "event", "2026-10-28", "2026-10-28", "08:00", "11:30", "Main Gym", null],
  ["024", "End of Quarter 1", "academic", "2026-10-30", "2026-10-30", null, null, null, null],
  ["025", "Spirit Day: Green and Gold", "event", "2026-10-30", "2026-10-30", null, null, null, null],
  ["026", "NO SCHOOL: Election Day / Staff Development", "no-school", "2026-11-03", "2026-11-03", null, null, null, null],
  ["027", "Quarter 1 Report Cards Posted", "academic", "2026-11-05", "2026-11-05", null, null, null, null],
  ["028", "Maker Club: Study Buddy Build Night", "event", "2026-11-09", "2026-11-09", "15:30", "17:00", "Room 214", null],
  ["029", "TEST: Biology Unit 2 - Genetics", "test", "2026-11-10", "2026-11-10", "10:02", null, null, "Biology"],
  ["030", "Veterans Day Assembly", "event", "2026-11-11", "2026-11-11", "09:00", "09:45", "Auditorium", null],
  ["031", "DUE: World History primary-source essay", "due", "2026-11-12", "2026-11-12", null, null, null, "World History"],
  ["032", "Fall Play: Our Town", "event", "2026-11-13", "2026-11-13", "19:00", "21:00", "Auditorium", null],
  ["033", "TEST: Spanish II Unit 3", "test", "2026-11-17", "2026-11-17", "12:39", null, null, "Spanish II"],
  ["034", "Parent-Teacher Conferences", "event", "2026-11-19", "2026-11-19", "16:00", "20:00", "Main Hallway", null],
  ["035", "DUE: Algebra II Parabola in the Wild project", "due", "2026-11-20", "2026-11-20", null, null, null, "Algebra II"],
  ["036", "Maker Club: Study Buddy Build Night", "event", "2026-11-23", "2026-11-23", "15:30", "17:00", "Room 214", null],
  ["037", "NO SCHOOL: Thanksgiving Break", "no-school", "2026-11-25", "2026-11-27", null, null, null, null],
  ["038", "TEST: Algebra II Unit 4 - Polynomials", "test", "2026-12-01", "2026-12-01", "08:00", null, null, "Algebra II"],
  ["039", "DUE: Biology genetics poster", "due", "2026-12-03", "2026-12-03", null, null, null, "Biology"],
  ["040", "TEST: World History Unit 2 - Classical Civilizations", "test", "2026-12-08", "2026-12-08", "11:03", null, null, "World History"],
  ["041", "Winter Concert", "event", "2026-12-10", "2026-12-10", "19:00", "20:30", "Auditorium", null],
  ["042", "DUE: English 10 personal narrative final", "due", "2026-12-11", "2026-12-11", null, null, null, "English 10"],
  ["043", "Early Dismissal 12:00 PM (Winter Break Begins)", "academic", "2026-12-18", "2026-12-18", null, null, null, null],
  ["044", "NO SCHOOL: Winter Break", "no-school", "2026-12-21", "2027-01-01", null, null, null, null],
  ["045", "School Resumes", "academic", "2027-01-04", "2027-01-04", null, null, null, null],
  ["046", "DUE: Spanish II skit script", "due", "2027-01-07", "2027-01-07", null, null, null, "Spanish II"],
  ["047", "DUE: Physical Computing sensor-project writeup", "due", "2027-01-08", "2027-01-08", null, null, null, "Physical Computing"],
  ["048", "TEST: Algebra II Semester 1 Final", "test", "2027-01-12", "2027-01-12", "08:00", null, null, "Algebra II"],
  ["049", "TEST: English 10 Semester 1 Final", "test", "2027-01-13", "2027-01-13", "08:00", null, null, "English 10"],
  ["050", "TEST: Biology Semester 1 Final", "test", "2027-01-14", "2027-01-14", "08:00", null, null, "Biology"],
  ["051", "End of Semester 1", "academic", "2027-01-15", "2027-01-15", null, null, null, null],
  ["052", "TEST: World History Semester 1 Final", "test", "2027-01-15", "2027-01-15", "08:00", null, null, "World History"],
  ["053", "TEST: Spanish II Semester 1 Final", "test", "2027-01-15", "2027-01-15", "10:30", null, null, "Spanish II"],
  ["054", "NO SCHOOL: Martin Luther King Jr. Day", "no-school", "2027-01-18", "2027-01-18", null, null, null, null],
  ["055", "Semester 2 Begins", "academic", "2027-01-19", "2027-01-19", null, null, null, null],
  ["056", "TEST: Biology Unit 3 - Cell Energy", "test", "2027-01-28", "2027-01-28", "10:02", null, null, "Biology"],
  ["057", "DUE: English 10 research paper outline", "due", "2027-02-04", "2027-02-04", null, null, null, "English 10"],
  ["058", "TEST: Algebra II Unit 5 - Exponentials", "test", "2027-02-09", "2027-02-09", "08:00", null, null, "Algebra II"],
  ["059", "NO SCHOOL: Presidents' Day", "no-school", "2027-02-15", "2027-02-15", null, null, null, null],
  ["060", "DUE: Biology science-fair project board", "due", "2027-02-17", "2027-02-17", null, null, null, "Biology"],
  ["061", "Science Fair", "event", "2027-02-18", "2027-02-18", "16:00", "19:00", "Main Gym", null],
  ["062", "TEST: World History Unit 3 - Medieval World", "test", "2027-02-23", "2027-02-23", "11:03", null, null, "World History"],
  ["063", "DUE: Spanish II Unit 5 project", "due", "2027-02-26", "2027-02-26", null, null, null, "Spanish II"],
  ["064", "TEST: Spanish II Unit 6", "test", "2027-03-04", "2027-03-04", "12:39", null, null, "Spanish II"],
  ["065", "TEST: Algebra II Unit 6 - Logarithms", "test", "2027-03-09", "2027-03-09", "08:00", null, null, "Algebra II"],
  ["066", "DUE: English 10 research paper draft", "due", "2027-03-12", "2027-03-12", null, null, null, "English 10"],
  ["067", "TEST: Biology Unit 4 - Evolution", "test", "2027-03-16", "2027-03-16", "10:02", null, null, "Biology"],
  ["068", "Spring Musical", "event", "2027-03-19", "2027-03-19", "19:00", "21:30", "Auditorium", null],
  ["069", "DUE: World History debate preparation packet", "due", "2027-03-25", "2027-03-25", null, null, null, "World History"],
  ["070", "End of Quarter 3", "academic", "2027-03-26", "2027-03-26", null, null, null, null],
  ["071", "NO SCHOOL: Spring Break", "no-school", "2027-03-29", "2027-04-02", null, null, null, null],
  ["072", "School Resumes (Quarter 4 Begins)", "academic", "2027-04-05", "2027-04-05", null, null, null, null],
  ["073", "Quarter 3 Report Cards Posted", "academic", "2027-04-08", "2027-04-08", null, null, null, null],
  ["074", "TEST: Algebra II Unit 7 - Trigonometry", "test", "2027-04-13", "2027-04-13", "08:00", null, null, "Algebra II"],
  ["075", "DUE: English 10 research paper final", "due", "2027-04-16", "2027-04-16", null, null, null, "English 10"],
  ["076", "TEST: Biology Unit 5 - Ecology", "test", "2027-04-20", "2027-04-20", "10:02", null, null, "Biology"],
  ["077", "Prom", "event", "2027-04-24", "2027-04-24", "19:00", "23:00", "Main Gym", null],
  ["078", "TEST: Spanish II Unit 7", "test", "2027-04-27", "2027-04-27", "12:39", null, null, "Spanish II"],
  ["079", "AP Exams", "event", "2027-05-04", "2027-05-14", null, null, null, null],
  ["080", "DUE: World History final project", "due", "2027-05-06", "2027-05-06", null, null, null, "World History"],
  ["081", "TEST: World History Unit 5 - Revolutions", "test", "2027-05-11", "2027-05-11", "11:03", null, null, "World History"],
  ["082", "TEST: Algebra II Unit 8 - Statistics", "test", "2027-05-18", "2027-05-18", "08:00", null, null, "Algebra II"],
  ["083", "DUE: Biology ecology field journal", "due", "2027-05-21", "2027-05-21", null, null, null, "Biology"],
  ["084", "NO SCHOOL: Memorial Day", "no-school", "2027-05-25", "2027-05-25", null, null, null, null],
  ["085", "Spring Concert", "event", "2027-05-27", "2027-05-27", "19:00", "20:30", "Auditorium", null],
  ["086", "Graduation", "event", "2027-05-29", "2027-05-29", "10:00", "12:00", "Griffin Field", null],
  ["087", "TEST: Algebra II Final Exam", "test", "2027-06-01", "2027-06-01", "08:00", null, null, "Algebra II"],
  ["088", "TEST: English 10 Final Exam", "test", "2027-06-01", "2027-06-01", "10:30", null, null, "English 10"],
  ["089", "TEST: Biology Final Exam", "test", "2027-06-02", "2027-06-02", "08:00", null, null, "Biology"],
  ["090", "TEST: World History Final Exam", "test", "2027-06-02", "2027-06-02", "10:30", null, null, "World History"],
  ["091", "Last Day of School (Early Dismissal 12:00 PM)", "academic", "2027-06-03", "2027-06-03", null, null, null, null],
  ["092", "TEST: Spanish II Final Exam", "test", "2027-06-03", "2027-06-03", "08:00", null, null, "Spanish II"]
];

// agent.toml wording
const GREETING = 'Good morning from Cedar Ridge.';
const FLAVOR = 'Griffins aim high!';
const SAY = [['vs.', 'versus'], [' - ', ', '], ['PSAT 10', 'P S A T ten']];
const WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const PLACES = ['Today', 'Next test', 'Due soon', 'Not mentioned'];
const QUIZ_DAY = '2026-10-19';
const QUIZ = [
  { id: '017', answer: 'Today', why: 'It is today and its category is event.' },
  { id: '018', answer: 'Next test', why: 'It is the first test after today, 1 day away.' },
  { id: '019', answer: 'Due soon', why: 'A due date 2 days away is inside the 7-day window.' },
  { id: '020', answer: 'Due soon', why: '3 days away, and it is the second due item, within the limit of 3.' },
  { id: '021', answer: 'Not mentioned', why: 'A sports event is announced only on its own day.' },
  { id: '022', answer: 'Not mentioned', why: 'An event on a later day is not in the briefing. It is also 7 days away, at the edge of the window.' },
  { id: '029', answer: 'Not mentioned', why: '22 days away, outside the 7-day window.' },
  { id: '024', answer: 'Not mentioned', why: 'An academic milestone is announced only on its own day.' }
];

let events = [];
let mode = 'explore';
let qIndex = 0;
let submitted = false;
let finished = false;
let results = [];
let feedback = '';
let feedbackCorrect = false;

let modeButton, placeLabel, placeSelect, submitButton, nextButton, dateLabel, dateInput, itemsSlider, daysSlider;

// ---------- calendar arithmetic (local school time, in minutes) ----------

function dayNum(s) {
  const [y, m, d] = s.split('-').map(Number);
  return Date.UTC(y, m - 1, d) / 86400000;
}
function weekdayOf(dn) {           // 0 = Monday, like Python's weekday()
  return (new Date(dn * 86400000).getUTCDay() + 6) % 7;
}
function minutesOf(hhmm) {
  const [h, m] = hhmm.split(':').map(Number);
  return h * 60 + m;
}

function buildEvents() {
  events = EVENTS_RAW.map(r => {
    const e = { id: r[0], title: r[1], category: r[2], first: dayNum(r[3]), last: dayNum(r[4]), location: r[7], course: r[8], timed: r[5] !== null };
    e.start = e.timed ? e.first * 1440 + minutesOf(r[5]) : e.first * 1440;
    e.end = e.timed ? e.last * 1440 + minutesOf(r[6] || r[5]) : (e.last + 1) * 1440;
    return e;
  });
}

const sortEvents = list => list.sort((a, b) => (a.start - b.start) || (a.title < b.title ? -1 : a.title > b.title ? 1 : 0));

function onDay(dn) {
  return sortEvents(events.filter(e => e.first <= dn && dn <= e.last));
}

function isSchoolDay(dn) {
  return weekdayOf(dn) < 5 && !onDay(dn).some(e => e.category === 'no-school');
}

// query.upcoming: not finished yet, and starting before now + days
function upcoming(now, days, cats) {
  const horizon = now + days * 1440;
  return sortEvents(events.filter(e => {
    if (!cats.includes(e.category)) return false;
    const notOver = (e.timed && e.end === e.start) ? e.start >= now : e.end > now;
    return notOver && e.start < horizon;
  }));
}

// ---------- compose.py wording ----------

function splitTitle(title) {
  const m = title.match(/^\s*(TEST|DUE|NO\s+SCHOOL)\s*:\s*(.*)$/i);
  return m ? m[2].trim() : title.trim();
}
function speakable(t) {
  for (const [a, b] of SAY) t = t.split(a).join(b);
  return t.split(/\s+/).filter(w => w).join(' ');
}
function clockWords(mins) {
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  const h12 = h % 12 || 12;
  const suffix = h < 12 ? 'AM' : 'PM';
  return m === 0 ? h12 + ' ' + suffix : h12 + ':' + String(m).padStart(2, '0') + ' ' + suffix;
}
function dayWords(dn, today) {
  const gap = dn - today;
  if (gap === 0) return 'today';
  if (gap === 1) return 'tomorrow';
  if (gap >= 2 && gap <= 6) return WEEKDAYS[weekdayOf(dn)];
  const d = new Date(dn * 86400000);
  return WEEKDAYS[weekdayOf(dn)] + ', ' + MONTHS[d.getUTCMonth()] + ' ' + d.getUTCDate();
}
function whenPhrase(e, today) {
  const dn = Math.floor(e.start / 1440);
  const day = dayWords(dn, today);
  const on = (day === 'today' || day === 'tomorrow') ? '' : 'on ';
  if (!e.timed) return on + day;
  return on + day + ' at ' + clockWords(e.start - dn * 1440);
}
function nameOf(e) {
  return e.category === 'test' && e.course ? e.course + ' test' : splitTitle(e.title);
}
const sentenceCase = t => t.slice(0, 1).toUpperCase() + t.slice(1);
function sentenceFor(e, today) {
  const name = speakable(nameOf(e));
  const when = whenPhrase(e, today);
  if (e.category === 'test') return 'Your ' + name + ' is ' + when + '.';
  if (e.category === 'due') return sentenceCase(name) + ' is due ' + when + '.';
  if (e.category === 'no-school') return 'No school ' + when + ': ' + speakable(splitTitle(e.title)) + '.';
  const where = e.location ? ' Location: ' + speakable(e.location) + '.' : '';
  return sentenceCase(name) + ' is ' + when + '.' + where;
}

// compose.daily_briefing: returns null on a weekend or no-school day
function dailyBriefing(today, maxItems, window) {
  if (!isSchoolDay(today)) return null;
  const now = today * 1440 + 7 * 60 + 30;
  const parts = [{ text: GREETING, kind: 'greeting' }];
  const todays = onDay(today).filter(e => ['test', 'due', 'event', 'sports', 'academic'].includes(e.category));
  if (todays.length) {
    todays.slice(0, maxItems).forEach(e => parts.push({ text: sentenceFor(e, today), kind: 'Today', id: e.id, ev: e }));
    if (todays.length > maxItems) parts.push({ text: (todays.length - maxItems) + ' more things are on the calendar today.', kind: 'Today' });
  } else {
    parts.push({ text: 'Nothing special is on the calendar today.', kind: 'Today' });
  }
  const tests = upcoming(now, window, ['test']).filter(e => e.first > today);
  if (tests.length) parts.push({ text: sentenceFor(tests[0], today).replace('Your ', 'Your next '), kind: 'Next test', id: tests[0].id, ev: tests[0] });
  const dues = upcoming(now, window, ['due']).filter(e => e.first > today);
  dues.slice(0, maxItems).forEach(e => parts.push({ text: sentenceFor(e, today), kind: 'Due soon', id: e.id, ev: e }));
  parts.push({ text: FLAVOR, kind: 'flavor' });
  return { parts: parts, speak: parts.map(p => p.text).join(' ') };
}

// for the verification harness: the text for a date and settings, or null
function briefingText(dateStr, maxItems, window) {
  const b = dailyBriefing(dayNum(dateStr), maxItems, window);
  return b ? b.speak : null;
}

// ---------- setup and drawing ----------

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);
  buildEvents();

  modeButton = createButton('Start the 8 events');
  modeButton.mousePressed(toggleMode);
  placeLabel = createSpan('Place:');
  placeSelect = createSelect();
  placeSelect.option('choose');
  for (const p of PLACES) placeSelect.option(p);
  submitButton = createButton('Submit');
  submitButton.mousePressed(submitAnswer);
  nextButton = createButton('Next event');
  nextButton.mousePressed(nextEvent);
  dateLabel = createSpan('Briefing date:');
  dateInput = createInput(QUIZ_DAY, 'date');
  dateInput.attribute('min', '2026-08-24');
  dateInput.attribute('max', '2027-06-11');
  for (const el of [modeButton, placeLabel, placeSelect, submitButton, nextButton, dateLabel, dateInput]) el.style('font-size', '16px');
  itemsSlider = createSlider(1, 5, 3, 1);
  daysSlider = createSlider(1, 14, 7, 1);

  positionControls();
  updateControlStates();

  describe('The Cedar Ridge daily briefing for a school morning. On the left, the events of the briefing are grouped as Today, Next test and Due soon; on the right, the rules and the spoken briefing text. In explore mode the learner changes the date and the two settings and the briefing is rebuilt. In the quiz the learner sorts eight events from Monday, October 19, 2026 into the part of the briefing they appear in, or Not mentioned, while the briefing is built.', LABEL);
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
  text('Daily Briefing Composer', canvasWidth / 2, 10);
  textSize(16);
  fill('dimgray');
  const maxItems = mode === 'quiz' ? 3 : Number(itemsSlider.value());
  const window = mode === 'quiz' ? 7 : Number(daysSlider.value());
  const dateStr = mode === 'quiz' ? QUIZ_DAY : (dateInput.value() || QUIZ_DAY);
  const dn = dayNum(dateStr);
  let status = WEEKDAYS[weekdayOf(dn)] + ' ' + dateStr + ', max_items ' + maxItems + ', upcoming_days ' + window;
  if (mode === 'quiz') status = (finished ? 'All 8 events done' : 'Event ' + (qIndex + 1) + ' of 8') + '   |   Score: ' + countCorrect() + ' of 8   |   ' + status;
  text(status, canvasWidth / 2, 42);

  const b = dailyBriefing(dn, maxItems, window);
  const split = canvasWidth * 0.54;
  if (mode === 'quiz') drawQuizList(margin, 70, split - margin - 8);
  else drawGroups(b, dn, margin, 70, split - margin - 8);
  drawRules(maxItems, window, split, 70, canvasWidth - split - margin);
  drawBriefing(b, dn, split, 210, canvasWidth - split - margin, 216);
  drawPanel(margin, 434, canvasWidth - 2 * margin, drawHeight - 442);

  noStroke();
  fill(mode === 'explore' ? 'black' : 'silver');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  const half = canvasWidth / 2;
  text('max_items: ' + itemsSlider.value(), 10, drawHeight + 98);
  text('upcoming_days: ' + daysSlider.value(), half + 10, drawHeight + 98);
}

function shortDate(e) {
  const d = new Date(e.first * 86400000);
  const s = WEEKDAYS[weekdayOf(e.first)].slice(0, 3) + ' ' + MONTHS[d.getUTCMonth()].slice(0, 3) + ' ' + d.getUTCDate();
  return s + (e.timed ? ' ' + clockWords(e.start - e.first * 1440) : '');
}

function drawQuizList(x, y, w) {
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(15);
  textStyle(BOLD);
  text('The 8 events', x, y);
  textStyle(NORMAL);
  let yy = y + 24;
  QUIZ.forEach((q, i) => {
    const e = events.find(ev => ev.id === q.id);
    const cur = i === qIndex && !finished;
    if (cur) {
      fill('lightyellow');
      stroke('gold');
      rect(x - 4, yy - 3, w + 4, 40, 6);
    }
    noStroke();
    fill('black');
    textSize(14);
    textStyle(cur ? BOLD : NORMAL);
    let title = e.title;
    while (textWidth(title) > w - 6 && title.length > 4) title = title.slice(0, -2);
    if (title !== e.title) title = title.trim() + '...';
    text((i + 1) + '. ' + title, x, yy);
    textStyle(NORMAL);
    textSize(13);
    fill('dimgray');
    let tail = shortDate(e) + ', ' + e.category;
    if (i < qIndex || finished || (i === qIndex && submitted)) {
      fill(results[i] ? 'darkgreen' : 'firebrick');
      tail += '  ->  ' + q.answer;
    }
    text(tail, x + 16, yy + 18);
    yy += 42;
  });
}

function drawGroups(b, dn, x, y, w) {
  noStroke();
  textAlign(LEFT, TOP);
  textSize(15);
  fill('black');
  textStyle(BOLD);
  text('What the briefing reads out', x, y);
  textStyle(NORMAL);
  if (!b) {
    fill('firebrick');
    const ns = onDay(dn).find(e => e.category === 'no-school');
    drawWrapped(ns ? 'No briefing: ' + ns.title + '.' : 'No briefing: it is a weekend.', x, y + 30, w, 20);
    return;
  }
  let yy = y + 26;
  for (const kind of ['Today', 'Next test', 'Due soon']) {
    fill('navy');
    textSize(15);
    textStyle(BOLD);
    text(kind, x, yy);
    textStyle(NORMAL);
    yy += 20;
    const items = b.parts.filter(p => p.kind === kind);
    textSize(13);
    fill('black');
    if (!items.length) { fill('dimgray'); text('(none)', x + 10, yy); yy += 18; }
    for (const p of items) {
      const label = p.ev ? shortDate(p.ev) + ': ' + splitTitle(p.ev.title) : p.text;
      yy = drawWrapped(label, x + 10, yy, w - 10, 17);
    }
    yy += 8;
  }
}

function drawRules(maxItems, window, x, y, w) {
  fill(255, 255, 255, 235);
  stroke('silver');
  rect(x, y, w, 132, 8);
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(13);
  let yy = y + 6;
  const rules = [
    'Today: today\'s test, due, event, sports or academic events, up to ' + maxItems + '.',
    'Next test: the first test after today, within ' + window + ' days.',
    'Due soon: due items after today, within ' + window + ' days, up to ' + maxItems + '.',
    'Anything else is not mentioned. No briefing on weekends or no-school days.'
  ];
  for (const r of rules) yy = drawWrapped(r, x + 8, yy, w - 16, 16) + 2;
}

function drawBriefing(b, dn, x, y, w, h) {
  fill('honeydew');
  stroke('seagreen');
  rect(x, y, w, h, 8);
  noStroke();
  fill('darkgreen');
  textAlign(LEFT, TOP);
  textSize(14);
  textStyle(BOLD);
  text(mode === 'quiz' && !finished ? 'Briefing so far' : 'The spoken briefing', x + 8, y + 6);
  textStyle(NORMAL);
  fill('black');
  textSize(14);
  let txt;
  if (mode === 'quiz') {
    // add each event's sentence once its place is known
    const known = finished ? QUIZ.length : qIndex + (submitted ? 1 : 0);
    const ids = QUIZ.slice(0, known).map(q => q.id);
    txt = b.parts.filter(p => p.kind === 'greeting' || (p.id && ids.includes(p.id)) || (finished && p.kind === 'flavor')).map(p => p.text).join(' ');
  } else {
    txt = b ? b.speak : '(no briefing)';
  }
  const yy = drawWrapped(txt, x + 8, y + 28, w - 16, 18);
  fill('dimgray');
  textSize(13);
  if (b && (mode === 'explore' || finished)) text(b.speak.length + ' characters', x + 8, min(yy + 4, y + h - 18));
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
    text('Which part of the briefing is this event in?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Change the date and upcoming_days and watch events enter or leave the briefing. Try a Saturday and a no-school day.', x + pad, yy + 22, tw, 20);
    return;
  }
  if (finished) {
    const sc = countCorrect();
    fill(sc >= 7 ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    text('Score: ' + sc + ' of 8. ' + (sc >= 7 ? 'Mastery reached.' : 'Mastery is 7 of 8.'), x + pad, yy);
    textStyle(NORMAL);
    fill('black');
    drawWrapped('Only 4 of the 8 events are spoken. Which categories appear only on their own day?', x + pad, yy + 24, tw, 20);
    return;
  }
  if (!submitted) {
    fill('navy');
    textStyle(ITALIC);
    text('Which part of the briefing is this event in?', x + pad, yy);
    textStyle(NORMAL);
    fill('dimgray');
    drawWrapped('Today is Monday, October 19, 2026 (3 items, 7 days). Choose Today, Next test, Due soon or Not mentioned, then Submit.', x + pad, yy + 22, tw, 20);
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
    qIndex = 0;
    results = [];
    submitted = false;
    finished = false;
  } else {
    mode = 'explore';
  }
  placeSelect.selected('choose');
  updateControlStates();
}

function submitAnswer() {
  if (mode !== 'quiz' || submitted || finished) return;
  const c = placeSelect.value();
  if (c === 'choose') return;
  const q = QUIZ[qIndex];
  const correct = c === q.answer;
  results[qIndex] = correct;
  feedbackCorrect = correct;
  feedback = correct ? 'Correct: ' + q.why : 'Not quite. This event goes in ' + q.answer + ': ' + q.why;
  submitted = true;
  updateControlStates();
}

function nextEvent() {
  if (!submitted) return;
  if (qIndex === QUIZ.length - 1) finished = true;
  else { qIndex++; submitted = false; }
  placeSelect.selected('choose');
  updateControlStates();
}

function setEnabled(el, on) {
  el.elt.disabled = !on;
}

function updateControlStates() {
  const quiz = mode === 'quiz';
  const answering = quiz && !submitted && !finished;
  modeButton.html(quiz ? 'Back to explore' : 'Start the 8 events');
  setEnabled(placeSelect, answering);
  setEnabled(submitButton, answering);
  setEnabled(nextButton, quiz && submitted && !finished);
  nextButton.html(qIndex === QUIZ.length - 1 ? 'See score' : 'Next event');
  for (const el of [dateInput, itemsSlider, daysSlider]) setEnabled(el, !quiz);
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
  layoutRow([modeButton, placeLabel, placeSelect, submitButton, nextButton], 10, drawHeight + 8, 8);
  layoutRow([dateLabel, dateInput], 10, drawHeight + 46, 8);
  const half = canvasWidth / 2;
  itemsSlider.position(130, drawHeight + 88);
  itemsSlider.size(half - 130 - 20);
  daysSlider.position(half + 160, drawHeight + 88);
  daysSlider.size(half - 160 - margin);
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
