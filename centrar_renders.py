"""
Recorta jersey_frente.png y jersey_dorso.png al contenido real
y los recentra con padding uniforme en un canvas cuadrado.
"""
from PIL import Image
import os

DESKTOP = os.path.expanduser("~/Desktop/")
PADDING = 0.08   # margen relativo al lado más largo (8%)

def centrar(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")

    # Bounding box de píxeles no-transparentes (alpha > 10)
    r, g, b, a = img.split()
    bbox = a.point(lambda x: 255 if x > 10 else 0).getbbox()

    if bbox is None:
        print(f"  ⚠️  {os.path.basename(input_path)}: imagen completamente transparente")
        return

    x0, y0, x1, y1 = bbox
    w = x1 - x0
    h = y1 - y0
    print(f"  {os.path.basename(input_path)}: contenido en ({x0},{y0})-({x1},{y1}) → {w}×{h}px")

    # Canvas cuadrado: lado = lado más largo + padding
    side = int(max(w, h) * (1 + PADDING * 2))
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))

    # Pegar centrado
    offset_x = (side - w) // 2
    offset_y = (side - h) // 2
    canvas.paste(img.crop(bbox), (offset_x, offset_y))
    canvas.save(output_path)
    print(f"  ✓ guardado: {output_path} ({side}×{side}px)")

print("── Centrando renders ──")
centrar(DESKTOP + "jersey_frente.png", DESKTOP + "jersey_frente.png")
centrar(DESKTOP + "jersey_dorso.png",  DESKTOP + "jersey_dorso.png")
print("🎉 Listo")
