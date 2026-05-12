import io
import base64
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from PIL import Image
from matplotlib.patches import Circle, FancyArrowPatch

# ============================================================
# CONFIGURAÇÃO GERAL
# ============================================================
st.set_page_config(
    page_title="Simulador Campo Elétrico Esfera",
    layout="wide",
    initial_sidebar_state="collapsed"
)

EPS0 = 8.854e-12  # permissividade do vácuo (C²/N·m²)
K = 1 / (4 * np.pi * EPS0)

# Faixas máximas dos sliders (usadas para manter escala fixa na imagem)
A_MAX = 5.0
B_MAX = 6.0
R_MAX_GLOBAL = 2.5 * B_MAX  # 15 m

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================
def cor_carga(q):
    if q > 1e-18:
        return "red"
    if q < -1e-18:
        return "blue"
    return "black"


def fmt_num(x, casas=4):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "indefinido"
    if abs(x) >= 1e4 or (abs(x) > 0 and abs(x) < 1e-3):
        s = f"{x:.{casas}e}"
        mantissa, expoente = s.split("e")
        mantissa = mantissa.replace(".", ",")
        return f"{mantissa}×10^{int(expoente)}"
    return f"{x:.{casas}f}".replace(".", ",")


def fmt_coulomb(q_c):
    return f"{fmt_num(q_c, 4)} C"


def fmt_microc(q_micro):
    return f"{fmt_num(q_micro, 4)} μC"


def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=180, bbox_inches="tight", facecolor="white")
    buf.seek(0)
    img_bytes = buf.read()
    plt.close(fig)
    return base64.b64encode(img_bytes).decode()


def carga_superficies(condutor, a, q1, q2):
    """
    Retorna (qint, qext) em Coulomb.
    q2 é a carga total da esfera/casca.
    """
    if condutor:
        if a > 0 and abs(q1) > 1e-18:
            # Fisicamente correto:
            # carga induzida na superfície interna é oposta a q1
            qint = -q1
            qext = q2 - qint
        else:
            qint = 0.0
            qext = q2
    else:
        qint = 0.0
        qext = 0.0
    return qint, qext


def Q_enc(r, a, b, q1, q2, condutor):
    if r <= 0:
        return 0.0

    if condutor:
        if a == 0:
            # esfera maciça condutora
            if r < b:
                return 0.0
            return q2
        else:
            # casca condutora com possível partícula central
            qint, _ = carga_superficies(condutor, a, q1, q2)
            if r < a:
                return q1
            elif r < b:
                return q1 + qint
            else:
                return q1 + q2
    else:
        # isolante
        if a == 0:
            # esfera maciça isolante
            if r < b:
                return q2 * (r**3) / (b**3)
            return q2
        else:
            # casca esférica isolante
            if r < a:
                return q1
            elif r < b:
                frac = (r**3 - a**3) / (b**3 - a**3)
                return q1 + q2 * frac
            else:
                return q1 + q2


def E_no_raio(r, a, b, q1, q2, condutor):
    if r <= 0:
        return np.nan
    Q = Q_enc(r, a, b, q1, q2, condutor)
    return K * Q / (r**2)


def gerar_curva_E(a, b, q1, q2, condutor, r_ref, n=1400):
    r_min = 1e-4
    r_max = max(2.2 * b, b + 0.5, r_ref, 2.5 * b)
    rs = np.linspace(r_min, r_max, n)
    Es = np.array([E_no_raio(r, a, b, q1, q2, condutor) for r in rs])
    return rs, Es


