import numpy as np
import streamlit as st
import plotly.graph_objects as go

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Calculadora Acústica",
    page_icon="🔊",
    layout="wide",
)

st.title("🔊 Calculadora Acústica de Recintos")
st.caption("Tiempos de reverberación · Campo sonoro · Distancia crítica")

# ── Constantes ───────────────────────────────────────────────────────────────
c      = 343.0
I0     = 1e-12
FREQS  = np.array([125, 250, 500, 1000, 2000, 4000])
FREQ_LABELS = [f"{f} Hz" for f in FREQS]

MATERIALES = {
    "concreto":  [0.01, 0.01, 0.02, 0.02, 0.03, 0.04],
    "drywall":   [0.05, 0.05, 0.05, 0.04, 0.07, 0.09],
    "ladrillo":  [0.01, 0.01, 0.02, 0.02, 0.03, 0.04],
    "vidrio":    [0.28, 0.22, 0.15, 0.12, 0.08, 0.06],
    "madera":    [0.15, 0.11, 0.10, 0.07, 0.06, 0.07],
    "aluminio":  [0.01, 0.01, 0.02, 0.02, 0.02, 0.02],
    "baldosa":   [0.01, 0.01, 0.02, 0.02, 0.03, 0.04],
}

# ── Sidebar: parámetros de entrada ──────────────────────────────────────────
with st.sidebar:
    st.header("Dimensiones del recinto")
    largo = st.number_input("Largo (m)", min_value=1.0, value=10.0, step=0.5)
    ancho = st.number_input("Ancho (m)", min_value=1.0, value=8.0,  step=0.5)
    alto  = st.number_input("Altura (m)", min_value=1.0, value=3.0, step=0.1)

    st.divider()
    st.header("Materiales")
    piso  = st.selectbox("Piso",  list(MATERIALES.keys()), index=4)
    techo = st.selectbox("Techo", list(MATERIALES.keys()), index=0)

    st.divider()
    st.header("Paredes")
    n_paredes = st.number_input("Número de materiales en paredes", min_value=1, max_value=6, value=2, step=1)

    paredes = []
    for i in range(int(n_paredes)):
        with st.expander(f"Material de pared {i+1}", expanded=True):
            mat  = st.selectbox("Material", list(MATERIALES.keys()), key=f"mat_{i}")
            area = st.number_input("Área (m²)", min_value=0.1, value=30.0, step=1.0, key=f"area_{i}")
            paredes.append((mat, area))

    st.divider()
    st.header("Fuente sonora")
    Lw = st.slider("Nivel de potencia sonora Lw (dB)", 50, 150, 90)
    r  = st.slider("Distancia fuente–receptor r (m)", 0.5, 20.0, 2.0, step=0.5)
    Q  = st.selectbox("Factor de directividad Q", [1, 2, 4], index=1,
                      format_func=lambda x: {1:"1 — esfera completa", 2:"2 — semiesfera", 4:"4 — cuarto de esfera"}[x])

# ── Cálculos ─────────────────────────────────────────────────────────────────
V        = largo * ancho * alto
S_piso   = largo * ancho
S_techo  = S_piso
S_pared  = 2*(largo*alto) + 2*(ancho*alto)
S_total  = 2*S_piso + S_pared
l        = 4*V / S_total
tau      = l / c
W        = 10**((Lw - 120) / 10)
If_      = W / (4 * np.pi * r**2)
LI       = 10 * np.log10(If_ / I0)

alpha_piso  = np.array(MATERIALES[piso])
alpha_techo = np.array(MATERIALES[techo])

RT_sabine    = np.zeros(6)
RT_eyring    = np.zeros(6)
RT_millington= np.zeros(6)
n_reflex     = np.zeros(6)
Lp_arr       = np.zeros(6)
Dc_arr       = np.zeros(6)
R_arr        = np.zeros(6)

