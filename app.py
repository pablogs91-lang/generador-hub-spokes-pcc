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
# CONFIGURACIÓN Y ESTILOS CUSTOM
# ================================

st.set_page_config(
    page_title="Trend Hunter Pro",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS CUSTOM - APPLE-INSPIRED DESIGN
st.markdown("""
<style>
    /* Importar fuente Inter (similar a San Francisco de Apple) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variables de color - Modo oscuro elegante */
    :root {
        --primary-bg: #0a0a0a;
        --secondary-bg: #1a1a1a;
        --card-bg: rgba(255, 255, 255, 0.05);
        --card-border: rgba(255, 255, 255, 0.1);
        --text-primary: #ffffff;
        --text-secondary: #a0a0a0;
        --accent-orange: #FF6B00;
        --accent-blue: #0A84FF;
        --accent-green: #30D158;
        --accent-red: #FF453A;
        --glass-bg: rgba(255, 255, 255, 0.03);
        --glass-border: rgba(255, 255, 255, 0.08);
    }
    
    /* Reset y fuente global */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* Fondo principal */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
    }
    
    /* Header personalizado */
    .main-header {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FF6B00 0%, #FF8533 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .main-header p {
        color: var(--text-secondary);
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Cards con glassmorphism */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.3);
        border-color: rgba(255, 107, 0, 0.3);
    }
    
    /* Métricas estilo Apple */
    .metric-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: var(--accent-orange);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
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
    
    .metric-delta.positive {
        color: var(--accent-green);
    }
    
    .metric-delta.negative {
        color: var(--accent-red);
    }
    
    /* Botones estilo Apple */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-orange) 0%, #ff8533 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(255, 107, 0, 0.3);
        cursor: pointer;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(255, 107, 0, 0.4);
        background: linear-gradient(135deg, #ff8533 0%, var(--accent-orange) 100%);
    }
    
    /* Inputs elegantes */
    .stTextInput > div > div > input {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        color: var(--text-primary);
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--accent-orange);
        box-shadow: 0 0 0 3px rgba(255, 107, 0, 0.1);
    }
    
    /* Selectbox elegante */
    .stSelectbox > div > div {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
    }
    
    /* Multiselect */
    .stMultiSelect > div > div {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
    }
    
    /* Tabs estilo Apple */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: transparent;
        border-bottom: 1px solid var(--glass-border);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        color: var(--text-secondary);
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--glass-bg);
        color: var(--text-primary);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--glass-bg);
        color: var(--accent-orange) !important;
        border-bottom: 2px solid var(--accent-orange);
    }
    
    /* Expander elegante */
    .streamlit-expanderHeader {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        color: var(--text-primary);
        font-weight: 500;
        padding: 1rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(255, 107, 0, 0.1);
        border-color: var(--accent-orange);
    }
    
    /* DataFrames elegantes */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Sidebar elegante */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f0f 0%, #1a1a1a 100%);
        border-right: 1px solid var(--glass-border);
    }
    
    [data-testid="stSidebar"] h2 {
        color: var(--accent-orange);
        font-weight: 600;
    }
    
    /* Slider estilo Apple */
    .stSlider > div > div > div {
        background: var(--glass-bg);
    }
    
    .stSlider [role="slider"] {
        background: var(--accent-orange);
    }
    
    /* Radio buttons elegantes */
    .stRadio > div {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* Success/Warning/Error messages */
    .stSuccess, .stWarning, .stError, .stInfo {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        padding: 1rem;
        backdrop-filter: blur(20px);
    }
    
    /* Spinner personalizado */
    .stSpinner > div {
        border-color: var(--accent-orange) !important;
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Espaciado mejorado */
    .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }
    
    /* Scrollbar personalizado */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--primary-bg);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--glass-border);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-orange);
    }
    
    /* Animaciones */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .glass-card, .metric-card {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Badge de relevancia */
    .relevance-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    
    .badge-high {
        background: rgba(48, 209, 88, 0.2);
        color: var(--accent-green);
        border: 1px solid rgba(48, 209, 88, 0.3);
    }
    
    .badge-medium {
        background: rgba(255, 204, 0, 0.2);
        color: #FFCC00;
        border: 1px solid rgba(255, 204, 0, 0.3);
    }
    
    .badge-low {
        background: rgba(255, 149, 0, 0.2);
        color: #FF9500;
        border: 1px solid rgba(255, 149, 0, 0.3);
    }
    
    .badge-doubt {
        background: rgba(255, 69, 58, 0.2);
        color: var(--accent-red);
        border: 1px solid rgba(255, 69, 58, 0.3);
    }
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
                    "rgb", "retroiluminado", "gaming keyboard", "clavier", "tastatur"],
        "icon": "⌨️"
    },
    "Ratones": {
        "keywords": ["ratón", "mouse", "mice", "dpi", "sensor", "gaming mouse",
                    "wireless mouse", "inalámbrico", "souris", "maus"],
        "icon": "🖱️"
    },
    "Auriculares": {
        "keywords": ["auriculares", "headset", "headphones", "audio", "micrófono",
                    "microphone", "sonido", "sound", "gaming headset", "casque"],
        "icon": "🎧"
    },
    "Monitores": {
        "keywords": ["monitor", "pantalla", "screen", "display", "hz", "refresh rate",
                    "resolución", "resolution", "4k", "1080p", "1440p"],
        "icon": "🖥️"
    },
    "Periféricos": {
        "keywords": ["periférico", "peripheral", "gaming", "pc", "setup", "rgb", "usb"],
        "icon": "🎮"
    }
}

# ================================
# FUNCIONES API (mantenidas)
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
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def calculate_changes(timeline_data):
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
    except:
        return None, None, None, None

def analyze_brand(brand, countries):
    results = {}
    for geo in countries:
        timeline_data = get_interest_over_time(brand, geo)
        time.sleep(1)
        month_change, quarter_change, year_change, avg_value = calculate_changes(timeline_data)
        
        results[geo] = {
            'country': COUNTRIES[geo]['name'],
            'timeline': timeline_data,
            'month_change': month_change,
            'quarter_change': quarter_change,
            'year_change': year_change,
            'avg_value': avg_value
        }
    return results

def extract_brand_from_url(url):
    try:
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        known_brands = [
            "asus", "msi", "gigabyte", "logitech", "razer", "corsair",
            "hyperx", "steelseries", "roccat", "cooler master"
        ]
        
        for brand in known_brands:
            if brand in path:
                if brand == "asus":
                    return "ASUS"
                elif brand == "msi":
                    return "MSI"
                elif brand == "hyperx":
                    return "HyperX"
                else:
                    return brand.title()
        
        parts = path.split('/')
        for part in parts:
            if part and len(part) > 2:
                common_words = ['producto', 'product', 'item']
                if part not in common_words:
                    cleaned = part.replace('-', ' ').title()
                    return cleaned.split()[0] if cleaned else None
        
        return None
    except:
        return None

# ================================
# COMPONENTES UI REUTILIZABLES
# ================================

def render_metric_card(label, value, delta=None, delta_color="neutral"):
    """Renderiza una métrica estilo Apple"""
    delta_class = "positive" if delta and delta > 0 else "negative" if delta and delta < 0 else ""
    delta_symbol = "↑" if delta and delta > 0 else "↓" if delta and delta < 0 else ""
    
    delta_html = f'<div class="metric-delta {delta_class}">{delta_symbol} {abs(delta):.1f}%</div>' if delta is not None else ""
    
    html = f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """
    return html

def create_trend_chart(dates, values, brand_name, color="#FF6B00"):
    """Crea gráfico de tendencias estilo Apple"""
    fig = go.Figure()
    
    # Línea principal con gradiente
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines',
        name=brand_name,
        line=dict(
            color=color,
            width=3,
            shape='spline'
        ),
        fill='tozeroy',
        fillcolor=f'rgba(255, 107, 0, 0.1)',
        hovertemplate='<b>%{y}</b><br>%{x}<extra></extra>'
    ))
    
    # Estilo Apple
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family='Inter, -apple-system, BlinkMacSystemFont, sans-serif',
            color='#ffffff',
            size=12
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.05)',
            zeroline=False,
            showline=False,
            title=None
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.05)',
            zeroline=False,
            showline=False,
            title=None,
            range=[0, max(values) * 1.1] if values else [0, 100]
        ),
        hovermode='x unified',
        height=350,
        margin=dict(l=0, r=0, t=30, b=0),
        hoverlabel=dict(
            bgcolor='rgba(0, 0, 0, 0.8)',
            font_size=13,
            font_family='Inter'
        )
    )
    
    return fig

