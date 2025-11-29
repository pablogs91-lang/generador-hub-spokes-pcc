import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time

try:
    import plotly.graph_objects as go
    import plotly.express as px
except ImportError:
    st.error("Error al cargar Plotly. Reinstalando...")
    import subprocess
    subprocess.check_call(["pip", "install", "--upgrade", "plotly"])
    import plotly.graph_objects as go
    import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Trend Hunter - PCComponentes",
    page_icon="🔍",
    layout="wide"
)

# API Key de SerpAPI
SERPAPI_KEY = "282b59f5ce2f8b2b7ddff4fea0c6c5b9bbb35b832ab1db3800be405fa5719094"

# Mapeo de países
COUNTRIES = {
    "ES": {"name": "España", "flag": "🇪🇸"},
    "PT": {"name": "Portugal", "flag": "🇵🇹"},
    "FR": {"name": "Francia", "flag": "🇫🇷"},
    "IT": {"name": "Italia", "flag": "🇮🇹"},
    "DE": {"name": "Alemania", "flag": "🇩🇪"}
}

# Título principal
st.title("🔍 Trend Hunter - PCComponentes")
st.markdown("### Análisis de tendencias de marcas en Google Trends")

# Sidebar para configuración
st.sidebar.header("⚙️ Configuración")

# Upload CSV
uploaded_file = st.sidebar.file_uploader("📁 Sube tu CSV con marcas", type=['csv'])

# Selector de países (multi-select)
selected_countries = st.sidebar.multiselect(
    "🌍 Selecciona países",
    options=list(COUNTRIES.keys()),
    default=["ES"],
    format_func=lambda x: f"{COUNTRIES[x]['flag']} {COUNTRIES[x]['name']}"
)

if not selected_countries:
    st.warning("⚠️ Selecciona al menos un país")
    st.stop()

