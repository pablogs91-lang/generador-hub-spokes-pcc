# generador-hub-spokes-pcc
# 🚀 Generador Hub & Spokes - PCComponentes

Herramienta avanzada de generación de contenido técnico con IA para artículos de hardware, IA y PC.

![Status](https://img.shields.io/badge/status-active-success.svg)
![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Características

- 🤖 **IA Claude Sonnet 4.5**: Generación de contenido de alta calidad
- 🔍 **Research automático**: Busca información actualizada de 2025
- 📊 **Sistema de validación**: 9 checks SEO/AEO (C1-C9)
- 🔧 **Correcciones automáticas**: Mejora el contenido iterativamente
- 📝 **Múltiples modos**: Desde cero o desde contenido existente
- 🎯 **40+ arquetipos**: Reviews, guías, comparativas, tutoriales...
- 🎨 **CSS integrado**: Sistema de diseño completo incluido
- 📚 **Historial local**: Guarda tus artículos en el navegador
- 🌐 **Datos en GitHub Raw**: Actualización centralizada sin redeployar

## 🎯 Arquetipos disponibles (40)

### Reviews y análisis
- Review / Análisis de producto
- Análisis retro / consola vintage
- Benchmarks y pruebas

### Comparativas
- Comparativa A vs B
- Comparativa multimodelo (3-5 productos)
- Roundup / Mejores X

### Guías de compra
- Guía de compra por perfil
- Guía de compra por rango de precio
- Build completa / Configuración PC
- Accesorios y complementos esenciales

### Tutoriales
- Guía / How-to
- Guía de iniciación
- Guía de instalación / montaje
- Tutorial: 10 trucos / hacks
- Troubleshooting / Solución de problemas

### Educativos
- Batalla de specs / Decodificador de marketing
- Mitos vs realidad
- Seguridad y privacidad
- Sostenibilidad y consumo energético

[Ver lista completa de 40 arquetipos](data/arquetipos.json)

## 🚀 Uso rápido

### Opción 1: Claude.ai (Recomendado)
1. Ve a [claude.ai](https://claude.ai)
2. Copia el código de `src/HubSpokeGenerator.jsx`
3. Pídele a Claude: "Crea un artifact con este código React"
4. **Cambia `TU-USUARIO` por tu usuario de GitHub** en la línea 15
5. ¡Listo! Usa la herramienta directamente

### Opción 2: Desarrollo local
```bash
# Requisitos: Node.js 18+
git clone https://github.com/pablogs91-lang/generador-hub-spokes-pcc.git
cd generador-hub-spokes-pcc
npm install react lucide-react
npm run dev
```

## 📖 Guía de uso

### Modo: Crear desde cero

1. **Configuración inicial**
   - Selecciona arquetipo (ej: "Review / Análisis de producto")
   - Define categoría (Home, Mobility, Computing, Home Entertainment)
   - Ajusta intención: 0% (informativo) → 100% (transaccional)
   - Elige ciclo de vida del contenido
   - Define título/tema y keywords

2. **Generación de títulos**
   - El sistema busca info actualizada de 2025
   - Genera 5 opciones SEO-optimizadas
   - Selecciona tu favorito

3. **Creación de outline**
   - Research adicional automático
   - Estructura completa con TOC, callouts, tablas
   - Revisable antes de generar HTML

4. **Generación HTML**
   - Artículo completo en 3 bloques
   - Validación automática (9 checks)
   - CSS integrado

5. **Correcciones (opcional)**
   - Corrección automática de checks fallidos
   - Comentarios personalizados
   - Registro detallado de cambios

### Modo: Desde contenido existente

- **Crear nuevo**: Usa contenido como base, busca info actualizada
- **Actualizar existente**: Mejora y actualiza fechas/datos a 2025
- Soporta: TXT, HTML, Markdown, Word

## ✅ Sistema de validación (C1-C9)

| Check | Criterio | Descripción |
|-------|----------|-------------|
| C1 | Cobertura keywords | ≥80% de keywords presentes |
| C2 | Legibilidad | Párrafos ≤140 palabras |
| C3 | Preguntas | ≥8% del contenido |
| C4 | Enlaces internos | Con UTM tracking |
| C5 | Capitalización | Solo primera letra en títulos |
| C6 | Tablas .lt | Formato correcto |
| C7 | CTA dual | 2+ llamadas a la acción |
| C8 | JSON-LD | Schema FAQPage presente |
| C9 | Anti-IA | Sin señales de generación automática |

## 📦 Datos estructurados en GitHub Raw

Todos los datos están centralizados en `/data` para fácil actualización:

- **`arquetipos.json`**: 40 arquetipos completos con metadata
- **`categorias.json`**: 4 categorías con tonos de voz específicos
- **`css-completo.json`**: Estilos base + 5 variantes visuales
- **`plantillas-html.json`**: 10 módulos visuales reutilizables
- **`prompt-base.json`**: Documento maestro del sistema
- **`reglas-validacion.json`**: Criterios C1-C9 con pesos
- **`configuracion.json`**: Variables del sistema y audiencias
- **`prompt-templates.json`**: Templates de prompts reutilizables

### Actualizar datos sin redeployar
```bash
# 1. Edita el JSON en GitHub (botón Edit)
# 2. Cambia lo que necesites
# 3. Commit changes
# 4. ¡Listo! Los cambios están disponibles en segundos

# O desde terminal:
git clone https://github.com/TU-USUARIO/generador-hub-spokes-pcc.git
cd generador-hub-spokes-pcc
nano data/arquetipos.json  # Edita
git add data/arquetipos.json
git commit -m "Añadidos 5 arquetipos nuevos"
git push
```

## 🎨 Características técnicas

### Research automático
- Búsqueda web antes de cada generación
- Verificación de precios 2025
- Benchmarks actualizados
- Contexto temporal correcto

### Anti-detección IA
- Factor de naturalidad configurable (0.0-0.3)
- Variación de longitud de frases
- Sin plantillas rígidas
- Eliminación de marcadores típicos de IA

### Sistema de correcciones
- Análisis de checks fallidos
- Aplicación selectiva de cambios
- Registro detallado
- Comentarios personalizados del usuario

## 📊 Configuración avanzada
```javascript
// Personalizable en la interfaz
{
  length: 'largo',           // corto | medio | largo
  styleVariant: 'neo-cards', // neo-cards | minimal-zen | tech-pro | gaming-edge
  naturalidadFactor: '0.15', // 0.0 (estructurado) - 0.3 (natural)
  audiencia: 'mixta',        // mixta | gamer | consumidor | workstation_pro
  tonoVoz: 'equilibrado'     // Varía según categoría
}
```

## 🔧 Requisitos técnicos

- **Browser**: Chrome/Edge/Firefox moderno
- **Artifact environment**: Claude.ai (recomendado)
- **Desarrollo local**: React 18+, Node 18+
- **API**: Anthropic Claude API (incluida en artifacts)

## 📦 Dependencias
```json
{
  "react": "^18.0.0",
  "lucide-react": "^0.263.1"
}
```

## 🎯 Casos de uso

1. **Redactor SEO**: Genera artículos optimizados rápidamente
2. **Content Manager**: Planifica y estructura contenido técnico
3. **E-commerce**: Crea fichas de producto enriquecidas
4. **Marketing**: Produce landing pages y guías de compra
5. **Tech blogging**: Publica reviews y análisis técnicos

## ⚙️ Instalación y configuración

### Paso 1: Fork o Clone
```bash
git clone https://github.com/pablogs91-lang/generador-hub-spokes-pcc.git
cd generador-hub-spokes-pcc
```

### Paso 2: Configurar tu usuario de GitHub
Edita `src/HubSpokeGenerator.jsx` línea 15:
```javascript
const GITHUB_USER = 'pablogs91-lang'; // ⚠️ Cambia esto por tu usuario
```

### Paso 3: Usar en Claude.ai
1. Copia todo el contenido de `src/HubSpokeGenerator.jsx`
2. Ve a claude.ai
3. Pega: "Crea un artifact con este código React: [pegar código]"
4. ¡Listo!

## 🚦 Roadmap

- [ ] Exportación directa a WordPress/CMS
- [ ] Integración con Google Analytics
- [ ] Templates personalizados por usuario
- [ ] API REST para automatización
- [ ] Plugin para editores CMS
- [ ] Análisis de competencia automático
- [ ] Generación de imágenes con IA
- [ ] Multi-idioma (en-US, de-DE, fr-FR)

## 📄 Licencia

MIT License - Uso libre con atribución

## 🤝 Contribuciones

Las contribuciones son bienvenidas:
1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/mejora`)
3. Commit cambios (`git commit -m 'Add: nueva feature'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Abre un Pull Request

## 📞 Soporte

- Issues: [GitHub Issues](https://github.com/pablogs91-lang/generador-hub-spokes-pcc/issues)
- Documentación: Ver archivos en `/data`

## 🙏 Créditos

Desarrollado para PCComponentes  
Powered by Anthropic Claude Sonnet 4.5

---

**⚠️ Nota importante**: Esta herramienta requiere acceso a Claude.ai o API de Anthropic para funcionar. Los datos se cargan automáticamente desde GitHub Raw.
