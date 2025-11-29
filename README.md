# 🔍 Trend Hunter Pro

**Plataforma de Inteligencia Competitiva para PCComponentes**

Análisis completo de tendencias usando Google Trends API (SerpAPI) con filtrado inteligente por categorías de producto.

---

## ✨ Características

### 📡 **APIs de Google Trends**
- ✅ Interest Over Time (5 años de histórico)
- ✅ Related Queries (TOP + RISING)
- ✅ Related Topics (TOP + RISING)

### 🎯 **Filtrado Inteligente**
- 10 categorías de producto con keywords multiidioma
- Scoring de relevancia (0-100%)
- Clasificación automática: Preguntas vs Atributos
- Badges visuales de relevancia

### 🌍 **Multi-País**
- España 🇪🇸
- Portugal 🇵🇹
- Francia 🇫🇷
- Italia 🇮🇹
- Alemania 🇩🇪

### 🔍 **3 Modos de Búsqueda**
1. **Manual** - Busca cualquier marca o keyword
2. **URL** - Extracción automática desde URL de producto
3. **CSV** - Análisis bulk de múltiples marcas

### 📊 **Métricas**
- Cambio mensual, trimestral y anual (%)
- Promedio 5 años
- Gráficos interactivos (Plotly)
- Visualización temporal completa

### 🎨 **UI/UX Premium**
- Diseño Light Mode estilo Apple
- **Floating footer toolbar** con todos los controles
- Sin sidebar - Máximo espacio para datos
- Glassmorphism & shadows sutiles
- 100% responsive

---

## 🚀 Instalación

```bash
# Clonar repositorio
git clone https://github.com/pablogs91-lang/trend-hunter-pccom.git
cd trend-hunter-pccom

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar app
streamlit run app.py
```

---

## 📋 Requisitos

Ver `requirements.txt`

---

## 🎯 Uso

1. **Configura** en la barra flotante inferior (toolbar):
   - Modo de búsqueda
   - Países
   - Categorías
   - Filtros

2. **Busca** una marca

3. **Analiza** resultados

---

## 🔑 API Key

Necesitas una API key de SerpAPI.

Edita `app.py` línea 346:
```python
SERPAPI_KEY = "tu_api_key_aquí"
```

---

## 👤 Autor

Pablo García - PCComponentes

---

## 📄 Versión

**v6.0** - Floating Footer Toolbar

---

**Desarrollado para PCComponentes | Powered by SerpAPI**
