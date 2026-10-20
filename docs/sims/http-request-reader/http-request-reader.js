// HTTP Request Reader - p5.js MicroSim
// CANVAS_HEIGHT: 520
// Interpret the parts of the HTTP POST the Pico sends to the buddy server
// (the request printed by src/chapters/13-wifi-http-agent-link/04-raw-http-post.py):
// request line, headers, the blank line, and a 73-byte JSON body.
// The head is 121 bytes (with CRLF line ends) and the whole request 194 bytes.
// Hover over a line to read what it is called; answer 8 questions with A, B or C.

let canvasWidth = 800;
let drawHeight = 470;
let controlHeight = 50;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

const LINES = [
  { text: 'POST /v1/ask HTTP/1.0', name: 'Request line: the method (POST), the path (/v1/ask) and the HTTP version' },
  { text: 'Host: 192.168.1.50:8080', name: 'Header Host: which server, and which port, the request is for' },
  { text: 'Content-Type: application/json', name: 'Header Content-Type: the format of the body' },
  { text: 'Content-Length: 73', name: 'Header Content-Length: how many bytes of body follow the blank line' },
  { text: 'Connection: close', name: 'Header Connection: close the connection after the reply' },
  { text: '', name: 'Blank line: ends the headers; the body starts right after it' },
  { text: '{"device": "desk-07", "kind": "question", "text": "when is my next test"}', name: 'Body: 73 bytes of JSON, the question itself' }
];
const QUESTIONS = [
  { q: 'Which line says what the client wants done, and where?', choices: ['L1', 'L2', 'L7'], answer: 0, lines: [1],
    why: 'The request line holds the method (POST), the path (/v1/ask) and the HTTP version.' },
  { q: 'Which line tells the server how many bytes of body to read?', choices: ['L3', 'L4', 'L5'], answer: 1, lines: [4],
    why: "Content-Length counts the body's bytes." },
  { q: 'What does the blank line L6 do?', choices: ['It ends the headers, so the body starts after it', 'It is optional', 'It separates two requests'], answer: 0, lines: [6],
    why: 'Without it the server would keep reading header lines.' },
  { q: 'Content-Length says 60 but the body is 73 bytes. What does the buddy server do?',
    choices: ['Reads 60 bytes and answers 400 because the JSON is cut off', 'Reads all 73 and answers 200', 'Waits for 13 more bytes'], answer: 0, lines: [4, 7],
    why: 'The server trusts the header, so it stops at 60 and the JSON is incomplete.' },
  { q: 'Content-Length says 90 but the body is 73 bytes. What happens?',
    choices: ['The server answers 200', 'The server answers 400', "The server waits for 17 more bytes, and the Pico's timeout ends it"], answer: 2, lines: [4, 7],
    why: 'The server is still reading and the Pico is waiting for the reply, so neither moves.' },
  { q: 'Which line tells the server the body is JSON?', choices: ['L2', 'L3', 'L5'], answer: 1, lines: [3],
    why: 'Content-Type names the format of the body.' },
  { q: 'The reply starts with HTTP/1.0 400 Bad Request. Whose mistake is it?',
    choices: ["The client's request was wrong", 'The server is broken', 'The Wi-Fi dropped'], answer: 0, lines: [], reply: ['HTTP/1.0 400 Bad Request'],
    why: 'A first digit of 4 means the client made the mistake; 5 means the server did.' },
  { q: 'The reply has Content-Length: 103. How many body bytes should the Pico read?',
    choices: ['73', '103', 'As many as arrive until a timeout'], answer: 1, lines: [], reply: ['HTTP/1.0 200 OK', 'Content-Type: application/json', 'Content-Length: 103'],
    why: "The reply's Content-Length counts the reply's body, and the Pico stops there." }
];
const LETTERS = ['A', 'B', 'C'];

let qIndex = 0;
let submitted = false;
let finished = false;
let results = [];
let chosen = -1;
let feedback = '';
let feedbackCorrect = false;
let hoverLine = -1;

let choiceButtons = [];
let nextButton, restartButton;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  for (let i = 0; i < 3; i++) {
    const b = createButton('Answer ' + LETTERS[i]);
    b.mousePressed(() => choose(i));
    choiceButtons.push(b);
  }
  nextButton = createButton('Next question');
  nextButton.mousePressed(nextQuestion);
  restartButton = createButton('Start over');
  restartButton.mousePressed(restart);
  for (const el of [...choiceButtons, nextButton, restartButton]) el.style('font-size', '16px');

  positionControls();
  updateControlStates();

  describe('An HTTP POST request shown as seven numbered lines: the request line, four headers, a blank line and a JSON body. Hovering over a line names it. Below, one of eight questions about the request is shown with three answers, chosen with the A, B and C buttons; after each choice the lines involved are highlighted and the reason is given.', LABEL);
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
  text('HTTP Request Reader', canvasWidth / 2, 10);
  textSize(16);
  fill('dimgray');
  const head = finished ? 'All 8 questions done' : 'Question ' + (qIndex + 1) + ' of 8';
  text(head + '   |   Score: ' + countCorrect() + ' of 8', canvasWidth / 2, 42);

  const q = QUESTIONS[min(qIndex, 7)];
  const hot = submitted && !finished ? q.lines : [];
  hoverLine = drawRequest(margin, 70, canvasWidth - 2 * margin, hot);
  const yReply = drawReply(!finished && q.reply, margin, 262, canvasWidth - 2 * margin);
  if (finished) drawSummary(margin, yReply, canvasWidth - 2 * margin, drawHeight - yReply - 8);
  else drawQuestion(q, margin, yReply, canvasWidth - 2 * margin, drawHeight - yReply - 8);
}

