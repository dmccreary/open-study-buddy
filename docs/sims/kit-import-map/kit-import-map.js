// Kit Import Map - vis-network
// CANVAS_HEIGHT: 560
// Shows the 8 kit files of src/kits/study-buddy-base/ with an arrow from each
// importing file to each file it imports, grouped by their folder on the Pico.
// The learner clicks files to read their folder and purpose, then answers a
// 5-file import check by selecting the kit files each one imports.
//
// Provenance: the imports were read from the kit source files:
//   03-buttons.py       import config
//   04-hello-world.py   import config, import shapes
//   06-listen-meter.py  import config (plus standard-library math, struct, time)
//   config.py           import gc9b72, vga1_8x16, vga1_bold_16x32 (plus machine)
//   lib/shapes.py, lib/gc9b72.py, lib/vga1_*.py import no kit files
// Standard-library modules are not drawn.

// ===========================================
// DATA
// ===========================================
const files = [
  { id: '03-buttons.py', folder: 'top', desc: 'Test 03, reports button presses', imports: ['config.py'] },
  { id: '04-hello-world.py', folder: 'top', desc: 'Test 04, draws "Hello World!"', imports: ['config.py', 'shapes.py'] },
  { id: '06-listen-meter.py', folder: 'top', desc: 'Test 06, a microphone level meter', imports: ['config.py'] },
  { id: 'config.py', folder: 'top', desc: 'Every pin number and helper function for the kit',
    imports: ['gc9b72.py', 'vga1_8x16.py', 'vga1_bold_16x32.py'] },
  { id: 'shapes.py', folder: 'lib', desc: 'Circles, rings, polygons, sprites', imports: [] },
  { id: 'gc9b72.py', folder: 'lib', desc: 'The display driver', imports: [] },
  { id: 'vga1_8x16.py', folder: 'lib', desc: 'The small 8 by 16 font', imports: [] },
  { id: 'vga1_bold_16x32.py', folder: 'lib', desc: 'The large 16 by 32 font', imports: [] }
];

// Fixed positions. Rows are offset a few pixels so no edge is perfectly horizontal.
const positions = {
  '03-buttons.py': { x: -165, y: -230 },
  '04-hello-world.py': { x: 5, y: -245 },
  '06-listen-meter.py': { x: 175, y: -225 },
  'config.py': { x: -40, y: -95 },
  'gc9b72.py': { x: -195, y: 65 },
  'shapes.py': { x: 185, y: 70 },
  'vga1_8x16.py': { x: -120, y: 175 },
  'vga1_bold_16x32.py': { x: 60, y: 165 }
};

// The 5 files in the check, in order, with a one-sentence reason for the feedback
const checkItems = [
  { file: '03-buttons.py', reason: 'its only arrow goes to config, which supplies the pin numbers' },
  { file: '04-hello-world.py', reason: 'it has one arrow to config for the pins and display and one to shapes for drawing' },
  { file: '06-listen-meter.py', reason: 'math, struct and time are standard-library modules, so config is its only kit import' },
  { file: 'config.py', reason: 'its three arrows go to the display driver and the two fonts in lib' },
  { file: 'shapes.py', reason: 'no arrows leave shapes.py, because it only uses standard-library modules' }
];

const colors = {
  top: { background: 'lightskyblue', border: 'steelblue' },
  lib: { background: 'palegreen', border: 'seagreen' },
  asked: { background: 'gold', border: 'darkgoldenrod' },
  right: { background: 'palegreen', border: 'green' },
  wrong: { background: 'mistyrose', border: 'crimson' }
};

// ===========================================
// STATE
// ===========================================
let nodes, edges, network;
let phase = 'explore';       // 'explore', 'question', 'revealed', 'done'
let itemIndex = 0;
let score = 0;
let lastSelection = [];

// ===========================================
// UTILITIES
// ===========================================
function isInIframe() {
  try { return window.self !== window.top; } catch (e) { return true; }
}

function fileById(id) {
  return files.find(f => f.id === id);
}

function moduleName(id) {
  return id.replace(/\.py$/, '');
}

// "config", "config and shapes", "a, b and c", or "no kit files"
function listText(ids) {
  const names = ids.map(moduleName);
  if (names.length === 0) return 'no kit files';
  if (names.length === 1) return names[0];
  return names.slice(0, -1).join(', ') + ' and ' + names[names.length - 1];
}

// Every file reachable through imports of imports (not counting direct imports)
function indirectImports(id) {
  const direct = new Set(fileById(id).imports);
  const seen = new Set();
  const stack = [...direct];
  while (stack.length) {
    const cur = stack.pop();
    for (const next of fileById(cur).imports) {
      if (!seen.has(next)) { seen.add(next); stack.push(next); }
    }
  }
  return [...seen].filter(x => !direct.has(x));
}

