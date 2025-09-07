# configuracionWin.py

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QGridLayout, QLabel, QLineEdit, QCheckBox, QPushButton, 
                             QComboBox, QFrame, QColorDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from utils import norm
from PyQt5.QtGui import QIcon


class ConfiguracionWin(QMainWindow):
    # Señal para comunicar cambios a la ventana principal
    configuracionCambiada = pyqtSignal(dict)
    
    def __init__(self, vista_principal, controller):
        super().__init__()
        self.vista = vista_principal  # Referencia a la vista principal
        
        self.vController = controller  # Referencia al controlador principal
        self.fs_actual = self.vController.frecuencia_muestreo_actual
        # Obtener dimensiones de la pantalla desde la vista principal
        self.anchoX = self.vista.anchoX
        self.altoY = self.vista.altoY
        
        self.setWindowTitle("Configuración de gráficos")
        self.setWindowIcon(QIcon('img/LogoCINTRA1.png'))
        self.setGeometry(norm(self.anchoX, self.altoY, 0.2, 0.2, 0.6, 0.6))
        
        self.initUI()
        
    def initUI(self):
        # Crear widget central
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        
        # Layout principal
        self.confWinLayout = QVBoxLayout(centralWidget)
        self.confinfoLayout = QHBoxLayout()
        self.confBotonesLayout = QHBoxLayout()
        self.confWinLayout.addLayout(self.confinfoLayout)
        self.confWinLayout.addLayout(self.confBotonesLayout)
        
        # Crear grupos de configuración
        self.crearGrupoTiempo()
        self.crearGrupoEspectro()
        self.crearGrupoNivel()
        
        # Botones
        self.btnConfigAplicar = QPushButton("Aplicar")
        self.btnConfigAplicar.clicked.connect(self.aplicarConfiguracion)
        self.btnConfigCancelar = QPushButton("Cancelar")
        self.btnConfigCancelar.clicked.connect(self.close)
        
        # Agregar grupos al layout
        self.confinfoLayout.addWidget(self.ejesGroupTiempo)
        self.confinfoLayout.addWidget(self.ejesGroupEspectro)
        self.confinfoLayout.addWidget(self.ejesGroupNivel)
        self.confBotonesLayout.addWidget(self.btnConfigCancelar)
        self.confBotonesLayout.addWidget(self.btnConfigAplicar)
        
        # Stretch
        self.confWinLayout.addStretch()
        
        # Aplicar estilos
        self.aplicarEstilos()
        
        # Cargar valores actuales
        self.cargarValoresActuales()
    
    def crearGrupoTiempo(self):
        """Crea el grupo de configuración para gráficos de tiempo"""
        self.ejesGroupTiempo = QGroupBox("Configuración de ejes tiempo")
        ejesLayoutTiempo = QVBoxLayout()
        
        # Escala
        escalaLayoutTiempo = QHBoxLayout()
        escalaLayoutTiempo.addWidget(QLabel("Escala:"))
        #self.cbEscalaXTiempo = QCheckBox("Eje X Logarítmico")
        self.cbEscalaYTiempo = QCheckBox("Eje Y logarítmico")
        #escalaLayoutTiempo.addWidget(self.cbEscalaXTiempo)
        escalaLayoutTiempo.addWidget(self.cbEscalaYTiempo)
        escalaLayoutTiempo.addStretch()
        ejesLayoutTiempo.addLayout(escalaLayoutTiempo)
        
        # Límites X
        ejeXGroupTiempo = QGroupBox("Límites del eje X")
        ejeXLayoutTiempo = QGridLayout()
        ejeXLayoutTiempo.addWidget(QLabel("Mínimo:"), 0, 0)
        self.txtXMinTiempo = QLineEdit()
        self.txtXMinTiempo.setMaximumWidth(100)
        ejeXLayoutTiempo.addWidget(self.txtXMinTiempo, 0, 1)
        ejeXLayoutTiempo.addWidget(QLabel("[s]"), 0, 2)
        ejeXLayoutTiempo.addWidget(QLabel("Máximo:"), 0, 3)
        ejeXLayoutTiempo.addWidget(QLabel("[s]"), 0, 5)
        self.txtXMaxTiempo = QLineEdit()
        self.txtXMaxTiempo.setMaximumWidth(100)
        ejeXLayoutTiempo.addWidget(self.txtXMaxTiempo, 0, 4)
        ejeXGroupTiempo.setLayout(ejeXLayoutTiempo)
        ejesLayoutTiempo.addWidget(ejeXGroupTiempo)
        
        # Límites Y
        ejeYGroupTiempo = QGroupBox("Límites del eje Y")
        ejeYLayoutTiempo = QGridLayout()
        ejeYLayoutTiempo.addWidget(QLabel("Mínimo:"), 0, 0)
        self.txtYMinTiempo = QLineEdit()
        self.txtYMinTiempo.setMaximumWidth(100)
        ejeYLayoutTiempo.addWidget(self.txtYMinTiempo, 0, 1)
        ejeYLayoutTiempo.addWidget(QLabel("[dB]"), 0, 2)
        ejeYLayoutTiempo.addWidget(QLabel("Máximo:"), 0, 3)
        ejeYLayoutTiempo.addWidget(QLabel("[dB]"), 0, 5)
        self.txtYMaxTiempo = QLineEdit()
        self.txtYMaxTiempo.setMaximumWidth(100)
        ejeYLayoutTiempo.addWidget(self.txtYMaxTiempo, 0, 4)
        ejeYGroupTiempo.setLayout(ejeYLayoutTiempo)
        ejesLayoutTiempo.addWidget(ejeYGroupTiempo)
        
        # Etiquetas
        etiquetasGroupTiempo = QGroupBox("Etiquetas de ejes")
        etiquetasLayoutTiempo = QGridLayout()
        etiquetasLayoutTiempo.addWidget(QLabel("Eje X:"), 0, 0)
        self.txtEtiquetaXTiempo = QLineEdit()
        etiquetasLayoutTiempo.addWidget(self.txtEtiquetaXTiempo, 0, 1)
        etiquetasLayoutTiempo.addWidget(QLabel("Eje Y:"), 1, 0)
        self.txtEtiquetaYTiempo = QLineEdit()
        etiquetasLayoutTiempo.addWidget(self.txtEtiquetaYTiempo, 1, 1)
        etiquetasGroupTiempo.setLayout(etiquetasLayoutTiempo)
        ejesLayoutTiempo.addWidget(etiquetasGroupTiempo)
        
        # Color
        colorGroupTiempo = QGroupBox("Color de línea")
        colorLayoutTiempo = QHBoxLayout()
        self.colorFrameTiempo = QFrame()
        self.colorFrameTiempo.setFixedSize(30, 20)
        self.btnColorTiempo = QPushButton("Seleccionar color")
        self.btnColorTiempo.clicked.connect(lambda: self.seleccionarColor(self.colorFrameTiempo, "tiempo"))
        colorLayoutTiempo.addWidget(QLabel("Color:"))
        colorLayoutTiempo.addWidget(self.colorFrameTiempo)
        colorLayoutTiempo.addWidget(self.btnColorTiempo)
        colorLayoutTiempo.addStretch()
        colorGroupTiempo.setLayout(colorLayoutTiempo)
        ejesLayoutTiempo.addWidget(colorGroupTiempo)
        
        # Tipo de línea
        tipoLineaGroupTiempo = QGroupBox("Tipo de línea")
        tipoLineaLayoutTiempo = QHBoxLayout()
        tipoLineaLayoutTiempo.addWidget(QLabel("Estilo:"))
        self.cmbTipoLineaTiempo = QComboBox()
        self.cmbTipoLineaTiempo.addItems(["Sólida", "Punteada", "Rayada"])
        tipoLineaLayoutTiempo.addWidget(self.cmbTipoLineaTiempo)
        tipoLineaLayoutTiempo.addStretch()
        tipoLineaGroupTiempo.setLayout(tipoLineaLayoutTiempo)
        ejesLayoutTiempo.addWidget(tipoLineaGroupTiempo)
        
        self.ejesGroupTiempo.setLayout(ejesLayoutTiempo)
    
    def crearGrupoEspectro(self):
        """Crea el grupo de configuración para gráficos de espectro"""
        self.ejesGroupEspectro = QGroupBox("Configuración de ejes espectro")
        ejesLayoutEspectro = QVBoxLayout()
        
        # Escala
        escalaLayoutEspectro = QHBoxLayout()
        escalaLayoutEspectro.addWidget(QLabel("Escala:"))
        self.cbEscalaXEspectro = QCheckBox("Eje X logarítmico")
        self.cbEscalaYEspectro = QCheckBox("Eje Y logarítmico")
        escalaLayoutEspectro.addWidget(self.cbEscalaXEspectro)
        escalaLayoutEspectro.addWidget(self.cbEscalaYEspectro)
        escalaLayoutEspectro.addStretch()
        ejesLayoutEspectro.addLayout(escalaLayoutEspectro)
        
        # Límites X
        ejeXGroupEspectro = QGroupBox("Límites del eje X")
        ejeXLayoutEspectro = QGridLayout()
        ejeXLayoutEspectro.addWidget(QLabel("Mínimo:"), 0, 0)
        self.txtXMinEspectro = QLineEdit()
        self.txtXMinEspectro.setMaximumWidth(100)
        ejeXLayoutEspectro.addWidget(self.txtXMinEspectro, 0, 1)
        ejeXLayoutEspectro.addWidget(QLabel("[Hz]"), 0, 2)
        ejeXLayoutEspectro.addWidget(QLabel("Máximo:"), 0, 3)
        ejeXLayoutEspectro.addWidget(QLabel("[Hz]"), 0, 5)
        self.txtXMaxEspectro = QLineEdit()
        self.txtXMaxEspectro.setMaximumWidth(100)
        ejeXLayoutEspectro.addWidget(self.txtXMaxEspectro, 0, 4)
        ejeXGroupEspectro.setLayout(ejeXLayoutEspectro)
        ejesLayoutEspectro.addWidget(ejeXGroupEspectro)
        self.txtXMaxEspectro.editingFinished.connect(self.validarLimiteXMaxEspectro)
        
        # Límites Y
        ejeYGroupEspectro = QGroupBox("Límites del eje Y")
        ejeYLayoutEspectro = QGridLayout()
        ejeYLayoutEspectro.addWidget(QLabel("Mínimo:"), 0, 0)
        self.txtYMinEspectro = QLineEdit()
        self.txtYMinEspectro.setMaximumWidth(100)
        ejeYLayoutEspectro.addWidget(self.txtYMinEspectro, 0, 1)
        ejeYLayoutEspectro.addWidget(QLabel("[dB]"), 0, 2)
        ejeYLayoutEspectro.addWidget(QLabel("Máximo:"), 0, 3)
        ejeYLayoutEspectro.addWidget(QLabel("[dB]"), 0, 5)
        self.txtYMaxEspectro = QLineEdit()
        self.txtYMaxEspectro.setMaximumWidth(100)
        ejeYLayoutEspectro.addWidget(self.txtYMaxEspectro, 0, 4)
        ejeYGroupEspectro.setLayout(ejeYLayoutEspectro)
        ejesLayoutEspectro.addWidget(ejeYGroupEspectro)
        
        # Etiquetas
        etiquetasGroupEspectro = QGroupBox("Etiquetas de ejes")
        etiquetasLayoutEspectro = QGridLayout()
        etiquetasLayoutEspectro.addWidget(QLabel("Eje X:"), 0, 0)
        self.txtEtiquetaXEspectro = QLineEdit()
        etiquetasLayoutEspectro.addWidget(self.txtEtiquetaXEspectro, 0, 1)
        etiquetasLayoutEspectro.addWidget(QLabel("Eje Y:"), 1, 0)
        self.txtEtiquetaYEspectro = QLineEdit()
        etiquetasLayoutEspectro.addWidget(self.txtEtiquetaYEspectro, 1, 1)
        etiquetasGroupEspectro.setLayout(etiquetasLayoutEspectro)
        ejesLayoutEspectro.addWidget(etiquetasGroupEspectro)
        
        # Color
        colorGroupEspectro = QGroupBox("Color de línea")
        colorLayoutEspectro = QHBoxLayout()
        self.colorFrameEspectro = QFrame()
        self.colorFrameEspectro.setFixedSize(30, 20)
        self.btnColorEspectro = QPushButton("Seleccionar color")
        self.btnColorEspectro.clicked.connect(lambda: self.seleccionarColor(self.colorFrameEspectro, "espectro"))
        colorLayoutEspectro.addWidget(QLabel("Color:"))
        colorLayoutEspectro.addWidget(self.colorFrameEspectro)
        colorLayoutEspectro.addWidget(self.btnColorEspectro)
        colorLayoutEspectro.addStretch()
        colorGroupEspectro.setLayout(colorLayoutEspectro)
        ejesLayoutEspectro.addWidget(colorGroupEspectro)
        
        # Tipo de gráfico
        tipoGraficoGroupEspectro = QGroupBox("Tipo de gráfico")
        tipoGraficoLayoutEspectro = QHBoxLayout()
        tipoGraficoLayoutEspectro.addWidget(QLabel("Estilo:"))
        self.cmbTipoGraficoEspectro = QComboBox()
        self.cmbTipoGraficoEspectro.addItems(["Línea", "Barras-octavas", "Barras-tercios"])
        tipoGraficoLayoutEspectro.addWidget(self.cmbTipoGraficoEspectro)
        tipoGraficoLayoutEspectro.addStretch()
        tipoGraficoGroupEspectro.setLayout(tipoGraficoLayoutEspectro)
        ejesLayoutEspectro.addWidget(tipoGraficoGroupEspectro)
        
        self.ejesGroupEspectro.setLayout(ejesLayoutEspectro)
    
    def crearGrupoNivel(self):
        """Crea el grupo de configuración para gráficos de nivel"""
        self.ejesGroupNivel = QGroupBox("Configuración de ejes nivel")
        ejesLayoutNivel = QVBoxLayout()
        
        # Escala
        escalaLayoutNivel = QHBoxLayout()
        escalaLayoutNivel.addWidget(QLabel("Escala:"))
        self.cbEscalaYNivel = QCheckBox("Eje Y logarítmico")
        escalaLayoutNivel.addWidget(self.cbEscalaYNivel)
        escalaLayoutNivel.addStretch()
        ejesLayoutNivel.addLayout(escalaLayoutNivel)
        
        # Límites X
        ejeXGroupNivel = QGroupBox("Límites del eje X")
        ejeXLayoutNivel = QGridLayout()
        ejeXLayoutNivel.addWidget(QLabel("Mínimo:"), 0, 0)
        self.txtXMinNivel = QLineEdit()
        self.txtXMinNivel.setMaximumWidth(100)
        ejeXLayoutNivel.addWidget(self.txtXMinNivel, 0, 1)
        ejeXLayoutNivel.addWidget(QLabel("[s]"), 0, 2)
        ejeXLayoutNivel.addWidget(QLabel("Máximo:"), 0, 3)
        ejeXLayoutNivel.addWidget(QLabel("[s]"), 0, 5)
        self.txtXMaxNivel = QLineEdit()
        self.txtXMaxNivel.setMaximumWidth(100)
        ejeXLayoutNivel.addWidget(self.txtXMaxNivel, 0, 4)
        ejeXGroupNivel.setLayout(ejeXLayoutNivel)
        ejesLayoutNivel.addWidget(ejeXGroupNivel)
        
        # Límites Y
        ejeYGroupNivel = QGroupBox("Límites del eje Y")
        ejeYLayoutNivel = QGridLayout()
        ejeYLayoutNivel.addWidget(QLabel("Mínimo:"), 0, 0)
        self.txtYMinNivel = QLineEdit()
        self.txtYMinNivel.setMaximumWidth(100)
        ejeYLayoutNivel.addWidget(self.txtYMinNivel, 0, 1)
        ejeYLayoutNivel.addWidget(QLabel("[dB]"), 0, 2)
        ejeYLayoutNivel.addWidget(QLabel("Máximo:"), 0, 3)
        ejeYLayoutNivel.addWidget(QLabel("[dB]"), 0, 4)
        self.txtYMaxNivel = QLineEdit()
        self.txtYMaxNivel.setMaximumWidth(100)
        ejeYLayoutNivel.addWidget(self.txtYMaxNivel, 0, 3)
        ejeYGroupNivel.setLayout(ejeYLayoutNivel)
        ejesLayoutNivel.addWidget(ejeYGroupNivel)
        
        # Etiquetas
        etiquetasGroupNivel = QGroupBox("Etiquetas de ejes")
        etiquetasLayoutNivel = QGridLayout()
        etiquetasLayoutNivel.addWidget(QLabel("Eje X:"), 0, 0)
        self.txtEtiquetaXNivel = QLineEdit()
        etiquetasLayoutNivel.addWidget(self.txtEtiquetaXNivel, 0, 1)
        etiquetasLayoutNivel.addWidget(QLabel("Eje Y:"), 1, 0)
        self.txtEtiquetaYNivel = QLineEdit()
        etiquetasLayoutNivel.addWidget(self.txtEtiquetaYNivel, 1, 1)
        etiquetasGroupNivel.setLayout(etiquetasLayoutNivel)
        ejesLayoutNivel.addWidget(etiquetasGroupNivel)
        
        # Color
        colorGroupNivel = QGroupBox("Color de línea")
        colorLayoutNivel = QHBoxLayout()
        self.colorFrameNivel = QFrame()
        self.colorFrameNivel.setFixedSize(30, 20)
        self.btnColorNivel = QPushButton("Seleccionar color")
        self.btnColorNivel.clicked.connect(lambda: self.seleccionarColor(self.colorFrameNivel, "nivel"))
        colorLayoutNivel.addWidget(QLabel("Color:"))
        colorLayoutNivel.addWidget(self.colorFrameNivel)
        colorLayoutNivel.addWidget(self.btnColorNivel)
        colorLayoutNivel.addStretch()
        colorGroupNivel.setLayout(colorLayoutNivel)
        ejesLayoutNivel.addWidget(colorGroupNivel)
        
        # Tipo de línea
        tipoLineaGroupNivel = QGroupBox("Tipo de línea")
        tipoLineaLayoutNivel = QHBoxLayout()
        tipoLineaLayoutNivel.addWidget(QLabel("Estilo:"))
        self.cmbTipoLineaNivel = QComboBox()
        self.cmbTipoLineaNivel.addItems(["Sólida", "Punteada", "Rayada"])
        tipoLineaLayoutNivel.addWidget(self.cmbTipoLineaNivel)
        tipoLineaLayoutNivel.addStretch()
        tipoLineaGroupNivel.setLayout(tipoLineaLayoutNivel)
        ejesLayoutNivel.addWidget(tipoLineaGroupNivel)
        
        self.ejesGroupNivel.setLayout(ejesLayoutNivel)
    
    def cargarValoresActuales(self):
        """Carga los valores actuales desde la vista principal"""
        # Valores de tiempo
        #self.cbEscalaXTiempo.setChecked(getattr(self.vista, 'var_logModeXTiempo', False))
        self.cbEscalaYTiempo.setChecked(getattr(self.vista, 'var_logModeYTiempo', False))
        self.txtXMinTiempo.setText(str(getattr(self.vista, 'var_xMinTiempo', 0)))
        self.txtXMaxTiempo.setText(str(getattr(self.vista, 'var_xMaxTiempo', 1024)))
        self.txtYMinTiempo.setText(str(getattr(self.vista, 'var_yMinTiempo', -1)))
        self.txtYMaxTiempo.setText(str(getattr(self.vista, 'var_yMaxTiempo', 1)))
        self.txtEtiquetaXTiempo.setText(getattr(self.vista, 'var_etiquetaXTiempo', 'Tiempo'))
        self.txtEtiquetaYTiempo.setText(getattr(self.vista, 'var_etiquetaYTiempo', 'Amplitud Normalizada'))
        
        # Valores de espectro
        self.cbEscalaXEspectro.setChecked(getattr(self.vista, 'var_logModeXEspectro', False))
        self.cbEscalaYEspectro.setChecked(getattr(self.vista, 'var_logModeYEspectro', False))
        self.txtXMinEspectro.setText(str(getattr(self.vista, 'var_xMinEspectro', 0)))
        self.txtXMaxEspectro.setText(str(getattr(self.vista, 'var_xMaxEspectro', 1024)))
        self.txtYMinEspectro.setText(str(getattr(self.vista, 'var_yMinEspectro', -1)))
        self.txtYMaxEspectro.setText(str(getattr(self.vista, 'var_yMaxEspectro', 1)))
        self.txtEtiquetaXEspectro.setText(getattr(self.vista, 'var_etiquetaXEspectro', 'Tiempo'))
        self.txtEtiquetaYEspectro.setText(getattr(self.vista, 'var_etiquetaYEspectro', 'Amplitud Normalizada'))
        
        # Valores de nivel
        self.cbEscalaYNivel.setChecked(getattr(self.vista, 'var_logModeYNivel', False))
        self.txtXMinNivel.setText(str(getattr(self.vista, 'var_xMinNivel', 0)))
        self.txtXMaxNivel.setText(str(getattr(self.vista, 'var_xMaxNivel', 1024)))
        self.txtYMinNivel.setText(str(getattr(self.vista, 'var_yMinNivel', -1)))
        self.txtYMaxNivel.setText(str(getattr(self.vista, 'var_yMaxNivel', 1)))
        self.txtEtiquetaXNivel.setText(getattr(self.vista, 'var_etiquetaXNivel', 'Tiempo'))
        self.txtEtiquetaYNivel.setText(getattr(self.vista, 'var_etiquetaYNivel', 'Amplitud Normalizada'))
        
        # Cargar colores
        color_tiempo = getattr(self.vista, 'default_color_tiempo', "#006400")
        if hasattr(self.vista, 'colorTiempo'):
            color_tiempo = self.vista.get_color_str(self.vista.colorTiempo)
        self.colorFrameTiempo.setStyleSheet(f"background-color: {color_tiempo}; border: 1px solid black;")
        
        color_espectro = getattr(self.vista, 'default_color_espectro', "#1E90FF")
        if hasattr(self.vista, 'colorEspectro'):
            color_espectro = self.vista.get_color_str(self.vista.colorEspectro)
        self.colorFrameEspectro.setStyleSheet(f"background-color: {color_espectro}; border: 1px solid black;")
        
        color_nivel = getattr(self.vista, 'default_color_nivel', "#8A2BE2")
        if hasattr(self.vista, 'colorNivel'):
            color_nivel = self.vista.get_color_str(self.vista.colorNivel)
        self.colorFrameNivel.setStyleSheet(f"background-color: {color_nivel}; border: 1px solid black;")
        
        # Cargar tipos de línea/gráfico
        if hasattr(self.vista, 'var_tipoLineaTiempo') and self.vista.var_tipoLineaTiempo:
            idx = self.cmbTipoLineaTiempo.findText(self.vista.var_tipoLineaTiempo)
            if idx >= 0:
                self.cmbTipoLineaTiempo.setCurrentIndex(idx)
                
        if hasattr(self.vista, 'var_tipoGraficoEspectro') and self.vista.var_tipoGraficoEspectro:
            idx = self.cmbTipoGraficoEspectro.findText(self.vista.var_tipoGraficoEspectro)
            if idx >= 0:
                self.cmbTipoGraficoEspectro.setCurrentIndex(idx)
                
        if hasattr(self.vista, 'var_tipoLineaNivel') and self.vista.var_tipoLineaNivel:
            idx = self.cmbTipoLineaNivel.findText(self.vista.var_tipoLineaNivel)
            if idx >= 0:
                self.cmbTipoLineaNivel.setCurrentIndex(idx)
    
    def seleccionarColor(self, colorFrame, tipoGrafico):
        """Abre el diálogo de selección de color"""
        color = QColorDialog.getColor()
        if color.isValid():
            colorFrame.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
            # Guardar el color en la vista principal
            if tipoGrafico == "tiempo":
                self.vista.colorTiempo = color
            elif tipoGrafico == "espectro":
                self.vista.colorEspectro = color
            elif tipoGrafico == "nivel":
                self.vista.colorNivel = color
    
    def aplicarConfiguracion(self):
        """Aplica la configuración y la envía a la vista principal"""
        try:
            # Crear diccionario con toda la configuración
            config = {
                'tiempo': {
                    #'logModeX': self.cbEscalaXTiempo.isChecked(),
                    'logModeY': self.cbEscalaYTiempo.isChecked(),
                    'xMin': float(self.txtXMinTiempo.text()),
                    'xMax': float(self.txtXMaxTiempo.text()),
                    'yMin': float(self.txtYMinTiempo.text()),
                    'yMax': float(self.txtYMaxTiempo.text()),
                    'etiquetaX': self.txtEtiquetaXTiempo.text(),
                    'etiquetaY': self.txtEtiquetaYTiempo.text(),
                    'tipoLinea': self.cmbTipoLineaTiempo.currentText()
                },
                'espectro': {
                    'logModeX': self.cbEscalaXEspectro.isChecked(),
                    'logModeY': self.cbEscalaYEspectro.isChecked(),
                    'xMin': float(self.txtXMinEspectro.text()),
                    'xMax': float(self.txtXMaxEspectro.text()),
                    'yMin': float(self.txtYMinEspectro.text()),
                    'yMax': float(self.txtYMaxEspectro.text()),
                    'etiquetaX': self.txtEtiquetaXEspectro.text(),
                    'etiquetaY': self.txtEtiquetaYEspectro.text(),
                    'tipoGrafico': self.cmbTipoGraficoEspectro.currentText()
                },
                'nivel': {
                    'logModeY': self.cbEscalaYNivel.isChecked(),
                    'xMin': float(self.txtXMinNivel.text()),
                    'xMax': float(self.txtXMaxNivel.text()),
                    'yMin': float(self.txtYMinNivel.text()),
                    'yMax': float(self.txtYMaxNivel.text()),
                    'etiquetaX': self.txtEtiquetaXNivel.text(),
                    'etiquetaY': self.txtEtiquetaYNivel.text(),
                    'tipoLinea': self.cmbTipoLineaNivel.currentText()
                }
            }
            
            # Aplicar configuración directamente a la vista principal
            self.vista.aplicarConfiguracionExterna(config)
            
            # Cerrar la ventana
            self.close()
            
        except ValueError:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "Por favor ingrese valores numéricos válidos")
        except Exception as e:
            print(f"Error al aplicar configuración: {e}")
    
    def aplicarEstilos(self):
        """Aplica estilos a los botones y combos"""
        for boton in [self.btnColorTiempo, self.btnColorEspectro, self.btnColorNivel, 
                     self.btnConfigAplicar, self.btnConfigCancelar]:
            boton.setProperty("class", "ventanasSec")

        for combo in [self.cmbTipoLineaTiempo, self.cmbTipoGraficoEspectro, self.cmbTipoLineaNivel]:
            combo.setProperty("class", "ventanasSec")
     
    def validarLimiteXMaxEspectro(self):
        try:
            valor = float(self.txtXMaxEspectro.text())
            fs_actual = self.vController.get_frecuencia_muestreo_actual()  # o donde sea que lo tengas

            if valor > fs_actual / 2:
                self.txtXMaxEspectro.setText(str(fs_actual / 2))
                QMessageBox.information(self, "Límite aplicado", "El valor ha sido ajustado a Fs/2.")

        except ValueError:
            # Si no es un número válido, ignoramos
            pass
            
    def closeEvent(self, event):
        self.vController.ventanas_abiertas["configuracion"] = None
        event.accept()
            
    @pyqtSlot(int)
    def actualizarLimiteXMaxEspectro(self, frecuencia_muestreo):
        limite_max = frecuencia_muestreo / 2
        try:
            valor_actual = float(self.txtXMaxEspectro.text())
            if valor_actual > limite_max:
                self.txtXMaxEspectro.setText(str(limite_max))
        except ValueError:
            self.txtXMaxEspectro.setText(str(limite_max))