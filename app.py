from pathlib import Path
import base64
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

logo_path = Path("logo_maua.png")

logo_src = ""
if logo_path.exists():
    import base64
    data = base64.b64encode(logo_path.read_bytes()).decode()
    logo_src = f'data:image/png;base64,{data}'

html = f"""
<!DOCTYPE html>
<html>
<head>

<!-- ✅ CORREÇÃO DO PROBLEMA DO CABEÇALHO -->
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>

<script>
window.MathJax = {{
  tex: {{
    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']]
  }}
}};
</script>

<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>

<style>
body {{ font-family: Arial; }}
.box {{ border:1px solid #ccc; padding:10px; margin:10px; border-radius:10px; }}
</style>

</head>
<body>

<h1>Simulador Campo Elétrico Esfera</h1>
<p>Estude o campo elétrico de uma esfera.</p>

<div class="box">
<h2>Parâmetros</h2>

a: <input id="a" type="range" min="0.5" max="5" step="0.1" value="1"><span id="aval"></span><br>

b: <span id="bval"></span><br>

q2: <input id="q2" type="range" min="-20" max="20" step="0.1" value="5"><span id="q2val"></span><br>

<button onclick="toggleParticle()">Adicionar/remover partícula</button><br>

<div id="q1box">
q1: <input id="q1" type="range" min="-10" max="10" step="0.1" value="2"><span id="q1val"></span>
</div>

r: <input id="r" type="range" min="0.1" max="8" step="0.05" value="1.5"><span id="rval"></span>

</div>

<div class="box">
<h2>Imagem</h2>
<canvas id="canvas" width="500" height="500"></canvas>

<p>
Arraste a circunferência tracejada (superfície gaussiana) ou use o slider do raio r na seção “Parâmetros” para estudar o campo elétrico em diferentes regiões. Em telas pequenas, deslize horizontalmente a figura para enxergá-la por completo.
</p>
</div>

<div class="box">
<h2>Gráfico</h2>
<div id="grafico"></div>
</div>

<script>
let hasParticle = false;

function toggleParticle(){{
  hasParticle = !hasParticle;
  document.getElementById("q1box").style.display = hasParticle ? "block" : "none";
}}

function atualizar(){{
  let a = parseFloat(document.getElementById("a").value);
  let b = a + 0.5; // ✅ REGRA 4

  let q1 = parseFloat(document.getElementById("q1").value);
  let q2 = parseFloat(document.getElementById("q2").value);
  let r = parseFloat(document.getElementById("r").value);

  document.getElementById("aval").innerText = " = " + a.toFixed(2);
  document.getElementById("bval").innerText = b.toFixed(2);
  document.getElementById("q1val").innerText = q1.toFixed(2);
  document.getElementById("q2val").innerText = q2.toFixed(2);
  document.getElementById("rval").innerText = r.toFixed(2);

  // ✅ DESENHO COM ESCALA FIXA
  let ctx = document.getElementById("canvas").getContext("2d");
  ctx.clearRect(0,0,500,500);

  let center = 250;
  let scale = 30;

  ctx.beginPath();
  ctx.arc(center,center,a*scale,0,2*Math.PI);
  ctx.stroke();

  ctx.beginPath();
  ctx.arc(center,center,b*scale,0,2*Math.PI);
  ctx.stroke();

  ctx.setLineDash([5,5]);
  ctx.beginPath();
  ctx.arc(center,center,r*scale,0,2*Math.PI);
  ctx.stroke();
  ctx.setLineDash([]);

  // ✅ GRÁFICO CORRIGIDO
  let x = [];
  let y = [];

  for(let i=0.1;i<8;i+=0.05){{
    x.push(i);
    let val = 1/(4*Math.PI*8.8e-12)*(q2*1e-6)/(i*i);
    y.push(val);
  }}

  Plotly.newPlot("grafico",[
    {{x:x,y:y}}
  ]);
}}

document.querySelectorAll("input").forEach(el=>el.oninput=atualizar);

atualizar();
</script>

</body>
</html>
"""

components.html(html, height=1200, scrolling=True)