function sameSet(a, b) {
  return a.length === b.length && a.every(x => b.includes(x));
}

// ===========================================
// NETWORK
// ===========================================
function baseNode(f) {
  const c = colors[f.folder];
  return {
    id: f.id,
    label: f.id,
    x: positions[f.id].x,
    y: positions[f.id].y,
    color: { background: c.background, border: c.border,
      highlight: { background: 'gold', border: 'darkgoldenrod' } },
    borderWidth: 2,
    font: { size: 18, face: 'Arial', color: 'black' }
  };
}

function baseEdge(from, to) {
  return {
    id: from + '->' + to,
    from: from,
    to: to,
    color: { color: 'gray', highlight: 'gray' },
    width: 2
  };
}

function initializeNetwork() {
  nodes = new vis.DataSet(files.map(baseNode));
  const edgeList = [];
  for (const f of files) for (const t of f.imports) edgeList.push(baseEdge(f.id, t));
  edges = new vis.DataSet(edgeList);

  const enableMouse = !isInIframe();
  const options = {
    layout: { improvedLayout: false },
    physics: { enabled: false },
    interaction: {
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
      shadow: { enabled: true, color: 'rgba(0,0,0,0.2)', size: 5, x: 2, y: 2 }
    },
    edges: {
      arrows: { to: { enabled: true, scaleFactor: 1.1 } },
      smooth: { type: 'curvedCW', roundness: 0.08 }
    }
  };
  network = new vis.Network(document.getElementById('network'), { nodes: nodes, edges: edges }, options);

  // Folder backgrounds drawn behind the nodes
  network.on('beforeDrawing', drawFolders);
  network.on('click', params => {
    if (params.nodes.length > 0) showFileInfo(params.nodes[0]);
  });
  network.once('afterDrawing', fitView);
  window.addEventListener('resize', fitView);
}

function fitView() {
  network.fit({ animation: false });
  // leave room for the title and legend overlays
  const scale = network.getScale() * 0.92;
  const pos = network.getViewPosition();
  network.moveTo({ position: { x: pos.x, y: pos.y - 30 }, scale: scale, animation: false });
}

function drawFolders(ctx) {
  const groups = [
    { folder: 'top', label: 'Pico top level  /', fill: 'rgba(135, 206, 250, 0.15)', stroke: 'steelblue' },
    { folder: 'lib', label: 'Pico folder  /lib', fill: 'rgba(152, 251, 152, 0.18)', stroke: 'seagreen' }
  ];
  for (const g of groups) {
    let box = null;
    for (const f of files.filter(x => x.folder === g.folder)) {
      const b = network.getBoundingBox(f.id);
      if (!b) continue;
      box = box ? { left: Math.min(box.left, b.left), right: Math.max(box.right, b.right),
        top: Math.min(box.top, b.top), bottom: Math.max(box.bottom, b.bottom) } : { ...b };
    }
    if (!box) continue;
    const pad = 22;
    const x = box.left - pad, y = box.top - pad - 18;
    const w = box.right - box.left + 2 * pad, h = box.bottom - box.top + 2 * pad + 18;
    ctx.save();
    ctx.fillStyle = g.fill;
    ctx.strokeStyle = g.stroke;
    ctx.setLineDash([8, 6]);
    ctx.lineWidth = 2;
    ctx.beginPath();
    if (ctx.roundRect) ctx.roundRect(x, y, w, h, 14); else ctx.rect(x, y, w, h);
    ctx.fill();
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = g.stroke;
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'top';
    ctx.fillText(g.label, x + w - 10, y + 6);
    ctx.restore();
  }
}

function resetHighlights() {
  nodes.update(files.map(f => ({ id: f.id, color: baseNode(f).color, borderWidth: 2 })));
  edges.update(edges.getIds().map(id => ({ id: id, color: { color: 'gray', highlight: 'gray' }, width: 2 })));
}

function highlightAsked(fileId) {
  resetHighlights();
  nodes.update({ id: fileId, color: { background: colors.asked.background, border: colors.asked.border,
    highlight: { background: 'gold', border: 'darkgoldenrod' } }, borderWidth: 4 });
}

