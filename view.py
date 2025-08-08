# Importo librerias

#import Librerias graficas
# from tkinter import Y
# from PyQt5.QtWidgets import * 

import pyqtgraph as pg

from PyQt5.QtWidgets import QMainWindow, QApplication, QHBoxLayout, QVBoxLayout, QTabWidget, QPushButton
from PyQt5.QtWidgets import QLabel, QLineEdit, QGroupBox, QRadioButton, QCheckBox, QAction, QWidget, QGridLayout
from PyQt5.QtWidgets import QMenu, QTextEdit, QMessageBox, QColorDialog, QFrame, QComboBox, QFileDialog, QGraphicsOpacityEffect

from PyQt5.QtGui import QPixmap, QIcon, QPainter, QColor
from PyQt5.QtCore import QRect, QPointF
# from PyQt5 import QtWidgets
from pyqtgraph.Qt import QtGui, QtCore

# Imports para QChart (solo para la ventana de calibración)
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QBarSeries, QBarSet, QBarCategoryAxis
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen

# from pyqtgraph.Point import Point

#import utilidades del sistema
import sys
import os

import numpy as np

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

class vista(QMainWindow):

    def norm(self, x, y, ancho, alto):
        return QtCore.QRect(int(self.anchoX * x), int(self.altoY * y), int(self.anchoX * ancho), int(self.altoY * alto))

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
        
        with open("estilos.qss", "r", encoding='utf-8') as f:
            self.app.setStyleSheet(f.read())
    
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
        self.var_colorTiempo=""
        self.var_colorEspectro=""
        self.var_colorNivel=""
        
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
        self.btn.setToolTip("Importar señal de audio de un archivo .Nuse")
        self.btn.clicked.connect(self.importSignal)
        self.btngbr = QPushButton("Grabar")
        self.btngbr.setToolTip("Iniciar Grabacion de audio")
        self.btngbr.setCheckable(True)
        self.btngbr.clicked.connect(self.grabar)
        
        # Agregar icono de play al botón
        # Intentar cargar icono personalizado desde archivo PNG
        icon_play_path = "img/boton-de-play.png" 
        self.btngbr.setIcon(QIcon(icon_play_path))
        icon_import_path = "img/importar.png"
        self.btn.setIcon(QIcon(icon_import_path))
        
        # Estilo para los botones con padding y bordes redondeados
        button_style = """
        QPushButton {
            padding: 10px 20px;
            border-radius: 8px;
            border: 2px solid #cccccc;
            background-color: #f0f0f0;
            font-weight: bold;
            font-size: 12px;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
            border-color: #999999;
        }
        QPushButton:pressed {
            background-color: #d0d0d0;
            border-color: #666666;
        }
        QPushButton:checked {
            background-color: #4CAF50;
            color: white;
            border-color: #45a049;
        }
        """
        
        # Aplicar estilo a ambos botones
        self.btn.setStyleSheet(button_style)
        self.btngbr.setStyleSheet(button_style)
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
        self.ram = QLabel("Ram")
        self.ram.setAlignment(QtCore.Qt.AlignCenter)
        self.ram.setStyleSheet("background-color: lightblue; font-size:11pt; color: white;")
        
        tipoGraficoLayout.addLayout(botonesLayout, 75)
        tipoGraficoLayout.addWidget(self.ram, 25)
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

        self.show() 

    def iniciarCalibracion(self):
        if self.radioBtnAutomatica.isChecked():
            self.vController.calAutomatica()
        elif self.radioBtnRelativa.isChecked():
            self.vController.calRelativa()

    def importSignal(self):
        self.vController.importSignal() # conexion con el controlador

    def grabar(self):
        self.vController.dalePlay() # conexion con el controlador

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
    
    def closeEvent(self, event):
        """Se ejecuta cuando se cierra la ventana principal"""
        # Cerrar todas las ventanas secundarias
        if hasattr(self, 'calWin') and self.calWin.isVisible():
            self.calWin.close()
        if hasattr(self, 'confWin') and self.confWin.isVisible():
            self.confWin.close()
        if hasattr(self, 'confDispWin') and self.confDispWin.isVisible():
            self.confDispWin.close()
        if hasattr(self, 'calAutWin') and self.calAutWin.isVisible():
            self.calAutWin.close()
        if hasattr(self, 'calManWin') and self.calManWin.isVisible():
            self.calManWin.close()
        if hasattr(self, 'calFEWin') and self.calFEWin.isVisible():
            self.calFEWin.close()
        
        # Aceptar el evento de cierre
        event.accept()
        
    def calibracionAutomatica(self):
        self.calAutWin = QMainWindow()
        self.calAutWin.setWindowTitle("Calibracion Automatica") 
        self.calAutWin.setGeometry(self.norm(0.2, 0.3, 0.4, 0.4))

        #Descripcion de la calibracion
        self.descripcionMenu = QLabel("Se precisa de una fuente externa o bien se puede usar el generador de señales. Se realizará una captura de sonido durante 3 segundos y usted debera indicar el nivel medido por su instrumento patrón", self.calAutWin)
        self.descripcionMenu.setWordWrap(True)
        self.descripcionMenu.setGeometry(self.norm(0.02, 0.02, 0.6, 0.4))
        self.descripcionMenu.setStyleSheet("font: 13pt")

        # Cuadro de texto de la medicion
        self.txDecMed = QLabel("80.0 [dB]", self.calAutWin)
        self.txDecMed.setGeometry(self.norm(0.65, 0.1, 0.3, 0.15))
        self.txDecMed.setStyleSheet("font: bold 12pt")

        # cuador de texto del seteo
        self.txDecIn = QTextEdit("75.0 [dB]", self.calAutWin)
        self.txDecIn.setGeometry(self.norm(0.65, 0.3, 0.3, 0.15))
        self.txDecIn.setStyleSheet("font: bold 12pt")

        # Botones de aceptar cancelar y generador
        self.btnAcept = QPushButton("Calibrar", self.calAutWin)
        self.btnAcept.clicked.connect(self.fnCalibrar)
        
        self.btnCance = QPushButton("Cancelar", self.calAutWin)
        self.btnCance.clicked.connect(self.fnCancelar)
        
        self.btnGener = QPushButton("Generador", self.calAutWin)
        self.btnGener.clicked.connect(self.fnGenerador)

        self.btnAcept.setGeometry(self.norm(0.02, 0.8, 0.25, 0.1))
        self.btnCance.setGeometry(self.norm(0.3, 0.8, 0.25, 0.1))
        self.btnGener.setGeometry(self.norm(0.58, 0.8, 0.25, 0.1))

        self.calAutWin.show()

    def calibracionManual(self):
        self.calManWin = QMainWindow()
        self.calManWin.setWindowTitle("Calibracion Manual") 
        self.calManWin.setGeometry(self.norm(0.2, 0.2, 0.6, 0.6))
        self.calManWin.show() 

    def calibracionFondoEscala(self):
        self.calFEWin = QMainWindow()
        self.calFEWin.setWindowTitle("Calibracion a Fondo de escala") 
        self.calFEWin.setGeometry(self.norm(0.2, 0.2, 0.6, 0.6))
        self.calFEWin.show() 

    # funciones

    def fnCalibrar(self):
        self.btnAcept.setText("Aceptar")
        self.vController.calAutomatica()

    def fnCancelar(self):
        pass

    def fnGenerador(self):
        pass

    def abrirSitioCintra(self):
        """Abre el sitio web de CINTRA en el navegador predeterminado"""
        import webbrowser
        try:
            webbrowser.open("https://cintra.ar")
        except Exception as e:
            print(f"Error al abrir el sitio web de CINTRA: {e}")

    def actualizarEscala(self):
        """Actualiza la escala del gráfico según los checkboxes seleccionados"""
        try:
            # Obtener el estado de los checkboxes
            escalaX = self.cbEscalaX.isChecked()
            escalaY = self.cbEscalaY.isChecked()
            
            # Aplicar la escala al gráfico
            self.waveform1.setLogMode(x=escalaX, y=escalaY)
            
            # Actualizar el gráfico
            self.waveform1.replot()
            
        except Exception as e:
            print(f"Error al actualizar escala: {e}")

    def aplicarLimitesX(self):
        """Aplica los límites del eje X al gráfico"""
        try:
            # Obtener los valores de los campos de texto
            x_min = float(self.txtXMin.text())
            x_max = float(self.txtXMax.text())
            
            # Validar que el mínimo sea menor que el máximo
            if x_min >= x_max:
                QMessageBox.warning(self, "Error", "El valor mínimo debe ser menor que el máximo")
                return
            
            # Aplicar los límites al gráfico
            self.waveform1.setXRange(x_min, x_max, padding=0)
            
            # Actualizar el gráfico
            self.waveform1.replot()
            
        except ValueError:
            QMessageBox.warning(self, "Error", "Por favor ingrese valores numéricos válidos")
        except Exception as e:
            print(f"Error al aplicar límites X: {e}")

    def aplicarLimitesY(self):
        """Aplica los límites del eje Y al gráfico"""
        try:
            # Obtener los valores de los campos de texto
            y_min = float(self.txtYMin.text())
            y_max = float(self.txtYMax.text())
            
            # Validar que el mínimo sea menor que el máximo
            if y_min >= y_max:
                QMessageBox.warning(self, "Error", "El valor mínimo debe ser menor que el máximo")
                return
            
            # Aplicar los límites al gráfico
            self.waveform1.setYRange(y_min, y_max, padding=0)
            
            # Actualizar el gráfico
            self.waveform1.replot()
            
        except ValueError:
            QMessageBox.warning(self, "Error", "Por favor ingrese valores numéricos válidos")
        except Exception as e:
            print(f"Error al aplicar límites Y: {e}")

    def aplicarEtiquetas(self):
        """Aplica las etiquetas de los ejes al gráfico"""
        try:
            # Obtener las etiquetas de los campos de texto
            etiqueta_x = self.txtEtiquetaX.text()
            etiqueta_y = self.txtEtiquetaY.text()
            
            # Aplicar las etiquetas al gráfico
            self.waveform1.setLabel('bottom', etiqueta_x)
            self.waveform1.setLabel('left', etiqueta_y)
            
            # Actualizar el gráfico
            self.waveform1.replot()
            
        except Exception as e:
            print(f"Error al aplicar etiquetas: {e}")

    def aplicarconfiguracion(self):
        """Aplica la configuración personalizada según el tipo de gráfico seleccionado"""
        try:
            # Guardar la configuración actual
            self.guardarConfiguracion()
            
            if self.btnTiempo.isChecked():
                # Aplicar configuración personalizada para gráfico de tiempo
                self.aplicarConfiguracionTiempo()
                
            elif self.btnFrecuencia.isChecked():
                # Aplicar configuración personalizada para gráfico de frecuencia
                self.aplicarConfiguracionEspectro()
                
            elif self.btnNivel.isChecked():
                # Aplicar configuración personalizada para gráfico de nivel
                self.aplicarConfiguracionNivel()
            
            # Actualizar el gráfico
            self.waveform1.replot()
            
            # Cerrar la ventana de configuración
            self.confWin.close()
            
        except Exception as e:
            print(f"Error en configuración automática: {e}")

    def guardarConfiguracion(self):
        """Guarda la configuración actual en las variables de configuración"""
        try:
            # Guardar configuración de tiempo
            if hasattr(self, 'cbEscalaXTiempo'):
                self.var_logModeXTiempo = self.cbEscalaXTiempo.isChecked()
            if hasattr(self, 'cbEscalaYTiempo'):
                self.var_logModeYTiempo = self.cbEscalaYTiempo.isChecked()
            if hasattr(self, 'txtXMinTiempo'):
                self.var_xMinTiempo = float(self.txtXMinTiempo.text())
            if hasattr(self, 'txtXMaxTiempo'):
                self.var_xMaxTiempo = float(self.txtXMaxTiempo.text())
            if hasattr(self, 'txtYMinTiempo'):
                self.var_yMinTiempo = float(self.txtYMinTiempo.text())
            if hasattr(self, 'txtYMaxTiempo'):
                self.var_yMaxTiempo = float(self.txtYMaxTiempo.text())
            if hasattr(self, 'txtEtiquetaXTiempo'):
                self.var_etiquetaXTiempo = self.txtEtiquetaXTiempo.text()
            if hasattr(self, 'txtEtiquetaYTiempo'):
                self.var_etiquetaYTiempo = self.txtEtiquetaYTiempo.text()
            # Guardar tipo de línea y color de tiempo
            if hasattr(self, 'cmbTipoLineaTiempo'):
                self.var_tipoLineaTiempo = self.cmbTipoLineaTiempo.currentText()
            if hasattr(self, 'colorTiempo'):
                self.var_colorTiempo = self.colorTiempo.name()
            # Guardar configuración de espectro
            if hasattr(self, 'cbEscalaXEspectro'):
                self.var_logModeXEspectro = self.cbEscalaXEspectro.isChecked()
            if hasattr(self, 'cbEscalaYEspectro'):
                self.var_logModeYEspectro = self.cbEscalaYEspectro.isChecked()
            if hasattr(self, 'txtXMinEspectro'):
                self.var_xMinEspectro = float(self.txtXMinEspectro.text())
            if hasattr(self, 'txtXMaxEspectro'):
                self.var_xMaxEspectro = float(self.txtXMaxEspectro.text())
            if hasattr(self, 'txtYMinEspectro'):
                self.var_yMinEspectro = float(self.txtYMinEspectro.text())
            if hasattr(self, 'txtYMaxEspectro'):
                self.var_yMaxEspectro = float(self.txtYMaxEspectro.text())
            if hasattr(self, 'txtEtiquetaXEspectro'):
                self.var_etiquetaXEspectro = self.txtEtiquetaXEspectro.text()
            if hasattr(self, 'txtEtiquetaYEspectro'):
                self.var_etiquetaYEspectro = self.txtEtiquetaYEspectro.text()
            # Guardar tipo de gráfico y color de espectro
            if hasattr(self, 'cmbTipoGraficoEspectro'):
                self.var_tipoGraficoEspectro = self.cmbTipoGraficoEspectro.currentText()
            if hasattr(self, 'colorEspectro'):
                self.var_colorEspectro = self.colorEspectro.name()
            # Guardar configuración de nivel
            if hasattr(self, 'cbEscalaYNivel'):
                self.var_logModeYNivel = self.cbEscalaYNivel.isChecked()
            if hasattr(self, 'txtXMinNivel'):
                self.var_xMinNivel = float(self.txtXMinNivel.text())
            if hasattr(self, 'txtXMaxNivel'):
                self.var_xMaxNivel = float(self.txtXMaxNivel.text())
            if hasattr(self, 'txtYMinNivel'):
                self.var_yMinNivel = float(self.txtYMinNivel.text())
            if hasattr(self, 'txtYMaxNivel'):
                self.var_yMaxNivel = float(self.txtYMaxNivel.text())
            if hasattr(self, 'txtEtiquetaXNivel'):
                self.var_etiquetaXNivel = self.txtEtiquetaXNivel.text()
            if hasattr(self, 'txtEtiquetaYNivel'):
                self.var_etiquetaYNivel = self.txtEtiquetaYNivel.text()
            # Guardar tipo de línea y color de nivel
            if hasattr(self, 'cmbTipoLineaNivel'):
                self.var_tipoLineaNivel = self.cmbTipoLineaNivel.currentText()
            if hasattr(self, 'colorNivel'):
                self.var_colorNivel = self.colorNivel.name()
        except Exception as e:
            print(f"Error al guardar configuración: {e}")

    def aplicarConfiguracionTiempo(self):
        """Aplica la configuración personalizada para el gráfico de tiempo"""
        try:
            # Escalas
            escalaX = self.cbEscalaXTiempo.isChecked()
            self.var_logModeXTiempo = escalaX
            escalaY = self.cbEscalaYTiempo.isChecked()
            self.var_logModeYTiempo = escalaY
            self.waveform1.setLogMode(x=escalaX, y=escalaY)
            
            # Límites
            x_min = float(self.txtXMinTiempo.text())
            x_max = float(self.txtXMaxTiempo.text())
            y_min = float(self.txtYMinTiempo.text())
            y_max = float(self.txtYMaxTiempo.text())
            
            # Guardar límites en variables de configuración
            self.var_xMinTiempo = x_min
            self.var_xMaxTiempo = x_max
            self.var_yMinTiempo = y_min
            self.var_yMaxTiempo = y_max
            
            self.waveform1.setXRange(x_min, x_max, padding=0)
            self.waveform1.setYRange(y_min, y_max, padding=0)
            
            # Etiquetas
            etiqueta_x = self.txtEtiquetaXTiempo.text()
            etiqueta_y = self.txtEtiquetaYTiempo.text()
            
            # Guardar etiquetas en variables de configuración
            self.var_etiquetaXTiempo = etiqueta_x
            self.var_etiquetaYTiempo = etiqueta_y
            
            self.waveform1.setLabel('bottom', etiqueta_x)
            self.waveform1.setLabel('left', etiqueta_y)
            
            # Color y tipo de línea
            if hasattr(self, 'colorTiempo'):
                color = self.colorTiempo.name()
            else:
                color = "#8A0101"  # Color por defecto
            
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
            escalaX = self.cbEscalaXEspectro.isChecked()
            self.var_logModeXEspectro = escalaX
            escalaY = self.cbEscalaYEspectro.isChecked()
            self.var_logModeYEspectro = escalaY
            self.waveform1.setLogMode(x=escalaX, y=escalaY)
            
            # Límites
            x_min = float(self.txtXMinEspectro.text())
            x_max = float(self.txtXMaxEspectro.text())
            y_min = float(self.txtYMinEspectro.text())
            y_max = float(self.txtYMaxEspectro.text())
            
            # Guardar límites en variables de configuración
            self.var_xMinEspectro = x_min
            self.var_xMaxEspectro = x_max
            self.var_yMinEspectro = y_min
            self.var_yMaxEspectro = y_max
            
            self.waveform1.setXRange(x_min, x_max, padding=0)
            self.waveform1.setYRange(y_min, y_max, padding=0)
            
            # Etiquetas
            etiqueta_x = self.txtEtiquetaXEspectro.text()
            etiqueta_y = self.txtEtiquetaYEspectro.text()
            
            # Guardar etiquetas en variables de configuración
            self.var_etiquetaXEspectro = etiqueta_x
            self.var_etiquetaYEspectro = etiqueta_y
            
            self.waveform1.setLabel('bottom', etiqueta_x)
            self.waveform1.setLabel('left', etiqueta_y)
            
            # Color y tipo de gráfico
            if hasattr(self, 'colorEspectro'):
                color = self.colorEspectro.name()
            else:
                color = "#8A3F01"  # Color por defecto
            
            tipoGrafico = self.obtenerTipoGraficoEspectro()
            self.actualizarEstiloGraficoEspectro(color, tipoGrafico)
            
        except Exception as e:
            print(f"Error al aplicar configuración de espectro: {e}")

    def aplicarConfiguracionNivel(self):
        """Aplica la configuración personalizada para el gráfico de nivel"""
        try:
            # Escalas
            escalaY = self.cbEscalaYNivel.isChecked()
            self.var_logModeYNivel = escalaY
            self.waveform1.setLogMode(x=False, y=escalaY)
            
            # Límites
            x_min = float(self.txtXMinNivel.text())
            x_max = float(self.txtXMaxNivel.text())
            y_min = float(self.txtYMinNivel.text())
            y_max = float(self.txtYMaxNivel.text())
            
            # Guardar límites en variables de configuración
            self.var_xMinNivel = x_min
            self.var_xMaxNivel = x_max
            self.var_yMinNivel = y_min
            self.var_yMaxNivel = y_max
            
            self.waveform1.setXRange(x_min, x_max, padding=0)
            self.waveform1.setYRange(y_min, y_max, padding=0)
            
            # Etiquetas
            etiqueta_x = self.txtEtiquetaXNivel.text()
            etiqueta_y = self.txtEtiquetaYNivel.text()
            
            # Guardar etiquetas en variables de configuración
            self.var_etiquetaXNivel = etiqueta_x
            self.var_etiquetaYNivel = etiqueta_y
            
            self.waveform1.setLabel('bottom', etiqueta_x)
            self.waveform1.setLabel('left', etiqueta_y)
            
            # Color y tipo de línea
            if hasattr(self, 'colorNivel'):
                color = self.colorNivel.name()
            else:
                color = "#000000"  # Color por defecto
            
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
            elif tipoGrafico == "Barras":
                # Para gráfico de barras, el estilo se maneja en update_plot
                # Aquí solo guardamos el color para usar en las barras
                if hasattr(self, 'colorEspectro'):
                    self.colorEspectro = color
                # Limpiar el gráfico para que se actualice en el próximo update_plot
                if hasattr(self, 'waveform1'):
                    self.waveform1.clear()
            
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
            return self.cmbTipoLineaTiempo.currentText()
        elif tipoGrafico == "nivel":
            return self.cmbTipoLineaNivel.currentText()
        return "Sólida"  # Valor por defecto

    def obtenerTipoGraficoEspectro(self):
        """Obtiene el tipo de gráfico seleccionado para el espectro"""
        return self.cmbTipoGraficoEspectro.currentText()

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
                color = "#8A0101"  # Color por defecto
                if hasattr(self, 'colorTiempo'):
                    color = self.colorTiempo.name()
                tipoLinea = "Sólida"
                if hasattr(self, 'cmbTipoLineaTiempo'):
                    tipoLinea = self.cmbTipoLineaTiempo.currentText()
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
                if hasattr(self, 'cmbTipoGraficoEspectro'):
                    tipoGrafico = self.cmbTipoGraficoEspectro.currentText()
                color = '#8A3F01'
                if hasattr(self, 'colorEspectro'):
                    color = self.colorEspectro.name()
                if tipoGrafico == "Barras" and device_num == 1 and len(fft_freqs) > 0:
                    # Calcular tercios de octava desde el modelo
                    bandas, niveles = self.vController.cModel.calcular_tercios_octava(fft_freqs, fft_magnitude)
                    
                    if len(bandas) > 0 and len(niveles) > 0:
                        self.waveform1.clear()
                        
                        # Usar eje logarítmico para X
                        if not hasattr(self, 'log_x_axis'):
                            self.log_x_axis = LogAxis(orientation='bottom')
                        self.waveform1.setAxisItems({'bottom': self.log_x_axis})
                        
                        # Calcular anchos de barras proporcionales a las bandas de frecuencia
                        # Para tercios de octava, cada banda es 2^(1/3) veces la anterior
                        log_bandas = np.log10(bandas)
                        
                        # Calcular anchos de barras
                        if len(bandas) > 1:
                            # Para múltiples bandas, calcular el ancho basado en la diferencia entre bandas
                            widths = np.diff(log_bandas) * 0.8  # 0.8 para dejar espacio entre barras
                            # Agregar un ancho para la última banda (aproximadamente igual al anterior)
                            if len(widths) > 0:
                                widths = np.append(widths, widths[-1])
                        else:
                            # Si solo hay una banda, usar un ancho por defecto
                            widths = [0.1]
                        
                        # Verificar que todos los arrays tengan la misma longitud
                        if len(log_bandas) != len(niveles) or len(log_bandas) != len(widths):
                            print(f"Error: Arrays con longitudes diferentes - log_bandas: {len(log_bandas)}, niveles: {len(niveles)}, widths: {len(widths)}")
                            return
                        
                        # Crear el gráfico de barras
                        bar_item = pg.BarGraphItem(
                            x=log_bandas, 
                            height=niveles, 
                            width=widths, 
                            brush=color,
                            pen=pg.mkPen(color='black', width=1)
                        )
                        self.waveform1.addItem(bar_item)
                        
                        # Configurar rangos de ejes
                        self.waveform1.setXRange(np.log10(20), np.log10(20000))
                        
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
                        
                        # Configurar modo logarítmico para X
                        self.waveform1.setLogMode(x=False, y=False)
                        
                        # Limpiar línea de tiempo si existe
                        if hasattr(self, 'plot_line'):
                            self.plot_line.setData([], [])
                        
                        # Guardar referencia al item de barras para poder limpiarlo después
                        self.current_bar_item = bar_item
                        
                        print(f"Graficando barras: {len(bandas)} bandas, niveles: {niveles[:5]}...")
                        print(f"Anchos de barras: {len(widths)} anchos, valores: {widths[:5]}...")
                        print(f"Posiciones X: {len(log_bandas)} posiciones, valores: {log_bandas[:5]}...")
                    else:
                        print("No hay datos de tercios de octava disponibles")
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
    
    # CODIGO configuracion de calibración
    def calibracionWin(self):
        self.calWin = QMainWindow()
        self.calWin.setWindowTitle("Calibracion")
        self.calWin.setGeometry(self.norm(0.4, 0.3, 0.2, 0.4))
            
        # Widget central y layout principal
        centralWidget = QWidget()
        self.calWin.setCentralWidget(centralWidget)
        mainLayout = QVBoxLayout(centralWidget)
            
        tipoCalLayoutHori = QHBoxLayout()
        tipoCalLayoutVer = QVBoxLayout()
        confHardLayout = QHBoxLayout()
        valorRefLayout = QHBoxLayout()
        botonesLayout = QHBoxLayout()
            
        self.lblTipoCal = QLabel("Tipo de Calibracion:")
        tipoCalLayoutHori.addWidget(self.lblTipoCal)
            
        self.radioBtnRelativa = QRadioButton("Calibración relativa")
        self.radioBtnRelativa.setChecked(True) 
        self.radioBtnRelativa.toggled.connect(self.toggleValRef)
        tipoCalLayoutVer.addWidget(self.radioBtnRelativa)

        self.radioBtnAutomatica = QRadioButton("Calibración automatica (fondo de escala)")
        tipoCalLayoutVer.addWidget(self.radioBtnAutomatica)

        self.radioBtnExterna = QRadioButton("Calibración externa")
        self.radioBtnExterna.toggled.connect(self.toggleImportButton)
        tipoCalLayoutVer.addWidget(self.radioBtnExterna)
            
        tipoCalLayoutHori.addLayout(tipoCalLayoutVer)
        tipoCalLayoutHori.addStretch()
            
        self.lblDispEnt = QLabel("Dispositivo de entrada: ")
        confHardLayout.addWidget(self.lblDispEnt)
        self.lblConfHard = QLabel("")
        confHardLayout.addWidget(self.lblConfHard)
        self.btnConfHard = QPushButton("Configurar Dispositivo")
        confHardLayout.addWidget(self.btnConfHard)
        self.btnConfHard.clicked.connect(self.configuracionDispositivo)
            
        self.lblValRef = QLabel("Valor de Referencia:")
        valorRefLayout.addWidget(self.lblValRef)
        self.txtValorRef = QLineEdit("")
        valorRefLayout.addWidget(self.txtValorRef)
            
        self.btnImportSig = QPushButton("Importar Señal")
        self.btnImportSig.setEnabled(False)
        self.btnImportSig.setToolTip("Importar desde archivo .wav")
        self.btnImportSig.clicked.connect(self.importarSenalCalibracion)
            
        # Crear QChart para la ventana de calibración
        self.chart2 = QChart()
        self.chart2.setTheme(QChart.ChartThemeDark)
            
        # Crear QChartView para mostrar el gráfico
        self.winGraph2 = QChartView(self.chart2)
        self.winGraph2.setRenderHint(QPainter.Antialiasing)
            
        # Crear series para el gráfico de calibración
        self.plot_line_cal = QLineSeries()
            
        # Configurar ejes para el gráfico de calibración
        self.axisX2 = QValueAxis()
        self.axisX2.setTitleText("Tiempo")
        self.axisX2.setRange(0, 1024)
            
        self.axisY2 = QValueAxis()
        self.axisY2.setTitleText("Amplitud Normalizada")
        self.axisY2.setRange(-1.2, 1.2)
            
        self.chart2.setAxisX(self.axisX2, self.plot_line_cal)
        self.chart2.setAxisY(self.axisY2, self.plot_line_cal)
        self.chart2.legend().hide()

        # Definir las líneas del gráfico (para compatibilidad)
        self.ptdomTiempo2 = self.plot_line_cal
        self.ptdomEspect2 = self.plot_line_cal
            
        self.btnCalibrar = QPushButton("Calibrar")
        self.btnRepetir = QPushButton("Repetir")
        self.btnGenerador = QPushButton("Generador de señales")
        self.btnGenerador.clicked.connect(self.generadorWin)
        self.btnCancel = QPushButton("Cancelar")
        self.btnCancel.clicked.connect(self.closeCalibracion)
        botonesLayout.addWidget(self.btnCalibrar)
        botonesLayout.addWidget(self.btnRepetir)
        botonesLayout.addWidget(self.btnGenerador)
        botonesLayout.addWidget(self.btnCancel)
            
        # Agregar el grupo al layout principal
        mainLayout.addLayout(tipoCalLayoutHori)
        mainLayout.addLayout(confHardLayout)
        mainLayout.addLayout(valorRefLayout)
        #mainLayout.addLayout(importLayout)
        mainLayout.addWidget(self.btnImportSig)
        mainLayout.addWidget(self.winGraph2)
        mainLayout.addLayout(botonesLayout)
                    
        # Actualizar el nombre del dispositivo actual en el label
        self.actualizarNombreDispositivo()
            
        for boton in [self.btnCalibrar, self.btnRepetir, self.btnGenerador, self.btnCancel, self.btnConfHard, self.btnImportSig]:
            boton.setProperty("class", "ventanasSec")

        for radio in [self.radioBtnAutomatica, self.radioBtnExterna, self.radioBtnRelativa]:
            radio.setProperty("class", "ventanasSec")
            
        for lbl in [self.lblDispEnt, self.lblValRef, self.lblTipoCal]:
            lbl.setProperty("class", "ventanasSecLabelDestacado")    
                
        self.winGraph2.setVisible(self.radioBtnExterna.isChecked())
        self.radioBtnExterna.toggled.connect(self.toggleChart2Visibility)

        self.btnCalibrar.clicked.connect(self.iniciarCalibracion)
            
        self.calWin.show()

    def closeCalibracion(self):
        self.calWin.close()
        self.calWin = None
 
    def generadorWin(self):
        self.genWin = QMainWindow()
        self.genWin.setWindowTitle("Generador de señales")
        self.genWin.setGeometry(self.norm(0.4, 0.3, 0.2, 0.4))
        
        # Widget central y layout principal
        centralWidget = QWidget()
        self.genWin.setCentralWidget(centralWidget)
        mainLayout = QVBoxLayout(centralWidget)
        
        configLayout = QHBoxLayout()
        
        self.lbltipoSig = QLabel("Tipo de señal:")
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Senoidal", "Cuadrada", "Triangular"])
        configLayout.addWidget(self.lbltipoSig)
        configLayout.addWidget(self.tipo_combo)
        
        self.lblFrecSig = QLabel("Frecuencia (Hz):")
        self.freq_input = QLineEdit("440")
        configLayout.addWidget(self.lblFrecSig)
        configLayout.addWidget(self.freq_input)
        
        self.lblAmpSig = QLabel("Amplitud:")
        self.amp_input = QLineEdit("1")
        configLayout.addWidget(self.lblAmpSig)
        configLayout.addWidget(self.amp_input)

        self.lblDurSig = QLabel("Duración (s):")
        self.dur_input = QLineEdit("1")
        configLayout.addWidget(self.lblDurSig)
        configLayout.addWidget(self.dur_input)

        self.btn_generar = QPushButton("Generar y Graficar")
        self.btn_generar.clicked.connect(self.generar_senal)
        configLayout.addWidget(self.btn_generar)
        
        self.seriesGenSig = QLineSeries()
        self.chartGenSig = QChart()
        self.chartGenSig.addSeries(self.seriesGenSig)
        self.chartGenSig.createDefaultAxes()
        self.chartGenSig.setTitle("Señal Generada")

        self.chartGenSig_view = QChartView(self.chartGenSig)
        self.chartGenSig_view.setRenderHint(QPainter.Antialiasing)
        
        mainLayout.addLayout(configLayout)
        mainLayout.addWidget(self.chartGenSig_view)
            
        self.genWin.show()
        
    def generar_senal(self):
        tipo = self.tipo_combo.currentText()
        f = float(self.freq_input.text())
        A = float(self.amp_input.text())
        T = float(self.dur_input.text())
        Fs = 44100
        t = np.linspace(0, T, int(Fs*T))

        if tipo == "Senoidal":
            y = A * np.sin(2 * np.pi * f * t)
        elif tipo == "Cuadrada":
            y = A * np.sign(np.sin(2 * np.pi * f * t))
        elif tipo == "Triangular":
            y = A * 2 * np.abs(2 * (t * f - np.floor(t * f + 0.5))) - 1


        self.chartGenSig.removeSeries(self.seriesGenSig)
        self.seriesGenSig.clear()
        
        for i in range(len(t)):
            self.seriesGenSig.append(QPointF(t[i], y[i]))
        
        self.chartGenSig.addSeries(self.seriesGenSig)
        self.chartGenSig.createDefaultAxes()
            
    def toggleChart2Visibility(self, checked):
        if hasattr(self, 'winGraph2'):
            self.winGraph2.setVisible(checked)
        
    def toggleImportButton(self, checked):
        """Habilita o deshabilita el botón Importar Señal según el estado del radio button externa"""
        if hasattr(self, 'btnImportSig'):
            self.btnImportSig.setEnabled(checked)
    
    def toggleValRef(self, checked):
        """Habilita o deshabilita el campo de texto del valor de la referencia segun el radio button relativa"""
        if hasattr(self, 'txtValorRef'):
            self.txtValorRef.setEnabled(checked)
    
    def importarSenalCalibracion(self):
        """Importa un archivo .wav y lo grafica en chart2"""
        try:
            from scipy.io.wavfile import read as wavread
            
            # Abrir explorador de archivos para seleccionar archivo .wav
            fileName, _ = QFileDialog.getOpenFileName(
                self.calWin, 
                "Seleccionar archivo de audio", 
                "", 
                "Archivos de audio (*.wav);;Todos los archivos (*)"
            )
            
            if fileName:
                # Leer archivo .wav
                Fs, x = wavread(fileName)
                
                # Manejar archivos estéreo (convertir a mono si es necesario)
                if len(x.shape) > 1:
                    # Si es estéreo, promediar los canales
                    x = np.mean(x, axis=1)
                
                # Normalizar los datos
                maxX = np.max(np.abs(x))
                if maxX > 0:
                    signaldata = x / maxX
                else:
                    signaldata = x
                
                # Crear array de tiempo
                tiempo = np.arange(len(signaldata)) / Fs
                
                # Limpiar el gráfico anterior
                if hasattr(self, 'plot_line_cal'):
                    self.chart2.removeSeries(self.plot_line_cal)
                
                # Crear nueva serie para el gráfico
                self.plot_line_cal = QLineSeries()
                # Configurar color amarillo para la línea de calibración
                pen = QPen(QColor(71, 142, 203))  # Color amarillo (R=255, G=255, B=0)
                pen.setWidth(2)  # Grosor de la línea
                self.plot_line_cal.setPen(pen)
                
                # Agregar puntos al gráfico (limitando a 10000 puntos para rendimiento)
                step = max(1, len(signaldata) // 10000)
                for i in range(0, len(signaldata), step):
                    self.plot_line_cal.append(tiempo[i], signaldata[i])
                
                # Agregar la serie al gráfico
                self.chart2.addSeries(self.plot_line_cal)
                
                # Configurar ejes
                self.axisX2.setRange(0, tiempo[-1] if len(tiempo) > 0 else 1)
                self.axisY2.setRange(-1.2, 1.2)
                
                # Actualizar etiquetas de ejes
                self.axisX2.setTitleText("Tiempo (s)")
                self.axisY2.setTitleText("Amplitud Normalizada")
                
                # Mostrar información del archivo
                #print(f"Archivo cargado: {fileName}")
                #print(f"Frecuencia de muestreo: {Fs} Hz")
                #print(f"Duración: {tiempo[-1]:.2f} segundos")
                #print(f"Número de muestras: {len(signaldata)}")
                
        except Exception as e:
            QMessageBox.critical(self.calWin, "Error", f"Error al importar archivo: {str(e)}")
            print(f"Error en importarSenalCalibracion: {e}")
    
    # CODIGO configuracion del graficos
    def configuracion(self):
            self.confWin = QMainWindow()
            self.confWin.setWindowTitle("Configuracion de Gráficos")
            self.confWin.setGeometry(self.norm(0.2, 0.2, 0.6, 0.6))
            
            # Crear widget central para la ventana de configuración
            centralWidget = QWidget()
            self.confWin.setCentralWidget(centralWidget)
            
            # Layout principal para la ventana de configuración
            self.confWinLayout = QVBoxLayout(centralWidget)
            self.confinfoLayout = QHBoxLayout()
            self.confBotonesLayout = QHBoxLayout()
            self.confWinLayout.addLayout(self.confinfoLayout)
            self.confWinLayout.addLayout(self.confBotonesLayout)
            
            # Grupo de configuración de ejes
            ejesGroupTiempo = QGroupBox("Configuración de Ejes Tiempo")
            ejesGroupEspectro = QGroupBox("Configuración de Ejes Espectro")
            ejesGroupNivel = QGroupBox("Configuración de Ejes Nivel")
            configLayout = QHBoxLayout()
            ejesLayoutTiempo = QVBoxLayout()
            ejesLayoutEspectro = QVBoxLayout()
            ejesLayoutNivel = QVBoxLayout()
            
            
            #CONFIGURACION DE ESCALA
            # Configuración de escala Tiempo
            escalaLayoutTiempo = QHBoxLayout()
            escalaLayoutTiempo.addWidget(QLabel("Escala:"))
            
            self.cbEscalaXTiempo = QCheckBox("Eje X Logarítmico")
            self.cbEscalaXTiempo.setChecked(self.var_logModeXTiempo)
            self.cbEscalaYTiempo = QCheckBox("Eje Y Logarítmico")
            self.cbEscalaYTiempo.setChecked(self.var_logModeYTiempo)
            
            
            escalaLayoutTiempo.addWidget(self.cbEscalaXTiempo)
            escalaLayoutTiempo.addWidget(self.cbEscalaYTiempo)
            escalaLayoutTiempo.addStretch()
            ejesLayoutTiempo.addLayout(escalaLayoutTiempo)
            
            # Configuración de escala Espectro
            escalaLayoutEspectro = QHBoxLayout()
            escalaLayoutEspectro.addWidget(QLabel("Escala:"))
            
            self.cbEscalaXEspectro = QCheckBox("Eje X Logarítmico")
            self.cbEscalaXEspectro.setChecked(self.var_logModeXEspectro)
            self.cbEscalaYEspectro = QCheckBox("Eje Y Logarítmico")
            self.cbEscalaYEspectro.setChecked(self.var_logModeYEspectro)
            
            
            escalaLayoutEspectro.addWidget(self.cbEscalaXEspectro)
            escalaLayoutEspectro.addWidget(self.cbEscalaYEspectro)
            escalaLayoutEspectro.addStretch()
            ejesLayoutEspectro.addLayout(escalaLayoutEspectro)
            
            # Configuración de escala Nivel
            escalaLayoutNivel = QHBoxLayout()
            escalaLayoutNivel.addWidget(QLabel("Escala:"))
            
            self.cbEscalaYNivel = QCheckBox("Eje Y Logarítmico")
            self.cbEscalaYNivel.setChecked(self.var_logModeYNivel)
            
            
            escalaLayoutNivel.addWidget(self.cbEscalaYNivel)
            escalaLayoutNivel.addStretch()
            ejesLayoutNivel.addLayout(escalaLayoutNivel)
            
            
            #CONFIGURACION DE LIMITES
            # Configuración de límites del eje X Tiempo
            ejeXGroupTiempo = QGroupBox("Límites del Eje X")
            ejeXLayoutTiempo = QGridLayout()
            
            ejeXLayoutTiempo.addWidget(QLabel("Mínimo:"), 0, 0)
            self.txtXMinTiempo = QLineEdit(str(self.var_xMinTiempo))
            self.txtXMinTiempo.setMaximumWidth(100)
            ejeXLayoutTiempo.addWidget(self.txtXMinTiempo, 0, 1)
            
            ejeXLayoutTiempo.addWidget(QLabel("Máximo:"), 0, 2)
            self.txtXMaxTiempo = QLineEdit(str(self.var_xMaxTiempo))
            self.txtXMaxTiempo.setMaximumWidth(100)
            ejeXLayoutTiempo.addWidget(self.txtXMaxTiempo, 0, 3)
            
            
            ejeXGroupTiempo.setLayout(ejeXLayoutTiempo)
            ejesLayoutTiempo.addWidget(ejeXGroupTiempo)
            
            # Configuración de límites del eje Y Tiempo
            ejeYGroupTiempo = QGroupBox("Límites del Eje Y")
            ejeYLayoutTiempo = QGridLayout()
            
            ejeYLayoutTiempo.addWidget(QLabel("Mínimo:"), 0, 0)
            self.txtYMinTiempo = QLineEdit(str(self.var_yMinTiempo))
            self.txtYMinTiempo.setMaximumWidth(100)
            ejeYLayoutTiempo.addWidget(self.txtYMinTiempo, 0, 1)
            
            ejeYLayoutTiempo.addWidget(QLabel("Máximo:"), 0, 2)
            self.txtYMaxTiempo = QLineEdit(str(self.var_yMaxTiempo))
            self.txtYMaxTiempo.setMaximumWidth(100)
            ejeYLayoutTiempo.addWidget(self.txtYMaxTiempo, 0, 3)
            
            ejeYGroupTiempo.setLayout(ejeYLayoutTiempo)
            ejesLayoutTiempo.addWidget(ejeYGroupTiempo)
            
            # Configuración de límites del eje X Espectro
            ejeXGroupEspectro = QGroupBox("Límites del Eje X")
            ejeXLayoutEspectro = QGridLayout()
            
            ejeXLayoutEspectro.addWidget(QLabel("Mínimo:"), 0, 0)
            self.txtXMinEspectro = QLineEdit(str(self.var_xMinEspectro))
            self.txtXMinEspectro.setMaximumWidth(100)
            ejeXLayoutEspectro.addWidget(self.txtXMinEspectro, 0, 1)
            
            ejeXLayoutEspectro.addWidget(QLabel("Máximo:"), 0, 2)
            self.txtXMaxEspectro = QLineEdit(str(self.var_xMaxEspectro))
            self.txtXMaxEspectro.setMaximumWidth(100)
            ejeXLayoutEspectro.addWidget(self.txtXMaxEspectro, 0, 3)
            
            ejeXGroupEspectro.setLayout(ejeXLayoutEspectro)
            ejesLayoutEspectro.addWidget(ejeXGroupEspectro)
            
            # Configuración de límites del eje Y Espectro
            ejeYGroupEspectro = QGroupBox("Límites del Eje Y")
            ejeYLayoutEspectro = QGridLayout()
            
            ejeYLayoutEspectro.addWidget(QLabel("Mínimo:"), 0, 0)
            self.txtYMinEspectro = QLineEdit(str(self.var_yMinEspectro))
            self.txtYMinEspectro.setMaximumWidth(100)
            ejeYLayoutEspectro.addWidget(self.txtYMinEspectro, 0, 1)
            
            ejeYLayoutEspectro.addWidget(QLabel("Máximo:"), 0, 2)
            self.txtYMaxEspectro = QLineEdit(str(self.var_yMaxEspectro))
            self.txtYMaxEspectro.setMaximumWidth(100)
            ejeYLayoutEspectro.addWidget(self.txtYMaxEspectro, 0, 3)
            
            ejeYGroupEspectro.setLayout(ejeYLayoutEspectro)
            ejesLayoutEspectro.addWidget(ejeYGroupEspectro)
            
            # Configuración de límites del eje X Nivel
            ejeXGroupNivel = QGroupBox("Límites del Eje X")
            ejeXLayoutNivel = QGridLayout()
            
            ejeXLayoutNivel.addWidget(QLabel("Mínimo:"), 0, 0)
            self.txtXMinNivel = QLineEdit(str(self.var_xMinNivel))
            self.txtXMinNivel.setMaximumWidth(100)
            ejeXLayoutNivel.addWidget(self.txtXMinNivel, 0, 1)
            
            ejeXLayoutNivel.addWidget(QLabel("Máximo:"), 0, 2)
            self.txtXMaxNivel = QLineEdit(str(self.var_xMaxNivel))
            self.txtXMaxNivel.setMaximumWidth(100)
            ejeXLayoutNivel.addWidget(self.txtXMaxNivel, 0, 3)
            
            ejeXGroupNivel.setLayout(ejeXLayoutNivel)
            ejesLayoutNivel.addWidget(ejeXGroupNivel)
            
            # Configuración de límites del eje Y Nivel
            ejeYGroupNivel = QGroupBox("Límites del Eje Y")
            ejeYLayoutNivel = QGridLayout()
            
            ejeYLayoutNivel.addWidget(QLabel("Mínimo:"), 0, 0)
            self.txtYMinNivel = QLineEdit(str(self.var_yMinNivel))
            self.txtYMinNivel.setMaximumWidth(100)
            ejeYLayoutNivel.addWidget(self.txtYMinNivel, 0, 1)
            
            ejeYLayoutNivel.addWidget(QLabel("Máximo:"), 0, 2)
            self.txtYMaxNivel = QLineEdit(str(self.var_yMaxNivel))
            self.txtYMaxNivel.setMaximumWidth(100)
            ejeYLayoutNivel.addWidget(self.txtYMaxNivel, 0, 3)
            
            ejeYGroupNivel.setLayout(ejeYLayoutNivel)
            ejesLayoutNivel.addWidget(ejeYGroupNivel)
            
            
            #CONFIGURACION DE ETIQUETAS
            # Configuración de etiquetas Tiempo
            etiquetasGroupTiempo = QGroupBox("Etiquetas de Ejes")
            etiquetasLayoutTiempo = QGridLayout()
            
            etiquetasLayoutTiempo.addWidget(QLabel("Eje X:"), 0, 0)
            self.txtEtiquetaXTiempo = QLineEdit(self.var_etiquetaXTiempo)
            etiquetasLayoutTiempo.addWidget(self.txtEtiquetaXTiempo, 0, 1)
            
            etiquetasLayoutTiempo.addWidget(QLabel("Eje Y:"), 1, 0)
            self.txtEtiquetaYTiempo = QLineEdit(self.var_etiquetaYTiempo)
            etiquetasLayoutTiempo.addWidget(self.txtEtiquetaYTiempo, 1, 1)
            
            etiquetasGroupTiempo.setLayout(etiquetasLayoutTiempo)
            ejesLayoutTiempo.addWidget(etiquetasGroupTiempo)
            
            # Configuración de etiquetas Espectro
            etiquetasGroupEspectro = QGroupBox("Etiquetas de Ejes")
            etiquetasLayoutEspectro = QGridLayout()
            
            etiquetasLayoutEspectro.addWidget(QLabel("Eje X:"), 0, 0)
            self.txtEtiquetaXEspectro = QLineEdit(self.var_etiquetaXEspectro)
            etiquetasLayoutEspectro.addWidget(self.txtEtiquetaXEspectro, 0, 1)
            
            etiquetasLayoutEspectro.addWidget(QLabel("Eje Y:"), 1, 0)
            self.txtEtiquetaYEspectro = QLineEdit(self.var_etiquetaYEspectro)
            etiquetasLayoutEspectro.addWidget(self.txtEtiquetaYEspectro, 1, 1)
            
            etiquetasGroupEspectro.setLayout(etiquetasLayoutEspectro)
            ejesLayoutEspectro.addWidget(etiquetasGroupEspectro)
            
            # Configuración de etiquetas Nivel
            etiquetasGroupNivel = QGroupBox("Etiquetas de Ejes")
            etiquetasLayoutNivel = QGridLayout()
            
            etiquetasLayoutNivel.addWidget(QLabel("Eje X:"), 0, 0)
            self.txtEtiquetaXNivel = QLineEdit(self.var_etiquetaXNivel)
            etiquetasLayoutNivel.addWidget(self.txtEtiquetaXNivel, 0, 1)
            
            etiquetasLayoutNivel.addWidget(QLabel("Eje Y:"), 1, 0)
            self.txtEtiquetaYNivel = QLineEdit(self.var_etiquetaYNivel)
            etiquetasLayoutNivel.addWidget(self.txtEtiquetaYNivel, 1, 1)
            
            etiquetasGroupNivel.setLayout(etiquetasLayoutNivel)
            ejesLayoutNivel.addWidget(etiquetasGroupNivel)
            
            
            #CONFIGURACION DE COLORES
            # Configuración de color Tiempo
            colorGroupTiempo = QGroupBox("Color de Línea")
            colorLayoutTiempo = QHBoxLayout()
            
            self.colorFrameTiempo = QFrame()
            self.colorFrameTiempo.setFixedSize(30, 20)
            self.colorFrameTiempo.setStyleSheet("background-color: #8A0101; border: 1px solid black;")
            
            self.btnColorTiempo = QPushButton("Seleccionar Color")
            self.btnColorTiempo.clicked.connect(lambda: self.seleccionarColor(self.colorFrameTiempo, "tiempo"))
            
            colorLayoutTiempo.addWidget(QLabel("Color:"))
            colorLayoutTiempo.addWidget(self.colorFrameTiempo)
            colorLayoutTiempo.addWidget(self.btnColorTiempo)
            colorLayoutTiempo.addStretch()
            
            colorGroupTiempo.setLayout(colorLayoutTiempo)
            ejesLayoutTiempo.addWidget(colorGroupTiempo)
            
            # Configuración de color Espectro
            colorGroupEspectro = QGroupBox("Color de Línea")
            colorLayoutEspectro = QHBoxLayout()
            
            self.colorFrameEspectro = QFrame()
            self.colorFrameEspectro.setFixedSize(30, 20)
            self.colorFrameEspectro.setStyleSheet("background-color: #8A3F01; border: 1px solid black;")
            
            self.btnColorEspectro = QPushButton("Seleccionar Color")
            self.btnColorEspectro.clicked.connect(lambda: self.seleccionarColor(self.colorFrameEspectro, "espectro"))
            
            colorLayoutEspectro.addWidget(QLabel("Color:"))
            colorLayoutEspectro.addWidget(self.colorFrameEspectro)
            colorLayoutEspectro.addWidget(self.btnColorEspectro)
            colorLayoutEspectro.addStretch()
            
            colorGroupEspectro.setLayout(colorLayoutEspectro)
            ejesLayoutEspectro.addWidget(colorGroupEspectro)
            
            # Configuración de color Nivel
            colorGroupNivel = QGroupBox("Color de Línea")
            colorLayoutNivel = QHBoxLayout()
            
            self.colorFrameNivel = QFrame()
            self.colorFrameNivel.setFixedSize(30, 20)
            self.colorFrameNivel.setStyleSheet("background-color: #000000; border: 1px solid black;")
            
            self.btnColorNivel = QPushButton("Seleccionar Color")
            self.btnColorNivel.clicked.connect(lambda: self.seleccionarColor(self.colorFrameNivel, "nivel"))
            
            colorLayoutNivel.addWidget(QLabel("Color:"))
            colorLayoutNivel.addWidget(self.colorFrameNivel)
            colorLayoutNivel.addWidget(self.btnColorNivel)
            colorLayoutNivel.addStretch()
            
            colorGroupNivel.setLayout(colorLayoutNivel)
            ejesLayoutNivel.addWidget(colorGroupNivel)
            
            # CONFIGURACION DE TIPO DE LINEA y TIPO DE GRAFICO
            # Configuración de tipo de línea Tiempo
            tipoLineaGroupTiempo = QGroupBox("Tipo de Línea")
            tipoLineaLayoutTiempo = QHBoxLayout()
            
            tipoLineaLayoutTiempo.addWidget(QLabel("Estilo:"))
            self.cmbTipoLineaTiempo = QComboBox()
            self.cmbTipoLineaTiempo.addItems(["Sólida", "Punteada", "Rayada"])
            # Seleccionar el valor guardado
            if self.var_tipoLineaTiempo:
                idx = self.cmbTipoLineaTiempo.findText(self.var_tipoLineaTiempo)
                if idx >= 0:
                    self.cmbTipoLineaTiempo.setCurrentIndex(idx)
            tipoLineaLayoutTiempo.addWidget(self.cmbTipoLineaTiempo)
            tipoLineaLayoutTiempo.addStretch()
            tipoLineaGroupTiempo.setLayout(tipoLineaLayoutTiempo)
            ejesLayoutTiempo.addWidget(tipoLineaGroupTiempo)
            
            # Configuración de tipo de gráfico Espectro
            tipoGraficoGroupEspectro = QGroupBox("Tipo de Gráfico")
            tipoGraficoLayoutEspectro = QHBoxLayout()
            
            tipoGraficoLayoutEspectro.addWidget(QLabel("Estilo:"))
            self.cmbTipoGraficoEspectro = QComboBox()
            self.cmbTipoGraficoEspectro.addItems(["Línea", "Barras"])
            # Seleccionar el valor guardado
            if self.var_tipoGraficoEspectro:
                idx = self.cmbTipoGraficoEspectro.findText(self.var_tipoGraficoEspectro)
                if idx >= 0:
                    self.cmbTipoGraficoEspectro.setCurrentIndex(idx)
            tipoGraficoLayoutEspectro.addWidget(self.cmbTipoGraficoEspectro)
            tipoGraficoLayoutEspectro.addStretch()
            tipoGraficoGroupEspectro.setLayout(tipoGraficoLayoutEspectro)
            ejesLayoutEspectro.addWidget(tipoGraficoGroupEspectro)
            
            # Configuración de tipo de línea Nivel
            tipoLineaGroupNivel = QGroupBox("Tipo de Línea")
            tipoLineaLayoutNivel = QHBoxLayout()
            
            tipoLineaLayoutNivel.addWidget(QLabel("Estilo:"))
            self.cmbTipoLineaNivel = QComboBox()
            self.cmbTipoLineaNivel.addItems(["Sólida", "Punteada", "Rayada"])
            # Seleccionar el valor guardado
            if self.var_tipoLineaNivel:
                idx = self.cmbTipoLineaNivel.findText(self.var_tipoLineaNivel)
                if idx >= 0:
                    self.cmbTipoLineaNivel.setCurrentIndex(idx)
            tipoLineaLayoutNivel.addWidget(self.cmbTipoLineaNivel)
            tipoLineaLayoutNivel.addStretch()
            tipoLineaGroupNivel.setLayout(tipoLineaLayoutNivel)
            ejesLayoutNivel.addWidget(tipoLineaGroupNivel)
            
            
            
            # Botón para aplicar configuración automática según el tipo de gráfico
            self.btnConfigAplicar = QPushButton("Aplicar")
            self.btnConfigAplicar.clicked.connect(self.aplicarconfiguracion)
            self.btnConfigCancelar = QPushButton("Cancelar")
            self.btnConfigCancelar.clicked.connect(self.confWin.close)
            
            ejesGroupTiempo.setLayout(ejesLayoutTiempo)
            ejesGroupEspectro.setLayout(ejesLayoutEspectro)
            ejesGroupNivel.setLayout(ejesLayoutNivel)
            
            self.confinfoLayout.addWidget(ejesGroupTiempo)
            self.confinfoLayout.addWidget(ejesGroupEspectro)
            self.confinfoLayout.addWidget(ejesGroupNivel)
            self.confBotonesLayout.addWidget(self.btnConfigCancelar)
            self.confBotonesLayout.addWidget(self.btnConfigAplicar)
            
            
            # Agregar stretch para empujar todo hacia arriba
            self.confWinLayout.addStretch()
            
            for boton in [self.btnColorTiempo, self.btnColorEspectro, self.btnColorNivel, self.btnConfigAplicar, self.btnConfigCancelar]:
                boton.setProperty("class", "ventanasSec")
    
            for combo in [self.cmbTipoLineaTiempo, self.cmbTipoGraficoEspectro, self.cmbTipoLineaNivel]:
                combo.setProperty("class", "ventanasSec")
            # Mostrar la ventana de configuración
            self.confWin.show()

    def actualizarNombreDispositivo(self):
        """Actualiza el label con el nombre del dispositivo actual"""
        try:
            # Verificar si el label existe (solo se crea cuando se abre la ventana de calibración)
            if not hasattr(self, 'lblConfHard'):
                print("Label lblConfHard no existe - ventana de calibración no abierta")
                return
                
            dispositivo_actual = self.vController.cModel.getDispositivoActual()
            if dispositivo_actual is not None:
                # Obtener los nombres e índices de dispositivos
                nombres = self.vController.cModel.getDispositivosEntrada('nombre')
                indices = self.vController.cModel.getDispositivosEntrada('indice')
                
                # Buscar el nombre del dispositivo actual
                try:
                    idx_actual = indices.index(dispositivo_actual)
                    nombre_dispositivo = nombres[idx_actual]
                    self.lblConfHard.setText(nombre_dispositivo)
                    print(f"Dispositivo actualizado: {nombre_dispositivo}")
                except ValueError:
                    # Si no se encuentra el dispositivo actual, mostrar "Desconocido"
                    self.lblConfHard.setText("Desconocido")
                    print("Dispositivo no encontrado en la lista")
            else:
                self.lblConfHard.setText("No disponible")
                print("No hay dispositivo actual")
        except Exception as e:
            print(f"Error al actualizar nombre del dispositivo: {e}")
            if hasattr(self, 'lblConfHard'):
                self.lblConfHard.setText("Error")
    
    def actualizarNombreDispositivoSalida(self):
        """Actualiza el label con el nombre del dispositivo de salida actual"""
        try:
            # Verificar si el label existe (solo se crea cuando se abre la ventana de calibración)
            if not hasattr(self, 'lblConfHardSalida'):
                print("Label lblConfHardSalida no existe - ventana de calibración no abierta")
                return
                
            dispositivo_salida_actual = self.vController.cModel.getDispositivoSalidaActual()
            if dispositivo_salida_actual is not None:
                # Obtener los nombres e índices de dispositivos de salida
                nombres = self.vController.cModel.getDispositivosSalida('nombre')
                indices = self.vController.cModel.getDispositivosSalida('indice')
                
                # Buscar el nombre del dispositivo actual
                try:
                    idx_actual = indices.index(dispositivo_salida_actual)
                    nombre_dispositivo = nombres[idx_actual]
                    self.lblConfHardSalida.setText(nombre_dispositivo)
                    print(f"Dispositivo de salida actualizado: {nombre_dispositivo}")
                except ValueError:
                    # Si no se encuentra el dispositivo actual, mostrar "Desconocido"
                    self.lblConfHardSalida.setText("Desconocido")
                    print("Dispositivo de salida no encontrado en la lista")
            else:
                self.lblConfHardSalida.setText("No disponible")
                print("No hay dispositivo de salida actual")
        except Exception as e:
            print(f"Error al actualizar nombre del dispositivo de salida: {e}")
            if hasattr(self, 'lblConfHardSalida'):
                self.lblConfHardSalida.setText("Error")

    def configuracionDispositivo(self):
        self.confDispWin = QMainWindow()
        self.confDispWin.setWindowTitle("Configuración de Dispositivo")
        self.confDispWin.setGeometry(self.norm(0.4, 0.4, 0.2, 0.2))

        # Widget central y layout principal
        centralWidget = QWidget()
        self.confDispWin.setCentralWidget(centralWidget)
        mainLayout = QVBoxLayout(centralWidget)

        # Layout de selección de dispositivo Entrada
        dispGroupEntrada = QGroupBox("Dispositivo de Entrada")
        dispLayoutEntrada = QHBoxLayout()
        self.cmbDispositivosEntrada = QComboBox()
        # Obtener lista de dispositivos del modelo
        dispositivosEntrada = self.vController.cModel.getDispositivosEntrada('nombre')
        self.cmbDispositivosEntrada.addItems(dispositivosEntrada)
        
        # Obtener el dispositivo actual y seleccionarlo en el ComboBox
        dispositivo_actual = self.vController.cModel.getDispositivoActual()
        if dispositivo_actual is not None:
            # Buscar el índice del dispositivo actual en la lista de dispositivos
            indices = self.vController.cModel.getDispositivosEntrada('indice')
            try:
                idx_actual = indices.index(dispositivo_actual)
                self.cmbDispositivosEntrada.setCurrentIndex(idx_actual)
            except ValueError:
                # Si no se encuentra el dispositivo actual, usar el primer dispositivo
                self.cmbDispositivosEntrada.setCurrentIndex(0)
        else:
            # Si no hay dispositivo actual, usar el primer dispositivo
            self.cmbDispositivosEntrada.setCurrentIndex(0)
        
        self.lblSelEnt = QLabel("Seleccionar:")
        dispLayoutEntrada.addWidget(self.lblSelEnt)
        dispLayoutEntrada.addWidget(self.cmbDispositivosEntrada)
        dispGroupEntrada.setLayout(dispLayoutEntrada)
        mainLayout.addWidget(dispGroupEntrada)
        
        # Layout de selección de dispositivo Salida
        dispGroupSalida = QGroupBox("Dispositivo de Salida")
        dispLayoutSalida = QHBoxLayout()
        self.cmbDispositivosSalida = QComboBox()
        # Obtener lista de dispositivos de salida del modelo
        dispositivosSalida = self.vController.cModel.getDispositivosSalida('nombre')
        self.cmbDispositivosSalida.addItems(dispositivosSalida)
        
        # Obtener el dispositivo de salida actual y seleccionarlo en el ComboBox
        dispositivo_salida_actual = self.vController.cModel.getDispositivoSalidaActual()
        if dispositivo_salida_actual is not None:
            # Buscar el índice del dispositivo actual en la lista de dispositivos
            indicesSalida = self.vController.cModel.getDispositivosSalida('indice')
            try:
                idx_actual = indicesSalida.index(dispositivo_salida_actual)
                self.cmbDispositivosSalida.setCurrentIndex(idx_actual)
            except ValueError:
                # Si no se encuentra el dispositivo actual, usar el primer dispositivo
                self.cmbDispositivosSalida.setCurrentIndex(0)
        else:
            # Si no hay dispositivo actual, usar el primer dispositivo
            self.cmbDispositivosSalida.setCurrentIndex(0)
        
        self.lblSelSal= QLabel("Seleccionar:")
        dispLayoutSalida.addWidget(self.lblSelSal)
        dispLayoutSalida.addWidget(self.cmbDispositivosSalida)
        dispGroupSalida.setLayout(dispLayoutSalida)
        mainLayout.addWidget(dispGroupSalida)
        
        # Layout de configuración de rate y chunk
        rateChunkGroup = QGroupBox("Parámetros de Audio")
        rateChunkLayout = QHBoxLayout()
        self.txtRate = QLineEdit(str(self.vController.cModel.rate))
        self.txtChunk = QLineEdit(str(self.vController.cModel.chunk))
        self.lblRate = QLabel("Rate (Hz):")
        rateChunkLayout.addWidget(self.lblRate)
        rateChunkLayout.addWidget(self.txtRate)
        self.lblChunk = QLabel("Chunk:")
        rateChunkLayout.addWidget(self.lblChunk)
        rateChunkLayout.addWidget(self.txtChunk)
        rateChunkGroup.setLayout(rateChunkLayout)
        mainLayout.addWidget(rateChunkGroup)

        # Botones Agregar y Cancelar
        botonesLayout = QHBoxLayout()
        self.btnDispAgregar = QPushButton("Aplicar")
        self.btnDispAgregar.clicked.connect(self.aplicarConfiguracionDispositivo)
        self.btnDispCancelar = QPushButton("Cancelar")
        self.btnDispCancelar.clicked.connect(self.confDispWin.close)
        botonesLayout.addWidget(self.btnDispCancelar)
        botonesLayout.addWidget(self.btnDispAgregar)
        mainLayout.addLayout(botonesLayout)

        for boton in [self.btnDispAgregar, self.btnDispCancelar]:
            boton.setProperty("class", "ventanasSec")
        
        for lbl in [self.lblChunk, self.lblRate, self.lblSelEnt, self.lblSelSal]:
            lbl.setProperty("class", "ventanasSecLabelDestacado")
            
        for cmb in [self.cmbDispositivosEntrada, self.cmbDispositivosSalida]:
            cmb.setProperty("class", "ventanasSec")
        self.confDispWin.show()

    def aplicarConfiguracionDispositivo(self):
        try:
            # Obtener valores seleccionados
            dispositivo_entrada_idx = self.cmbDispositivosEntrada.currentIndex()
            dispositivo_salida_idx = self.cmbDispositivosSalida.currentIndex()
            rate = int(self.txtRate.text())
            chunk = int(self.txtChunk.text())
            
            # Obtener el índice real del dispositivo de entrada seleccionado
            indices_entrada = self.vController.cModel.getDispositivosEntrada('indice')
            device_index_entrada = indices_entrada[dispositivo_entrada_idx] if dispositivo_entrada_idx < len(indices_entrada) else None
            
            # Obtener el índice real del dispositivo de salida seleccionado
            indices_salida = self.vController.cModel.getDispositivosSalida('indice')
            device_index_salida = indices_salida[dispositivo_salida_idx] if dispositivo_salida_idx < len(indices_salida) else None
            
            # Obtener el dispositivo actual antes del cambio
            dispositivo_entrada_actual = self.vController.cModel.getDispositivoActual()
            dispositivo_salida_actual = self.vController.cModel.getDispositivoSalidaActual()
            
            print(f"Dispositivo entrada actual: {dispositivo_entrada_actual}")
            print(f"Dispositivo entrada seleccionado: {device_index_entrada}")
            print(f"Dispositivo salida actual: {dispositivo_salida_actual}")
            print(f"Dispositivo salida seleccionado: {device_index_salida}")
            print(f"Rate: {rate}, Chunk: {chunk}")
            
            # Cambiar el dispositivo de entrada si es diferente al actual
            if device_index_entrada != dispositivo_entrada_actual:
                print(f"Cambiando dispositivo de entrada de {dispositivo_entrada_actual} a {device_index_entrada}")
                
                # Cerrar el stream actual si existe
                if hasattr(self.vController.cModel, 'stream') and self.vController.cModel.stream is not None:
                    print("Cerrando stream actual...")
                    self.vController.cModel.stream.close()
                
                # Reinicializar el stream con el nuevo dispositivo
                print("Inicializando nuevo stream...")
                self.vController.cModel.initialize_audio_stream(device_index_entrada, rate, chunk)
                
                # Verificar que el cambio se aplicó correctamente
                nuevo_dispositivo_entrada = self.vController.cModel.getDispositivoActual()
                print(f"Dispositivo entrada después del cambio: {nuevo_dispositivo_entrada}")
                
                if nuevo_dispositivo_entrada == device_index_entrada:
                    print("✅ Cambio de dispositivo de entrada exitoso")
                    # Actualizar el label con el nuevo nombre del dispositivo
                    self.actualizarNombreDispositivo()
                else:
                    print("⚠️ El cambio de dispositivo de entrada no se aplicó correctamente")
            else:
                print("No se requiere cambio de dispositivo de entrada")
            
            # Cambiar el dispositivo de salida si es diferente al actual
            if device_index_salida != dispositivo_salida_actual:
                print(f"Cambiando dispositivo de salida de {dispositivo_salida_actual} a {device_index_salida}")
                
                # Actualizar el dispositivo de salida en el modelo
                self.vController.cModel.setDispositivoSalida(device_index_salida)
                
                # Verificar que el cambio se aplicó correctamente
                nuevo_dispositivo_salida = self.vController.cModel.getDispositivoSalidaActual()
                print(f"Dispositivo salida después del cambio: {nuevo_dispositivo_salida}")
                
                if nuevo_dispositivo_salida == device_index_salida:
                    print("✅ Cambio de dispositivo de salida exitoso")
                    # Actualizar el label con el nuevo nombre del dispositivo de salida
                    self.actualizarNombreDispositivoSalida()
                else:
                    print("⚠️ El cambio de dispositivo de salida no se aplicó correctamente")
            else:
                print("No se requiere cambio de dispositivo de salida")
            
            # Cerrar ventana
            self.confDispWin.close()
            
        except Exception as e:
            print(f"Error al aplicar configuración: {e}")
            QMessageBox.critical(self, "Error", f"Error al aplicar configuración de dispositivo: {e}")
