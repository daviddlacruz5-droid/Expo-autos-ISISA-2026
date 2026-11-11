import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import csv
import os
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Registro Expo Autos ISISA 2026", page_icon="🏎️", layout="centered")

st.title("🏎️ Registro de Asistencia")
st.subheader("Expo Autos ISISA 2026 - ESIME Zacatenco")
st.markdown("Completa tus datos para generar y descargar tu gafete de acceso oficial.")

ARCHIVO_PLANTILLA = "plantilla_gafete.png" 
ARCHIVO_REGISTROS = "asistentes_registrados.csv"

# Lista completa de instituciones
OPCIONES_INSTITUCION = [
    "CECYT 1 \"Gonzalo Vázquez Vela\"", "CECYT 2 \"Miguel Bernard Perales\"",
    "CECYT 3 \"Estanislao Ramírez Ruiz\"", "CECYT 4 \"Lázaro Cárdenas\"",
    "CECYT 5 \"Benito Juárez García\"", "CECYT 6 \"Miguel Othón de Mendizábal\"",
    "CECYT 7 \"Cuauhtémoc\"", "CECYT 8 \"Narciso Bassols García\"",
    "CECYT 9 \"Juan de Dios Bátiz Paredes\"", "CECYT 10 \"Carlos Vallejo Márquez\"",
    "CECYT 11 \"Wilfrido Massieu\"", "CECYT 12 \"José María Morelos y Pavón\"",
    "CECYT 13 \"Ricardo Flores Magón\"", "CECYT 14 \"Luis Enrique Erro Soler\"",
    "CECYT 15 \"Diódoro Antúnez Echegaray\"", "CECYT 16 \"Unidad Hidalgo\"",
    "CECYT 17 \"Unidad Guanajuato\" (León)", "CECYT 18 \"Unidad Zacatecas\"",
    "CECYT 19 \"Leona Vicario\" (Tecámac)", "CECYT 20 \"Natalia Serdán Alatriste\" (Puebla)",
    "CET 1 \"Walter Cross Buchanan\"",
    "CICS UMA - Centro Interdisciplinario de Ciencias de la Salud, Unidad Milpa Alta",
    "CICS UST - Centro Interdisciplinario de Ciencias de la Salud, Unidad Santo Tomás",
    "ENBA - Escuela Nacional de Biblioteconomía y Archivonomía",
    "ENCB - Escuela Nacional de Ciencias Biológicas",
    "ENMH - Escuela Nacional de Medicina y Homeopatía",
    "ESCA Santo Tomás - Escuela Superior de Comercio y Administración",
    "ESCA Tepepan - Escuela Superior de Comercio y Administración",
    "ESCOM - Escuela Superior de Cómputo", "ESE - Escuela Superior de Economía",
    "ESEO - Escuela Superior de Enfermería y Obstetricia", 
    "ESFM - Escuela Superior de Física y Matemáticas",
    "ESIA Tecamachalco - Escuela Superior de Ingeniería y Arquitectura",
    "ESIA Ticomán - Escuela Superior de Ingeniería y Arquitectura",
    "ESIA Zacatenco - Escuela Superior de Ingeniería y Arquitectura",
    "ESIME Azcapotzalco - Escuela Superior de Ingeniería Mecánica y Eléctrica",
    "ESIME Culhuacán - Escuela Superior de Ingeniería Mecánica y Eléctrica",
    "ESIME Ticomán - Escuela Superior de Ingeniería Mecánica y Eléctrica",
    "ESIME Zacatenco - Escuela Superior de Ingeniería Mecánica y Eléctrica",
    "ESIQIE - Escuela Superior de Ingeniería Química e Industrias Extractivas",
    "ESIT - Escuela Superior de Ingeniería Textil", "ESM - Escuela Superior de Medicina",
    "EST - Escuela Superior de Turismo", "UPIBI - Unidad Profesional Interdisciplinaria de Biotecnología",
    "UPIEM - Unidad Profesional Interdisciplinaria de Energía y Movilidad",
    "UPIIAP - Unidad Profesional Interdisciplinaria de Ingeniería (Puebla)",
    "UPIICSA - Unidad Profesional Interdisciplinaria de Ingeniería y Ciencias Sociales",
    "UPIITA - Unidad Profesional Interdisciplinaria en Ingeniería y Tecnologías Avanzadas",
    "UPIIC - Unidad Profesional Interdisciplinaria de Ingeniería Campus Coahuila",
    "UPIIG - Unidad Profesional Interdisciplinaria de Ingeniería Campus Guanajuato",
    "UPIIH - Unidad Profesional Interdisciplinaria de Ingeniería Campus Hidalgo",
    "UPIIP - Unidad Profesional Interdisciplinaria de Ingeniería Campus Palenque",
    "UPIIT - Unidad Profesional Interdisciplinaria de Ingeniería Campus Tlaxcala",
    "UPIIZ - Unidad Profesional Interdisciplinaria de Ingeniería Campus Zacatecas",
    "Público General", "Otra (especificar)"
]

