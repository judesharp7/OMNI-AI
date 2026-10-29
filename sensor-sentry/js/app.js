/* ===== SENSOR SENTRY — CORE ENGINE ===== */

// ── CONFIG ──────────────────────────────────────────────
const SENSORS = [
  { id: 'TMP-01', name: 'Temperature',     unit: '°C',  base: 72,   noise: 3,   spike: 18,  color: '#00d9ff', accentColor: '#ff9f1c' },
  { id: 'PRS-02', name: 'Pressure',        unit: 'PSI', base: 145,  noise: 5,   spike: 35,  color: '#a855f7', accentColor: '#ff3860' },
  { id: 'VBR-03', name: 'Vibration',       unit: 'mm/s',base: 2.1,  noise: 0.4, spike: 3.5, color: '#00ff87', accentColor: '#ff3860' },
  { id: 'HUM-04', name: 'Humidity',        unit: '%RH', base: 55,   noise: 4,   spike: 22,  color: '#ffaa00', accentColor: '#ff3860' },
  { id: 'CUR-05', name: 'Current Draw',    unit: 'A',   base: 12.4, noise: 0.8, spike: 6,   color: '#38bdf8', accentColor: '#ff3860' },
  { id: 'FLW-06', name: 'Flow Rate',       unit: 'L/m', base: 88,   noise: 6,   spike: 40,  color: '#f472b6', accentColor: '#ff3860' },
];

const WINDOW = 50;       // sliding window for Z-score
const Z_CRITICAL = 3.0;  // critical anomaly threshold
const Z_WARNING  = 2.0;  // warning threshold
const TICK_MS    = 800;  // data update interval

// ── STATE ───────────────────────────────────────────────
const state = {
  history: SENSORS.map(() => []),   // raw values per sensor
  zScores: SENSORS.map(() => 0),
  anomalies: 0,
  events: 0,
  alertCount: 0,
  paused: false,
  chartSensor: 0,
  chartData: [],
  anomalyLog: [],
  distCounts: [0, 0, 0, 0, 0, 0],  // per sensor anomaly counts
  lastMinuteAnomalies: [],
  startTime: Date.now(),
};

// ── BOOT SEQUENCE ────────────────────────────────────────
const bootMessages = [
  'Initializing anomaly detection engine...',
  'Loading Z-score algorithm modules...',
  'Connecting to sensor network...',
  'Calibrating sliding window (50 samples)...',
  'Establishing Telegram alert bridge...',
  'Mounting real-time dashboard...',
  'System ready. Monitoring active.',
];

let bootIdx = 0;
const bootBar = document.getElementById('boot-bar');
const bootStatus = document.getElementById('boot-status');
const bootOverlay = document.getElementById('boot-overlay');

function runBoot() {
  const step = () => {
    if (bootIdx >= bootMessages.length) {
      setTimeout(() => {
        bootOverlay.classList.add('hidden');
        setTimeout(() => { bootOverlay.style.display = 'none'; init(); }, 700);
      }, 300);
      return;
    }
    bootStatus.textContent = bootMessages[bootIdx];
    bootBar.style.width = ((bootIdx + 1) / bootMessages.length * 100) + '%';
    bootIdx++;
    setTimeout(step, 250 + Math.random() * 200);
  };
  step();
}

// ── INIT ─────────────────────────────────────────────────
function init() {
  renderSensorCards();
  renderGauges();
  initMainChart();
  initDistChart();
  updateClock();
  setInterval(updateClock, 1000);
  setInterval(tick, TICK_MS);
}

// ── CLOCK ────────────────────────────────────────────────
function updateClock() {
  const now = new Date();
  document.getElementById('system-time').textContent =
    now.toTimeString().slice(0, 8);
  document.getElementById('system-date').textContent =
    now.toDateString().toUpperCase();
}

