"""
CivicFlow MTY - Prototipo web (Streamlit)
==========================================

Versión con interfaz gráfica que corre en el navegador, ideal para GitHub
Codespaces o cualquier entorno sin pantalla gráfica (donde Tkinter no
funciona porque no hay $DISPLAY). Cualquier persona con el repositorio
puede levantarla con un solo comando.

Instalación (una sola vez):
    pip install -r requirements.txt

Ejecución:
    streamlit run streamlit_app.py

En GitHub Codespaces, al ejecutar el comando anterior aparecerá una
notificación para abrir el puerto reenviado (normalmente 8501) en el
navegador — solo da clic en "Open in Browser".
"""

import json
import os
from datetime import datetime

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Configuración y persistencia (mismo formato que las versiones de terminal/GUI)
# ---------------------------------------------------------------------------

DATA_FILE = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "reportes.json")

CATEGORIAS = [
    "Alumbrado público",
    "Baches y pavimentación",
    "Mantenimiento de parques",
    "Otro",
]

ESTATUS_FLUJO = ["Nuevo", "En Proceso", "Canalizado", "Atendido"]

ESTATUS_COLOR = {
    "Nuevo": "#f5c518",
    "En Proceso": "#2e86de",
    "Canalizado": "#e67e22",
    "Atendido": "#27ae60",
}

COLOR_HEADER = "#3d5a80"
COLOR_ACENTO = "#2e86de"


def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"ultimo_folio": 1000, "reportes": []}


def guardar_datos(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def ahora():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def buscar_reporte(data, folio_buscado):
    folio_buscado = folio_buscado.strip().upper().replace("#", "")
    if not folio_buscado.startswith("MTY-"):
        folio_buscado = f"MTY-{folio_buscado}"
    for r in data["reportes"]:
        if r["folio"] == folio_buscado:
            return r
    return None


# ---------------------------------------------------------------------------
# Configuración de la página y estilos
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="CivicFlow MTY",
    page_icon="🏛️",
    layout="centered",
)

st.markdown(
    f"""
    <style>
    .civicflow-header {{
        background-color: {COLOR_HEADER};
        color: white;
        padding: 20px 28px;
        border-radius: 10px;
        margin-bottom: 24px;
    }}
    .civicflow-header h1 {{
        margin: 0;
        font-size: 1.6rem;
    }}
    .civicflow-header p {{
        margin: 4px 0 0 0;
        color: #d6e4f0;
        font-size: 0.9rem;
    }}
    .badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 14px;
        color: white;
        font-weight: 600;
        font-size: 0.85rem;
    }}
    .stButton>button {{
        background-color: {COLOR_ACENTO};
        color: white;
        border-radius: 6px;
        border: none;
        font-weight: 600;
    }}
    </style>
    <div class="civicflow-header">
        <h1>🏛️ CivicFlow MTY</h1>
        <p>Registro y seguimiento de problemáticas — 7ma Regiduría del Cabildo de Monterrey</p>
    </div>
    """,
    unsafe_allow_html=True,
)

data = cargar_datos()

tab_reportar, tab_consultar, tab_panel = st.tabs(
    ["📝 Reportar problemática", "🔍 Consultar folio", "📊 Panel de administración"]
)

# ---------------------------------------------------------------------------
# Tab 1: Reportar problemática
# ---------------------------------------------------------------------------

with tab_reportar:
    st.subheader("¿Qué problema deseas reportar?")

    col_izq, col_centro, col_der = st.columns([1, 2, 1])
    with col_centro:
        with st.form("form_reporte", clear_on_submit=True):
            categoria = st.selectbox("Categoría", CATEGORIAS)
            descripcion = st.text_area("Descripción del problema", height=100)
            ubicacion = st.text_input(
                "Ubicación (colonia / calle / referencia)")
            foto = st.file_uploader(
                "Foto de evidencia (opcional)", type=["png", "jpg", "jpeg"]
            )
            anonimo = st.checkbox("Enviar como reporte anónimo")
            contacto = ""
            if not anonimo:
                contacto = st.text_input("Contacto (teléfono o nombre)")

            enviado = st.form_submit_button("Enviar reporte")

            if enviado:
                if not descripcion.strip() or not ubicacion.strip():
                    st.warning(
                        "Por favor describe el problema e indica la ubicación.")
                else:
                    data["ultimo_folio"] += 1
                    folio = f"MTY-{data['ultimo_folio']}"
                    reporte = {
                        "folio": folio,
                        "categoria": categoria,
                        "descripcion": descripcion.strip(),
                        "ubicacion": ubicacion.strip(),
                        "foto": foto.name if foto else None,
                        "anonimo": anonimo,
                        "contacto": contacto.strip() or None,
                        "estatus": ESTATUS_FLUJO[0],
                        "historial": [{"estatus": ESTATUS_FLUJO[0], "fecha": ahora()}],
                        "fecha_registro": ahora(),
                    }
                    data["reportes"].append(reporte)
                    guardar_datos(data)
                    st.success(
                        f"¡Gracias! Tu reporte fue registrado con el folio **#{folio}**. "
                        "Te mantendremos informado sobre el cambio de estatus."
                    )

