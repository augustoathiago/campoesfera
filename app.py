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

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================
def cor_carga(q):
    """Retorna cor conforme sinal da carga."""
    if q > 1e-15:
        return "red"
    elif q < -1e-15:
        return "blue"
    return "black"

def sinal_texto(q):
    if q > 1e-15:
        return "+"
    elif q < -1e-15:
        return "-"
    return "0"

def fmt_num(x, casas=4):
    """Formatação numérica em português."""
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
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight", facecolor="white")
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
            qint = -q1
            qext = q2 - qint  # q2 = qint + qext
        else:
            qint = 0.0
            qext = q2
    else:
        # Em isolante a carga é volumétrica (não superficial)
        qint = 0.0
        qext = 0.0
    return qint, qext

def Q_enc(r, a, b, q1, q2, condutor):
    """
    Carga total contida na superfície gaussiana de raio r (em C).
    """
    if r <= 0:
        return 0.0

    if condutor:
        if a == 0:
            # esfera maciça condutora
            if r < b:
                return 0.0
            return q2
        else:
            # casca condutora com possível carga central
            qint, _ = carga_superficies(condutor, a, q1, q2)
            if r < a:
                return q1
            elif r < b:
                return q1 + qint  # deve dar zero
            else:
                return q1 + q2
    else:
        # isolante
        if a == 0:
            # esfera maciça isolante com carga homogênea em volume
            if r < b:
                return q2 * (r**3) / (b**3)
            return q2
        else:
            # casca esférica isolante com carga homogênea no volume da casca
            if r < a:
                return q1
            elif r < b:
                frac = (r**3 - a**3) / (b**3 - a**3)
                return q1 + q2 * frac
            else:
                return q1 + q2

def E_no_raio(r, a, b, q1, q2, condutor):
    """
    Campo elétrico no raio r (magnitude com sinal radial):
      positivo -> para fora
      negativo -> para dentro
    """
    if r <= 0:
        return np.nan
    Q = Q_enc(r, a, b, q1, q2, condutor)
    return K * Q / (r**2)

def gerar_curva_E(a, b, q1, q2, condutor, n=900):
    """
    Gera pontos para gráfico E(r).
    """
    r_min = 1e-4
    r_max = max(2.2 * b, b + 0.5)
    rs = np.linspace(r_min, r_max, n)
    Es = np.array([E_no_raio(r, a, b, q1, q2, condutor) for r in rs])

    # Evitar explosões visuais perto de singularidade
    finitos = Es[np.isfinite(Es)]
    if len(finitos) > 0:
        p99 = np.percentile(np.abs(finitos), 99)
        if p99 > 0:
            Es = np.clip(Es, -1.2 * p99, 1.2 * p99)

    return rs, Es