// ── SENSOR CARDS ─────────────────────────────────────────
function renderSensorCards() {
  const grid = document.getElementById('sensor-grid');
  grid.innerHTML = SENSORS.map((s, i) => `
    <div class="sensor-card" id="sc-${i}">
      <div class="sc-header">
        <span class="sc-id">${s.id}</span>
        <span class="sc-status" id="sc-dot-${i}"></span>
      </div>
      <div class="sc-value-wrap">
        <div class="sc-value" id="sc-val-${i}">--.-</div>
        <div class="sc-unit">${s.unit}</div>
      </div>
      <div class="sc-name">${s.name}</div>
      <canvas class="sc-sparkline" id="spark-${i}" height="32"></canvas>
      <div class="sc-zscore" id="sc-z-${i}">Z: <span>0.00</span></div>
    </div>
  `).join('');
}

// ── GAUGES ───────────────────────────────────────────────
function renderGauges() {
  const wrap = document.getElementById('gauges-wrap');
  wrap.innerHTML = SENSORS.map((s, i) => `
    <div class="gauge-item">
      <div class="gauge-val" id="gv-${i}" style="color:${s.color}">0.0</div>
      <div class="gauge-bar-wrap">
        <div class="gauge-bar" id="gb-${i}" style="background:${s.color}; height:5%;"></div>
      </div>
      <div class="gauge-label">${s.id}</div>
    </div>
  `).join('');
}

// ── MAIN CHART SETUP ─────────────────────────────────────
let mainCtx, mainCanvas;
const chartColors = { line: '#00d9ff', anomaly: '#ff3860', warning: '#ffaa00', grid: '#1a2535', text: '#5a7090' };

function initMainChart() {
  mainCanvas = document.getElementById('main-chart');
  mainCtx = mainCanvas.getContext('2d');
  resizeMainChart();
  window.addEventListener('resize', resizeMainChart);
}

function resizeMainChart() {
  mainCanvas.width = mainCanvas.offsetWidth;
  mainCanvas.height = mainCanvas.offsetHeight;
}