# ---------------------------------------------------------------------------
# Tab 2: Consultar folio
# ---------------------------------------------------------------------------

with tab_consultar:
    st.subheader("Consulta el avance de tu reporte")

    col_izq, col_centro, col_der = st.columns([1, 2, 1])
    with col_centro:
        folio_input = st.text_input("Folio (ej. MTY-1001 o 1001)")
        buscar = st.button("Buscar")

        if buscar and folio_input.strip():
            reporte = buscar_reporte(data, folio_input)
            if not reporte:
                st.error(
                    f"No se encontró ningún reporte con folio '{folio_input}'.")
            else:
                color = ESTATUS_COLOR.get(reporte["estatus"], "#999999")
                st.markdown(f"### Folio #{reporte['folio']}")
                st.markdown(
                    f'<span class="badge" style="background-color:{color}">'
                    f'{reporte["estatus"]}</span>',
                    unsafe_allow_html=True,
                )
                st.write(f"**Categoría:** {reporte['categoria']}")
                st.write(f"**Descripción:** {reporte['descripcion']}")
                st.write(f"**Ubicación:** {reporte['ubicacion']}")
                st.write(
                    f"**Anónimo:** {'Sí' if reporte['anonimo'] else 'No'}")
                st.write(f"**Registrado:** {reporte['fecha_registro']}")

                st.markdown("**Historial de avance:**")
                for paso in reporte["historial"]:
                    st.write(f"- {paso['fecha']} → {paso['estatus']}")

# ---------------------------------------------------------------------------
# Tab 3: Panel de administración
# ---------------------------------------------------------------------------

with tab_panel:
    st.subheader("Panel de administración")

    reportes = data["reportes"]

    if not reportes:
        st.info("Aún no hay reportes registrados.")
    else:
        conteo = {est: 0 for est in ESTATUS_FLUJO}
        for r in reportes:
            conteo[r["estatus"]] = conteo.get(r["estatus"], 0) + 1

        cols = st.columns(len(ESTATUS_FLUJO))
        for col, est in zip(cols, ESTATUS_FLUJO):
            with col:
                st.markdown(
                    f"""
                    <div style="background-color:{ESTATUS_COLOR[est]};
                                border-radius:10px; padding:14px; text-align:center; color:white;">
                        <div style="font-size:1.6rem; font-weight:700;">{conteo[est]}</div>
                        <div style="font-size:0.85rem;">{est}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("### Reportes")
        df = pd.DataFrame(
            [
                {
                    "Folio": f"#{r['folio']}",
                    "Categoría": r["categoria"],
                    "Ubicación": r["ubicacion"],
                    "Fecha": r["fecha_registro"],
                    "Estatus": r["estatus"],
                }
                for r in reportes
            ]
        )

        def resaltar_estatus(val):
            color = ESTATUS_COLOR.get(val, "#ffffff")
            return f"background-color: {color}22"

        st.dataframe(
            df.style.applymap(resaltar_estatus, subset=["Estatus"]),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### Actualizar estatus")
        col1, col2, col3 = st.columns([2, 2, 1])
        folios_disponibles = [r["folio"] for r in reportes]
        with col1:
            folio_sel = st.selectbox("Folio", folios_disponibles)
        with col2:
            nuevo_estatus = st.selectbox("Nuevo estatus", ESTATUS_FLUJO)
        with col3:
            st.write("")
            st.write("")
            actualizar = st.button("Actualizar")

        if actualizar:
            reporte = next(
                (r for r in reportes if r["folio"] == folio_sel), None)
            if reporte:
                if reporte["estatus"] == nuevo_estatus:
                    st.info("El folio ya tiene ese estatus.")
                else:
                    reporte["estatus"] = nuevo_estatus
                    reporte["historial"].append(
                        {"estatus": nuevo_estatus, "fecha": ahora()}
                    )
                    guardar_datos(data)
                    st.success(
                        f"Folio #{reporte['folio']} actualizado a '{nuevo_estatus}'.")
                    st.rerun()
