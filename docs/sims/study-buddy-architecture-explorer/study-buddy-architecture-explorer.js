// Study Buddy Architecture Explorer - vis-network MicroSim
// CANVAS_HEIGHT: 620
// Six parts in two groups: the agent terminal (the desk device) with five kit
// parts, and the school network with the buddy server. Explore mode: hover or
// click a part to read its job and the meaning of its connections. Quiz mode:
// read a job description and click the part that does that job.
// Bloom level: Remember (identify).

// ===========================================
// CONTENT (from the specification)
// ===========================================
const TERMINAL_GROUP = 'Agent terminal (the desk device)';
const NETWORK_GROUP = 'School network';

const partData = [
    { id: 'pico', name: 'Raspberry Pi Pico 2 W', label: 'Raspberry Pi\nPico 2 W',
      group: TERMINAL_GROUP, x: 0, y: -95,
      job: 'Runs the terminal program, reads the microphone and buttons, drives the display and speaker, and talks to the buddy server over Wi-Fi.' },
    { id: 'display', name: 'Round color display', label: 'Round color\ndisplay',
      group: TERMINAL_GROUP, x: 150, y: -200,
      job: "Shows the clock, the agent's words, and status as a 360 by 360 pixel round picture." },
    { id: 'mic', name: 'INMP441 microphone', label: 'INMP441\nmicrophone',
      group: TERMINAL_GROUP, x: -150, y: -200,
      job: 'Turns sound into digital numbers that the Pico can read.' },
    { id: 'speaker', name: 'MAX98357A amplifier and speaker', label: 'MAX98357A amplifier\nand speaker',
      group: TERMINAL_GROUP, x: 150, y: 10,
      job: 'Turns digital audio numbers into sound that the student hears.' },
    { id: 'buttons', name: 'Mode, Up, and Down buttons', label: 'Mode, Up, and\nDown buttons',
      group: TERMINAL_GROUP, x: -150, y: 10,
      job: 'Let the student change modes, move through menus, and adjust values by hand.' },
    { id: 'server', name: 'Buddy server', label: 'Buddy server',
      group: NETWORK_GROUP, x: 30, y: 200,
      job: 'Receives requests, decides on a reply, and sends it back. It runs on a school computer and is not part of the desk device.' }
];

// No edge is perfectly horizontal (the Pico-to-server edge runs from x 0 to x 30) to avoid
// the vis-network edge-label rendering bug on perfectly horizontal edges.
const edgeData = [
    { id: 'e1', from: 'mic', to: 'pico', meaning: 'Sends digital sound numbers to the Pico.' },
    { id: 'e2', from: 'buttons', to: 'pico', meaning: 'Send button presses to the Pico.' },
    { id: 'e3', from: 'pico', to: 'display', meaning: 'Sends text and pictures to show.' },
    { id: 'e4', from: 'pico', to: 'speaker', meaning: 'Sends digital audio numbers to play.' },
    { id: 'e5', from: 'pico', to: 'server', meaning: 'Sends requests and receives replies over Wi-Fi on the school network.', both: true }
];

const quizQuestions = [
    { job: 'Turns sound into digital numbers.', answer: 'mic' },
    { job: 'Turns digital audio numbers into sound the student hears.', answer: 'speaker' },
    { job: "Shows the clock and the agent's words as a round picture.", answer: 'display' },
    { job: 'Runs the terminal program and connects to Wi-Fi.', answer: 'pico' },
    { job: 'Lets the student change modes and adjust values by hand.', answer: 'buttons' },
    { job: 'Decides on a reply and sends it back, from a school computer.', answer: 'server' }
];

// ===========================================
// COLORS
// ===========================================
const colors = {
    terminal: { background: 'lightcyan', border: 'teal' },
    server: { background: 'lavender', border: 'slateblue' },
    selected: { background: 'lightyellow', border: 'royalblue' },
    correct: { background: 'palegreen', border: 'seagreen' },
    wrong: { background: 'peachpuff', border: 'darkorange' },
    edge: 'slategray',
    edgeDim: 'gainsboro',
    edgeLit: 'royalblue'
};

// ===========================================
// STATE
// ===========================================
let nodes, edges, network;
let mode = 'explore';       // 'explore' or 'quiz'
let selectedId = null;      // explore-mode selection
let quizIndex = 0;
let quizScore = 0;
let quizAnswered = false;
let quizResults = [];       // { q, clicked, correct }
let quizFinished = false;