# ================================
# HEADER PRINCIPAL
# ================================

st.markdown("""
<div class="main-header">
    <h1>🔍 Trend Hunter Pro</h1>
    <p>Inteligencia Competitiva para PCComponentes</p>
</div>
""", unsafe_allow_html=True)

# ================================
# SIDEBAR ELEGANTE
# ================================

with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    st.markdown("")
    
    # Modo de búsqueda
    search_mode = st.radio(
        "🔎 Modo de búsqueda",
        ["🔍 Búsqueda manual", "🔗 Desde URL", "📊 Análisis CSV"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Países
    st.markdown("#### 🌍 Países")
    selected_countries = st.multiselect(
        "Selecciona países",
        options=list(COUNTRIES.keys()),
        default=["ES"],
        format_func=lambda x: f"{COUNTRIES[x]['flag']} {COUNTRIES[x]['name']}",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Categorías
    st.markdown("#### 🎯 Categorías")
    selected_categories = st.multiselect(
        "Filtra por categoría",
        options=list(PRODUCT_CATEGORIES.keys()),
        default=["Periféricos"],
        format_func=lambda x: f"{PRODUCT_CATEGORIES[x]['icon']} {x}",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("##### 📊 Versión 4.0 Premium")
    st.markdown("*Diseñado para PCComponentes*")

# ================================
# MODO: BÚSQUEDA MANUAL
# ================================

if search_mode == "🔍 Búsqueda manual":
    
    # Búsqueda con diseño elegante
    col1, col2 = st.columns([4, 1])
    
    with col1:
        search_query = st.text_input(
            "Buscar marca o keyword",
            placeholder="Ej: Logitech, ASUS ROG, Gaming Mouse...",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_button = st.button("🔍 Buscar", type="primary", use_container_width=True)
    
    if search_button and search_query:
        
        # Indicador de carga elegante
        with st.spinner('✨ Analizando tendencias...'):
            results = analyze_brand(search_query, selected_countries)
        
        # Título del resultado
        st.markdown(f"""
        <div class="glass-card">
            <h2 style="margin: 0; font-size: 2rem; color: white;">📊 {search_query}</h2>
            <p style="color: #a0a0a0; margin-top: 0.5rem;">Análisis de tendencias multi-país</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Resultados por país
        for geo, data in results.items():
            country_name = f"{COUNTRIES[geo]['flag']} {COUNTRIES[geo]['name']}"
            
            with st.expander(f"**{country_name}**", expanded=True):
                
                # MÉTRICAS EN GRID
                st.markdown("#### 📈 Métricas Clave")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    value = f"{data['month_change']:.1f}%" if data['month_change'] is not None else "N/A"
                    st.markdown(render_metric_card(
                        "Último Mes",
                        value,
                        data['month_change']
                    ), unsafe_allow_html=True)
                
                with col2:
                    value = f"{data['quarter_change']:.1f}%" if data['quarter_change'] is not None else "N/A"
                    st.markdown(render_metric_card(
                        "Último Quarter",
                        value,
                        data['quarter_change']
                    ), unsafe_allow_html=True)
                
                with col3:
                    value = f"{data['year_change']:.1f}%" if data['year_change'] is not None else "N/A"
                    st.markdown(render_metric_card(
                        "Último Año",
                        value,
                        data['year_change']
                    ), unsafe_allow_html=True)
                
                with col4:
                    value = f"{data['avg_value']:.0f}/100" if data['avg_value'] is not None else "N/A"
                    st.markdown(render_metric_card(
                        "Promedio 5 Años",
                        value
                    ), unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # GRÁFICO DE TENDENCIAS
                if data['timeline'] and 'interest_over_time' in data['timeline']:
                    st.markdown("#### 📊 Tendencia Temporal (5 años)")
                    
                    timeline = data['timeline']['interest_over_time']['timeline_data']
                    dates = [p['date'] for p in timeline]
                    values = [p['values'][0]['extracted_value'] if p['values'] else 0 for p in timeline]
                    
                    fig = create_trend_chart(dates, values, search_query)
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
                else:
                    st.info("📊 No hay datos de tendencias disponibles para este período")

# ================================
# MODO: DESDE URL
# ================================

elif search_mode == "🔗 Desde URL":
    
    st.markdown("#### 🔗 Extraer Marca desde URL")
    
    url_input = st.text_input(
        "Pega la URL del producto",
        placeholder="https://www.pccomponentes.com/logitech-g-pro-x-superlight",
        label_visibility="collapsed"
    )
    
    if url_input:
        extracted_brand = extract_brand_from_url(url_input)
        
        if extracted_brand:
            st.success(f"✅ Marca detectada: **{extracted_brand}**")
            
            if st.button(f"🔍 Analizar {extracted_brand}", type="primary"):
                with st.spinner('✨ Analizando...'):
                    results = analyze_brand(extracted_brand, selected_countries)
                
                # Mostrar resultados (misma lógica que búsqueda manual)
                st.markdown(f"""
                <div class="glass-card">
                    <h2 style="margin: 0;">📊 {extracted_brand}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                for geo, data in results.items():
                    country_name = f"{COUNTRIES[geo]['flag']} {COUNTRIES[geo]['name']}"
                    
                    with st.expander(f"**{country_name}**", expanded=True):
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            value = f"{data['month_change']:.1f}%" if data['month_change'] else "N/A"
                            st.markdown(render_metric_card("Mes", value, data['month_change']), unsafe_allow_html=True)
                        with col2:
                            value = f"{data['quarter_change']:.1f}%" if data['quarter_change'] else "N/A"
                            st.markdown(render_metric_card("Quarter", value, data['quarter_change']), unsafe_allow_html=True)
                        with col3:
                            value = f"{data['year_change']:.1f}%" if data['year_change'] else "N/A"
                            st.markdown(render_metric_card("Año", value, data['year_change']), unsafe_allow_html=True)
                        with col4:
                            value = f"{data['avg_value']:.0f}/100" if data['avg_value'] else "N/A"
                            st.markdown(render_metric_card("Avg 5yr", value), unsafe_allow_html=True)
                        
                        if data['timeline'] and 'interest_over_time' in data['timeline']:
                            st.markdown("<br>", unsafe_allow_html=True)
                            timeline = data['timeline']['interest_over_time']['timeline_data']
                            dates = [p['date'] for p in timeline]
                            values = [p['values'][0]['extracted_value'] if p['values'] else 0 for p in timeline]
                            
                            fig = create_trend_chart(dates, values, extracted_brand)
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.error("❌ No se pudo extraer la marca. Intenta con búsqueda manual.")

# ================================
# MODO: CSV
# ================================

else:
    uploaded_file = st.file_uploader(
        "📁 Sube tu archivo CSV",
        type=['csv'],
        help="El CSV debe tener una columna llamada 'Brand'"
    )
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        st.success(f"✅ **{len(df)} marcas** cargadas correctamente")
        
        if 'Brand' not in df.columns:
            st.error("❌ El CSV debe contener una columna llamada 'Brand'")
            st.stop()
        
        with st.expander("👀 Preview del CSV"):
            st.dataframe(df.head(10), use_container_width=True)
        
        st.markdown("---")
        
        selected_brand = st.selectbox(
            "Selecciona una marca para analizar:",
            df['Brand'].tolist()
        )
        
        if st.button("🔍 Analizar marca", type="primary"):
            with st.spinner(f'✨ Analizando {selected_brand}...'):
                results = analyze_brand(selected_brand, selected_countries)
            
            st.markdown(f"""
            <div class="glass-card">
                <h2 style="margin: 0;">📊 {selected_brand}</h2>
                <p style="color: #a0a0a0; margin-top: 0.5rem;">Análisis detallado de tendencias</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Mostrar resultados...
            for geo, data in results.items():
                country_name = f"{COUNTRIES[geo]['flag']} {COUNTRIES[geo]['name']}"
                
                with st.expander(f"**{country_name}**", expanded=True):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        value = f"{data['month_change']:.1f}%" if data['month_change'] else "N/A"
                        st.markdown(render_metric_card("Mes", value, data['month_change']), unsafe_allow_html=True)
                    with col2:
                        value = f"{data['quarter_change']:.1f}%" if data['quarter_change'] else "N/A"
                        st.markdown(render_metric_card("Quarter", value, data['quarter_change']), unsafe_allow_html=True)
                    with col3:
                        value = f"{data['year_change']:.1f}%" if data['year_change'] else "N/A"
                        st.markdown(render_metric_card("Año", value, data['year_change']), unsafe_allow_html=True)
                    with col4:
                        value = f"{data['avg_value']:.0f}/100" if data['avg_value'] else "N/A"
                        st.markdown(render_metric_card("Promedio", value), unsafe_allow_html=True)
                    
                    if data['timeline'] and 'interest_over_time' in data['timeline']:
                        st.markdown("<br>", unsafe_allow_html=True)
                        timeline = data['timeline']['interest_over_time']['timeline_data']
                        dates = [p['date'] for p in timeline]
                        values = [p['values'][0]['extracted_value'] if p['values'] else 0 for p in timeline]
                        
                        fig = create_trend_chart(dates, values, selected_brand)
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    else:
        # Estado vacío elegante
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 4rem 2rem;">
            <h2 style="color: #a0a0a0; font-weight: 400;">📁 Arrastra tu archivo CSV aquí</h2>
            <p style="color: #606060; margin-top: 1rem;">o usa búsqueda manual para empezar</p>
        </div>
        """, unsafe_allow_html=True)

# ================================
# FOOTER
# ================================

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #606060; font-size: 0.9rem; padding: 2rem 0;">
    🔧 Desarrollado para PCComponentes | 🔍 Powered by SerpAPI<br>
    <span style="color: #404040;">Versión 4.0 Premium - UI/UX Enhanced</span>
</div>
""", unsafe_allow_html=True)