def desenhar_sistema(a, b, r_g, q1, q2, condutor):
    qint, qext = carga_superficies(condutor, a, q1, q2)
    E_r = E_no_raio(r_g, a, b, q1, q2, condutor)

    # ESCALA FIXA EM UNIDADES REAIS (m)
    # Mantém a mesma escala independentemente dos valores escolhidos.
    x_left = -7.5
    x_right = 18.5
    y_bottom = -16.0
    y_top = 16.0

    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_aspect("equal")
    ax.set_xlim(x_left, x_right)
    ax.set_ylim(y_bottom, y_top)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    cor_part = cor_carga(q1)
    cor_q2 = cor_carga(q2)
    cor_int = cor_carga(qint)
    cor_ext = cor_carga(qext)

    # -------- Esfera/casca --------
    if not condutor:
        if a == 0:
            esfera = Circle((0, 0), b, facecolor=cor_q2, edgecolor=cor_q2, alpha=0.15, linewidth=2.5)
            ax.add_patch(esfera)
            ax.add_patch(Circle((0, 0), b, fill=False, edgecolor=cor_q2, linewidth=3))
        else:
            ax.add_patch(Circle((0, 0), b, facecolor=cor_q2, edgecolor="none", alpha=0.15))
            ax.add_patch(Circle((0, 0), a, facecolor="white", edgecolor="none"))
            ax.add_patch(Circle((0, 0), a, fill=False, edgecolor=cor_q2, linewidth=3))
            ax.add_patch(Circle((0, 0), b, fill=False, edgecolor=cor_q2, linewidth=3))
    else:
        if a == 0:
            ax.add_patch(Circle((0, 0), b, facecolor="#d9d9d9", edgecolor=cor_ext, alpha=0.35, linewidth=3))
        else:
            ax.add_patch(Circle((0, 0), b, facecolor="#d9d9d9", edgecolor="none", alpha=0.35))
            ax.add_patch(Circle((0, 0), a, facecolor="white", edgecolor="none"))
            ax.add_patch(Circle((0, 0), a, fill=False, edgecolor=cor_int if abs(qint) > 1e-18 else "gray", linewidth=3))
            ax.add_patch(Circle((0, 0), b, fill=False, edgecolor=cor_ext if abs(qext) > 1e-18 else "gray", linewidth=3))

    # -------- Superfície gaussiana --------
    ax.add_patch(Circle((0, 0), r_g, fill=False, edgecolor="green", linestyle="--", linewidth=2.4))

    # -------- Partícula central --------
    if a > 0 and abs(q1) > 1e-18:
        raio_particula = max(0.16, 0.03 * B_MAX)
        ax.add_patch(Circle((0, 0), raio_particula, facecolor=cor_part, edgecolor="black", linewidth=0.8))
        ax.text(0.35, 0.35, "q1", fontsize=13, color=cor_part, weight="bold")

    # -------- Cotas verticais de RAIO --------
    # raio externo b: do centro até a borda superior
    x_dim_b = -5.2
    ax.annotate(
        "", xy=(x_dim_b, 0), xytext=(x_dim_b, b),
        arrowprops=dict(arrowstyle="<->", lw=1.8, color="black")
    )
    ax.plot([x_dim_b + 0.15, 0], [0, 0], color="black", lw=1)
    ax.plot([x_dim_b + 0.15, 0], [b, b], color="black", lw=1)
    ax.text(
        x_dim_b - 0.35, b / 2, f"raio externo b = {fmt_num(b, 3)} m",
        rotation=90, va="center", ha="center", fontsize=11
    )

    # raio interno a: do centro até a borda interna superior
    if a > 0:
        x_dim_a = -6.3
        ax.annotate(
            "", xy=(x_dim_a, 0), xytext=(x_dim_a, a),
            arrowprops=dict(arrowstyle="<->", lw=1.6, color="black")
        )
        ax.plot([x_dim_a + 0.15, 0], [0, 0], color="black", lw=1)
        ax.plot([x_dim_a + 0.15, 0], [a, a], color="black", lw=1)
        ax.text(
            x_dim_a - 0.35, a / 2, f"raio interno a = {fmt_num(a, 3)} m",
            rotation=90, va="center", ha="center", fontsize=11
        )

    # -------- Vetor de campo no ponto mais à direita da superfície gaussiana --------
    x0, y0 = r_g, 0
    comprimento = 1.5
    if np.isfinite(E_r):
        x1 = x0 + comprimento if E_r >= 0 else x0 - comprimento
        ax.add_patch(
            FancyArrowPatch((x0, y0), (x1, y0), arrowstyle="->", mutation_scale=18, lw=2.2, color="purple")
        )
        ax.text((x0 + x1) / 2, 0.5, "E", color="purple", fontsize=13, weight="bold", ha="center")

    # -------- Box do valor do campo --------
    box_x = min(max(r_g + 1.0, 8.5), 13.8)
    box_y = 6.2
    ax.text(
        box_x, box_y,
        f"Campo elétrico\nE(r) = {fmt_num(E_r, 4)} N/C",
        fontsize=11,
        ha="left",
        va="top",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#f7f7f7", edgecolor="gray")
    )

    # -------- Box com cargas --------
    linhas = [
        ("q1", f"{fmt_num(q1 * 1e6, 4)} μC", cor_part),
        ("q2", f"{fmt_num(q2 * 1e6, 4)} μC", cor_q2)
    ]

    if abs(qint) > 1e-18:
        linhas.append(("qint", f"{fmt_num(qint * 1e6, 4)} μC", cor_int))
    if abs(qext) > 1e-18:
        linhas.append(("qext", f"{fmt_num(qext * 1e6, 4)} μC", cor_ext))

    x_box = 8.3
    y_top_box = -0.2
    ax.text(
        x_box, y_top_box + 1.4, "Cargas", fontsize=12, weight="bold",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="gray")
    )
    for i, (rotulo, valor, cor) in enumerate(linhas):
        ax.text(x_box, y_top_box + 0.9 - 0.85 * i, f"{rotulo} = {valor}", color=cor, fontsize=11)

    ax.text(-1.2, -14.3, "Superfície gaussiana (verde tracejado)", color="green", fontsize=10)
    ax.text(-1.2, -15.1, "Vetor do campo elétrico (roxo)", color="purple", fontsize=10)

    return fig


