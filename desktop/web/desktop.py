"""NyxOS Desktop — browser-based windowed environment."""


def render_desktop():
    return r"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>NyxOS</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
html,body { height:100%; overflow:hidden; font-family:'Segoe UI',system-ui,sans-serif; }
body { background:#1a1a2e; color:#e0e0e0; }

/* ---------- BOOT ---------- */
#boot { position:fixed; inset:0; background:#000; color:#0f0; font-family:'Courier New',monospace;
        font-size:14px; padding:30px; z-index:9999; overflow:hidden; }
#boot pre { line-height:1.4; }
.boot-logo { color:#58a6ff; font-size:28px; font-weight:bold; margin-bottom:20px;
             font-family:'Segoe UI',sans-serif; }

/* ---------- LOGIN ---------- */
#login { position:fixed; inset:0; z-index:9998; display:flex; align-items:center;
         justify-content:center; background:linear-gradient(135deg,#1a1a2e 0%,#0f3460 100%); }
.login-box { text-align:center; }
.login-logo { font-size:80px; margin-bottom:20px; }
.login-name { color:#58a6ff; font-size:36px; font-weight:bold; margin-bottom:40px; letter-spacing:2px; }
.login-user { display:flex; flex-direction:column; align-items:center; gap:15px; }
.login-avatar { width:80px; height:80px; border-radius:50%; background:#0f3460; border:3px solid #58a6ff;
                display:flex; align-items:center; justify-content:center; font-size:36px; }
.login-input { background:rgba(255,255,255,0.1); border:1px solid #58a6ff; color:white;
               padding:10px 20px; border-radius:20px; text-align:center; font-size:16px; width:250px; }
.login-btn { background:#58a6ff; color:#000; border:none; padding:10px 40px; border-radius:20px;
             font-size:16px; cursor:pointer; font-weight:bold; }
.login-btn:hover { background:#79c0ff; }

/* ---------- DESKTOP ---------- */
#desktop { display:none; height:100%; position:relative;
           background:url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920') center/cover;
           background-color:#0d1117; }
#desktop.active { display:block; }
.overlay { position:absolute; inset:0; background:rgba(13,17,23,0.55); }

/* ---------- TOP PANEL ---------- */
.topbar { position:absolute; top:0; left:0; right:0; height:32px; background:rgba(0,0,0,0.75);
          display:flex; align-items:center; padding:0 15px; font-size:13px; z-index:100;
          backdrop-filter:blur(10px); border-bottom:1px solid rgba(88,166,255,0.2); }
.topbar .activity { color:#58a6ff; font-weight:bold; cursor:pointer; padding:0 12px; }
.topbar .activity:hover { background:rgba(88,166,255,0.2); border-radius:4px; }
.topbar .title { flex:1; text-align:center; color:#c9d1d9; }
.topbar .right { display:flex; gap:15px; color:#8b949e; align-items:center; }
.topbar .clock { color:#c9d1d9; }

/* ---------- START MENU ---------- */
#startmenu { position:absolute; top:32px; left:10px; width:520px; max-height:70vh; overflow-y:auto;
             background:rgba(22,27,34,0.98); border:1px solid #30363d; border-radius:12px;
             padding:20px; display:none; z-index:200; backdrop-filter:blur(20px); }
#startmenu.open { display:block; }
#startmenu h3 { color:#58a6ff; font-size:14px; margin-bottom:15px; text-transform:uppercase;
                letter-spacing:1px; }
.app-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; }
.app-item { padding:12px 8px; text-align:center; border-radius:8px; cursor:pointer;
            transition:0.15s; }
.app-item:hover { background:rgba(88,166,255,0.15); }
.app-item .ico { font-size:26px; margin-bottom:6px; }
.app-item .lbl { color:#c9d1d9; font-size:11px; }

/* ---------- WINDOWS ---------- */
.window { position:absolute; background:#161b22; border:1px solid #30363d; border-radius:10px;
          box-shadow:0 20px 60px rgba(0,0,0,0.6); min-width:500px; min-height:300px;
          display:flex; flex-direction:column; overflow:hidden; resize:both; }
.window.focused { border-color:#58a6ff; }
.titlebar { background:linear-gradient(180deg,#21262d,#161b22); padding:10px 15px;
            display:flex; align-items:center; cursor:move; user-select:none;
            border-bottom:1px solid #30363d; }
.titlebar .wt { color:#c9d1d9; font-size:13px; font-weight:600; flex:1; }
.titlebar .wbtns { display:flex; gap:8px; }
.wbtn { width:14px; height:14px; border-radius:50%; cursor:pointer; border:none; }
.wbtn.close { background:#ff5f56; }
.wbtn.min { background:#ffbd2e; }
.wbtn.max { background:#27c93f; }
.wbody { padding:20px; overflow:auto; flex:1; font-size:14px; }
.wbody input, .wbody select { background:#0d1117; color:#c9d1d9; border:1px solid #30363d;
                              padding:8px; border-radius:6px; font-size:14px; }
.wbody button { background:#238636; color:white; padding:8px 18px; border:none;
                border-radius:6px; cursor:pointer; font-size:14px; }
.wbody button:hover { background:#2ea043; }
.wbody pre { background:#0d1117; padding:15px; border-radius:6px; overflow:auto;
             max-height:400px; font-size:12px; border:1px solid #30363d;
             white-space:pre-wrap; word-break:break-word; color:#c9d1d9; font-family:'Courier New',monospace; }
.wbody table { width:100%; border-collapse:collapse; }
.wbody th, .wbody td { text-align:left; padding:8px; border-bottom:1px solid #30363d; font-size:13px; }
.wbody th { color:#8b949e; font-size:11px; text-transform:uppercase; }
.badge { padding:2px 6px; border-radius:3px; font-size:10px; font-weight:bold; }
.critical{background:#7d0c0c;} .high{background:#a33;} .medium{background:#a70;}
.low{background:#365314;} .info{background:#1f4f8b;}

/* ---------- TERMINAL ---------- */
.term { background:#000; font-family:'Courier New',monospace; font-size:13px;
        color:#c9d1d9; padding:15px; height:100%; overflow:auto; }
.term .line { white-space:pre-wrap; word-break:break-word; }
.term .prompt { color:#58a6ff; }
.term-input { background:transparent; border:none; outline:none; color:#c9d1d9;
              font-family:'Courier New',monospace; font-size:13px; width:80%; }

/* ---------- TASKBAR (bottom) ---------- */
.taskbar { position:absolute; bottom:0; left:0; right:0; height:48px; background:rgba(0,0,0,0.8);
           backdrop-filter:blur(10px); border-top:1px solid rgba(88,166,255,0.2);
           display:flex; align-items:center; padding:0 15px; gap:10px; z-index:100; }
.taskbar .tb-app { padding:8px 14px; border-radius:6px; color:#c9d1d9; cursor:pointer;
                   font-size:13px; background:rgba(255,255,255,0.05); }
.taskbar .tb-app:hover { background:rgba(88,166,255,0.2); }
.taskbar .tb-start { background:#58a6ff; color:#000; font-weight:bold; }

/* Icon glyphs */
.g { font-family:'Segoe UI Emoji',sans-serif; }
</style></head>
<body>

<!-- BOOT SCREEN -->
<div id="boot">
  <div class="boot-logo">&#x1F6E1;&#xFE0F; NyxOS 0.1.0</div>
  <pre id="bootlog"></pre>
</div>

<!-- LOGIN SCREEN -->
<div id="login">
  <div class="login-box">
    <div class="login-logo">&#x1F6E1;&#xFE0F;</div>
    <div class="login-name">NyxOS</div>
    <div class="login-user">
      <div class="login-avatar">&#x1F464;</div>
      <input class="login-input" id="userInput" value="analyst" readonly>
      <button class="login-btn" onclick="login()">Sign In</button>
    </div>
  </div>
</div>

<!-- DESKTOP -->
<div id="desktop">
  <div class="overlay"></div>

  <div class="topbar">
    <div class="activity" onclick="toggleStart()">&#x1F6E1;&#xFE0F; Activities</div>
    <div class="title">NyxOS</div>
    <div class="right">
      <span>&#x1F4E1;</span>
      <span>&#x1F50A;</span>
      <span>&#x1F50B;</span>
      <span class="clock" id="clock"></span>
    </div>
  </div>

  <div id="startmenu">
    <h3>Applications</h3>
    <div class="app-grid" id="appGrid"></div>
  </div>

  <div class="taskbar" id="taskbar">
    <div class="tb-app tb-start" onclick="toggleStart()">&#x1F6E1;&#xFE0F; Start</div>
  </div>
</div>

<script>
const APPS = [
  {id:'terminal', label:'Terminal', icon:'&#x2328;&#xFE0F;'},
  {id:'cases', label:'Cases', icon:'&#x1F4C1;'},
  {id:'recon', label:'Recon', icon:'&#x1F50D;'},
  {id:'network', label:'Network', icon:'&#x1F310;'},
  {id:'web', label:'Web', icon:'&#x1F578;&#xFE0F;'},
  {id:'vulnerability', label:'Vuln Scan', icon:'&#x26A0;&#xFE0F;'},
  {id:'credentials', label:'Credentials', icon:'&#x1F511;'},
  {id:'forensics', label:'Forensics', icon:'&#x1F50E;'},
  {id:'wireless', label:'Wireless', icon:'&#x1F4F6;'},
  {id:'redteam', label:'Red Team', icon:'&#x1F3AF;'},
  {id:'findings', label:'Findings', icon:'&#x1F4CB;'},
  {id:'assets', label:'Assets', icon:'&#x1F5C2;&#xFE0F;'},
  {id:'timeline', label:'Timeline', icon:'&#x23F1;&#xFE0F;'},
  {id:'ai', label:'AI Assistant', icon:'&#x1F916;'},
  {id:'reports', label:'Reports', icon:'&#x1F4C4;'},
  {id:'about', label:'About', icon:'&#x2139;&#xFE0F;'},
];

// ---------- BOOT ----------
const BOOT_LINES = [
  '[    0.000000] NyxOS kernel 6.1.0-nyx booting...',
  '[    0.001234] Command line: BOOT_IMAGE=/boot/vmlinuz root=UUID=nyx-root quiet',
  '[    0.012345] Memory: 3.0GiB available',
  '[    0.023456] CPU: x86_64, 2 cores',
  '[    0.045678] ACPI: Core revision 20230331',
  '[    0.067890] PCI: Probing PCI hardware',
  '[    0.123456] usbcore: registered new interface driver usbfs',
  '[    0.234567] systemd[1]: NyxOS systemd 252 running',
  '[    0.345678] systemd[1]: Reached target Basic System',
  '[    0.456789] systemd[1]: Started NyxOS Core Daemon (nyxosd)',
  '[    0.567890] nyxosd: initializing database...',
  '[    0.678901] nyxosd: loading 25 workbenches...',
  '[    0.789012] nyxosd: loading tool adapters...',
  '[    0.890123] nyxosd: loading plugin registry...',
  '[    1.000000] systemd[1]: Reached target Multi-User System',
  '[    1.100000] systemd[1]: Started NyxOS Desktop Manager',
  '[    1.234567] nyx:  Welcome to NyxOS',
];
let li = 0;
function bootStep() {
  if (li < BOOT_LINES.length) {
    document.getElementById('bootlog').textContent += BOOT_LINES[li] + '\n';
    li++;
    setTimeout(bootStep, 120);
  } else {
    setTimeout(() => {
      document.getElementById('boot').style.display = 'none';
    }, 600);
  }
}
bootStep();

// ---------- CLOCK ----------
function tick() {
  const d = new Date();
  document.getElementById('clock').textContent =
    d.toLocaleDateString() + ' ' + d.toLocaleTimeString();
}
setInterval(tick, 1000); tick();

// ---------- LOGIN ----------
function login() {
  document.getElementById('login').style.display = 'none';
  document.getElementById('desktop').classList.add('active');
  buildStartMenu();
  setTimeout(openApp.bind(null,'terminal'), 400);
}

// ---------- START MENU ----------
function buildStartMenu() {
  const grid = document.getElementById('appGrid');
  grid.innerHTML = '';
  APPS.forEach(a => {
    const el = document.createElement('div');
    el.className = 'app-item';
    el.innerHTML = `<div class="ico g">${a.icon}</div><div class="lbl">${a.label}</div>`;
    el.onclick = () => { toggleStart(false); openApp(a.id); };
    grid.appendChild(el);
  });
}
function toggleStart(force) {
  const m = document.getElementById('startmenu');
  if (force === false) m.classList.remove('open');
  else m.classList.toggle('open');
}

// ---------- WINDOW MANAGER ----------
let zTop = 100;
function makeWindow(title, bodyHtml, opts) {
  opts = opts || {};
  const w = document.createElement('div');
  w.className = 'window focused';
  const offset = (document.querySelectorAll('.window').length % 8) * 40;
  w.style.left = (100 + offset) + 'px';
  w.style.top = (60 + offset) + 'px';
  w.style.width = (opts.width || 700) + 'px';
  w.style.height = (opts.height || 500) + 'px';
  w.style.zIndex = ++zTop;
  w.innerHTML = `
    <div class="titlebar">
      <div class="wt">${title}</div>
      <div class="wbtns">
        <button class="wbtn min" onclick="this.closest('.window').style.display='none'"></button>
        <button class="wbtn max"></button>
        <button class="wbtn close" onclick="this.closest('.window').remove()"></button>
      </div>
    </div>
    <div class="wbody">${bodyHtml}</div>`;
  document.getElementById('desktop').appendChild(w);
  w.addEventListener('mousedown', () => {
    document.querySelectorAll('.window').forEach(x => x.classList.remove('focused'));
    w.classList.add('focused'); w.style.zIndex = ++zTop;
  });
  dragify(w);
  return w;
}

function dragify(w) {
  const tb = w.querySelector('.titlebar');
  let sx, sy, ox, oy, dragging = false;
  tb.addEventListener('mousedown', e => {
    if (e.target.classList.contains('wbtn')) return;
    dragging = true;
    sx = e.clientX; sy = e.clientY;
    ox = w.offsetLeft; oy = w.offsetTop;
  });
  document.addEventListener('mousemove', e => {
    if (!dragging) return;
    w.style.left = (ox + e.clientX - sx) + 'px';
    w.style.top = (oy + e.clientY - sy) + 'px';
  });
  document.addEventListener('mouseup', () => dragging = false);
}

// ---------- APPS ----------
async function openApp(id) {
  if (id === 'terminal') return openTerminal();
  if (id === 'about') return openAbout();
  if (id === 'cases') return openCases();
  if (id === 'findings') return openFindings();
  if (id === 'assets') return openAssets();
  if (id === 'timeline') return openTimeline();
  if (id === 'ai') return openAI();
  if (id === 'reports') return openReports();
  // workbenches
  return openWorkbench(id);
}

function openAbout() {
  makeWindow('About NyxOS', `
    <h2 style="color:#58a6ff;">&#x1F6E1;&#xFE0F; NyxOS 0.1.0</h2>
    <p>An installable, Linux-based Cybersecurity Operating Platform.</p>
    <p style="color:#8b949e;font-size:13px;margin-top:15px;">
      Built on Debian bookworm. 25 security domains. Local-first.<br>
      Not a Kali clone — a unified security platform.
    </p>
    <p style="margin-top:20px;">
      <b>Workbenches:</b> 25<br>
      <b>Tool adapters:</b> 15+<br>
      <b>Data model:</b> unified<br>
      <b>Reports:</b> HTML/PDF, Markdown, JSON<br>
    </p>
  `, {width:520, height:420});
}

async function openCases() {
  const r = await fetch('/api/cases').then(x=>x.json());
  let rows = r.cases.map(c =>
    `<tr><td>${c.id}</td><td>${c.name}</td><td>${c.status}</td>
     <td><a href="/report-html?case=${c.id}" target="_blank" style="color:#58a6ff;">report</a></td></tr>`
  ).join('') || '<tr><td colspan="4" style="color:#8b949e;">No cases yet.</td></tr>';
  const w = makeWindow('Cases', `
    <div style="display:flex;gap:10px;margin-bottom:15px;">
      <input id="cn" placeholder="New case name" style="flex:1;">
      <button onclick="createCase()">Create</button>
    </div>
    <table>
      <tr><th>ID</th><th>Name</th><th>Status</th><th>Report</th></tr>
      ${rows}
    </table>
  `);
}

async function createCase() {
  const n = document.getElementById('cn').value.trim();
  if (!n) return;
  await fetch('/api/case', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({name:n})});
  document.querySelectorAll('.window').forEach(w => {
    if (w.querySelector('.wt').textContent === 'Cases') w.remove();
  });
  openCases();
}

async function openWorkbench(name) {
  const r = await fetch('/api/cases').then(x=>x.json());
  const opts = r.cases.map(c => `<option value="${c.id}">${c.id}: ${c.name}</option>`).join('')
    || '<option value="">Create a case first</option>';
  const ph = name === 'forensics' ? '/etc/hostname'
           : name === 'credentials' ? 'paste hash here'
           : 'target (IP, domain, URL)';
  const w = makeWindow(name.charAt(0).toUpperCase()+name.slice(1)+' Workbench', `
    <div style="display:flex;gap:10px;margin-bottom:15px;flex-wrap:wrap;">
      <select id="cid_${name}">${opts}</select>
      <input id="tgt_${name}" placeholder="${ph}" style="flex:1;min-width:200px;">
      <button onclick="runWB('${name}')">Run</button>
    </div>
    <div id="out_${name}" style="color:#8b949e;font-size:13px;">Ready.</div>
  `, {width:800, height:520});
}

async function runWB(name) {
  const cid = document.getElementById('cid_'+name).value;
  const tgt = document.getElementById('tgt_'+name).value;
  const out = document.getElementById('out_'+name);
  out.innerHTML = '<span style="color:#58a6ff;">Running...</span>';
  try {
    const r = await fetch('/api/workbench/'+name, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({case_id: parseInt(cid), target: tgt})
    }).then(x=>x.json());
    out.innerHTML = '<pre>'+JSON.stringify(r,null,2)+'</pre>';
  } catch(e) {
    out.innerHTML = '<pre style="color:#da3633;">'+e+'</pre>';
  }
}

async function openFindings() {
  const r = await fetch('/api/findings').then(x=>x.json());
  const rows = r.findings.map(f =>
    `<tr><td>${f.id}</td><td>${f.title}</td>
     <td><span class="badge ${f.severity}">${f.severity}</span></td>
     <td>${f.risk_score}</td></tr>`
  ).join('') || '<tr><td colspan="4" style="color:#8b949e;">None yet.</td></tr>';
  makeWindow('Findings', `
    <table><tr><th>ID</th><th>Title</th><th>Sev</th><th>Risk</th></tr>${rows}</table>
  `, {width:750, height:500});
}

async function openAssets() {
  const r = await fetch('/api/assets').then(x=>x.json());
  const rows = r.assets.map(a =>
    `<tr><td>${a.id}</td><td>${a.type}</td><td>${a.identifier}</td></tr>`
  ).join('') || '<tr><td colspan="3" style="color:#8b949e;">None yet.</td></tr>';
  makeWindow('Assets', `
    <table><tr><th>ID</th><th>Type</th><th>Identifier</th></tr>${rows}</table>
  `, {width:700, height:450});
}

async function openTimeline() {
  const r = await fetch('/api/events').then(x=>x.json());
  const rows = r.events.map(e =>
    `<tr><td>${e.id}</td><td>${e.created_at.slice(0,19)}</td>
     <td><code>${e.topic}</code></td></tr>`
  ).join('') || '<tr><td colspan="3" style="color:#8b949e;">No events.</td></tr>';
  makeWindow('Timeline', `
    <table><tr><th>ID</th><th>Time</th><th>Topic</th></tr>${rows}</table>
  `, {width:750, height:500});
}

function openAI() {
  const w = makeWindow('AI Assistant', `
    <div style="display:flex;gap:10px;margin-bottom:15px;">
      <input id="aiq" placeholder="Ask: nmap, sqlmap, next steps..." style="flex:1;">
      <button onclick="askAI()">Ask</button>
    </div>
    <div id="aiout" style="color:#8b949e;font-size:13px;">Ask a question.</div>
  `, {width:700, height:450});
}
async function askAI() {
  const q = document.getElementById('aiq').value;
  const out = document.getElementById('aiout');
  out.innerHTML = '<span style="color:#58a6ff;">Thinking...</span>';
  const r = await fetch('/api/ai?q='+encodeURIComponent(q)).then(x=>x.json());
  out.innerHTML = '<pre>'+JSON.stringify(r,null,2)+'</pre>';
}

async function openReports() {
  const r = await fetch('/api/cases').then(x=>x.json());
  const rows = r.cases.map(c =>
    `<tr><td>${c.id}</td><td>${c.name}</td>
     <td><a href="/report-html?case=${c.id}" target="_blank" style="color:#58a6ff;">HTML/PDF</a> |
     <a href="/report-md?case=${c.id}" target="_blank" style="color:#58a6ff;">md</a> |
     <a href="/report-json?case=${c.id}" target="_blank" style="color:#58a6ff;">json</a></td></tr>`
  ).join('') || '<tr><td colspan="3" style="color:#8b949e;">No cases.</td></tr>';
  makeWindow('Reports', `
    <table><tr><th>ID</th><th>Case</th><th>Export</th></tr>${rows}</table>
  `, {width:700, height:450});
}

// ---------- TERMINAL ----------
function openTerminal() {
  const w = makeWindow('Terminal — nyx@nyxos:~', `
    <div class="term" id="termout"></div>
    <div class="term" style="padding-top:0;">
      <span class="prompt">nyx@nyxos:~$</span>
      <input class="term-input" id="termin" autofocus>
    </div>
  `, {width:800, height:500});
  const out = w.querySelector('#termout');
  const input = w.querySelector('#termin');
  const history = [];
  let histIdx = -1;

  function line(txt, cls) {
    const d = document.createElement('div');
    d.className = 'line ' + (cls || '');
    d.textContent = txt;
    out.appendChild(d);
    out.scrollTop = out.scrollHeight;
  }

  line('NyxOS 0.1.0 (Debian bookworm 6.1.0) — type "help" for commands');
  line('');

  input.addEventListener('keydown', async e => {
    if (e.key === 'Enter') {
      const cmd = input.value.trim();
      input.value = '';
      line('nyx@nyxos:~$ ' + cmd, 'prompt');
      if (!cmd) return;
      history.push(cmd); histIdx = history.length;
      if (cmd === 'clear') { out.innerHTML = ''; return; }
      if (cmd === 'help') {
        line('Available commands:');
        line('  help              — this message');
        line('  ls-workbenches    — list all 25 security workbenches');
        line('  case-list         — list cases');
        line('  case-create <n>   — create a case');
        line('  run <wb> <tgt>    — run a workbench (needs case selected)');
        line('  findings          — list findings');
        line('  clear             — clear screen');
        line('  about             — about NyxOS');
        line('  exit              — close terminal');
        return;
      }
      if (cmd === 'about') {
        line('NyxOS 0.1.0 — Cybersecurity Operating Platform');
        line('Built on Debian. Local-first. 25 security domains.');
        return;
      }
      if (cmd === 'ls-workbenches' || cmd === 'ls') {
        const r = await fetch('/api/workbenches').then(x=>x.json());
        r.workbenches.forEach(w => line('  ' + w.name.padEnd(15) + ' ' + w.domain));
        return;
      }
      if (cmd === 'case-list') {
        const r = await fetch('/api/cases').then(x=>x.json());
        if (!r.cases.length) { line('(no cases)'); return; }
        r.cases.forEach(c => line(`  #${c.id}  ${c.name}  [${c.status}]`));
        return;
      }
      if (cmd.startsWith('case-create ')) {
        const name = cmd.slice(12).trim();
        await fetch('/api/case', {method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({name})});
        line(`Case created: ${name}`);
        return;
      }
      if (cmd === 'findings') {
        const r = await fetch('/api/findings').then(x=>x.json());
        if (!r.findings.length) { line('(no findings)'); return; }
        r.findings.forEach(f => line(`  [${f.severity.toUpperCase()}] ${f.title} (risk=${f.risk_score})`));
        return;
      }
      if (cmd.startsWith('run ')) {
        const [_, wb, ...t] = cmd.split(' ');
        const target = t.join(' ');
        const cases = await fetch('/api/cases').then(x=>x.json());
        if (!cases.cases.length) { line('Error: create a case first (case-create <name>)'); return; }
        const cid = cases.cases[0].id;
        line(`Running ${wb} on ${target} (case #${cid})...`);
        const r = await fetch('/api/workbench/'+wb, {
          method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({case_id: cid, target})
        }).then(x=>x.json());
        line(JSON.stringify(r, null, 2));
        return;
      }
      if (cmd === 'exit') { w.remove(); return; }
      line('bash: ' + cmd + ': command not found');
    } else if (e.key === 'ArrowUp') {
      if (histIdx > 0) { histIdx--; input.value = history[histIdx]; }
      e.preventDefault();
    } else if (e.key === 'ArrowDown') {
      if (histIdx < history.length - 1) { histIdx++; input.value = history[histIdx]; }
      else { histIdx = history.length; input.value = ''; }
      e.preventDefault();
    }
  });

  w.addEventListener('click', () => input.focus());
  setTimeout(() => input.focus(), 100);
}
</script>
</body></html>"""
