// Kit Parts Infographic MicroSim (HTML + inline SVG, no libraries)
// CANVAS_HEIGHT: 540
// Explore: select any of the five kit parts in the labeled picture to read its job.
// Check: 5 job statements in fixed order, one attempt each; pick the part that
// does the job from the five parts (always offered together, in a fixed order).
// Mastery is 4 of 5 on the first attempt.

(function () {
  // Parts in the fixed order they are always offered
  const parts = [
    { id: 'pico', name: 'Raspberry Pi Pico 2 W',
      desc: 'The brain. It runs your MicroPython program and connects to Wi-Fi.' },
    { id: 'display', name: 'Round display',
      desc: 'The face. A 360 by 360 color screen that shows text, shapes, and meters.' },
    { id: 'mic', name: 'INMP441 microphone',
      desc: 'The ear. It senses sound and sends 24-bit digital numbers to the Pico.' },
    { id: 'amp', name: 'MAX98357A amplifier and speaker',
      desc: 'The voice. The amplifier turns digital audio into power for the speaker.' },
    { id: 'buttons', name: 'Mode, Up, and Down buttons',
      desc: 'The hands. Three switches you press to change modes, settings, and to talk.' }
  ];

  // Job statements in the spec order
  const jobs = [
    { text: 'Turns room sound into digital numbers.', answer: 'mic',
      why: 'The converter is built into the microphone board.' },
    { text: 'Runs the MicroPython program.', answer: 'pico',
      why: 'The Pico is the only part that runs your code.' },
    { text: 'Drives the speaker from digital audio.', answer: 'amp',
      why: 'The amplifier takes I2S audio and powers the speaker.' },
    { text: 'Shows a level meter and text.', answer: 'display',
      why: 'The display draws what the Pico tells it to draw.' },
    { text: 'Lets the student start push-to-talk.', answer: 'buttons',
      why: 'A held button is read as a signal on a Pico pin.' }
  ];

  const byId = {};
  parts.forEach(p => { byId[p.id] = p; });

  // State
  let mode = 'explore';   // 'explore' | 'check' | 'done'
  let jobIndex = 0;
  let score = 0;
  let answered = false;

  const svg = document.getElementById('kit-svg');
  const statusEl = document.getElementById('status');
  const scoreEl = document.getElementById('score');
  const messageEl = document.getElementById('message');
  const choicesEl = document.getElementById('choices');
  const startBtn = document.getElementById('start-btn');
  const nextBtn = document.getElementById('next-btn');
  const partEls = Array.from(document.querySelectorAll('.part'));

  function clearPartMarks() {
    partEls.forEach(el => el.classList.remove('selected', 'correct', 'wrong'));
  }

  function partEl(id) {
    return document.getElementById('part-' + id);
  }

  function setMessage(html, kind) {
    messageEl.innerHTML = html;
    messageEl.className = kind || '';
  }

  // ---- Explore mode ----
  function selectPart(id) {
    if (mode === 'check') return;   // descriptions are hidden during the check
    clearPartMarks();
    partEl(id).classList.add('selected');
    const p = byId[id];
    setMessage('<span class="name">' + p.name + '</span>: ' + p.desc, '');
  }

  function showExplore() {
    mode = 'explore';
    svg.classList.remove('checking');
    clearPartMarks();
    statusEl.textContent = 'Explore the parts';
    scoreEl.textContent = '';
    setMessage('Select a part to learn its job.', '');
    choicesEl.innerHTML = '';
    startBtn.textContent = 'Start the Check';
    startBtn.hidden = false;
    nextBtn.hidden = true;
  }

  // ---- Check mode ----
  function startCheck() {
    mode = 'check';
    svg.classList.add('checking');
    jobIndex = 0;
    score = 0;
    showJob();
  }

  function showJob() {
    answered = false;
    clearPartMarks();
    const job = jobs[jobIndex];
    statusEl.textContent = 'Job ' + (jobIndex + 1) + ' of 5';
    scoreEl.textContent = 'Score: ' + score + ' of 5';
    setMessage('Which part does this job? <strong>' + job.text + '</strong>', '');
    choicesEl.innerHTML = '';
    parts.forEach(p => {
      const b = document.createElement('button');
      b.textContent = p.name;
      b.dataset.part = p.id;
      b.addEventListener('click', () => pick(p.id, b));
      choicesEl.appendChild(b);
    });
    startBtn.textContent = 'Back to Explore';
    startBtn.hidden = false;
    nextBtn.hidden = true;
  }

  function pick(id, button) {
    if (mode !== 'check' || answered) return;
    answered = true;
    const job = jobs[jobIndex];
    const correct = (id === job.answer);
    if (correct) score++;
    // Reveal the correct part right after the pick
    Array.from(choicesEl.children).forEach(b => {
      b.disabled = true;
      if (b.dataset.part === job.answer) b.classList.add('pick-correct');
    });
    partEl(job.answer).classList.add('correct');
    if (!correct) {
      button.classList.add('pick-wrong');
      partEl(id).classList.add('wrong');
    }
    scoreEl.textContent = 'Score: ' + score + ' of 5';
    if (correct) {
      setMessage('Correct: ' + job.why, 'good');
    } else {
      setMessage('Not quite. This is the job of the ' + byId[job.answer].name + ': ' + job.why, 'bad');
    }
    nextBtn.textContent = (jobIndex === jobs.length - 1) ? 'See Score' : 'Next';
    nextBtn.hidden = false;
  }

  function next() {
    if (!answered) return;
    jobIndex++;
    if (jobIndex >= jobs.length) {
      showDone();
    } else {
      showJob();
    }
  }

  function showDone() {
    mode = 'done';
    svg.classList.remove('checking');
    clearPartMarks();
    statusEl.textContent = 'Check finished';
    scoreEl.textContent = 'Score: ' + score + ' of 5';
    const mastery = score >= 4
      ? 'Mastery reached (4 of 5 needed).'
      : 'Mastery needs 4 of 5. Select each part to review its job, then try again.';
    setMessage('You scored ' + score + ' of 5. ' + mastery +
      ' Remember: the Pico runs the code, but the microphone, amplifier, display, and buttons each do their own job.',
      score >= 4 ? 'good' : '');
    choicesEl.innerHTML = '';
    startBtn.textContent = 'Retake the Check';
    nextBtn.textContent = 'Back to Explore';
    nextBtn.hidden = false;
  }

  // ---- Wiring ----
  partEls.forEach(el => {
    el.addEventListener('click', () => selectPart(el.dataset.part));
    el.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        selectPart(el.dataset.part);
      }
    });
  });

  startBtn.addEventListener('click', () => {
    if (mode === 'check') showExplore();
    else startCheck();
  });

  nextBtn.addEventListener('click', () => {
    if (mode === 'done') showExplore();
    else next();
  });

  showExplore();
})();