# Buscador de fuentes nativas (arregla el tamaño y los acentos en Streamlit Cloud)
def obtener_fuente_ajustada(texto, draw, max_ancho, tamaño_inicial=42):
    tamaño = max(int(tamaño_inicial), 10) 
    fuentes_a_intentar = ["arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf", "FreeSans.ttf"]
    
    while tamaño > 6:
        fuente_cargada = None
        for nombre_fuente in fuentes_a_intentar:
            try:
                fuente_cargada = ImageFont.truetype(nombre_fuente, tamaño)
                break
            except:
                continue
                
        if not fuente_cargada:
            return ImageFont.load_default() 
            
        bbox = draw.textbbox((0, 0), texto, font=fuente_cargada)
        if (bbox[2] - bbox[0]) <= max_ancho:
            return fuente_cargada
        tamaño -= 2
        
    return ImageFont.load_default()

# Formulario
with st.form("form_registro", clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre(s):")
    with col2:
        apellidos = st.text_input("Apellidos:")
        
    correo = st.text_input("Correo electrónico:")
    
    col3, col4 = st.columns(2)
    with col3:
        # Búsqueda segura del índice por defecto
        try:
            indice_esime = OPCIONES_INSTITUCION.index("ESIME Zacatenco - Escuela Superior de Ingeniería Mecánica y Eléctrica")
        except ValueError:
            try:
                indice_esime = OPCIONES_INSTITUCION.index("ESIME Zacatenco - Escuela Superior de Ingeniería Mecánica y Eléctrica, Unidad Zacatenco")
            except ValueError:
                indice_esime = 0
                
        opcion_inst = st.selectbox(
            "Institución / Escuela / Procedencia:",
            OPCIONES_INSTITUCION,
            index=indice_esime
        )
        otra_inst = st.text_input("Escribe tu institución (solo si elegiste 'Otra'):")
    with col4:
        tipo_asistente = st.selectbox("Tipo de Asistente:", ["Visitante", "Estudiante", "Expositor", "Docente"])
        
    boton_registro = st.form_submit_button("Generar y Descargar Gafete", use_container_width=True)

if boton_registro:
    nombre_completo = f"{nombre.strip()} {apellidos.strip()}".strip()
    institucion_final = otra_inst.strip() if opcion_inst == "Otra (especificar)" else opcion_inst
    
    if not nombre_completo or not correo.strip():
        st.error("⚠️ Por favor completa tu nombre completo y correo electrónico.")
    else:
        # Lógica para Folio desde cero leyendo el CSV
        numero_folio = 1
        if os.path.exists(ARCHIVO_REGISTROS):
            try:
                df_existente = pd.read_csv(ARCHIVO_REGISTROS)
                numero_folio = len(df_existente) + 1
            except:
                pass
        
        folio = f"ISISA-{numero_folio:04d}" 
        
        # Guardar en CSV temporal
        nuevo_registro = not os.path.exists(ARCHIVO_REGISTROS)
        with open(ARCHIVO_REGISTROS, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if nuevo_registro:
                writer.writerow(["Fecha", "Folio", "Nombre Completo", "Correo", "Institución", "Tipo"])
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), folio, nombre_completo, correo, institucion_final, tipo_asistente])
        
        # Generar Gafete
        img = Image.open(ARCHIVO_PLANTILLA).convert("RGB")
        draw = ImageDraw.Draw(img)
        ancho_img, alto_img = img.size
        
        y_caja_superior = int(alto_img * 0.72)
        y_caja_inferior = int(alto_img * 0.93)
        margen_x = int(ancho_img * 0.08)
        ancho_disponible = (ancho_img - (margen_x * 2)) - 40
        x_centro = ancho_img / 2
        alto_caja = y_caja_inferior - y_caja_superior
        
        # Dibujar caja blanca
        draw.rounded_rectangle([(margen_x, y_caja_superior), (ancho_img - margen_x, y_caja_inferior)], radius=15, fill="#FFFFFF")
        
        # Separar institución en dos renglones si contiene " - "
        if " - " in institucion_final:
            partes = institucion_final.split(" - ", 1)
            inst_abrev = partes[0].strip()
            inst_full = partes[1].strip()
        else:
            inst_abrev = institucion_final
            inst_full = ""
            
        # --- MULTIPLICADORES DE TAMAÑO GIGANTES ---
        fuente_nombre = obtener_fuente_ajustada(nombre_completo, draw, ancho_disponible, tamaño_inicial=int(alto_img * 0.050))
        fuente_inst_abrev = obtener_fuente_ajustada(inst_abrev, draw, ancho_disponible, tamaño_inicial=int(alto_img * 0.040))
        
        # Función rápida para cargar la fuente de Rol y Folio
        def cargar_fuente_estatica(tam):
            for f in ["arial.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"]:
                try:
                    return ImageFont.truetype(f, tam)
                except:
                    continue
            return ImageFont.load_default()

        fuente_tipo = cargar_fuente_estatica(int(alto_img * 0.025))
        fuente_folio = cargar_fuente_estatica(int(alto_img * 0.035))
            
        # Imprimir Textos en la imagen (Coordenadas ajustadas)
        draw.text((x_centro, y_caja_superior + int(alto_caja * 0.15)), nombre_completo, font=fuente_nombre, fill="#111111", anchor="mm")
        draw.text((x_centro, y_caja_superior + int(alto_caja * 0.35)), inst_abrev, font=fuente_inst_abrev, fill="#444444", anchor="mm")
        
        if inst_full:
            # Letra más pequeña para el nombre completo de la escuela para que quepa en un renglón
            fuente_inst_full = obtener_fuente_ajustada(inst_full, draw, ancho_disponible, tamaño_inicial=int(alto_img * 0.016))
            draw.text((x_centro, y_caja_superior + int(alto_caja * 0.50)), inst_full, font=fuente_inst_full, fill="#666666", anchor="mm")
            
        draw.text((x_centro, y_caja_superior + int(alto_caja * 0.70)), f"ROL: {tipo_asistente.upper()}", font=fuente_tipo, fill="#005A36", anchor="mm")
        draw.text((x_centro, y_caja_superior + int(alto_caja * 0.85)), f"FOLIO: {folio}", font=fuente_folio, fill="#6B1D2F", anchor="mm")
        
        # Guardar como PDF en memoria
        buffer_pdf = io.BytesIO()
        img.save(buffer_pdf, format="PDF", resolution=100.0)
        pdf_bytes = buffer_pdf.getvalue()
        
        st.success(f"¡Registro exitoso! Tu número de folio es **{folio}**.")
        st.download_button(label="📥 DESCARGAR MI GAFETE EN PDF", data=pdf_bytes, file_name=f"Gafete_{folio}.pdf", mime="application/pdf", use_container_width=True)
        st.image(img, caption="Vista previa de tu gafete de acceso", use_container_width=True)