# Función para llamar a SerpAPI - Interest Over Time
def get_interest_over_time(brand, geo="ES"):
    """Obtiene datos de interés a lo largo del tiempo (5 años)"""
    url = "https://serpapi.com/search.json"
    
    params = {
        "engine": "google_trends",
        "q": brand,
        "data_type": "TIMESERIES",
        "date": "today 5-y",
        "geo": geo,
        "api_key": SERPAPI_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error en API: {e}")
        return None

# Función para obtener Related Queries
def get_related_queries(brand, geo="ES"):
    """Obtiene búsquedas relacionadas (TOP + RISING)"""
    url = "https://serpapi.com/search.json"
    
    params = {
        "engine": "google_trends",
        "q": brand,
        "data_type": "RELATED_QUERIES",
        "geo": geo,
        "api_key": SERPAPI_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

# Función para obtener Related Topics
def get_related_topics(brand, geo="ES"):
    """Obtiene temas relacionados (TOP + RISING)"""
    url = "https://serpapi.com/search.json"
    
    params = {
        "engine": "google_trends",
        "q": brand,
        "data_type": "RELATED_TOPICS",
        "geo": geo,
        "api_key": SERPAPI_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

# Función para calcular cambios porcentuales MEJORADA
def calculate_changes(timeline_data):
    """Calcula % cambio mes, quarter, año con más precisión"""
    if not timeline_data or 'interest_over_time' not in timeline_data:
        return None, None, None, None
    
    try:
        values = timeline_data['interest_over_time']['timeline_data']
        
        if len(values) < 12:
            return None, None, None, None
        
        # Extraer valores
        all_values = []
        all_dates = []
        
        for point in values:
            if point.get('values') and len(point['values']) > 0:
                val = point['values'][0].get('extracted_value', 0)
                all_values.append(val)
                all_dates.append(point.get('date', ''))
        
        if len(all_values) < 12:
            return None, None, None, None
        
        # Valor actual (más reciente)
        current = all_values[-1]
        
        # Valor hace 1 mes (4-5 semanas atrás)
        month_ago = all_values[-5] if len(all_values) >= 5 else all_values[0]
        
        # Valor hace 3 meses (12-13 semanas atrás)
        quarter_ago = all_values[-13] if len(all_values) >= 13 else all_values[0]
        
        # Valor hace 1 año (52 semanas atrás)
        year_ago = all_values[-52] if len(all_values) >= 52 else all_values[0]
        
        # Calcular cambios porcentuales
        month_change = ((current - month_ago) / month_ago * 100) if month_ago > 0 else 0
        quarter_change = ((current - quarter_ago) / quarter_ago * 100) if quarter_ago > 0 else 0
        year_change = ((current - year_ago) / year_ago * 100) if year_ago > 0 else 0
        
        # Promedio de los últimos 5 años
        avg_value = sum(all_values) / len(all_values) if all_values else 0
        
        return month_change, quarter_change, year_change, avg_value
    
    except Exception as e:
        return None, None, None, None

# Función principal de análisis
def analyze_brand(brand, countries):
    """Análisis completo de una marca para múltiples países"""
    
    results = {}
    
    for geo in countries:
        country_name = COUNTRIES[geo]['name']
        
        with st.spinner(f'🔎 Analizando {brand} en {country_name}...'):
            
            # 1. Interest Over Time
            timeline_data = get_interest_over_time(brand, geo)
            time.sleep(1)
            
            # 2. Related Queries
            queries_data = get_related_queries(brand, geo)
            time.sleep(1)
            
            # 3. Related Topics
            topics_data = get_related_topics(brand, geo)
            time.sleep(1)
            
            # Calcular cambios
            month_change, quarter_change, year_change, avg_value = calculate_changes(timeline_data)
            
            results[geo] = {
                'country': country_name,
                'timeline': timeline_data,
                'queries': queries_data,
                'topics': topics_data,
                'month_change': month_change,
                'quarter_change': quarter_change,
                'year_change': year_change,
                'avg_value': avg_value
            }
    
    return results

# Función para mostrar gráfico comparativo multi-país
def show_comparative_chart(brand, results):
    """Muestra gráfico comparativo de tendencias entre países"""
    
    fig = go.Figure()
    
    for geo, data in results.items():
        if data['timeline'] and 'interest_over_time' in data['timeline']:
            timeline = data['timeline']['interest_over_time']['timeline_data']
            
            dates = []
            values = []
            
            for point in timeline:
                dates.append(point['date'])
                val = point['values'][0]['extracted_value'] if point['values'] else 0
                values.append(val)
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=values,
                mode='lines',
                name=f"{COUNTRIES[geo]['flag']} {COUNTRIES[geo]['name']}",
                line=dict(width=2)
            ))
    
    fig.update_layout(
        title=f"Comparativa de tendencias: {brand}",
        xaxis_title="Fecha",
        yaxis_title="Interés (0-100)",
        hovermode='x unified',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

# Función para extraer datos de queries clasificados
def extract_queries_by_type(queries_data):
    """Extrae y clasifica queries en: todo, preguntas, atributos"""
    
    if not queries_data or 'related_queries' not in queries_data:
        return None, None, None
    
    all_queries = []
    questions = []
    attributes = []
    
    # Palabras clave para identificar preguntas
    question_words = ['qué', 'cómo', 'cuál', 'cuáles', 'dónde', 'cuándo', 'por qué', 'quién', 
                      'what', 'how', 'which', 'where', 'when', 'why', 'who']
    
    # TOP queries
    if 'top' in queries_data['related_queries']:
        for item in queries_data['related_queries']['top']:
            query = item.get('query', '').lower()
            all_queries.append(item)
            
            # Clasificar
            is_question = any(qw in query for qw in question_words)
            
            if is_question:
                questions.append(item)
            else:
                # Atributos son queries que no son preguntas
                attributes.append(item)
    
    # RISING queries
    if 'rising' in queries_data['related_queries']:
        for item in queries_data['related_queries']['rising']:
            query = item.get('query', '').lower()
            
            is_question = any(qw in query for qw in question_words)
            
            if is_question and item not in questions:
                questions.append(item)
            elif not is_question and item not in attributes:
                attributes.append(item)
    
    return all_queries, questions, attributes

# Interfaz principal
if uploaded_file is not None:
    # Leer CSV
    df = pd.read_csv(uploaded_file)
    
    st.success(f"✅ CSV cargado: {len(df)} marcas encontradas")
    
    # Mostrar preview del CSV
    with st.expander("👀 Preview de marcas"):
        st.dataframe(df.head(10))
    
    # Verificar que existe columna "Brand"
    if 'Brand' not in df.columns:
        st.error("❌ El CSV debe tener una columna llamada 'Brand'")
        st.stop()
    
    # Selector de marca individual o análisis masivo
    analysis_mode = st.radio(
        "Modo de análisis:",
        ["📊 Marca individual", "🚀 Análisis masivo (todas las marcas)"],
        horizontal=True
    )
    
    if analysis_mode == "📊 Marca individual":
        # Análisis de marca individual
        selected_brand = st.selectbox("Selecciona una marca:", df['Brand'].tolist())
        
        if st.button("🔍 Analizar marca", type="primary"):
            results = analyze_brand(selected_brand, selected_countries)
            
            # Mostrar resultados
            st.markdown(f"## 📈 Resultados para: **{selected_brand}**")
            
            # Si hay múltiples países, mostrar comparativa
            if len(selected_countries) > 1:
                st.markdown("### 📊 Comparativa entre países")
                
                # Gráfico comparativo
                fig = show_comparative_chart(selected_brand, results)
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabla comparativa de métricas
                st.markdown("### 📊 Métricas comparativas")
                
                comparison_data = []
                for geo, data in results.items():
                    comparison_data.append({
                        'País': f"{COUNTRIES[geo]['flag']} {COUNTRIES[geo]['name']}",
                        '% Cambio Mes': f"{data['month_change']:.1f}%" if data['month_change'] is not None else "N/A",
                        '% Cambio Quarter': f"{data['quarter_change']:.1f}%" if data['quarter_change'] is not None else "N/A",
                        '% Cambio Año': f"{data['year_change']:.1f}%" if data['year_change'] is not None else "N/A",
                        'Promedio 5 años': f"{data['avg_value']:.1f}" if data['avg_value'] is not None else "N/A"
                    })
                
                comparison_df = pd.DataFrame(comparison_data)
                st.dataframe(comparison_df, use_container_width=True)
            
            # Mostrar detalles por país
            for geo, data in results.items():
                country_name = f"{COUNTRIES[geo]['flag']} {COUNTRIES[geo]['name']}"
                
                with st.expander(f"📍 Detalles: {country_name}", expanded=(len(selected_countries) == 1)):
                    
                    # Métricas
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if data['month_change'] is not None:
                            st.metric(
                                "Cambio último mes",
                                f"{data['month_change']:.1f}%",
                                delta=f"{data['month_change']:.1f}%"
                            )
                        else:
                            st.metric("Cambio último mes", "N/A")
                    
                    with col2:
                        if data['quarter_change'] is not None:
                            st.metric(
                                "Cambio último quarter",
                                f"{data['quarter_change']:.1f}%",
                                delta=f"{data['quarter_change']:.1f}%"
                            )
                        else:
                            st.metric("Cambio último quarter", "N/A")
                    
                    with col3:
                        if data['year_change'] is not None:
                            st.metric(
                                "Cambio último año",
                                f"{data['year_change']:.1f}%",
                                delta=f"{data['year_change']:.1f}%"
                            )
                        else:
                            st.metric("Cambio último año", "N/A")
                    
                    with col4:
                        if data['avg_value'] is not None:
                            st.metric(
                                "Promedio 5 años",
                                f"{data['avg_value']:.1f}"
                            )
                        else:
                            st.metric("Promedio 5 años", "N/A")
                    
                    # Gráfico individual si solo hay un país
                    if len(selected_countries) == 1 and data['timeline'] and 'interest_over_time' in data['timeline']:
                        st.markdown("#### 📊 Tendencia de búsquedas (5 años)")
                        
                        timeline = data['timeline']['interest_over_time']['timeline_data']
                        
                        dates = []
                        values = []
                        
                        for point in timeline:
                            dates.append(point['date'])
                            val = point['values'][0]['extracted_value'] if point['values'] else 0
                            values.append(val)
                        
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatter(
                            x=dates,
                            y=values,
                            mode='lines',
                            name=selected_brand,
                            line=dict(color='#FF6B00', width=2),
                            fill='tozeroy',
                            fillcolor='rgba(255, 107, 0, 0.1)'
                        ))
                        
                        fig.update_layout(
                            title=f"Interest Over Time - {selected_brand}",
                            xaxis_title="Fecha",
                            yaxis_title="Interés (0-100)",
                            hovermode='x unified',
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Related Queries con clasificación
                    if data['queries']:
                        st.markdown("#### 🔎 Búsquedas Relacionadas")
                        
                        # Extraer y clasificar queries
                        all_q, questions, attributes = extract_queries_by_type(data['queries'])
                        
                        # Tabs para diferentes vistas
                        tab1, tab2, tab3, tab4 = st.tabs(["📋 Todo", "❓ Preguntas", "🏷️ Atributos", "📈 Tendencias"])
                        
                        with tab1:
                            col_top, col_rising = st.columns(2)
                            
                            with col_top:
                                st.markdown("**🔝 TOP**")
                                if 'related_queries' in data['queries'] and 'top' in data['queries']['related_queries']:
                                    top_queries = data['queries']['related_queries']['top']
                                    if top_queries:
                                        df_top = pd.DataFrame(top_queries[:10])
                                        if 'query' in df_top.columns and 'value' in df_top.columns:
                                            st.dataframe(df_top[['query', 'value']], use_container_width=True, hide_index=True)
                                    else:
                                        st.info("No hay datos disponibles")
                                else:
                                    st.info("No hay datos disponibles")
                            
                            with col_rising:
                                st.markdown("**📈 RISING**")
                                if 'related_queries' in data['queries'] and 'rising' in data['queries']['related_queries']:
                                    rising_queries = data['queries']['related_queries']['rising']
                                    if rising_queries:
                                        df_rising = pd.DataFrame(rising_queries[:10])
                                        if 'query' in df_rising.columns and 'value' in df_rising.columns:
                                            st.dataframe(df_rising[['query', 'value']], use_container_width=True, hide_index=True)
                                    else:
                                        st.info("No hay datos disponibles")
                                else:
                                    st.info("No hay datos disponibles")
                        
                        with tab2:
                            st.markdown("**❓ Preguntas detectadas**")
                            if questions:
                                df_questions = pd.DataFrame(questions[:15])
                                if 'query' in df_questions.columns and 'value' in df_questions.columns:
                                    st.dataframe(df_questions[['query', 'value']], use_container_width=True, hide_index=True)
                            else:
                                st.info("No se detectaron preguntas")
                        
                        with tab3:
                            st.markdown("**🏷️ Atributos y términos relacionados**")
                            if attributes:
                                df_attributes = pd.DataFrame(attributes[:15])
                                if 'query' in df_attributes.columns and 'value' in df_attributes.columns:
                                    st.dataframe(df_attributes[['query', 'value']], use_container_width=True, hide_index=True)
                            else:
                                st.info("No se detectaron atributos")
                        
                        with tab4:
                            st.markdown("**📈 Tendencias emergentes (RISING)**")
                            if 'related_queries' in data['queries'] and 'rising' in data['queries']['related_queries']:
                                rising = data['queries']['related_queries']['rising']
                                if rising:
                                    # Filtrar solo los que tienen growth > 100% o "Breakout"
                                    emerging = []
                                    for item in rising:
                                        value = item.get('value', '')
                                        if 'Breakout' in str(value) or (isinstance(value, (int, float)) and value > 100):
                                            emerging.append(item)
                                    
                                    if emerging:
                                        df_emerging = pd.DataFrame(emerging)
                                        st.dataframe(df_emerging, use_container_width=True, hide_index=True)
                                        st.success(f"🚀 {len(emerging)} tendencias emergentes detectadas")
                                    else:
                                        st.info("No hay tendencias con crecimiento significativo")
                                else:
                                    st.info("No hay datos disponibles")
                            else:
                                st.info("No hay datos disponibles")
                    
                    # Related Topics
                    if data['topics']:
                        st.markdown("#### 🏷️ Temas Relacionados")
                        
                        col_top, col_rising = st.columns(2)
                        
                        with col_top:
                            st.markdown("**🔝 TOP**")
                            if 'related_topics' in data['topics'] and 'top' in data['topics']['related_topics']:
                                top_topics = data['topics']['related_topics']['top']
                                if top_topics:
                                    df_top = pd.DataFrame(top_topics[:10])
                                    st.dataframe(df_top, use_container_width=True, hide_index=True)
                                else:
                                    st.info("No hay datos disponibles")
                            else:
                                st.info("No hay datos disponibles")
                        
                        with col_rising:
                            st.markdown("**📈 RISING**")
                            if 'related_topics' in data['topics'] and 'rising' in data['topics']['related_topics']:
                                rising_topics = data['topics']['related_topics']['rising']
                                if rising_topics:
                                    df_rising = pd.DataFrame(rising_topics[:10])
                                    st.dataframe(df_rising, use_container_width=True, hide_index=True)
                                else:
                                    st.info("No hay datos disponibles")
                            else:
                                st.info("No hay datos disponibles")
    
    else:
        # Análisis masivo
        st.warning("⚠️ **Análisis masivo**: El tiempo de análisis depende del número de marcas y países seleccionados.")
        
        # Calcular estimación de tiempo
        num_brands_slider = st.slider("¿Cuántas marcas quieres analizar?", 1, len(df), min(20, len(df)))
        estimated_time = (num_brands_slider * len(selected_countries) * 3) / 60  # 3 segundos por marca-país
        
        st.info(f"⏱️ **Tiempo estimado**: ~{estimated_time:.1f} minutos para {num_brands_slider} marcas en {len(selected_countries)} país(es)")
        
        if st.button("🚀 Iniciar análisis masivo", type="primary"):
            all_results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, brand in enumerate(df['Brand'].head(num_brands_slider)):
                status_text.text(f"Analizando {idx+1}/{num_brands_slider}: {brand}")
                
                brand_results = analyze_brand(brand, selected_countries)
                
                # Consolidar resultados
                for geo, data in brand_results.items():
                    all_results.append({
                        'Marca': brand,
                        'País': f"{COUNTRIES[geo]['flag']} {COUNTRIES[geo]['name']}",
                        'País_Code': geo,
                        '% Cambio Mes': data['month_change'],
                        '% Cambio Quarter': data['quarter_change'],
                        '% Cambio Año': data['year_change'],
                        'Promedio 5 años': data['avg_value']
                    })
                
                progress_bar.progress((idx + 1) / num_brands_slider)
            
            status_text.text("✅ Análisis completado!")
            
            # Crear DataFrame con resultados
            results_df = pd.DataFrame(all_results)
            
            st.markdown("## 📊 Resultados del Análisis Masivo")
            
            # Filtros
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                filter_country = st.multiselect(
                    "Filtrar por país:",
                    options=results_df['País'].unique(),
                    default=results_df['País'].unique()
                )
            
            with col_filter2:
                sort_by = st.selectbox(
                    "Ordenar por:",
                    ["% Cambio Año", "% Cambio Quarter", "% Cambio Mes", "Promedio 5 años"]
                )
            
            # Aplicar filtros
            filtered_df = results_df[results_df['País'].isin(filter_country)]
            filtered_df = filtered_df.sort_values(by=sort_by, ascending=False)
            
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
            
            # Visualizaciones
            st.markdown("### 📈 Top 15 Marcas por Crecimiento Anual")
            
            # Agrupar por marca si hay múltiples países
            if len(selected_countries) > 1:
                # Promedio por marca
                top_brands = results_df.groupby('Marca')['% Cambio Año'].mean().nlargest(15).reset_index()
            else:
                top_brands = results_df.nlargest(15, '% Cambio Año')[['Marca', '% Cambio Año']]
            
            fig = px.bar(
                top_brands,
                x='% Cambio Año',
                y='Marca',
                orientation='h',
                title='Top 15 Marcas con Mayor Crecimiento Anual',
                labels={'% Cambio Año': 'Cambio (%)', 'Marca': ''},
                color='% Cambio Año',
                color_continuous_scale='RdYlGn'
            )
            
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
            
            # Si hay múltiples países, mostrar comparativa
            if len(selected_countries) > 1:
                st.markdown("### 🌍 Comparativa por País")
                
                avg_by_country = results_df.groupby('País')['% Cambio Año'].mean().reset_index()
                
                fig2 = px.bar(
                    avg_by_country,
                    x='País',
                    y='% Cambio Año',
                    title='Crecimiento Promedio por País',
                    color='% Cambio Año',
                    color_continuous_scale='RdYlGn'
                )
                
                st.plotly_chart(fig2, use_container_width=True)
            
            # Botón de descarga
            csv = results_df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="💾 Descargar resultados completos (CSV)",
                data=csv,
                file_name=f'trend_analysis_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
                mime='text/csv',
            )

else:
    st.info("👆 Por favor, sube un archivo CSV con la columna 'Brand' para comenzar")
    
    # Instrucciones
    st.markdown(f"""
    ### 📋 Formato del CSV
    
    Tu archivo CSV debe tener este formato:
    
    ```
    Brand
    ASUS
    MSI
    Gigabyte
    Corsair
    ...
    ```
    
    ### 🎯 ¿Qué hace esta herramienta?
    
    - 🌍 **Análisis multi-país**: {', '.join([COUNTRIES[c]['name'] for c in COUNTRIES.keys()])}
    - 📊 Tendencias de búsqueda en Google Trends (5 años)
    - 📈 Cambios porcentuales (mes, quarter, año)
    - 🔍 Búsquedas relacionadas clasificadas:
      - 📋 Todo
      - ❓ Preguntas
      - 🏷️ Atributos
      - 📈 Tendencias emergentes
    - 🏷️ Temas relacionados (TOP + RISING)
    - 📊 Comparativas entre países
    - 💾 Exportación completa a CSV
    
    ### ⚙️ Funcionalidades
    
    - ✅ Análisis individual por marca
    - ✅ Análisis masivo con filtros
    - ✅ Gráficos comparativos
    - ✅ Detección de tendencias emergentes
    - ✅ Clasificación automática de queries
    
    ### 🚀 Roadmap próximo
    
    - [ ] Dashboard consolidado con KPIs
    - [ ] Alertas automáticas para marcas emergentes
    - [ ] Análisis de estacionalidad
    - [ ] Integración con Google Sheets
    - [ ] Exportación a PDF con reportes visuales
    """)

# Footer
st.markdown("---")
st.markdown("🔧 Desarrollado para PCComponentes | 🔍 Powered by SerpAPI | Versión 2.0")
