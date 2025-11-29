import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import re
from urllib.parse import urlparse

try:
    import plotly.graph_objects as go
    import plotly.express as px
except ImportError:
    import subprocess
    subprocess.check_call(["pip", "install", "--upgrade", "plotly"])
    import plotly.graph_objects as go
    import plotly.express as px

# ================================
# CONFIGURACIÓN Y ESTILOS
# ================================

st.set_page_config(
    page_title="Trend Hunter Pro",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS CUSTOM - LIGHT MODE
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-bg: #ffffff;
        --secondary-bg: #f5f5f7;
        --card-bg: #ffffff;
        --card-border: rgba(0, 0, 0, 0.08);
        --text-primary: #1d1d1f;
        --text-secondary: #6e6e73;
        --text-tertiary: #86868b;
        --accent-orange: #FF6B00;
        --accent-blue: #007AFF;
        --accent-green: #34C759;
        --accent-red: #FF3B30;
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.04);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.08);
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.12);
    }
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
    }
    
    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #f5f5f7 100%);
    }
    
    .main-header {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 24px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-lg);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FF6B00 0%, #FF8533 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .main-header p {
        color: var(--text-secondary);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    .glass-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
    }
    
    .metric-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-color: var(--accent-orange);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0.5rem 0;
    }
    
    .metric-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-delta {
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .metric-delta.positive { color: var(--accent-green); }
    .metric-delta.negative { color: var(--accent-red); }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-orange) 0%, #ff8533 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(255, 107, 0, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(255, 107, 0, 0.4);
    }
    
    .stTextInput > div > div > input {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        color: var(--text-primary);
        padding: 0.75rem 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--accent-orange);
        box-shadow: 0 0 0 3px rgba(255, 107, 0, 0.1);
        outline: none;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: var(--text-tertiary);
    }
    
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* FLOATING FOOTER - Barra de herramientas flotante abajo */
    .floating-toolbar {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-top: 1px solid var(--card-border);
        box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.12);
        padding: 1rem 2rem;
        z-index: 9999;
        animation: slideUp 0.3s ease-out;
    }
    
    @keyframes slideUp {
        from {
            transform: translateY(100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    /* Ajustar padding del contenido para que no quede tapado */
    .main .block-container {
        padding-bottom: 140px !important;
    }
    
    /* Compact multiselect tags */
    .stMultiSelect [data-baseweb="tag"] {
        margin: 2px;
        font-size: 0.8rem;
        padding: 0.2rem 0.5rem;
    }
    
    /* Compact selectbox */
    .stSelectbox select {
        font-size: 0.9rem;
        padding: 0.5rem;
    }
    
    /* Slider más compacto */
    .stSlider {
        padding-top: 0.25rem;
    }
    
    /* Labels más pequeños en toolbar */
    .stSelectbox label,
    .stMultiSelect label,
    .stSlider label {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Chips/Pills para categorías */
    .category-chip {
        display: inline-block;
        background: var(--secondary-bg);
        border: 1px solid var(--card-border);
        border-radius: 20px;
        padding: 0.4rem 0.8rem;
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--text-primary);
        margin: 0.25rem;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .category-chip:hover {
        background: var(--accent-orange);
        color: white;
        border-color: var(--accent-orange);
    }
    
    .category-chip.selected {
        background: var(--accent-orange);
        color: white;
        border-color: var(--accent-orange);
    }
    
    /* Country flags */
    .country-flag {
        font-size: 1.5rem;
        cursor: pointer;
        opacity: 0.3;
        transition: all 0.2s ease;
        margin: 0 0.25rem;
    }
    
    .country-flag:hover {
        opacity: 1;
        transform: scale(1.2);
    }
    
    .country-flag.selected {
        opacity: 1;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        border-bottom: 1px solid var(--card-border);
    }
    
    .stTabs [data-baseweb="tab"] {
        color: var(--text-secondary);
        font-weight: 500;
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--secondary-bg);
        color: var(--text-primary);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--secondary-bg);
        color: var(--accent-orange) !important;
        border-bottom: 2px solid var(--accent-orange);
    }
    
    .streamlit-expanderHeader {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        color: var(--text-primary);
        font-weight: 500;
        padding: 1rem 1.5rem;
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--secondary-bg);
        border-color: var(--accent-orange);
    }
    
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    
    .badge-high {
        background: rgba(52, 199, 89, 0.15);
        color: #248A3D;
        border: 1px solid rgba(52, 199, 89, 0.3);
    }
    
    .badge-medium {
        background: rgba(255, 204, 0, 0.15);
        color: #B38600;
        border: 1px solid rgba(255, 204, 0, 0.3);
    }
    
    .badge-low {
        background: rgba(255, 149, 0, 0.15);
        color: #C66900;
        border: 1px solid rgba(255, 149, 0, 0.3);
    }
    
    .badge-doubt {
        background: rgba(255, 59, 48, 0.15);
        color: #D70015;
        border: 1px solid rgba(255, 59, 48, 0.3);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================================
# CONFIGURACIÓN
# ================================

SERPAPI_KEY = "282b59f5ce2f8b2b7ddff4fea0c6c5b9bbb35b832ab1db3800be405fa5719094"

COUNTRIES = {
    "ES": {"name": "España", "flag": "🇪🇸"},
    "PT": {"name": "Portugal", "flag": "🇵🇹"},
    "FR": {"name": "Francia", "flag": "🇫🇷"},
    "IT": {"name": "Italia", "flag": "🇮🇹"},
    "DE": {"name": "Alemania", "flag": "🇩🇪"}
}

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
                    "kopfhörer", "7.1", "surround", "noise cancelling"],
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
                    "reposabrazos", "armrest", "reclinable", "ergonómica", "ergonomic"],
        "icon": "🪑"
    },
    "Periféricos": {
        "keywords": ["periférico", "peripheral", "gaming", "pc", "setup", "escritorio",
                    "accesorio", "accessory", "rgb", "usb", "cable", "wireless"],
        "icon": "🎮"
    },
    "Componentes PC": {
        "keywords": ["gpu", "cpu", "procesador", "gráfica", "graphics card",
                    "ram", "memoria", "placa", "motherboard", "ssd", "nvme", "fuente",
                    "power supply", "refrigeración", "cooling", "ventilador"],
        "icon": "💻"
    },
    "Portátiles": {
        "keywords": ["portátil", "laptop", "notebook", "gaming laptop",
                    "rtx", "gtx", "intel", "amd", "ryzen", "batería"],
        "icon": "💻"
    },
    "Streaming": {
        "keywords": ["webcam", "cámara", "streaming", "capturadora",
                    "capture card", "obs", "twitch", "youtube", "micrófono", "luz"],
        "icon": "📹"
    },
    "Alfombrillas": {
        "keywords": ["alfombrilla", "mousepad", "desk mat", "rgb mousepad",
                    "extended", "xl", "superficie"],
        "icon": "🔲"
    }
}

