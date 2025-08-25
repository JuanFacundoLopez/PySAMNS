# Importo librerias

import pyqtgraph as pg
from ventanas.programarWin import ProgramarWin
from ventanas.calibracionWin import CalibracionWin
from ventanas.configDispWin import ConfigDispWin
from ventanas.configuracionWin import ConfiguracionWin

from PyQt5.QtWidgets import (QMainWindow, QApplication, QHBoxLayout, QVBoxLayout, QTabWidget, QPushButton,
                             QLabel, QGroupBox, QRadioButton, QCheckBox, QAction, QWidget, QGridLayout,
                             QMenu, QMessageBox, QColorDialog, QFileDialog)

from PyQt5.QtGui import QPixmap, QIcon
from pyqtgraph.Qt import  QtCore
from pyqtgraph import AxisItem, BarGraphItem
from PyQt5.QtCore import Qt
from utils import norm
import numpy as np

#import utilidades del sistema
import sys
import os

# --- Eje logarítmico personalizado para frecuencia ---
class LogAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        strings = []
        for val in values:
            exp = int(np.round(val))
            if np.isclose(val, exp, atol=0.01) and 0 <= exp <= 5:
                strings.append(f"10^{exp}")
            else:
                strings.append(" ")  # Espacio en vez de string vacío para evitar duplicados
        return strings

# --- Eje de tiempo personalizado para mostrar segundos ---
class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def tickStrings(self, values, scale, spacing):
        # Formatea los valores del eje X para mostrar segundos
        strings = []
        for val in values:
            # Formatea el valor como segundos con 2 decimales
            strings.append(f"{val:.2f} s")
        return strings

class FrequencyAxisItem(pg.AxisItem):
    """
    Eje personalizado para mostrar etiquetas de frecuencia en gráficos de barras
    """
    def __init__(self, orientation='bottom', bandas=None):
        super().__init__(orientation)
        self.bandas = bandas if bandas is not None else []
    
    def tickValues(self, minVal, maxVal, size):
        """
        Forzar que se muestren ticks para cada posición de barra
        """
        if len(self.bandas) == 0:
            return []
        
        # Crear ticks para cada posición de barra
        major_ticks = list(range(len(self.bandas)))
        return [(1.0, major_ticks), (0.0, [])]  # (spacing, ticks)
    
    def tickStrings(self, values, scale, spacing):
        """
        Devuelve las etiquetas personalizadas para cada posición
        """
        strings = []
        for v in values:
            # v es la posición en el eje (0, 1, 2, 3...)
            idx = int(round(v))
            if 0 <= idx < len(self.bandas):
                freq = self.bandas[idx]
                # Formatear la frecuencia de manera legible
                if freq >= 1000:
                    if freq % 1000 == 0:
                        strings.append(f'{int(freq/1000)}k')
                    else:
                        strings.append(f'{freq/1000:.1f}k')
                else:
                    if freq == int(freq):
                        strings.append(f'{int(freq)}')
                    else:
                        strings.append(f'{freq:.1f}')
            else:
                strings.append('')
        return strings
    
    def update_bandas(self, new_bandas):
        """
        Actualizar las bandas de frecuencia
        """
        self.bandas = new_bandas
        self.update()
    
    def update_bandas(self, new_bandas):
        """
        Actualizar las bandas de frecuencia
        """
        self.bandas = new_bandas
        self.update()
