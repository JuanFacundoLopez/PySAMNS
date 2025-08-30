# Importo librerias
from ventanas.generadorWin import GeneradorWin
from ventanas.configDispWin import ConfigDispWin

from PyQt5.QtWidgets import (QMainWindow, QApplication, QHBoxLayout, QVBoxLayout, QPushButton,
                             QLabel, QLineEdit, QGroupBox, QRadioButton, QWidget, QGridLayout, QMessageBox, QFileDialog)

from PyQt5.QtGui import  QPainter

# Imports para QChart (solo para la ventana de calibración)
from PyQt5.QtChart import QChart, QChartView
from PyQt5.QtCore import Qt
from utils import norm
import os



class CalibracionWin(QMainWindow):
    def __init__(self, vController):
        super().__init__()
        self.setWindowTitle("Calibración")
        screen = QApplication.primaryScreen().size()
        self.anchoX = screen.width()
        self.altoY = screen.height()
        self.setGeometry(norm(self.anchoX, self.altoY,0.35, 0.35, 0.3, 0.3))

        with open("estilos.qss", "r", encoding='utf-8') as f:
            QApplication.instance().setStyleSheet(f.read())
          
        self.vController = vController

        # Widget central y layout principal
        centralWidget = QWidget()
        mainLayout = QVBoxLayout(centralWidget)

        # Layouts
        tipoCalLayoutHori = QHBoxLayout()
        tipoCalLayoutVer = QVBoxLayout()
        confLayoutVer = QVBoxLayout()
        confLayoutVer.addStretch()
        gridHardLayout = QGridLayout()
        self.valorRefLayout = QHBoxLayout() # Make it a class attribute for visibility control
        botonesLayout = QHBoxLayout()

        # --- Tipo de Calibracion ---
        self.lblTipoCal = QLabel("Tipo de Calibración:")
        tipoCalLayoutHori.addWidget(self.lblTipoCal)
        self.radioBtnRelativa = QRadioButton("Calibración con fuente de referencia externa")
        self.radioBtnAutomatica = QRadioButton("Calibración relativa a fondo de escala")
        self.radioBtnExterna = QRadioButton("Calibración con fuente de referencia interna")
        tipoCalLayoutVer.addWidget(self.radioBtnRelativa)
        tipoCalLayoutVer.addWidget(self.radioBtnAutomatica)
        tipoCalLayoutVer.addWidget(self.radioBtnExterna)
        tipoCalLayoutHori.addLayout(tipoCalLayoutVer)
        tipoCalLayoutHori.addStretch()

        # --- Dispositivo ---
        self.lblDispEnt = QLabel("Dispositivo de entrada: ")
        gridHardLayout.addWidget(self.lblDispEnt,0,0)
        self.lblConfDispEnt = QLabel("")
        gridHardLayout.addWidget(self.lblConfDispEnt,0,1)
        self.lblDispSal = QLabel("Dispositivo de salida: ")
        gridHardLayout.addWidget(self.lblDispSal,1,0)
        self.lblConfDispSal = QLabel("")
        gridHardLayout.addWidget(self.lblConfDispSal,1,1)
        
        
        self.btnConfHard = QPushButton("Configurar dispositivo")
        confLayoutVer.addWidget(self.btnConfHard, alignment=Qt.AlignHCenter)
        confLayoutVer.addStretch()
        self.btnConfHard.clicked.connect(self.configuracionDispositivo)
        gridHardLayout.addLayout(confLayoutVer, 0, 2, 2, 1)

        # --- Calibracion Relativa ---
        self.lblValRef = QLabel("Valor de deferencia:")
        self.valorRefLayout.addWidget(self.lblValRef)
        self.txtValorRef = QLineEdit("")
        self.valorRefLayout.addWidget(self.txtValorRef)
        self.lblUnidadRef = QLabel("[dB]")
        self.valorRefLayout.addWidget(self.lblUnidadRef)

        # --- Calibracion Externa ---
        self.calExternaGroup = QGroupBox("Parámetros de calibración externa")
        layoutExterna = QGridLayout(self.calExternaGroup)
        self.btnImportSig = QPushButton("Importar archivo de referencia (.wav)")
        self.btnImportSig.clicked.connect(self.importarSenalCalibracion)
        self.lblRutaArchivoCal = QLabel("Ningún archivo seleccionado.")
        self.lblRutaArchivoCal.setWordWrap(True)
        self.lblValRefExterna = QLabel("Nivel de referencia (dBSPL):")
        self.txtValorRefExterna = QLineEdit("94.0")
        self.btnReproducirCal = QPushButton("Reproducir señal de referencia")
        # self.btnReproducirCal.clicked.connect(self.vController.reproducir_audio_calibracion)
        layoutExterna.addWidget(self.btnImportSig, 0, 0, 1, 2)
        layoutExterna.addWidget(self.lblRutaArchivoCal, 1, 0, 1, 2)
        layoutExterna.addWidget(self.lblValRefExterna, 2, 0)
        layoutExterna.addWidget(self.txtValorRefExterna, 2, 1)
        layoutExterna.addWidget(self.btnReproducirCal, 3, 0, 1, 2)

        # --- Grafico ---
        self.chart2 = QChart()
        self.chart2.setTheme(QChart.ChartThemeDark)
        self.winGraph2 = QChartView(self.chart2)
        self.winGraph2.setRenderHint(QPainter.Antialiasing)
        # ... (chart setup as before)

        # --- Botones ---
        self.btnAceptar = QPushButton("Aceptar")
        self.btnCalibrar = QPushButton("Calibrar")
        self.calibracion_realizada = False
        self.btnGenerador = QPushButton("Generador de señales")
        self.btnGenerador.clicked.connect(self.generadorWin)
        self.btnCancel = QPushButton("Cancelar")
        self.btnCancel.clicked.connect(self.close)
        botonesLayout.addWidget(self.btnAceptar)
        botonesLayout.addWidget(self.btnCalibrar)
        botonesLayout.addWidget(self.btnGenerador)
        botonesLayout.addWidget(self.btnCancel)

        # --- Layout Principal ---
        mainLayout.addLayout(tipoCalLayoutHori)
        mainLayout.addLayout(gridHardLayout)
        mainLayout.addLayout(self.valorRefLayout)
        mainLayout.addWidget(self.calExternaGroup)
        mainLayout.addWidget(self.winGraph2)
        mainLayout.addLayout(botonesLayout)

        # --- Conexiones y Estado Inicial ---
        self.radioBtnRelativa.toggled.connect(self.actualizar_vista_calibracion)
        self.radioBtnExterna.toggled.connect(self.actualizar_vista_calibracion)
        self.btnCalibrar.clicked.connect(self.iniciarCalibracion)
        self.radioBtnRelativa.setChecked(True)
        self.actualizar_vista_calibracion() # Set initial state
        self.actualizarNombreDispositivos()
        
        self.setCentralWidget(centralWidget)
      
    
    def iniciarCalibracion(self):
        """Router para llamar al método de calibración correcto según la selección."""
        exito = False
        if self.radioBtnRelativa.isChecked():
            # Llama al método de calibración relativa existente en el controlador
            exito=self.vController.calFuenteCalibracionExterna()
        elif self.radioBtnAutomatica.isChecked():
            # Llama al método de calibración automática existente en el controlador
            exito=self.vController.calRelativaAFondoDeEscala()
        elif self.radioBtnExterna.isChecked():
            # Llama al nuevo método de calibración externa en el controlador
            exito=self.vController.calFuenteReferenciaInterna()
        
        if exito and not self.calibracion_realizada:
            self.btnCalibrar.setText("Repetir calibración")
            self.calibracion_realizada = True          
    
    def actualizar_vista_calibracion(self):
        relativa_checked = self.radioBtnRelativa.isChecked()
        externa_checked = self.radioBtnExterna.isChecked()

        self.lblValRef.setVisible(relativa_checked)
        self.txtValorRef.setVisible(relativa_checked)
        self.lblUnidadRef.setVisible(relativa_checked)
        self.calExternaGroup.setVisible(externa_checked)
        self.winGraph2.setVisible(externa_checked) 
        
    def actualizarNombreDispositivos(self):
        """Actualiza los labels con los nombres de los dispositivos de entrada y salida actuales"""
        try:
            # Verificar si los labels existen
            if not hasattr(self, 'lblConfDispEnt') or not hasattr(self, 'lblConfDispSal'):
                print("Labels de configuración no existen - ventana de calibración no abierta")
                return

            # --------------------
            # Dispositivo de entrada
            # --------------------
            disp_ent = self.vController.cModel.getDispositivoActual()
            if disp_ent is not None:
                nombres_ent = self.vController.cModel.getDispositivosEntrada('nombre')
                indices_ent = self.vController.cModel.getDispositivosEntrada('indice')

                try:
                    idx_ent = indices_ent.index(disp_ent)
                    nombre_ent = nombres_ent[idx_ent]
                    self.lblConfDispEnt.setText(nombre_ent)
                    print(f"Dispositivo de entrada actualizado: {nombre_ent}")
                except ValueError:
                    self.lblConfDispEnt.setText("Desconocido")
                    print("Dispositivo de entrada no encontrado en la lista")
            else:
                self.lblConfDispEnt.setText("No disponible")
                print("No hay dispositivo de entrada actual")

            # --------------------
            # Dispositivo de salida
            # --------------------
            disp_sal = self.vController.cModel.getDispositivoSalidaActual()
            if disp_sal is not None:
                nombres_sal = self.vController.cModel.getDispositivosSalida('nombre')
                indices_sal = self.vController.cModel.getDispositivosSalida('indice')

                try:
                    idx_sal = indices_sal.index(disp_sal)
                    nombre_sal = nombres_sal[idx_sal]
                    self.lblConfDispSal.setText(nombre_sal)
                    print(f"Dispositivo de salida actualizado: {nombre_sal}")
                except ValueError:
                    self.lblConfDispSal.setText("Desconocido")
                    print("Dispositivo de salida no encontrado en la lista")
            else:
                self.lblConfDispSal.setText("No disponible")
                print("No hay dispositivo de salida actual")

        except Exception as e:
            print(f"Error al actualizar nombres de dispositivos: {e}")
            if hasattr(self, 'lblConfDispEnt'):
                self.lblConfDispEnt.setText("Error")
            if hasattr(self, 'lblConfDispSal'):
                self.lblConfDispSal.setText("Error")

    
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
    
    def generadorWin(self):
        self.genWin = GeneradorWin(self.vController)
        self.genWin.show()
        
    def configuracionDispositivo(self):
        """Abre la ventana de configuración de dispositivos."""
        self.configDispWin = ConfigDispWin(self.vController, parent_cal_win=self)
        self.configDispWin.show()
    
    def importarSenalCalibracion(self):
        """Importa un archivo .wav y lo grafica en chart2"""
        try:
            from scipy.io.wavfile import read as wavread
            
            # Abrir explorador de archivos para seleccionar archivo .wav
            fileName, _ = QFileDialog.getOpenFileName(
                self, 
                "Seleccionar archivo de audio", 
                "", 
                "Archivos de audio (*.wav);;Todos los archivos (*)"
            )
            
            if fileName:
                # Actualizar label con la ruta del archivo
                if hasattr(self, 'lblRutaArchivoCal'):
                    self.lblRutaArchivoCal.setText(os.path.basename(fileName))
                
                # Guardar la ruta en el controlador para que la lógica la use
                self.vController.establecer_ruta_archivo_calibracion(fileName)

        except Exception as e:
            QMessageBox.critical(self.calWin, "Error", f"Error al importar archivo: {str(e)}")
            print(f"Error en importarSenalCalibracion: {e}")