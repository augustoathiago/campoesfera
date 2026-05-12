import io
import math
import os
import base64

import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import patches
import plotly.graph_objects as go


# ============================================================
# Configuração geral
# ============================================================
st.set_page_config(
    page_title="Simulador Campo Elétrico Esfera",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Permissividade do vácuo conforme solicitado
EPSILON_0 = 8.8e-12  # C²/(N·m²)

# Limites dos controles
R_MIN = 0.10
R_MAX = 5.00
Q_MIN_uC = -100.0
Q_MAX_uC = 100.0
R_GAUSS_MIN = 0.00
R_GAUSS_MAX = 6.00


# ============================================================
# Funções auxiliares de formatação
# ============================================================
SUPERSCRIPT_MAP = str.maketrans("0123456789-+", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺")


def to_superscript(n: int) -> str:
    return str(n).translate(SUPERSCRIPT_MAP)


def format_num_ptbr(value: float, unidade: str = "", sig: int = 4) -> str:
    """
    Formatação amigável em pt-BR.
    Usa notação do tipo 1,23 × 10⁴ (nunca e4).
    """
    if abs(value) < 1e-15:
        texto = "0"
    else:
        av = abs(value)
        if 1e-3 <= av < 1e4:
            casas = max(0, sig - 1 - int(math.floor(math.log10(av))))
            texto = f"{value:.{casas}f}".replace(".", ",")
        else:
            expo = int(math.floor(math.log10(av)))
            mant = value / (10 ** expo)
            casas = max(0, sig - 1)
            mant_str = f"{mant:.{casas}f}".rstrip("0").rstrip(".").replace(".", ",")
            texto = f"{mant_str} × 10{to_superscript(expo)}"

    if unidade:
        return f"{texto} {unidade}"
    return texto


def format_latex_num(value: float, sig: int = 4) -> str:
    """
    Formatação para LaTeX:
    - evita notação e-06
    - usa \\times 10^{n}
    - usa vírgula decimal como 8{,}8
    """
    if abs(value) < 1e-15:
        return "0"

    av = abs(value)
    if 1e-3 <= av < 1e4:
        casas = max(0, sig - 1 - int(math.floor(math.log10(av))))
        s = f"{value:.{casas}f}"
        return s.replace(".", "{,}")
    else:
        expo = int(math.floor(math.log10(av)))
        mant = value / (10 ** expo)
        casas = max(0, sig - 1)
        mant_str = f"{mant:.{casas}f}".rstrip("0").rstrip(".").replace(".", "{,}")
        return rf"{mant_str}\times 10^{{{expo}}}"


def color_from_charge(q_coulomb: float) -> str:
    if q_coulomb > 0:
        return "#e53935"  # vermelho
    elif q_coulomb < 0:
        return "#2563eb"  # azul
    return "#111111"      # preto


def alpha_fill_from_charge(q_coulomb: float) -> str:
    if q_coulomb > 0:
        return "#f8c8c8"
    elif q_coulomb < 0:
        return "#cfe0ff"
    return "#d9d9d9"


def fig_to_base64(fig) -> str:
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=220, bbox_inches="tight", facecolor="white")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


# ============================================================
# Física
# ============================================================
def q_gauss(Q_c: float, R: float, r: float, isolante: bool) -> float:
    if r >= R:
        return Q_c
    if not isolante:
        return 0.0
    return Q_c * (r ** 3) / (R ** 3)


def area_gauss(r: float) -> float:
    return 4 * math.pi * (r ** 2)


def electric_field(Q_c: float, R: float, r: float, isolante: bool, eps0: float = EPSILON_0) -> float:
    """
    Campo elétrico radial no ponto r.
    Sinal:
    > 0 : para fora
    < 0 : para o centro
    """
    if abs(r) < 1e-15:
        return 0.0

    if isolante:
        if r < R:
            return Q_c * r / (4 * math.pi * eps0 * R**3)
        return Q_c / (4 * math.pi * eps0 * r**2)
    else:
        if r < R:
            return 0.0
        return Q_c / (4 * math.pi * eps0 * r**2)


def electric_field_curve(Q_c: float, R: float, isolante: bool, eps0: float = EPSILON_0):
    r_max_plot = min(max(3.0 * R, R + 0.6, 1.2), R_GAUSS_MAX)
    r_vals = np.linspace(0.001, r_max_plot, 900)

    if isolante:
        E_vals = np.where(
            r_vals < R,
            Q_c * r_vals / (4 * np.pi * eps0 * R**3),
            Q_c / (4 * np.pi * eps0 * r_vals**2),
        )
    else:
        E_vals = np.where(
            r_vals < R,
            0.0,
            Q_c / (4 * np.pi * eps0 * r_vals**2),
        )
    return r_vals, E_vals


# ============================================================
# Desenho da figura principal
# ============================================================
def draw_dimension_left(ax, x, radius_value, label_value, y_shift=0.0, color="#444444"):
    """
    Cota vertical à esquerda do círculo, mostrando apenas o valor.
    Texto na vertical.
    """
    ax.plot([x, x], [0, radius_value], color=color, linewidth=1.8, zorder=6)

    tick = 0.16
    ax.plot([x - tick, x + tick], [0, 0], color=color, linewidth=1.8, zorder=6)
    ax.plot([x - tick, x + tick], [radius_value, radius_value], color=color, linewidth=1.8, zorder=6)

    ax.annotate(
        "",
        xy=(x, radius_value),
        xytext=(x, 0),
        arrowprops=dict(arrowstyle="<->", lw=1.8, color=color, shrinkA=0, shrinkB=0),
        zorder=6,
    )

    ax.text(
        x - 0.35,
        radius_value / 2 + y_shift,
        label_value,
        fontsize=11.2,
        va="center",
        ha="center",
        rotation=90,
        color="#111827",
        bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.95),
        zorder=15,
    )