function drawMainChart() {
  const ctx = mainCtx;
  const W = mainCanvas.width;
  const H = mainCanvas.height;
  ctx.clearRect(0, 0, W, H);

  const data = state.chartData;
  if (data.length < 2) return;

  const s = SENSORS[state.chartSensor];
  const vals = data.map(d => d.v);
  const min = Math.min(...vals) - s.noise;
  const max = Math.max(...vals) + s.noise;
  const range = max - min || 1;

  const px = (i) => (i / (data.length - 1)) * (W - 60) + 30;
  const py = (v) => H - 30 - ((v - min) / range) * (H - 50);

  // Grid lines
  ctx.strokeStyle = chartColors.grid;
  ctx.lineWidth = 1;
  for (let y = 0; y <= 4; y++) {
    const yy = 10 + (y / 4) * (H - 40);
    ctx.beginPath(); ctx.moveTo(30, yy); ctx.lineTo(W - 30, yy); ctx.stroke();
    const val = (max - (y / 4) * range).toFixed(1);
    ctx.fillStyle = chartColors.text;
    ctx.font = '9px IBM Plex Mono';
    ctx.fillText(val, 2, yy + 3);
  }

  // Mean line
  const mean = vals.reduce((a,b) => a+b, 0) / vals.length;
  const std = Math.sqrt(vals.reduce((a,b) => a + (b-mean)**2, 0) / vals.length);
  const warnHi = mean + Z_WARNING * std;
  const warnLo = mean - Z_WARNING * std;
  const critHi = mean + Z_CRITICAL * std;
  const critLo = mean - Z_CRITICAL * std;

  // Warning band
  ctx.fillStyle = 'rgba(255,170,0,0.05)';
  ctx.fillRect(30, py(warnHi), W - 60, py(warnLo) - py(warnHi));

  // Critical band
  ctx.fillStyle = 'rgba(255,56,96,0.06)';
  ctx.fillRect(30, py(critHi > max ? max : critHi), W - 60, py(critLo < min ? min : critLo) - py(critHi > max ? max : critHi));

  // Warning threshold lines
  [warnHi, warnLo].forEach(th => {
    if (th >= min && th <= max) {
      ctx.setLineDash([4, 4]);
      ctx.strokeStyle = 'rgba(255,170,0,0.5)';
      ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(30, py(th)); ctx.lineTo(W - 30, py(th)); ctx.stroke();
    }
  });
  ctx.setLineDash([]);

  // Mean line
  ctx.strokeStyle = 'rgba(0,217,255,0.2)';
  ctx.lineWidth = 1;
  ctx.setLineDash([6, 3]);
  ctx.beginPath(); ctx.moveTo(30, py(mean)); ctx.lineTo(W - 30, py(mean)); ctx.stroke();
  ctx.setLineDash([]);

  // Gradient fill under line
  const grad = ctx.createLinearGradient(0, 10, 0, H - 30);
  grad.addColorStop(0, `${s.color}30`);
  grad.addColorStop(1, `${s.color}00`);
  ctx.beginPath();
  ctx.moveTo(px(0), py(vals[0]));
  for (let i = 1; i < data.length; i++) {
    ctx.lineTo(px(i), py(vals[i]));
  }
  ctx.lineTo(px(data.length - 1), H - 30);
  ctx.lineTo(px(0), H - 30);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();

  // Main line
  ctx.beginPath();
  ctx.strokeStyle = s.color;
  ctx.lineWidth = 1.5;
  ctx.shadowBlur = 6;
  ctx.shadowColor = s.color;
  ctx.moveTo(px(0), py(vals[0]));
  for (let i = 1; i < data.length; i++) {
    ctx.lineTo(px(i), py(vals[i]));
  }
  ctx.stroke();
  ctx.shadowBlur = 0;

  // Anomaly markers
  data.forEach((d, i) => {
    if (Math.abs(d.z) >= Z_CRITICAL) {
      ctx.beginPath();
      ctx.arc(px(i), py(d.v), 5, 0, Math.PI * 2);
      ctx.fillStyle = chartColors.anomaly;
      ctx.fill();
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 1;
      ctx.stroke();
    } else if (Math.abs(d.z) >= Z_WARNING) {
      ctx.beginPath();
      ctx.arc(px(i), py(d.v), 4, 0, Math.PI * 2);
      ctx.fillStyle = chartColors.warning;
      ctx.fill();
    }
  });

  // Latest point
  const last = data[data.length - 1];
  ctx.beginPath();
  ctx.arc(px(data.length - 1), py(last.v), 4, 0, Math.PI * 2);
  ctx.fillStyle = s.color;
  ctx.shadowBlur = 10;
  ctx.shadowColor = s.color;
  ctx.fill();
  ctx.shadowBlur = 0;

  // Update footer
  document.getElementById('chart-stats').textContent =
    `Z-SCORE: ${last.z.toFixed(2)} | MEAN: ${mean.toFixed(2)} | STD: ${std.toFixed(2)}`;
}

// ── DIST CHART ───────────────────────────────────────────
let distCtx, distCanvas;

function initDistChart() {
  distCanvas = document.getElementById('dist-chart');
  distCtx = distCanvas.getContext('2d');
  resizeDistChart();
  window.addEventListener('resize', resizeDistChart);
}

function resizeDistChart() {
  distCanvas.width = distCanvas.offsetWidth;
  distCanvas.height = distCanvas.offsetHeight;
}

