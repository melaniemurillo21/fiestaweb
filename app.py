import streamlit as st
import libsql
import pandas as pd

# Configuración inicial
st.set_page_config(page_title="Fiesta de Aniversario 🎉", layout="centered")

# Leer credenciales
TURSO_URL = st.secrets["TURSO_URL"]
TURSO_TOKEN = st.secrets["TURSO_TOKEN"]

# Conexión con Turso
conn = libsql.connect(
    "fiesta.db",
    sync_url=TURSO_URL,
    auth_token=TURSO_TOKEN
)
cursor = conn.cursor()

st.title("🎊 Lista de Invitados - Fiesta de Aniversario")
st.divider()

# ---- CREAR INVITADO ----
with st.expander("➕ Agregar nuevo invitado"):
    nombre = st.text_input("Nombre")
    apellidos = st.text_input("Apellidos")
    telefono = st.text_input("Teléfono")
    correo = st.text_input("Correo")
    asistira = st.radio("¿Asistirá?", ["Sí", "No"], horizontal=True)
    num_acompanantes = st.number_input("Número de acompañantes", min_value=0, max_value=10, step=1)

    if st.button("Guardar invitado"):
        if nombre and apellidos:
            cursor.execute("""
                INSERT INTO invitados (nombre, apellidos, telefono, correo, asistira, num_acompanantes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nombre, apellidos, telefono, correo, asistira, num_acompanantes))
            conn.commit()
            st.success(f"✅ Invitado {nombre} {apellidos} agregado correctamente.")
        else:
            st.error("Por favor, completa al menos nombre y apellidos.")

st.divider()

# ---- LEER / MOSTRAR INVITADOS ----
st.subheader("📋 Lista de invitados registrados")
data = cursor.execute("SELECT * FROM invitados").fetchall()
df = pd.DataFrame(data, columns=["ID", "Nombre", "Apellidos", "Teléfono", "Correo", "Asistirá", "Acompañantes"])
st.dataframe(df, use_container_width=True)

# ---- ACTUALIZAR INVITADO ----
with st.expander("✏️ Editar invitado existente"):
    ids = [row[0] for row in data]
    if ids:
        selected_id = st.selectbox("Selecciona ID del invitado", ids)
        if selected_id:
            invitado = cursor.execute("SELECT * FROM invitados WHERE id = ?", (selected_id,)).fetchone()
            if invitado:
                nombre_edit = st.text_input("Nombre", invitado[1])
                apellidos_edit = st.text_input("Apellidos", invitado[2])
                telefono_edit = st.text_input("Teléfono", invitado[3])
                correo_edit = st.text_input("Correo", invitado[4])
                asistira_edit = st.radio("¿Asistirá?", ["Sí", "No"], index=0 if invitado[5] == "Sí" else 1, horizontal=True)
                num_acompanantes_edit = st.number_input("Número de acompañantes", min_value=0, max_value=10, value=invitado[6], step=1)

                if st.button("Actualizar datos"):
                    cursor.execute("""
                        UPDATE invitados
                        SET nombre = ?, apellidos = ?, telefono = ?, correo = ?, asistira = ?, num_acompanantes = ?
                        WHERE id = ?
                    """, (nombre_edit, apellidos_edit, telefono_edit, correo_edit, asistira_edit, num_acompanantes_edit, selected_id))
                    conn.commit()
                    st.success("✅ Datos actualizados correctamente.")
    else:
        st.info("No hay invitados para editar todavía.")

# ---- ELIMINAR INVITADO ----
with st.expander("🗑️ Eliminar invitado"):
    ids = [row[0] for row in data]
    if ids:
        delete_id = st.selectbox("Selecciona ID para eliminar", ids)
        if st.button("Eliminar invitado"):
            cursor.execute("DELETE FROM invitados WHERE id = ?", (delete_id,))
            conn.commit()
            st.warning(f"Invitado con ID {delete_id} eliminado.")
    else:
        st.info("No hay invitados para eliminar todavía.")

conn.close()
