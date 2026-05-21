# Diseñador de Camisetas — Handoff de sesión
**Fecha:** 21 Mayo 2026  
**Estado:** En progreso activo

---

## ¿Qué es este proyecto?

Diseñador web de camisetas de fútbol — página standalone en vanilla HTML/CSS/JS + React CDN (sin build step). UI tipo "FORMA Custom Kit Studio" — dark theme cinematográfico. Deploy en Render como static site.

**URL live:** https://disenador-camisetas.onrender.com  
**Repo GitHub:** https://github.com/sebastianlarocca-ops/disenador-camisetas

---

## Archivos en `~/Desktop/disenador-camisetas/`

| Archivo | Descripción |
|---------|-------------|
| `disenador.html` | **El diseñador completo** — versión de desarrollo |
| `index.html` | Copia de `disenador.html` — es el que sirve Render (entry point) |
| `jersey_render.py` | Script Python para Blender — genera los renders |
| `centrar_renders.py` | Post-proceso Pillow: autocrop + recentrado de PNGs |
| `jersey_frente.png` | Render frente Blender (386×386px, fondo transparente) |
| `jersey_dorso.png` | Render dorso Blender (385×385px, fondo transparente) |

> **Workflow de edición:** editar `disenador.html` → copiar a `index.html` → commit → push → Render auto-deploya.

---

## Stack técnico

- **Vanilla HTML/CSS/JS** — sin dependencias locales, sin build step
- **React 18** via CDN (unpkg) + **Babel standalone** para JSX inline
- **Fuentes:** `Space Grotesk` + `JetBrains Mono` + `Bebas Neue` + `Manrope` — Google Fonts
- **SVG viewBox:** `0 0 400 480`
- **Deploy:** Render Static Site, Publish Directory = `.`, branch `main`

---

## Arquitectura del diseñador

### UI — FORMA Custom Kit Studio (dark theme)

Diseño implementado a partir del bundle de Claude Design (`Diseñador Premium.html`).

```
App (React)
├── TopBar         — logo FORMA, nombre proyecto editable, undo/redo, descargar
├── Sidebar (340px) — colapsable, 6 secciones acordeón:
│   ├── 01 Presets de equipo (12 presets)
│   ├── 02 Colores (cuerpo / mangas / cuello / pantalón)
│   ├── 03 Estilo gráfico (6 estilos)
│   ├── 04 Nombre y número + tipografía del dorsal
│   ├── 05 Tela y construcción (UI only)
│   └── 06 Detalles avanzados (UI only, toggles)
└── Stage (canvas)
    ├── Spotlight reactivo al cursor (CSS vars --cx/--cy)
    ├── View toggle: Frente / Dorso / Comparar
    ├── Jersey component (PNG renders de Blender)
    ├── Favorites strip (derecha, hasta 6, persiste localStorage)
    ├── Floating toolbar (zoom + fullscreen)
    ├── CTA Card (precio ARS animado, talle, cantidad)
    └── Hotkeys hint (F/B/C/⌘Z)
```

### Técnica de renderizado de la camiseta (ESTADO FINAL)

El PNG de Blender ES la camiseta. La colorización se hace por zonas con **SVG filters** (`feColorMatrix saturate:0 → feFlood → feBlend multiply → feComposite`):

```
Capa 1 (base):   PNG sin clipPath → color MANGAS
                 El alpha transparente del PNG define la forma de las mangas
Capa 2 (encima): PNG + clip-torso (evenodd) → color CUERPO
                 evenodd excluye las zonas de manga
Capa 3 (encima): PNG + clip-collar → color CUELLO
Capa 4 (SVG):    rect sintético debajo del hem → color PANTALÓN
                 Con radialGradient de shading propio (no necesita PNG)
```

**Por qué este orden:** las mangas van sin clipPath para que las puntas redondeadas del render Blender no sean cortadas por los paths angulares del SVG.

### Zonas de color

| Zona | Mecanismo | Filter ID (idPrefix-based) |
|------|-----------|---------------------------|
| Cuerpo | `feFlood` en `{p}fb` | prop `colors.body` |
| Mangas | `feFlood` en `{p}fs` | prop `colors.sleeves` |
| Cuello | `feFlood` en `{p}fc` | prop `colors.collar` |
| Pantalón | SVG `<rect>` fill directo + multiply shading | prop `colors.shorts` |

### Jersey component (`function Jersey(...)`)

Props: `view` (front/back), `colors` (body/sleeves/collar/shorts), `style`, `idPrefix`, `name`, `number`, `textColor`, `jerseyFont`

- `idPrefix` único por instancia para evitar conflictos de ID en vista "Comparar" (donde hay 2 jerseys simultáneos: `cmp-f` y `cmp-b`)
- Texto renderizado como SVG `<text>` inline (no HTML overlay)
- Posiciones del texto:
  - Frente: nombre y=232, número y=310 (fontSize 26/88)
  - Dorso: nombre y=193, número y=338 (fontSize 30/118)

### Estilos gráficos (6)

