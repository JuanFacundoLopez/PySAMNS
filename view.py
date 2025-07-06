# Importo librerias

#import Librerias graficas
# from tkinter import Y
# from PyQt5.QtWidgets import * 

import pyqtgraph as pg

from PyQt5.QtWidgets import QMainWindow, QApplication, QHBoxLayout, QVBoxLayout, QTabWidget, QPushButton
from PyQt5.QtWidgets import QLabel, QLineEdit, QGroupBox, QRadioButton, QCheckBox, QAction, QWidget, QGridLayout
from PyQt5.QtWidgets import QMenu, QTextEdit, QMessageBox

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRect
# from PyQt5 import QtWidgets
from pyqtgraph.Qt import QtGui, QtCore

# from pyqtgraph.Point import Point

#import utilidades del sistema
import sys


class vista(QMainWindow):

    #def norm(self, x, y, ancho, alto):
    #    return QtCore.QRect(int(self.anchoX * x), int(self.altoY * y), int(self.anchoX * ancho), int(self.altoY * alto))

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
        self.tab_2 = QWidget()
        self.tabWidget.addTab(self.tab_1, "Gráfico")
        self.tabWidget.addTab(self.tab_2, "Valores del gráfico")
        
        # Layout para tab_1
        self.tab1Layout = QHBoxLayout(self.tab_1)
        self.columna1tab1 = QVBoxLayout()
        
        # Gráfico
        self.winGraph1 = pg.GraphicsLayoutWidget()
        self.winGraph1.setBackground('w')
        self.columna1tab1.addWidget(self.winGraph1)
        
        # Configuración del gráfico
        self.waveform1 = self.winGraph1.addPlot()
        self.waveform1.setDownsampling(mode='peak')
        self.waveform1.setClipToView(True)
        self.waveform1.showGrid(x=True, y=True)
        self.waveform1.setYRange(-1.2, 1.2, padding=0)

        # Definir las líneas del gráfico
        self.ptdomTiempo = self.waveform1.plot(pen=(138, 1, 1), width=2)
        self.ptdomEspect = self.waveform1.plot(pen=(138, 63, 1), width=2)

        self.ptNivZSlow = self.waveform1.plot(pen='k', width=3)  # (138, 108, 1)
        self.ptNivZFast = self.waveform1.plot(pen='g', width=3)  # (124, 138, 1)
        self.ptNivZInst = self.waveform1.plot(pen='b', width=3)  # (70, 138, 1)
        self.ptNivZPico = self.waveform1.plot(pen='r', width=3)  # (3, 138, 1)

        self.ptNivCSlow = self.waveform1.plot(pen=(1, 138, 42), width=3)
        self.ptNivCFast = self.waveform1.plot(pen=(1, 138, 92), width=3)
        self.ptNivCInst = self.waveform1.plot(pen=(1, 117, 138), width=3)
        self.ptNivCPico = self.waveform1.plot(pen=(1, 54, 138), width=3)

        self.ptNivASlow = self.waveform1.plot(pen=(28, 1, 138), width=3)
        self.ptNivAFast = self.waveform1.plot(pen=(51, 1, 138), width=3)
        self.ptNivAInst = self.waveform1.plot(pen=(108, 1, 138), width=3)
        self.ptNivAPico = self.waveform1.plot(pen=(138, 1, 63), width=3)
        
        # Botones y cronómetro
        buttonLayout = QHBoxLayout()
        self.btn = QPushButton("Importar señal")
        self.btn.clicked.connect(self.importSignal)
        self.btngbr = QPushButton("Grabar")
        self.btngbr.setCheckable(True)
        self.btngbr.clicked.connect(self.grabar)
        self.cronometroGrabacion = QLabel("0:00 s")
        self.cronometroGrabacion.setStyleSheet("font: bold 20pt")
        
        buttonLayout.addWidget(self.btn)
        buttonLayout.addWidget(self.btngbr)
        buttonLayout.addWidget(self.cronometroGrabacion)
        buttonLayout.addStretch()
        self.columna1tab1.addLayout(buttonLayout)
        
        # Layout para tab_2 (Configuración de ejes)
        self.tab2Layout = QVBoxLayout(self.tab_2)
        
        # Grupo de configuración de ejes
        ejesGroup = QGroupBox("Configuración de Ejes del Gráfico")
        ejesLayout = QVBoxLayout()
        
        # Configuración de escala
        escalaLayout = QHBoxLayout()
        escalaLayout.addWidget(QLabel("Escala:"))
        
        self.cbEscalaX = QCheckBox("Eje X Logarítmico")
        self.cbEscalaY = QCheckBox("Eje Y Logarítmico")
        self.cbEscalaX.stateChanged.connect(self.actualizarEscala)
        self.cbEscalaY.stateChanged.connect(self.actualizarEscala)
        
        escalaLayout.addWidget(self.cbEscalaX)
        escalaLayout.addWidget(self.cbEscalaY)
        escalaLayout.addStretch()
        ejesLayout.addLayout(escalaLayout)
        
        # Configuración de límites del eje X
        ejeXGroup = QGroupBox("Límites del Eje X")
        ejeXLayout = QGridLayout()
        
        ejeXLayout.addWidget(QLabel("Mínimo:"), 0, 0)
        self.txtXMin = QLineEdit("0")
        self.txtXMin.setMaximumWidth(100)
        ejeXLayout.addWidget(self.txtXMin, 0, 1)
        
        ejeXLayout.addWidget(QLabel("Máximo:"), 0, 2)
        self.txtXMax = QLineEdit("1024")
        self.txtXMax.setMaximumWidth(100)
        ejeXLayout.addWidget(self.txtXMax, 0, 3)
        
        self.btnAplicarX = QPushButton("Aplicar")
        self.btnAplicarX.clicked.connect(self.aplicarLimitesX)
        ejeXLayout.addWidget(self.btnAplicarX, 0, 4)
        
        ejeXGroup.setLayout(ejeXLayout)
        ejesLayout.addWidget(ejeXGroup)
        
        # Configuración de límites del eje Y
        ejeYGroup = QGroupBox("Límites del Eje Y")
        ejeYLayout = QGridLayout()
        
        ejeYLayout.addWidget(QLabel("Mínimo:"), 0, 0)
        self.txtYMin = QLineEdit("-1")
        self.txtYMin.setMaximumWidth(100)
        ejeYLayout.addWidget(self.txtYMin, 0, 1)
        
        ejeYLayout.addWidget(QLabel("Máximo:"), 0, 2)
        self.txtYMax = QLineEdit("1")
        self.txtYMax.setMaximumWidth(100)
        ejeYLayout.addWidget(self.txtYMax, 0, 3)
        
        self.btnAplicarY = QPushButton("Aplicar")
        self.btnAplicarY.clicked.connect(self.aplicarLimitesY)
        ejeYLayout.addWidget(self.btnAplicarY, 0, 4)
        
        ejeYGroup.setLayout(ejeYLayout)
        ejesLayout.addWidget(ejeYGroup)
        
        # Configuración de etiquetas
        etiquetasGroup = QGroupBox("Etiquetas de Ejes")
        etiquetasLayout = QGridLayout()
        
        etiquetasLayout.addWidget(QLabel("Eje X:"), 0, 0)
        self.txtEtiquetaX = QLineEdit("Tiempo")
        etiquetasLayout.addWidget(self.txtEtiquetaX, 0, 1)
        
        etiquetasLayout.addWidget(QLabel("Eje Y:"), 1, 0)
        self.txtEtiquetaY = QLineEdit("Amplitud Normalizada")
        etiquetasLayout.addWidget(self.txtEtiquetaY, 1, 1)
        
        self.btnAplicarEtiquetas = QPushButton("Aplicar")
        self.btnAplicarEtiquetas.clicked.connect(self.aplicarEtiquetas)
        etiquetasLayout.addWidget(self.btnAplicarEtiquetas, 2, 0, 1, 2)
        
        etiquetasGroup.setLayout(etiquetasLayout)
        ejesLayout.addWidget(etiquetasGroup)
        
        # Botón para aplicar configuración automática según el tipo de gráfico
        self.btnConfigAuto = QPushButton("Configuración Automática")
        self.btnConfigAuto.clicked.connect(self.configuracionAutomatica)
        ejesLayout.addWidget(self.btnConfigAuto)
        
        ejesGroup.setLayout(ejesLayout)
        self.tab2Layout.addWidget(ejesGroup)
        
        # Agregar stretch para empujar todo hacia arriba
        self.tab2Layout.addStretch()
        
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
        calAutAct = QAction("Calibración Automática", self)
        calAutAct.triggered.connect(self.calibracionAutomatica)
        self.menuCalibracion.addAction(calAutAct)

        calManAct = QAction("Calibración Manual", self)
        calManAct.triggered.connect(self.calibracionManual)
        self.menuCalibracion.addAction(calManAct)

        calFondEscalaAct = QAction("Calibración a fondo de escala", self)
        calFondEscalaAct.triggered.connect(self.calibracionFondoEscala)
        self.menuCalibracion.addAction(calFondEscalaAct)

        # Otros menús
        self.menuConfiguracion = QMenu("Configuración", self)
        self.menuAyuda = QMenu("Ayuda", self)
        self.menuAcerca_de = QMenu("Acerca de...", self)

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
        self.waveform1.setLabel('bottom', 'Tiempo')
        
        # Actualizar el gráfico
        self.waveform1.replot()

        self.show()

    def importSignal(self):
        self.vController.importSignal() # conexion con el controlador

    def grabar(self):
        self.vController.dalePlay() # conexion con el controlador

    def ventanaTiempo(self):
        self.btnNivel.setChecked(False)
        self.btnFrecuencia.setChecked(False)
        self.tabFilt.setDisabled(True)
        self.tabNieles.setDisabled(True)
        
        # Limpiar el gráfico actual
        self.waveform1.clear()
        
        # Configuración para gráfico de tiempo
        self.waveform1.setLogMode(x=False, y=False)  # Escala lineal
        self.waveform1.setYRange(-1, 1, padding=0)   # Amplitud normalizada
        self.waveform1.setXRange(0, 1024, padding=0) # Rango de tiempo
        self.waveform1.setLabel('left', 'Amplitud Normalizada')
        self.waveform1.setLabel('bottom', 'Tiempo')
        
        # Actualizar controles de configuración en tab_2
        self.cbEscalaX.setChecked(False)
        self.cbEscalaY.setChecked(False)
        self.txtXMin.setText("0")
        self.txtXMax.setText("1024")
        self.txtYMin.setText("-1")
        self.txtYMax.setText("1")
        self.txtEtiquetaX.setText("Tiempo")
        self.txtEtiquetaY.setText("Amplitud Normalizada")
        
        # Actualizar el gráfico
        self.waveform1.replot()
        self.vController.graficar()
        
    def ventanaFrecuencia(self):
        self.btnNivel.setChecked(False)
        self.btnTiempo.setChecked(False)
        self.tabFilt.setDisabled(True)
        self.tabNieles.setDisabled(True)
        
        # Limpiar el gráfico actual
        self.waveform1.clear()
        
        # Configuración para gráfico de frecuencia
        self.waveform1.setLogMode(x=True, y=True)    # Escala logarítmica
        self.waveform1.setXRange(20, 20000, padding=0) # Rango de frecuencia
        self.waveform1.setYRange(-120, 0, padding=0)   # Rango de amplitud en dB
        self.waveform1.setLabel('left', 'Nivel (dB)')
        self.waveform1.setLabel('bottom', 'Frecuencia (Hz)')
        
        # Actualizar controles de configuración en tab_2
        self.cbEscalaX.setChecked(True)
        self.cbEscalaY.setChecked(True)
        self.txtXMin.setText("20")
        self.txtXMax.setText("20000")
        self.txtYMin.setText("-120")
        self.txtYMax.setText("0")
        self.txtEtiquetaX.setText("Frecuencia (Hz)")
        self.txtEtiquetaY.setText("Nivel (dB)")
        
        # Actualizar el gráfico
        self.waveform1.replot()
        self.vController.graficar()
        
    def ventanaNivel(self):
        self.btnTiempo.setChecked(False)
        self.btnFrecuencia.setChecked(False)
        self.tabFilt.setEnabled(True)
        self.tabNieles.setEnabled(True)
        
        # Limpiar el gráfico actual
        self.waveform1.clear()
        
        # Configuración para gráfico de nivel
        self.waveform1.setLogMode(x=False, y=False)  # Escala lineal
        self.waveform1.setYRange(-120, 0, padding=0)  # Rango de presión en dB
        self.waveform1.setXRange(0, 1024, padding=0)  # Rango de tiempo
        self.waveform1.setLabel('left', 'Nivel fondo de escala (dB)')
        self.waveform1.setLabel('bottom', 'Tiempo')
        
        # Actualizar controles de configuración en tab_2
        self.cbEscalaX.setChecked(False)
        self.cbEscalaY.setChecked(False)
        self.txtXMin.setText("0")
        self.txtXMax.setText("1024")
        self.txtYMin.setText("-120")
        self.txtYMax.setText("0")
        self.txtEtiquetaX.setText("Tiempo")
        self.txtEtiquetaY.setText("Nivel fondo de escala (dB)")
        
        # Actualizar el gráfico
        self.waveform1.replot()
        self.vController.graficar()

    def graficar(self):
        self.vController.graficar()

    def animation(self):
        """Inicia el bucle principal de la aplicación"""
        self.show()
        return self.app.exec_()
        
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

    def configuracionAutomatica(self):
        """Aplica la configuración automática según el tipo de gráfico seleccionado"""
        try:
            if self.btnTiempo.isChecked():
                # Configuración para gráfico de tiempo
                self.cbEscalaX.setChecked(False)
                self.cbEscalaY.setChecked(False)
                self.txtXMin.setText("0")
                self.txtXMax.setText("1024")
                self.txtYMin.setText("-1")
                self.txtYMax.setText("1")
                self.txtEtiquetaX.setText("Tiempo")
                self.txtEtiquetaY.setText("Amplitud Normalizada")
                
                # Aplicar configuración
                self.waveform1.setLogMode(x=False, y=False)
                self.waveform1.setXRange(0, 1024, padding=0)
                self.waveform1.setYRange(-1, 1, padding=0)
                self.waveform1.setLabel('bottom', 'Tiempo')
                self.waveform1.setLabel('left', 'Amplitud Normalizada')
                
            elif self.btnFrecuencia.isChecked():
                # Configuración para gráfico de frecuencia
                self.cbEscalaX.setChecked(True)
                self.cbEscalaY.setChecked(True)
                self.txtXMin.setText("20")
                self.txtXMax.setText("20000")
                self.txtYMin.setText("-120")
                self.txtYMax.setText("0")
                self.txtEtiquetaX.setText("Frecuencia (Hz)")
                self.txtEtiquetaY.setText("Nivel (dB)")
                
                # Aplicar configuración
                self.waveform1.setLogMode(x=True, y=True)
                self.waveform1.setXRange(20, 20000, padding=0)
                self.waveform1.setYRange(-120, 0, padding=0)
                self.waveform1.setLabel('bottom', 'Frecuencia (Hz)')
                self.waveform1.setLabel('left', 'Nivel (dB)')
                
            elif self.btnNivel.isChecked():
                # Configuración para gráfico de nivel
                self.cbEscalaX.setChecked(False)
                self.cbEscalaY.setChecked(False)
                self.txtXMin.setText("0")
                self.txtXMax.setText("1024")
                self.txtYMin.setText("-120")
                self.txtYMax.setText("0")
                self.txtEtiquetaX.setText("Tiempo")
                self.txtEtiquetaY.setText("Nivel fondo de escala (dB)")
                
                # Aplicar configuración
                self.waveform1.setLogMode(x=False, y=False)
                self.waveform1.setXRange(0, 1024, padding=0)
                self.waveform1.setYRange(-120, 0, padding=0)
                self.waveform1.setLabel('bottom', 'Tiempo')
                self.waveform1.setLabel('left', 'Nivel fondo de escala (dB)')
            
            # Actualizar el gráfico
            self.waveform1.replot()
            
        except Exception as e:
            print(f"Error en configuración automática: {e}")