// ===========================================
// ENVIRONMENT DETECTION
// ===========================================
function isInIframe() {
    try {
        return window.self !== window.top;
    } catch (e) {
        return true;
    }
}

function partById(id) {
    return partData.find(p => p.id === id);
}

function baseColor(p) {
    return p.group === NETWORK_GROUP ? colors.server : colors.terminal;
}

// ===========================================
// NETWORK SETUP
// ===========================================
function initializeNetwork() {
    nodes = new vis.DataSet(partData.map(p => ({
        id: p.id,
        label: p.label,
        x: p.x,
        y: p.y,
        color: { background: baseColor(p).background, border: baseColor(p).border,
                 highlight: { background: baseColor(p).background, border: baseColor(p).border },
                 hover: { background: baseColor(p).background, border: 'royalblue' } },
        borderWidth: 2
    })));

    edges = new vis.DataSet(edgeData.map(e => ({
        id: e.id,
        from: e.from,
        to: e.to,
        arrows: e.both ? { to: { enabled: true }, from: { enabled: true } } : { to: { enabled: true } },
        color: { color: colors.edge, highlight: colors.edge, hover: colors.edge },
        width: 2
    })));

    const enableMouse = !isInIframe();
    const options = {
        layout: { improvedLayout: false },
        physics: { enabled: false },
        interaction: {
            hover: true,
            selectConnectedEdges: false,
            dragNodes: false,
            dragView: enableMouse,
            zoomView: enableMouse,
            navigationButtons: true,
            keyboard: { enabled: false }
        },
        nodes: {
            shape: 'box',
            margin: 10,
            font: { size: 16, face: 'Arial', color: 'black', multi: false },
            widthConstraint: { minimum: 120 },
            shadow: { enabled: true, color: 'rgba(0,0,0,0.2)', size: 5, x: 2, y: 2 }
        },
        edges: {
            width: 2,
            smooth: false,
            arrows: { to: { scaleFactor: 0.9 } }
        }
    };

    network = new vis.Network(document.getElementById('network'), { nodes: nodes, edges: edges }, options);

    // shaded group boxes behind the nodes
    network.on('beforeDrawing', drawGroups);

    network.on('click', params => {
        if (params.nodes.length > 0) {
            onPartClicked(params.nodes[0]);
        } else if (mode === 'explore') {
            clearSelection();
        }
    });

    // hover shows the job in explore mode only (never in quiz mode)
    network.on('hoverNode', params => {
        if (mode === 'explore' && !selectedId) showPartInfo(params.node, false);
    });
    network.on('blurNode', () => {
        if (mode === 'explore' && !selectedId) showInstruction();
    });

    network.once('afterDrawing', fitView);
    window.addEventListener('resize', () => { network.redraw(); fitView(); });
}

// Fit all nodes plus the group boxes (padding and labels, see drawGroups)
// into the view, leaving a strip at the top for the title overlay
function fitView() {
    const titleRoom = 34;   // pixels
    let x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity;
    for (const p of partData) {
        const b = network.getBoundingBox(p.id);
        x1 = Math.min(x1, b.left); y1 = Math.min(y1, b.top);
        x2 = Math.max(x2, b.right); y2 = Math.max(y2, b.bottom);
    }
    x1 -= 26; x2 += 26; y1 -= 26 + 22; y2 += 26 + 22;   // group pad + label strip
    const el = document.getElementById('network');
    const w = el.clientWidth, h = el.clientHeight;
    const s = Math.min(w / (x2 - x1), (h - titleRoom) / (y2 - y1)) * 0.95;
    network.moveTo({ position: { x: (x1 + x2) / 2, y: (y1 + y2) / 2 - titleRoom / 2 / s },
        scale: s, animation: false });
}

