import base64
import io
import math
import os

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from matplotlib import patches
import matplotlib.pyplot as plt

# ============================================================
# Configuração geral
# ============================================================
st.set_page_config(
    page_title="Simulador Campo Elétrico Esfera",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------
# Constante física (conforme solicitado pelo enunciado)
# ------------------------------------------------------------
EPSILON_0 = 8.8e-12  # C²/(N·m²)

# ------------------------------------------------------------
# Limites globais (mantêm a escala visual fixa na imagem)
# ------------------------------------------------------------
R_MIN = 0.10
R_MAX = 5.00
Q_MIN_uC = -100.0
Q_MAX_uC = 100.0
R_GAUSS_MIN = 0.00
R_GAUSS_MAX = 8.00

# ============================================================
# Funções auxiliares de formatação
# ============================================================
SUPERSCRIPT_MAP = str.maketrans("0123456789-+", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺")


def to_superscript(n: int) -> str:
    return str(n).translate(SUPERSCRIPT_MAP)


def format_decimal_br(value: float, casas: int = 3) -> str:
    """
    Formata número em pt-BR sem notação científica.
    """
    s = f"{value:.{casas}f}"
    return s.replace(".", ",")


def format_num_ptbr(value: float, unidade: str = "", sig: int = 4) -> str:
    """
    Formato amigável em pt-BR.
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


def color_from_charge(q_coulomb: float) -> str:
    if q_coulomb > 0:
        return "#d62828"  # vermelho
    elif q_coulomb < 0:
        return "#1d4ed8"  # azul
    return "#111111"      # preto


def alpha_fill_from_charge(q_coulomb: float) -> str:
    if q_coulomb > 0:
        return "#f7c7c7"
    elif q_coulomb < 0:
        return "#c9d9ff"
    return "#d7d7d7"


# ============================================================
# Física
# ============================================================
def q_gauss(Q_c: float, R: float, r: float, isolante: bool) -> float:
    """
    Carga contida na superfície gaussiana.
    """
    if r >= R:
        return Q_c
    if not isolante:
        return 0.0
    return Q_c * (r ** 3) / (R ** 3)


def area_gauss(r: float) -> float:
    return 4 * math.pi * (r ** 2)


def electric_field(Q_c: float, R: float, r: float, isolante: bool, eps0: float = EPSILON_0) -> float:
    """
    Campo elétrico radial em módulo no ponto r.
    Sinal indica sentido:
      >0  para fora (Q positiva)
      <0  para dentro (Q negativa)
    """
    if abs(r) < 1e-15:
        return 0.0

    if isolante:
        if r < R:
            # Dentro de esfera isolante uniformemente carregada:
            # E = Q r / (4π ε0 R^3)
            return Q_c * r / (4 * math.pi * eps0 * (R ** 3))
        else:
            # Fora:
            # E = Q / (4π ε0 r^2)
            return Q_c / (4 * math.pi * eps0 * (r ** 2))
    else:
        # Condutora:
        if r < R:
            return 0.0
        else:
            return Q_c / (4 * math.pi * eps0 * (r ** 2))


def electric_field_curve(Q_c: float, R: float, isolante: bool, eps0: float = EPSILON_0):
    """
    Retorna arrays para o gráfico E x r.
    """
    r_max_plot = max(3.0 * R, 1.25)
    r_max_plot = min(max(r_max_plot, R + 0.5), R_GAUSS_MAX)

    r_vals = np.linspace(0.001, r_max_plot, 800)

    if isolante:
        E_vals = np.where(
            r_vals < R,
            Q_c * r_vals / (4 * np.pi * eps0 * (R ** 3)),
            Q_c / (4 * np.pi * eps0 * (r_vals ** 2)),
        )
    else:
        E_vals = np.where(
            r_vals < R,
            0.0,
            Q_c / (4 * np.pi * eps0 * (r_vals ** 2)),
        )

    return r_vals, E_vals


# ============================================================
# Figura da esfera (matplotlib -> imagem em base64)
# ============================================================
def fig_to_base64(fig) -> str:
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=200, bbox_inches="tight", facecolor="white")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def draw_dimension(ax, x, r_value, label, color="#444444"):
    """
    Cota vertical do centro até o raio.
    """
    ax.plot([x, x], [0, r_value], color=color, linewidth=1.8)
    tick = 0.18
    ax.plot([x - tick, x + tick], [0, 0], color=color, linewidth=1.8)
    ax.plot([x - tick, x + tick], [r_value, r_value], color=color, linewidth=1.8)
    ax.annotate(
        "",
        xy=(x, r_value),
        xytext=(x, 0),
        arrowprops=dict(arrowstyle="<->", lw=1.8, color=color, shrinkA=0, shrinkB=0),
    )
    ax.text(
        x + 0.22,
        r_value / 2,
        label,
        fontsize=12,
        va="center",
        ha="left",
        color=color,
        bbox=dict(boxstyle="round,pad=0.20", fc="white", ec="none", alpha=0.9),
    )


def build_sphere_figure(R: float, r: float, Q_c: float, isolante: bool, E_at_r: float):
    """
    Constrói a imagem principal com:
      - esfera
      - superfície gaussiana
      - cotas de R e r
      - vetor E no ponto mais à direita da superfície gaussiana
      - boxes de Q e E
    """
    edge_color = color_from_charge(Q_c)
    fill_color = alpha_fill_from_charge(Q_c)

    # Escala fixa da figura (para variação de R ser visualmente percebida)
    xlim = (-8.6, 11.8)
    ylim = (-8.2, 8.2)

    fig, ax = plt.subplots(figsize=(11.5, 7.2))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # Título interno opcional discreto
    ax.text(
        -8.2,
        7.55,
        "Representação da esfera e da superfície gaussiana",
        fontsize=13,
        weight="bold",
        ha="left",
        va="center",
        color="#222222",
    )

    # Eixos de referência discretos
    ax.plot([xlim[0] + 0.4, xlim[1] - 0.4], [0, 0], color="#efefef", lw=1.0, zorder=0)
    ax.plot([0, 0], [ylim[0] + 0.4, ylim[1] - 0.4], color="#efefef", lw=1.0, zorder=0)

    # Desenho da esfera
    sphere_fill_alpha = 0.55 if isolante else 0.12

    sphere = patches.Circle(
        (0, 0),
        R,
        facecolor=fill_color,
        edgecolor=edge_color,
        linewidth=3.0,
        alpha=sphere_fill_alpha,
        zorder=2,
    )
    ax.add_patch(sphere)

    # Se condutora, enfatiza que a carga está na superfície externa
    if not isolante:
        ax.add_patch(
            patches.Circle(
                (0, 0),
                R,
                fill=False,
                edgecolor=edge_color,
                linewidth=4.0,
                zorder=3,
            )
        )
        ax.text(
            -7.9,
            -7.2,
            "Esfera condutora: carga concentrada na superfície externa",
            fontsize=11,
            color="#333333",
            ha="left",
            va="center",
        )
    else:
        ax.text(
            -7.9,
            -7.2,
            "Esfera isolante: distribuição volumétrica uniforme de carga",
            fontsize=11,
            color="#333333",
            ha="left",
            va="center",
        )

    # Superfície gaussiana
    gauss_color = "#666666"
    gauss = patches.Circle(
        (0, 0),
        r,
        fill=False,
        edgecolor=gauss_color,
        linewidth=2.4,
        linestyle="--",
        zorder=1,
    )
    ax.add_patch(gauss)

    # Labels centrais discretos
    ax.text(
        0,
        0,
        "centro",
        fontsize=10,
        ha="center",
        va="center",
        color="#4b5563",
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85),
        zorder=5,
    )

    # Cotas verticais ao lado da esfera
    x_dim_base = max(R, r) + 0.95
    x_dim_R = x_dim_base
    x_dim_r = x_dim_base + 1.05

    draw_dimension(ax, x_dim_R, R, "R")
    draw_dimension(ax, x_dim_r, r, "r")

    # Box da carga Q
    q_text_color = edge_color
    q_box_x = -8.0
    q_box_y = 5.7
    q_text = (
        f"Q = {format_num_ptbr(Q_c * 1e6, 'µC', sig=4)}\n"
        f"Q = {format_num_ptbr(Q_c, 'C', sig=4)}"
    )
    ax.text(
        q_box_x,
        q_box_y,
        q_text,
        fontsize=12,
        color=q_text_color,
        ha="left",
        va="top",
        bbox=dict(boxstyle="round,pad=0.45", fc="white", ec=q_text_color, lw=1.8),
        zorder=10,
    )

    # Vetor do campo elétrico no ponto mais à direita da superfície gaussiana
    px, py = r, 0
    E_mag = abs(E_at_r)

    if E_mag < 1e-20:
        # marca discreta do ponto sem seta
        ax.plot(px, py, marker="o", color="#111111", ms=5, zorder=8)
        ax.text(
            px + 0.4,
            py + 0.5,
            "E = 0",
            fontsize=12,
            color="#111111",
            ha="left",
            va="bottom",
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#111111", lw=1.5),
            zorder=10,
        )
    else:
        arrow_len = 1.15
        direction = 1 if E_at_r > 0 else -1
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
            zorder=9,
        )

        # Box do valor de E sem sobreposição
        e_box_x = px + (1.55 if direction > 0 else -4.55)
        e_box_y = 1.1
        e_text = (
            f"E(r) = {format_num_ptbr(E_at_r, 'N/C', sig=4)}\n"
            f"no ponto r = {format_num_ptbr(r, 'm', sig=4)}"
        )
        ax.text(
            e_box_x,
            e_box_y,
            e_text,
            fontsize=11.5,
            color=edge_color,
            ha="left",
            va="center",
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=edge_color, lw=1.6),
            zorder=10,
        )

    # Legenda discreta da superfície gaussiana
    ax.text(
        -8.0,
        3.55,
        "Superfície gaussiana (tracejada)",
        fontsize=11,
        color="#444444",
        ha="left",
        va="center",
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#666666", lw=1.2),
        zorder=10,
    )

    return fig


# ============================================================
# CSS
# ============================================================
st.markdown(
    """
    <style>
        .main {
            background-color: white;
        }

        .bloco {
            border: 1px solid #e5e7eb;
            border-radius: 16px;
            padding: 1rem 1rem 0.8rem 1rem;
            margin-bottom: 1rem;
            background: #ffffff;
            box-shadow: 0 1px 10px rgba(0,0,0,0.03);
        }

        .sec-titulo {
            font-size: 1.30rem;
            font-weight: 700;
            margin-bottom: 0.4rem;
            color: #111827;
        }

        .sec-subtitulo {
            font-size: 0.98rem;
            color: #374151;
            margin-bottom: 0.8rem;
        }

        div[data-testid="stSlider"] label p {
            font-size: 1.06rem !important;
            font-weight: 700 !important;
            color: #9b1c1c !important;
        }

        .formula-box {
            border-left: 5px solid #d1d5db;
            background: #fafafa;
            padding: 0.75rem 0.9rem;
            border-radius: 10px;
            margin-top: 0.4rem;
            margin-bottom: 0.5rem;
        }

        .small-note {
            color: #4b5563;
            font-size: 0.92rem;
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
            max-width: none;
            display: block;
            margin: 0 auto;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Cabeçalho
# ============================================================
col_logo, col_title = st.columns([1, 4], vertical_alignment="center")

with col_logo:
    if os.path.exists("logo_maua.png"):
        st.image("logo_maua.png", use_container_width=True)
    else:
        st.warning("Arquivo logo_maua.png não encontrado na mesma pasta do app.")

with col_title:
    st.markdown(
        """
        <div style="padding-top: 0.2rem;">
            <div style="font-size: 2rem; font-weight: 800; color: #111827;">
                Simulador Campo Elétrico Esfera
            </div>
            <div style="font-size: 1.05rem; color: #374151; margin-top: 0.15rem;">
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

p1, p2, p3 = st.columns([1.2, 1.2, 1.2])

with p1:
    R = st.number_input(
        "Raio externo R da esfera (m)",
        min_value=R_MIN,
        max_value=R_MAX,
        value=1.50,
        step=0.10,
        format="%.2f",
    )

with p2:
    Q_uC = st.number_input(
        "Carga Q da esfera (micronC)",
        min_value=Q_MIN_uC,
        max_value=Q_MAX_uC,
        value=8.0,
        step=1.0,
        format="%.2f",
    )

with p3:
    esfera_tipo = st.radio(
        "Tipo da esfera",
        ["Isolante", "Condutora"],
        horizontal=True,
    )
    isolante = esfera_tipo == "Isolante"

st.write("")

r = st.slider(
    "Raio da superfície gaussiana r (m) para estudo do campo elétrico",
    min_value=float(R_GAUSS_MIN),
    max_value=float(R_GAUSS_MAX),
    value=float(min(max(R + 0.5, 0.2), R_GAUSS_MAX)),
    step=0.01,
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
st.markdown(
    '<div class="sec-subtitulo">Escala fixa para permitir a comparação visual do tamanho da esfera e da superfície gaussiana.</div>',
    unsafe_allow_html=True
)

fig = build_sphere_figure(R, r, Q_c, isolante, E_r)
img_b64 = fig_to_base64(fig)
plt.close(fig)

st.markdown(
    f"""
    <div class="img-scroll-wrap">
        <img src="data:image/png;base64,{img_b64}" alt="Esfera e superfície gaussiana" />
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="small-note">Em telas pequenas, se necessário, deslize horizontalmente para visualizar toda a figura.</div>',
    unsafe_allow_html=True
)
st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# Lei de Gauss
# ============================================================
st.markdown('<div class="bloco">', unsafe_allow_html=True)
st.markdown('<div class="sec-titulo">Lei de Gauss</div>', unsafe_allow_html=True)

st.latex(r"\phi = \oint \vec{E}\cdot d\vec{A} = \frac{Q_{\mathrm{contida}}}{\varepsilon_0}")

st.markdown(
    """
- **\u03D5** é o **fluxo elétrico** na superfície gaussiana.  
- **E** é o **campo elétrico**.  
- **A** é a **área** da superfície gaussiana.  
- **Q** é a **carga contida** na superfície gaussiana.  
- **\u03B5₀** é a **permissividade do vácuo**:
"""
)

st.latex(r"\varepsilon_0 = 8{,}8 \times 10^{-12}\ \mathrm{C^2/(N\cdot m^2)}")
st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# Carga q_gauss
# ============================================================
st.markdown('<div class="bloco">', unsafe_allow_html=True)
st.markdown('<div class="sec-titulo">Carga q<sub>gauss</sub> contida na superfície gaussiana</div>', unsafe_allow_html=True)

if r >= R:
    st.markdown("**(i) A superfície gaussiana está fora da esfera.**")
    st.latex(r"q_{\mathrm{gauss}} = Q")
    st.latex(
        rf"q_{{\mathrm{{gauss}}}} = {Q_uC:.6f}\,\mu C = {Q_c:.6e}\,C"
    )
    st.markdown(
        f"Valor final: **q<sub>gauss</sub> = {format_num_ptbr(Q_uC, 'µC', sig=4)} = {format_num_ptbr(Q_c, 'C', sig=4)}**",
        unsafe_allow_html=True,
    )

else:
    if not isolante:
        st.markdown("**(ii) A superfície gaussiana está dentro da esfera condutora.**")
        st.latex(r"q_{\mathrm{gauss}} = 0")
        st.markdown(
            "Toda a carga está na **superfície externa** do condutor; portanto, a carga contida por uma superfície gaussiana interna é nula."
        )
        st.markdown(
            "Valor final: **q<sub>gauss</sub> = 0 C**",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("**(iii) A superfície gaussiana está dentro da esfera isolante.**")
        st.latex(r"\rho = \frac{Q}{V_{\mathrm{total}}} = \frac{q_{\mathrm{gauss}}}{V_r}")
        st.latex(r"\frac{Q}{\frac{4}{3}\pi R^3} = \frac{q_{\mathrm{gauss}}}{\frac{4}{3}\pi r^3}")
        st.latex(r"q_{\mathrm{gauss}} = Q\frac{r^3}{R^3}")

        qg_formula_num = Q_c * (r ** 3) / (R ** 3)
        st.latex(
            rf"q_{{\mathrm{{gauss}}}} = ({Q_c:.6e})\cdot\frac{{({r:.4f})^3}}{{({R:.4f})^3}} = {qg_formula_num:.6e}\ \mathrm{{C}}"
        )

        st.markdown(
            f"Valor final: **q<sub>gauss</sub> = {format_num_ptbr(qg, 'C', sig=4)}** "
            f"(**{format_num_ptbr(qg * 1e6, 'µC', sig=4)}**)",
            unsafe_allow_html=True,
        )

st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# Área da superfície gaussiana
# ============================================================
st.markdown('<div class="bloco">', unsafe_allow_html=True)
st.markdown('<div class="sec-titulo">Área da superfície gaussiana</div>', unsafe_allow_html=True)

st.latex(r"A = 4\pi r^2")
st.latex(
    rf"A = 4\pi({r:.4f})^2 = {A:.6f}\ \mathrm{{m^2}}"
)
st.markdown(
    f"Valor final: **A = {format_num_ptbr(A, 'm²', sig=5)}**",
    unsafe_allow_html=True,
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
    rf"E = \frac{{{qg:.6e}}}{{({A:.6e})({EPSILON_0:.6e})}} = {E_r:.6e}\ \mathrm{{N/C}}"
)

if abs(E_r) < 1e-20:
    sentido = "nulo"
elif E_r > 0:
    sentido = "para fora da esfera"
else:
    sentido = "para o centro da esfera"

st.markdown(
    f"Valor final: **E = {format_num_ptbr(E_r, 'N/C', sig=4)}**, com sentido **{sentido}**."
)
st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# Gráfico
# ============================================================
st.markdown('<div class="bloco">', unsafe_allow_html=True)
st.markdown('<div class="sec-titulo">Gráfico</div>', unsafe_allow_html=True)

r_vals, E_vals = electric_field_curve(Q_c, R, isolante)

# Ajuste automático do eixo y para boa visualização
abs_max = np.max(np.abs(E_vals)) if len(E_vals) else 1.0
if abs_max < 1e-12:
    y_lim = 1.0
else:
    y_lim = 1.12 * abs_max

linha_cor = color_from_charge(Q_c)

fig_plot = go.Figure()

fig_plot.add_trace(
    go.Scatter(
        x=r_vals,
        y=E_vals,
        mode="lines",
        name="E(r)",
        line=dict(color=linha_cor, width=3),
        hovertemplate="r = %{x:.4f} m<br>E = %{y:.6g} N/C<extra></extra>",
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
        hovertemplate="r = %{x:.4f} m<br>E = %{y:.6g} N/C<extra></extra>",
    )
)

fig_plot.update_layout(
    template=None,
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=30, r=20, t=20, b=30),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=420,
)

fig_plot.update_xaxes(
    title_text="Distância r (m)",
    showgrid=True,
    gridcolor="#e5e7eb",
    zeroline=True,
    zerolinecolor="#9ca3af",
    range=[0, max(r_vals)],
)

fig_plot.update_yaxes(
    title_text="Campo elétrico E (N/C)",
    showgrid=True,
    gridcolor="#e5e7eb",
    zeroline=True,
    zerolinecolor="#9ca3af",
    range=[-y_lim, y_lim] if np.min(E_vals) < 0 < np.max(E_vals) else None,
    exponentformat="power",
    showexponent="all",
)

st.plotly_chart(fig_plot, use_container_width=True, config={"displayModeBar": False})

st.markdown(
    '<div class="small-note">Os eixos se ajustam automaticamente para boa visualização do comportamento do campo elétrico, inclusive em celulares.</div>',
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# Rodapé didático opcional
# ============================================================
st.markdown(
    """
<div style="margin-top: 0.8rem; color: #4b5563; font-size: 0.95rem;">
Observação: o sinal de <strong>E</strong> indica o sentido radial do campo:
positivo = para fora da esfera; negativo = para o centro.
</div>
""",
    unsafe_allow_html=True,
)