def desenhar_sistema(a, b, r_g, q1, q2, condutor):
    """
    Desenha esfera/casca, partícula, superfícies, cotas, superfície gaussiana,
    vetor campo e box com valores.
    """
    qint, qext = carga_superficies(condutor, a, q1, q2)
    E_r = E_no_raio(r_g, a, b, q1, q2, condutor)

    # Geometria normalizada pelo raio externo b
    R_out = 1.0
    R_in = a / b if b > 0 else 0.0
    Rg = r_g / b if b > 0 else 0.0

    cor_part = cor_carga(q1)
    cor_mat = cor_carga(q2)
    cor_int = cor_carga(qint if condutor else q2)
    cor_ext = cor_carga(qext if condutor else q2)

    # Limites com margem para não cortar nada
    x_left = -2.2
    x_right = max(2.8, Rg + 1.6)
    y_lim = max(1.7, Rg + 0.7)

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_aspect("equal")
    ax.set_xlim(x_left, x_right)
    ax.set_ylim(-y_lim, y_lim)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # -------- Material da esfera/casca --------
    if not condutor:
        if a == 0:
            # esfera maciça isolante
            esfera = Circle((0, 0), R_out, facecolor=cor_mat, edgecolor=cor_ext, alpha=0.15, linewidth=2.5)
            ax.add_patch(esfera)
            cont_externa = Circle((0, 0), R_out, fill=False, edgecolor=cor_ext, linewidth=3)
            ax.add_patch(cont_externa)
        else:
            # casca isolante
            ext_fill = Circle((0, 0), R_out, facecolor=cor_mat, edgecolor="none", alpha=0.15)
            int_hole = Circle((0, 0), R_in, facecolor="white", edgecolor="none")
            ax.add_patch(ext_fill)
            ax.add_patch(int_hole)

            cont_interna = Circle((0, 0), R_in, fill=False, edgecolor=cor_int, linewidth=3)
            cont_externa = Circle((0, 0), R_out, fill=False, edgecolor=cor_ext, linewidth=3)
            ax.add_patch(cont_interna)
            ax.add_patch(cont_externa)
    else:
        # condutor
        if a == 0:
            esfera = Circle((0, 0), R_out, facecolor="#d9d9d9", edgecolor=cor_ext, alpha=0.35, linewidth=3)
            ax.add_patch(esfera)
        else:
            ext_fill = Circle((0, 0), R_out, facecolor="#d9d9d9", edgecolor="none", alpha=0.35)
            int_hole = Circle((0, 0), R_in, facecolor="white", edgecolor="none")
            ax.add_patch(ext_fill)
            ax.add_patch(int_hole)

            cont_interna = Circle((0, 0), R_in, fill=False, edgecolor=cor_int, linewidth=3)
            cont_externa = Circle((0, 0), R_out, fill=False, edgecolor=cor_ext, linewidth=3)
            ax.add_patch(cont_interna)
            ax.add_patch(cont_externa)

    # -------- Superfície gaussiana --------
    if Rg > 0:
        gauss = Circle((0, 0), Rg, fill=False, edgecolor="green", linestyle="--", linewidth=2.5)
        ax.add_patch(gauss)

    # -------- Partícula central --------
    if a > 0 and abs(q1) > 1e-18:
        part = Circle((0, 0), 0.06, facecolor=cor_part, edgecolor="black", linewidth=0.8)
        ax.add_patch(part)
        ax.text(0.12, 0.12, "q", fontsize=12, color=cor_part, weight="bold")

    # -------- Cotas verticais --------
    # cota do raio externo b
    x_dim_b = -1.55
    ax.annotate("", xy=(x_dim_b, -R_out), xytext=(x_dim_b, R_out),
                arrowprops=dict(arrowstyle="<->", lw=1.8, color="black"))
    ax.plot([x_dim_b + 0.08, -R_out], [R_out, R_out], color="black", lw=1)
    ax.plot([x_dim_b + 0.08, -R_out], [-R_out, -R_out], color="black", lw=1)
    ax.text(x_dim_b - 0.18, 0, f"b = {fmt_num(b, 3)} m", rotation=90,
            va="center", ha="center", fontsize=11)

    # cota do raio interno a
    if a > 0:
        x_dim_a = -1.90
        ax.annotate("", xy=(x_dim_a, -R_in), xytext=(x_dim_a, R_in),
                    arrowprops=dict(arrowstyle="<->", lw=1.6, color="black"))
        ax.plot([x_dim_a + 0.08, -R_in], [R_in, R_in], color="black", lw=1)
        ax.plot([x_dim_a + 0.08, -R_in], [-R_in, -R_in], color="black", lw=1)
        ax.text(x_dim_a - 0.18, 0, f"a = {fmt_num(a, 3)} m", rotation=90,
                va="center", ha="center", fontsize=11)

    # -------- Vetor do campo na superfície gaussiana (ponto mais à direita) --------
    if Rg > 0:
        x0, y0 = Rg, 0
        comprimento = 0.55
        if np.isfinite(E_r):
            if E_r >= 0:
                x1 = x0 + comprimento
            else:
                x1 = x0 - comprimento
            seta = FancyArrowPatch((x0, y0), (x1, y0), arrowstyle="->",
                                   mutation_scale=18, lw=2.2, color="purple")
            ax.add_patch(seta)
            ax.text((x0 + x1)/2, 0.12, "E", color="purple", fontsize=12, weight="bold", ha="center")

        # box do valor do campo
        box_x = max(1.45, Rg + 0.2)
        box_y = 0.95
        ax.text(box_x, box_y,
                f"Campo elétrico\nE(r) = {fmt_num(E_r, 4)} N/C",
                fontsize=11,
                ha="left", va="top",
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#f7f7f7", edgecolor="gray"))

    # -------- Box com q, qint, qext --------
    q_text_x = 1.35
    q_text_y = -0.10
    ax.text(q_text_x, q_text_y + 0.50, "Cargas", fontsize=12, weight="bold",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="gray"))
    ax.text(q_text_x, q_text_y + 0.28, f"q = {fmt_num(q1 * 1e6, 4)} μC", color=cor_part, fontsize=11)
    ax.text(q_text_x, q_text_y + 0.08, f"qint = {fmt_num(qint * 1e6, 4)} μC", color=cor_carga(qint), fontsize=11)
    ax.text(q_text_x, q_text_y - 0.12, f"qext = {fmt_num(qext * 1e6, 4)} μC", color=cor_carga(qext), fontsize=11)

    # -------- Legendas discretas --------
    ax.text(-0.15, -1.35, "Superfície gaussiana (verde tracejado)", color="green", fontsize=10)
    ax.text(-0.15, -1.52, "Vetor do campo elétrico (roxo)", color="purple", fontsize=10)

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
                            border:1px solid #ccc; border-radius:10px; background:#fafafa;">
                    <span style="color:#666;">logo_maua.png</span>
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
            <img src="data:image/png;base64,{img_b64}" style="max-width:none; width:1100px; display:block; margin:auto;" />
        </div>
        """,
        unsafe_allow_html=True
    )

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
    a = st.slider("Raio interno a da esfera (m)", min_value=0.0, max_value=5.0, value=1.0, step=0.05)
    b_min = max(a + 0.05, 0.05)
    b_default = max(b_min, 2.0)
    b = st.slider("Raio externo b da esfera (m)", min_value=float(b_min), max_value=6.0, value=float(min(b_default, 6.0)), step=0.05)

    q1_micro = st.slider(
        "Carga da partícula q1 (μC)",
        min_value=-20.0,
        max_value=20.0,
        value=5.0 if a > 0 else 0.0,
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
        step=0.01,
    )

    st.markdown(
        """
        <div style="padding:14px; border:2px solid #0f62fe; border-radius:12px; background:#f8fbff;">
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
A = 4 * np.pi * (r_g**2)
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
st.markdown(
    f"""
- \(\phi\) é o **fluxo elétrico** na superfície gaussiana;  
- \(E\) é o **campo elétrico**;  
- \(A\) é a **área** da superfície gaussiana;  
- \(Q\) é a **carga contida** na superfície gaussiana;  
- \(\varepsilon_0\) é a **permissividade do vácuo**, adotada no simulador como  
  \(\varepsilon_0 = {fmt_num(EPS0, 4)} \\, C^2/(N\\cdot m^2)\).
"""
)

