import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
import re  

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Simulador Solar Web", layout="wide", page_icon="☀️", initial_sidebar_state="expanded")

# --- ESTILOS VISUALES ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("☀️ Simulador de Análisis de Celdas (Final)")
st.markdown("---")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("1. Configuración de Medición")
    is_dark = st.checkbox("¿Es medición en OSCURIDAD?", value=False) 
    
    turn_on_threshold = 0.0
    if is_dark:
        st.info("Define 'comienza a aumentar':")
        turn_on_threshold = st.number_input(
            "Corriente de corte (mA/cm²)", 
            value=0.1, 
            step=0.01, 
            format="%.3f"
        )

    st.header("2. Parámetros Físicos")
    area = st.number_input("Área (cm²)", value=0.121, step=0.001, format="%.3f")
    potencia = st.number_input("Potencia (W/cm²)", value=0.1, step=0.01)

    st.header("3. Límites de Gráfica (Web)")
    col1, col2 = st.columns(2)
    xmin = col1.number_input("X Min", value=-0.1) 
    xmax = col2.number_input("X Max", value=1.5)
    ymin = col1.number_input("Y Min", value=-1.0)
    ymax = col2.number_input("Y Max", value=20.0)

# --- FUNCIÓN DE INTERPOLACIÓN ---
def calcular_interseccion(x, y, target_y=0):
    x, y = np.array(x), np.array(y)
    idx_sort = np.argsort(x)
    x, y = x[idx_sort], y[idx_sort]
    y_diff = y - target_y
    sign_changes = np.where(np.diff(np.signbit(y_diff)))[0]
    if len(sign_changes) > 0:
        idx = sign_changes[0] 
        x1, x2, y1, y2 = x[idx], x[idx+1], y[idx], y[idx+1]
        return x1 + (target_y - y1) * (x2 - x1) / (y2 - y1)
    return x[np.abs(y_diff).argmin()]

# --- PROCESAMIENTO ---
st.subheader("Cargar Archivos (.txt)")
uploaded_files = st.file_uploader("Arrastra tus archivos aquí", type=["txt"], accept_multiple_files=True)