// Draw a rounded, labeled rectangle around each group of nodes
function drawGroups(ctx) {
    const groups = [
        { name: TERMINAL_GROUP, fill: 'rgba(0,128,128,0.07)', stroke: 'teal', labelAtTop: true },
        { name: NETWORK_GROUP, fill: 'rgba(106,90,205,0.08)', stroke: 'slateblue', labelAtTop: false }
    ];
    for (const g of groups) {
        const ids = partData.filter(p => p.group === g.name).map(p => p.id);
        let x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity;
        for (const id of ids) {
            const b = network.getBoundingBox(id);
            x1 = Math.min(x1, b.left); y1 = Math.min(y1, b.top);
            x2 = Math.max(x2, b.right); y2 = Math.max(y2, b.bottom);
        }
        const pad = 24;
        // leave a 22-unit strip for the group label (top or bottom)
        x1 -= pad; x2 += pad;
        y1 -= pad + (g.labelAtTop ? 22 : 0);
        y2 += pad + (g.labelAtTop ? 0 : 22);
        ctx.save();
        ctx.fillStyle = g.fill;
        ctx.strokeStyle = g.stroke;
        ctx.lineWidth = 2;
        ctx.setLineDash([8, 6]);
        ctx.beginPath();
        if (ctx.roundRect) {
            ctx.roundRect(x1, y1, x2 - x1, y2 - y1, 14);
        } else {
            ctx.rect(x1, y1, x2 - x1, y2 - y1);
        }
        ctx.fill();
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = g.stroke;
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'top';
        ctx.fillText(g.name, x1 + 10, g.labelAtTop ? y1 + 6 : y2 - 24);
        ctx.restore();
    }
}

// ===========================================
// HIGHLIGHTING
// ===========================================
function resetColors() {
    nodes.update(partData.map(p => ({
        id: p.id,
        color: { background: baseColor(p).background, border: baseColor(p).border,
                 highlight: { background: baseColor(p).background, border: baseColor(p).border },
                 hover: { background: baseColor(p).background, border: 'royalblue' } },
        borderWidth: 2
    })));
    edges.update(edgeData.map(e => ({ id: e.id, color: { color: colors.edge, highlight: colors.edge, hover: colors.edge }, width: 2 })));
}

function setNodeColor(id, c, width) {
    nodes.update({ id: id, color: { background: c.background, border: c.border,
        highlight: { background: c.background, border: c.border },
        hover: { background: c.background, border: c.border } }, borderWidth: width || 4 });
}

// Selected node plus every edge connected to it
function highlightPart(id) {
    resetColors();
    setNodeColor(id, colors.selected, 4);
    edges.update(edgeData.map(e => {
        const lit = e.from === id || e.to === id;
        return { id: e.id, color: { color: lit ? colors.edgeLit : colors.edgeDim,
            highlight: lit ? colors.edgeLit : colors.edgeDim, hover: lit ? colors.edgeLit : colors.edgeDim },
            width: lit ? 4 : 1 };
    }));
}

// ===========================================
// EXPLORE MODE
// ===========================================
function showInstruction() {
    document.getElementById('explore-instruction').textContent = 'Click a part to learn its job.';
    document.getElementById('part-name').textContent = '';
    document.getElementById('part-group').textContent = '';
    document.getElementById('part-job').textContent = '';
    document.getElementById('connections').innerHTML = '';
}

function showPartInfo(id, withConnections) {
    const p = partById(id);
    document.getElementById('explore-instruction').textContent = withConnections ? '' : 'Click to see its connections.';
    document.getElementById('part-name').textContent = p.name;
    document.getElementById('part-group').textContent = p.group;
    document.getElementById('part-job').textContent = p.job;
    const conn = document.getElementById('connections');
    conn.innerHTML = '';
    if (!withConnections) return;
    const title = document.createElement('div');
    title.className = 'box-title';
    title.textContent = 'Connections:';
    conn.appendChild(title);
    const ul = document.createElement('ul');
    for (const e of edgeData.filter(e => e.from === id || e.to === id)) {
        const li = document.createElement('li');
        // name the other end of the edge and the direction of the data
        const other = e.from === id ? partById(e.to).name : partById(e.from).name;
        const dir = e.both ? 'With ' : (e.from === id ? 'To ' : 'From ');
        li.textContent = dir + other + ': ' + e.meaning;
        ul.appendChild(li);
    }
    conn.appendChild(ul);
}

function clearSelection() {
    selectedId = null;
    network.unselectAll();
    resetColors();
    showInstruction();
}

// ===========================================
// QUIZ MODE
// ===========================================
function startQuiz() {
    quizIndex = 0;
    quizScore = 0;
    quizAnswered = false;
    quizResults = [];
    quizFinished = false;
    resetColors();
    renderQuiz();
}

