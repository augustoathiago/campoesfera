import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

html = """
<!DOCTYPE html>
<html>
<head>

<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>

<style>
body {
  font-family: Arial;
  background: #ffffff;
  color: #111;
  margin: 20px;
}

.card {
  border:1px solid #ccc;
  padding:20px;
  border-radius:12px;
  margin-bottom:20px;
}

h1 { margin-bottom: 5px; }
</style>

</head>
<body>

<h1>Simulador Campo Elétrico Esfera</h1>
<p>Estude o campo elétrico de uma esfera.</p>

<div class="card">

<h2>Parâmetros</h2>

a:
<input id="a" type="range" min="0.5" max="5" step="0.1" value="1.0">
<span id="aval"></span><br><br>

b:
<span id="bval"></span><br><br>

q2 (μC):
<input id="q2" type="range" min="-20" max="20" step="0.1" value="5.0">
<span id="q2val"></span><br><br>

<button onclick="toggleParticle()">Adicionar/remover partícula</button><br><br>

<div id="q1box" style="display:none;">
q1 (μC):
<input id="q1" type="range" min="-10" max="10" step="0.1" value="2.0">
<span id="q1val"></span><br><br>
</div>

r:
<input id="r" type="range" min="0.1" max="8" step="0.05" value="1.5">
<span id="rval"></span>

</div>

<div class="card">

<h2>Imagem</h2>
<canvas id="canvas" width="600" height="600"></canvas>

<p>
Arraste a circunferência tracejada (superfície gaussiana) ou use o slider do raio r na seção “Parâmetros” para estudar o campo elétrico em diferentes regiões. Em telas pequenas, deslize horizontalmente a figura para enxergá-la por completo.
</p>

</div>

<div class="card">

<h2>Cargas</h2>
<div id="cargas"></div>

</div>

<div class="card">

<h2>Gráfico E × r</h2>
<div id="grafico"></div>

</div>

<script>

let hasParticle = false;

function toggleParticle(){
  hasParticle = !hasParticle;
  document.getElementById("q1box").style.display = hasParticle ? "block" : "none";
}

function fmt(num){
  return num.toFixed(2);
}

function atualizar(){

  let a = parseFloat(aRange.value);
  let b = a + 0.5;
  let q1 = parseFloat(q1Range.value);
  let q2 = parseFloat(q2Range.value);
  let r = parseFloat(rRange.value);

  aval.innerText = fmt(a);
  bval.innerText = fmt(b);
  q1val.innerText = fmt(q1);
  q2val.innerText = fmt(q2);
  rval.innerText = fmt(r);

  // DESENHO (ESCALA FIXA)
  let ctx = canvas.getContext("2d");
  ctx.clearRect(0,0,600,600);

  let center = 300;
  let scale = 40;

  // casca
  ctx.beginPath();
  ctx.arc(center,center,b*scale,0,2*Math.PI);
  ctx.stroke();

  ctx.beginPath();
  ctx.arc(center,center,a*scale,0,2*Math.PI);
  ctx.stroke();

  // superfície gaussiana
  ctx.setLineDash([5,5]);
  ctx.beginPath();
  ctx.arc(center,center,r*scale,0,2*Math.PI);
  ctx.stroke();
  ctx.setLineDash([]);

  // partículas
  if(hasParticle){
    ctx.beginPath();
    ctx.arc(center,center,6,0,2*Math.PI);
    ctx.fill();
  }

  // CARGAS
  let html = "";

  if(hasParticle){
    html += "q1 = " + fmt(q1) + " μC<br>";
  }

  html += "q2 = " + fmt(q2) + " μC<br><br>";

  if(hasParticle){
    html += "q2i = " + fmt(-q1) + " μC<br>";
    html += "q2e = " + fmt(q2 + q1) + " μC";
  }

  cargas.innerHTML = html;

  // GRÁFICO
  let x = [];
  let y = [];

  for(let i=0.1;i<8;i+=0.05){
    x.push(i);
    let Q = q2*1e-6;
    let E = Q/(4*Math.PI*8.8e-12*i*i);
    y.push(E);
  }

  Plotly.newPlot("grafico",[{
    x:x,
    y:y,
    type:"scatter"
  }],{
    paper_bgcolor:"#fff",
    plot_bgcolor:"#fff"
  });

}

document.querySelectorAll("input").forEach(i => i.oninput = atualizar);

atualizar();

</script>

</body>
</html>
"""

components.html(html, height=1200)