# ================================
# FUNCIONES API
# ================================

def get_interest_over_time(brand, geo="ES"):
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
        return response.json() if response.status_code == 200 else None
    except:
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
        return response.json() if response.status_code == 200 else None
    except:
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
        return response.json() if response.status_code == 200 else None
    except:
        return None

def calculate_changes(timeline_data):
    if not timeline_data or 'interest_over_time' not in timeline_data:
        return None, None, None, None
    
    try:
        values = timeline_data['interest_over_time']['timeline_data']
        if len(values) < 12:
            return None, None, None, None
        
        all_values = [p['values'][0].get('extracted_value', 0) 
                     for p in values if p.get('values')]
        
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
    except:
        return None, None, None, None

def calculate_relevance(query, categories):
    """Calcula relevancia de query vs categorías seleccionadas"""
    if not categories:
        return 100, [], "N/A"
    
    query_lower = query.lower()
    max_score = 0
    best_matches = []
    best_category = ""
    
    for category in categories:
        keywords = PRODUCT_CATEGORIES[category]["keywords"]
        matches = [kw for kw in keywords if kw.lower() in query_lower]
        
        if matches:
            score = (len(matches) / len(keywords)) * 100
            important_matches = [kw for kw in keywords[:5] if kw.lower() in query_lower]
            if important_matches:
                score += 20
            score = min(score, 100)
            
            if score > max_score:
                max_score = score
                best_matches = matches
                best_category = category
    
    return max_score, best_matches, best_category

def get_relevance_badge(score):
    if score >= 80:
        return "🟢 Alto", "badge-high"
    elif score >= 50:
        return "🟡 Medio", "badge-medium"
    elif score >= 30:
        return "🟠 Bajo", "badge-low"
    else:
        return "🔴 Dudoso", "badge-doubt"