for i in range(6):
    A_pared = sum(area * MATERIALES[mat][i] for mat, area in paredes)
    A       = S_piso*alpha_piso[i] + S_techo*alpha_techo[i] + A_pared
    ap      = min(A / S_total, 0.9999)

    RT_sabine[i]     = 0.161 * V / A
    RT_eyring[i]     = 0.161 * V / (-S_total * np.log(1 - ap))
    lp_sum = (S_piso  * np.log(1 - min(alpha_piso[i],  0.9999)) +
              S_techo * np.log(1 - min(alpha_techo[i], 0.9999)) +
              (A_pared * np.log(1 - ap) / ap if ap > 0 else 0))
    RT_millington[i] = 0.161 * V / (-lp_sum)

    R         = A / (1 - ap)
    R_arr[i]  = R
    Lp_arr[i] = Lw + 10*np.log10(Q/(4*np.pi*r**2) + 4/R)
    Dc_arr[i] = 0.057 * np.sqrt(Q * R)
    n_reflex[i] = c * RT_sabine[i] / l

# ── Métricas generales ───────────────────────────────────────────────────────
st.subheader("Datos generales del recinto")
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Volumen",          f"{V:.1f} m³")
c2.metric("Superficie total", f"{S_total:.1f} m²")
c3.metric("Rec. libre medio", f"{l:.2f} m")
c4.metric("RT Sabine prom.",  f"{RT_sabine.mean():.2f} s")
c5.metric("Lp campo total",   f"{Lp_arr.mean():.1f} dB")
c6.metric("Distancia crítica",f"{Dc_arr.mean():.2f} m")

st.divider()

# ── Gráfica RT ───────────────────────────────────────────────────────────────
st.subheader("Tiempo de reverberación vs frecuencia")

fig = go.Figure()
fig.add_trace(go.Scatter(x=FREQ_LABELS, y=RT_sabine,    mode="lines+markers", name="Sabine",
                         line=dict(color="#378ADD", width=2), marker=dict(size=7)))
fig.add_trace(go.Scatter(x=FREQ_LABELS, y=RT_eyring,    mode="lines+markers", name="Eyring",
                         line=dict(color="#1D9E75", width=2), marker=dict(size=7)))
fig.add_trace(go.Scatter(x=FREQ_LABELS, y=RT_millington,mode="lines+markers", name="Millington",
                         line=dict(color="#D85A30", width=2), marker=dict(size=7)))
fig.update_layout(
    xaxis_title="Frecuencia (Hz)",
    yaxis_title="RT (s)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=380,
    margin=dict(l=0, r=0, t=10, b=0),
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Tabla de resultados ───────────────────────────────────────────────────────
st.subheader("Resultados por banda de frecuencia")

import pandas as pd

df = pd.DataFrame({
    "Frecuencia":        FREQ_LABELS,
    "RT Sabine (s)":     np.round(RT_sabine,    3),
    "RT Eyring (s)":     np.round(RT_eyring,    3),
    "RT Millington (s)": np.round(RT_millington,3),
    "Reflexiones":       np.round(n_reflex,     1),
    "Lp (dB)":           np.round(Lp_arr,       1),
    "Distancia crítica (m)": np.round(Dc_arr,   2),
})
st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()

# ── Detalles físicos ──────────────────────────────────────────────────────────
with st.expander("Ver detalles físicos adicionales"):
    d1, d2, d3 = st.columns(3)
    d1.metric("Tiempo entre reflexiones τ", f"{tau*1000:.2f} ms")
    d2.metric("Intensidad directa If",       f"{If_:.2e} W/m²")
    d3.metric("Nivel de intensidad LI",      f"{LI:.1f} dB")

# ── Instrucciones de despliegue ───────────────────────────────────────────────
with st.expander("📦 Cómo desplegar en Streamlit Cloud"):
    st.markdown("""
1. Sube `app.py` a un repositorio de GitHub.
2. Crea un archivo `requirements.txt` con:
   ```
   streamlit
   numpy
   plotly
   pandas
   ```
3. Ve a [share.streamlit.io](https://share.streamlit.io) → **New app**
4. Conecta tu repo y selecciona `app.py`.
5. Clic en **Deploy** — en minutos tendrás una URL pública.
""")