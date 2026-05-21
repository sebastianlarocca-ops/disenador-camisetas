"""
JERSEY SHADING MAP RENDERER
Pegá este script en el panel Scripting de Blender y ejecutalo con Run Script.
Guarda jersey_frente.png y jersey_dorso.png en el Escritorio.
"""

import bpy
import math
import os

# ── CONFIG ────────────────────────────────────────────────
OUTPUT_DIR  = os.path.expanduser("~/Desktop/")
FRONT_FILE  = OUTPUT_DIR + "jersey_frente.png"
BACK_FILE   = OUTPUT_DIR + "jersey_dorso.png"
RESOLUTION  = 1024   # px (subir a 2048 para producción)
SAMPLES     = 48     # muestras Cycles (más = mejor calidad, más lento)
# ──────────────────────────────────────────────────────────


def limpiar_luces_y_camara():
    for obj in list(bpy.data.objects):
        if obj.type in ['LIGHT', 'CAMERA']:
            bpy.data.objects.remove(obj, do_unlink=True)

def aplicar_material_blanco(meshes):
    mat = bpy.data.materials.new(name="JerseyShadingMap")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    # Color base: gris muy claro (no puro blanco para conservar detalle)
    bsdf.inputs['Base Color'].default_value = (0.90, 0.90, 0.90, 1.0)
    bsdf.inputs['Roughness'].default_value  = 0.72
    # Compatibilidad Blender 3.x y 4.x
    try:
        bsdf.inputs['Specular IOR Level'].default_value = 0.25
    except KeyError:
        try:
            bsdf.inputs['Specular'].default_value = 0.25
        except KeyError:
            pass

    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    for obj in meshes:
        obj.data.materials.clear()
        obj.data.materials.append(mat)
    print(f"  Material aplicado a {len(meshes)} mesh(es)")

def calcular_bbox(meshes):
    verts = []
    for obj in meshes:
        for v in obj.data.vertices:
            verts.append(obj.matrix_world @ v.co)
    xs = [v.x for v in verts]
    ys = [v.y for v in verts]
    zs = [v.z for v in verts]
    return (
        (min(xs)+max(xs))/2,
        (min(ys)+max(ys))/2,
        (min(zs)+max(zs))/2,
        max(xs)-min(xs),   # width
        max(zs)-min(zs),   # height
    )

def crear_luces(cx, cy, cz, scale):
    # Key: luz principal desde arriba-izquierda-frente (más contenida)
    bpy.ops.object.light_add(type='AREA',
        location=(cx - scale*0.9, cy - scale*2.0, cz + scale*1.4))
    key = bpy.context.active_object
    key.name = "Key"
    key.data.energy = 600 * scale   # bajado para no sobreexponer el frente
    key.data.size   = scale * 2.0
    key.rotation_euler = (math.radians(55), 0, math.radians(-30))

    # Fill: derecha, muy suave
    bpy.ops.object.light_add(type='AREA',
        location=(cx + scale*1.2, cy - scale*0.8, cz + scale*0.3))
    fill = bpy.context.active_object
    fill.name = "Fill"
    fill.data.energy = 180 * scale   # reducido
    fill.data.size   = scale * 3.0
    fill.rotation_euler = (math.radians(40), 0, math.radians(55))

    # Rim: desde atrás — da borde luminoso que separa del fondo
    bpy.ops.object.light_add(type='AREA',
        location=(cx, cy + scale*2.2, cz + scale*0.8))
    rim = bpy.context.active_object
    rim.name = "Rim"
    rim.data.energy = 250 * scale   # subido para más contraste en bordes
    rim.data.size   = scale * 1.8
    rim.rotation_euler = (math.radians(-58), 0, 0)

    print("  3 luces creadas (Key / Fill / Rim)")

def crear_camara(cx, cy, cz, width, height):
    dist = max(width, height) * 3.5
    bpy.ops.object.camera_add(
        location=(cx, cy - dist, cz),
        rotation=(math.radians(90), 0, 0)
    )
    cam_obj = bpy.context.active_object
    cam_obj.name = "RenderCam"
    cam = cam_obj.data
    cam.type = 'ORTHO'
    # Margen del 20% a cada lado para que la remera llene bien el frame
    cam.ortho_scale = max(width, height) * 1.40
    bpy.context.scene.camera = cam_obj

    # Apuntar la cámara exactamente al centro del bbox
    bpy.context.view_layer.update()
    print(f"  Cámara: centro=({cx:.2f},{cy:.2f},{cz:.2f}) escala={cam.ortho_scale:.2f}")
    return cam_obj, cy, dist

def configurar_render(samples, resolution):
    scene = bpy.context.scene
    scene.render.engine          = 'CYCLES'
    scene.cycles.samples         = samples
    scene.cycles.use_denoising   = True
    scene.render.resolution_x    = resolution
    scene.render.resolution_y    = resolution
    scene.render.pixel_aspect_x  = 1
    scene.render.pixel_aspect_y  = 1
    scene.render.image_settings.file_format  = 'PNG'
    scene.render.image_settings.color_mode  = 'RGBA'
    scene.render.image_settings.compression = 15
    scene.render.film_transparent = True   # fondo transparente

    # Mundo: negro puro (sin luz ambiental extra)
    world = scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value    = (0.0, 0.0, 0.0, 1.0)
        bg.inputs['Strength'].default_value = 0.0
    print(f"  Render: {resolution}px · {samples} samples · fondo transparente")

def renderizar(filepath, label):
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)
    print(f"  ✓ {label} → {filepath}")


# ═══════════════════════════════════════════════════════════
print("\n━━━ JERSEY RENDER SCRIPT ━━━")

meshes = [o for o in bpy.data.objects if o.type == 'MESH']

if not meshes:
    print("⚠️  No hay meshes en la escena.")
    print("    Importá el modelo de camiseta primero (File → Import)")
else:
    print(f"  {len(meshes)} mesh(es) encontrado(s): {[m.name for m in meshes]}")

    # 1. Preparar escena
    limpiar_luces_y_camara()
    aplicar_material_blanco(meshes)
    cx, cy, cz, w, h = calcular_bbox(meshes)
    scale = max(w, h) / 2
    print(f"  Centro: ({cx:.2f}, {cy:.2f}, {cz:.2f}) | W={w:.2f} H={h:.2f}")

    # 2. Luces y cámara
    crear_luces(cx, cy, cz, scale)
    cam_obj, base_y, dist = crear_camara(cx, cy, cz, w, h)

    # 3. Render config
    configurar_render(SAMPLES, RESOLUTION)

    # 4. FRENTE
    print("\n  Renderizando FRENTE...")
    renderizar(FRONT_FILE, "Frente")

    # 5. DORSO — cámara al otro lado
    cam_obj.location.y       = base_y + dist
    cam_obj.rotation_euler   = (math.radians(90), 0, math.radians(180))
    print("\n  Renderizando DORSO...")
    renderizar(BACK_FILE, "Dorso")

    print("\n🎉 ¡Listo!")
    print(f"   {FRONT_FILE}")
    print(f"   {BACK_FILE}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
