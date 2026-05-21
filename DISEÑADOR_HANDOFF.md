# Diseñador de Camisetas — Handoff de sesión
**Fecha:** 21 Mayo 2026  
**Estado:** En progreso activo

---

## ¿Qué es este proyecto?

Diseñador web de camisetas de fútbol — página standalone en vanilla HTML/CSS/JS, sin frameworks ni build step. Similar en concepto a `dropextra.store/disenadorweb`.

---

## Archivos en `~/Desktop/disenador-camisetas/`

| Archivo | Descripción |
|---------|-------------|
| `disenador.html` | **El diseñador completo** — abrir directo en browser (file://) |
| `jersey_render.py` | Script Python para Blender — genera los renders |
| `centrar_renders.py` | Post-proceso Pillow: autocrop + recentrado de PNGs |
| `jersey_frente.png` | Render frente Blender (386×386px, fondo transparente, listo) |
| `jersey_dorso.png` | Render dorso Blender (385×385px, fondo transparente, listo) |

---

## Arquitectura actual de `disenador.html`

### Stack
- Vanilla HTML/CSS/JS — sin dependencias externas
- Fuentes: `Bebas Neue` + `Inter Tight` — Google Fonts
- SVG inline con viewBox `0 0 400 480`

### Técnica de renderizado (estado final de esta sesión)

El PNG de Blender ES la camiseta. No hay paths SVG de color debajo. La colorización se hace por zonas usando **SVG filters** (`feFlood → feBlend multiply → feComposite`):

```
Capa 1 (base):   PNG jersey_frente.png — SIN clipPath → color MANGAS
                 El alpha transparente del PNG define la forma real de las mangas
Capa 2 (encima): PNG jersey_frente.png — clip-torso (evenodd) → color CUERPO
                 evenodd excluye las zonas de manga del clip del torso
Capa 3 (encima): PNG jersey_frente.png — clip-collar → color CUELLO
```

**Por qué este orden**: las mangas van sin clipPath para que las puntas redondeadas del render Blender no sean cortadas por los paths angulares del SVG. El torso pinta encima y cubre solo la zona del cuerpo.

### Zonas de color
| Zona | Mecanismo | Elemento JS |
|------|-----------|-------------|
| Cuerpo | `feFlood` en `filter-body-f/b` | `flood-body-f`, `flood-body-b` |
| Mangas | `feFlood` en `filter-sleeve-f/b` | `flood-sleeve-f`, `flood-sleeve-b` |
| Cuello | `feFlood` en `filter-collar-f/b` | `flood-collar-f`, `flood-collar-b` |
| Pantalón | **eliminado** — pendiente render Blender | — |

### JavaScript: `applyColor(zone, color)`
Actualiza `flood-color` en el elemento `feFlood` correspondiente:
```js
zoneMap[zone].forEach(id => document.getElementById(id).setAttribute('flood-color', color));
```

### Features activos
- ✅ Vista FRENTE + DORSO simultáneas
- ✅ Color picker: Cuerpo / Mangas / Cuello
- ✅ 8 combinaciones predefinidas (Argentina, Brasil, Boca, River, etc.)
- ✅ Nombre y número con color de texto configurable
- ✅ Estilo: Clásico / Rayas V / Rayas H
- ✅ Descarga como PNG
- ✅ Drop shadow en la camiseta (filter `js-shadow`)

### Lo que fue eliminado en esta sesión
- ❌ Paths SVG de color (jersey-body, jersey-sleeve-l/r, jersey-collar, back-*)
- ❌ Gradientes SVG sintéticos de shading (f-body-ao, f-side-l, etc.)
- ❌ Textura de tela SVG (mix-blend-mode overlay sobre path)
- ❌ Contornos SVG de silueta (stroke paths)
- ❌ Pantalón/shorts (se sumará con render Blender en el futuro)
- ❌ Sombra de piso (ellipse debajo de la camiseta)
- ❌ `clip-sleeve-f/b` (reemplazado por alpha del PNG)

---

## Estado de Blender

- PNGs generados con `jersey_render.py` (luces Key/Fill/Rim)
- Post-procesados con `centrar_renders.py` (Pillow) — autocrop + padding 8%
- ✅ `jersey_frente.png` (386×386px) y `jersey_dorso.png` (385×385px) con fondo transparente
- **Pendiente**: render de pantalón/shorts para sumar como nueva zona

---

## Próximos pasos

1. **[ ] Integrar nuevo diseño de UI** generado con Claude Design — el usuario tiene una propuesta lista
2. **[ ] Render Blender de pantalón** — agregar como capa adicional (misma técnica: filter-shorts)
3. **[ ] Afinar alineación PNG→SVG** si hace falta después de ver el nuevo diseño
4. **[ ] Eventuales mejoras**: subir escudo/logo, más tipos de cuello, exportar frente+dorso juntos

---

## Prompt para continuar

```
Estoy desarrollando un diseñador de camisetas de fútbol en vanilla HTML/CSS/JS.
Todos los archivos están en ~/Desktop/disenador-camisetas/

ESTADO ACTUAL — técnica de render:
- El PNG de Blender ES la camiseta (jersey_frente.png y jersey_dorso.png, 386px, fondo transparente)
- Colorización por zonas via SVG filters (feFlood → feBlend multiply → feComposite)
- Orden de capas: mangas (base, sin clip) → torso (clip evenodd) → cuello (clip)
- Mangas sin clipPath para preservar las puntas redondeadas del render 3D
- JavaScript actualiza flood-color en los feFlood elements via setAttribute

FEATURES ACTIVOS: color picker (cuerpo/mangas/cuello), 8 presets, nombre+número, rayas V/H, descarga PNG
PENDIENTE: pantalón (render Blender futuro), nuevo diseño de UI desde Claude Design

TAREA SIGUIENTE:
Integrar el nuevo diseño de UI generado con Claude Design (el usuario lo tiene listo).
Leer disenador.html antes de empezar para entender la estructura actual.

El proyecto vive en ~/Desktop/disenador-camisetas/ — sin git por ahora.
El usuario tiene Blender instalado y sabe hacer renders básicos.
Proyecto separado de SL Financial Planning (~/Desktop/web.slfinancialplanning.claudecode/).
```