st.markdown("---")

# ============================================================
# CARGA NA ESFERA
# ============================================================
st.header("Carga na esfera")

if not condutor:
    st.markdown(f"**Carga distribuída homogeneamente por ser material isolante:**  \n**q₂ = {fmt_coulomb(q2)}**")
else:
    if a == 0 or abs(q1) < 1e-18:
        st.markdown(f"**Carga toda na superfície externa por ser material condutor:**  \n**q₂ = {fmt_coulomb(q2)}**")
    else:
        st.markdown(
            f"""
A partícula no centro induz carga na superfície interna da casca condutora:  
\[
q_{{2i}} = -q_1 = -({fmt_coulomb(q1)}) = {fmt_coulomb(qint)}
\]

Como a carga total da casca é \(q_2\), então:
\[
q_2 = q_{{2i}} + q_{{2e}}
\]

Logo:
\[
q_{{2e}} = q_2 - q_{{2i}}
\]

Substituindo os valores:
\[
q_{{2e}} = {fmt_coulomb(q2)} - ({fmt_coulomb(qint)}) = {fmt_coulomb(qext)}
\]
"""
        )

st.markdown("---")

# ============================================================
# CARGA Q CONTIDA NA SUPERFÍCIE GAUSSIANA
# ============================================================
st.header("Carga Q contida na superfície gaussiana")

