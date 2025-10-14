from PIL import Image
import os

# Ruta de la imagen de origen (PNG)
input_path = os.path.join('img', 'Logocintra.png')
# Ruta de salida para el ícono (ICO)
output_path = os.path.join('img', 'Logocintra.ico')

# Abrir la imagen
img = Image.open(input_path)

# Convertir a modo RGBA si no lo está
if img.mode != 'RGBA':
    img = img.convert('RGBA')

# Guardar como ICO con múltiples tamaños para mejor compatibilidad
sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
img.save(output_path, sizes=[(s[0], s[1]) for s in sizes])

print(f'Ícono convertido y guardado en: {output_path}')
