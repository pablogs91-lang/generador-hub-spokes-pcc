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

# DICCIONARIO DE CATEGORÍAS Y KEYWORDS
PRODUCT_CATEGORIES = {
    "Teclados": {
        "keywords": ["teclado", "keyboard", "tecla", "switch", "mecánico", "mechanical", 
                    "rgb", "retroiluminado", "gaming keyboard", "clavier", "tastatur",
                    "keycap", "hot-swappable", "wireless keyboard", "inalámbrico"],
        "icon": "⌨️"
    },
    "Ratones": {
        "keywords": ["ratón", "mouse", "mice", "dpi", "sensor", "gaming mouse",
                    "wireless mouse", "inalámbrico", "souris", "maus", "polling rate",
                    "botones", "buttons", "scroll", "grip"],
        "icon": "🖱️"
    },
    "Auriculares": {
        "keywords": ["auriculares", "headset", "headphones", "audio", "micrófono",
                    "microphone", "sonido", "sound", "gaming headset", "casque",
                    "kopfhörer", "7.1", "surround", "noise cancelling", "cancelación ruido"],
        "icon": "🎧"
    },
    "Monitores": {
        "keywords": ["monitor", "pantalla", "screen", "display", "hz", "refresh rate",
                    "resolución", "resolution", "4k", "1080p", "1440p", "ultrawide",
                    "curved", "curvo", "ips", "va", "tn", "hdr", "freesync", "g-sync"],
        "icon": "🖥️"
    },
    "Sillas Gaming": {
        "keywords": ["silla", "chair", "gaming chair", "asiento", "respaldo", "lumbar",
                    "reposabrazos", "armrest", "reclinable", "chaise", "stuhl",
                    "ergonómica", "ergonomic", "cojín", "cushion"],
        "icon": "🪑"
    },
    "Periféricos en general": {
        "keywords": ["periférico", "peripheral", "gaming", "pc", "setup", "escritorio",
                    "desk", "accesorio", "accessory", "rgb", "usb", "cable", "wireless"],
        "icon": "🎮"
    },
    "Componentes PC": {
        "keywords": ["gpu", "cpu", "procesador", "processor", "gráfica", "graphics card",
                    "ram", "memoria", "placa", "motherboard", "ssd", "nvme", "fuente",
                    "power supply", "refrigeración", "cooling", "ventilador", "fan"],
        "icon": "💻"
    },
    "Portátiles Gaming": {
        "keywords": ["portátil", "laptop", "notebook", "gaming laptop", "móvil",
                    "ordenador portátil", "rtx", "gtx", "intel", "amd", "ryzen",
                    "pantalla", "batería", "battery"],
        "icon": "💻"
    },
    "Webcams y Streaming": {
        "keywords": ["webcam", "cámara", "camera", "streaming", "stream", "capturadora",
                    "capture card", "1080p", "4k", "obs", "twitch", "youtube",
                    "micrófono", "microphone", "luz", "lighting"],
        "icon": "📹"
    },
    "Alfombrillas": {
        "keywords": ["alfombrilla", "mousepad", "pad", "tapis", "mauspad", "desk mat",
                    "rgb mousepad", "extended", "xl", "superficie", "surface"],
        "icon": "🔲"
    }
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

# NUEVO: Selector de categorías de producto
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Categorías de Producto")
st.sidebar.markdown("*Filtra búsquedas relacionadas por categoría*")

selected_categories = st.sidebar.multiselect(
    "Selecciona categorías objetivo:",
    options=list(PRODUCT_CATEGORIES.keys()),
    default=["Periféricos en general"],
    format_func=lambda x: f"{PRODUCT_CATEGORIES[x]['icon']} {x}"
)

# Umbral de relevancia
relevance_threshold = st.sidebar.slider(
    "📊 Umbral de relevancia mínima (%)",
    min_value=0,
    max_value=100,
    value=30,
    step=10,
    help="Queries con relevancia menor a este % se marcarán como 'Dudosas'"
)

if not selected_countries:
    st.warning("⚠️ Selecciona al menos un país")
    st.stop()

# Función para calcular relevancia de una query respecto a categorías
def calculate_relevance(query, categories):
    """
    Calcula el % de relevancia de una query respecto a las categorías seleccionadas
    Retorna: (relevance_score, matched_keywords, category_matched)
    """
    if not categories:
        return 100, [], "N/A"  # Si no hay categorías, todo es relevante
    
    query_lower = query.lower()
    max_score = 0
    best_matches = []
    best_category = ""
    
    for category in categories:
        keywords = PRODUCT_CATEGORIES[category]["keywords"]
        matches = [kw for kw in keywords if kw.lower() in query_lower]
        
        if matches:
            # Score = % de palabras clave que coinciden
            score = (len(matches) / len(keywords)) * 100
            
            # Bonus si coincide con keywords importantes (primeras 5)
            important_matches = [kw for kw in keywords[:5] if kw.lower() in query_lower]
            if important_matches:
                score += 20
            
            # Limitar a 100
            score = min(score, 100)
            
            if score > max_score:
                max_score = score
                best_matches = matches
                best_category = category
    
    return max_score, best_matches, best_category

def get_relevance_badge(score):
    """Retorna un badge visual según el score de relevancia"""
    if score >= 80:
        return "🟢 Alto", "#28a745"
    elif score >= 50:
        return "🟡 Medio", "#ffc107"
    elif score >= 30:
        return "🟠 Bajo", "#fd7e14"
    else:
        return "🔴 Dudoso", "#dc3545"

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
        return None

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

def calculate_changes(timeline_data):
    """Calcula % cambio mes, quarter, año con más precisión"""
    if not timeline_data or 'interest_over_time' not in timeline_data:
        return None, None, None, None
    
    try:
        values = timeline_data['interest_over_time']['timeline_data']
        
        if len(values) < 12:
            return None, None, None, None
        
        all_values = []
        
        for point in values:
            if point.get('values') and len(point['values']) > 0:
                val = point['values'][0].get('extracted_value', 0)
                all_values.append(val)
        
        if len(all_values) < 12:
            return None, None, None, None
        
        current = all_values[-1]
        month_ago = all_values[-5] if len(all_values) >= 5 else all_values[0]
        quarter_ago = all_values[-13] if len(all_values) >= 13 else all_values[0]
        year_ago = all_values[-52] if len(all_values) >= 52 else all_values[0]
        
        month_change = ((current - month_ago) / month_ago * 100) if month_ago > 0 else 0
        quarter_change = ((current - quarter_ago) / quarter_ago * 100) if quarter_ago > 0 else 0
        year_change = ((current - year_ago) / year_ago * 100) if year_ago > 0 else 0
        avg_value = sum(all_values) / len(all_values) if all_values else 0
        
        return month_change, quarter_change, year_change, avg_value
    
    except Exception as e:
        return None, None, None, None

def analyze_brand(brand, countries):
    """Análisis completo de una marca para múltiples países"""
    
    results = {}
    
    for geo in countries:
        country_name = COUNTRIES[geo]['name']
        
        with st.spinner(f'🔎 Analizando {brand} en {country_name}...'):
            
            timeline_data = get_interest_over_time(brand, geo)
            time.sleep(1)
            
            queries_data = get_related_queries(brand, geo)
            time.sleep(1)
            
            topics_data = get_related_topics(brand, geo)
            time.sleep(1)
            
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

def extract_and_classify_queries(queries_data, categories, threshold):
    """
    Extrae y clasifica queries con filtrado por categoría y relevancia
    Retorna: all_queries, questions, attributes, emerging
    """
    
    if not queries_data or 'related_queries' not in queries_data:
        return [], [], [], []
    
    all_queries = []
    questions = []
    attributes = []
    emerging = []
    
    # Palabras clave para identificar preguntas en múltiples idiomas
    question_words = [
        # Español
        'qué', 'cómo', 'cuál', 'cuáles', 'dónde', 'cuándo', 'por qué', 'quién', 'para qué',
        # Inglés
        'what', 'how', 'which', 'where', 'when', 'why', 'who',
        # Francés
        'quoi', 'comment', 'quel', 'quelle', 'où', 'quand', 'pourquoi', 'qui',
        # Alemán
        'was', 'wie', 'welche', 'wo', 'wann', 'warum', 'wer',
        # Portugués
        'que', 'como', 'qual', 'onde', 'quando', 'por que', 'quem'
    ]
    
    # Procesar TOP queries
    if 'top' in queries_data['related_queries']:
        for item in queries_data['related_queries']['top']:
            query = item.get('query', '')
            query_lower = query.lower()
            
            # Calcular relevancia
            relevance, matches, category = calculate_relevance(query, categories)
            
            # Solo incluir si supera el umbral
            if relevance >= threshold:
                item_with_relevance = {
                    **item,
                    'relevance': relevance,
                    'matched_keywords': matches,
                    'category': category,
                    'badge': get_relevance_badge(relevance)[0],
                    'color': get_relevance_badge(relevance)[1]
                }
                
                all_queries.append(item_with_relevance)
                
                # Clasificar
                is_question = any(qw in query_lower for qw in question_words)
                
                if is_question:
                    questions.append(item_with_relevance)
                else:
                    attributes.append(item_with_relevance)
    
    # Procesar RISING queries (tendencias)
    if 'rising' in queries_data['related_queries']:
        for item in queries_data['related_queries']['rising']:
            query = item.get('query', '')
            value = item.get('value', '')
            
            # Calcular relevancia
            relevance, matches, category = calculate_relevance(query, categories)
            
            # Solo incluir si supera el umbral
            if relevance >= threshold:
                item_with_relevance = {
                    **item,
                    'relevance': relevance,
                    'matched_keywords': matches,
                    'category': category,
                    'badge': get_relevance_badge(relevance)[0],
                    'color': get_relevance_badge(relevance)[1]
                }
                
                # Identificar tendencias emergentes (>100% o Breakout)
                if 'Breakout' in str(value) or (isinstance(value, (int, float)) and value > 100):
                    emerging.append(item_with_relevance)
    
    # Ordenar por relevancia
    all_queries.sort(key=lambda x: x['relevance'], reverse=True)
    questions.sort(key=lambda x: x['relevance'], reverse=True)
    attributes.sort(key=lambda x: x['relevance'], reverse=True)
    emerging.sort(key=lambda x: x['relevance'], reverse=True)
    
    return all_queries, questions, attributes, emerging

def display_queries_table(queries, show_relevance=True):
    """Muestra tabla de queries con relevancia"""
    if not queries:
        st.info("No hay datos disponibles que cumplan el umbral de relevancia")
        return
    
    # Preparar datos para tabla
    table_data = []
    for q in queries:
        row = {
            'Query': q.get('query', ''),
            'Valor': q.get('value', ''),
        }
        
        if show_relevance:
            row['Relevancia'] = f"{q.get('relevance', 0):.0f}%"
            row['Estado'] = q.get('badge', '')
            row['Categoría'] = q.get('category', 'N/A')
        
        table_data.append(row)
    
    df = pd.DataFrame(table_data)
    
    # Aplicar colores según relevancia
    def highlight_relevance(row):
        if 'Estado' in row:
            if '🟢' in row['Estado']:
                return ['background-color: #d4edda'] * len(row)
            elif '🟡' in row['Estado']:
                return ['background-color: #fff3cd'] * len(row)
            elif '🟠' in row['Estado']:
                return ['background-color: #f8d7da'] * len(row)
            elif '🔴' in row['Estado']:
                return ['background-color: #f5c6cb'] * len(row)
        return [''] * len(row)
    
    if show_relevance:
        styled_df = df.style.apply(highlight_relevance, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

# Interfaz principal
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    st.success(f"✅ CSV cargado: {len(df)} marcas encontradas")
    
    with st.expander("👀 Preview de marcas"):
        st.dataframe(df.head(10))
    
    if 'Brand' not in df.columns:
        st.error("❌ El CSV debe tener una columna llamada 'Brand'")
        st.stop()
    
    # Mostrar categorías seleccionadas
    if selected_categories:
        st.info(f"🎯 **Filtrando por**: {', '.join([f'{PRODUCT_CATEGORIES[cat]['icon']} {cat}' for cat in selected_categories])}")
        st.caption(f"📊 Umbral de relevancia: {relevance_threshold}%")
    
    analysis_mode = st.radio(
        "Modo de análisis:",
        ["📊 Marca individual", "🚀 Análisis masivo"],
        horizontal=True
    )
    
    if analysis_mode == "📊 Marca individual":
        selected_brand = st.selectbox("Selecciona una marca:", df['Brand'].tolist())
        
        if st.button("🔍 Analizar marca", type="primary"):
            results = analyze_brand(selected_brand, selected_countries)
            
            st.markdown(f"## 📈 Resultados para: **{selected_brand}**")
            
            # Gráfico comparativo si hay múltiples países
            if len(selected_countries) > 1:
                st.markdown("### 📊 Comparativa entre países")
                fig = show_comparative_chart(selected_brand, results)
                st.plotly_chart(fig, use_container_width=True)
                
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
                st.dataframe(comparison_df, use_container_width=True, hide_index=True)
            
            # Detalles por país
            for geo, data in results.items():
                country_name = f"{COUNTRIES[geo]['flag']} {COUNTRIES[geo]['name']}"
                
                with st.expander(f"📍 Detalles: {country_name}", expanded=(len(selected_countries) == 1)):
                    
                    # Métricas
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if data['month_change'] is not None:
                            st.metric("Cambio último mes", f"{data['month_change']:.1f}%", delta=f"{data['month_change']:.1f}%")
                        else:
                            st.metric("Cambio último mes", "N/A")
                    
                    with col2:
                        if data['quarter_change'] is not None:
                            st.metric("Cambio último quarter", f"{data['quarter_change']:.1f}%", delta=f"{data['quarter_change']:.1f}%")
                        else:
                            st.metric("Cambio último quarter", "N/A")
                    
                    with col3:
                        if data['year_change'] is not None:
                            st.metric("Cambio último año", f"{data['year_change']:.1f}%", delta=f"{data['year_change']:.1f}%")
                        else:
                            st.metric("Cambio último año", "N/A")
                    
                    with col4:
                        if data['avg_value'] is not None:
                            st.metric("Promedio 5 años", f"{data['avg_value']:.1f}")
                        else:
                            st.metric("Promedio 5 años", "N/A")
                    
                    # Gráfico individual
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
                    
                    # BÚSQUEDAS RELACIONADAS CON FILTRADO
                    if data['queries']:
                        st.markdown("#### 🔎 Búsquedas Relacionadas (Filtradas por Categoría)")
                        
                        # Extraer y clasificar
                        all_q, questions, attributes, emerging = extract_and_classify_queries(
                            data['queries'], 
                            selected_categories,
                            relevance_threshold
                        )
                        
                        # Mostrar resumen
                        col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
                        with col_stats1:
                            st.metric("📋 Total", len(all_q))
                        with col_stats2:
                            st.metric("❓ Preguntas", len(questions))
                        with col_stats3:
                            st.metric("🏷️ Atributos", len(attributes))
                        with col_stats4:
                            st.metric("🚀 Emergentes", len(emerging))
                        
                        # Tabs
                        tab1, tab2, tab3, tab4 = st.tabs(["📋 Todo", "❓ Preguntas", "🏷️ Atributos", "🚀 Emergentes"])
                        
                        with tab1:
                            st.markdown("**Todas las búsquedas relacionadas (filtradas)**")
                            display_queries_table(all_q[:20])
                        
                        with tab2:
                            st.markdown("**Preguntas detectadas (filtradas por categoría)**")
                            display_queries_table(questions[:15])
                            
                            if questions:
                                with st.expander("💡 Keywords que coinciden"):
                                    for q in questions[:5]:
                                        if q.get('matched_keywords'):
                                            st.caption(f"**{q['query']}**: {', '.join(q['matched_keywords'][:5])}")
                        
                        with tab3:
                            st.markdown("**Atributos y términos relacionados (filtrados por categoría)**")
                            display_queries_table(attributes[:15])
                            
                            if attributes:
                                with st.expander("💡 Keywords que coinciden"):
                                    for q in attributes[:5]:
                                        if q.get('matched_keywords'):
                                            st.caption(f"**{q['query']}**: {', '.join(q['matched_keywords'][:5])}")
                        
                        with tab4:
                            st.markdown("**Tendencias emergentes (>100% crecimiento, filtradas)**")
                            display_queries_table(emerging)
                            
                            if emerging:
                                st.success(f"🚀 {len(emerging)} tendencias emergentes detectadas")
                            else:
                                st.info("No hay tendencias emergentes que superen el umbral")
                    
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
        st.warning("⚠️ **Análisis masivo**: El tiempo depende del número de marcas y países.")
        
        num_brands_slider = st.slider("¿Cuántas marcas quieres analizar?", 1, len(df), min(20, len(df)))
        estimated_time = (num_brands_slider * len(selected_countries) * 3) / 60
        
        st.info(f"⏱️ **Tiempo estimado**: ~{estimated_time:.1f} minutos para {num_brands_slider} marcas en {len(selected_countries)} país(es)")
        
        if st.button("🚀 Iniciar análisis masivo", type="primary"):
            all_results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, brand in enumerate(df['Brand'].head(num_brands_slider)):
                status_text.text(f"Analizando {idx+1}/{num_brands_slider}: {brand}")
                
                brand_results = analyze_brand(brand, selected_countries)
                
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
            
            results_df = pd.DataFrame(all_results)
            
            st.markdown("## 📊 Resultados del Análisis Masivo")
            
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
            
            filtered_df = results_df[results_df['País'].isin(filter_country)]
            filtered_df = filtered_df.sort_values(by=sort_by, ascending=False)
            
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
            
            # Visualizaciones
            st.markdown("### 📈 Top 15 Marcas por Crecimiento Anual")
            
            if len(selected_countries) > 1:
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
            
            csv = results_df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="💾 Descargar resultados completos (CSV)",
                data=csv,
                file_name=f'trend_analysis_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
                mime='text/csv',
            )

else:
    st.info("👆 Por favor, sube un archivo CSV con la columna 'Brand' para comenzar")
    
    # Instrucciones mejoradas
    st.markdown("""
    ### 🎯 Nueva Funcionalidad: Filtrado por Categoría de Producto
    
    Ahora puedes **filtrar las búsquedas relacionadas** según el tipo de producto que te interesa:
    
    """)
    
    # Mostrar categorías disponibles
    cols = st.columns(3)
    for idx, (cat_name, cat_data) in enumerate(PRODUCT_CATEGORIES.items()):
        with cols[idx % 3]:
            st.markdown(f"**{cat_data['icon']} {cat_name}**")
            st.caption(f"Keywords: {', '.join(cat_data['keywords'][:3])}...")
    
    st.markdown("""
    
    ### 📊 Sistema de Relevancia
    
    Cada query se puntúa según su relevancia a las categorías seleccionadas:
    
    - 🟢 **Alto (80-100%)**: Muy relevante para la categoría
    - 🟡 **Medio (50-79%)**: Relevancia moderada
    - 🟠 **Bajo (30-49%)**: Baja relevancia
    - 🔴 **Dudoso (<30%)**: Posiblemente no relacionado
    
    ### 📋 Formato del CSV
    
    ```
    Brand
    ASUS
    MSI
    Logitech
    ...
    ```
    
    ### 🚀 Próximas funcionalidades
    
    - [ ] Más categorías de producto
    - [ ] Exportación con análisis de relevancia
    - [ ] Alertas para tendencias emergentes relevantes
    - [ ] Dashboard consolidado por categoría
    """)

st.markdown("---")
st.markdown("🔧 Desarrollado para PCComponentes | 🔍 Powered by SerpAPI | Versión 3.0 - Smart Filtering")
