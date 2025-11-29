import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time

# Configuración de la página
st.set_page_config(
    page_title="Trend Hunter - PCComponentes",
    page_icon="🔍",
    layout="wide"
)

# API Key de SerpAPI
SERPAPI_KEY = "282b59f5ce2f8b2b7ddff4fea0c6c5b9bbb35b832ab1db3800be405fa5719094"

# Título principal
st.title("🔍 Trend Hunter - PCComponentes")
st.markdown("### Análisis de tendencias de marcas en Google Trends")

# Sidebar para configuración
st.sidebar.header("⚙️ Configuración")

# Upload CSV
uploaded_file = st.sidebar.file_uploader("📁 Sube tu CSV con marcas", type=['csv'])

# Selector de país (por ahora solo España)
country = st.sidebar.selectbox(
    "🌍 País",
    ["ES"],
    index=0,
    help="Actualmente solo España está disponible"
)

# Mapeo de códigos de país
country_names = {
    "ES": "España"
}

# Función para llamar a SerpAPI - Interest Over Time
def get_interest_over_time(brand, geo="ES"):
    """Obtiene datos de interés a lo largo del tiempo (5 años)"""
    url = "https://serpapi.com/search.json"
    
    params = {
        "engine": "google_trends",
        "q": brand,
        "data_type": "TIMESERIES",
        "date": "today 5-y",  # Últimos 5 años
        "geo": geo,
        "api_key": SERPAPI_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.warning(f"Error en API para {brand}: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error: {e}")
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
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error: {e}")
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
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# Función para calcular cambios porcentuales
def calculate_changes(timeline_data):
    """Calcula % cambio mes, quarter, año"""
    if not timeline_data or 'interest_over_time' not in timeline_data:
        return None, None, None
    
    try:
        values = timeline_data['interest_over_time']['timeline_data']
        
        if len(values) < 12:
            return None, None, None
        
        # Último valor (más reciente)
        current = values[-1]['values'][0]['extracted_value'] if values[-1]['values'] else 0
        
        # Valor hace 1 mes (aproximado - 4 semanas)
        month_ago = values[-5]['values'][0]['extracted_value'] if len(values) >= 5 and values[-5]['values'] else 0
        
        # Valor hace 3 meses (quarter - 12 semanas)
        quarter_ago = values[-13]['values'][0]['extracted_value'] if len(values) >= 13 and values[-13]['values'] else 0
        
        # Valor hace 1 año (52 semanas)
        year_ago = values[-53]['values'][0]['extracted_value'] if len(values) >= 53 and values[-53]['values'] else 0
        
        # Calcular cambios porcentuales
        month_change = ((current - month_ago) / month_ago * 100) if month_ago > 0 else 0
        quarter_change = ((current - quarter_ago) / quarter_ago * 100) if quarter_ago > 0 else 0
        year_change = ((current - year_ago) / year_ago * 100) if year_ago > 0 else 0
        
        return month_change, quarter_change, year_change
    
    except Exception as e:
        st.warning(f"Error calculando cambios: {e}")
        return None, None, None

# Función principal de análisis
def analyze_brand(brand, geo="ES"):
    """Análisis completo de una marca"""
    
    with st.spinner(f'🔎 Analizando {brand} en {country_names[geo]}...'):
        
        # 1. Interest Over Time
        timeline_data = get_interest_over_time(brand, geo)
        time.sleep(1)  # Delay para no saturar la API
        
        # 2. Related Queries
        queries_data = get_related_queries(brand, geo)
        time.sleep(1)
        
        # 3. Related Topics
        topics_data = get_related_topics(brand, geo)
        time.sleep(1)
        
        # Calcular cambios
        month_change, quarter_change, year_change = calculate_changes(timeline_data)
        
        return {
            'brand': brand,
            'timeline': timeline_data,
            'queries': queries_data,
            'topics': topics_data,
            'month_change': month_change,
            'quarter_change': quarter_change,
            'year_change': year_change
        }

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
            result = analyze_brand(selected_brand, country)
            
            # Mostrar resultados
            st.markdown(f"## 📈 Resultados para: **{selected_brand}**")
            
            # Métricas de cambio
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if result['month_change'] is not None:
                    st.metric(
                        "Cambio último mes",
                        f"{result['month_change']:.1f}%",
                        delta=f"{result['month_change']:.1f}%"
                    )
                else:
                    st.metric("Cambio último mes", "N/A")
            
            with col2:
                if result['quarter_change'] is not None:
                    st.metric(
                        "Cambio último quarter",
                        f"{result['quarter_change']:.1f}%",
                        delta=f"{result['quarter_change']:.1f}%"
                    )
                else:
                    st.metric("Cambio último quarter", "N/A")
            
            with col3:
                if result['year_change'] is not None:
                    st.metric(
                        "Cambio último año",
                        f"{result['year_change']:.1f}%",
                        delta=f"{result['year_change']:.1f}%"
                    )
                else:
                    st.metric("Cambio último año", "N/A")
            
            # Gráfico de tendencia (5 años)
            if result['timeline'] and 'interest_over_time' in result['timeline']:
                st.markdown("### 📊 Tendencia de búsquedas (5 años)")
                
                timeline = result['timeline']['interest_over_time']['timeline_data']
                
                dates = []
                values = []
                
                for point in timeline:
                    dates.append(point['date'])
                    val = point['values'][0]['extracted_value'] if point['values'] else 0
                    values.append(val)
                
                # Crear gráfico con Plotly
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=values,
                    mode='lines',
                    name=selected_brand,
                    line=dict(color='#FF6B00', width=2)
                ))
                
                fig.update_layout(
                    title=f"Interest Over Time - {selected_brand}",
                    xaxis_title="Fecha",
                    yaxis_title="Interés (0-100)",
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Related Queries
            if result['queries']:
                st.markdown("### 🔎 Búsquedas Relacionadas")
                
                col_top, col_rising = st.columns(2)
                
                with col_top:
                    st.markdown("#### 🔝 TOP")
                    if 'related_queries' in result['queries'] and 'top' in result['queries']['related_queries']:
                        top_queries = result['queries']['related_queries']['top']
                        if top_queries:
                            df_top = pd.DataFrame(top_queries[:10])
                            st.dataframe(df_top[['query', 'value']], use_container_width=True)
                        else:
                            st.info("No hay datos disponibles")
                    else:
                        st.info("No hay datos disponibles")
                
                with col_rising:
                    st.markdown("#### 📈 RISING")
                    if 'related_queries' in result['queries'] and 'rising' in result['queries']['related_queries']:
                        rising_queries = result['queries']['related_queries']['rising']
                        if rising_queries:
                            df_rising = pd.DataFrame(rising_queries[:10])
                            st.dataframe(df_rising[['query', 'value']], use_container_width=True)
                        else:
                            st.info("No hay datos disponibles")
                    else:
                        st.info("No hay datos disponibles")
            
            # Related Topics
            if result['topics']:
                st.markdown("### 🏷️ Temas Relacionados")
                
                col_top, col_rising = st.columns(2)
                
                with col_top:
                    st.markdown("#### 🔝 TOP")
                    if 'related_topics' in result['topics'] and 'top' in result['topics']['related_topics']:
                        top_topics = result['topics']['related_topics']['top']
                        if top_topics:
                            df_top = pd.DataFrame(top_topics[:10])
                            st.dataframe(df_top[['topic', 'value']], use_container_width=True)
                        else:
                            st.info("No hay datos disponibles")
                    else:
                        st.info("No hay datos disponibles")
                
                with col_rising:
                    st.markdown("#### 📈 RISING")
                    if 'related_topics' in result['topics'] and 'rising' in result['topics']['related_topics']:
                        rising_topics = result['topics']['related_topics']['rising']
                        if rising_topics:
                            df_rising = pd.DataFrame(rising_topics[:10])
                            st.dataframe(df_rising[['topic', 'value']], use_container_width=True)
                        else:
                            st.info("No hay datos disponibles")
                    else:
                        st.info("No hay datos disponibles")
    
    else:
        # Análisis masivo
        st.warning("⚠️ **Análisis masivo**: Con 195 marcas, esto puede tardar ~15-20 minutos.")
        st.info("💡 **Tip**: La API tiene límites. Considera analizar en lotes de 20-30 marcas.")
        
        # Selector de cuántas marcas analizar
        num_brands = st.slider("¿Cuántas marcas quieres analizar?", 1, len(df), 20)
        
        if st.button("🚀 Iniciar análisis masivo", type="primary"):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, brand in enumerate(df['Brand'].head(num_brands)):
                status_text.text(f"Analizando {idx+1}/{num_brands}: {brand}")
                
                result = analyze_brand(brand, country)
                results.append({
                    'Marca': brand,
                    '% Cambio Mes': result['month_change'],
                    '% Cambio Quarter': result['quarter_change'],
                    '% Cambio Año': result['year_change']
                })
                
                progress_bar.progress((idx + 1) / num_brands)
            
            status_text.text("✅ Análisis completado!")
            
            # Crear DataFrame con resultados
            results_df = pd.DataFrame(results)
            
            st.markdown("## 📊 Resultados del Análisis Masivo")
            st.dataframe(results_df, use_container_width=True)
            
            # Gráfico de barras con top marcas por crecimiento
            st.markdown("### 📈 Top 10 Marcas por Crecimiento Anual")
            
            top_growing = results_df.nlargest(10, '% Cambio Año')
            
            fig = px.bar(
                top_growing,
                x='% Cambio Año',
                y='Marca',
                orientation='h',
                title='Top 10 Marcas con Mayor Crecimiento Anual',
                labels={'% Cambio Año': 'Cambio (%)', 'Marca': ''},
                color='% Cambio Año',
                color_continuous_scale='RdYlGn'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Botón de descarga
            csv = results_df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="💾 Descargar resultados (CSV)",
                data=csv,
                file_name=f'trend_analysis_{country}_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
            )

else:
    st.info("👆 Por favor, sube un archivo CSV con la columna 'Brand' para comenzar")
    
    # Instrucciones
    st.markdown("""
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
    
    - 📊 Analiza tendencias de búsqueda en Google Trends
    - 📈 Calcula cambios porcentuales (mes, quarter, año)
    - 🔍 Encuentra búsquedas y temas relacionados
    - 💾 Exporta resultados a CSV
    
    ### ⚙️ Configuración
    
    - Actualmente configurado para **España** (ES)
    - Análisis de los **últimos 5 años**
    - Datos actualizados de Google Trends
    """)

# Footer
st.markdown("---")
st.markdown("🔧 Desarrollado para PCComponentes | 🔍 Powered by SerpAPI")
