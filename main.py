from controller import controlador
# import sys
# sys.path.append('C:/Users/Facu/Desktop/SAMNS PyVersion pygraph/SAMNS PyVersion pygraph/funciones')
from db import crear_tabla

if __name__=='__main__':
    crear_tabla()
    SAMNS = controlador()
    SAMNS.cVista.animation()
    