# Will Sports — Custom Kit Studio · Handoff
**Fecha última actualización:** 23 Mayo 2026  
**Estado:** En progreso activo

---

## ¿Qué es este proyecto?

Diseñador web de camisetas de fútbol para **Will Sports Sportswear** — página standalone en vanilla HTML/CSS/JS + React CDN (sin build step). Dark theme cinematográfico. Deploy en Render como static site.

**URL live:** https://disenador-camisetas.onrender.com  
**Repo GitHub:** https://github.com/sebastianlarocca-ops/disenador-camisetas

---

## Archivos en `~/Desktop/disenador-camisetas/`

| Archivo | Descripción |
|---------|-------------|
| `index.html` | **El diseñador completo** — único archivo, es el que sirve Render |
| `jersey_render.py` | Script Python para Blender — genera los renders |
| `centrar_renders.py` | Post-proceso Pillow: autocrop + recentrado de PNGs |
| `jersey_frente.png` | Render frente Blender (386×386px, fondo transparente) |
| `jersey_dorso.png` | Render dorso Blender (385×385px, fondo transparente) |

> **Workflow de edición:** editar `index.html` → commit → push → Render auto-deploya.  
> ⚠️ `disenador.html` quedó desincronizado — ya no se usa. Todo va en `index.html`.

---

## Stack técnico

- **Vanilla HTML/CSS/JS** — sin dependencias locales, sin build step
- **React 18** via CDN (unpkg) + **Babel standalone** para JSX inline
- **Fuentes:** `Space Grotesk` + `JetBrains Mono` + `Bebas Neue` + `Manrope` — Google Fonts
- **SVG viewBox:** `0 0 400 480`
- **Deploy:** Render Static Site, Publish Directory = `.`, branch `main`

---

## Identidad visual (Will Sports)

| Variable CSS | Valor | Uso |
|---|---|---|
| `--accent` | `#6ABBE0` | Celeste Will Sports — botones, bordes activos, glow |
| `--accent-deep` | `#4A9FC4` | Variante oscura del celeste |
| `--accent-ink` | `#0a1a2e` | Texto sobre fondo celeste |
| Brand mark | navy `#172A46` → `#1B3560` | Fondo del cuadrado "W" |

---

## Arquitectura del diseñador

```
App (React)
├── TopBar         — logo Will Sports (W navy + celeste), nombre proyecto editable, undo/redo, descargar
├── Sidebar (340px) — colapsable, 6 secciones acordeón:
│   ├── 01 Presets de equipo (12 presets)
│   ├── 02 Colores (cuerpo / mangas / cuello / pantalón*)
│   ├── 03 Estilo gráfico (6 estilos)
│   ├── 04 Nombre y número + tipografía del dorsal
│   ├── 05 Tela y construcción (UI only)
│   └── 06 Detalles avanzados (UI only, toggles)
└── Stage (canvas)
    ├── Spotlight reactivo al cursor (CSS vars --cx/--cy)
    ├── View toggle: Frente / Dorso / Comparar
    ├── Jersey component (PNG renders de Blender)
    ├── Favorites strip (derecha, hasta 6, persiste localStorage)
    ├── Floating toolbar (zoom + fullscreen) — oculto en mobile
    ├── CTA Card (precio ARS, talle, cantidad, tela, botón compra)
    └── Hotkeys hint (F/B/C/⌘Z)
```

> *El campo `colors.shorts` existe en el estado pero el pantalón visual fue eliminado. Se puede reactivar con render Blender real.

---

## Técnica de renderizado de la camiseta

El PNG de Blender ES la camiseta. Colorización por zonas via **SVG filters** (`feColorMatrix saturate:0 → feFlood → feBlend multiply → feComposite`):

```
Capa 1 (base):   PNG sin clipPath → color MANGAS
                 Alpha del PNG define la forma — no hay path hardcodeado
Capa 2 (encima): PNG + clip-torso (evenodd) → color CUERPO
Capa 3 (encima): PNG + clip-collar → color CUELLO
Capa 4 (overlay): rect con mask={png-alpha} → patrón de estilo (rayas/banda/etc.)
                  Usa <mask style="maskType:alpha"> con el PNG — sigue la silueta exacta
```

**Eliminados (eran remanentes del SVG viejo):**
- Pantaloncito (`<rect>` sintético con shading)
- Sombra de piso (`<ellipse>`)
- Costura central punteada (`<line>`)
- Placeholder SPONSOR

---

## Zonas de color

| Zona | Mecanismo | Filter ID |
|------|-----------|-----------|
| Cuerpo | `feFlood` en `{p}fb` | `colors.body` |
| Mangas | `feFlood` en `{p}fs` | `colors.sleeves` |
| Cuello | `feFlood` en `{p}fc` | `colors.collar` |
| Pantalón | solo en estado/presets, sin render visual activo | `colors.shorts` |

---

## Jersey component (`function Jersey(...)`)

Props: `view` (front/back), `colors` (body/sleeves/collar/shorts), `style`, `idPrefix`, `name`, `number`, `textColor`, `jerseyFont`

- `idPrefix` único por instancia — evita conflictos en vista "Comparar" (`cmp-f` / `cmp-b`)
- Texto renderizado como SVG `<text>` inline

### Posiciones de texto actuales

| Vista | Elemento | x | y | fontSize |
|-------|----------|---|---|----------|
| Frente | Número (escudo) | 242 | 192 | 28 |
| Dorso | Apellido | 200 | 193 | 30 |
| Dorso | Número | 200 | 290 | 118 |

