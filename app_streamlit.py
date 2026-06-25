import io
import unicodedata
import streamlit as st
from PIL import Image

from analizador_paleta import AnalizadorPaleta
from generador_paleta import GeneradorPaletas
from editor_imagen import EditorImagen
from color import Color

# ──────────────────────────────────────────────
# Ayudantes
# ──────────────────────────────────────────────

def normalizar_texto(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = texto.replace(" ", "_")
    return "".join(ch for ch in texto if ch.isalnum() or ch in "-_")


def pil_a_bytes(imagen: Image.Image, fmt: str = "PNG") -> bytes:
    buf = io.BytesIO()
    imagen.save(buf, format=fmt)
    return buf.getvalue()


# ──────────────────────────────────────────────
# Procesamiento
# ──────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def analizar(img_bytes: bytes, n_colores: int):
    """Extrae colores dominantes. Cacheado para no recalcular en cada interacción."""
    imagen = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    analizador = AnalizadorPaleta.__new__(AnalizadorPaleta)
    analizador.ruta_imagen = None
    analizador.n_colores = n_colores
    analizador.imagen = imagen
    analizador.colores_dominantes = []
    colores = analizador.extraer_colores()
    paleta_visual = analizador.obtener_paleta_visual()
    paleta_sobre_imagen = analizador.obtener_paleta_original()
    return colores, paleta_visual, paleta_sobre_imagen


def procesar_imagen(img_bytes: bytes, colores_orig, colores_nuevos,
                    brillo: float, saturacion: float,
                    escala: int) -> Image.Image:
    """Aplica paleta + ajustes de brillo, saturación y tamaño."""
    imagen = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    editor = EditorImagen(imagen)

    # 1. Paleta
    nuevos = colores_nuevos[: len(colores_orig)]
    resultado = editor.aplicar_paleta(colores_orig, nuevos)

    # 2. Brillo
    if brillo != 1.0:
        editor2 = EditorImagen(resultado)
        resultado = editor2.cambiar_brillo(brillo)

    # 3. Saturación
    if saturacion != 1.0:
        editor3 = EditorImagen(resultado)
        resultado = editor3.cambiar_saturacion(saturacion)

    # 4. Tamaño (escala %)
    if escala != 100:
        nuevo_ancho = int(resultado.width * escala / 100)
        nuevo_alto = int(resultado.height * escala / 100)
        editor4 = EditorImagen(resultado)
        resultado = editor4.cambiar_tamano(nuevo_ancho, nuevo_alto)

    return resultado


def crear_comparativa(original: Image.Image, editada: Image.Image) -> Image.Image:
    altura = min(original.height, editada.height)
    orig_r = original.resize((int(original.width * altura / original.height), altura))
    # Escalar editada a la misma altura para comparativa siempre legible
    edit_r = editada.resize((int(editada.width * altura / editada.height), altura))
    margen = 20
    comp = Image.new("RGB", (orig_r.width + margen + edit_r.width, altura), "white")
    comp.paste(orig_r, (0, 0))
    comp.paste(edit_r, (orig_r.width + margen, 0))
    return comp


# ──────────────────────────────────────────────
# Interfaz de usuario
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="Paletas de Color",
    page_icon="🌈",
    layout="wide",
)

st.title("Paletas de Color")
st.subheader("Procesamiento de Imágenes")
st.caption("Extraé los colores dominantes de tu imagen y aplicá paletas alternativas.")

# ── Sidebar ─────────────────────────────────────
with st.sidebar:
    st.header("Configuración")

    uploaded = st.file_uploader(
        "Subí tu imagen",
        type=["png", "jpg", "jpeg", "bmp", "webp"],
        key="uploaded",
    )

    st.divider()
    st.subheader("Extracción de colores")
    n_colores = st.slider("Cantidad de colores", min_value=1, max_value=8, value=5)
    analizar_btn = st.button("Analizar imagen", use_container_width=True, type="primary")
    limpiar_btn = st.button("Borrar resultados", use_container_width=True)

    if limpiar_btn:
        for key in ("colores", "paletas", "img_bytes", "paleta_visual", "paleta_original"):
            st.session_state[key] = None
        st.rerun()

    st.divider()
    st.subheader("Paleta alternativa")
    tipo_paleta = st.radio(
        "Tipo de paleta",
        options=["Complementaria", "Análoga", "Triádica"],
        index=0,
    )

    st.divider()
    st.subheader("Ajustes de imagen")

    brillo = st.slider(
        "Brillo",
        min_value=0.1, max_value=3.0, value=1.0, step=0.05,
        help="1.0 = sin cambios · <1 más oscuro · >1 más claro",
    )
    saturacion = st.slider(
        "Saturación",
        min_value=0.0, max_value=3.0, value=1.0, step=0.05,
        help="1.0 = sin cambios · 0 escala de grises · >1 más saturado",
    )
    escala = st.slider(
        "Tamaño (%)",
        min_value=10, max_value=200, value=100, step=5,
        help="100 = tamaño original",
    )

