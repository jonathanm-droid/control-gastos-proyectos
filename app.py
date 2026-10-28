import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Control de Gastos y Utilidad", layout="wide")

# --- CONFIGURACIÓN ---
# PEGA AQUÍ EL ENLACE DE TU HOJA DE GOOGLE SHEETS
SHEET_URL = "https://docs.google.com/spreadsheets/d/15jy_83GcYCqGivTmjsqmEvtDSeahJxCNWzMg5BJj6HU/edit?usp=sharing" 

# Función para convertir enlace de Google Sheets a CSV exportable
def get_gsheet_url(url, sheet_name):
    # Esta función transforma el link de la hoja en un link de descarga de datos
    sheet_id = url.split("/d/")[1].split("/")[0]
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# RUBROS
RUBROS = ["Materiales", "Mano de Obra", "Transporte", "Administrativos", "Otros"]

st.title("📊 Gestión de Proyectos: Gastos y Utilidad")

menu = st.sidebar.selectbox("Menú", ["Ingresar Datos", "Dashboard de Utilidad"])

if menu == "Ingresar Datos":
    st.header("📝 Registro de Información")
    
    tab1, tab2 = st.tabs(["Registrar Gasto", "Actualizar Cotización"])
    
    with tab1:
        with st.form("form_gasto"):
            proyecto = st.text_input("Nombre del Proyecto")
            rubro = st.selectbox("Rubro del Gasto", RUBROS)
            monto = st.number_input("Valor del Gasto ($)", min_value=0.0, step=100.0)
            motivo = st.text_area("Motivo/Descripción")
            submit = st.form_submit_button("Guardar Gasto")
            
            if submit:
                if proyecto:
                    st.warning("Para guardar datos sin credenciales, usa la hoja de cálculo directamente o contacta a un desarrollador para configurar la API de Google.")
                    st.info("Copia estos datos en tu hoja: " + f"{proyecto} | {rubro} | {monto} | {motivo}")
                else:
                    st.error("Por favor, ingresa el nombre del proyecto")

    with tab2:
        st.info("La cotización debe actualizarse directamente en la pestaña 'Cotizaciones' de tu hoja de Google Sheets para mantener la seguridad.")

elif menu == "Dashboard de Utilidad":
    st.header("📈 Informe de Rendimiento")
    
    try:
        # Leer datos directamente desde el link público
        df_gastos = pd.read_csv(get_gsheet_url(SHEET_URL, "Gastos"))
        df_cot = pd.read_csv(get_gsheet_url(SHEET_URL, "Cotizaciones"))
        
        proyectos_disponibles = df_cot['Proyecto'].unique()
        proyecto_sel = st.selectbox("Selecciona un proyecto para analizar", proyectos_disponibles)
        
        if proyecto_sel:
            valor_cotizacion = df_cot.loc[df_cot['Proyecto'] == proyecto_sel, 'Valor_Cotizacion'].values[0]
            gastos_proyecto = df_gastos[df_gastos['Proyecto'] == proyecto_sel]
            total_gastado = gastos_proyecto['Monto'].sum()
            utilidad_valor = valor_cotizacion - total_gastado
            utilidad_porcentaje = (utilidad_valor / valor_cotizacion) * 100 if valor_cotizacion > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Valor Cotizado", f"${valor_cotizacion:,.2f}")
            col2.metric("Total Gastado", f"${total_gastado:,.2f}")
            col3.metric("Utilidad Neta", f"${utilidad_valor:,.2f}")
            col4.metric("Margen de Utilidad", f"{utilidad_porcentaje:.2f}%")
            
            st.divider()
            
            col_left, col_right = st.columns([1, 1])
            with col_left:
                st.subheader("Gastos por Rubro")
                if not gastos_proyecto.empty:
                    resumen_rubros = gastos_proyecto.groupby("Rubro")["Monto"].sum()
                    st.bar_chart(resumen_rubros)
                else:
                    st.info("No hay gastos registrados.")
            
            with col_right:
                st.subheader("Detalle de Gastos")
                st.dataframe(gastos_proyecto, use_container_width=True)
                
    except Exception as e:
        st.error("No se pudo conectar con la hoja. Verifica que el enlace sea correcto y que la hoja sea PÚBLICA (Editor).")