**Frente:** solo número pequeño en pecho derecho del espectador (= pecho izquierdo del portador), estilo escudo de camiseta de fútbol. Sin apellido en el frente.

---

## Estilos gráficos (6)

| ID | Nombre | Implementación |
|----|--------|---------------|
| `classic` | Liso | sin overlay |
| `stripes-v` | Rayas V | `<pattern>` vertical 32px |
| `stripes-h` | Rayas H | `<pattern>` horizontal 32px |
| `stripes-thin` | Pinstripe | `<pattern>` 14px |
| `sash` | Banda | `<linearGradient>` diagonal |
| `gradient` | Degradé | `<linearGradient>` top-bottom |

El overlay de estilo usa `<rect mask={png-alpha}>` — respeta la silueta exacta del PNG.

---

## CTA Card

- **Desktop:** `position:absolute; bottom:22px; right:90px` — deja libre la tira de favoritos (56px)
- **Mobile ≤880px:** `position:fixed; bottom:0` — barra de compra pegada al fondo, patrón e-commerce estándar
- Botón "Agregar al carrito": ícono SVG acotado a 16px con CSS (`.cta-card .cta-btn svg`)
- "Dry Piqué" (tipo de tela): sin flecha, texto centrado

---

## Breakpoints responsive

| Breakpoint | Cambios clave |
|---|---|
| ≤1380px | Oculta brand-tag |
| ≤1180px | Sidebar colapsada más angosta, oculta status/badges/hotkeys |
| ≤1100px | Oculta favoritos, CTA card 240px |
| ≤980px | Oculta project-meta |
| ≤880px | Layout vertical (topbar/stage/sidebar), CTA fixed al fondo, floating toolbar oculto |
| ≤768px | Brand más chico, botones compactos, sidebar 44vh |
| ≤480px | Oculta brand name (solo mark W), sidebar 40vh, CTA card mínima |

---

## Estado global — Undo/Redo

`useReducer` con `designReducer`. Actions: `SET`, `SET_COLOR`, `APPLY_PRESET`, `UNDO`, `REDO`, `REPLACE`. Historial hasta 30 pasos.

---

## Presets (12)

Argentina · Brasil · Boca · River · Carbon · Lime · Sunset · Mint · Cobalt · Sangre · Pitch · Cream

---

## Tipografías del dorsal (3)

Bebas Neue · Space Grotesk · JetBrains Mono

---

## Keyboard shortcuts

`F` → Frente · `B` → Dorso · `C` → Comparar · `⌘Z` → Undo · `⌘⇧Z` / `⌘Y` → Redo

---

## Download (Descargar PNG)

1. Busca el SVG activo en DOM (`.canvas-cell:not(.compare) .jersey-stage svg`)
2. Clona + serializa con `XMLSerializer`
3. Blob URL → `new Image()` → `drawImage` en `<canvas>` a 2× (800×960px)
4. Fallback SVG si falla el canvas

---

## Deploy en Render

- **Tipo:** Static Site
- **Repo:** `sebastianlarocca-ops/disenador-camisetas`
- **Branch:** `main` — Render auto-deploya en cada push
- **Build Command:** *(vacío)*
- **Publish Directory:** `.`
- **URL:** https://disenador-camisetas.onrender.com

---

## Próximos pasos

1. **[ ] Render Blender de pantalón/shorts** — reemplazar el estado `colors.shorts` con PNG real (misma técnica de filter por zona)
2. **[ ] Subir logo SVG/PNG de Will Sports** — reemplazar el "W" tipográfico en el brand-mark por el isotipo real
3. **[ ] Exportar frente + dorso juntos** — botón que genera imagen combinada
4. **[ ] Dominio custom en Render** — willsports.com o similar

---

## Prompt para continuar

```
Estoy desarrollando un diseñador de camisetas de fútbol para Will Sports Sportswear.
Todos los archivos están en ~/Desktop/disenador-camisetas/
URL live: https://disenador-camisetas.onrender.com
Repo: https://github.com/sebastianlarocca-ops/disenador-camisetas

ESTADO ACTUAL:
- Stack: HTML single-file (index.html), React 18 CDN + Babel standalone, sin build step
- Identidad: Will Sports — celeste #6ABBE0 / navy #172A46, marca "W"
- Jersey: PNG de Blender (jersey_frente.png / jersey_dorso.png, ~386px, fondo transparente)
- Colorización por zonas via SVG filters (saturate:0 → feFlood → multiply → feComposite)
- Capas: mangas (base) → torso (clip evenodd) → cuello (clip) → patrón de estilo (mask PNG alpha)
- Frente: solo número pequeño en pecho izquierdo del portador (escudo)
- Dorso: apellido y número centrado
- Eliminados: pantalón SVG, costura, sombra, sponsor placeholder
- Undo/redo (30 pasos), keyboard shortcuts (F/B/C/⌘Z)
- 12 presets, 6 estilos gráficos, 3 tipografías de dorsal
- Vista Frente / Dorso / Comparar con animación flip
- Favorites strip (localStorage), CTA card precio ARS
- CTA: position:fixed en mobile ≤880px, right:90px en desktop
- Breakpoints: 880px / 768px / 480px
- Deploy: Render Static Site, Publish Directory ".", branch main

ARCHIVOS CLAVE:
- index.html = archivo único de desarrollo Y producción
- jersey_frente.png / jersey_dorso.png = renders de Blender
```