// the 7 numbered lines; returns the index of the line under the mouse
function drawRequest(x, y, w, hot) {
  const rh = 22;
  const boxH = LINES.length * rh + 14;
  fill('white');
  stroke('steelblue');
  rect(x, y, w, boxH, 8);
  let over = -1;
  // shrink the code font until the longest line fits
  textFont('monospace');
  let ts = 15;
  textSize(ts);
  while (textWidth(LINES[6].text) > w - 64 && ts > 10) textSize(--ts);
  for (let i = 0; i < LINES.length; i++) {
    const yy = y + 7 + i * rh;
    const isOver = mouseX > x && mouseX < x + w && mouseY >= yy && mouseY < yy + rh;
    if (isOver) over = i;
    if (hot.includes(i + 1) || isOver) {
      noStroke();
      fill(hot.includes(i + 1) ? 'gold' : 'lightcyan');
      rect(x + 2, yy, w - 4, rh, 4);
    }
    noStroke();
    fill('dimgray');
    textAlign(LEFT, TOP);
    text('L' + (i + 1), x + 8, yy + 3);
    fill(LINES[i].text ? 'midnightblue' : 'gray');
    text(LINES[i].text || '(blank line)', x + 50, yy + 3);
  }
  textFont('sans-serif');
  noStroke();
  textSize(14);
  textAlign(LEFT, TOP);
  const infoY = y + boxH + 4;
  if (over >= 0) {
    fill('navy');
    text('L' + (over + 1) + ' = ' + LINES[over].name, x + 4, infoY);
  } else {
    fill('dimgray');
    text('Hover over a line to see what it is called. Head 121 bytes + body 73 bytes = 194 bytes.', x + 4, infoY);
  }
  return over;
}

// the server's reply, for the two questions about it; returns the next free y
function drawReply(reply, x, y, w) {
  if (!reply) return y;
  const rh = 20;
  fill('honeydew');
  stroke('seagreen');
  rect(x, y, w, reply.length * rh + 30, 8);
  noStroke();
  fill('darkgreen');
  textSize(14);
  textAlign(LEFT, TOP);
  text('Reply from the server:', x + 8, y + 5);
  textFont('monospace');
  fill('black');
  reply.forEach((s, i) => text(s, x + 50, y + 24 + i * rh));
  textFont('sans-serif');
  return y + reply.length * rh + 38;
}

function drawQuestion(q, x, y, w, h) {
  fill(255, 255, 255, 235);
  stroke('silver');
  rect(x, y, w, h, 10);
  const pad = 10;
  const tw = w - 2 * pad;
  let yy = y + 8;
  noStroke();
  textAlign(LEFT, TOP);
  textSize(16);
  fill('black');
  textStyle(BOLD);
  yy = drawWrapped(q.q, x + pad, yy, tw, 20) + 4;
  textStyle(NORMAL);
  for (let i = 0; i < 3; i++) {
    let col = 'black';
    if (submitted && i === q.answer) col = 'darkgreen';
    else if (submitted && i === chosen) col = 'firebrick';
    fill(col);
    const mark = submitted && i === q.answer ? '  (answer)' : (submitted && i === chosen ? '  (your choice)' : '');
    yy = drawWrapped(LETTERS[i] + '.  ' + q.choices[i] + mark, x + pad + 10, yy, tw - 10, 20);
  }
  yy += 4;
  if (submitted) {
    fill(feedbackCorrect ? 'darkgreen' : 'firebrick');
    textStyle(BOLD);
    drawWrapped(feedback, x + pad, yy, tw, 20);
    textStyle(NORMAL);
  } else {
    fill('dimgray');
    drawWrapped('Choose Answer A, B or C below. One attempt per question.', x + pad, yy, tw, 20);
  }
}

function drawSummary(x, y, w, h) {
  fill(255, 255, 255, 235);
  stroke('silver');
  rect(x, y, w, h, 10);
  const sc = countCorrect();
  noStroke();
  textAlign(LEFT, TOP);
  textSize(18);
  textStyle(BOLD);
  fill(sc >= 7 ? 'darkgreen' : 'firebrick');
  text('Score: ' + sc + ' of 8. ' + (sc >= 7 ? 'Mastery reached.' : 'Mastery is 7 of 8.'), x + 10, y + 10);
  textStyle(NORMAL);
  textSize(16);
  fill('black');
  drawWrapped('Questions 4 and 5 changed only whether Content-Length was smaller or larger than the real body. Why does one give a quick 400 and the other a long wait?',
    x + 10, y + 40, w - 20, 20);
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

function choose(i) {
  if (submitted || finished) return;
  const q = QUESTIONS[qIndex];
  chosen = i;
  const correct = i === q.answer;
  results[qIndex] = correct;
  feedbackCorrect = correct;
  feedback = correct ? 'Correct: ' + q.why : 'Not quite. The answer is ' + LETTERS[q.answer] + ', ' + q.choices[q.answer] + ': ' + q.why;
  submitted = true;
  updateControlStates();
}

function nextQuestion() {
  if (!submitted) return;
  if (qIndex === QUESTIONS.length - 1) finished = true;
  else { qIndex++; submitted = false; chosen = -1; }
  updateControlStates();
}

function restart() {
  qIndex = 0;
  submitted = false;
  finished = false;
  results = [];
  chosen = -1;
  updateControlStates();
}

function setEnabled(el, on) {
  el.elt.disabled = !on;
}

function updateControlStates() {
  for (const b of choiceButtons) setEnabled(b, !submitted && !finished);
  setEnabled(nextButton, submitted && !finished);
  nextButton.html(qIndex === QUESTIONS.length - 1 ? 'See score' : 'Next question');
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
  layoutRow([...choiceButtons, nextButton, restartButton], 10, drawHeight + 10, 10);
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