# Panel de Administrador Oculto
st.markdown("---")
with st.expander("Ver base de datos de asistentes (Solo Administradores)"):
    # Pedir contraseña para mostrar los datos
    password = st.text_input("Ingresa la contraseña de administrador para acceder:", type="password")
    
    # Contraseña configurada
    if password == "Comite2026": 
        if os.path.exists(ARCHIVO_REGISTROS):
            df = pd.read_csv(ARCHIVO_REGISTROS)
            
            st.subheader("📊 Resumen de Registros")
            st.metric(label="Total de Asistentes Registrados", value=len(df))
            
            st.write("**Desglose por Tipo de Asistente:**")
            conteo_roles = df["Tipo"].value_counts().reset_index()
            conteo_roles.columns = ["Rol", "Cantidad"]
            st.dataframe(conteo_roles, hide_index=True)
            
            st.markdown("---")
            st.write("**Base de datos detallada:**")
            st.dataframe(df, use_container_width=True)
            
            with open(ARCHIVO_REGISTROS, "rb") as file:
                st.download_button(
                    label="📥 Descargar Base de Datos completa (CSV)", 
                    data=file, 
                    file_name="Registro_ExpoAutos_ISISA.csv", 
                    mime="text/csv"
                )
        else:
            st.info("Aún no hay ningún asistente registrado.")
    elif password != "":
        st.error("Contraseña incorrecta.")
