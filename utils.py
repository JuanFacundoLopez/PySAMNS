from PyQt5.QtCore import QRect

def norm(anchoX, altoY, x, y, ancho, alto):
    return QRect(int(anchoX * x), int(altoY * y), int(anchoX * ancho), int(altoY * alto))