function renderQuiz() {
    const progress = document.getElementById('quiz-progress');
    const job = document.getElementById('quiz-job');
    const instr = document.getElementById('quiz-instruction');
    const fb = document.getElementById('quiz-feedback');
    const nextBtn = document.getElementById('next-btn');
    document.getElementById('quiz-score').textContent = 'Score: ' + quizScore + ' of 6';

    if (quizFinished) {
        progress.textContent = 'Quiz complete';
        job.textContent = 'You matched ' + quizScore + ' of 6 jobs correctly.';
        instr.textContent = quizScore >= 5 ? 'Mastery reached (5 of 6 needed).' :
            'Mastery needs 5 of 6. Explore the parts again, then restart the quiz.';
        const missed = quizResults.filter(r => !r.correct);
        fb.className = 'feedback ' + (quizScore >= 5 ? 'correct' : 'incorrect');
        fb.innerHTML = '';
        if (missed.length === 0) {
            fb.textContent = 'No missed parts.';
        } else {
            const t = document.createElement('div');
            t.className = 'box-title';
            t.textContent = 'Missed parts:';
            fb.appendChild(t);
            const ul = document.createElement('ul');
            for (const r of missed) {
                const p = partById(r.q.answer);
                const li = document.createElement('li');
                li.textContent = p.name + ': ' + p.job;
                ul.appendChild(li);
            }
            fb.appendChild(ul);
        }
        nextBtn.disabled = true;
        nextBtn.classList.add('hidden');
        return;
    }

    const q = quizQuestions[quizIndex];
    progress.textContent = 'Question ' + (quizIndex + 1) + ' of 6';
    job.textContent = q.job;
    instr.textContent = quizAnswered ? '' : 'Click the part that does this job.';
    if (!quizAnswered) {
        fb.className = 'feedback';
        fb.textContent = '';
    }
    nextBtn.classList.remove('hidden');
    nextBtn.disabled = !quizAnswered;
    nextBtn.textContent = quizIndex === quizQuestions.length - 1 ? 'See results' : 'Next question';
}

function answerQuiz(clickedId) {
    if (quizAnswered || quizFinished) return;   // one attempt per question
    const q = quizQuestions[quizIndex];
    const correct = clickedId === q.answer;
    const p = partById(q.answer);
    quizAnswered = true;
    if (correct) quizScore++;
    quizResults.push({ q: q, clicked: clickedId, correct: correct });

    // reveal: correct part green; a wrong click orange
    resetColors();
    setNodeColor(q.answer, colors.correct, 4);
    if (!correct) setNodeColor(clickedId, colors.wrong, 4);

    const fb = document.getElementById('quiz-feedback');
    fb.className = 'feedback ' + (correct ? 'correct' : 'incorrect');
    fb.textContent = correct ? 'Correct: ' + p.job :
        'Not quite. The part that does this is the ' + p.name + ': ' + p.job;
    renderQuiz();
}

function nextQuestion() {
    if (!quizAnswered) return;
    if (quizIndex < quizQuestions.length - 1) {
        quizIndex++;
        quizAnswered = false;
        resetColors();
    } else {
        quizFinished = true;
        resetColors();
    }
    renderQuiz();
}

// ===========================================
// MODE SWITCHING AND CLICKS
// ===========================================
function setMode(m) {
    mode = m;
    document.getElementById('explore-btn').classList.toggle('active', m === 'explore');
    document.getElementById('quiz-btn').classList.toggle('active', m === 'quiz');
    document.getElementById('explore-panel').classList.toggle('hidden', m !== 'explore');
    document.getElementById('quiz-panel').classList.toggle('hidden', m !== 'quiz');
    network.unselectAll();
    if (m === 'quiz') {
        selectedId = null;
        startQuiz();
    } else {
        clearSelection();
    }
}

function onPartClicked(id) {
    if (mode === 'explore') {
        selectedId = id;
        highlightPart(id);
        showPartInfo(id, true);
    } else {
        network.unselectAll();
        answerQuiz(id);
    }
}

document.addEventListener('DOMContentLoaded', function () {
    initializeNetwork();
    showInstruction();
    document.getElementById('explore-btn').addEventListener('click', () => setMode('explore'));
    document.getElementById('quiz-btn').addEventListener('click', () => setMode('quiz'));
    document.getElementById('next-btn').addEventListener('click', nextQuestion);
    document.getElementById('restart-btn').addEventListener('click', startQuiz);
    document.getElementById('reveal-btn').addEventListener('click', () => {
        document.getElementById('check-answer').textContent =
            'The buddy server. The Pico sends requests and receives replies over Wi-Fi on the school network.';
    });
});