def classify_query_type(query):
    """Clasifica si es pregunta o atributo"""
    question_words = ["qué", "cuál", "cómo", "dónde", "cuándo", "quién", "por qué",
                     "what", "how", "where", "when", "why", "which", "who"]
    
    query_lower = query.lower()
    is_question = any(word in query_lower for word in question_words)
    
    return "❓ Pregunta" if is_question else "🏷️ Atributo"

def extract_brand_from_url(url):
    try:
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        known_brands = ["asus", "msi", "gigabyte", "logitech", "razer", "corsair",
                       "hyperx", "steelseries", "roccat", "cooler master", "keychron"]
        
        for brand in known_brands:
            if brand in path:
                return brand.title() if brand not in ["msi", "asus", "hyperx"] else brand.upper()
        
        parts = path.split('/')
        for part in parts:
            if part and len(part) > 2:
                return part.replace('-', ' ').title().split()[0]
        return None
    except:
        return None

def analyze_brand(brand, countries, categories, threshold):
    """Análisis completo con todas las APIs"""
    results = {}
    
    for geo in countries:
        with st.spinner(f'🔎 Analizando {brand} en {COUNTRIES[geo]["name"]}...'):
            timeline = get_interest_over_time(brand, geo)
            time.sleep(1)
            
            queries = get_related_queries(brand, geo)
            time.sleep(1)
            
            topics = get_related_topics(brand, geo)
            time.sleep(1)
            
            month_change, quarter_change, year_change, avg_value = calculate_changes(timeline)
            
            results[geo] = {
                'country': COUNTRIES[geo]['name'],
                'timeline': timeline,
                'queries': queries,
                'topics': topics,
                'month_change': month_change,
                'quarter_change': quarter_change,
                'year_change': year_change,
                'avg_value': avg_value
            }
    
    return results

# ================================
# COMPONENTES UI
# ================================

def render_metric_card(label, value, delta=None):
    delta_class = "positive" if delta and delta > 0 else "negative" if delta and delta < 0 else ""
    delta_symbol = "↑" if delta and delta > 0 else "↓" if delta and delta < 0 else ""
    delta_html = f'<div class="metric-delta {delta_class}">{delta_symbol} {abs(delta):.1f}%</div>' if delta is not None else ""
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """

def create_trend_chart(dates, values, brand_name):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates, y=values,
        mode='lines',
        name=brand_name,
        line=dict(color='#FF6B00', width=3, shape='spline'),
        fill='tozeroy',
        fillcolor='rgba(255, 107, 0, 0.08)',
        hovertemplate='<b>%{y}</b><br>%{x}<extra></extra>'
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(255, 255, 255, 0)',
        plot_bgcolor='rgba(255, 255, 255, 0)',
        font=dict(family='Inter', color='#1d1d1f', size=12),
        xaxis=dict(showgrid=True, gridcolor='rgba(0, 0, 0, 0.05)', title=None, color='#6e6e73'),
        yaxis=dict(showgrid=True, gridcolor='rgba(0, 0, 0, 0.05)', title=None, 
                  range=[0, max(values) * 1.1] if values else [0, 100], color='#6e6e73'),
        hovermode='x unified',
        height=350,
        margin=dict(l=0, r=0, t=30, b=0),
        hoverlabel=dict(bgcolor='rgba(0, 0, 0, 0.85)', font_color='white')
    )
    
    return fig

def display_queries_filtered(queries_data, categories, threshold, query_type="all"):
    """Muestra queries filtradas por categoría y tipo"""
    if not queries_data:
        st.info("No hay datos de queries disponibles")
        return
    
    all_queries = []
    
    # TOP queries
    if 'top' in queries_data.get('related_queries', {}):
        for item in queries_data['related_queries']['top']:
            query = item.get('query', '')
            value = item.get('value', 0)
            score, matches, cat = calculate_relevance(query, categories)
            qtype = classify_query_type(query)
            
            if score >= threshold:
                if query_type == "all" or query_type in qtype:
                    badge, badge_class = get_relevance_badge(score)
                    all_queries.append({
                        'Query': query,
                        'Tipo': qtype,
                        'Valor': value,
                        'Relevancia': f'{score:.0f}%',
                        'Badge': badge,
                        'Categoría': cat,
                        'Keywords': ', '.join(matches[:3])
                    })
    
    # RISING queries
    if 'rising' in queries_data.get('related_queries', {}):
        for item in queries_data['related_queries']['rising']:
            query = item.get('query', '')
            value = item.get('value', 'Breakout')
            score, matches, cat = calculate_relevance(query, categories)
            qtype = classify_query_type(query)
            
            if score >= threshold:
                if query_type == "all" or query_type in qtype:
                    badge, badge_class = get_relevance_badge(score)
                    all_queries.append({
                        'Query': query,
                        'Tipo': qtype,
                        'Valor': f'+{value}' if isinstance(value, int) else value,
                        'Relevancia': f'{score:.0f}%',
                        'Badge': badge,
                        'Categoría': cat,
                        'Keywords': ', '.join(matches[:3])
                    })
    
    if all_queries:
        df = pd.DataFrame(all_queries)
        st.dataframe(df, use_container_width=True, height=400)
        st.caption(f"📊 Total: **{len(all_queries)}** queries filtradas")
    else:
        st.warning(f"No hay queries con relevancia ≥ {threshold}%")

# ================================
# HEADER
# ================================

st.markdown("""
<div class="main-header">
    <h1>🔍 Trend Hunter Pro</h1>
    <p>Inteligencia Competitiva con Análisis Completo de Google Trends</p>
