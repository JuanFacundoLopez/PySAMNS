# Importo librerias
from ventanas.generadorWin import GeneradorWin
from ventanas.configDispWin import ConfigDispWin

from PyQt5.QtWidgets import (QMainWindow, QApplication, QHBoxLayout, QVBoxLayout, QPushButton,
                             QLabel, QLineEdit, QGroupBox, QRadioButton, QWidget, QGridLayout, QMessageBox, QFileDialog, QComboBox)

from PyQt5.QtGui import  QPainter, QIcon

# Imports para QChart (solo para la ventana de calibración)
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtCore import Qt
from utils import norm
import os
import numpy as np



class CalibracionWin(QMainWindow):
    def __init__(self, vController, vVista):
        super().__init__()
        self.setWindowTitle("Calibración")
        self.setWindowIcon(QIcon('img/LogoCINTRA1.png'))
        screen = QApplication.primaryScreen().size()
        self.anchoX = screen.width()
        self.altoY = screen.height()
        self.setGeometry(norm(self.anchoX, self.altoY,0.35, 0.35, 0.3, 0.3))

        with open("estilos.qss", "r", encoding='utf-8') as f:
            QApplication.instance().setStyleSheet(f.read())
          
        self.vController = vController
        self.vVista = vVista
        self._cal_times = None
        self._cal_duration = 0.0
        self._last_samplerate = None
        # Widget central y layout principal
        centralWidget = QWidget()
        mainLayout = QVBoxLayout(centralWidget)

        # Layouts
        tipoCalLayoutHori = QHBoxLayout()
        tipoCalLayoutVer = QVBoxLayout()
        confLayoutVer = QVBoxLayout()
        confLayoutVer.addStretch()
        gridHardLayout = QGridLayout()
        self.valorRefLayout = QHBoxLayout() 
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
        self.btnConfHard.clicked.connect(self.vController.abrir_config_disp)
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

        # Controles de zoom del grafico
        self.zoomLayout = QHBoxLayout()
        self.lblZoom = QLabel("Escala de tiempo:")
        self.cboZoom = QComboBox()
        self.cboZoom.addItem("50 ms", 0.05)
        self.cboZoom.addItem("100 ms", 0.1)
        self.cboZoom.addItem("200 ms", 0.2)
        self.cboZoom.addItem("500 ms", 0.5)
        self.cboZoom.addItem("1 s", 1.0)
        self.cboZoom.addItem("3 s", 3.0)
        self.cboZoom.setCurrentIndex(self.cboZoom.count() - 1)
        self.cboZoom.currentIndexChanged.connect(self._aplicar_zoom_calibracion)
        self.zoomLayout.addWidget(self.lblZoom)
        self.zoomLayout.addWidget(self.cboZoom)
        self.zoomLayout.addStretch()

        #self.btnReproducirCal = QPushButton("Reproducir señal de referencia")
        # self.btnReproducirCal.clicked.connect(self.vController.reproducir_audio_calibracion)
        layoutExterna.addWidget(self.btnImportSig, 0, 0, 1, 2)
        layoutExterna.addWidget(self.lblRutaArchivoCal, 1, 0, 1, 2)
        layoutExterna.addWidget(self.lblValRefExterna, 2, 0)
        layoutExterna.addWidget(self.txtValorRefExterna, 2, 1)
        layoutExterna.addLayout(self.zoomLayout, 3, 0, 1, 2)

        #layoutExterna.addWidget(self.btnReproducirCal, 3, 0, 1, 2)

        # --- Grafico ---
        # Crear QChart para la ventana de calibración
        self.chart2 = QChart()
        self.chart2.setTheme(QChart.ChartThemeDark)
        
        # Crear QChartView para mostrar el gráfico
        self.winGraph2 = QChartView(self.chart2)
        self.winGraph2.setRenderHint(QPainter.Antialiasing)
        self.winGraph2.setRubberBand(QChartView.RectangleRubberBand)

        # Crear series para el gráfico de calibración
        self.plot_line_cal = QLineSeries()
        if hasattr(self.plot_line_cal, "setUseOpenGL"):
            self.plot_line_cal.setUseOpenGL(True)
        self.chart2.addSeries(self.plot_line_cal)
        pen = self.plot_line_cal.pen()
        pen.setWidthF(1.0)
        self.plot_line_cal.setPen(pen)

        # Configurar ejes para el gráfico de calibración
        self.axisX2 = QValueAxis()
        self.axisX2.setTitleText("Tiempo [s]")
        self.axisX2.setRange(0.0, 3.0)
        
        self.axisY2 = QValueAxis()
        self.axisY2.setTitleText("Amplitud Normalizada")
        self.axisY2.setRange(-1.2, 1.2)
        
        
        self.chart2.setAxisX(self.axisX2, self.plot_line_cal)
        self.chart2.setAxisY(self.axisY2, self.plot_line_cal)
        self.chart2.legend().hide()

        # Definir las líneas del gráfico (para compatibilidad)
        self.ptdomTiempo2 = self.plot_line_cal
        self.ptdomEspect2 = self.plot_line_cal

        # --- Botones ---
        self.btnAceptar = QPushButton("Aceptar")
        self.btnCalibrar = QPushButton("Calibrar")
        self.calibracion_realizada = False
        self.btnGenerador = QPushButton("Generador de señales")
        self.btnGenerador.clicked.connect(self.vController.abrir_generador)
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
        #mainLayout.addLayout(self.zoomLayout)
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

        # Inicializar rango del grafico segun la seleccion actual
        self._aplicar_zoom_calibracion()
      
    
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
        
        if self.vVista.esta_calibrado and not self.calibracion_realizada:
            self.btnCalibrar.setText("Repetir calibración")
            self.calibracion_realizada = True
        self.vVista.actualizar_badge_calibracion_pyqtgraph()          
    
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
    

    def _aplicar_zoom_calibracion(self):
        """Actualiza el rango del eje X segun la seleccion del usuario."""
        if not hasattr(self, 'axisX2'):
            return

        selected_window = 3.0
        if hasattr(self, 'cboZoom') and self.cboZoom is not None:
            data = self.cboZoom.currentData()
            if data is not None:
                selected_window = float(data)

        duration = float(getattr(self, '_cal_duration', 0.0) or 0.0)
        if duration <= 0.0:
            duration = min(selected_window, 3.0)

        min_step = 0.001
        samplerate = getattr(self, '_last_samplerate', None)
        if samplerate is not None and samplerate > 0:
            min_step = max(min_step, 1.0 / float(samplerate))

        display_window = min(selected_window, max(duration, min_step))
        self.axisX2.setRange(0.0, display_window)


    def _actualizar_grafico_calibracion(self, data, samplerate, file_path):
        # Actualiza el grafico con la senal importada.
        if data is None or samplerate is None or samplerate <= 0:
            raise ValueError("Datos de audio invalidos.")

        waveform = np.asarray(data)
        if waveform.size == 0:
            raise ValueError("El archivo de audio no contiene muestras.")

        original_dtype = waveform.dtype
        if waveform.ndim > 1:
            waveform = waveform.astype(np.float64)
            waveform = waveform.mean(axis=1)
        else:
            waveform = waveform.astype(np.float64)

        if np.issubdtype(original_dtype, np.integer):
            info = np.iinfo(original_dtype)
            max_abs = float(max(abs(info.min), abs(info.max)))
            if max_abs > 0:
                waveform /= max_abs

        limited_to_window = False
        max_duration_sec = 3.0
        max_samples = max(int(round(max_duration_sec * float(samplerate))), 1)
        if waveform.size > max_samples:
            waveform = waveform[:max_samples]
            limited_to_window = True

        total_samples = waveform.size
        if total_samples == 0:
            raise ValueError("No hay muestras para graficar.")

        max_points = min(60000, total_samples)
        if total_samples <= max_points:
            indices = np.arange(total_samples, dtype=np.int64)
        else:
            indices = np.linspace(0, total_samples - 1, num=max_points, dtype=np.int64)

        waveform_plot = waveform[indices]
        times_plot = indices.astype(np.float64) / float(samplerate)

        self.plot_line_cal.clear()
        for t, y in zip(times_plot, waveform_plot):
            self.plot_line_cal.append(float(t), float(y))

        peak = float(np.max(np.abs(waveform_plot))) if waveform_plot.size else 1.0
        if peak <= 0.0:
            peak = 1.0
        padding = peak * 0.1
        self.axisY2.setRange(-peak - padding, peak + padding)

        self._cal_times = times_plot
        self._cal_duration = float(times_plot[-1]) if times_plot.size else 0.0
        if limited_to_window and self._cal_duration < max_duration_sec:
            self._cal_duration = max_duration_sec
        self._last_samplerate = float(samplerate)

        self._aplicar_zoom_calibracion()


        if file_path:
            self.chart2.setTitle(os.path.basename(file_path))

    def importarSenalCalibracion(self):
        """Importa un archivo .wav y lo grafica en chart2."""
        from scipy.io.wavfile import read as wavread

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de audio",
            "",
            "Archivos de audio (*.wav);;Todos los archivos (*)"
        )

        if not file_name:
            return

        try:
            samplerate, data = wavread(file_name)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo leer el archivo de referencia: {e}"
            )
            print(f"Error al leer archivo de calibracion: {e}")
            return

        if hasattr(self, 'lblRutaArchivoCal'):
            self.lblRutaArchivoCal.setText(os.path.basename(file_name))

        self.vController.establecer_ruta_archivo_calibracion(file_name)

        try:
            self._actualizar_grafico_calibracion(data, samplerate, file_name)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Advertencia",
                f"No se pudo graficar el archivo seleccionado: {e}"
            )
            print(f"Error al graficar archivo de calibracion: {e}")

    def closeEvent(self, event):
        self.vController.ventanas_abiertas["calibracion"] = None
        event.accept()