if not condutor:
    if a == 0:
        # esfera maciça isolante
        if r_g < b:
            rho = q2 / ((4/3) * np.pi * b**3)
            Q_calc = q2 * (r_g**3) / (b**3)

            st.markdown(
                f"""
Como a esfera é **maciça isolante**, a carga está distribuída uniformemente no volume.

\[
\\rho = \\frac{{q_2}}{{V_{{total}}}} = \\frac{{Q}}{{V_r}}
\]

onde \(\\rho\) é a densidade de carga volumétrica e \(V\) é o volume.

\[
\\frac{{q_2}}{{\\frac{{4}}{{3}}\\pi b^3}} = \\frac{{Q}}{{\\frac{{4}}{{3}}\\pi r^3}}
\]

\[
Q = q_2 \\frac{{r^3}}{{b^3}}
\]

Substituindo os valores:
\[
Q = ({fmt_coulomb(q2)})\\frac{{({fmt_num(r_g,4)})^3}}{{({fmt_num(b,4)})^3}} = {fmt_coulomb(Q_calc)}
\]
"""
            )
        else:
            st.markdown(f"Como a superfície gaussiana está **fora da esfera**, toda a carga é envolvida:  \n\[
Q = q_2 = {fmt_coulomb(q2)}
\]")
    else:
        # casca isolante
        if r_g < a:
            st.markdown(f"Como a superfície gaussiana está **na cavidade**, a carga contida é apenas a partícula central:  \n\[
Q = q_1 = {fmt_coulomb(q1)}
\]")
        elif r_g < b:
            rho = q2 / ((4/3) * np.pi * (b**3 - a**3))
            Q_shell = q2 * ((r_g**3 - a**3) / (b**3 - a**3))
            Q_total = q1 + Q_shell

            st.markdown(
                f"""
Como a superfície gaussiana está **dentro da espessura da casca esférica isolante**, usa-se densidade volumétrica uniforme:

\[
\\rho = \\frac{{q_2}}{{V_{{total}}}} = \\frac{{Q_{{casca}}}}{{V_r}}
\]

com

\[
\\frac{{q_2}}{{\\frac{{4}}{{3}}\\pi (b^3-a^3)}} = \\frac{{Q_{{casca}}}}{{\\frac{{4}}{{3}}\\pi (r^3-a^3)}}
\]

Portanto, a carga da parte da casca contida até o raio \(r\) é:

\[
Q_{{casca}} = q_2\\frac{{r^3-a^3}}{{b^3-a^3}}
\]

Substituindo os valores:
\[
Q_{{casca}} = ({fmt_coulomb(q2)})\\frac{{({fmt_num(r_g,4)})^3-({fmt_num(a,4)})^3}}{{({fmt_num(b,4)})^3-({fmt_num(a,4)})^3}} = {fmt_coulomb(Q_shell)}
\]

Como existe a partícula central, a carga total contida é:

\[
Q = q_1 + Q_{{casca}} = {fmt_coulomb(q1)} + {fmt_coulomb(Q_shell)} = {fmt_coulomb(Q_total)}
\]
"""
            )
        else:
            st.markdown(
                f"""
Como a superfície gaussiana está **fora da esfera**, toda a carga é envolvida:

\[
Q = q_1 + q_2 = {fmt_coulomb(q1)} + {fmt_coulomb(q2)} = {fmt_coulomb(q1 + q2)}
\]
"""
            )
else:
    # condutor
    if a == 0:
        if r_g < b:
            st.markdown(
                f"""
Como a esfera é **maciça condutora**, toda a carga fica na superfície externa.

\[
Q = 0
\]
"""
            )
        else:
            st.markdown(
                f"""
Como a superfície gaussiana está **fora da esfera**, toda a carga total do condutor é envolvida:

\[
Q = q_2 = {fmt_coulomb(q2)}
\]
"""
            )
    else:
        if r_g < a:
            st.markdown(
                f"""
Como a superfície gaussiana está **na cavidade**, a carga contida é apenas a partícula:

\[
Q = q_1 = {fmt_coulomb(q1)}
\]
"""
            )
        elif r_g < b:
            st.markdown(
                f"""
Como a superfície gaussiana está **dentro da espessura da casca esférica condutora**:

\[
Q = q_1 + q_{{2i}}
\]

Como

\[
q_{{2i}} = {fmt_coulomb(qint)}
\]

então

\[
Q = {fmt_coulomb(q1)} + {fmt_coulomb(qint)} = {fmt_coulomb(q1 + qint)}
\]

Logo,

\[
Q = 0
\]
"""
            )
        else:
            st.markdown(
                f"""
Como a superfície gaussiana está **fora da casca condutora**, ela envolve a carga total:

\[
Q = q_1 + q_2 = {fmt_coulomb(q1)} + {fmt_coulomb(q2)} = {fmt_coulomb(q1 + q2)}
\]
"""
            )