def build_sphere_figure(R: float, r: float, Q_c: float, isolante: bool, E_at_r: float):
    edge_color = color_from_charge(Q_c)
    fill_color = alpha_fill_from_charge(Q_c)

    # Escala fixa
    xlim = (-9.8, 11.2)
    ylim = (-7.8, 8.8)

    fig, ax = plt.subplots(figsize=(12.6, 7.8))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")

    # Linhas discretas de referência
    ax.plot([xlim[0] + 0.4, xlim[1] - 0.4], [0, 0], color="#ececec", lw=1.0, zorder=0)
    ax.plot([0, 0], [ylim[0] + 0.4, ylim[1] - 0.4], color="#ececec", lw=1.0, zorder=0)

    # Esfera
    sphere_alpha = 0.55 if isolante else 0.12
    sphere = patches.Circle(
        (0, 0),
        R,
        facecolor=fill_color,
        edgecolor=edge_color,
        linewidth=3.0,
        alpha=sphere_alpha,
        zorder=3,
    )
    ax.add_patch(sphere)

    if not isolante:
        ax.add_patch(
            patches.Circle(
                (0, 0),
                R,
                fill=False,
                edgecolor=edge_color,
                linewidth=4.0,
                zorder=4,
            )
        )

    # Superfície gaussiana
    gauss_color = "#5f6368"
    gauss = patches.Circle(
        (0, 0),
        r,
        fill=False,
        edgecolor=gauss_color,
        linewidth=2.5,
        linestyle="--",
        zorder=2,
    )
    ax.add_patch(gauss)

    # --------------------------------------------------------
    # Cotas à esquerda, sem sobreposição
    # --------------------------------------------------------
    # Separação horizontal maior entre elas
    left_base = -max(R, r) - 1.15
    x_dim_near = left_base
    x_dim_far = left_base - 1.45

    # Pequeno deslocamento vertical quando R e r são próximos
    y_shift_R = 0.0
    y_shift_r = 0.0
    if abs(R - r) < 0.60:
        y_shift_R = 0.45
        y_shift_r = -0.45

    # Mantém a maior cota mais à esquerda e a menor mais próxima
    if R >= r:
        x_dim_R = x_dim_far
        x_dim_r = x_dim_near
    else:
        x_dim_R = x_dim_near
        x_dim_r = x_dim_far

    draw_dimension_left(ax, x_dim_R, R, format_num_ptbr(R, "m", sig=4), y_shift=y_shift_R)
    draw_dimension_left(ax, x_dim_r, r, format_num_ptbr(r, "m", sig=4), y_shift=y_shift_r)

    # --------------------------------------------------------
    # Boxes acima dos círculos
    # --------------------------------------------------------
    q_box_text = (
        f"Q = {format_num_ptbr(Q_c * 1e6, 'µC', sig=4)}\n"
        f"Q = {format_num_ptbr(Q_c, 'C', sig=4)}"
    )
    ax.text(
        -7.6,
        8.05,
        q_box_text,
        fontsize=12,
        color=edge_color,
        ha="left",
        va="top",
        bbox=dict(boxstyle="round,pad=0.42", fc="white", ec=edge_color, lw=1.8),
        zorder=20,
    )

    if isolante:
        gauss_desc = "Superfície gaussiana (tracejada)\nEsfera isolante"
    else:
        gauss_desc = "Superfície gaussiana (tracejada)\nEsfera condutora"

    ax.text(
        1.8,
        8.05,
        gauss_desc,
        fontsize=11.5,
        color="#374151",
        ha="left",
        va="top",
        bbox=dict(boxstyle="round,pad=0.40", fc="white", ec="#6b7280", lw=1.4),
        zorder=20,
    )

    # --------------------------------------------------------
    # Vetor de campo no ponto mais à direita da superfície gaussiana
    # --------------------------------------------------------
    px, py = r, 0
    E_mag = abs(E_at_r)

    if E_mag < 1e-20:
        ax.plot(px, py, marker="o", color="#111111", ms=5, zorder=10)
        ax.text(
            px + 0.45,
            0.8,
            "E = 0 N/C",
            fontsize=11.5,
            color="#111111",
            ha="left",
            va="center",
            bbox=dict(boxstyle="round,pad=0.30", fc="white", ec="#111111", lw=1.4),
            zorder=20,
        )
    else:
        direction = 1 if E_at_r > 0 else -1
        arrow_len = 1.15
        dx = direction * arrow_len

        ax.annotate(
            "",
            xy=(px + dx, py),
            xytext=(px, py),
            arrowprops=dict(
                arrowstyle="->",
                lw=3.0,
                color=edge_color,
                shrinkA=0,
                shrinkB=0,
            ),
            zorder=12,
        )

        e_box_x = px + 1.55 if direction > 0 else px - 4.55
        ax.text(
            e_box_x,
            1.05,
            f"E(r) = {format_num_ptbr(E_at_r, 'N/C', sig=4)}",
            fontsize=11.5,
            color=edge_color,
            ha="left",
            va="center",
            bbox=dict(boxstyle="round,pad=0.32", fc="white", ec=edge_color, lw=1.5),
            zorder=20,
        )

    return fig


