import sys
from PyQt5.QtWidgets import QApplication
import pyqtgraph as pg
from pyqtgraph import PlotWidget, BarGraphItem

app = QApplication(sys.argv)

# Crear ventana y gráfico
win = pg.GraphicsLayoutWidget(title="Espectro por Octavas")
plot = win.addPlot()

# Frecuencias centrales (octavas)
frecuencias = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
niveles = [10, 20, 35, 15, 25, 30, 20, 10, 5, 2]

# Agregar barras
bar_item = BarGraphItem(x=frecuencias, height=niveles, width=40, brush='b')
plot.addItem(bar_item)

# Crear etiquetas [(valor_x, "texto")]
etiquetas = [(f, f"{int(f)} Hz") for f in frecuencias]
bottom_axis = plot.getAxis('bottom')
bottom_axis.setTicks([etiquetas])  # aplicar las etiquetas

# Asegurar espacio suficiente para el eje
plot.layout.setRowFixedHeight(2, 40)

# Mostrar ventana
win.show()
sys.exit(app.exec_())