st.markdown("---")

# ============================================================
# ÁREA DA SUPERFÍCIE GAUSSIANA
# ============================================================
st.header("Área da superfície gaussiana")

st.latex(r"A = 4\pi r^2")
st.latex(
    rf"A = 4\pi ({r_g:.4f})^2 = {A:.6f}\ \text{{m}}^2"
)

st.markdown("---")

# ============================================================
# CAMPO ELÉTRICO
# ============================================================
st.header("Campo elétrico")

st.markdown(
    """
Lei de Gauss no caso de simetria esférica: o campo elétrico tem o mesmo módulo em toda a superfície gaussiana e é sempre paralelo ao vetor área.
"""
)

st.latex(r"EA = \frac{Q}{\varepsilon_0}")
st.latex(r"E = \frac{Q}{A\varepsilon_0}")

st.latex(
    rf"E = \frac{{{Q:.6e}}}{{({A:.6e})({EPS0:.6e})}} = {E:.6e}\ \text{{N/C}}"
)

if np.isfinite(E):
    if E > 0:
        st.success("Sinal de E positivo: campo radial para fora.")
    elif E < 0:
        st.info("Sinal de E negativo: campo radial para dentro.")
    else:
        st.warning("Campo elétrico nulo neste raio.")
else:
    st.warning("No ponto r = 0 o campo de uma carga puntiforme não é definido.")

st.markdown("---")

# ============================================================
# GRÁFICO
# ============================================================
st.header("Gráfico")

rs, Es = gerar_curva_E(a, b, q1, q2, condutor)

fig2, ax2 = plt.subplots(figsize=(10, 5.5))
fig2.patch.set_facecolor("white")
ax2.set_facecolor("white")

ax2.plot(rs, Es, color="#0f62fe", lw=2.2, label="E(r)")
ax2.axhline(0, color="black", lw=1)

# Marcas características
ax2.axvline(b, color="gray", linestyle="--", lw=1.2, label="b")
if a > 0:
    ax2.axvline(a, color="gray", linestyle=":", lw=1.2, label="a")
ax2.axvline(r_g, color="green", linestyle="--", lw=1.5, label="r selecionado")

ax2.set_xlabel("Distância radial r (m)")
ax2.set_ylabel("Campo elétrico E (N/C)")
ax2.set_title("Campo elétrico em função da distância radial")
ax2.grid(True, alpha=0.25)

# Ajuste automático de eixo y
valid = Es[np.isfinite(Es)]
if len(valid) > 0:
    ymin = np.min(valid)
    ymax = np.max(valid)
    if abs(ymax - ymin) < 1e-12:
        margem = max(1.0, abs(ymax) * 0.2 + 1)
        ax2.set_ylim(ymin - margem, ymax + margem)
    else:
        margem = 0.1 * (ymax - ymin)
        ax2.set_ylim(ymin - margem, ymax + margem)

ax2.legend(loc="best")
st.pyplot(fig2, use_container_width=True)

st.markdown("---")

# ============================================================
# RESUMO NUMÉRICO
# ============================================================
st.header("Resumo numérico")

c1, c2, c3, c4 = st.columns(4)
c1.metric("q", f"{fmt_num(q1_micro, 3)} μC")
c2.metric("qint", f"{fmt_num(qint * 1e6, 3)} μC")
c3.metric("qext", f"{fmt_num(qext * 1e6, 3)} μC")
c4.metric("E(r)", f"{fmt_num(E, 4)} N/C")

st.caption("Dica: para incorporar este app no Canvas LMS, hospede primeiro no Streamlit Community Cloud e depois use um iframe no Editor HTML do Canvas.")