def bloco_titulo():
    c1, c2 = st.columns([1, 3])

    with c1:
        try:
            logo = Image.open("logo_maua.png")
            st.image(logo, use_container_width=True)
        except Exception:
            st.markdown(
                """
                <div style="height:120px; display:flex; align-items:center; justify-content:center;
                            border:1px solid #ccc; border-radius:10px; background:#fafafa; color:#444;">
                    <span>logo_maua.png</span>
                </div>
                """,
                unsafe_allow_html=True
            )

    with c2:
        st.markdown(
            """
            <h1 style="margin-bottom:0.2rem;">Simulador Campo Elétrico Esfera</h1>
            <p style="font-size:1.1rem; margin-top:0;">Estude o campo elétrico de uma esfera.</p>
            """,
            unsafe_allow_html=True
        )


def caixa_rolavel_imagem(fig):
    img_b64 = fig_to_base64(fig)
    st.markdown(
        f"""
        <div style="overflow-x:auto; width:100%; border:1px solid #ddd; border-radius:10px; padding:8px; background:white;">
            <img src="data:image/png;base64,{img_b64}" style="display:block; width:1450px; max-width:none; height:auto;" />
        </div>
        """,
        unsafe_allow_html=True
    )


def secao_carga_na_esfera(a, q1, q2, qint, qext, condutor):
    st.header("Carga na esfera")

    if not condutor:
        st.write("**Carga distribuída homogeneamente por ser material isolante:**")
        st.latex(rf"q_2 = {q2:.6e}\ \text{{C}}")
        return

    if a == 0 or abs(q1) < 1e-18:
        st.write("**Carga toda na superfície externa por ser material condutor:**")
        st.latex(rf"q_2 = {q2:.6e}\ \text{{C}}")
        return

    st.write("A partícula atrai cargas para a superfície interna da casca condutora:")
    st.latex(rf"q_{{2i}} = -q_1 = -({q1:.6e}) = {qint:.6e}\ \text{{C}}")
    st.write("Como a carga total da casca é q₂, então:")
    st.latex(r"q_2 = q_{2i} + q_{2e}")
    st.write("Em seguida:")
    st.latex(r"q_{2e} = q_2 - q_{2i}")
    st.write("Substituindo os valores:")
    st.latex(rf"q_{{2e}} = {q2:.6e} - ({qint:.6e}) = {qext:.6e}\ \text{{C}}")


# ============================================================
# TÍTULO
# ============================================================
bloco_titulo()
st.markdown("---")

# ============================================================
# PARÂMETROS
# ============================================================
st.header("Parâmetros")
colA, colB = st.columns([1.15, 1])

with colA:
    st.subheader("Geometria e cargas")

    a = st.slider("Raio interno a da esfera (m)", min_value=0.0, max_value=A_MAX, value=1.0, step=0.05)

    b_min = max(a + 0.05, 0.05)
    b_default = max(b_min, 2.0)
    b = st.slider("Raio externo b da esfera (m)", min_value=float(b_min), max_value=B_MAX, value=float(min(b_default, B_MAX)), step=0.05)

    q1_default = 5.0 if a > 0 else 0.0
    q1_micro = st.slider(
        "Carga da partícula q1 (μC)",
        min_value=-20.0,
        max_value=20.0,
        value=float(q1_default),
        step=0.5,
        disabled=(a == 0)
    )

    if a == 0:
        st.info("Como a = 0, a esfera é maciça. A partícula central q1 fica desabilitada neste modelo.")

    q2_micro = st.slider("Carga da casca esférica q2 (μC)", min_value=-40.0, max_value=40.0, value=10.0, step=0.5)

    condutor = st.toggle("Considerar esfera condutora", value=False)

    if condutor:
        st.success("Modo selecionado: esfera condutora")
    else:
        st.info("Modo selecionado: esfera isolante")