if uploaded_files:
    resultados_lista = []
    datos_para_excel = {}

    for uploaded_file in uploaded_files:
        try:
            # --- CORRECCIÓN: Extrae la combinación inicial de números y letras (ej. "1B", "1T") ---
            match = re.match(r'^([A-Za-z0-9]+)', uploaded_file.name)
            grupo_num = match.group(1).upper() if match else "Otro"

            df = pd.read_csv(uploaded_file, sep=r'\s+', skiprows=1, header=None, engine='python')
            df = df.dropna()
            df[0] = df[0].astype(str).str.replace(',', '.').astype(float)
            df[1] = df[1].astype(str).str.replace(',', '.').astype(float)

            # Ajuste de Polaridad y Densidad
            factor_polaridad = 1.0 if is_dark else -1.0
            VF = df[1].values
            IM_mA = (factor_polaridad * df[0].values / area) * 1000

            sort_idx = np.argsort(VF)
            VF, IM_mA = VF[sort_idx], IM_mA[sort_idx]

            # Cálculos
            if is_dark:
                val_Voc = calcular_interseccion(VF, IM_mA, turn_on_threshold)
                res = {"Archivo": uploaded_file.name, "Celda Num": grupo_num, f"V_turn-on (@{turn_on_threshold})": round(val_Voc, 4), "Jsc": "N/A", "FF": "N/A", "Eta": "N/A"}
            else:
                val_Voc = calcular_interseccion(VF, IM_mA, 0)
                val_Jsc = calcular_interseccion(IM_mA, VF, 0)
                P_max = np.max((IM_mA / 1000.0) * VF)
                Eta = (P_max / potencia) * 100
                val_FF = 100 * (P_max / ((val_Jsc / 1000.0) * val_Voc)) if (val_Jsc * val_Voc) != 0 else 0
                res = {"Archivo": uploaded_file.name, "Celda Num": grupo_num, "Voc (V)": round(val_Voc, 4), "Jsc (mA)": round(val_Jsc, 4), "FF (%)": round(val_FF, 2), "Eta (%)": round(Eta, 2)}

            resultados_lista.append(res)
            datos_para_excel[uploaded_file.name] = {'Voltaje': VF, 'Corriente': IM_mA, 'Grupo': grupo_num}

        except Exception as e:
            st.error(f"Error en {uploaded_file.name}: {e}")

    # Mostrar Tabla General 
    with st.expander("Ver Tabla General (Todas las celdas)", expanded=False):
        df_res = pd.DataFrame(resultados_lista)
        st.dataframe(df_res, use_container_width=True)

    st.markdown("---")
    
    # --- SECCIÓN DE FILTRADO Y ESTADÍSTICAS ---
    st.subheader("📈 Curva I-V y Análisis por Celda")
    
    # Selector de grupos
    grupos_disponibles = sorted(df_res["Celda Num"].unique(), key=lambda x: (x=="Otro", str(x)))
    grupos_seleccionados = st.multiselect(
        "Filtra la gráfica seleccionando el identificador de celda:", 
        options=grupos_disponibles, 
        default=grupos_disponibles
    )

    # Generar la gráfica solo con los seleccionados
    fig = go.Figure()
    for nombre_archivo, datos in datos_para_excel.items():
        if datos['Grupo'] in grupos_seleccionados:
            fig.add_trace(go.Scatter(x=datos['Voltaje'], y=datos['Corriente'], mode='lines', name=nombre_archivo))

    y_label = "Corriente (mA/cm²)"
    fig.update_layout(xaxis_title="Voltaje (V)", yaxis_title=y_label, xaxis_range=[xmin, xmax], yaxis_range=[ymin, ymax], template="plotly_white", height=500)
    st.plotly_chart(fig, use_container_width=True)

    # Mostrar tablas de datos específicos
    if not is_dark and len(grupos_seleccionados) > 0:
        # Filtramos el DataFrame maestro en base a lo que elegiste
        df_filtrado = df_res[df_res["Celda Num"].isin(grupos_seleccionados)]
        
        st.markdown(f"#### 📄 Parámetros Individuales (Celdas Seleccionadas)")
        st.dataframe(df_filtrado, use_container_width=True)
        
        # Generar las estadísticas extendidas (Incluye Voc, Jsc, FF y Eta)
        stats = df_filtrado.groupby("Celda Num").agg(
            Voc_Promedio=('Voc (V)', 'mean'),
            Jsc_Promedio=('Jsc (mA)', 'mean'),
            FF_Promedio=('FF (%)', 'mean'),
            Mejor_Eficiencia=('Eta (%)', 'max'),
            Desv_Estandar=('Eta (%)', 'std'),
            Eta_Promedio=('Eta (%)', 'mean'),
            Cantidad=('Archivo', 'count')
        ).reset_index()

        stats = stats.fillna(0) 

        stats.rename(columns={
            'Voc_Promedio': 'Promedio Voc (V)',
            'Jsc_Promedio': 'Promedio Jsc (mA)',
            'FF_Promedio': 'Promedio FF (%)',
            'Mejor_Eficiencia': 'Mejor Eta (%)',
            'Desv_Estandar': 'Desv. Estándar Eta (%)',
            'Eta_Promedio': 'Promedio Eta (%)',
            'Cantidad': 'Celdas Medidas'
        }, inplace=True)

        st.markdown("#### 🏆 Resumen Estadístico por Identificador de Celda")
        st.dataframe(stats.style.format({
            "Promedio Voc (V)": "{:.4f}",
            "Promedio Jsc (mA)": "{:.4f}",
            "Promedio FF (%)": "{:.2f}",
            "Mejor Eta (%)": "{:.2f}",
            "Desv. Estándar Eta (%)": "{:.3f}",
            "Promedio Eta (%)": "{:.2f}"
        }), use_container_width=True)

        # --- DESCARGA EXCLUSIVA DE LA TABLA DE ESTADÍSTICAS ---
        output_stats = io.BytesIO()
        with pd.ExcelWriter(output_stats, engine='xlsxwriter') as writer:
            stats.to_excel(writer, sheet_name='Estadisticas_Resumen', index=False)
            df_filtrado.to_excel(writer, sheet_name='Celdas_Filtradas', index=False)
            
            # Ajustar ancho columnas
            worksheet = writer.sheets['Estadisticas_Resumen']
            for i, col in enumerate(stats.columns):
                column_len = max(stats[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, column_len)

        st.download_button(
            label="📥 Descargar Tabla de Estadísticas (Excel)",
            data=output_stats.getvalue(),
            file_name="Estadisticas_Celdas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_stats"
        )

    st.markdown("---")

    # --- GENERACIÓN DE EXCEL GENERAL ---
    st.subheader("💾 Exportar Excel General Completo (con Gráfica Editable)")
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_res.to_excel(writer, sheet_name='Resultados', index=False)
        
        df_raw = pd.DataFrame()
        for k, v in datos_para_excel.items():
            df_raw[f"V_{k}"] = pd.Series(v['Voltaje'])
            df_raw[f"I_{k}"] = pd.Series(v['Corriente'])
        df_raw.to_excel(writer, sheet_name='Datos_Crudos', index=False)
        
        workbook = writer.book
        worksheet_res = writer.sheets['Resultados']
        chart = workbook.add_chart({'type': 'scatter', 'subtype': 'smooth'})
        
        num_filas = len(df_raw)
        for i, nombre_archivo in enumerate(datos_para_excel.keys()):
            col_v = i * 2
            col_i = i * 2 + 1
            chart.add_series({
                'name':       nombre_archivo,
                'categories': ['Datos_Crudos', 1, col_v, num_filas, col_v],
                'values':     ['Datos_Crudos', 1, col_i, num_filas, col_i],
                'line':       {'width': 1.5},
            })
            
        chart.set_title({'name': 'Curvas I-V (Editables)'})
        chart.set_x_axis({'name': 'Voltaje (V)', 'major_gridlines': {'visible': True}})
        chart.set_y_axis({'name': 'Corriente (mA/cm²)', 'major_gridlines': {'visible': True}})
        
        worksheet_res.insert_chart('G2', chart, {'x_scale': 1.5, 'y_scale': 1.5})

    st.download_button(
        label="📥 Descargar Reporte Excel Completo",
        data=output.getvalue(),
        file_name="Reporte_I-V_Completo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_full"
    )
else:
    st.info("Carga tus archivos .txt arriba.")
