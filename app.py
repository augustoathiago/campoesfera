from pathlib import Path
import base64
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Simulador Campo Elétrico Esfera",
    layout="wide"
)

BASE_DIR = Path(__file__).parent
logo_path = BASE_DIR / "logo_maua.png"

logo_src = "logo_maua.png"
if logo_path.exists():
    mime = "image/png"
    data = base64.b64encode(logo_path.read_bytes()).decode("ascii")
    logo_src = f"data:{mime};base64,{data}"

html_template = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Simulador Campo Elétrico Esfera</title>

  https://cdn.plot.ly/plotly-2.35.2.min.jsscript>

  <script>
    window.MathJax = {
      tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']]
      },
      svg: { fontCache: 'global' }
    };
  </script>
  https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.jsscript>

  <style>
    :root {
      --bg: #f5f7fb;
      --card: #ffffff;
      --text: #1f2937;
      --muted: #6b7280;
      --primary: #1d4ed8;
      --border: #d1d5db;
      --positive: #c81e1e;
      --negative: #1d4ed8;
      --zero: #111827;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--text);
      background: var(--bg);
    }

    .container {
      max-width: 1260px;
      margin: 0 auto;
      padding: 20px;
    }

    .header-card, .section {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      box-shadow: 0 2px 10px rgba(0,0,0,.06);
    }

    .header-card {
      padding: 18px;
      margin-bottom: 18px;
    }

    .header-grid {
      display: grid;
      grid-template-columns: minmax(130px, 220px) 1fr;
      gap: 18px;
      align-items: center;
    }

    .logo-box {
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 120px;
      border: 1px dashed var(--border);
      border-radius: 14px;
      background: #fff;
    }

    .logo-box img {
      max-width: 100%;
      max-height: 100px;
      object-fit: contain;
    }

    .logo-fallback {
      display: none;
      align-items: center;
      justify-content: center;
      color: var(--muted);
      font-size: 14px;
      text-align: center;
      padding: 8px;
    }

    h1 {
      margin: 0 0 6px 0;
      font-size: clamp(24px, 3vw, 36px);
    }

    .subtitle {
      color: var(--muted);
      font-size: 18px;
    }

    .section {
      padding: 18px;
      margin-bottom: 18px;
    }

    .section h2 {
      margin-top: 0;
      font-size: 22px;
    }

    .param-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(280px, 1fr));
      gap: 14px 18px;
      align-items: start;
    }

    .control {
      margin-bottom: 14px;
    }

    .control label {
      display: block;
      font-weight: 700;
      margin-bottom: 6px;
      line-height: 1.3;
    }

    .control .row {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    input[type=range] {
      width: 100%;
    }

    .value-badge {
      min-width: 100px;
      text-align: right;
      font-variant-numeric: tabular-nums;
      color: var(--primary);
      font-weight: 700;
    }

    .toggle {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }

    .toggle button {
      border: 1px solid var(--border);
      background: #fff;
      color: var(--text);
      padding: 10px 14px;
      border-radius: 999px;
      cursor: pointer;
      font-weight: 700;
      transition: .15s ease;
    }

    .toggle button.active {
      background: var(--primary);
      color: #fff;
      border-color: var(--primary);
    }

    .hidden {
      display: none !important;
    }

    .note {
      color: var(--muted);
      font-size: 14px;
      line-height: 1.45;
      margin-top: 8px;
    }

    .img-scroll {
      overflow-x: auto;
      overflow-y: hidden;
      padding-bottom: 8px;
    }

    .viz-wrap {
      min-width: 980px;
    }

    .legend-box, .field-box {
      fill: rgba(255,255,255,.95);
      stroke: #374151;
      stroke-width: 1.2px;
      rx: 12px;
      ry: 12px;
    }

    .equation-block {
      background: #fff;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 14px;
      overflow-x: auto;
    }

    .small {
      font-size: 14px;
    }

    .footer-note {
      color: var(--muted);
      font-size: 13px;
      margin-top: 10px;
    }

    @media (max-width: 980px) {
      .header-grid {
        grid-template-columns: 1fr;
      }

      .logo-box {
        min-height: 90px;
      }

      .param-grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
<div class="container">

  <div class="header-card">
    <div class="header-grid">
      <div class="logo-box">
        __LOGO_SRC__style.display='flex';" />
        <div id="logoFallback" class="logo-fallback">
          Adicione o arquivo <strong>logo_maua.png</strong> na mesma pasta do app para exibir o logotipo.
        </div>
      </div>
      <div>
        <h1>Simulador Campo Elétrico Esfera</h1>
        <div class="subtitle">Estude o campo elétrico de uma esfera.</div>
      </div>
    </div>
  </div>

  <!-- PARÂMETROS -->
  <div class="section">
    <h2>Parâmetros</h2>

    <div class="param-grid">
      <div class="control">
        <label for="aRange">Raio interno a da esfera (m)</label>
        <div class="row">
          <input id="aRange" type="range" min="0" max="5" step="0.1" value="1.0" />
          <div id="aVal" class="value-badge">1,0 m</div>
        </div>
      </div>

      <div class="control">
        <label for="bRange">Raio externo b da esfera (m)</label>
        <div class="row">
          <input id="bRange" type="range" min="0.5" max="6" step="0.1" value="2.5" />
          <div id="bVal" class="value-badge">2,5 m</div>
        </div>
      </div>

      <div class="control">
        <label for="q2Range">Carga da casca esférica q2 (μC)</label>
        <div class="row">
          <input id="q2Range" type="range" min="-20" max="20" step="0.1" value="6.0" />
          <div id="q2Val" class="value-badge">6,0 μC</div>
        </div>
      </div>

      <div class="control">
        <label for="rRange">Raio r da superfície gaussiana para estudo do campo elétrico (m)</label>
        <div class="row">
          <input id="rRange" type="range" min="0.1" max="8.0" step="0.01" value="1.50" />
          <div id="rVal" class="value-badge">1,50 m</div>
        </div>
      </div>

      <div id="particleToggleControl" class="control">
        <label>Partícula no centro da casca</label>
        <div class="toggle">
          <button id="btnSemParticula" class="active">Sem partícula</button>
          <button id="btnComParticula">Com partícula</button>
        </div>
      </div>

      <div id="q1Control" class="control hidden">
        <label for="q1Range">Carga da partícula q1 (μC)</label>
        <div class="row">
          <input id="q1Range" type="range" min="-10" max="10" step="0.1" value="3.0" />
          <div id="q1Val" class="value-badge">3,0 μC</div>
        </div>
      </div>

      <div class="control">
        <label>Material</label>
        <div class="toggle">
          <button id="btnIsolante" class="active">Esfera isolante</button>
          <button id="btnCondutora">Esfera condutora</button>
        </div>
      </div>
    </div>

    <div class="note" id="paramNote"></div>
  </div>

  <!-- IMAGEM -->
  <div class="section">
    <h2>Imagem</h2>
    <div class="img-scroll">
      <div class="viz-wrap">
        <svg id="viz" width="980" height="550" viewBox="0 0 980 550" role="img" aria-label="Esfera com superfície gaussiana arrastável"></svg>
      </div>
    </div>
    <div class="footer-note">
      Arraste a circunferência tracejada (superfície gaussiana) ou use o slider de r na seção “Parâmetros”.
      Em telas pequenas, deslize horizontalmente a figura.
    </div>
  </div>

  <!-- LEI DE GAUSS -->
  <div class="section">
    <h2>Lei de Gauss</h2>
    <div class="equation-block" id="gaussLaw"></div>
  </div>

  <!-- CARGA NA ESFERA -->
  <div class="section">
    <h2>Carga na esfera</h2>
    <div class="equation-block" id="sphereCharge"></div>
  </div>

  <!-- CARGA ENCERRADA -->
  <div class="section">
    <h2>Carga Q contida na superfície gaussiana</h2>
    <div class="equation-block" id="qEnclosed"></div>
  </div>

  <!-- ÁREA -->
  <div class="section">
    <h2>Área da superfície gaussiana</h2>
    <div class="equation-block" id="areaEq"></div>
  </div>

  <!-- CAMPO -->
  <div class="section">
    <h2>Campo elétrico</h2>
    <div class="equation-block" id="fieldEq"></div>
  </div>

  <!-- GRÁFICO -->
  <div class="section">
    <h2>Gráfico</h2>
    <div id="chart" style="width:100%;height:440px;"></div>
  </div>
</div>

<script>
(() => {
  const EPS0 = 8.8e-12;
  const FOUR_PI = 4 * Math.PI;

  // Escala fixa da imagem (melhoria solicitada)
  const PX_PER_M = 28;
  const MAX_R = 8.0;

  const state = {
    a: 1.0,
    b: 2.5,
    q1uC: 3.0,
    q2uC: 6.0,
    material: 'isolante',
    hasParticle: false,
    r: 1.5
  };

  const els = {
    aRange: document.getElementById('aRange'),
    bRange: document.getElementById('bRange'),
    q1Range: document.getElementById('q1Range'),
    q2Range: document.getElementById('q2Range'),
    rRange: document.getElementById('rRange'),

    aVal: document.getElementById('aVal'),
    bVal: document.getElementById('bVal'),
    q1Val: document.getElementById('q1Val'),
    q2Val: document.getElementById('q2Val'),
    rVal: document.getElementById('rVal'),

    q1Control: document.getElementById('q1Control'),
    particleToggleControl: document.getElementById('particleToggleControl'),
    btnSemParticula: document.getElementById('btnSemParticula'),
    btnComParticula: document.getElementById('btnComParticula'),

    btnIsolante: document.getElementById('btnIsolante'),
    btnCondutora: document.getElementById('btnCondutora'),

    paramNote: document.getElementById('paramNote'),

    viz: document.getElementById('viz'),

    gaussLaw: document.getElementById('gaussLaw'),
    sphereCharge: document.getElementById('sphereCharge'),
    qEnclosed: document.getElementById('qEnclosed'),
    areaEq: document.getElementById('areaEq'),
    fieldEq: document.getElementById('fieldEq'),

    chart: document.getElementById('chart')
  };

  const center = { x: 340, y: 270 };
  const minRPx = 10;
  const maxRPx = MAX_R * PX_PER_M;

  function colorFor(qMicro) {
    if (qMicro > 1e-12) return '#c81e1e';
    if (qMicro < -1e-12) return '#1d4ed8';
    return '#111827';
  }

  function fillColor(qMicro) {
    if (qMicro > 1e-12) return 'rgba(200,30,30,0.16)';
    if (qMicro < -1e-12) return 'rgba(29,78,216,0.14)';
    return 'rgba(17,24,39,0.08)';
  }

  function fmt(num, digits = 3) {
    if (!Number.isFinite(num)) return '—';
    const abs = Math.abs(num);
    if (abs >= 1e4 || (abs > 0 && abs < 1e-3)) {
      return num.toExponential(3).replace('e', '×10^');
    }
    return Number(num.toFixed(digits)).toString().replace('.', ',');
  }

  function fmtLatex(num, digits = 3) {
    if (!Number.isFinite(num)) return '\\text{—}';
    const abs = Math.abs(num);
    if (abs >= 1e4 || (abs > 0 && abs < 1e-3)) {
      const parts = num.toExponential(3).split('e');
      const mant = Number(parts[0]).toFixed(3);
      const exp = parseInt(parts[1], 10);
      return mant + '\\times 10^{' + exp + '}';
    }
    return Number(num.toFixed(digits)).toString().replace('.', '{,}');
  }

  function asCoulomb(microC) {
    return microC * 1e-6;
  }

  function clamp(x, lo, hi) {
    return Math.max(lo, Math.min(hi, x));
  }

  function mToPx(m) {
    return m * PX_PER_M;
  }

  function pxToM(px) {
    return px / PX_PER_M;
  }

  function isShell() {
    return state.a > 0;
  }

  function currentQ1uC() {
    return (isShell() && state.hasParticle) ? state.q1uC : 0;
  }

  function surfaceCharges() {
    const q1 = currentQ1uC();
    const q2 = state.q2uC;

    if (state.material === 'isolante') {
      return { q1, q2, q2i: 0, q2e: 0 };
    }

    if (isShell() && state.hasParticle && Math.abs(q1) > 1e-12) {
      const q2i = -q1;
      const q2e = q2 - q2i;
      return { q1, q2, q2i, q2e };
    }

    return { q1, q2, q2i: 0, q2e: q2 };
  }

  function enclosedChargeC(r) {
    const a = state.a;
    const b = state.b;
    const q1 = asCoulomb(currentQ1uC());
    const q2 = asCoulomb(state.q2uC);

    if (r <= 0) return 0;

    if (state.material === 'isolante') {
      if (a === 0) {
        if (r < b) return q2 * (r ** 3) / (b ** 3);
        return q2;
      }

      if (r < a) return q1;
      if (r < b) return q1 + q2 * ((r ** 3 - a ** 3) / (b ** 3 - a ** 3));
      return q1 + q2;
    }

    // Condutora
    if (a === 0) {
      if (r < b) return 0;
      return q2;
    }

    const sc = surfaceCharges();
    const q2iC = asCoulomb(sc.q2i);
    const q2eC = asCoulomb(sc.q2e);

    if (r < a) return q1;
    if (r < b) return q1 + q2iC;
    return q1 + q2iC + q2eC;
  }

  function fieldAt(r) {
    if (r <= 0) return 0;
    const Q = enclosedChargeC(r);
    return Q / (FOUR_PI * EPS0 * r * r);
  }

  function areaOfGaussian(r) {
    return FOUR_PI * r * r;
  }

  function regionLabel(r) {
    const a = state.a;
    const b = state.b;

    if (a === 0) {
      if (r < b) {
        return state.material === 'isolante'
          ? 'interior_da_esfera_macica_isolante'
          : 'interior_condutor_macico';
      }
      return 'exterior';
    }

    if (r < a) return 'cavidade';
    if (r < b) return state.material === 'isolante' ? 'espessura_isolante' : 'espessura_condutora';
    return 'exterior';
  }

  function updateInputs() {
    if (state.a > state.b - 0.1) {
      state.a = Math.max(0, state.b - 0.1);
      els.aRange.value = state.a.toFixed(1);
    }

    state.r = clamp(state.r, 0.10, MAX_R);
    els.rRange.value = state.r.toFixed(2);

    const shell = isShell();
    if (!shell) {
      state.hasParticle = false;
    }

    els.particleToggleControl.classList.toggle('hidden', !shell);
    els.q1Control.classList.toggle('hidden', !(shell && state.hasParticle));

    els.btnSemParticula.classList.toggle('active', !state.hasParticle);
    els.btnComParticula.classList.toggle('active', state.hasParticle);

    els.aVal.textContent = state.a.toFixed(1).replace('.', ',') + ' m';
    els.bVal.textContent = state.b.toFixed(1).replace('.', ',') + ' m';
    els.q1Val.textContent = state.q1uC.toFixed(1).replace('.', ',') + ' μC';
    els.q2Val.textContent = state.q2uC.toFixed(1).replace('.', ',') + ' μC';
    els.rVal.textContent = state.r.toFixed(2).replace('.', ',') + ' m';

    els.btnIsolante.classList.toggle('active', state.material === 'isolante');
    els.btnCondutora.classList.toggle('active', state.material === 'condutora');

    let note = '';
    if (state.a === 0) {
      note += 'Esfera maciça: não há cavidade interna e não se considera partícula central.';
    } else {
      note += 'Casca esférica: é possível escolher se existe ou não uma partícula no centro da cavidade.';
    }

    if (state.material === 'condutora') {
      note += ' No material condutor, o campo elétrico no interior do material condutor é nulo em equilíbrio eletrostático.';
    } else {
      note += ' No material isolante, a carga q2 é assumida homogênea no volume da esfera/casca.';
    }

    note += ' A escala da imagem foi mantida fixa para facilitar a comparação entre dimensões.';
    els.paramNote.textContent = note;
  }

  function drawViz() {
    const svg = els.viz;
    svg.innerHTML = '';

    const aPx = mToPx(state.a);
    const bPx = mToPx(state.b);
    const gPx = mToPx(state.r);

    const q1 = currentQ1uC();
    const sc = surfaceCharges();
    const q2 = sc.q2;
    const q2i = sc.q2i;
    const q2e = sc.q2e;
    const E = fieldAt(state.r);

    function add(tag, attrs = {}, parent = svg) {
      const el = document.createElementNS('http://www.w3.org/2000/svg', tag);
      Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
      parent.appendChild(el);
      return el;
    }

    const defs = add('defs');
    const markerOut = add('marker', {
      id: 'arrowHead',
      markerWidth: '10',
      markerHeight: '10',
      refX: '8',
      refY: '3',
      orient: 'auto',
      markerUnits: 'strokeWidth'
    }, defs);
    add('path', { d: 'M0,0 L0,6 L9,3 z', fill: '#111827' }, markerOut);

    // título interno
    add('text', {
      x: 24,
      y: 34,
      fill: '#374151',
      'font-size': '16',
      'font-weight': '700'
    }).textContent = 'Figura da esfera e superfície gaussiana';

    // Preenchimento do material
    if (state.material === 'isolante') {
      if (state.a > 0) {
        add('circle', {
          cx: center.x, cy: center.y, r: bPx,
          fill: fillColor(state.q2uC), stroke: 'none'
        });
        add('circle', {
          cx: center.x, cy: center.y, r: aPx,
          fill: '#ffffff', stroke: 'none'
        });
      } else {
        add('circle', {
          cx: center.x, cy: center.y, r: bPx,
          fill: fillColor(state.q2uC), stroke: 'none'
        });
      }
    } else {
      if (state.a > 0) {
        add('circle', {
          cx: center.x, cy: center.y, r: bPx,
          fill: 'rgba(17,24,39,0.05)', stroke: 'none'
        });
        add('circle', {
          cx: center.x, cy: center.y, r: aPx,
          fill: '#ffffff', stroke: 'none'
        });
      } else {
        add('circle', {
          cx: center.x, cy: center.y, r: bPx,
          fill: 'rgba(17,24,39,0.05)', stroke: 'none'
        });
      }
    }

    // Fronteiras do material
    if (state.a > 0) {
      const innerStroke = (state.material === 'isolante')
        ? colorFor(state.q2uC)   // melhoria 3
        : colorFor(q2i);

      add('circle', {
        cx: center.x,
        cy: center.y,
        r: aPx,
        fill: 'none',
        stroke: innerStroke,
        'stroke-width': '5'
      });
    }

    const outerStroke = (state.material === 'condutora')
      ? colorFor(q2e)
      : colorFor(state.q2uC);

    add('circle', {
      cx: center.x,
      cy: center.y,
      r: bPx,
      fill: 'none',
      stroke: outerStroke,
      'stroke-width': '6'
    });

    // Partícula central (somente se existir)
    if (state.hasParticle && state.a > 0) {
      add('circle', {
        cx: center.x,
        cy: center.y,
        r: 10,
        fill: colorFor(q1),
        stroke: '#111827',
        'stroke-width': '1.2'
      });
    }

    // Superfície gaussiana
    const gauss = add('circle', {
      id: 'gaussian',
      cx: center.x,
      cy: center.y,
      r: gPx,
      fill: 'none',
      stroke: '#111827',
      'stroke-width': '3',
      'stroke-dasharray': '9 7',
      cursor: 'ew-resize'
    });

    const handle = add('circle', {
      id: 'handle',
      cx: center.x + gPx,
      cy: center.y,
      r: 10,
      fill: '#ffffff',
      stroke: '#111827',
      'stroke-width': '2',
      cursor: 'ew-resize'
    });

    // Vetor E no ponto mais à direita
    const pX = center.x + gPx;
    const pY = center.y;
    const arrowMag = clamp(34 + 18 * Math.log10(1 + Math.abs(E)), 0, 95);
    const direction = Math.sign(E) || 0;

    if (direction !== 0) {
      const x2 = pX + direction * arrowMag;
      add('line', {
        x1: pX, y1: pY,
        x2: x2, y2: pY,
        stroke: '#111827',
        'stroke-width': '4',
        'marker-end': 'url(#arrowHead)'
      });

      add('text', {
        x: direction > 0 ? x2 + 10 : x2 - 34,
        y: pY - 10,
        fill: '#111827',
        'font-size': '18',
        'font-weight': '700'
      }).textContent = 'E';
    } else {
      add('text', {
        x: pX + 14,
        y: pY - 10,
        fill: '#111827',
        'font-size': '16',
        'font-weight': '700'
      }).textContent = 'E = 0';
    }

    // Cotas verticais de raio (não diâmetro)
    const dimX = 90;

    // raio b
    add('line', {
      x1: dimX, y1: center.y,
      x2: dimX, y2: center.y - bPx,
      stroke: '#111827',
      'stroke-width': '2'
    });
    add('line', {
      x1: dimX - 8, y1: center.y,
      x2: dimX + 8, y2: center.y,
      stroke: '#111827',
      'stroke-width': '2'
    });
    add('line', {
      x1: dimX - 8, y1: center.y - bPx,
      x2: dimX + 8, y2: center.y - bPx,
      stroke: '#111827',
      'stroke-width': '2'
    });
    add('text', {
      x: dimX + 14,
      y: center.y - bPx / 2,
      fill: '#111827',
      'font-size': '16',
      'font-weight': '700'
    }).textContent = 'b = ' + state.b.toFixed(2) + ' m';

    // raio a (somente se casca)
    if (state.a > 0) {
      const dimX2 = 135;
      add('line', {
        x1: dimX2, y1: center.y,
        x2: dimX2, y2: center.y - aPx,
        stroke: '#6b7280',
        'stroke-width': '1.7'
      });
      add('line', {
        x1: dimX2 - 6, y1: center.y,
        x2: dimX2 + 6, y2: center.y,
        stroke: '#6b7280',
        'stroke-width': '1.7'
      });
      add('line', {
        x1: dimX2 - 6, y1: center.y - aPx,
        x2: dimX2 + 6, y2: center.y - aPx,
        stroke: '#6b7280',
        'stroke-width': '1.7'
      });
      add('text', {
        x: dimX2 + 12,
        y: center.y - aPx / 2,
        fill: '#374151',
        'font-size': '15',
        'font-weight': '700'
      }).textContent = 'a = ' + state.a.toFixed(2) + ' m';
    }

    // Box de cargas
    const chargeItems = [];
    if (state.hasParticle && state.a > 0) {
      chargeItems.push({ label: 'q1', value: q1 });
    }
    chargeItems.push({ label: 'q2', value: q2 });

    if (state.material === 'condutora') {
      chargeItems.push({ label: 'q2i', value: q2i });
      chargeItems.push({ label: 'q2e', value: q2e });
    }

    const chargeBoxHeight = 56 + chargeItems.length * 30;
    add('rect', {
      x: 675,
      y: 36,
      width: 265,
      height: chargeBoxHeight,
      class: 'legend-box'
    });

    add('text', {
      x: 695, y: 64,
      fill: '#111827',
      'font-size': '18',
      'font-weight': '700'
    }).textContent = 'Cargas';

    chargeItems.forEach((item, idx) => {
      const y = 95 + idx * 30;
      add('text', {
        x: 695,
        y: y,
        fill: '#111827',
        'font-size': '16'
      }).textContent = item.label + ' = ';

      add('text', {
        x: 750,
        y: y,
        fill: colorFor(item.value),
        'font-size': '16',
        'font-weight': '700'
      }).textContent = item.value.toFixed(2) + ' μC';
    });

    // Box do campo (sem carga da superfície gaussiana)
    add('rect', {
      x: 675,
      y: 240,
      width: 265,
      height: 116,
      class: 'field-box'
    });

    add('text', {
      x: 695,
      y: 268,
      fill: '#111827',
      'font-size': '18',
      'font-weight': '700'
    }).textContent = 'Na superfície gaussiana';

    add('text', {
      x: 695,
      y: 300,
      fill: '#111827',
      'font-size': '16'
    }).textContent = 'r = ' + state.r.toFixed(3) + ' m';

    add('text', {
      x: 695,
      y: 334,
      fill: '#111827',
      'font-size': '16',
      'font-weight': '700'
    }).textContent = 'E = ' + fmt(E, 4) + ' N/C';

    // Drag da superfície gaussiana
    let dragging = false;

    const onMove = (evt) => {
      if (!dragging) return;
      const pt = svg.createSVGPoint();
      pt.x = evt.clientX;
      pt.y = evt.clientY;
      const sp = pt.matrixTransform(svg.getScreenCTM().inverse());
      const dx = sp.x - center.x;
      const dy = sp.y - center.y;
      const px = clamp(Math.sqrt(dx * dx + dy * dy), minRPx, maxRPx);
      state.r = clamp(pxToM(px), 0.10, MAX_R);
      render();
    };

    const onUp = () => {
      dragging = false;
      window.removeEventListener('pointermove', onMove);
    };

    const onDown = (evt) => {
      dragging = true;
      evt.preventDefault();
      window.addEventListener('pointermove', onMove);
      window.addEventListener('pointerup', onUp, { once: true });
    };

    gauss.addEventListener('pointerdown', onDown);
    handle.addEventListener('pointerdown', onDown);
  }

  function renderMath() {
    const a = state.a;
    const b = state.b;
    const r = state.r;

    const q1u = currentQ1uC();
    const q2u = state.q2uC;

    const q1 = asCoulomb(q1u);
    const q2 = asCoulomb(q2u);

    const sc = surfaceCharges();
    const q2i = sc.q2i;
    const q2e = sc.q2e;
    const q2iC = asCoulomb(q2i);

    const Q = enclosedChargeC(r);
    const A = areaOfGaussian(r);
    const E = fieldAt(r);
    const reg = regionLabel(r);

    els.gaussLaw.innerHTML = `
      <div>$$\\Phi = \\oint \\vec{E}\\cdot d\\vec{A} = \\frac{Q}{\\varepsilon_0}$$</div>
      <div class="small">
        \\(\\Phi\\) é o fluxo elétrico na superfície gaussiana;
        \\(\\vec{E}\\) é o campo elétrico;
        \\(A\\) é a área da superfície gaussiana;
        \\(Q\\) é a carga contida na superfície gaussiana;
        \\(\\varepsilon_0 = 8{,}8\\times 10^{-12}\\;\\mathrm{C^2/(N\\,m^2)}\\).
      </div>
    `;

    let sphereChargeHtml = '';

    if (state.material === 'isolante') {
      sphereChargeHtml += `
        <div>$$\\text{Carga distribuída homogeneamente por ser material isolante: } q_2 = ${fmtLatex(q2u)}\\,\\mu\\mathrm{C}$$</div>
      `;
      if (a > 0 && state.hasParticle && Math.abs(q1u) > 1e-12) {
        sphereChargeHtml += `
          <div class="small">
            A partícula central \\(q_1\\) permanece localizada no centro da cavidade, enquanto
            \\(q_2\\) fica distribuída uniformemente no volume da casca.
          </div>
        `;
      }
    } else {
      if (a === 0 || !state.hasParticle || Math.abs(q1u) < 1e-12) {
        sphereChargeHtml += `
          <div>$$\\text{Carga toda na superfície externa por ser material condutor: } q_2 = ${fmtLatex(q2u)}\\,\\mu\\mathrm{C}$$</div>
        `;
      } else {
        sphereChargeHtml += `
          <div>$$\\text{A partícula induz carga na superfície interna da casca condutora: } q_{2i} = -q_1 = ${fmtLatex(-q1u)}\\,\\mu\\mathrm{C}$$</div>
          <div>$$\\text{Como a carga total da casca é } q_2, \\text{ então: } q_2 = q_{2i} + q_{2e}$$</div>
          <div>$$q_{2e} = q_2 - q_{2i}$$</div>
          <div>$$q_{2e} = ${fmtLatex(q2u)} - (${fmtLatex(-q1u)}) = ${fmtLatex(q2e)}\\,\\mu\\mathrm{C}$$</div>
        `;
      }
    }

    els.sphereCharge.innerHTML = sphereChargeHtml;

    let qHtml = '';

    if (reg === 'cavidade') {
      if (state.hasParticle && Math.abs(q1u) > 1e-12) {
        qHtml += `<div>$$Q = q_1 = ${fmtLatex(q1u)}\\,\\mu\\mathrm{C}$$</div>`;
      } else {
        qHtml += `<div>$$Q = 0$$</div>`;
      }
    } else if (reg === 'exterior') {
      qHtml += `
        <div>$$Q = q_1 + q_2 = ${fmtLatex(q1u)} + ${fmtLatex(q2u)} = ${fmtLatex((q1 + q2) * 1e6)}\\,\\mu\\mathrm{C}$$</div>
      `;
    } else if (reg === 'interior_da_esfera_macica_isolante') {
      qHtml += `
        <div>$$\\rho = \\frac{q_2}{V_{total}} = \\frac{Q}{V_r}$$</div>
        <div class="small">\\(V\\) é o volume e \\(\\rho\\) é a densidade de carga volumétrica.</div>
        <div>$$\\frac{q_2}{\\frac{4}{3}\\pi b^3} = \\frac{Q}{\\frac{4}{3}\\pi r^3}$$</div>
        <div>$$Q = q_2\\frac{r^3}{b^3}$$</div>
        <div>$$Q = (${fmtLatex(q2)}\\,\\mathrm{C})\\frac{(${fmtLatex(r)})^3}{(${fmtLatex(b)})^3} = ${fmtLatex(Q)}\\,\\mathrm{C} = ${fmtLatex(Q * 1e6)}\\,\\mu\\mathrm{C}$$</div>
      `;
    } else if (reg === 'espessura_isolante') {
      qHtml += `
        <div>$$\\rho = \\frac{q_2}{V_{total}} = \\frac{Q-q_1}{V_r}$$</div>
        <div class="small">\\(V_{total}=\\tfrac{4}{3}\\pi(b^3-a^3)\\) e \\(V_r=\\tfrac{4}{3}\\pi(r^3-a^3)\\).</div>
        <div>$$\\frac{q_2}{\\frac{4}{3}\\pi(b^3-a^3)} = \\frac{Q-q_1}{\\frac{4}{3}\\pi(r^3-a^3)}$$</div>
        <div>$$Q = q_1 + q_2\\frac{r^3-a^3}{b^3-a^3}$$</div>
        <div>$$Q = ${fmtLatex(q1)} + (${fmtLatex(q2)})\\frac{(${fmtLatex(r)})^3-(${fmtLatex(a)})^3}{(${fmtLatex(b)})^3-(${fmtLatex(a)})^3} = ${fmtLatex(Q)}\\,\\mathrm{C} = ${fmtLatex(Q * 1e6)}\\,\\mu\\mathrm{C}$$</div>
      `;
    } else if (reg === 'interior_condutor_macico') {
      qHtml += `<div>$$\\text{Como toda a carga está na superfície externa, } Q = 0$$</div>`;
    } else if (reg === 'espessura_condutora') {
      qHtml += `
        <div>$$Q = q_1 + q_{2i} = ${fmtLatex(q1u)} + (${fmtLatex(q2i)}) = ${fmtLatex((q1 + q2iC) * 1e6)}\\,\\mu\\mathrm{C} = 0$$</div>
      `;
    }

    els.qEnclosed.innerHTML = qHtml;

    els.areaEq.innerHTML = `
      <div>$$A = 4\\pi r^2$$</div>
      <div>$$A = 4\\pi(${fmtLatex(r)})^2 = ${fmtLatex(A)}\\,\\mathrm{m^2}$$</div>
    `;

    els.fieldEq.innerHTML = `
      <div>$$\\text{Lei de Gauss no caso de simetria: campo constante } E \\text{ em toda a superfície gaussiana e sempre paralelo ao vetor área.}$$</div>
      <div>$$EA = \\frac{Q}{\\varepsilon_0}$$</div>
      <div>$$E = \\frac{Q}{A\\varepsilon_0}$$</div>
      <div>$$E = \\frac{${fmtLatex(Q)}\\,\\mathrm{C}}{(${fmtLatex(A)}\\,\\mathrm{m^2})(8{,}8\\times10^{-12}\\,\\mathrm{C^2/(N\\,m^2)})} = ${fmtLatex(E)}\\,\\mathrm{N/C}$$</div>
      <div class="small">Sinal positivo indica campo radial para fora; sinal negativo indica campo radial para dentro.</div>
    `;

    if (window.MathJax && window.MathJax.typesetPromise) {
      MathJax.typesetPromise([
        els.gaussLaw,
        els.sphereCharge,
        els.qEnclosed,
        els.areaEq,
        els.fieldEq
      ]).catch(() => {});
    }
  }

  function renderChart() {
    const a = state.a;
    const b = state.b;
    const rAtual = state.r;

    const rMax = Math.max(8.0, b + 1.6);
    const rs = [];
    const Es = [];
    const n = 500;

    for (let i = 1; i <= n; i++) {
      let r = (i / n) * rMax;
      if (a > 0 && Math.abs(r - a) < 0.01) r += 0.01;
      if (Math.abs(r - b) < 0.01) r += 0.01;
      rs.push(r);
      Es.push(fieldAt(r));
    }

    const EAtual = fieldAt(rAtual);
    const yMin = Math.min(...Es, EAtual);
    const yMax = Math.max(...Es, EAtual);
    const pad = 0.08 * Math.max(1, Math.abs(yMax - yMin));

    const trace = {
      x: rs,
      y: Es,
      mode: 'lines',
      line: { color: '#1d4ed8', width: 3 },
      hovertemplate: 'r = %{x:.3f} m<br>E = %{y:.3e} N/C<extra></extra>'
    };

    const currentPoint = {
      x: [rAtual],
      y: [EAtual],
      mode: 'markers',
      marker: { size: 10, color: '#c81e1e' },
      hovertemplate: 'r = %{x:.3f} m<br>E = %{y:.3e} N/C<extra></extra>'
    };

    const shapes = [];

    if (a > 0) {
      shapes.push({
        type: 'line',
        x0: a, x1: a,
        y0: yMin - pad, y1: yMax + pad,
        line: { color: '#6b7280', dash: 'dot', width: 2 }
      });
    }

    shapes.push({
      type: 'line',
      x0: b, x1: b,
      y0: yMin - pad, y1: yMax + pad,
      line: { color: '#111827', dash: 'dash', width: 2 }
    });

    shapes.push({
      type: 'line',
      x0: rAtual, x1: rAtual,
      y0: yMin - pad, y1: yMax + pad,
      line: { color: '#c81e1e', dash: 'longdash', width: 2.5 }
    });

    const annotations = [];

    if (a > 0) {
      annotations.push({
        x: a,
        y: yMax + pad,
        text: '<b>a</b>',
        showarrow: false,
        yshift: 12,
        font: { color: '#6b7280', size: 14 }
      });
    }

    annotations.push({
      x: b,
      y: yMax + pad,
      text: '<b>b</b>',
      showarrow: false,
      yshift: 12,
      font: { color: '#111827', size: 14 }
    });

    annotations.push({
      x: rAtual,
      y: yMax + pad,
      text: '<b>r</b>',
      showarrow: false,
      yshift: 12,
      font: { color: '#c81e1e', size: 14 }
    });

    Plotly.newPlot(
      els.chart,
      [trace, currentPoint],
      {
        paper_bgcolor: '#ffffff',
        plot_bgcolor: '#ffffff',
        margin: { l: 62, r: 16, t: 24, b: 58 },
        xaxis: {
          title: 'Distância r (m)',
          automargin: true,
          zeroline: true
        },
        yaxis: {
          title: 'Campo elétrico E (N/C)',
          automargin: true,
          zeroline: true,
          range: [yMin - pad, yMax + pad]
        },
        shapes: shapes,
        annotations: annotations,
        showlegend: false,
        responsive: true
      },
      {
        displayModeBar: false,
        responsive: true
      }
    );
  }

  function render() {
    updateInputs();
    drawViz();
    renderMath();
    renderChart();
  }

  // Eventos
  els.aRange.addEventListener('input', (e) => {
    state.a = parseFloat(e.target.value);
    if (state.a >= state.b) {
      state.b = Math.min(6, state.a + 0.1);
      els.bRange.value = state.b.toFixed(1);
    }
    render();
  });

  els.bRange.addEventListener('input', (e) => {
    state.b = parseFloat(e.target.value);
    if (state.b <= state.a) {
      state.a = Math.max(0, state.b - 0.1);
      els.aRange.value = state.a.toFixed(1);
    }
    render();
  });

  els.q1Range.addEventListener('input', (e) => {
    state.q1uC = parseFloat(e.target.value);
    render();
  });

  els.q2Range.addEventListener('input', (e) => {
    state.q2uC = parseFloat(e.target.value);
    render();
  });

  els.rRange.addEventListener('input', (e) => {
    state.r = parseFloat(e.target.value);
    render();
  });

  els.btnSemParticula.addEventListener('click', () => {
    state.hasParticle = false;
    render();
  });

  els.btnComParticula.addEventListener('click', () => {
    if (state.a > 0) {
      state.hasParticle = true;
      render();
    }
  });

  els.btnIsolante.addEventListener('click', () => {
    state.material = 'isolante';
    render();
  });

  els.btnCondutora.addEventListener('click', () => {
    state.material = 'condutora';
    render();
  });

  window.addEventListener('resize', () => {
    if (window.Plotly) {
      Plotly.Plots.resize(els.chart);
    }
  });

  render();
})();
</script>
</body>
</html>
"""

html = html_template.replace("__LOGO_SRC__", logo_src)
components.html(html, height=4200, scrolling=True)