function revealArrows(fileId, selection) {
  const correct = fileById(fileId).imports;
  for (const t of correct) {
    edges.update({ id: fileId + '->' + t, color: { color: 'green', highlight: 'green' }, width: 5 });
    nodes.update({ id: t, color: { background: colors.right.background, border: colors.right.border,
      highlight: { background: 'gold', border: 'darkgoldenrod' } }, borderWidth: 4 });
  }
  for (const s of selection.filter(x => !correct.includes(x))) {
    nodes.update({ id: s, color: { background: colors.wrong.background, border: colors.wrong.border,
      highlight: { background: 'gold', border: 'darkgoldenrod' } }, borderWidth: 4 });
  }
}

// ===========================================
// PANEL
// ===========================================
function showFileInfo(id) {
  const f = fileById(id);
  document.getElementById('info-title').textContent = f.id;
  const folder = f.folder === 'top' ? 'top level ( / )' : '/lib';
  document.getElementById('info-content').innerHTML =
    '<div><strong>Pico folder:</strong> ' + folder + '</div><div>' + f.desc + '.</div>';
}

function buildChoices(askedId) {
  const box = document.getElementById('choices');
  box.innerHTML = '';
  for (const f of files) {
    const label = document.createElement('label');
    const cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.value = f.id;
    if (f.id === askedId) {
      cb.disabled = true;
      label.classList.add('self');
    }
    label.appendChild(cb);
    label.appendChild(document.createTextNode(f.id));
    box.appendChild(label);
  }
}

function currentSelection() {
  return [...document.querySelectorAll('#choices input:checked')].map(cb => cb.value);
}

function markChoices(correct, selection) {
  document.querySelectorAll('#choices label').forEach(label => {
    const cb = label.querySelector('input');
    cb.disabled = true;
    if (correct.includes(cb.value)) label.classList.add('right');
    else if (selection.includes(cb.value)) label.classList.add('wrong');
  });
}

function setFeedback(text, cls) {
  const fb = document.getElementById('feedback');
  fb.textContent = text;
  fb.className = 'feedback' + (cls ? ' ' + cls : '');
}

function updateScore() {
  document.getElementById('score').textContent = phase === 'explore' ? '' : 'Score: ' + score + ' of 5';
}

function showQuestion() {
  const item = checkItems[itemIndex];
  phase = 'question';
  document.getElementById('question').textContent =
    'File ' + (itemIndex + 1) + ' of 5: which kit files does ' + item.file + ' import?';
  document.getElementById('hint').textContent = 'Select every file it imports (or none), then press Submit.';
  buildChoices(item.file);
  setFeedback('', '');
  highlightAsked(item.file);
  showFileInfo(item.file);
  const btn = document.getElementById('action-btn');
  btn.textContent = 'Submit';
  updateScore();
}

function submitAnswer() {
  const item = checkItems[itemIndex];
  const correct = fileById(item.file).imports;
  const selection = currentSelection();
  lastSelection = selection;
  const list = listText(correct);
  if (sameSet(selection, correct)) {
    score++;
    setFeedback('Correct: ' + item.file + ' imports ' + list + '.', 'correct');
  } else {
    // A chosen file that is only reached through another import gets the transitive-import reason
    const indirect = indirectImports(item.file);
    const reason = selection.some(s => indirect.includes(s))
      ? 'a file imports only what its own arrows point to, not what its imports import'
      : item.reason;
    setFeedback('Not quite. ' + item.file + ' imports ' + list + '; ' + reason + '.', 'incorrect');
  }
  markChoices(correct, selection);
  revealArrows(item.file, selection);
  phase = 'revealed';
  document.getElementById('action-btn').textContent = itemIndex === checkItems.length - 1 ? 'Show score' : 'Next file';
  updateScore();
}

function showDone() {
  phase = 'done';
  resetHighlights();
  document.getElementById('question').textContent =
    'Check complete. Score: ' + score + ' of 5' + (score >= 4 ? ' (mastery reached).' : ' (mastery is 4 of 5).');
  document.getElementById('hint').textContent =
    'Tests and config.py sit at the top level; the display driver, fonts and shapes live in /lib.';
  document.getElementById('choices').innerHTML = '';
  setFeedback('', '');
  document.getElementById('action-btn').textContent = 'Start check again';
  updateScore();
}

function actionButton() {
  if (phase === 'explore' || phase === 'done') {
    itemIndex = 0;
    score = 0;
    showQuestion();
  } else if (phase === 'question') {
    submitAnswer();
  } else if (phase === 'revealed') {
    if (itemIndex === checkItems.length - 1) {
      showDone();
    } else {
      itemIndex++;
      showQuestion();
    }
  }
}

// ===========================================
// INITIALIZATION
// ===========================================
document.addEventListener('DOMContentLoaded', function () {
  initializeNetwork();
  document.getElementById('action-btn').addEventListener('click', actionButton);
  updateScore();
});