function drawDistChart() {
  const ctx = distCtx;
  const W = distCanvas.width;
  const H = distCanvas.height;
  ctx.clearRect(0, 0, W, H);

  const counts = state.distCounts;
  const total = counts.reduce((a,b) => a+b, 0) || 1;
  const maxC = Math.max(...counts) || 1;

  const barW = (W - 60) / SENSORS.length;
  const padX = 30;

  SENSORS.forEach((s, i) => {
    const h = ((counts[i] / maxC) * (H - 50)) || 2;
    const x = padX + i * barW + barW * 0.15;
    const bw = barW * 0.7;
    const y = H - 25 - h;

    // Bar gradient
    const grad = ctx.createLinearGradient(x, y, x, H - 25);
    grad.addColorStop(0, s.color);
    grad.addColorStop(1, s.color + '40');
    ctx.fillStyle = grad;
    ctx.fillRect(x, y, bw, h);

    // Glow
    ctx.shadowBlur = 8;
    ctx.shadowColor = s.color;
    ctx.fillRect(x, y, bw, Math.min(h, 3));
    ctx.shadowBlur = 0;

    // Label
    ctx.fillStyle = '#5a7090';
    ctx.font = '8px IBM Plex Mono';
    ctx.textAlign = 'center';
    ctx.fillText(s.id.split('-')[0], x + bw / 2, H - 10);

    // Count
    if (counts[i] > 0) {
      ctx.fillStyle = s.color;
      ctx.font = '9px IBM Plex Mono';
      ctx.fillText(counts[i], x + bw / 2, y - 4);
    }
  });

  ctx.textAlign = 'left';
}

// ── SPARKLINES ───────────────────────────────────────────
function drawSparkline(i, data) {
  const canvas = document.getElementById(`spark-${i}`);
  if (!canvas) return;
  canvas.width = canvas.offsetWidth;
  canvas.height = 32;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  if (data.length < 2) return;

  const vals = data.slice(-20);
  const min = Math.min(...vals);
  const max = Math.max(...vals);
  const range = max - min || 1;
  const W = canvas.width;
  const H = canvas.height;

  const px = (i) => (i / (vals.length - 1)) * W;
  const py = (v) => H - 2 - ((v - min) / range) * (H - 4);

  const s = SENSORS[i];
  const grad = ctx.createLinearGradient(0, 0, 0, H);
  grad.addColorStop(0, s.color + '60');
  grad.addColorStop(1, s.color + '00');

  ctx.beginPath();
  ctx.moveTo(px(0), py(vals[0]));
  for (let j = 1; j < vals.length; j++) ctx.lineTo(px(j), py(vals[j]));
  ctx.lineTo(W, H); ctx.lineTo(0, H); ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();

  ctx.beginPath();
  ctx.strokeStyle = s.color;
  ctx.lineWidth = 1.5;
  ctx.moveTo(px(0), py(vals[0]));
  for (let j = 1; j < vals.length; j++) ctx.lineTo(px(j), py(vals[j]));
  ctx.stroke();
}

// ── Z-SCORE ──────────────────────────────────────────────
function zScore(data) {
  if (data.length < 5) return 0;
  const window = data.slice(-WINDOW);
  const mean = window.reduce((a,b) => a+b, 0) / window.length;
  const std = Math.sqrt(window.reduce((a,b) => a+(b-mean)**2, 0) / window.length);
  if (std === 0) return 0;
  return (data[data.length - 1] - mean) / std;
}

function getMean(data) {
  if (!data.length) return 0;
  const w = data.slice(-WINDOW);
  return w.reduce((a,b)=>a+b,0)/w.length;
}

function getStd(data) {
  if (data.length < 2) return 0;
  const w = data.slice(-WINDOW);
  const m = w.reduce((a,b)=>a+b,0)/w.length;
  return Math.sqrt(w.reduce((a,b)=>a+(b-m)**2,0)/w.length);
}

// ── DATA GENERATION ──────────────────────────────────────
function generateReading(s, hist) {
  // Occasionally inject anomalies
  const spikeChance = Math.random();
  let value;
  if (spikeChance > 0.97) {
    // Critical spike
    value = s.base + (Math.random() > 0.5 ? 1 : -1) * (s.spike + Math.random() * s.spike * 0.5);
  } else if (spikeChance > 0.93) {
    // Drift/warning
    value = s.base + (Math.random() > 0.5 ? 1 : -1) * (s.spike * 0.55 + Math.random() * s.noise);
  } else {
    // Normal with noise
    value = s.base + (Math.random() - 0.5) * 2 * s.noise;
  }
  return parseFloat(value.toFixed(2));
}