# ── Estado de sesión ────────────────────────────
for key in ("colores", "paletas", "img_bytes", "paleta_visual", "paleta_original"):
    if key not in st.session_state:
        st.session_state[key] = None

# ── Análisis ────────────────────────────────────
if uploaded and analizar_btn:
    img_bytes = uploaded.read()
    st.session_state.img_bytes = img_bytes

    with st.spinner("Extrayendo colores dominantes…"):
        colores, paleta_visual, paleta_original = analizar(img_bytes, n_colores)
        paletas = GeneradorPaletas(colores).generar_paletas()

    st.session_state.colores = colores
    st.session_state.paleta_visual = paleta_visual
    st.session_state.paleta_original = paleta_original
    st.session_state.paletas = paletas

# ── Resultados ──────────────────────────────────
if st.session_state.colores is not None:
    colores = st.session_state.colores
    paletas = st.session_state.paletas
    img_bytes = st.session_state.img_bytes

    # — Imagen original + paleta dominante —
    st.subheader("Imagen original y paleta dominante")
    col_img, col_paleta = st.columns(2)
    with col_img:
        st.image(img_bytes, caption="Imagen subida", use_container_width=True)
    with col_paleta:
        st.image(st.session_state.paleta_visual,
                 caption="Paleta de colores dominantes", use_container_width=True)
        st.image(st.session_state.paleta_original,
                 caption="Paleta sobre imagen original", use_container_width=True)

    # — Swatches de colores extraídos —
    st.subheader("Colores extraídos")
    cols = st.columns(len(colores))
    for col_ui, color in zip(cols, colores):
        c = Color(color)
        hex_val = c.rgb_to_hex()
        with col_ui:
            st.markdown(
                f"""<div style="background:{hex_val};height:80px;border-radius:8px;
                                border:1px solid #ccc;margin-bottom:4px"></div>
                    <p style="text-align:center;font-size:13px;margin:0">
                        <b>{hex_val}</b><br>{c.clasificar_temperatura()}<br>{c.clasificar_brillo()}
                    </p>""",
                unsafe_allow_html=True,
            )

    # — Paleta alternativa —
    colores_nuevos = paletas[tipo_paleta]["colores"]
    descripcion = paletas[tipo_paleta].get("descripcion", "")
    st.subheader(f"Paleta alternativa — {tipo_paleta}")
    st.caption(descripcion)

    cols_alt = st.columns(len(colores_nuevos))
    for col_ui, color in zip(cols_alt, colores_nuevos):
        c = Color(color)
        hex_val = c.rgb_to_hex()
        with col_ui:
            st.markdown(
                f"""<div style="background:{hex_val};height:80px;border-radius:8px;
                                border:1px solid #ccc;margin-bottom:4px"></div>
                    <p style="text-align:center;font-size:13px;margin:0">
                        <b>{hex_val}</b><br>{c.clasificar_temperatura()}<br>{c.clasificar_brillo()}
                    </p>""",
                unsafe_allow_html=True,
            )

    # — Resultado con todos los ajustes —
    st.subheader("Resultado")

    ajustes_activos = []
    if brillo != 1.0:
        ajustes_activos.append(f"Brillo {brillo:.2f}")
    if saturacion != 1.0:
        ajustes_activos.append(f"Saturación {saturacion:.2f}")
    if escala != 100:
        ajustes_activos.append(f"Tamaño {escala}%")
    if ajustes_activos:
        st.caption("Ajustes aplicados: " + " · ".join(ajustes_activos))

    with st.spinner("Procesando imagen…"):
        img_editada = procesar_imagen(
            img_bytes, colores, colores_nuevos,
            brillo, saturacion, escala,
        )
        img_original_pil = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        comparativa = crear_comparativa(img_original_pil, img_editada)

    col_edit, col_comp = st.columns([1, 2])
    with col_edit:
        st.image(img_editada, caption="Imagen procesada", use_container_width=True)
        ancho_px = img_editada.width
        alto_px = img_editada.height
        st.caption(f"Dimensiones: {ancho_px} × {alto_px} px")
    with col_comp:
        st.image(comparativa, caption="Comparativa original vs. procesada",
                 use_container_width=True)

    # — Descargas —
    st.subheader("Descargar resultados")
    nombre_base = normalizar_texto(tipo_paleta)
    d1, d2, d3 = st.columns(3)

    with d1:
        st.download_button(
            "Imagen procesada",
            data=pil_a_bytes(img_editada),
            file_name=f"{nombre_base}_{n_colores}colores.png",
            mime="image/png",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            "Comparativa",
            data=pil_a_bytes(comparativa),
            file_name=f"comparativa_{nombre_base}_{n_colores}colores.png",
            mime="image/png",
            use_container_width=True,
        )
    with d3:
        st.download_button(
            "Paleta visual",
            data=pil_a_bytes(st.session_state.paleta_visual),
            file_name=f"paleta_{nombre_base}_{n_colores}colores.png",
            mime="image/png",
            use_container_width=True,
        )

else:
    if not uploaded:
        st.info("Subí una imagen desde el panel izquierdo para comenzar.")
    else:
        st.info("Ajustá los parámetros y presioná **Analizar imagen**.")