with colB:
    st.subheader("Superfície gaussiana")

    r_max_slider = max(2.5 * b, b + 0.5)
    r_default = min(max(0.75 * b, 0.05), r_max_slider)

    r_g = st.slider(
        "Raio da superfície gaussiana r (m) para estudo do campo elétrico",
        min_value=0.001,
        max_value=float(r_max_slider),
        value=float(r_default),
        step=0.01
    )

    st.markdown(
        """
        <div style="padding:14px; border:2px solid #0f62fe; border-radius:12px; background:#f8fbff; color:#111111;">
            <b>Destaque:</b> ajuste o raio <b>r</b> da superfície gaussiana para analisar
            como a carga contida e o campo elétrico variam com a posição.
        </div>
        """,
        unsafe_allow_html=True
    )

# Conversão para SI
q1 = q1_micro * 1e-6
q2 = q2_micro * 1e-6

qint, qext = carga_superficies(condutor, a, q1, q2)
Q = Q_enc(r_g, a, b, q1, q2, condutor)
A = 4 * np.pi * (r_g ** 2)
E = E_no_raio(r_g, a, b, q1, q2, condutor)

st.markdown("---")

# ============================================================
# IMAGEM
# ============================================================
st.header("Imagem")
fig_sistema = desenhar_sistema(a, b, r_g, q1, q2, condutor)
caixa_rolavel_imagem(fig_sistema)

st.markdown("---")

# ============================================================
# LEI DE GAUSS
# ============================================================
st.header("Lei de Gauss")

st.latex(r"\phi = \oint \vec{E}\cdot d\vec{A} = \frac{Q}{\varepsilon_0}")

st.write("• φ é o fluxo elétrico na superfície gaussiana.")
st.write("• E é o campo elétrico.")
st.write("• A é a área da superfície gaussiana.")
st.write("• Q é a carga contida na superfície gaussiana.")
st.write("• ε₀ é a permissividade do vácuo: ε₀ = 8,85 × 10⁻¹² C²/(N·m²).")

st.markdown("---")

# ============================================================
# CARGA NA ESFERA
# ============================================================
secao_carga_na_esfera(a, q1, q2, qint, qext, condutor)

st.markdown("---")

# ============================================================
# CARGA Q CONTIDA NA SUPERFÍCIE GAUSSIANA
# ============================================================
st.header("Carga Q contida na superfície gaussiana")

if not condutor:
    if a == 0:
        # esfera maciça isolante
        if r_g < b:
            Q_calc = q2 * (r_g ** 3) / (b ** 3)

            st.write("Como a superfície gaussiana está dentro da esfera maciça isolante:")
            st.latex(r"\rho = \frac{q_2}{V_{total}} = \frac{Q}{V_r}")
            st.write("sendo V o volume e ρ a densidade de carga volumétrica.")
            st.latex(r"\frac{q_2}{\frac{4}{3}\pi b^3} = \frac{Q}{\frac{4}{3}\pi r^3}")
            st.latex(r"Q = q_2\frac{r^3}{b^3}")
            st.write("Substituindo os valores:")
            st.latex(rf"Q = ({q2:.6e})\frac{{({r_g:.4f})^3}}{{({b:.4f})^3}} = {Q_calc:.6e}\ \text{{C}}")
        else:
            st.write("Como a superfície gaussiana está fora da esfera, toda a carga é envolvida:")
            st.latex(rf"Q = q_2 = {q2:.6e}\ \text{{C}}")
    else:
        # casca isolante
        if r_g < a:
            st.write("Como a superfície gaussiana está na cavidade, a carga contida é apenas a partícula central:")
            st.latex(rf"Q = q_1 = {q1:.6e}\ \text{{C}}")
        elif r_g < b:
            Q_shell = q2 * ((r_g ** 3 - a ** 3) / (b ** 3 - a ** 3))
            Q_total = q1 + Q_shell

            st.write("Como a superfície gaussiana está dentro da espessura da casca esférica isolante:")
            st.latex(r"\rho = \frac{q_2}{V_{total}} = \frac{Q_{casca}}{V_r}")
            st.write("sendo V o volume.")
            st.latex(r"\frac{q_2}{\frac{4}{3}\pi(b^3-a^3)} = \frac{Q_{casca}}{\frac{4}{3}\pi(r^3-a^3)}")
            st.latex(r"Q_{casca} = q_2\frac{r^3-a^3}{b^3-a^3}")
            st.write("Substituindo os valores:")
            st.latex(
                rf"Q_{{casca}} = ({q2:.6e})\frac{{({r_g:.4f})^3-({a:.4f})^3}}{{({b:.4f})^3-({a:.4f})^3}} = {Q_shell:.6e}\ \text{{C}}"
            )
            st.write("Como existe a partícula central, a carga total contida é:")
            st.latex(rf"Q = q_1 + Q_{{casca}} = {q1:.6e} + {Q_shell:.6e} = {Q_total:.6e}\ \text{{C}}")
        else:
            st.write("Como a superfície gaussiana está fora da esfera, toda a carga é envolvida:")
            st.latex(rf"Q = q_1 + q_2 = {q1:.6e} + {q2:.6e} = {(q1 + q2):.6e}\ \text{{C}}")
