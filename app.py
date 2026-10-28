import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuración de la página
st.set_page_config(page_title="Control de Gastos y Utilidad", layout="wide")

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CONFIGURACIÓN DE RUBROS ---
RUBROS = ["Materiales", "Mano de Obra", "Transporte", "Administrativos", "Otros"]

st.title("📊 Gestión de Proyectos: Gastos y Utilidad")

# Menú lateral para navegación
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
                    # Leer datos actuales
                    df_gastos = conn.read(worksheet="Gastos")
                    # Añadir nueva fila
                    new_data = pd.DataFrame([[pd.Timestamp.now(), proyecto, rubro, monto, motivo]], 
                                            columns=["Fecha", "Proyecto", "Rubro", "Monto", "Motivo"])
                    df_final = pd.concat([df_gastos, new_data], ignore_index=True)
                    # Actualizar Google Sheets
                    conn.update(worksheet="Gastos", data=df_final)
                    st.success(f"Gasto registrado exitosamente en {proyecto}")
                else:
                    st.error("Por favor, ingresa el nombre del proyecto")

    with tab2:
        with st.form("form_cotizacion"):
            proyecto_cot = st.text_input("Nombre del Proyecto")
            valor_cot = st.number_input("Valor Total de la Cotización ($)", min_value=0.0, step=1000.0)
            submit_cot = st.form_submit_button("Actualizar Cotización")
            
            if submit_cot:
                if proyecto_cot:
                    df_cot = conn.read(worksheet="Cotizaciones")
                    # Actualizar si existe, si no, agregar
                    if proyecto_cot in df_cot['Proyecto'].values:
                        df_cot.loc[df_cot['Proyecto'] == proyecto_cot, 'Valor_Cotizacion'] = valor_cot
                    else:
                        new_cot = pd.DataFrame([[proyecto_cot, valor_cot]], columns=["Proyecto", "Valor_Cotizacion"])
                        df_cot = pd.concat([df_cot, new_cot], ignore_index=True)
                    
                    conn.update(worksheet="Cotizaciones", data=df_cot)
                    st.success(f"Cotización actualizada para {proyecto_cot}")
                else:
                    st.error("Por favor, ingresa el nombre del proyecto")

elif menu == "Dashboard de Utilidad":
    st.header("📈 Informe de Rendimiento")
    
    # Cargar datos
    df_gastos = conn.read(worksheet="Gastos")
    df_cot = conn.read(worksheet="Cotizaciones")
    
    proyectos_disponibles = df_cot['Proyecto'].unique()
    proyecto_sel = st.selectbox("Selecciona un proyecto para analizar", proyectos_disponibles)
    
    if proyecto_sel:
        # Cálculos
        valor_cotizacion = df_cot.loc[df_cot['Proyecto'] == proyecto_sel, 'Valor_Cotizacion'].values[0]
        gastos_proyecto = df_gastos[df_gastos['Proyecto'] == proyecto_sel]
        total_gastado = gastos_proyecto['Monto'].sum()
        utilidad_valor = valor_cotizacion - total_gastado
        utilidad_porcentaje = (utilidad_valor / valor_cotizacion) * 100 if valor_cotizacion > 0 else 0
        
        # Mostrar Indicadores (KPIs)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Valor Cotizado", f"${valor_cotizacion:,.2f}")
        col2.metric("Total Gastado", f"${total_gastado:,.2f}", delta=f"-{total_gastado:,.2f}", delta_color="inverse")
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
                st.info("No hay gastos registrados para este proyecto.")
        
        with col_right:
            st.subheader("Detalle de Gastos")
            st.dataframe(gastos_proyecto[["Fecha", "Rubro", "Monto", "Motivo"]], use_container_width=True)