</div>
""", unsafe_allow_html=True)

# ================================
# FLOATING FOOTER TOOLBAR
# ================================

# Contenedor para la toolbar flotante
toolbar_container = st.container()

with toolbar_container:
    st.markdown('<div class="floating-toolbar">', unsafe_allow_html=True)
    
    # Controles en columnas compactas
    col1, col2, col3, col4, col5 = st.columns([1.2, 2, 2.5, 1.2, 1])
    
    with col1:
        search_mode = st.selectbox(
            "🔎 Modo",
            ["🔍 Manual", "🔗 URL", "📊 CSV"],
            key="search_mode"
        )
    
    with col2:
        selected_countries = st.multiselect(
            "🌍 Países",
            options=list(COUNTRIES.keys()),
            default=["ES"],
            format_func=lambda x: f"{COUNTRIES[x]['flag']} {COUNTRIES[x]['name']}",
            key="countries"
        )
    
    with col3:
        selected_categories = st.multiselect(
            "🎯 Categorías",
            options=list(PRODUCT_CATEGORIES.keys()),
            default=["Periféricos"],
            format_func=lambda x: f"{PRODUCT_CATEGORIES[x]['icon']} {x}",
            key="categories"
        )
    
    with col4:
        relevance_threshold = st.slider(
            "📊 Relevancia",
            min_value=0,
            max_value=100,
            value=30,
            step=10,
            key="threshold"
        )
    
    with col5:
        query_type_filter = st.selectbox(
            "🏷️ Tipo",
            ["Todos", "Preguntas", "Atributos"],
            key="query_type"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ================================
# BÚSQUEDA MANUAL
# ================================

if search_mode == "🔍 Manual":
    col1, col2 = st.columns([4, 1])
    
    with col1:
        search_query = st.text_input(
            "Marca o keyword",
            placeholder="Ej: Logitech, ASUS ROG, Razer...",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_button = st.button("🔍 Analizar", type="primary", use_container_width=True)
    
    if search_button and search_query and selected_countries:
        results = analyze_brand(search_query, selected_countries, selected_categories, relevance_threshold)
        
        st.markdown(f"""
        <div class="glass-card">
            <h2 style="margin: 0; color: #1d1d1f;">📊 {search_query}</h2>
            <p style="color: #6e6e73; margin-top: 0.5rem;">Análisis completo multi-país</p>
        </div>
        """, unsafe_allow_html=True)
        
        for geo, data in results.items():
            country_name = f"{COUNTRIES[geo]['flag']} {COUNTRIES[geo]['name']}"
            
            with st.expander(f"**{country_name}**", expanded=True):
                # MÉTRICAS
                st.markdown("#### 📈 Métricas Clave")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    val = f"{data['month_change']:.1f}%" if data['month_change'] else "N/A"
                    st.markdown(render_metric_card("Último Mes", val, data['month_change']), unsafe_allow_html=True)
                with col2:
                    val = f"{data['quarter_change']:.1f}%" if data['quarter_change'] else "N/A"
                    st.markdown(render_metric_card("Trimestre", val, data['quarter_change']), unsafe_allow_html=True)
                with col3:
                    val = f"{data['year_change']:.1f}%" if data['year_change'] else "N/A"
                    st.markdown(render_metric_card("Año", val, data['year_change']), unsafe_allow_html=True)
                with col4:
                    val = f"{data['avg_value']:.0f}/100" if data['avg_value'] else "N/A"
                    st.markdown(render_metric_card("Promedio 5Y", val), unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # GRÁFICO
                if data['timeline'] and 'interest_over_time' in data['timeline']:
                    st.markdown("#### 📊 Tendencia Temporal (5 años)")
                    timeline = data['timeline']['interest_over_time']['timeline_data']
                    dates = [p['date'] for p in timeline]
                    values = [p['values'][0]['extracted_value'] if p['values'] else 0 for p in timeline]
                    fig = create_trend_chart(dates, values, search_query)
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
                # TABS PARA QUERIES Y TOPICS
                tab1, tab2, tab3 = st.tabs(["🔍 Queries Filtradas", "📑 Related Topics", "🔥 Trending"])
                
                with tab1:
                    st.markdown("#### Búsquedas Relacionadas (Filtradas)")
                    qtype_map = {
                        "Todos": "all",
                        "Preguntas": "❓ Pregunta",
                        "Atributos": "🏷️ Atributo"
                    }
                    display_queries_filtered(data['queries'], selected_categories, 
                                            relevance_threshold, qtype_map[query_type_filter])
                
                with tab2:
                    if data['topics'] and 'related_topics' in data['topics']:
                        st.markdown("#### 🔝 Top Topics")
                        if 'top' in data['topics']['related_topics']:
                            topics_list = []
                            for t in data['topics']['related_topics']['top'][:10]:
                                topics_list.append({
                                    'Topic': t.get('topic', {}).get('title', 'N/A'),
                                    'Tipo': t.get('topic', {}).get('type', 'N/A'),
                                    'Valor': t.get('value', 0)
                                })
                            if topics_list:
                                st.dataframe(pd.DataFrame(topics_list), use_container_width=True)
                    else:
                        st.info("No hay topics disponibles")
                
                with tab3:
                    if data['queries'] and 'related_queries' in data['queries']:
                        if 'rising' in data['queries']['related_queries']:
                            st.markdown("#### 🔥 Queries en Tendencia (Rising)")
                            rising = data['queries']['related_queries']['rising'][:15]
                            rising_list = []
                            for q in rising:
                                rising_list.append({
                                    'Query': q.get('query', ''),
                                    'Crecimiento': q.get('value', 'Breakout')
                                })
                            if rising_list:
                                st.dataframe(pd.DataFrame(rising_list), use_container_width=True)
                    else:
                        st.info("No hay datos de tendencias")

elif search_mode == "🔗 URL":
    st.markdown("#### 🔗 Extraer Marca desde URL")
    url_input = st.text_input(
        "URL del producto",
        placeholder="https://www.pccomponentes.com/logitech-g-pro-x-superlight",
        label_visibility="collapsed"
    )
    
    if url_input:
        brand = extract_brand_from_url(url_input)
        if brand:
            st.success(f"✅ Marca detectada: **{brand}**")
            if st.button(f"🔍 Analizar {brand}", type="primary"):
                # Misma lógica que búsqueda manual
                pass
        else:
            st.error("❌ No se pudo extraer la marca")

else:  # CSV
    uploaded_file = st.file_uploader("📁 Sube tu CSV", type=['csv'])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ **{len(df)} marcas** cargadas")
        
        if 'Brand' in df.columns:
            selected_brand = st.selectbox("Selecciona marca:", df['Brand'].tolist())
            if st.button("🔍 Analizar", type="primary"):
                # Misma lógica que búsqueda manual
                pass
        else:
            st.error("❌ El CSV debe tener columna 'Brand'")

# FOOTER
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #86868b; font-size: 0.85rem; padding: 1.5rem 0; margin-top: 3rem; border-top: 1px solid var(--card-border);">
    <span style="color: #6e6e73;">🔧 PCComponentes | 🔍 SerpAPI | v5.0 Complete</span>
</div>
""", unsafe_allow_html=True)
