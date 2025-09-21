# Importo librerias

import pyqtgraph as pg
from ventanas.programarWin import ProgramarWin
from ventanas.calibracionWin import CalibracionWin
from ventanas.configDispWin import ConfigDispWin
from ventanas.configuracionWin import ConfiguracionWin
from ventanas.generadorWin import GeneradorWin

from PyQt5.QtWidgets import (QMainWindow, QApplication, QHBoxLayout, QVBoxLayout, QTabWidget, QPushButton,
                             QLabel, QGroupBox, QRadioButton, QCheckBox, QAction, QWidget, QGridLayout,
                             QMenu, QMessageBox, QColorDialog, QFileDialog,QFrame)

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
            strings.append(f"{val:.2f}")
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

    def create_checkbox_with_subscript(self, text, parent):
        # Crear un widget contenedor
        container = QWidget(parent)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Crear el checkbox sin texto
        checkbox = QCheckBox(container)
        
        # Crear el label con formato HTML
        styled_text = text.replace('<sub>', '<sub style="font-size: 14px;">').replace('</sub>', '</sub>')
        label = QLabel(styled_text, container)
        label.setTextFormat(Qt.RichText)
        label.setProperty("class", "subscript")
        
        layout.addWidget(checkbox)
        layout.addWidget(label)
        
        # Hacer que el label sea clickeable para activar el checkbox
        def toggle_checkbox():
            checkbox.setChecked(not checkbox.isChecked())
        
        label.mousePressEvent = lambda event: toggle_checkbox()
        
        # Almacenar referencia al checkbox para acceso fácil
        container.checkbox = checkbox
        
        # Retornar tanto el contenedor como el checkbox para facilitar el uso
        return container, checkbox

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
        self.setWindowIcon(QIcon('img/LogoCINTRA1.png'))
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
        #self.var_logModeXTiempo = False
        self.var_logModeYTiempo = False
        self.var_logModeXEspectro = True
        self.var_logModeYEspectro = False
        self.var_logModeXNivel = False
        self.var_logModeYNivel = False
        self.var_xMinTiempo = 0
        self.var_xMaxTiempo = 1024
        self.var_yMinTiempo = -1
        self.var_yMaxTiempo = 1
        self.var_xMinEspectro = np.log10(20)
        self.var_xMaxEspectro = np.log10(20000)
        self.var_eje2Visible = True
        self.var_valoresOctavas = True
        self.var_yMinEspectro = -120
        self.var_yMaxEspectro = 0
        self.var_xMinNivel = 0
        self.var_xMaxNivel = 1024
        self.var_yMinNivel = -150
        self.var_yMaxNivel = 0
        self.var_etiquetaXTiempo = "Tiempo (s)"
        self.var_etiquetaYTiempo = "Amplitud Normalizada"
        self.var_etiquetaXEspectro = "Frecuencia (Hz)"
        self.var_etiquetaYEspectro = "Nivel (dBFS)"
        self.var_etiquetaXNivel = "Tiempo (s)"
        self.var_etiquetaYNivel = "Nivel fondo de escala (dB)"
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
        self.btngbr.setToolTip("Iniciar o pausa la grabacion de audio")
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
        tipoGraficoGroup = QGroupBox("Análisis")
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
        self.filtrosGroup = QGroupBox("Filtros ponderados frecuenciales")
        filtrosLayout = QHBoxLayout()
        
        self.r0 = QRadioButton("A")
        self.r1 = QRadioButton("C")
        self.r2 = QRadioButton("Z")
        self.r2.setChecked(True)
        
        # Connect radio button signals to graficar method
        self.r0.toggled.connect(lambda: self.vController.graficar())
        self.r1.toggled.connect(lambda: self.vController.graficar())
        self.r2.toggled.connect(lambda: self.vController.graficar())
        
        filtrosLayout.addWidget(self.r0)
        filtrosLayout.addWidget(self.r1)
        filtrosLayout.addWidget(self.r2)
        self.filtrosGroup.setLayout(filtrosLayout)
        self.rightLayout.addWidget(self.filtrosGroup)
        
        # Niveles estadísticos
        self.nivelesGroup = QGroupBox("Niveles sonoros")        
    
        nivelesLayout = QGridLayout()
        
        self.nivelesGroup.setLayout(nivelesLayout)
        
        # Layout para Pico
        self.lblNivelesPico = QLabel("Pico\n"
                                     "(Peak)")
        self.cbNivPicoA_container, self.cbNivPicoA = self.create_checkbox_with_subscript("L<sub>Apk</sub>", self.nivelesGroup)
        self.cbNivPicoC_container, self.cbNivPicoC = self.create_checkbox_with_subscript("L<sub>Cpk</sub>", self.nivelesGroup)
        self.cbNivPicoZ_container, self.cbNivPicoZ = self.create_checkbox_with_subscript("L<sub>Zpk</sub>", self.nivelesGroup)
        
        nivelesLayout.addWidget(self.lblNivelesPico, 0, 0,QtCore.Qt.AlignCenter)
        nivelesLayout.addWidget(self.cbNivPicoA_container,0,1)
        nivelesLayout.addWidget(self.cbNivPicoC_container,0,2)
        nivelesLayout.addWidget(self.cbNivPicoZ_container,0,3)
        
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        nivelesLayout.addWidget(line1, 1, 0, 1, 4)


        # Layout para Instantaneo
        self.lblNivelesInst = QLabel("Impulsivo \n"
                                     "(Impulsive)")
        self.cbNivInstA_container, self.cbNivInstA = self.create_checkbox_with_subscript("L<sub>AI</sub>", self.nivelesGroup)
        self.cbNivInstC_container, self.cbNivInstC = self.create_checkbox_with_subscript("L<sub>CI</sub>", self.nivelesGroup)
        self.cbNivInstZ_container, self.cbNivInstZ = self.create_checkbox_with_subscript("L<sub>ZI</sub>", self.nivelesGroup)
        self.cbNivInstMinA_container, self.cbNivInstMinA = self.create_checkbox_with_subscript("L<sub>AImin</sub>", self.nivelesGroup)
        self.cbNivInstMinC_container, self.cbNivInstMinC = self.create_checkbox_with_subscript("L<sub>CImin</sub>", self.nivelesGroup)
        self.cbNivInstMinZ_container, self.cbNivInstMinZ = self.create_checkbox_with_subscript("L<sub>ZImin</sub>", self.nivelesGroup)
        self.cbNivInstMaxA_container, self.cbNivInstMaxA = self.create_checkbox_with_subscript("L<sub>AImax</sub>", self.nivelesGroup)
        self.cbNivInstMaxC_container, self.cbNivInstMaxC = self.create_checkbox_with_subscript("L<sub>CImax</sub>", self.nivelesGroup)
        self.cbNivInstMaxZ_container, self.cbNivInstMaxZ = self.create_checkbox_with_subscript("L<sub>ZImax</sub>", self.nivelesGroup)
        
        nivelesLayout.addWidget(self.lblNivelesInst, 2, 0,3,1,QtCore.Qt.AlignCenter)  
        # Primera fila
        nivelesLayout.addWidget(self.cbNivInstA_container, 2, 1)
        nivelesLayout.addWidget(self.cbNivInstC_container, 3, 1)
        nivelesLayout.addWidget(self.cbNivInstZ_container, 4, 1)
        # Segunda fila
        nivelesLayout.addWidget(self.cbNivInstMinA_container, 2, 2)
        nivelesLayout.addWidget(self.cbNivInstMinC_container, 3, 2)
        nivelesLayout.addWidget(self.cbNivInstMinZ_container, 4, 2)
        # Tercera fila
        nivelesLayout.addWidget(self.cbNivInstMaxA_container, 2, 3)
        nivelesLayout.addWidget(self.cbNivInstMaxC_container, 3, 3)
        nivelesLayout.addWidget(self.cbNivInstMaxZ_container, 4, 3)
        
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        nivelesLayout.addWidget(line2, 5, 0, 1, 4)

        # Layout para Instantaneo
        self.lblNivelesFast = QLabel("Rápido \n"
                                     "(Fast)")
        self.cbNivFastA_container, self.cbNivFastA = self.create_checkbox_with_subscript("L<sub>AF</sub>", self.nivelesGroup)
        self.cbNivFastC_container, self.cbNivFastC = self.create_checkbox_with_subscript("L<sub>CF</sub>", self.nivelesGroup)
        self.cbNivFastZ_container, self.cbNivFastZ = self.create_checkbox_with_subscript("L<sub>ZF</sub>", self.nivelesGroup)
        self.cbNivFastMinA_container, self.cbNivFastMinA = self.create_checkbox_with_subscript("L<sub>AFmin</sub>", self.nivelesGroup)
        self.cbNivFastMinC_container, self.cbNivFastMinC = self.create_checkbox_with_subscript("L<sub>CFmin</sub>", self.nivelesGroup)
        self.cbNivFastMinZ_container, self.cbNivFastMinZ = self.create_checkbox_with_subscript("L<sub>ZFmin</sub>", self.nivelesGroup)
        self.cbNivFastMaxA_container, self.cbNivFastMaxA = self.create_checkbox_with_subscript("L<sub>AFmax</sub>", self.nivelesGroup)
        self.cbNivFastMaxC_container, self.cbNivFastMaxC = self.create_checkbox_with_subscript("L<sub>CFmax</sub>", self.nivelesGroup)
        self.cbNivFastMaxZ_container, self.cbNivFastMaxZ = self.create_checkbox_with_subscript("L<sub>ZFmax</sub>", self.nivelesGroup)
        
        nivelesLayout.addWidget(self.lblNivelesFast, 6, 0,3,1,QtCore.Qt.AlignCenter)  
        # Primera fila
        nivelesLayout.addWidget(self.cbNivFastA_container, 6, 1)
        nivelesLayout.addWidget(self.cbNivFastC_container, 7, 1)
        nivelesLayout.addWidget(self.cbNivFastZ_container, 8, 1)
        # Segunda fila
        nivelesLayout.addWidget(self.cbNivFastMinA_container, 6, 2)
        nivelesLayout.addWidget(self.cbNivFastMinC_container, 7, 2)
        nivelesLayout.addWidget(self.cbNivFastMinZ_container, 8, 2)
        # Tercera fila
        nivelesLayout.addWidget(self.cbNivFastMaxA_container, 6, 3)
        nivelesLayout.addWidget(self.cbNivFastMaxC_container, 7, 3)
        nivelesLayout.addWidget(self.cbNivFastMaxZ_container, 8, 3)

        line3 = QFrame()
        line3.setFrameShape(QFrame.HLine)
        line3.setFrameShadow(QFrame.Sunken)
        nivelesLayout.addWidget(line3, 9, 0, 1, 4)
        
        # Layout para Slow
        self.lblNivelesPico = QLabel("Lento\n"
                                     "(Slow)")
        self.cbNivSlowA_container, self.cbNivSlowA = self.create_checkbox_with_subscript("L<sub>AS</sub>", self.nivelesGroup)
        self.cbNivSlowC_container, self.cbNivSlowC = self.create_checkbox_with_subscript("L<sub>CS</sub>", self.nivelesGroup)
        self.cbNivSlowZ_container, self.cbNivSlowZ = self.create_checkbox_with_subscript("L<sub>ZS</sub>", self.nivelesGroup)
        self.cbNivSlowMinA_container, self.cbNivSlowMinA = self.create_checkbox_with_subscript("L<sub>ASmin</sub>", self.nivelesGroup)
        self.cbNivSlowMinC_container, self.cbNivSlowMinC = self.create_checkbox_with_subscript("L<sub>CSmin</sub>", self.nivelesGroup)
        self.cbNivSlowMinZ_container, self.cbNivSlowMinZ = self.create_checkbox_with_subscript("L<sub>ZSmin</sub>", self.nivelesGroup)
        self.cbNivSlowMaxA_container, self.cbNivSlowMaxA = self.create_checkbox_with_subscript("L<sub>ASmax</sub>", self.nivelesGroup)
        self.cbNivSlowMaxC_container, self.cbNivSlowMaxC = self.create_checkbox_with_subscript("L<sub>CSmax</sub>", self.nivelesGroup)
        self.cbNivSlowMaxZ_container, self.cbNivSlowMaxZ = self.create_checkbox_with_subscript("L<sub>ZSmax</sub>", self.nivelesGroup)
        
        nivelesLayout.addWidget(self.lblNivelesPico, 10, 0,3,1,QtCore.Qt.AlignCenter)  
        # Primera fila
        nivelesLayout.addWidget(self.cbNivSlowA_container, 10, 1)
        nivelesLayout.addWidget(self.cbNivSlowC_container, 11, 1)
        nivelesLayout.addWidget(self.cbNivSlowZ_container, 12, 1)
        # Segunda fila
        nivelesLayout.addWidget(self.cbNivSlowMinA_container, 10, 2)
        nivelesLayout.addWidget(self.cbNivSlowMinC_container, 11, 2)
        nivelesLayout.addWidget(self.cbNivSlowMinZ_container, 12, 2)
        # Tercera fila
        nivelesLayout.addWidget(self.cbNivSlowMaxA_container, 10, 3)
        nivelesLayout.addWidget(self.cbNivSlowMaxC_container, 11, 3)
        nivelesLayout.addWidget(self.cbNivSlowMaxZ_container, 12, 3)
        
        line4 = QFrame()
        line4.setFrameShape(QFrame.HLine)
        line4.setFrameShadow(QFrame.Sunken)
        nivelesLayout.addWidget(line4, 13, 0, 1, 4)
        
        # Layout para filtro Z
        self.cbEqZ_container, self.cbEqZ = self.create_checkbox_with_subscript("L<sub>Zeq</sub>", self.nivelesGroup)
        self.cb01Z_container, self.cb01Z = self.create_checkbox_with_subscript("L<sub>Z01</sub>", self.nivelesGroup)
        self.cb10Z_container, self.cb10Z = self.create_checkbox_with_subscript("L<sub>Z10</sub>", self.nivelesGroup)
        self.cb50Z_container, self.cb50Z = self.create_checkbox_with_subscript("L<sub>Z50</sub>", self.nivelesGroup)
        self.cb90Z_container, self.cb90Z = self.create_checkbox_with_subscript("L<sub>Z90</sub>", self.nivelesGroup)
        self.cb99Z_container, self.cb99Z = self.create_checkbox_with_subscript("L<sub>Z99</sub>", self.nivelesGroup)

        # Layout para filtro C
        self.cbEqC_container, self.cbEqC = self.create_checkbox_with_subscript("L<sub>Ceq</sub>", self.nivelesGroup)
        self.cb01C_container, self.cb01C = self.create_checkbox_with_subscript("L<sub>C01</sub>", self.nivelesGroup)
        self.cb10C_container, self.cb10C = self.create_checkbox_with_subscript("L<sub>C10</sub>", self.nivelesGroup)
        self.cb50C_container, self.cb50C = self.create_checkbox_with_subscript("L<sub>C50</sub>", self.nivelesGroup)
        self.cb90C_container, self.cb90C = self.create_checkbox_with_subscript("L<sub>C90</sub>", self.nivelesGroup)
        self.cb99C_container, self.cb99C = self.create_checkbox_with_subscript("L<sub>C99</sub>", self.nivelesGroup)

        # Layout para filtro A
        self.cbEqA_container, self.cbEqA = self.create_checkbox_with_subscript("L<sub>Aeq</sub>", self.nivelesGroup)
        self.cb01A_container, self.cb01A = self.create_checkbox_with_subscript("L<sub>A01</sub>", self.nivelesGroup)
        self.cb10A_container, self.cb10A = self.create_checkbox_with_subscript("L<sub>A10</sub>", self.nivelesGroup)
        self.cb50A_container, self.cb50A = self.create_checkbox_with_subscript("L<sub>A50</sub>", self.nivelesGroup)
        self.cb90A_container, self.cb90A = self.create_checkbox_with_subscript("L<sub>A90</sub>", self.nivelesGroup)
        self.cb99A_container, self.cb99A = self.create_checkbox_with_subscript("L<sub>A99</sub>", self.nivelesGroup)

        
        # Primera fila
        self.lblNivelesContinuaEq = QLabel("Continua equivalente")
        nivelesLayout.addWidget(self.lblNivelesContinuaEq, 14, 0, QtCore.Qt.AlignCenter)
        nivelesLayout.addWidget(self.cbEqZ_container, 14, 3)
        nivelesLayout.addWidget(self.cbEqC_container, 14, 2)
        nivelesLayout.addWidget(self.cbEqA_container, 14, 1)
        
        line5 = QFrame()
        line5.setFrameShape(QFrame.HLine)
        line5.setFrameShadow(QFrame.Sunken)
        nivelesLayout.addWidget(line5, 15, 0, 1, 4)
        
        # Segunda fila
        self.lblNivelesPercentiles = QLabel("Percentiles\n"
                                            "(Percentile)")
        nivelesLayout.addWidget(self.lblNivelesPercentiles, 16, 0,5,1,QtCore.Qt.AlignCenter)
        nivelesLayout.addWidget(self.cb01Z_container, 16, 3)
        nivelesLayout.addWidget(self.cb01C_container, 16, 2)
        nivelesLayout.addWidget(self.cb01A_container, 16, 1)
        
        # Tercera fila
        nivelesLayout.addWidget(self.cb10Z_container, 17, 3)
        nivelesLayout.addWidget(self.cb10C_container, 17, 2)
        nivelesLayout.addWidget(self.cb10A_container, 17, 1)
        
        # Cuarta fila
        nivelesLayout.addWidget(self.cb50Z_container, 18, 3)
        nivelesLayout.addWidget(self.cb50C_container, 18, 2)
        nivelesLayout.addWidget(self.cb50A_container, 18, 1)
        
         # Quinta fila
        nivelesLayout.addWidget(self.cb90Z_container, 19, 3)
        nivelesLayout.addWidget(self.cb90C_container, 19, 2)
        nivelesLayout.addWidget(self.cb90A_container, 19, 1)
        
        # Sexta fila
        nivelesLayout.addWidget(self.cb99Z_container, 20, 3)
        nivelesLayout.addWidget(self.cb99C_container, 20, 2)
        nivelesLayout.addWidget(self.cb99A_container, 20, 1)
    
        self.btnClearNIntegra = QPushButton("Limpiar")
        self.btnClearNIntegra.clicked.connect(self.limpiarNiveles)
        self.btnClearNIntegra.setToolTip("Desmarca todos los niveles")
        self.btnClearNIntegra.setProperty("class", "filtros")
        nivelesLayout.addWidget(self.btnClearNIntegra, 21, 3, QtCore.Qt.AlignRight)
        
        
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
        
        self.cbEqA.toggled.connect(self.actualizarGraficoNivel)
        self.cb01A.toggled.connect(self.actualizarGraficoNivel)
        self.cb10A.toggled.connect(self.actualizarGraficoNivel)
        self.cb50A.toggled.connect(self.actualizarGraficoNivel)
        self.cb90A.toggled.connect(self.actualizarGraficoNivel)
        self.cb99A.toggled.connect(self.actualizarGraficoNivel)
        self.cbEqC.toggled.connect(self.actualizarGraficoNivel)
        self.cb01C.toggled.connect(self.actualizarGraficoNivel)
        self.cb10C.toggled.connect(self.actualizarGraficoNivel)
        self.cb50C.toggled.connect(self.actualizarGraficoNivel)
        self.cb90C.toggled.connect(self.actualizarGraficoNivel)
        self.cb99C.toggled.connect(self.actualizarGraficoNivel)
        self.cbEqZ.toggled.connect(self.actualizarGraficoNivel)
        self.cb01Z.toggled.connect(self.actualizarGraficoNivel)
        self.cb10Z.toggled.connect(self.actualizarGraficoNivel)
        self.cb50Z.toggled.connect(self.actualizarGraficoNivel)
        self.cb90Z.toggled.connect(self.actualizarGraficoNivel)
        self.cb99Z.toggled.connect(self.actualizarGraficoNivel)
        
        
        
        # Debug para verificar el estado inicial de los checkboxes
        print(f"DEBUG: Estado inicial cbNivSlowZ: {self.cbNivSlowZ.isChecked()}")
        
        self.rightLayout.addWidget(self.nivelesGroup)
        
        self.rightLayout.addStretch()
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
        calAct = QAction("Menú calibración", self)
        calAct.triggered.connect(self.vController.abrir_calibracion)
        self.menuCalibracion.addAction(calAct)

        # Otros menús
        self.menuConfiguracion = QMenu("Configuración", self)
        configAct = QAction("Configuración de gráficos", self)
        configAct.triggered.connect(self.vController.abrir_configuracion)
        self.menuConfiguracion.addAction(configAct)
        # Nueva acción para configuración de dispositivo
        configDispAct = QAction("Configuración de dispositivo", self)
        configDispAct.triggered.connect(self.vController.abrir_config_disp)
        self.menuConfiguracion.addAction(configDispAct)
        # Nueva acción para configuración de dispositivo
        genSig = QAction("Generador de señales", self)
        genSig.triggered.connect(self.vController.abrir_generador)
        self.menuConfiguracion.addAction(genSig)
       
        self.menuConfiguracion.setToolTip("Configuraciones de gráfico y dispositivos")
        
        self.menuProgramacion = QMenu("Programación", self)
        progAct = QAction("Programar", self)
        progAct.triggered.connect(self.vController.abrir_programar)
        self.menuProgramacion.addAction(progAct)
        grab = QAction("Grabaciones", self)
        grab.triggered.connect(self.vController.abrir_grabaciones)
        self.menuProgramacion.addAction(grab)
        
        self.menuAyuda = QMenu("Ayuda", self)
        self.menuAcerca_de = QMenu("Acerca de...", self)
        
        # Agregar acción para abrir el sitio web de CINTRA
        acercaCintraAct = QAction("Sitio web CINTRA", self)
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
        self.filtrosGroup.setVisible(False)
        self.nivelesGroup.setVisible(False)
        
        # Limpiar el gráfico actual
        self.waveform1.clear()
        
        # Configuración para gráfico de tiempo
        self.waveform1.setLogMode(x=False, y=False)  # Escala lineal
        self.waveform1.setYRange(-1, 1, padding=0)   # Amplitud normalizada
        self.waveform1.setXRange(0, 1024, padding=0) # Rango de tiempo
        self._ejeY_titulo_base = "Amplitud Normalizada"
        self.waveform1.setLabel('left', self._ejeY_titulo_base)
        self.waveform1.setLabel('bottom', 'Tiempo (s)')
        self.actualizar_badge_calibracion_pyqtgraph()
        
        # Actualizar el gráfico
        self.waveform1.replot()

        with open("estilos.qss", "r", encoding='utf-8') as f:
            self.app.setStyleSheet(f.read())
            
        self.show()        
        
    def limpiarNiveles(self):
        """Desmarca todos los checkboxes de niveles"""
        self.cbNivPicoA.setChecked(False)
        self.cbNivPicoC.setChecked(False)
        self.cbNivPicoZ.setChecked(False)
        self.cbNivInstA.setChecked(False)
        self.cbNivInstC.setChecked(False)
        self.cbNivInstZ.setChecked(False)
        self.cbNivInstMinA.setChecked(False)
        self.cbNivInstMinC.setChecked(False)
        self.cbNivInstMinZ.setChecked(False)
        self.cbNivInstMaxA.setChecked(False)
        self.cbNivInstMaxC.setChecked(False)
        self.cbNivInstMaxZ.setChecked(False)
        self.cbNivFastA.setChecked(False)
        self.cbNivFastC.setChecked(False)
        self.cbNivFastZ.setChecked(False)
        self.cbNivFastMinA.setChecked(False)
        self.cbNivFastMinC.setChecked(False)
        self.cbNivFastMinZ.setChecked(False)
        self.cbNivFastMaxA.setChecked(False)
        self.cbNivFastMaxC.setChecked(False)
        self.cbNivFastMaxZ.setChecked(False)
        self.cbNivSlowA.setChecked(False)
        self.cbNivSlowC.setChecked(False)
        self.cbNivSlowZ.setChecked(False)
        self.cbNivSlowMinA.setChecked(False)
        self.cbNivSlowMinC.setChecked(False)
        self.cbNivSlowMinZ.setChecked(False)
        self.cbNivSlowMaxA.setChecked(False)
        self.cbNivSlowMaxC.setChecked(False)
        self.cbNivSlowMaxZ.setChecked(False)
        self.cbEqZ.setChecked(False)
        self.cb01Z.setChecked(False)
        self.cb10Z.setChecked(False)
        self.cb50Z.setChecked(False)
        self.cb90Z.setChecked(False)
        self.cb99Z.setChecked(False)
        self.cbEqC.setChecked(False)
        self.cb01C.setChecked(False)
        self.cb10C.setChecked(False)
        self.cb50C.setChecked(False)
        self.cb90C.setChecked(False)
        self.cb99C.setChecked(False)
        self.cbEqA.setChecked(False)
        self.cb01A.setChecked(False)
        self.cb10A.setChecked(False)
        self.cb50A.setChecked(False)
        self.cb90A.setChecked(False)
        self.cb99A.setChecked(False)
      
    def configure_bar_chart_y_range(self, niveles):
        """
        Configura el rango Y para el gráfico de barras.
        Va desde -120 dB (piso de ruido) hasta el valor máximo capturado.
        Las barras se extienden desde -120 dB hacia arriba hasta el valor capturado.
        """
        y_min = -120.0
        y_max = np.max(niveles) if len(niveles) > 0 else -20.0
        if y_max < y_min + 20:
            y_max = y_min + 20

        if not hasattr(self, 'fft_ymin') or not hasattr(self, 'fft_ymax'):
            self.fft_ymin = y_min
            self.fft_ymax = y_max
        else:
            self.fft_ymin = -120.0
            if y_max > self.fft_ymax:
                self.fft_ymax = y_max

        return self.fft_ymin, self.fft_ymax  
    
    def abrirprogramarWin(self):
        self.programar_win = ProgramarWin()
        self.programar_win.show()

    def GeneradorSenales(self):
        self.genSenalesWin = GeneradorWin(self.vController)
        self.genSenalesWin.show()
        
    def configuracionDispositivo(self):
        self.calWin = CalibracionWin(self.vController)
        self.configDispWin = ConfigDispWin(self.vController,self.calWin )
        self.configDispWin.show()
        
    def calibracionWin(self):
        self.calWin = CalibracionWin(self.vController,self)
        self.calWin.show()
        
    # CODIGO configuracion del graficos
    def configuracion(self):
        self.confWin = ConfiguracionWin(self)
        self.confWin.show()

    
    def grabar(self):
        self.editar_botonGrabar() 
        if self.btngbr.isChecked():
            # Reset everything when starting a new recording
            self.vController.reset_all_data()
        self.vController.dalePlay() # conexion con el controlador

    def editar_botonGrabar(self):
        """Edita el botón de grabar para que se vea como un botón de pausa"""
        if self.btngbr.isChecked():
            self.btngbr.setText("Pausar")
            self.btngbr.setIcon(QIcon("img/boton-de-pausa.png"))
        else:
            self.btngbr.setText("Grabar")
            self.btngbr.setIcon(QIcon("img/boton-de-play.png"))
    
    def _sync_vb_right(self):
        if hasattr(self, 'vb_right'):
            self.vb_right.setGeometry(self.waveform1.vb.sceneBoundingRect())
            self.vb_right.linkedViewChanged(self.waveform1.vb, self.vb_right.XAxis)

    def _ensure_right_axis(self):
        if hasattr(self, 'vb_right'):
            return
        self.waveform1.showAxis('right')
        self.vb_right = pg.ViewBox()
        self.waveform1.scene().addItem(self.vb_right)
        self.waveform1.getAxis('right').linkToView(self.vb_right)
        self.vb_right.setXLink(self.waveform1.vb)   # comparte X
        self.vb_right.setYRange(0, 120, padding=0)
        self.waveform1.vb.sigResized.connect(self._sync_vb_right)
        self._sync_vb_right()

    def _remove_right_axis(self):
        axr = self.waveform1.getAxis('right')

        if hasattr(self, 'vb_right'):
            try:
                self.waveform1.vb.sigResized.disconnect(self._sync_vb_right)
            except Exception:
                pass
            # re-vincula a la vista principal para evitar weakref(None)
            axr.linkToView(self.waveform1.vb)
            self.waveform1.scene().removeItem(self.vb_right)
            del self.vb_right

        self.waveform1.hideAxis('right')
        axr.setLabel('')  # opcional
    
    def ventanaTiempo(self):
        self.btnNivel.setChecked(False)
        self.btnFrecuencia.setChecked(False)
        self.filtrosGroup.setVisible(False)
        self.nivelesGroup.setVisible(False)
        
        # Resetear bandera de nivel
        self.nivel_configured = False
        
        # Limpiar el gráfico actual
        self.waveform1.clear()
        self._remove_right_axis()
        
        
        # Asegurar que se use el eje de tiempo personalizado
        if not hasattr(self, 'time_axis') or self.waveform1.getAxis('bottom') != self.time_axis:
            self.time_axis = TimeAxisItem(orientation='bottom')
            self.waveform1.setAxisItems({'bottom': self.time_axis})
        
        # Aplicar configuración personalizada si existe, sino usar valores por defecto
        #if hasattr(self, 'txtXMinTiempo') and hasattr(self, 'txtXMaxTiempo'):
        if all(hasattr(self, a) for a in ("var_xMinTiempo", "var_xMaxTiempo")):
            self.aplicarConfiguracionTiempo()
        else:
            # Configuración por defecto para gráfico de tiempo
            self.waveform1.setLogMode(x=False, y=False)  # Escala lineal
            self.waveform1.setYRange(-1, 1, padding=0)   # Amplitud normalizada
            self.waveform1.setXRange(0, 1024, padding=0) # Rango de tiempo
            self.waveform1.setLabel('left', 'Amplitud Normalizada')
            self.waveform1.setLabel('bottom', 'Tiempo (s)')
            self.waveform1.setTitle('Gráfico de Dominio del Tiempo')
        
        # Actualizar el gráfico
        self.waveform1.replot()
        self.vController.graficar()
        
    def ventanaFrecuencia(self):
        self.btnNivel.setChecked(False)
        self.btnTiempo.setChecked(False)
        self.filtrosGroup.setVisible(True)
        self.nivelesGroup.setVisible(False)
        
        # Resetear bandera de nivel
        self.nivel_configured = False
        
        # Configurar el gráfico para frecuencia
        self.waveform1.clear()
        
        # Aplicar configuración personalizada si existe, sino usar valores por defecto
        #if hasattr(self, 'txtXMinEspectro') and hasattr(self, 'txtXMaxEspectro'):
        if all(hasattr(self, a) for a in ("var_xMinEspectro", "var_xMaxEspectro")):
            self.aplicarConfiguracionEspectro()
        else:
            # Configuración por defecto para gráfico de frecuencia
            self.waveform1.setLogMode(x=True, y=False)     # Escala logarítmica en X, lineal en Y
            self.waveform1.setXRange(np.log10(20), np.log10(20000))  # Rango de frecuencia logarítmico
            self.waveform1.setYRange(-120, 0)              # Rango de amplitud en dB
            
            # Configurar ticks del eje X para mostrar valores de frecuencia legibles
            ticks = [
                (np.log10(20), '20'),
                (np.log10(100), '100'),
                (np.log10(1000), '1k'),
                (np.log10(10000), '10k'),
                (np.log10(20000), '20k')
            ]
            self.waveform1.getAxis('bottom').setTicks([ticks])
            
            self.waveform1.setLabel('left', 'Nivel (dB)')
            self.waveform1.setLabel('bottom', 'Frecuencia (Hz)')
            self.waveform1.setTitle('Espectro de Frecuencia')
        
        # Actualizar el gráfico
        self.waveform1.replot()
        self.vController.graficar()
        
    def ventanaNivel(self):
        self.btnTiempo.setChecked(False)
        self.btnFrecuencia.setChecked(False)
        self.filtrosGroup.setVisible(False)
        self.nivelesGroup.setVisible(True)
        
        print("DEBUG: Configurando ventana de nivel")
        
        # Solo limpiar el gráfico si no está ya configurado para nivel
        if not hasattr(self, 'nivel_configured') or not self.nivel_configured:
            self.waveform1.clear()
            self.nivel_configured = True
        
        self._remove_right_axis()
        
        # Habilitar Z Slow por defecto para que se vea algo en el gráfico
        self.cbNivSlowZ.setChecked(True)
        print("DEBUG: Z Slow habilitado por defecto")
        
        # Aplicar configuración personalizada si existe, sino usar valores por defecto
        #if hasattr(self, 'txtXMinNivel') and hasattr(self, 'txtXMaxNivel'):
        if all(hasattr(self, a) for a in ("var_xMinNivel", "var_xMaxNivel")):
            self.aplicarConfiguracionNivel()
        else:
            # Configuración por defecto para gráfico de nivel
            self.waveform1.setLogMode(x=False, y=False)  # Escala lineal
            self.waveform1.setYRange(-120, 0, padding=0)
            # Invert the Y-axis to show negative values at the bottom
            self.waveform1.invertY(False) 
            self.waveform1.setXRange(0, 10, padding=0)  # Rango de tiempo en segundos
            self.waveform1.setLabel('left', 'Nivel fondo de escala (dB)')
            self.waveform1.setLabel('bottom', 'Tiempo (s)')
            self.waveform1.setTitle('Gráfico de Nivel de Presión Sonora')
            print("DEBUG: Configuración por defecto aplicada")
        
        # Actualizar el gráfico
        self.waveform1.replot()
        print("DEBUG: Gráfico actualizado")
        self.vController.graficar()

    def esta_calibrado(self) -> bool:
        m = self.vController.cModel
        cal_auto = False
        if hasattr(m, "getCalibracionAutomatica"):
            try:
                cal_auto = bool(m.getCalibracionAutomatica())
            except Exception:
                cal_auto = bool(getattr(m, "cal", False))
        ruta_ext = getattr(m, "get_ruta_archivo_calibracion", lambda: None)()
        offset  = float(getattr(m, "get_calibracion_offset_spl", lambda: 0.0)())
        return cal_auto or (ruta_ext is not None) or (abs(offset) > 1e-9)

    def actualizar_badge_calibracion_pyqtgraph(self):
        bandera = self.esta_calibrado()
        bandera2 = self.btnTiempo.isChecked()
        if bandera or bandera2:
            print("DEBUG: Está calibrado, actualizando badge")
            # Sin badge
            self.waveform1.setLabel('left', self._ejeY_titulo_base)
            if self.btnFrecuencia.isChecked():
                self.waveform1.getAxis('right').setLabel(self._ejeYDer_titulo_base)
        else:
            print("DEBUG: No está calibrado, actualizando badge")
            # Sufijo naranja "(sin calibrar)"
            self.waveform1.setLabel('left', f"{self._ejeY_titulo_base} <span style='color:#ff9800'>(sin calibrar)</span>")
            if self.btnFrecuencia.isChecked():
                self.waveform1.getAxis('right').setLabel(f"{self._ejeYDer_titulo_base} <span style='color:#ff9800'>(sin calibrar)</span>")
        
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
            self.waveform1.setLogMode(x=False, y=self.var_logModeYTiempo)
            # # Límites
            self.waveform1.setXRange(self.var_xMinTiempo, self.var_xMaxTiempo, padding=0)
            self.waveform1.setYRange(self.var_yMinTiempo, self.var_yMaxTiempo, padding=0)
            # # Etiquetas
            self._ejeY_titulo_base = self.var_etiquetaYTiempo
            self.waveform1.setLabel('bottom', self.var_etiquetaXTiempo)
            self.waveform1.setLabel('left', self._ejeY_titulo_base)
            # Color y tipo de línea
            if hasattr(self, 'colorTiempo'):
                color = self.get_color_str(self.colorTiempo)
            else:
                color = self.default_color_tiempo  # Color por defecto centralizado
            tipoLinea = self.obtenerTipoLinea("tiempo")
            self.actualizarEstiloLinea(color, tipoLinea)
            self.actualizar_badge_calibracion_pyqtgraph()
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
            self._ejeY_titulo_base = self.var_etiquetaYEspectro
            self.waveform1.setLabel('bottom', self.var_etiquetaXEspectro)
            self.waveform1.setLabel('left', self._ejeY_titulo_base)
            if self.var_eje2Visible:
                self._ensure_right_axis()
                self._ejeYDer_titulo_base = "Nivel (dB)"
                self.waveform1.getAxis('right').setLabel(self._ejeYDer_titulo_base)
                self.vb_right.setYRange(0, 120, padding=0)
            else:
                self._remove_right_axis()
            # Color y tipo de gráfico
            if hasattr(self, 'colorEspectro'):
                color = self.get_color_str(self.colorEspectro)
            else:
                color = self.default_color_espectro  # Color por defecto centralizado
            tipoGrafico = self.obtenerTipoGraficoEspectro()
            self.actualizarEstiloGraficoEspectro(color, tipoGrafico)
            self.actualizar_badge_calibracion_pyqtgraph()
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
            self._ejeY_titulo_base = self.var_etiquetaYNivel
            self.waveform1.setLabel('bottom', self.var_etiquetaXNivel)
            self.waveform1.setLabel('left', self._ejeY_titulo_base)
            # Color y tipo de línea
            if hasattr(self, 'colorNivel'):
                color = self.get_color_str(self.colorNivel)
            else:
                color = self.default_color_nivel  # Color por defecto centralizado
            tipoLinea = self.obtenerTipoLinea("nivel")
            self.actualizarEstiloLinea(color, tipoLinea)
            self.actualizar_badge_calibracion_pyqtgraph()
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

    def update_plot(self, device_num, current_data, all_data, normalized_current, normalized_all, device_name, times, fft_freqs, fft_magnitude):
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
                        # Calcular la altura de las barras desde -120 dB hasta el valor capturado
                        piso_ruido = -120.0
                        bar_heights = niveles - piso_ruido  # Altura = valor_capturado - (-120) = valor_capturado + 120
                        bar_bottoms = np.full_like(niveles, piso_ruido)  # Base de las barras en -120 dB
                        
                        # Debug: mostrar el color que se está usando
                        print(f"Color de las barras: {color}")
                        print(f"Tipo de color: {type(color)}")
                        
                        # Crear barras individuales usando PlotDataItem
                        print("Creando barras individuales...")
                        
                        # Calcular el ancho de cada barra para que se toquen (sin espacios)
                        total_width = len(bandas)  # Ancho total disponible
                        bar_width = total_width / len(bandas)  # Ancho de cada barra
                        
                        for i, (x, height, nivel) in enumerate(zip(x_positions, bar_heights, niveles)):
                            if height > 0:  # Solo crear barras con altura positiva
                                # Calcular los límites de la barra (sin espacios)
                                x_left = x - bar_width/2
                                x_right = x + bar_width/2
                                
                                # Crear puntos para la barra: base y cima
                                x_vals = [x_left, x_right, x_right, x_left, x_left]
                                y_vals = [piso_ruido, piso_ruido, nivel, nivel, piso_ruido]
                                
                                # Usar el color de la configuración
                                bar_color = self.get_color_str(color)
                                print(f"Usando color: {bar_color}")
                                
                                # Crear la barra como un PlotDataItem
                                bar_item = pg.PlotDataItem(
                                    x_vals, y_vals, 
                                    pen=pg.mkPen('black', width=1),
                                    brush=pg.mkBrush(bar_color),
                                    fillLevel=piso_ruido,
                                    fillBrush=pg.mkBrush(bar_color)
                                )
                                self.waveform1.addItem(bar_item)
                                print(f"Barra {i}: x={x:.1f}, ancho={bar_width:.2f}, altura={height:.1f}, nivel={nivel:.1f} dB")
                        
                        print(f"Total de barras creadas: {len([h for h in bar_heights if h > 0])}")
                        
                        if self.var_valoresOctavas:
                            for i, h in enumerate(niveles):
                                # Position the text slightly above the bar
                                text_item = pg.TextItem(text=f"{h:.2f}", anchor=(0.5, 0), color=(0, 0, 0, 115)) # Center horizontally, align to bottom of text
                                text_item.setPos(x_positions[i], h) # Adjust 0.5 for desired offset
                                text_item.setAngle(45)
                                self.waveform1.addItem(text_item)
                            
                        # Configurar rangos de ejes - ajustar para barras sin espacios
                        self.waveform1.setXRange(-0.5, len(bandas) - 0.5)
                        
                        # Configurar rango Y usando la función auxiliar
                        y_min, y_max = self.configure_bar_chart_y_range(niveles)
                        self.waveform1.setYRange(y_min, y_max)
                        
                        # Debug: mostrar información del rango Y
                        # print(f"Gráfico de barras - Rango Y: {y_min:.1f} dB a {y_max:.1f} dB")
                        # print(f"Niveles capturados: min={np.min(niveles):.1f} dB, max={np.max(niveles):.1f} dB")
                        # print(f"Alturas de barras: {bar_heights[:5]}... (desde -120 dB hasta valores capturados)")
                        # print(f"Las barras se extienden desde -120 dB hacia arriba hasta {y_max:.1f} dB")
                        # print(f"Posiciones X: {x_positions[:5]}...")
                        # print(f"Ancho de barras: {bar_width}")
                        # print(f"Piso de ruido: {piso_ruido}")
                        
                        # Etiquetas de ejes
                        self.waveform1.setLabel('left', 'Nivel (dB) - Barras desde -120 dB hacia arriba')
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
                        amp_plot = fft_magnitude[mask]  # Already in dB from model
                        
                        if len(freqs_plot) > 0:
                            self.waveform1.clear()
                            
                            # Limpiar barras anteriores si existen
                            if hasattr(self, 'current_bar_item'):
                                self.waveform1.removeItem(self.current_bar_item)
                                delattr(self, 'current_bar_item')
                            
                            # Configurar el gráfico para escala logarítmica en X y lineal en Y (dB)
                            self.waveform1.setAxisItems({'bottom': self.log_x_axis})
                            
                            # Graficar el espectro en dB
                            self.plot_line_freq = self.waveform1.plot(
                                np.log10(freqs_plot), 
                                amp_plot, 
                                pen=pg.mkPen(color=color, width=2)
                            )
                            
                            # Configurar rangos de los ejes
                            self.waveform1.setXRange(np.log10(20), np.log10(20000))
                            
                            # Actualizar etiquetas de los ejes
                            self.waveform1.setLabel('left', 'Nivel (dB)')
                            self.waveform1.setLabel('bottom', 'Frecuencia (Hz)')
                            self.waveform1.setTitle('Espectro de Frecuencia (dB)')
                            
                            # Configurar ticks del eje X para mostrar valores de frecuencia legibles
                            ticks = [
                                (np.log10(20), '20'),
                                (np.log10(100), '100'),
                                (np.log10(1000), '1k'),
                                (np.log10(10000), '10k'),
                                (np.log10(20000), '20k')
                            ]
                            self.waveform1.getAxis('bottom').setTicks([ticks])
                            if not hasattr(self, 'fft_ymin') or not hasattr(self, 'fft_ymax'):
                                self.fft_ymin = np.min(amp_plot)
                                self.fft_ymax = np.max(amp_plot)
                            else:
                                if np.min(amp_plot) < self.fft_ymin:
                                    self.fft_ymin = np.min(amp_plot)
                                if np.max(amp_plot) > self.fft_ymax:
                                    self.fft_ymax = np.max(amp_plot)
                            self.waveform1.setYRange(self.fft_ymin, self.fft_ymax)
                        self.waveform1.setLabel('left', 'Nivel (dB)')
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
                
                # Limpiar el gráfico completamente en cada actualización
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
                    
                    # --- Ploteo de niveles temporales (fluctuantes) ---
                    # Z Weighting (rojo, como en tu código original)
                    print(f"DEBUG: Checkboxes Z - Pico: {self.cbNivPicoZ.isChecked()}, Inst: {self.cbNivInstZ.isChecked()}, Fast: {self.cbNivFastZ.isChecked()}, Slow: {self.cbNivSlowZ.isChecked()}")
                    print(f"DEBUG: Datos Z lengths - Pico: {len(niveles_Z.get('pico', []))}, Inst: {len(niveles_Z.get('inst', []))}, Fast: {len(niveles_Z.get('fast', []))}, Slow: {len(niveles_Z.get('slow', []))}")
                    
                    if self.cbNivPicoZ.isChecked() and len(niveles_Z.get('pico', [])) > 0:
                        ydata = np.array(niveles_Z['pico'])
                        print(f"DEBUG PICO Z: Graficando {len(ydata)} puntos, último: {ydata[-1] if len(ydata)>0 else 'N/A'}")
                        plot = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='red', width=2, style=QtCore.Qt.SolidLine), name='Z Pico')
                        print(f"DEBUG PICO Z: Plot creado")

                    if self.cbNivInstZ.isChecked() and len(niveles_Z.get('inst', [])) > 0:
                        ydata = np.array(niveles_Z['inst'])
                        print(f"DEBUG INST Z: Graficando {len(ydata)} puntos, último: {ydata[-1] if len(ydata)>0 else 'N/A'}")
                        plot = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='red', width=2, style=QtCore.Qt.DashLine), name='Z Inst')
                        print(f"DEBUG INST Z: Plot creado")

                    if self.cbNivFastZ.isChecked() and len(niveles_Z.get('fast', [])) > 0:
                        ydata = np.array(niveles_Z['fast'])
                        print(f"DEBUG FAST Z: Graficando {len(ydata)} puntos, último: {ydata[-1] if len(ydata)>0 else 'N/A'}")
                        plot = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='red', width=2, style=QtCore.Qt.DotLine), name='Z Fast')
                        print(f"DEBUG FAST Z: Plot creado")

                    if self.cbNivSlowZ.isChecked() and len(niveles_Z.get('slow', [])) > 0:
                        ydata = np.array(niveles_Z['slow'])
                        print(f"DEBUG SLOW Z: Graficando {len(ydata)} puntos, último: {ydata[-1] if len(ydata)>0 else 'N/A'}")
                        plot = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='red', width=3, style=QtCore.Qt.SolidLine), name='Z Slow')
                        print(f"DEBUG SLOW Z: Plot creado")

                    # C Weighting (verde)
                    print(f"DEBUG: Checkboxes C - Pico: {self.cbNivPicoC.isChecked()}, Inst: {self.cbNivInstC.isChecked()}, Fast: {self.cbNivFastC.isChecked()}, Slow: {self.cbNivSlowC.isChecked()}")
                    print(f"DEBUG: Datos C lengths - Pico: {len(niveles_C.get('pico', []))}, Inst: {len(niveles_C.get('inst', []))}, Fast: {len(niveles_C.get('fast', []))}, Slow: {len(niveles_C.get('slow', []))}")
                    
                    if self.cbNivPicoC.isChecked() and len(niveles_C.get('pico', [])) > 0:
                        ydata = np.array(niveles_C['pico'])
                        print(f"DEBUG PICO C: Graficando {len(ydata)} puntos, último: {ydata[-1] if len(ydata)>0 else 'N/A'}")
                        plot = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='green', width=2, style=QtCore.Qt.SolidLine), name='C Pico')
                        print(f"DEBUG PICO C: Plot creado")
                    
                    if self.cbNivInstC.isChecked() and len(niveles_C.get('inst', [])) > 0:
                        ydata = np.array(niveles_C['inst'])
                        print(f"DEBUG INST C: Graficando {len(ydata)} puntos, último: {ydata[-1] if len(ydata)>0 else 'N/A'}")
                        plot = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='green', width=2, style=QtCore.Qt.DashLine), name='C Inst')
                        print(f"DEBUG INST C: Plot creado")
                    
                    if self.cbNivFastC.isChecked() and len(niveles_C.get('fast', [])) > 0:
                        ydata = np.array(niveles_C['fast'])
                        print(f"DEBUG FAST C: Graficando {len(ydata)} puntos, último: {ydata[-1] if len(ydata)>0 else 'N/A'}")
                        plot = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='green', width=2, style=QtCore.Qt.DotLine), name='C Fast')
                        print(f"DEBUG FAST C: Plot creado")
                    
                    if self.cbNivSlowC.isChecked() and len(niveles_C.get('slow', [])) > 0:
                        ydata = np.array(niveles_C['slow'])
                        print(f"DEBUG SLOW C: Graficando {len(ydata)} puntos, último: {ydata[-1] if len(ydata)>0 else 'N/A'}")
                        plot = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='green', width=3, style=QtCore.Qt.SolidLine), name='C Slow')
                        print(f"DEBUG SLOW C: Plot creado")
                    
                    # A Weighting (azul)
                    print(f"DEBUG: Checkboxes A - Pico: {self.cbNivPicoA.isChecked()}, Inst: {self.cbNivInstA.isChecked()}, Fast: {self.cbNivFastA.isChecked()}, Slow: {self.cbNivSlowA.isChecked()}")
                    print(f"DEBUG: Datos A lengths - Pico: {len(niveles_A.get('pico', []))}, Inst: {len(niveles_A.get('inst', []))}, Fast: {len(niveles_A.get('fast', []))}, Slow: {len(niveles_A.get('slow', []))}")
                    
                    if self.cbNivPicoA.isChecked() and len(niveles_A.get('pico', [])) > 0:
                        ydata = np.array(niveles_A['pico'])
                        print(f"DEBUG PICO A: Graficando {len(ydata)} puntos, último: {ydata[-1] if len(ydata)>0 else 'N/A'}")
                        plot = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='blue', width=2, style=QtCore.Qt.SolidLine), name='A Pico')
                        print(f"DEBUG PICO A: Plot creado")
                    
                    if self.cbNivInstA.isChecked() and len(niveles_A.get('inst', [])) > 0:
                        ydata = np.array(niveles_A['inst'])
                        print(f"DEBUG INST A: Graficando {len(ydata)} puntos, último: {ydata[-1] if len(ydata)>0 else 'N/A'}")
                        plot = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='blue', width=2, style=QtCore.Qt.DashLine), name='A Inst')
                        print(f"DEBUG INST A: Plot creado")
                    
                    if self.cbNivFastA.isChecked() and len(niveles_A.get('fast', [])) > 0:
                        ydata = np.array(niveles_A['fast'])
                        print(f"DEBUG FAST A: Graficando {len(ydata)} puntos, último: {ydata[-1] if len(ydata)>0 else 'N/A'}")
                        plot = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='blue', width=2, style=QtCore.Qt.DotLine), name='A Fast')
                        print(f"DEBUG FAST A: Plot creado")
                    
                    if self.cbNivSlowA.isChecked() and len(niveles_A.get('slow', [])) > 0:
                        ydata = np.array(niveles_A['slow'])
                        print(f"DEBUG SLOW A: Graficando {len(ydata)} puntos, último: {ydata[-1] if len(ydata)>0 else 'N/A'}")
                        plot = self.waveform1.plot(xdata, ydata, pen=pg.mkPen(color='blue', width=3, style=QtCore.Qt.SolidLine), name='A Slow')
                        print(f"DEBUG SLOW A: Plot creado")

                    # --- Ploteo de niveles estadísticos (horizontales constantes) ---
                    # Colores fijos por tipo de Ln (para parecerse al ejemplo: L10 rojo, L50 verde, L90 naranja)
                    # Usamos InfiniteLine en el último valor (asumiendo que es el percentile cumulativo actual)
                    color_map = {
                        'leq': 'purple',   # Leq: morado
                        'l01': 'yellow',   # L01: amarillo
                        'l10': 'red',      # L10: rojo
                        'l50': 'green',    # L50: verde
                        'l90': 'orange',   # L90: naranja
                        'l99': 'gray'      # L99: gris
                    }
                    style_map = QtCore.Qt.DashLine  # Dashed para todos los estadísticos
                    
                    # Función auxiliar para crear gráfico temporal de nivel estadístico
                    def plot_statistical_level(niveles_data, tiempos_data, color, label, checkbox_checked):
                        if not checkbox_checked or len(niveles_data) == 0:
                            return None
                            
                        # Asegurarse de que no haya valores NaN o infinitos
                        niveles_data = np.nan_to_num(niveles_data, nan=0.0, posinf=0.0, neginf=0.0)
                        
                        # Si los datos vienen con sus propios tiempos, usarlos
                        if isinstance(niveles_data, dict) and 'times' in niveles_data:
                            tiempos_hist = niveles_data['times']
                            niveles_data = niveles_data.get('data', np.array([]))
                        else:
                            # Usar los tiempos proporcionados como base
                            if len(tiempos_data) == 0:
                                tiempos_hist = np.arange(len(niveles_data))
                            elif len(tiempos_data) == len(niveles_data):
                                tiempos_hist = tiempos_data
                            elif len(tiempos_data) > len(niveles_data):
                                step = max(1, len(tiempos_data) // len(niveles_data))
                                tiempos_hist = tiempos_data[::step][:len(niveles_data)]
                            else:
                                tiempo_total = tiempos_data[-1] if len(tiempos_data) > 0 else len(niveles_data)
                                tiempos_hist = np.linspace(0, tiempo_total, len(niveles_data))
                        
                        # Asegurarse de que las longitudes coincidan
                        if len(niveles_data) > 0 and len(tiempos_hist) > 0:
                            min_len = min(len(tiempos_hist), len(niveles_data))
                            tiempos_hist = tiempos_hist[:min_len]
                            niveles_data = niveles_data[:min_len]
                            
                            # Crear el gráfico temporal
                            pen = pg.mkPen(color=color, width=2, style=style_map)
                            plot = self.waveform1.plot(tiempos_hist, niveles_data, pen=pen, name=label)
                            print(f"DEBUG Stats: Gráfico temporal creado para {label} con {len(niveles_data)} puntos")
                            return plot
                        return None
                    
                    # Obtener los tiempos para los niveles estadísticos (usar xdata escalado si es necesario)
                    def get_stat_times(data, base_times):
                        if len(data) == 0:
                            return np.array([])
                        if len(data) == len(base_times):
                            return base_times
                        # Si las longitudes no coinciden, escalar los tiempos
                        return np.linspace(0, base_times[-1] if len(base_times) > 0 else len(data), len(data))
                    
                    # Z Statistical - Gráficos temporales
                    plot_statistical_level(niveles_Z.get('leq', {}), xdata, color_map['leq'], 'Z Leq', self.cbEqZ.isChecked())
                    
                    # Z Statistical - Todos los niveles
                    plot_statistical_level(niveles_Z.get('l01', {}), xdata, color_map['l01'], 'Z L01', self.cb01Z.isChecked())
                    plot_statistical_level(niveles_Z.get('l10', {}), xdata, color_map['l10'], 'Z L10', self.cb10Z.isChecked())
                    plot_statistical_level(niveles_Z.get('l50', {}), xdata, color_map['l50'], 'Z L50', self.cb50Z.isChecked())
                    plot_statistical_level(niveles_Z.get('l90', {}), xdata, color_map['l90'], 'Z L90', self.cb90Z.isChecked())
                    plot_statistical_level(niveles_Z.get('l99', {}), xdata, color_map['l99'], 'Z L99', self.cb99Z.isChecked())
                    
                    # C Statistical - Gráficos temporales
                    plot_statistical_level(niveles_C.get('leq', {}), xdata, color_map['leq'], 'C Leq', self.cbEqC.isChecked())
                    plot_statistical_level(niveles_C.get('l01', {}), xdata, color_map['l01'], 'C L01', self.cb01C.isChecked())
                    plot_statistical_level(niveles_C.get('l10', {}), xdata, color_map['l10'], 'C L10', self.cb10C.isChecked())
                    plot_statistical_level(niveles_C.get('l50', {}), xdata, color_map['l50'], 'C L50', self.cb50C.isChecked())
                    plot_statistical_level(niveles_C.get('l90', {}), xdata, color_map['l90'], 'C L90', self.cb90C.isChecked())
                    plot_statistical_level(niveles_C.get('l99', {}), xdata, color_map['l99'], 'C L99', self.cb99C.isChecked())
                    
                    # A Statistical - Gráficos temporales
                    plot_statistical_level(niveles_A.get('leq', {}), xdata, color_map['leq'], 'A Leq', self.cbEqA.isChecked())
                    plot_statistical_level(niveles_A.get('l01', {}), xdata, color_map['l01'], 'A L01', self.cb01A.isChecked())
                    plot_statistical_level(niveles_A.get('l10', {}), xdata, color_map['l10'], 'A L10', self.cb10A.isChecked())
                    plot_statistical_level(niveles_A.get('l50', {}), xdata, color_map['l50'], 'A L50', self.cb50A.isChecked())
                    plot_statistical_level(niveles_A.get('l90', {}), xdata, color_map['l90'], 'A L90', self.cb90A.isChecked())
                    plot_statistical_level(niveles_A.get('l99', {}), xdata, color_map['l99'], 'A L99', self.cb99A.isChecked())
                    
                    # Ajustar rango X para mostrar los últimos 10 segundos
                    if len(xdata) > 0:
                        self.waveform1.setXRange(max(0, xdata[-1]-10), xdata[-1])
                    
                    print(f"DEBUG: Niveles actualizados - Ejemplo Z Slow último: {niveles_Z.get('slow', [0])[-1] if len(niveles_Z.get('slow', [])) > 0 else 'No data'} dB")
                    print(f"DEBUG: Estadísticos Z Leq último: {niveles_Z.get('leq', [0])[-1] if len(niveles_Z.get('leq', [])) > 0 else 'No data'} dB")
                    
                    # Forzar replot después de añadir todo
                    self.waveform1.replot()
                    print("DEBUG: replot forzado en nivel")
                    
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
            #self.var_logModeXTiempo = config['tiempo']['logModeX']
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
            self.var_eje2Visible = config['espectro']['eje2']
            self.var_etiquetaXEspectro = config['espectro']['etiquetaX']
            self.var_etiquetaYEspectro = config['espectro']['etiquetaY']
            self.var_tipoGraficoEspectro = config['espectro']['tipoGrafico']
            self.var_valoresOctavas = config['espectro']['valoresOcta']
            
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