class vista(QMainWindow):

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Actualizar dimensiones
        self.anchoX = self.width()
        self.altoY = self.height()
        
        # Tamaño mínimo para los logos
        min_logo_width = 100   # píxeles
        min_logo_height = 100  # píxeles

        # Calcula el nuevo tamaño, pero limitado al mínimo
        logo_width = max(int(self.anchoX * 0.1), min_logo_width)
        logo_height = max(int(self.altoY * 0.1), min_logo_height)
        
        # Actualizar tamaño de los logos
        if hasattr(self, 'logoCintra') and hasattr(self, 'logoUTN'):
            self.logoCintra.setPixmap(QPixmap('img/Logocintra.png').scaled(
                logo_width, logo_height,
                QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
            self.logoUTN.setPixmap(QPixmap('img/LogoCINTRA1.png').scaled(
                logo_width, logo_height,
                QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

    def __init__(self, Controller):
        # Primero creamos la aplicación
        self.app = QApplication(sys.argv)
        
        # Luego inicializamos la ventana principal
        super().__init__()
        self.vController = Controller
        
        
    
        # Obtenemos información de la pantalla
        self.screen = self.app.primaryScreen()
        self.size = self.screen.size()
        self.anchoX = self.size.width()
        self.altoY = self.size.height()

        # Configuración de la ventana principal
        self.setWindowTitle("SAMNS")
        self.setGeometry(int(self.anchoX * 0.01), int(self.altoY * 0.025), 
                        int(self.anchoX * 0.95), int(self.altoY * 0.9))
        
        # Establecer tamaño mínimo de la ventana
        min_width = 900  # píxeles
        min_height = 800  # píxeles
        self.setMinimumSize(min_width, min_height)
        
        # Iniciar en pantalla completa
        self.showMaximized()

        # Widget central y layout principal
        self.widgetP = QWidget()
        self.setCentralWidget(self.widgetP)
        
        # Layout principal horizontal
        self.mainLayout = QHBoxLayout(self.widgetP)
        
        # Panel izquierdo (contenedor de tabs)
        self.leftPanel = QWidget()
        self.leftLayout = QVBoxLayout(self.leftPanel)
        self.leftLayout.setContentsMargins(0, 0, 0, 0)
        
        # Tabs
        self.tabWidget = QTabWidget()
        self.leftLayout.addWidget(self.tabWidget)
        
        # Configuración de tabs
        self.tab_1 = QWidget()
        #self.tab_2 = QWidget()
        self.tabWidget.addTab(self.tab_1, "Gráfico")
        #self.tabWidget.addTab(self.tab_2, "Valores del gráfico")
        
        # Layout para tab_1
        self.tab1Layout = QHBoxLayout(self.tab_1)
        self.columna1tab1 = QVBoxLayout()
        
        # Gráfico
        self.winGraph1 = pg.GraphicsLayoutWidget()
        self.winGraph1.setBackground('w')
        self.columna1tab1.addWidget(self.winGraph1)
        
        #variables para configuracion de grafico
        self.var_logModeXTiempo = False
        self.var_logModeYTiempo = False
        self.var_logModeXEspectro = False
        self.var_logModeYEspectro = False
        self.var_logModeXNivel = False
        self.var_logModeYNivel = False
        self.var_xMinTiempo = 0
        self.var_xMaxTiempo = 1024
        self.var_yMinTiempo = -1
        self.var_yMaxTiempo = 1
        self.var_xMinEspectro = 0
        self.var_xMaxEspectro = 1024
        self.var_yMinEspectro = -1
        self.var_yMaxEspectro = 1
        self.var_xMinNivel = 0
        self.var_xMaxNivel = 1024
        self.var_yMinNivel = -1
        self.var_yMaxNivel = 1
        self.var_etiquetaXTiempo = "Tiempo"
        self.var_etiquetaYTiempo = "Amplitud Normalizada"
        self.var_etiquetaXEspectro = "Tiempo"
        self.var_etiquetaYEspectro = "Amplitud Normalizada"
        self.var_etiquetaXNivel = "Tiempo"
        self.var_etiquetaYNivel = "Amplitud Normalizada"
        self.var_tipoLineaTiempo = ""
        self.var_tipoGraficoEspectro = ""
        self.var_tipoLineaNivel = ""
        self.var_colorTiempo = ""
        self.var_colorEspectro = ""
        self.var_colorNivel = ""
        
        # Centralización de colores por defecto
        self.default_color_tiempo = "#006400"      # Verde oscuro
        self.default_color_espectro = "#1E90FF"    # Azul claro
        self.default_color_nivel = "#8A2BE2"       # Violeta
        
        # Configuración del gráfico
        # Crear eje de tiempo personalizado para mostrar segundos
        self.time_axis = TimeAxisItem(orientation='bottom')
        self.waveform1 = self.winGraph1.addPlot(axisItems={'bottom': self.time_axis})
        self.waveform1.setDownsampling(mode='peak')
        self.waveform1.setClipToView(True)
        self.waveform1.showGrid(x=True, y=True)
        self.waveform1.setYRange(-1.2, 1.2, padding=0)
        # Línea principal para graficar datos en tiempo real
        self.plot_line = self.waveform1.plot([], [], pen=pg.mkPen(color='r', width=2))
        # Línea para graficar el espectro de frecuencia
        self.plot_line_freq = self.waveform1.plot([], [], pen=pg.mkPen(color='b', width=2))
        # Inicializar límites de eje Y para update_plot
        self.ymin1 = -1.2
        self.ymax1 = 1.2
        # Inicializar límites de eje Y para el espectro de frecuencia
        self.fft_ymin1 = -120
        self.fft_ymax1 = 0

        # Definir las líneas del gráfico
        self.ptdomTiempo = self.waveform1.plot(pen=(138, 1, 1), width=2)
        self.ptdomEspect = self.waveform1.plot(pen=(138, 63, 1), width=2)

        # Plots para nivel Z
        self.ptNivZSlow = self.waveform1.plot(pen='k', width=3)  # (138, 108, 1)
        self.ptNivZFast = self.waveform1.plot(pen='g', width=3)  # (124, 138, 1)
        self.ptNivZInst = self.waveform1.plot(pen='b', width=3)  # (70, 138, 1)
        self.ptNivZPico = self.waveform1.plot(pen='r', width=3)  # (3, 138, 1)
        print("DEBUG: Plots Z creados:", self.ptNivZSlow, self.ptNivZFast, self.ptNivZInst, self.ptNivZPico)
        
        # Plots para nivel C
        self.ptNivCSlow = self.waveform1.plot(pen=(1, 138, 42), width=3)
        self.ptNivCFast = self.waveform1.plot(pen=(1, 138, 92), width=3)
        self.ptNivCInst = self.waveform1.plot(pen=(1, 117, 138), width=3)
        self.ptNivCPico = self.waveform1.plot(pen=(1, 54, 138), width=3)
        print("DEBUG: Plots C creados:", self.ptNivCSlow, self.ptNivCFast, self.ptNivCInst, self.ptNivCPico)
        
        # Plots para nivel A
        self.ptNivASlow = self.waveform1.plot(pen=(28, 1, 138), width=3)
        self.ptNivAFast = self.waveform1.plot(pen=(51, 1, 138), width=3)
        self.ptNivAInst = self.waveform1.plot(pen=(108, 1, 138), width=3)
        self.ptNivAPico = self.waveform1.plot(pen=(138, 1, 63), width=3)
        print("DEBUG: Plots A creados:", self.ptNivASlow, self.ptNivAFast, self.ptNivAInst, self.ptNivAPico)
        
        # Botones y cronómetro
        buttonLayout = QHBoxLayout()
        self.btn = QPushButton("Importar señal")
        self.btn.setToolTip("Importar señal de audio de un archivo .Wav")
        self.btn.clicked.connect(self.vController.importSignal)
        self.btngbr = QPushButton("Grabar")
        self.btngbr.setToolTip("Iniciar o Pausa la Grabacion de audio")
        self.btngbr.setCheckable(True)
        self.btngbr.clicked.connect(self.grabar)
        
        icon_play_path = "img/boton-de-play.png" 
        self.btngbr.setIcon(QIcon(icon_play_path))
        icon_import_path = "img/importar.png"
        self.btn.setIcon(QIcon(icon_import_path))
        
       
        
        # Aplicar estilo a ambos botones
        self.btn.setProperty("class", "grabacion")
        self.btngbr.setProperty("class", "grabacion")
        
        
        self.cronometroGrabacion = QLabel("0:00 s")
        self.cronometroGrabacion.setStyleSheet("font: bold 20pt")
        buttonLayout.addWidget(self.btn)
        buttonLayout.addWidget(self.btngbr)
        buttonLayout.addWidget(self.cronometroGrabacion)
        buttonLayout.addStretch()
        self.columna1tab1.addLayout(buttonLayout)
        
        # Panel derecho
        self.rightPanel = QWidget()
        self.rightLayout = QVBoxLayout(self.rightPanel)
        
        # Grupo de tipo de gráfico
        tipoGraficoGroup = QGroupBox("Tipo de gráfico")
        tipoGraficoLayout = QHBoxLayout()
        
        # Contenedor para los botones
        botonesLayout = QVBoxLayout()
        
        self.btnTiempo = QPushButton("Tiempo")
        self.btnTiempo.setCheckable(True)
        self.btnTiempo.setChecked(True)
        self.btnTiempo.clicked.connect(self.ventanaTiempo)
        
        self.btnFrecuencia = QPushButton("Frecuencia")
        self.btnFrecuencia.setCheckable(True)
        self.btnFrecuencia.clicked.connect(self.ventanaFrecuencia)
        
        self.btnNivel = QPushButton("Nivel")
        self.btnNivel.setCheckable(True)
        self.btnNivel.clicked.connect(self.ventanaNivel)
        
        botonesLayout.addWidget(self.btnTiempo)
        botonesLayout.addWidget(self.btnFrecuencia)
        botonesLayout.addWidget(self.btnNivel)
        
        # RAM
        # self.ram = QLabel("Ram")
        # self.ram.setAlignment(QtCore.Qt.AlignCenter)
        # self.ram.setStyleSheet("background-color: lightblue; font-size:11pt; color: white;")
        
        tipoGraficoLayout.addLayout(botonesLayout, 75)
        #tipoGraficoLayout.addWidget(self.ram, 25)
        tipoGraficoGroup.setLayout(tipoGraficoLayout)
        self.rightLayout.addWidget(tipoGraficoGroup)
        
        # Filtros ponderados
        filtrosGroup = QGroupBox("Filtros ponderados")
        filtrosLayout = QVBoxLayout()
        
        self.r0 = QRadioButton("Filtro ponderado A")
        self.r1 = QRadioButton("Filtro ponderado C")
        self.r2 = QRadioButton("Filtro ponderado Z")
        self.r2.setChecked(True)
        
        filtrosLayout.addWidget(self.r0)
        filtrosLayout.addWidget(self.r1)
        filtrosLayout.addWidget(self.r2)
        filtrosGroup.setLayout(filtrosLayout)
        self.rightLayout.addWidget(filtrosGroup)
        
        # Niveles estadísticos
        nivelesGroup = QGroupBox("Niveles estadísticos")
        self.tabFilt = QTabWidget()
        self.tabFiltA = QWidget()
        self.tabFiltC = QWidget()
        self.tabFiltZ = QWidget()
        
        # Layout para filtro A
        layoutFiltA = QGridLayout(self.tabFiltA)
        self.cbEqA = QCheckBox("LA eq",self.tabFiltA)
        self.cb01A = QCheckBox("01 eq",self.tabFiltA)
        self.cb10A = QCheckBox("10 eq",self.tabFiltA)
        self.cb50A = QCheckBox("50 eq",self.tabFiltA)
        self.cb90A = QCheckBox("90 eq",self.tabFiltA)
        self.cb99A = QCheckBox("99 eq",self.tabFiltA)
        # Primera fila
        layoutFiltA.addWidget(self.cbEqA, 0, 0)
        layoutFiltA.addWidget(self.cb01A, 0, 1)
        layoutFiltA.addWidget(self.cb10A, 0, 2)
        # Segunda fila
        layoutFiltA.addWidget(self.cb50A, 1, 0)
        layoutFiltA.addWidget(self.cb90A, 1, 1)
        layoutFiltA.addWidget(self.cb99A, 1, 2)
        # Agregar espacio al final
        layoutFiltA.setColumnStretch(3, 1)
        
        # Layout para filtro C
        layoutFiltC = QGridLayout(self.tabFiltC)
        self.cbEqC = QCheckBox("LC eq",self.tabFiltC)
        self.cb01C = QCheckBox("01 eq",self.tabFiltC)
        self.cb10C = QCheckBox("10 eq",self.tabFiltC)
        self.cb50C = QCheckBox("50 eq",self.tabFiltC)
        self.cb90C = QCheckBox("90 eq",self.tabFiltC)
        self.cb99C = QCheckBox("99 eq",self.tabFiltC)
        # Primera fila
        layoutFiltC.addWidget(self.cbEqC, 0, 0)
        layoutFiltC.addWidget(self.cb01C, 0, 1)
        layoutFiltC.addWidget(self.cb10C, 0, 2)
        # Segunda fila
        layoutFiltC.addWidget(self.cb50C, 1, 0)
        layoutFiltC.addWidget(self.cb90C, 1, 1)
        layoutFiltC.addWidget(self.cb99C, 1, 2)
        # Agregar espacio al final
        #layoutFiltC.setColumnStretch(3, 1)
        
        # Layout para filtro Z
        layoutFiltZ = QGridLayout(self.tabFiltZ)
        self.cbEqZ = QCheckBox("LZ eq",self.tabFiltZ)
        self.cb01Z = QCheckBox("01 eq",self.tabFiltZ)
        self.cb10Z = QCheckBox("10 eq",self.tabFiltZ)
        self.cb50Z = QCheckBox("50 eq",self.tabFiltZ)
        self.cb90Z = QCheckBox("90 eq",self.tabFiltZ)
        self.cb99Z = QCheckBox("99 eq",self.tabFiltZ)
        # Primera fila
        layoutFiltZ.addWidget(self.cbEqZ, 0, 0)
        layoutFiltZ.addWidget(self.cb01Z, 0, 1)
        layoutFiltZ.addWidget(self.cb10Z, 0, 2)
        # Segunda fila
        layoutFiltZ.addWidget(self.cb50Z, 1, 0)
        layoutFiltZ.addWidget(self.cb90Z, 1, 1)
        layoutFiltZ.addWidget(self.cb99Z, 1, 2)
        

        self.tabFilt.addTab(self.tabFiltA, "Filtro A")
        self.tabFilt.addTab(self.tabFiltC, "Filtro C")
        self.tabFilt.addTab(self.tabFiltZ, "Filtro Z")
        
        nivelesLayout = QVBoxLayout()
        nivelesLayout.addWidget(self.tabFilt)
        nivelesGroup.setLayout(nivelesLayout)
        self.rightLayout.addWidget(nivelesGroup)
        
        # Ponderación temporal
        ponderacionGroup = QGroupBox("Ponderación temporal")
        self.tabNieles = QTabWidget()
        self.tabNivPico = QWidget()
        self.tabNivInst = QWidget()
        self.tabNivFast = QWidget()
        self.tabNivSlow = QWidget()
        
        # Layout para Pico
        layoutPico = QHBoxLayout(self.tabNivPico)
        self.cbNivPicoA = QCheckBox("A")
        self.cbNivPicoC = QCheckBox("C")
        self.cbNivPicoZ = QCheckBox("Z")
        layoutPico.addWidget(self.cbNivPicoA)
        layoutPico.addWidget(self.cbNivPicoC)
        layoutPico.addWidget(self.cbNivPicoZ)
        layoutPico.addStretch()
        
        # Layout para Instantaneo
        layoutInst = QGridLayout(self.tabNivInst)
        self.cbNivInstA = QCheckBox("A")
        self.cbNivInstC = QCheckBox("C")
        self.cbNivInstZ = QCheckBox("Z")
        self.cbNivInstMinA = QCheckBox("A min")
        self.cbNivInstMinC = QCheckBox("C min")
        self.cbNivInstMinZ = QCheckBox("Z min")
        self.cbNivInstMaxA = QCheckBox("A max")
        self.cbNivInstMaxC = QCheckBox("C max")
        self.cbNivInstMaxZ = QCheckBox("Z max")
        # Primera fila
        layoutInst.addWidget(self.cbNivInstA, 0, 0)
        layoutInst.addWidget(self.cbNivInstC, 0, 1)
        layoutInst.addWidget(self.cbNivInstZ, 0, 2)
        # Segunda fila
        layoutInst.addWidget(self.cbNivInstMinA, 1, 0)
        layoutInst.addWidget(self.cbNivInstMinC, 1, 1)
        layoutInst.addWidget(self.cbNivInstMinZ, 1, 2)
        # Tercera fila
        layoutInst.addWidget(self.cbNivInstMaxA, 2, 0)
        layoutInst.addWidget(self.cbNivInstMaxC, 2, 1)
        layoutInst.addWidget(self.cbNivInstMaxZ, 2, 2)


        # Layout para Instantaneo
        layoutFast = QGridLayout(self.tabNivFast)
        self.cbNivFastA = QCheckBox("A")
        self.cbNivFastC = QCheckBox("C")
        self.cbNivFastZ = QCheckBox("Z")
        self.cbNivFastMinA = QCheckBox("A min")
        self.cbNivFastMinC = QCheckBox("C min")
        self.cbNivFastMinZ = QCheckBox("Z min")
        self.cbNivFastMaxA = QCheckBox("A max")
        self.cbNivFastMaxC = QCheckBox("C max")
        self.cbNivFastMaxZ = QCheckBox("Z max")
        # Primera fila
        layoutFast.addWidget(self.cbNivFastA, 0, 0)
        layoutFast.addWidget(self.cbNivFastC, 0, 1)
        layoutFast.addWidget(self.cbNivFastZ, 0, 2)
        # Segunda fila
        layoutFast.addWidget(self.cbNivFastMinA, 1, 0)
        layoutFast.addWidget(self.cbNivFastMinC, 1, 1)
        layoutFast.addWidget(self.cbNivFastMinZ, 1, 2)
        # Tercera fila
        layoutFast.addWidget(self.cbNivFastMaxA, 2, 0)
        layoutFast.addWidget(self.cbNivFastMaxC, 2, 1)
        layoutFast.addWidget(self.cbNivFastMaxZ, 2, 2)
        
        # Layout para Slow
        layoutSlow = QGridLayout(self.tabNivSlow)
        self.cbNivSlowA = QCheckBox("A")
        self.cbNivSlowC = QCheckBox("C")
        self.cbNivSlowZ = QCheckBox("Z")
        self.cbNivSlowMinA = QCheckBox("A min")
        self.cbNivSlowMinC = QCheckBox("C min")
        self.cbNivSlowMinZ = QCheckBox("Z min")
        self.cbNivSlowMaxA = QCheckBox("A max")
        self.cbNivSlowMaxC = QCheckBox("C max")
        self.cbNivSlowMaxZ = QCheckBox("Z max")
        # Primera fila
        layoutSlow.addWidget(self.cbNivSlowA, 0, 0)
        layoutSlow.addWidget(self.cbNivSlowC, 0, 1)
        layoutSlow.addWidget(self.cbNivSlowZ, 0, 2)
        # Segunda fila
        layoutSlow.addWidget(self.cbNivSlowMinA, 1, 0)
        layoutSlow.addWidget(self.cbNivSlowMinC, 1, 1)
        layoutSlow.addWidget(self.cbNivSlowMinZ, 1, 2)
        # Tercera fila
        layoutSlow.addWidget(self.cbNivSlowMaxA, 2, 0)
        layoutSlow.addWidget(self.cbNivSlowMaxC, 2, 1)
        layoutSlow.addWidget(self.cbNivSlowMaxZ, 2, 2)
        
        self.tabNieles.addTab(self.tabNivPico, "Pico")
        self.tabNieles.addTab(self.tabNivInst, "Instantaneo")
        self.tabNieles.addTab(self.tabNivFast, "Fast")
        self.tabNieles.addTab(self.tabNivSlow, "Slow")
        
        # Conectar checkboxes de nivel para actualizar el gráfico
        self.cbNivPicoA.toggled.connect(self.actualizarGraficoNivel)
        self.cbNivPicoC.toggled.connect(self.actualizarGraficoNivel)
        self.cbNivPicoZ.toggled.connect(self.actualizarGraficoNivel)
        self.cbNivInstA.toggled.connect(self.actualizarGraficoNivel)
        self.cbNivInstC.toggled.connect(self.actualizarGraficoNivel)
        self.cbNivInstZ.toggled.connect(self.actualizarGraficoNivel)
        self.cbNivFastA.toggled.connect(self.actualizarGraficoNivel)
        self.cbNivFastC.toggled.connect(self.actualizarGraficoNivel)
        self.cbNivFastZ.toggled.connect(self.actualizarGraficoNivel)
        self.cbNivSlowA.toggled.connect(self.actualizarGraficoNivel)
        self.cbNivSlowC.toggled.connect(self.actualizarGraficoNivel)
        self.cbNivSlowZ.toggled.connect(self.actualizarGraficoNivel)
        
        # Debug para verificar el estado inicial de los checkboxes
        print(f"DEBUG: Estado inicial cbNivSlowZ: {self.cbNivSlowZ.isChecked()}")
        
        ponderacionLayout = QVBoxLayout()
        ponderacionLayout.addWidget(self.tabNieles)
        ponderacionGroup.setLayout(ponderacionLayout)
        self.rightLayout.addWidget(ponderacionGroup)
        
        # Logos
        min_logo_width = 80   # píxeles
        min_logo_height = 80  # píxeles

        logo_width = max(int(self.anchoX * 0.1), min_logo_width)
        logo_height = max(int(self.altoY * 0.1), min_logo_height)

        self.logoCintra = QLabel()
        self.logoCintra.setPixmap(QPixmap('img/Logocintra.png').scaled(
            logo_width, logo_height,
            QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        
        self.logoUTN = QLabel()
        self.logoUTN.setPixmap(QPixmap('img/LogoCINTRA1.png').scaled(
            logo_width, logo_height,
            QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        
        logosLayout = QHBoxLayout()
        logosLayout.addWidget(self.logoCintra)
        logosLayout.addWidget(self.logoUTN)
        self.rightLayout.addLayout(logosLayout)
        
        # Agregar stretch al final del panel derecho para empujar todo hacia arriba
        self.rightLayout.addStretch()
        
        # Agregar los paneles al layout principal con proporciones
        self.mainLayout.addWidget(self.leftPanel, stretch=75)
        self.tab1Layout.addLayout(self.columna1tab1, stretch=85)
        self.tab1Layout.addWidget(self.rightPanel, stretch=15)

        # Creo la barra de menús usando el método nativo de QMainWindow
        self.menuBar = self.menuBar()  # Esto obtiene la barra de menús de la ventana principal

        # Menú Archivo
        self.menuArchivo = QMenu("Archivo", self)
        self.menuArchivo.addAction("Abrir")
        self.menuArchivo.addAction("Guardar")
        self.menuArchivo.addAction("Guardar como...")
        self.menuArchivo.addSeparator()
        self.menuArchivo.addAction("Exportar")
        self.menuArchivo.addAction("Importar")
        self.menuArchivo.addSeparator()
        self.menuArchivo.addAction("Salir")

        # Menú Calibración
        self.menuCalibracion = QMenu("Calibración", self)
        calAct = QAction("Menu Calibración", self)
        calAct.triggered.connect(self.calibracionWin)
        self.menuCalibracion.addAction(calAct)

        # Otros menús
        self.menuConfiguracion = QMenu("Configuración", self)
        configAct = QAction("Configuración de Gráficos", self)
        configAct.triggered.connect(self.configuracion)
        self.menuConfiguracion.addAction(configAct)
        # Nueva acción para configuración de dispositivo
        configDispAct = QAction("Configuración de Dispositivo", self)
        configDispAct.triggered.connect(self.configuracionDispositivo)
        self.menuConfiguracion.addAction(configDispAct)
       
        self.menuConfiguracion.setToolTip("Configuraciones de gráfico y dispositivos")
        
        self.menuProgramacion = QMenu("Programación", self)
        progAct = QAction("Programar", self)
        progAct.triggered.connect(self.abrirprogramarWin)
        self.menuProgramacion.addAction(progAct)
        
        self.menuAyuda = QMenu("Ayuda", self)
        self.menuAcerca_de = QMenu("Acerca de...", self)
        
        # Agregar acción para abrir el sitio web de CINTRA
        acercaCintraAct = QAction("Sitio Web CINTRA", self)
        acercaCintraAct.triggered.connect(self.abrirSitioCintra)
        self.menuAcerca_de.addAction(acercaCintraAct)

        # Agrego los menús a la barra
        self.menuBar.addMenu(self.menuArchivo)
        self.menuBar.addMenu(self.menuCalibracion)
        self.menuBar.addMenu(self.menuConfiguracion)
        self.menuBar.addMenu(self.menuProgramacion)
        self.menuBar.addMenu(self.menuAyuda)
        self.menuBar.addMenu(self.menuAcerca_de)

        # Configurar el gráfico inicial en modo tiempo
        self.btnTiempo.setChecked(True)
        self.btnFrecuencia.setChecked(False)
        self.btnNivel.setChecked(False)
        self.tabFilt.setDisabled(True)
        self.tabNieles.setDisabled(True)
        
        # Limpiar el gráfico actual
        self.waveform1.clear()
        
        # Configuración para gráfico de tiempo
        self.waveform1.setLogMode(x=False, y=False)  # Escala lineal
        self.waveform1.setYRange(-1, 1, padding=0)   # Amplitud normalizada
        self.waveform1.setXRange(0, 1024, padding=0) # Rango de tiempo
        self.waveform1.setLabel('left', 'Amplitud Normalizada')
        self.waveform1.setLabel('bottom', 'Tiempo (s)')
        
        # Actualizar el gráfico
        self.waveform1.replot()

        with open("estilos.qss", "r", encoding='utf-8') as f:
            self.app.setStyleSheet(f.read())
            
        self.show()

    def abrirprogramarWin(self):
        self.programar_win = ProgramarWin()
        self.programar_win.show()

    def configuracionDispositivo(self):
        self.calWin = CalibracionWin(self.vController)
        self.configDispWin = ConfigDispWin(self.vController,self.calWin )
        self.configDispWin.show()
        
    def calibracionWin(self):
        self.calWin = CalibracionWin(self.vController)
        self.calWin.show()
        
    # CODIGO configuracion del graficos
    def configuracion(self):
        self.confWin = ConfiguracionWin(self)
        self.confWin.show()

    
    def grabar(self):
        self.editar_botonGrabar() 
        self.vController.dalePlay() # conexion con el controlador

    def editar_botonGrabar(self):
        """Edita el botón de grabar para que se vea como un botón de pausa"""
        if self.btngbr.isChecked():
            self.btngbr.setText("Pausar")
            self.btngbr.setIcon(QIcon("img/boton-de-pausa.png"))
        else:
            self.btngbr.setText("Grabar")
            self.btngbr.setIcon(QIcon("img/boton-de-play.png"))
    
    def ventanaTiempo(self):
        self.btnNivel.setChecked(False)
        self.btnFrecuencia.setChecked(False)
        self.tabFilt.setDisabled(True)
        self.tabNieles.setDisabled(True)
        
        # Resetear bandera de nivel
        self.nivel_configured = False
        
        # Limpiar el gráfico actual
        self.waveform1.clear()
        
        # Asegurar que se use el eje de tiempo personalizado
        if not hasattr(self, 'time_axis') or self.waveform1.getAxis('bottom') != self.time_axis:
            self.time_axis = TimeAxisItem(orientation='bottom')
            self.waveform1.setAxisItems({'bottom': self.time_axis})
        
        # Aplicar configuración personalizada si existe, sino usar valores por defecto
        if hasattr(self, 'txtXMinTiempo') and hasattr(self, 'txtXMaxTiempo'):
            self.aplicarConfiguracionTiempo()
        else:
            # Configuración por defecto para gráfico de tiempo
            self.waveform1.setLogMode(x=False, y=False)  # Escala lineal
            self.waveform1.setYRange(-1, 1, padding=0)   # Amplitud normalizada
            self.waveform1.setXRange(0, 1024, padding=0) # Rango de tiempo
            self.waveform1.setLabel('left', 'Amplitud Normalizada')
            self.waveform1.setLabel('bottom', 'Tiempo (s)')
        
        # Actualizar el gráfico
        self.waveform1.replot()
        self.vController.graficar()
        
    def ventanaFrecuencia(self):
        self.btnNivel.setChecked(False)
        self.btnTiempo.setChecked(False)
        self.tabFilt.setDisabled(True)
        self.tabNieles.setDisabled(True)
        
        # Resetear bandera de nivel
        self.nivel_configured = False
        
        # Eliminar el clear para no borrar la línea del espectro
        # self.waveform1.clear()
        # Aplicar configuración personalizada si existe, sino usar valores por defecto
        if hasattr(self, 'txtXMinEspectro') and hasattr(self, 'txtXMaxEspectro'):
            self.aplicarConfiguracionEspectro()
        else:
            # Configuración por defecto para gráfico de frecuencia
            self.waveform1.setLogMode(x=False, y=False)    # Escala lineal
            self.waveform1.setXRange(20, 20000, padding=0) # Rango de frecuencia
            self.waveform1.setYRange(-120, 0, padding=0)   # Rango de amplitud en dB
            self.waveform1.setLabel('left', 'Amplitud')
            self.waveform1.setLabel('bottom', 'Frecuencia (Hz)')
        # Actualizar el gráfico
        self.waveform1.replot()
        self.vController.graficar()
        
    def ventanaNivel(self):
        self.btnTiempo.setChecked(False)
        self.btnFrecuencia.setChecked(False)
        self.tabFilt.setEnabled(True)
        self.tabNieles.setEnabled(True)
        
        print("DEBUG: Configurando ventana de nivel")
        
        # Solo limpiar el gráfico si no está ya configurado para nivel
        if not hasattr(self, 'nivel_configured') or not self.nivel_configured:
            self.waveform1.clear()
            self.nivel_configured = True
        
        # Habilitar Z Slow por defecto para que se vea algo en el gráfico
        self.cbNivSlowZ.setChecked(True)
        print("DEBUG: Z Slow habilitado por defecto")
        
        # Aplicar configuración personalizada si existe, sino usar valores por defecto
        if hasattr(self, 'txtXMinNivel') and hasattr(self, 'txtXMaxNivel'):
            self.aplicarConfiguracionNivel()
        else:
            # Configuración por defecto para gráfico de nivel
            self.waveform1.setLogMode(x=False, y=False)  # Escala lineal
            self.waveform1.setYRange(-150, 0, padding=0)  # Rango de presión en dB (ajustado para mostrar datos más bajos)
            self.waveform1.setXRange(0, 10, padding=0)  # Rango de tiempo en segundos
            self.waveform1.setLabel('left', 'Nivel fondo de escala (dB)')
            self.waveform1.setLabel('bottom', 'Tiempo (s)')
            self.waveform1.setTitle('Gráfico de Nivel de Presión Sonora')
            print("DEBUG: Configuración por defecto aplicada")
        
        # Actualizar el gráfico
        self.waveform1.replot()
        print("DEBUG: Gráfico actualizado")
        self.vController.graficar()

    def graficar(self):
        self.vController.graficar()

    def actualizarGraficoNivel(self):
        """Actualiza el gráfico de nivel cuando se cambia la selección de checkboxes"""
        print(f"DEBUG: actualizarGraficoNivel llamado, btnNivel.isChecked(): {self.btnNivel.isChecked()}")
        if self.btnNivel.isChecked():
            print("DEBUG: Llamando a vController.graficar()")
            self.vController.graficar()
            # Forzar actualización del gráfico
            self.waveform1.replot()
            print("DEBUG: replot forzado en actualizarGraficoNivel")

    def animation(self):
        """Inicia el bucle principal de la aplicación"""
        self.show()
        return self.app.exec_()

    def abrirSitioCintra(self):
        """Abre el sitio web de CINTRA en el navegador predeterminado"""
        import webbrowser
        try:
            webbrowser.open("https://cintra.ar")
        except Exception as e:
            print(f"Error al abrir el sitio web de CINTRA: {e}")


    def aplicarConfiguracionTiempo(self):
        """Aplica la configuración personalizada para el gráfico de tiempo"""
        try:
            # # Escalas
            self.waveform1.setLogMode(x=self.var_logModeXTiempo, y=self.var_logModeYTiempo)
            # # Límites
            self.waveform1.setXRange(self.var_xMinTiempo, self.var_xMaxTiempo, padding=0)
            self.waveform1.setYRange(self.var_yMinTiempo, self.var_yMaxTiempo, padding=0)
            # # Etiquetas
            self.waveform1.setLabel('bottom', self.var_etiquetaXTiempo)
            self.waveform1.setLabel('left', self.var_etiquetaYTiempo)
            # Color y tipo de línea
            if hasattr(self, 'colorTiempo'):
                color = self.get_color_str(self.colorTiempo)
            else:
                color = self.default_color_tiempo  # Color por defecto centralizado
            tipoLinea = self.obtenerTipoLinea("tiempo")
            self.actualizarEstiloLinea(color, tipoLinea)
        except Exception as e:
            print(f"Error al aplicar configuración de tiempo: {e}")

    def aplicarConfiguracionEspectro(self):
        """Aplica la configuración personalizada para el gráfico de espectro"""
        try:
            # Limpiar barras anteriores si existen
            if hasattr(self, 'current_bar_item'):
                self.waveform1.removeItem(self.current_bar_item)
                delattr(self, 'current_bar_item')
            # Escalas
            self.waveform1.setLogMode(x=self.var_logModeXEspectro, y=self.var_logModeYEspectro)
            # Límites
            self.waveform1.setXRange(self.var_xMinEspectro, self.var_xMaxEspectro, padding=0)
            self.waveform1.setYRange(self.var_yMinEspectro, self.var_yMaxEspectro, padding=0)
            # Etiquetas
            self.waveform1.setLabel('bottom', self.var_etiquetaXEspectro)
            self.waveform1.setLabel('left', self.var_etiquetaYEspectro)
            # Color y tipo de gráfico
            if hasattr(self, 'colorEspectro'):
                color = self.get_color_str(self.colorEspectro)
            else:
                color = self.default_color_espectro  # Color por defecto centralizado
            tipoGrafico = self.obtenerTipoGraficoEspectro()
            self.actualizarEstiloGraficoEspectro(color, tipoGrafico)
        except Exception as e:
            print(f"Error al aplicar configuración de espectro: {e}")

    def aplicarConfiguracionNivel(self):
        """Aplica la configuración personalizada para el gráfico de nivel"""
        try:
            # Escalas
            self.waveform1.setLogMode(x=False, y=self.var_logModeYNivel)
            # Límites
            self.waveform1.setXRange(self.var_xMinNivel, self.var_xMaxNivel, padding=0)
            self.waveform1.setYRange(self.var_yMinNivel, self.var_yMaxNivel, padding=0)
            # Etiquetas
            self.waveform1.setLabel('bottom', self.var_etiquetaXNivel)
            self.waveform1.setLabel('left', self.var_etiquetaYNivel)
            # Color y tipo de línea
            if hasattr(self, 'colorNivel'):
                color = self.get_color_str(self.colorNivel)
            else:
                color = self.default_color_nivel  # Color por defecto centralizado
            tipoLinea = self.obtenerTipoLinea("nivel")
            self.actualizarEstiloLinea(color, tipoLinea)
        except Exception as e:
            print(f"Error al aplicar configuración de nivel: {e}")

    def actualizarEstiloLinea(self, color, tipoLinea):
        """Actualiza el estilo de la línea del gráfico"""
        try:
            if tipoLinea == "Sólida":
                pen = pg.mkPen(color=color, width=2)
            elif tipoLinea == "Punteada":
                pen = pg.mkPen(color=color, width=2, style=QtCore.Qt.DotLine)
            elif tipoLinea == "Rayada":
                pen = pg.mkPen(color=color, width=2, style=QtCore.Qt.DashLine)
            else:
                pen = pg.mkPen(color=color, width=2)
            
            # Actualizar el pen de la línea principal
            if hasattr(self, 'ptdomTiempo'):
                self.ptdomTiempo.setPen(pen)
            if hasattr(self, 'ptdomEspect'):
                self.ptdomEspect.setPen(pen)
            
        except Exception as e:
            print(f"Error al actualizar estilo de línea: {e}")

    def actualizarEstiloGraficoEspectro(self, color, tipoGrafico):
        """Actualiza el estilo del gráfico de espectro"""
        try:
            if tipoGrafico == "Línea":
                # Para gráfico de línea, usar pen normal
                pen = pg.mkPen(color=color, width=2)
                if hasattr(self, 'ptdomEspect'):
                    self.ptdomEspect.setPen(pen)
            elif tipoGrafico in ["Barras-octavas", "Barras-tercios"]:
                # Limpiar el gráfico y guardar el color
                if hasattr(self, 'waveform1'):
                    self.waveform1.clear()
                self.colorEspectro = color
            
        except Exception as e:
            print(f"Error al actualizar estilo de gráfico de espectro: {e}")

    def seleccionarColor(self, colorFrame, tipoGrafico):
        """Abre el diálogo de selección de color y actualiza el frame de color"""
        color = QColorDialog.getColor()
        if color.isValid():
            colorFrame.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
            # Aquí puedes guardar el color seleccionado según el tipo de gráfico
            if tipoGrafico == "tiempo":
                self.colorTiempo = color
            elif tipoGrafico == "espectro":
                self.colorEspectro = color
            elif tipoGrafico == "nivel":
                self.colorNivel = color

    def obtenerTipoLinea(self, tipoGrafico):
        """Obtiene el tipo de línea seleccionado para el gráfico especificado"""
        if tipoGrafico == "tiempo":
            return self.var_tipoLineaTiempo
        elif tipoGrafico == "nivel":
            return self.var_tipoLineaNivel
        return "Sólida"  # Valor por defecto

    def obtenerTipoGraficoEspectro(self):
        """Obtiene el tipo de gráfico seleccionado para el espectro"""
        return self.var_tipoGraficoEspectro

    def get_color_str(self, color):
        """Devuelve el color como string hexadecimal, ya sea que sea QColor o string"""
        if hasattr(color, 'name'):
            return color.name()
        return color

# CODIGO YAMILI

    def update_plot(self, device_num, current_data, all_data, normalized_current, normalized_all, db_level, device_name, times, fft_freqs, fft_magnitude):
        try:
            if self.btnTiempo.isChecked():
                import numpy as np
                # Usar datos crudos para cálculos
                values_str = ", ".join([f"{v:.2f}" for v in normalized_current[:10]])
                
                # Asegurar que se use el eje de tiempo personalizado
                if not hasattr(self, 'time_axis') or self.waveform1.getAxis('bottom') != self.time_axis:
                    self.time_axis = TimeAxisItem(orientation='bottom')
                    self.waveform1.setAxisItems({'bottom': self.time_axis})
                    self.waveform1.setLabel('bottom', 'Tiempo (s)')
                
                # Aplicar suavizado SOLO para visualización
                smooth_data = np.interp(
                    np.linspace(0, len(normalized_all)-1, len(normalized_all)*2),
                    np.arange(len(normalized_all)),
                    normalized_all
                )
                # Crear array de tiempo suavizado
                smooth_times = np.interp(
                    np.linspace(0, len(times)-1, len(smooth_data)),
                    np.arange(len(times)),
                    times
                )
                
                # Mostrar solo los últimos N puntos
                N = 2000
                xdata = smooth_times[-N:]
                ydata = smooth_data[-N:]
                print("Graficando:", len(xdata), len(ydata), "Ejemplo:", ydata[:5])
                print("Eje X:", xdata[:10])
                # Eliminar la línea anterior si existe
                if hasattr(self, 'plot_line'):
                    self.waveform1.removeItem(self.plot_line)
                
                # Limpiar barras anteriores si existen
                if hasattr(self, 'current_bar_item'):
                    self.waveform1.removeItem(self.current_bar_item)
                    delattr(self, 'current_bar_item')
                # Obtener color y tipo de línea configurados
                color = self.default_color_tiempo  # Color por defecto centralizado
                if hasattr(self, 'colorTiempo'):
                    color = self.get_color_str(self.colorTiempo)
                tipoLinea = "Sólida"
                if hasattr(self, 'cmbTipoLineaTiempo'):
                    tipoLinea = self.var_tipoLineaTiempo
                # Crear el pen según el tipo de línea
                if tipoLinea == "Sólida":
                    pen = pg.mkPen(color=color, width=2)
                elif tipoLinea == "Punteada":
                    pen = pg.mkPen(color=color, width=2, style=QtCore.Qt.DotLine)
                elif tipoLinea == "Rayada":
                    pen = pg.mkPen(color=color, width=2, style=QtCore.Qt.DashLine)
                else:
                    pen = pg.mkPen(color=color, width=2)
                # Crear la línea con el pen configurado
                self.plot_line = self.waveform1.plot([], [], pen=pen)
                self.plot_line.setData(xdata, ydata)
                self.waveform1.setXRange(xdata[0], xdata[-1])
                self.waveform1.setYRange(-1, 1)
                self.plot_line_freq.setData([], [])

            if self.btnFrecuencia.isChecked():
                # Graficar espectro de prueba fijo
                import numpy as np
                """ test_freqs = np.linspace(20, 20000, 100)
                test_amp = 20 * np.log10(np.abs(np.sin(np.linspace(0, 10, 100))) + 1e-2)
                self.waveform1.clear() """
                # Usar eje logarítmico para X
                if not hasattr(self, 'log_x_axis'):
                    self.log_x_axis = LogAxis(orientation='bottom')
                self.waveform1.setAxisItems({'bottom': self.log_x_axis})
                # ---
                # Determinar tipo de gráfico de espectro
                tipoGrafico = "Línea"
                
                tipoGrafico = self.var_tipoGraficoEspectro
                color = self.default_color_espectro  # Color por defecto centralizado
                if hasattr(self, 'colorEspectro'):
                    color = self.get_color_str(self.colorEspectro)
                if tipoGrafico in ["Barras-octavas", "Barras-tercios"] and device_num == 1 and len(fft_freqs) > 0:
                    # Calcular tercios de octava desde el modelo
                    if tipoGrafico == "Barras-octavas":
                        bandas, niveles = self.vController.cModel.calcular_octavas(fft_freqs, fft_magnitude)
                    elif tipoGrafico == "Barras-tercios":
                        bandas, niveles = self.vController.cModel.calcular_tercios_octava(fft_freqs, fft_magnitude)
                    else:
                        bandas, niveles = [], []
                    
                    print("bandas:", bandas)
                    print("niveles:", niveles)
                    
                    if len(bandas) > 0 and len(niveles) > 0:
                        self.waveform1.clear()
                        
                        # Crear un eje personalizado para las etiquetas de frecuencia
                        frequency_axis = FrequencyAxisItem(orientation='bottom', bandas=bandas)
                        self.waveform1.setAxisItems({'bottom': frequency_axis})
                        
                        # Usar posiciones secuenciales para las barras (0, 1, 2, 3...)
                        x_positions = np.arange(len(bandas))
                        
                        # Calcular anchos de barras uniformes
                        bar_width = 0.8  # Ancho fijo para todas las barras
                        
                        # Verificar que todos los arrays tengan la misma longitud
                        if len(x_positions) != len(niveles):
                            print(f"Error: Arrays con longitudes diferentes - x_positions: {len(x_positions)}, niveles: {len(niveles)}")
                            return
                        
                        # Crear el gráfico de barras
                        bar_item = pg.BarGraphItem(
                            x=x_positions, 
                            height=niveles, 
                            width=bar_width, 
                            brush=color,
                            pen=pg.mkPen(color='black', width=1)
                        )
                        self.waveform1.addItem(bar_item)
                        
                        for i, h in enumerate(niveles):
                            # Position the text slightly above the bar
                            text_item = pg.TextItem(text=f"{h:.2f}", anchor=(0.5, 0)) # Center horizontally, align to bottom of text
                            text_item.setPos(x_positions[i], h + 0.5) # Adjust 0.5 for desired offset
                            self.waveform1.addItem(text_item)
                            
                        # Configurar rangos de ejes
                        self.waveform1.setXRange(-0.5, len(bandas) - 0.5)
                        
                        # Rango Y dinámico basado en los niveles
                        y_min = np.min(niveles) if len(niveles) > 0 else 0
                        y_max = np.max(niveles) if len(niveles) > 0 else 1
                        y_range = y_max - y_min
                        if y_range == 0:
                            y_range = 1
                        
                        # Usar el mismo sistema de rango Y fijo que el gráfico de línea
                        if not hasattr(self, 'fft_ymin') or not hasattr(self, 'fft_ymax'):
                            self.fft_ymin = y_min
                            self.fft_ymax = y_max
                        else:
                            if y_min < self.fft_ymin:
                                self.fft_ymin = y_min
                            if y_max > self.fft_ymax:
                                self.fft_ymax = y_max
                        
                        self.waveform1.setYRange(self.fft_ymin, self.fft_ymax)
                        
                        # Etiquetas de ejes
                        self.waveform1.setLabel('left', 'Amplitud')
                        self.waveform1.setLabel('bottom', 'Frecuencia (Hz)')
                        
                        # Configurar modo lineal para ambos ejes
                        self.waveform1.setLogMode(x=False, y=False)
                        
                        # Limpiar línea de tiempo si existe
                        if hasattr(self, 'plot_line'):
                            self.plot_line.setData([], [])
                        
                        # Guardar referencia al item de barras para poder limpiarlo después
                        self.current_bar_item = bar_item
                        
                        print(f"Graficando barras: {len(bandas)} bandas, niveles: {niveles[:5]}...")
                        print(f"Posiciones X: {len(x_positions)} posiciones, valores: {x_positions[:5]}...")
                else:
                    # Por defecto, línea
                    if device_num == 1 and len(fft_freqs) > 0:
                        mask = (fft_freqs >= 20) & (fft_freqs <= 20000)
                        freqs_plot = fft_freqs[mask]
                        amp_plot = fft_magnitude[mask]
                        if len(freqs_plot) > 0:
                            self.waveform1.clear()
                            
                            # Limpiar barras anteriores si existen
                            if hasattr(self, 'current_bar_item'):
                                self.waveform1.removeItem(self.current_bar_item)
                                delattr(self, 'current_bar_item')
                            
                            self.waveform1.setAxisItems({'bottom': self.log_x_axis})
                            self.plot_line_freq = self.waveform1.plot(np.log10(freqs_plot), amp_plot, pen=pg.mkPen(color=color, width=2))
                            self.waveform1.setXRange(np.log10(20), np.log10(20000))
                            if not hasattr(self, 'fft_ymin') or not hasattr(self, 'fft_ymax'):
                                self.fft_ymin = np.min(amp_plot)
                                self.fft_ymax = np.max(amp_plot)
                            else:
                                if np.min(amp_plot) < self.fft_ymin:
                                    self.fft_ymin = np.min(amp_plot)
                                if np.max(amp_plot) > self.fft_ymax:
                                    self.fft_ymax = np.max(amp_plot)
                            self.waveform1.setYRange(self.fft_ymin, self.fft_ymax)
                        self.waveform1.setLabel('left', 'Amplitud')
                        self.waveform1.setLabel('bottom', 'Frecuencia (Hz)')
                        self.waveform1.setLogMode(x=False, y=False)
                        if hasattr(self, 'plot_line'):
                            self.plot_line.setData([], [])
                    else:
                        if hasattr(self, 'plot_line_freq') and self.plot_line_freq is not None:
                            self.plot_line_freq.setData([], [])
                            
            elif self.btnNivel.isChecked(): 
                import numpy as np
                # --- Gráfico de Nivel ---
                print("DEBUG: Actualizando gráfico de nivel")
                
                # Limpiar el gráfico completamente en cada actualización (como hace el gráfico de tiempo)
                self.waveform1.clear()
                
                # Configuración del gráfico de nivel
                self.waveform1.setLogMode(x=False, y=False)
                self.waveform1.setYRange(-150, 0, padding=0)  # Rango típico para dB
                
                # Obtener datos de nivel del controlador
                tiempos, niveles_Z, niveles_C, niveles_A = self.vController.get_nivel_data()
                
                if len(tiempos) > 0:
                    xdata = np.array(tiempos)
                    # Configurar el rango X basado en los datos reales
                    max_time = max(xdata) if len(xdata) > 0 else 10
                    self.waveform1.setXRange(0, max_time * 1.1, padding=0)  # 10% extra para visualización
                    
                    # Crear nuevas líneas de plot en cada actualización (como hace el gráfico de tiempo)
                    # --- Z Weighting ---
                    if self.cbNivPicoZ.isChecked() and len(niveles_Z['pico']) > 0:
                        ydata = np.array(niveles_Z['pico'])
                        print(f"DEBUG PICO Z: Graficando {len(ydata)} puntos, datos: {ydata}")
                        plot_line = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='red', width=2, style=QtCore.Qt.SolidLine), name='Z Pico')
                        print(f"DEBUG PICO Z: Plot creado: {plot_line}")
                    
                    if self.cbNivInstZ.isChecked() and len(niveles_Z['inst']) > 0:
                        ydata = np.array(niveles_Z['inst'])
                        print(f"DEBUG INST Z: Graficando {len(ydata)} puntos, datos: {ydata}")
                        plot_line = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='red', width=2, style=QtCore.Qt.DashLine), name='Z Inst')
                        print(f"DEBUG INST Z: Plot creado: {plot_line}")
                    
                    if self.cbNivFastZ.isChecked() and len(niveles_Z['fast']) > 0:
                        ydata = np.array(niveles_Z['fast'])
                        print(f"DEBUG FAST Z: Graficando {len(ydata)} puntos, datos: {ydata}")
                        plot_line = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='red', width=2, style=QtCore.Qt.DotLine), name='Z Fast')
                        print(f"DEBUG FAST Z: Plot creado: {plot_line}")
                    
                    if self.cbNivSlowZ.isChecked() and len(niveles_Z['slow']) > 0:
                        ydata = np.array(niveles_Z['slow'])
                        print(f"DEBUG SLOW Z: Graficando {len(ydata)} puntos, datos: {ydata}")
                        plot_line = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='red', width=3, style=QtCore.Qt.SolidLine), name='Z Slow')
                        print(f"DEBUG SLOW Z: Plot creado: {plot_line}")
                    
                    # --- C Weighting ---
                    if self.cbNivPicoC.isChecked() and len(niveles_C['pico']) > 0:
                        ydata = np.array(niveles_C['pico'])
                        plot_line = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='green', width=2, style=QtCore.Qt.SolidLine), name='C Pico')
                    
                    if self.cbNivInstC.isChecked() and len(niveles_C['inst']) > 0:
                        ydata = np.array(niveles_C['inst'])
                        plot_line = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='green', width=2, style=QtCore.Qt.DashLine), name='C Inst')
                    
                    if self.cbNivFastC.isChecked() and len(niveles_C['fast']) > 0:
                        ydata = np.array(niveles_C['fast'])
                        plot_line = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='green', width=2, style=QtCore.Qt.DotLine), name='C Fast')
                    
                    if self.cbNivSlowC.isChecked() and len(niveles_C['slow']) > 0:
                        ydata = np.array(niveles_C['slow'])
                        plot_line = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='green', width=3, style=QtCore.Qt.SolidLine), name='C Slow')
                    
                    # --- A Weighting ---
                    if self.cbNivPicoA.isChecked() and len(niveles_A['pico']) > 0:
                        ydata = np.array(niveles_A['pico'])
                        plot_line = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='blue', width=2, style=QtCore.Qt.SolidLine), name='A Pico')
                    
                    if self.cbNivInstA.isChecked() and len(niveles_A['inst']) > 0:
                        ydata = np.array(niveles_A['inst'])
                        plot_line = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='blue', width=2, style=QtCore.Qt.DashLine), name='A Inst')
                    
                    if self.cbNivFastA.isChecked() and len(niveles_A['fast']) > 0:
                        ydata = np.array(niveles_A['fast'])
                        plot_line = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='blue', width=2, style=QtCore.Qt.DotLine), name='A Fast')
                    
                    if self.cbNivSlowA.isChecked() and len(niveles_A['slow']) > 0:
                        ydata = np.array(niveles_A['slow'])
                        plot_line = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='blue', width=3, style=QtCore.Qt.SolidLine), name='A Slow')
                    
                    # Ajustar rango X para mostrar los últimos 10 segundos
                    if len(xdata) > 0:
                        self.waveform1.setXRange(max(0, xdata[-1]-10), xdata[-1])
                    
                    print(f"DEBUG: Niveles actualizados - Z: {niveles_Z['slow'][-1]:.1f} dB, C: {niveles_C['slow'][-1]:.1f} dB, A: {niveles_A['slow'][-1]:.1f} dB")
                else:
                    print("DEBUG: No hay datos de nivel para graficar")
                    
        except Exception as e:
            print(f"Error en update_plot: {e}")
    
    
    def importarSenalCalibracion(self):
        """Abre un diálogo para seleccionar un archivo .wav y guarda su ruta."""
        try:
            fileName, _ = QFileDialog.getOpenFileName(
                self.calWin,
                "Seleccionar Archivo de Audio de Referencia",
                "",
                "Archivos de audio (*.wav)"
            )

            if fileName:
                # Enviar la ruta completa al controlador para que el modelo la guarde
                self.vController.establecer_ruta_archivo_calibracion(fileName)
                # Opcional: mostrar el nombre del archivo en algún label si existe
                QMessageBox.information(self.calWin, "Archivo Seleccionado", f"Archivo de referencia:\n{os.path.basename(fileName)}")

        except Exception as e:
            QMessageBox.critical(self.calWin, "Error", f"Error al importar archivo: {str(e)}")
            print(f"Error en importarSenalCalibracion: {e}")
    
    
    def aplicarConfiguracionExterna(self, config):
        """Aplica la configuración recibida desde la ventana externa de configuración"""
        try:
            # Guardar configuración en variables de clase
            # Configuración de tiempo
            self.var_logModeXTiempo = config['tiempo']['logModeX']
            self.var_logModeYTiempo = config['tiempo']['logModeY']
            self.var_xMinTiempo = config['tiempo']['xMin']
            self.var_xMaxTiempo = config['tiempo']['xMax']
            self.var_yMinTiempo = config['tiempo']['yMin']
            self.var_yMaxTiempo = config['tiempo']['yMax']
            self.var_etiquetaXTiempo = config['tiempo']['etiquetaX']
            self.var_etiquetaYTiempo = config['tiempo']['etiquetaY']
            self.var_tipoLineaTiempo = config['tiempo']['tipoLinea']
            
            # Configuración de espectro
            self.var_logModeXEspectro = config['espectro']['logModeX']
            self.var_logModeYEspectro = config['espectro']['logModeY']
            self.var_xMinEspectro = config['espectro']['xMin']
            self.var_xMaxEspectro = config['espectro']['xMax']
            self.var_yMinEspectro = config['espectro']['yMin']
            self.var_yMaxEspectro = config['espectro']['yMax']
            self.var_etiquetaXEspectro = config['espectro']['etiquetaX']
            self.var_etiquetaYEspectro = config['espectro']['etiquetaY']
            self.var_tipoGraficoEspectro = config['espectro']['tipoGrafico']
            
            # Configuración de nivel
            self.var_logModeYNivel = config['nivel']['logModeY']
            self.var_xMinNivel = config['nivel']['xMin']
            self.var_xMaxNivel = config['nivel']['xMax']
            self.var_yMinNivel = config['nivel']['yMin']
            self.var_yMaxNivel = config['nivel']['yMax']
            self.var_etiquetaXNivel = config['nivel']['etiquetaX']
            self.var_etiquetaYNivel = config['nivel']['etiquetaY']
            self.var_tipoLineaNivel = config['nivel']['tipoLinea']
            
            # Aplicar configuración según el gráfico activo
            if self.btnTiempo.isChecked():
                self.aplicarConfiguracionTiempo()
            elif self.btnFrecuencia.isChecked():
                self.aplicarConfiguracionEspectro()
            elif self.btnNivel.isChecked():
                self.aplicarConfiguracionNivel()
            
            # Actualizar el gráfico
            self.waveform1.replot()
            
            print("Configuración aplicada exitosamente")
            
        except Exception as e:
            print(f"Error al aplicar configuración externa: {e}")

    # 4. MODIFICAR LA FUNCIÓN closeEvent() para incluir la nueva ventana:
    def closeEvent(self, event):
        """Se ejecuta cuando se cierra la ventana principal"""
        # Cerrar todas las ventanas secundarias
        if hasattr(self, 'calWin') and self.calWin and self.calWin.isVisible():
            self.calWin.close()
        if hasattr(self, 'confWin') and self.confWin and self.confWin.isVisible():
            self.confWin.close()  # Esta línea ya funciona con la nueva ventana
        if hasattr(self, 'confDispWin') and self.confDispWin and self.confDispWin.isVisible():
            self.confDispWin.close()
        if hasattr(self, 'calAutWin') and self.calAutWin and self.calAutWin.isVisible():
            self.calAutWin.close()
        if hasattr(self, 'calManWin') and self.calManWin and self.calManWin.isVisible():
            self.calManWin.close()
        if hasattr(self, 'calFEWin') and self.calFEWin and self.calFEWin.isVisible():
            self.calFEWin.close()
        
        # Aceptar el evento de cierre
        event.accept()
        