// ── MAIN TICK ────────────────────────────────────────────
let tickStart = 0;

function tick() {
  if (state.paused) return;

  const t0 = performance.now();
  state.events += SENSORS.length;

  SENSORS.forEach((s, i) => {
    const val = generateReading(s, state.history[i]);
    state.history[i].push(val);
    if (state.history[i].length > 200) state.history[i].shift();

    const z = zScore(state.history[i]);
    state.zScores[i] = z;

    // Update sensor card
    const card = document.getElementById(`sc-${i}`);
    const valEl = document.getElementById(`sc-val-${i}`);
    const dotEl = document.getElementById(`sc-dot-${i}`);
    const zEl = document.getElementById(`sc-z-${i}`);

    valEl.textContent = val.toFixed(s.noise < 1 ? 2 : 1);

    if (Math.abs(z) >= Z_CRITICAL) {
      valEl.className = 'sc-value red';
      dotEl.className = 'sc-status red';
      card.className = 'sensor-card anomaly-active';
      zEl.className = 'sc-zscore anomaly';
      zEl.innerHTML = `Z: <span>${z.toFixed(2)}</span>`;

      // Log it
      logAnomaly(i, val, z, 'CRITICAL');
      state.distCounts[i]++;
      state.anomalies++;
      state.alertCount++;
      document.getElementById('hdr-alerts').textContent = state.alertCount;
      showAlert(`CRITICAL: ${s.id} — Z=${z.toFixed(2)}, Val=${val}${s.unit}`, 'critical');

    } else if (Math.abs(z) >= Z_WARNING) {
      valEl.className = 'sc-value amber';
      dotEl.className = 'sc-status amber';
      card.className = 'sensor-card warning-active';
      zEl.className = 'sc-zscore';
      zEl.innerHTML = `Z: <span style="color:var(--amber)">${z.toFixed(2)}</span>`;

    } else {
      valEl.className = 'sc-value';
      dotEl.className = 'sc-status';
      card.className = 'sensor-card';
      zEl.className = 'sc-zscore';
      zEl.innerHTML = `Z: <span>${z.toFixed(2)}</span>`;
    }

    drawSparkline(i, state.history[i]);
    updateGauge(i, z);
  });

  // Update chart data for selected sensor
  const cs = state.chartSensor;
  const hist = state.history[cs];
  const lastVal = hist[hist.length - 1];
  const lastZ = state.zScores[cs];
  state.chartData.push({ v: lastVal, z: lastZ });
  if (state.chartData.length > WINDOW) state.chartData.shift();

  // Update anomaly rate
  const now = Date.now();
  state.lastMinuteAnomalies = state.lastMinuteAnomalies.filter(t => now - t < 60000);
  if (state.anomalies > 0) state.lastMinuteAnomalies.push(now);

  // Render
  drawMainChart();
  drawDistChart();

  // Stats
  const latency = Math.round(performance.now() - t0);
  document.getElementById('st-total').textContent = state.anomalies;
  document.getElementById('st-latency').textContent = `${latency}ms`;
  document.getElementById('st-events').textContent = state.events.toLocaleString();
  document.getElementById('st-rate').textContent = `${state.lastMinuteAnomalies.length}/min`;

  const elapsed = (Date.now() - state.startTime) / 1000;
  const uptime = Math.max(99.5, 100 - (state.anomalies / Math.max(state.events, 1)) * 3).toFixed(1);
  document.getElementById('st-uptime').textContent = uptime + '%';
}