else:
    # condutor
    if a == 0:
        if r_g < b:
            st.write("Como toda a carga está na superfície externa da esfera condutora:")
            st.latex(r"Q = 0")
        else:
            st.write("Como a superfície gaussiana está fora da esfera, toda a carga do condutor é envolvida:")
            st.latex(rf"Q = q_2 = {q2:.6e}\ \text{{C}}")
    else:
        if r_g < a:
            st.write("Como a superfície gaussiana está na cavidade, a carga contida é apenas a partícula:")
            st.latex(rf"Q = q_1 = {q1:.6e}\ \text{{C}}")
        elif r_g < b:
            st.write("Como a superfície gaussiana está dentro da espessura da casca esférica condutora:")
            st.latex(r"Q = q_1 + q_{2i}")
            st.latex(rf"Q = {q1:.6e} + ({qint:.6e}) = {(q1 + qint):.6e}\ \text{{C}}")
            st.latex(r"Q = 0")
        else:
            st.write("Como a superfície gaussiana está fora da esfera, ela envolve a carga total:")
            st.latex(rf"Q = q_1 + q_2 = {q1:.6e} + {q2:.6e} = {(q1 + q2):.6e}\ \text{{C}}")

st.markdown("---")

# ============================================================
# ÁREA DA SUPERFÍCIE GAUSSIANA
# ============================================================
st.header("Área da superfície gaussiana")

st.latex(r"A = 4\pi r^2")
st.latex(rf"A = 4\pi ({r_g:.4f})^2 = {A:.6f}\ \text{{m}}^2")

st.markdown("---")

# ============================================================
# CAMPO ELÉTRICO
# ============================================================
st.header("Campo elétrico")

st.write("Lei de Gauss no caso de simetria: campo constante em toda a superfície gaussiana e sempre paralelo ao vetor área.")
st.latex(r"EA = \frac{Q}{\varepsilon_0}")
st.latex(r"E = \frac{Q}{A\varepsilon_0}")
st.latex(rf"E = \frac{{{Q:.6e}}}{{({A:.6e})({EPS0:.6e})}} = {E:.6e}\ \text{{N/C}}")

if np.isfinite(E):
    if E > 0:
        st.success("Sinal de E positivo: campo radial para fora.")
    elif E < 0:
        st.info("Sinal de E negativo: campo radial para dentro.")
    else:
        st.warning("Campo elétrico nulo neste raio.")
else:
    st.warning("No ponto r = 0 o campo elétrico não é definido.")

st.markdown("---")

# ============================================================
# GRÁFICO
# ============================================================
st.header("Gráfico")
st.write("Para melhorar a visualização do eixo vertical, o gráfico usa escala simétrica logarítmica no eixo y.")

rs, Es = gerar_curva_E(a, b, q1, q2, condutor, r_g)

fig2, ax2 = plt.subplots(figsize=(10, 5.6))
fig2.patch.set_facecolor("white")
ax2.set_facecolor("white")

ax2.plot(rs, Es, color="#0f62fe", lw=2.2, label="E(r)")
ax2.axhline(0, color="black", lw=1)
ax2.axvline(b, color="gray", linestyle="--", lw=1.2, label="b")
if a > 0:
    ax2.axvline(a, color="gray", linestyle=":", lw=1.2, label="a")
ax2.axvline(r_g, color="green", linestyle="--", lw=1.5, label="r selecionado")

ax2.set_xlabel("Distância radial r (m)")
ax2.set_ylabel("Campo elétrico E (N/C)")
ax2.set_title("Campo elétrico em função da distância radial")
ax2.grid(True, alpha=0.25, which="both")

valid = Es[np.isfinite(Es)]
if len(valid) > 0:
    positivos = np.abs(valid[valid != 0])
    if len(positivos) > 0:
        linthresh = max(np.percentile(positivos, 15), 1e-3)
        ax2.set_yscale("symlog", linthresh=linthresh)

ax2.legend(loc="best")
st.pyplot(fig2, use_container_width=True)