| ID | Nombre | Implementación |
|----|--------|---------------|
| `classic` | Liso | sin overlay |
| `stripes-v` | Rayas V | SVG `<pattern>` vertical 32px |
| `stripes-h` | Rayas H | SVG `<pattern>` horizontal 32px |
| `stripes-thin` | Pinstripe | SVG `<pattern>` 14px |
| `sash` | Banda | `<linearGradient>` diagonal 42-58% |
| `gradient` | Degradé | `<linearGradient>` top-bottom |

### Estado global — Undo/Redo

`useReducer` con `designReducer`. Actions: `SET`, `SET_COLOR`, `APPLY_PRESET`, `UNDO`, `REDO`, `REPLACE`. Historial de hasta 30 pasos.

### Presets (12)

Argentina, Brasil, Boca, River, Carbon, Lime, Sunset, Mint, Cobalt, Sangre, Pitch, Cream.

### Tipografías del dorsal (3)

Bebas Neue, Space Grotesk, JetBrains Mono — selector visual en la sección "Nombre y número".

### Keyboard shortcuts

`F` → Frente · `B` → Dorso · `C` → Comparar · `⌘Z` → Undo · `⌘⇧Z` / `⌘Y` → Redo

### Download (Descargar PNG)

Función `downloadJersey(view, design, jerseyFontStack)`:
1. Busca el SVG activo en el DOM (query por `.canvas-cell:not(.compare) .jersey-stage svg`)
2. Clona el SVG, lo serializa con `XMLSerializer`
3. Crea Blob URL → `new Image()` → `drawImage` en `<canvas>` a 2× resolución (800×960px)
4. Fallback: descarga como SVG si falla el canvas

---

## Deploy en Render

- **Tipo:** Static Site
- **Repo:** `sebastianlarocca-ops/disenador-camisetas`
- **Branch:** `main`
- **Build Command:** *(vacío)*
- **Publish Directory:** `.`
- **URL:** https://disenador-camisetas.onrender.com

> **Pendiente:** verificar que Publish Directory = `.` esté guardado (el "not found" en `/` fue por esto). Ya funciona en `/index.html`. Hacer Save Changes + Manual Deploy para que `/` también cargue.

---

## Estado de Blender

- PNGs generados con `jersey_render.py` (luces Key/Fill/Rim)
- Post-procesados con `centrar_renders.py` (Pillow) — autocrop + padding 8%
- ✅ `jersey_frente.png` (386×386px) y `jersey_dorso.png` (385×385px) con fondo transparente
- **Pendiente:** render de pantalón/shorts para reemplazar el rect sintético actual

---

## Próximos pasos

1. **[ ] Fix Publish Directory en Render** — poner `.`, Save, redeploy → `/` carga sin `/index.html`
2. **[ ] Render Blender de pantalón/shorts** — reemplazar el `<rect>` sintético con PNG real (misma técnica: filter por zona)
3. **[ ] Workflow de edición** — aclarar que hay que mantener `index.html` sincronizado con `disenador.html` (o unificarlos)
4. **[ ] Eventuales mejoras:** subir escudo/logo propio, exportar frente+dorso juntos, dominio custom en Render

---

## Prompt para continuar

```
Estoy desarrollando un diseñador de camisetas de fútbol en vanilla HTML/CSS/JS + React CDN.
Todos los archivos están en ~/Desktop/disenador-camisetas/
URL live: https://disenador-camisetas.onrender.com
Repo: https://github.com/sebastianlarocca-ops/disenador-camisetas

ESTADO ACTUAL — UI FORMA Custom Kit Studio (dark theme, Claude Design):
- Stack: HTML single-file, React 18 CDN + Babel standalone, sin build step
- Jersey: PNG de Blender (jersey_frente.png / jersey_dorso.png, 386px, fondo transparente)
- Colorización por zonas via SVG filters (feColorMatrix saturate:0 → feFlood → feBlend multiply → feComposite)
- Orden de capas: mangas (base, sin clip) → torso (clip evenodd) → cuello (clip) → pantalón (rect SVG sintético)
- Undo/redo con useReducer (30 pasos), keyboard shortcuts (F/B/C/⌘Z)
- 12 presets, 6 estilos gráficos, 3 tipografías de dorsal
- Vista Frente / Dorso / Comparar con animación flip
- Favorites strip (localStorage), CTA card con precio animado
- Deploy: Render Static Site, Publish Directory ".", branch main

ARCHIVOS CLAVE:
- disenador.html = archivo de desarrollo (editar acá)
- index.html = copia para Render (mantener sincronizado)
- jersey_frente.png / jersey_dorso.png = renders de Blender

PENDIENTE INMEDIATO:
- Fix Publish Directory en Render (guardar "." y redeploy) para que "/" cargue sin /index.html
- Render Blender de pantalón para reemplazar el rect sintético

El usuario tiene Blender instalado y sabe hacer renders básicos.
Proyecto separado de SL Financial Planning (~/Desktop/web.slfinancialplanning.claudecode/).
```