// ── GAUGE UPDATE ─────────────────────────────────────────
function updateGauge(i, z) {
  const bar = document.getElementById(`gb-${i}`);
  const val = document.getElementById(`gv-${i}`);
  const s = SENSORS[i];
  if (!bar || !val) return;

  const pct = Math.min(Math.abs(z) / Z_CRITICAL * 100, 100);
  bar.style.height = Math.max(pct, 3) + '%';
  val.textContent = Math.abs(z).toFixed(1);

  if (Math.abs(z) >= Z_CRITICAL) {
    bar.style.background = '#ff3860';
    val.style.color = '#ff3860';
  } else if (Math.abs(z) >= Z_WARNING) {
    bar.style.background = '#ffaa00';
    val.style.color = '#ffaa00';
  } else {
    bar.style.background = s.color;
    val.style.color = s.color;
  }
}

// ── ANOMALY LOG ──────────────────────────────────────────
function logAnomaly(i, val, z, level) {
  const s = SENSORS[i];
  const now = new Date().toTimeString().slice(0, 8);
  const entry = { sensor: s.id, name: s.name, val, z, unit: s.unit, time: now, level };
  state.anomalyLog.unshift(entry);
  if (state.anomalyLog.length > 50) state.anomalyLog.pop();

  const list = document.getElementById('log-list');
  const empty = list.querySelector('.log-empty');
  if (empty) empty.remove();

  const div = document.createElement('div');
  div.className = `log-entry ${level === 'CRITICAL' ? '' : 'warning'}`;
  div.innerHTML = `
    <div class="le-header">
      <span class="le-sensor">⚡ ${s.id} — ${level}</span>
      <span class="le-time">${now}</span>
    </div>
    <div class="le-details">Value: ${val}${s.unit} | Z-Score: ${z.toFixed(2)}</div>
  `;
  list.insertBefore(div, list.firstChild);

  // Limit log entries shown
  while (list.children.length > 20) {
    list.removeChild(list.lastChild);
  }
}

// ── ALERT TOASTS ─────────────────────────────────────────
const recentAlerts = new Set();

function showAlert(msg, type = 'critical') {
  // Dedupe
  if (recentAlerts.has(msg)) return;
  recentAlerts.add(msg);
  setTimeout(() => recentAlerts.delete(msg), 8000);

  const container = document.getElementById('alert-container');
  if (container.children.length >= 4) return;

  const toast = document.createElement('div');
  toast.className = `alert-toast ${type !== 'critical' ? 'warning' : ''}`;
  toast.innerHTML = `
    <div class="at-title">🚨 ANOMALY DETECTED</div>
    <div class="at-msg">${msg}</div>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'fadeOut 0.3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, 5000);
}

// ── CONTROLS ─────────────────────────────────────────────
function togglePause() {
  state.paused = !state.paused;
  const btn = document.getElementById('btn-pause');
  btn.textContent = state.paused ? '▶ RESUME' : '⏸ PAUSE';
  btn.classList.toggle('paused', state.paused);

  const pill = document.querySelector('.status-pill');
  if (state.paused) {
    pill.style.borderColor = 'var(--amber)';
    pill.style.color = 'var(--amber)';
    pill.style.background = 'var(--amber-dim)';
    pill.innerHTML = '<span style="width:6px;height:6px;background:var(--amber);border-radius:50%;display:inline-block;margin-right:6px"></span>PAUSED';
  } else {
    pill.style.borderColor = 'var(--green)';
    pill.style.color = 'var(--green)';
    pill.style.background = 'var(--green-dim)';
    pill.innerHTML = '<span class="pulse-dot"></span>LIVE MONITORING';
  }
}

function changeChartSensor(val) {
  state.chartSensor = parseInt(val);
  state.chartData = [];
  document.getElementById('chart-stats').textContent = 'Z-SCORE: 0.00 | MEAN: 0.00 | STD: 0.00';
}

function clearLog() {
  const list = document.getElementById('log-list');
  list.innerHTML = '<div class="log-empty">No anomalies detected</div>';
  state.anomalyLog = [];
}

// ── START ─────────────────────────────────────────────────
window.addEventListener('load', runBoot);