# ============================================================
# CSS
# ============================================================
st.markdown(
    """
    <style>
        .stApp {
            background: #ffffff !important;
            color: #111827 !important;
        }

        html, body, [class*="css"] {
            color: #111827 !important;
        }

        .main, .block-container {
            background: #ffffff !important;
            color: #111827 !important;
        }

        h1, h2, h3, h4, h5, h6, p, li, span, div, label {
            color: #111827 !important;
        }

        .bloco {
            border: 1px solid #e5e7eb;
            border-radius: 16px;
            padding: 1rem 1rem 0.85rem 1rem;
            margin-bottom: 1rem;
            background: #ffffff;
            box-shadow: 0 1px 10px rgba(0,0,0,0.04);
        }

        .sec-titulo {
            font-size: 1.28rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
            color: #111827 !important;
        }

        div[data-testid="stSlider"] label p {
            font-size: 1.02rem !important;
            font-weight: 700 !important;
            color: #9b1c1c !important;
        }

        .img-scroll-wrap {
            width: 100%;
            overflow-x: auto;
            overflow-y: hidden;
            border: 1px solid #e5e7eb;
            border-radius: 16px;
            padding: 0.5rem;
            background: white;
        }

        .img-scroll-wrap img {
            display: block;
            width: 1180px;
            max-width: none;
            height: auto;
        }

        div[data-baseweb="radio"] * {
            color: #111827 !important;
        }

        div[data-testid="stLatex"] {
            overflow-x: auto;
        }

        /* melhora ajuste do gráfico em telas menores */
        @media (max-width: 768px) {
            .img-scroll-wrap img {
                width: 1050px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Estados iniciais (para não vincular r a R)
# ============================================================
if "R_slider" not in st.session_state:
    st.session_state.R_slider = 1.50

if "Q_slider" not in st.session_state:
    st.session_state.Q_slider = 8.0

if "r_slider" not in st.session_state:
    st.session_state.r_slider = 2.00

if "tipo_esfera" not in st.session_state:
    st.session_state.tipo_esfera = "Isolante"


# ============================================================
# Cabeçalho
# ============================================================
col_logo, col_title = st.columns([1, 4], vertical_alignment="center")

with col_logo:
    if os.path.exists("logo_maua.png"):
        st.image("logo_maua.png", use_container_width=True)
    else:
        st.warning("Arquivo logo_maua.png não encontrado.")

with col_title:
    st.markdown(
        """
        <div style="padding-top: 0.15rem;">
            <div style="font-size: 2rem; font-weight: 800; color: #111827;">
                Simulador Campo Elétrico Esfera
            </div>
            <div style="font-size: 1.05rem; color: #374151; margin-top: 0.12rem;">
                Estude o campo elétrico de uma esfera.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")


# ============================================================
# Parâmetros
# ============================================================
st.markdown('<div class="bloco">', unsafe_allow_html=True)
st.markdown('<div class="sec-titulo">Parâmetros</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns([1.35, 1.35, 1.1], vertical_alignment="center")

with c1:
    R = st.slider(
        "Raio externo R da esfera (m)",
        min_value=float(R_MIN),
        max_value=float(R_MAX),
        step=0.01,
        key="R_slider",
    )

with c2:
    Q_uC = st.slider(
        "Carga Q da esfera (µC)",
        min_value=float(Q_MIN_uC),
        max_value=float(Q_MAX_uC),
        step=0.1,
        key="Q_slider",
    )

with c3:
    esfera_tipo = st.radio(
        "Tipo da esfera",
        ["Isolante", "Condutora"],
        horizontal=True,
        key="tipo_esfera",
    )
    isolante = esfera_tipo == "Isolante"

st.write("")

r = st.slider(
    "Raio da superfície gaussiana r (m) para estudo do campo elétrico",
    min_value=float(R_GAUSS_MIN),
    max_value=float(R_GAUSS_MAX),
    step=0.01,
    key="r_slider",
)

st.markdown("</div>", unsafe_allow_html=True)

Q_c = Q_uC * 1e-6
qg = q_gauss(Q_c, R, r, isolante)
A = area_gauss(r)
E_r = electric_field(Q_c, R, r, isolante)


# ============================================================
# Imagem
# ============================================================
st.markdown('<div class="bloco">', unsafe_allow_html=True)
st.markdown('<div class="sec-titulo">Imagem</div>', unsafe_allow_html=True)

fig = build_sphere_figure(R, r, Q_c, isolante, E_r)
img_b64 = fig_to_base64(fig)
plt.close(fig)

st.markdown(
    f"""
    <div class="img-scroll-wrap">
        <img src="data:image/png;base64,{img_b64}" alt="Figura da esfera e superfície gaussiana">
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# Lei de Gauss
# ============================================================
st.markdown('<div class="bloco">', unsafe_allow_html=True)
st.markdown('<div class="sec-titulo">Lei de Gauss</div>', unsafe_allow_html=True)

st.latex(r"\phi = \oint \vec{E}\cdot d\vec{A} = \frac{q_{\mathrm{gauss}}}{\varepsilon_0}")

st.markdown(
    """
- **φ** é o **fluxo elétrico** na superfície gaussiana.  
- **E** é o **campo elétrico**.  
- **A** é a **área** da superfície gaussiana.  
- **q<sub>gauss</sub>** é a **carga contida** na superfície gaussiana.  
- **ε₀** é a **permissividade do vácuo**.
    """,
    unsafe_allow_html=True,
)

st.latex(r"\varepsilon_0 = 8{,}8 \times 10^{-12}\ \mathrm{C^2/(N\cdot m^2)}")
st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# Carga q_gauss
# ============================================================
st.markdown('<div class="bloco">', unsafe_allow_html=True)
st.markdown('<div class="sec-titulo">Carga q<sub>gauss</sub> contida na superfície gaussiana</div>', unsafe_allow_html=True)

if r >= R:
    st.markdown("**(i) Se a superfície gaussiana estiver fora da esfera:**")
    st.latex(r"q_{\mathrm{gauss}} = Q")
    st.latex(
        rf"q_{{\mathrm{{gauss}}}} = {format_latex_num(Q_uC, 4)}\ \mu C = {format_latex_num(Q_c, 4)}\ C"
    )

elif not isolante:
    st.markdown("**(ii) Se a superfície gaussiana estiver dentro da esfera condutora:**")
    st.latex(r"q_{\mathrm{gauss}} = 0")
    st.markdown("Toda a carga está na superfície externa.")

else:
    st.markdown("**(iii) Se a superfície gaussiana estiver dentro da esfera isolante:**")
    st.latex(r"\rho = \frac{Q}{V_{\mathrm{total}}} = \frac{q_{\mathrm{gauss}}}{V_r}")
    st.latex(r"\frac{Q}{\frac{4}{3}\pi R^3} = \frac{q_{\mathrm{gauss}}}{\frac{4}{3}\pi r^3}")
    st.latex(r"q_{\mathrm{gauss}} = Q\frac{r^3}{R^3}")
    st.latex(
        rf"q_{{\mathrm{{gauss}}}} = "
        rf"\left({format_latex_num(Q_c, 4)}\right)"
        rf"\frac{{\left({format_latex_num(r, 4)}\right)^3}}{{\left({format_latex_num(R, 4)}\right)^3}}"
        rf" = {format_latex_num(qg, 4)}\ C"
    )

st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# Área da superfície gaussiana
# ============================================================
st.markdown('<div class="bloco">', unsafe_allow_html=True)
st.markdown('<div class="sec-titulo">Área da superfície gaussiana</div>', unsafe_allow_html=True)

st.latex(r"A = 4\pi r^2")
st.latex(
    rf"A = 4\pi\left({format_latex_num(r, 4)}\right)^2 = {format_latex_num(A, 5)}\ \mathrm{{m^2}}"
)

st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# Campo elétrico
# ============================================================
st.markdown('<div class="bloco">', unsafe_allow_html=True)
st.markdown('<div class="sec-titulo">Campo elétrico</div>', unsafe_allow_html=True)

st.markdown(
    "Lei de Gauss no caso de simetria, campo constante **E** em toda superfície gaussiana e sempre paralelo ao vetor área."
)
st.latex(r"EA = \frac{q_{\mathrm{gauss}}}{\varepsilon_0}")
st.latex(r"E = \frac{q_{\mathrm{gauss}}}{A\varepsilon_0}")
st.latex(
    rf"E = \frac{{{format_latex_num(qg, 4)}}}{{\left({format_latex_num(A, 5)}\right)\left({format_latex_num(EPSILON_0, 3)}\right)}}"
    rf" = {format_latex_num(E_r, 4)}\ \mathrm{{N/C}}"
)

st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# Gráfico
# ============================================================
st.markdown('<div class="bloco">', unsafe_allow_html=True)
st.markdown('<div class="sec-titulo">Gráfico</div>', unsafe_allow_html=True)

r_vals, E_vals = electric_field_curve(Q_c, R, isolante)
linha_cor = color_from_charge(Q_c)

abs_max = np.max(np.abs(E_vals)) if len(E_vals) else 1.0
if abs_max < 1e-12:
    y_lim = 1.0
else:
    y_lim = 1.12 * abs_max

hover_texts = [
    f"r = {format_num_ptbr(rv, 'm', sig=4)}<br>E = {format_num_ptbr(ev, 'N/C', sig=4)}"
    for rv, ev in zip(r_vals, E_vals)
]

fig_plot = go.Figure()

fig_plot.add_trace(
    go.Scatter(
        x=r_vals,
        y=E_vals,
        mode="lines",
        name="E(r)",
        line=dict(color=linha_cor, width=3),
        text=hover_texts,
        hovertemplate="%{text}<extra></extra>",
    )
)

fig_plot.add_vline(
    x=R,
    line_width=2,
    line_dash="dash",
    line_color="#6b7280",
    annotation_text="R",
    annotation_position="top left",
)

fig_plot.add_trace(
    go.Scatter(
        x=[r],
        y=[E_r],
        mode="markers",
        name="Ponto estudado",
        marker=dict(size=10, color="#111111"),
        text=[f"r = {format_num_ptbr(r, 'm', sig=4)}<br>E = {format_num_ptbr(E_r, 'N/C', sig=4)}"],
        hovertemplate="%{text}<extra></extra>",
    )
)

fig_plot.update_layout(
    template=None,
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=95, r=18, t=18, b=42),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=360,
    font=dict(color="#111827"),
    dragmode=False,
)

fig_plot.update_xaxes(
    title_text="Distância r (m)",
    title_font=dict(size=15),
    automargin=True,
    showgrid=True,
    gridcolor="#e5e7eb",
    zeroline=True,
    zerolinecolor="#9ca3af",
    range=[0, float(max(r_vals))],
    fixedrange=True,
)

if np.min(E_vals) < 0 < np.max(E_vals):
    y_range = [-y_lim, y_lim]
else:
    y_range = None

fig_plot.update_yaxes(
    title_text="Campo elétrico E (N/C)",
    title_font=dict(size=15),
    title_standoff=18,
    automargin=True,
    showgrid=True,
    gridcolor="#e5e7eb",
    zeroline=True,
    zerolinecolor="#9ca3af",
    range=y_range,
    exponentformat="power",
    showexponent="all",
    fixedrange=True,
)

st.plotly_chart(
    fig_plot,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "responsive": True,
        "scrollZoom": False,
        "doubleClick": False,
        "showTips": False,
    },
)

st.markdown("</div>", unsafe_allow_html=True)
