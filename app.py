
from pathlib import Path
import base64
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Simulador Campo Elétrico Esfera", layout="wide")

BASE_DIR = Path(__file__).parent
html_path = BASE_DIR / "simulador_esfera.html"
html = html_path.read_text(encoding="utf-8")

logo_path = BASE_DIR / "logo_maua.png"
if logo_path.exists():
    mime = "image/png"
    data = base64.b64encode(logo_path.read_bytes()).decode("ascii")
    html = html.replace('src="logo_maua.png"', f'src="data:{mime};base64,{data}"')

components.html(html, height=3600, scrolling=True)
