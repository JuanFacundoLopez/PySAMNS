# Importo librerias
import os
import sys
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QApplication, QHBoxLayout, QVBoxLayout, QPushButton,
                             QLabel, QLineEdit, QWidget, QMessageBox, QComboBox, QSpinBox)
# Importar pyqtgraph
import pyqtgraph as pg

from PyQt5.QtGui import QIcon, QPainter, QBrush
from PyQt5.QtCore import QPointF, QTimer, Qt
from scipy.signal import chirp

# Imports para QChart (solo para la ventana de calibración)
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from utils import norm
import time
from scipy.interpolate import interp1d



class GeneradorWin(QMainWindow):
    def _get_image_path(self, image_name):
        """Helper method to get image path that works in both dev and frozen environments"""
        if getattr(sys, 'frozen', False):
            # If running as compiled executable
            return os.path.join(sys._MEIPASS, 'img', image_name)
        else:
            # If running in development
            return os.path.join('img', image_name)
    
    def __init__(self, vController):
        self.vController = vController
        super().__init__()
        self.setWindowTitle("Generador de señales")
        self.setWindowIcon(QIcon(self._get_image_path('LogoCINTRA1.png')))
        screen = QApplication.primaryScreen().size()
        self.anchoX = screen.width()
        self.altoY = screen.height()
        self.setGeometry(norm(self.anchoX, self.altoY, 0.4, 0.3, 0.2, 0.4))

        # Timer para controlar el fin de la reproducción
        self.timer_reproduccion = QTimer()
        self.timer_reproduccion.setSingleShot(True)
        self.timer_reproduccion.timeout.connect(self.fin_reproduccion)

        # Handle stylesheet path for both development and frozen executable
        if getattr(sys, 'frozen', False):
            # If running as compiled executable
            base_path = sys._MEIPASS
        else:
            # If running in development
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        # Path to stylesheet
        estilos_path = os.path.join(base_path, 'estilos.qss')
        
        try:
            with open(estilos_path, "r", encoding='utf-8') as f:
                QApplication.instance().setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Warning: Could not load stylesheet at {estilos_path}")
        
        # Widget central y layout principal
        centralWidget = QWidget()
        mainLayout = QVBoxLayout(centralWidget)
        
        configLayout = QHBoxLayout()
        
        self.lbltipoSig = QLabel("Tipo de señal:")
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Senoidal", "Cuadrada", "Triangular", "Ruido Blanco", "Ruido Rosa", "Barrido senoidal exponencial", "Barrido senoidal lineal"])
        configLayout.addWidget(self.lbltipoSig)
        configLayout.addWidget(self.tipo_combo)
        
        self.lblFrecSig = QLabel("Frecuencia (Hz):")
        self.freq_input = QLineEdit("1000")
        configLayout.addWidget(self.lblFrecSig)
        configLayout.addWidget(self.freq_input)
        
        self.lblAmpSig = QLabel("Amplitud:")
        self.amp_input = QLineEdit("1")
        configLayout.addWidget(self.lblAmpSig)
        configLayout.addWidget(self.amp_input)

        self.lblDurSig = QLabel("Duración (s):")
        self.dur_input = QLineEdit("10")
        configLayout.addWidget(self.lblDurSig)
        configLayout.addWidget(self.dur_input)

        self.lblDutyCicleSig = QLabel("Duty cycle (%):")
        self.duty_input = QSpinBox()
        self.duty_input.setRange(0, 99)
        self.duty_input.setValue(50)  # Valor por defecto
        configLayout.addWidget(self.lblDutyCicleSig)
        configLayout.addWidget(self.duty_input)
        self.lblDutyCicleSig.setVisible(False)
        self.duty_input.setVisible(False)
        
        # Campo Tau (constante de decaimiento)
        self.lblFreFinSig = QLabel("Frecueuncia final (Hz):")
        self.FreFin_input = QLineEdit("1")
        configLayout.addWidget(self.lblFreFinSig)
        configLayout.addWidget(self.FreFin_input)
        self.lblFreFinSig.setVisible(False)
        self.FreFin_input.setVisible(False)
        
        self.btn_generar = QPushButton("Reproducir")
        icon_play_path = self._get_image_path("boton-de-play.png") 
        self.btn_generar.setIcon(QIcon(icon_play_path))
        self.btn_generar.clicked.connect(self.play_signal)
        configLayout.addWidget(self.btn_generar)
        
        self.btn_pausa = QPushButton("Pausar")
        icon_pausa_path = self._get_image_path("boton-de-pausa.png") 
        self.btn_pausa.setIcon(QIcon(icon_pausa_path))
        self.btn_pausa.setVisible(False)
        self.btn_pausa.clicked.connect(self.pausar_reproduccion)
        configLayout.addWidget(self.btn_pausa)
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w') # Fondo blanco para coincidir con QChart
        self.plot_widget.setTitle("Señal generada")
        self.plot_item = self.plot_widget.plotItem
        self.plot_item.showGrid(x=True, y=True)
        self.seriesGenSig = self.plot_widget.plot(pen=pg.mkPen(color='b', width=1)) # La serie de la línea
        
        # Renombrar la vista para que coincida con la antigua lógica
        self.chartGenSig_view = self.plot_widget
        
        self.tipo_combo.currentIndexChanged.connect(self.mostra_duty_cicle)
        self.tipo_combo.currentIndexChanged.connect(self.mostrar_frecuencia)
        self.tipo_combo.currentIndexChanged.connect(self.mostrar_tau)
        self.tipo_combo.currentIndexChanged.connect(self.generar_senal)
        self.dur_input.textChanged.connect(self.generar_senal)
        self.freq_input.textChanged.connect(self.generar_senal)
        self.amp_input.textChanged.connect(self.generar_senal)
        self.duty_input.valueChanged.connect(self.generar_senal)
        self.FreFin_input.textChanged.connect(self.generar_senal)
        

        mainLayout.addLayout(configLayout)
        self.lbl_error_gen_sig = QLabel("")
        self.lbl_error_gen_sig.setAlignment(Qt.AlignCenter)
        mainLayout.addWidget(self.lbl_error_gen_sig)
        self.lbl_error_gen_sig.setVisible(False)
        mainLayout.addWidget(self.chartGenSig_view)

        for boton in [self.btn_generar, self.btn_pausa]:
            boton.setProperty("class", "ventanasSec")

        for txt in [self.freq_input, self.amp_input, self.dur_input, self.duty_input, self.FreFin_input]:
            txt.setProperty("class", "ventanasSec")
            
        for lbl in [self.lbltipoSig, self.lblFrecSig, self.lblAmpSig, self.lblDurSig, self.lblDutyCicleSig, self.lblFreFinSig]:
            lbl.setProperty("class", "ventanasSecLabelDestacado")  

        self.lbl_error_gen_sig.setProperty("class", "errorLbl") 

        for combo in [self.tipo_combo]:
                combo.setProperty("class", "ventanasSec") 
         
         
        self.setCentralWidget(centralWidget)
        
        time.sleep(0.5)  # Pequeña pausa para asegurar que la ventana se renderice correctamente
        self.generar_senal()  # Generar la señal inicial
        
    
    def mostra_duty_cicle(self):
        if self.tipo_combo.currentText() == "Cuadrada":
            self.lblDutyCicleSig.setVisible(True)
            self.duty_input.setVisible(True)
        else:
            self.lblDutyCicleSig.setVisible(False)
            self.duty_input.setVisible(False)

    def mostrar_tau(self):
        if self.tipo_combo.currentText() in ["Barrido senoidal exponencial", "Barrido senoidal lineal"]:
            self.lblFrecSig.setText("Frecuencia Inicial(Hz):")
            self.lblFreFinSig.setVisible(True)
            self.FreFin_input.setVisible(True)
        else:
            self.lblFrecSig.setText("Frecuencia (Hz):")
            self.lblFreFinSig.setVisible(False)
            self.FreFin_input.setVisible(False)
            
    def mostrar_frecuencia(self):
        if self.tipo_combo.currentText() in [ "Ruido Blanco", "Ruido Rosa"]:
            self.lblFrecSig.setVisible(False)
            self.freq_input.setVisible(False)
        else:
            self.lblFrecSig.setVisible(True)
            self.freq_input.setVisible(True)
    
    def verificar_valores_generador(self):
        try:
            f = float(self.freq_input.text())
            A = float(self.amp_input.text())
            T = float(self.dur_input.text())
            d = self.duty_input.value()
            if f <= 0:
                self.lbl_error_gen_sig.setText("La frecuencia debe ser > 0 Hz.")
                self.lbl_error_gen_sig.setVisible(True)
                return False
            if A <= 0 or A > 100:
                self.lbl_error_gen_sig.setText("La amplitud debe ser > 0 y <= 100.")
                self.lbl_error_gen_sig.setVisible(True)
                return False
            if T <= 0 or T > 900:
                self.lbl_error_gen_sig.setText("La duración debe ser > 0 y <= 900 s.")
                self.lbl_error_gen_sig.setVisible(True)
                return False
            if self.tipo_combo.currentText() == "Cuadrada" and (d < 0 or d > 100):
                self.lbl_error_gen_sig.setText("El duty cycle debe ser entre 0 y 100%.")
                self.lbl_error_gen_sig.setVisible(True)
                return False
            if self.tipo_combo.currentText() in ["Barrido senoidal exponencial", "Barrido senoidal lineal"]:
                frecIni = float(self.freq_input.text())
                frecFin = float(self.FreFin_input.text())
                if frecIni <= 0 or frecFin <= 0:
                    self.lbl_error_gen_sig.setText("Las frecuencias deben ser mayores a > 0.")
                    self.lbl_error_gen_sig.setVisible(True)
                    return False
                
            self.lbl_error_gen_sig.setVisible(False)
            return True
        except ValueError:
            self.lbl_error_gen_sig.setText("Ingrese solo números en todos los campos.")
            self.lbl_error_gen_sig.setVisible(True)
            return False

    def pausar_reproduccion(self):
        """Pausa la reproduccion de la señal generada por el dispositivo de salida"""
        self.btn_generar.setVisible(True)
        self.btn_pausa.setVisible(False)
        
        # Detener el timer si está corriendo
        if self.timer_reproduccion.isActive():
            self.timer_reproduccion.stop()
            
        try:
            import sounddevice as sd
            sd.stop()  # Detiene cualquier señal en reproducción
            print("Reproducción pausada")
        except Exception as e:
            print(f"Error al pausar la señal: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo pausar la señal: {str(e)}")
    
    def fin_reproduccion(self):
        """Función que se ejecuta cuando termina la reproducción automáticamente"""
        self.btn_generar.setVisible(True)
        self.btn_pausa.setVisible(False)
        print("Reproducción terminada")
            
    def generar_senal(self):
        if not self.verificar_valores_generador():
            return

        tipo = self.tipo_combo.currentText()
        # Usa la frecuencia inicial o un valor por defecto si no es visible
        f = float(self.freq_input.text()) if self.freq_input.isVisible() and self.freq_input.text() else 1000
        A = float(self.amp_input.text())
        T = float(self.dur_input.text())
        Fs = 44100
        t = np.linspace(0, T, int(Fs * T), endpoint=False) # Usar endpoint=False para evitar un punto extra

        # Generate signal based on type
        if tipo == "Senoidal":
            y = A * np.sin(2 * np.pi * f * t)
        elif tipo == "Cuadrada":
            duty = self.duty_input.value() / 100.0
            fase = (f * t) % 1.0
            y = A * np.where(fase < duty, 1.0, -1.0) 
        elif tipo == "Triangular":
            y = A * (2 * np.abs(2 * (t * f - np.floor(t * f + 0.5))) - 1)
        elif tipo == "Ruido Blanco":
            y = np.random.normal(0, 1, len(t))
            y = y / np.max(np.abs(y)) # normalización a [-1, 1]
            y *= A
        elif tipo == "Ruido Rosa":
            N = len(t)
            uneven = N % 2
            X = np.random.randn(N // 2 + 1 + uneven) + 1j * np.random.randn(N // 2 + 1 + uneven)
            S = np.sqrt(np.arange(len(X)) + 1)
            # Manejar división por cero en S (el primer elemento, si N es muy pequeño)
            S[0] = S[1] if len(S) > 1 else 1.0
            y = (np.fft.irfft(X / S)).real
            y = y[:N]
            y /= np.max(np.abs(y))  # normalización a [-1, 1]
            y *= A
        elif tipo in ["Barrido senoidal exponencial", "Barrido senoidal lineal"]:
            f_ini = float(self.freq_input.text())
            f_fin = float(self.FreFin_input.text())
            method = 'logarithmic' if tipo == "Barrido senoidal exponencial" else 'linear'
            y = A * chirp(t, f0=f_ini, t1=T, f1=f_fin, method=method)
        else:
            return  # Invalid signal type
        
        # Store signal data
        self.signal_data = y.astype(np.float32)
        self.sample_rate = Fs

        # --- Lógica de Ajuste Dinámico para Visualización con pyqtgraph ---

        # Duración de zoom máxima para cualquier forma de onda periódica o barrido
        DURACION_ZOOM_MAX = 0.1 # 100 ms

        if tipo in ["Ruido Blanco", "Ruido Rosa"]:
            # Para ruidos, muestra un segmento corto (ej: 50ms)
            duracion_base = min(0.05, T)
        
        elif tipo in ["Barrido senoidal exponencial", "Barrido senoidal lineal"]:
            # Usar una duración de zoom FIJA (ej: 100 ms) para ver el barrido inicial en ambos sentidos
            duracion_base = T
            
        else: # Senoidal, Cuadrada, Triangular
            # Mostrar al menos 5 ciclos, o DURACION_ZOOM_MAX, lo que sea más corto (pero no menos de 5 ciclos)
            num_ciclos_visibles = 5
            # Calcular duración necesaria para 5 ciclos
            duracion_5_ciclos = num_ciclos_visibles / f if f > 0.01 else T
            # Limitar la duración base a 5 ciclos o al zoom máximo, lo que sea menor
            duracion_base = min(duracion_5_ciclos, DURACION_ZOOM_MAX, T)
            # Si la frecuencia es muy baja y duracion_base es muy grande, pyqtgraph lo manejará

        # Calcular el segmento de datos a mostrar
        num_samples_base = int(Fs * duracion_base)
        num_samples_base = min(num_samples_base, len(t))
        t_visible = t[:num_samples_base]
        y_visible = y[:num_samples_base]
        
        # La duración que el eje X debe mostrar
        duracion_ejeX = duracion_base

        # --- Graficación con pyqtgraph ---
        
        # 1. Limpiar y actualizar la serie
        # pyqtgraph acepta los arrays de numpy directamente, sin necesidad de interpolación o submuestreo manual.
        self.seriesGenSig.setData(t_visible, y_visible)

        # 2. Configurar el rango del eje
        # pyqtgraph usa setRange(xMin, xMax, yMin, yMax) o setLimits
        
        # Rango X
        self.plot_item.setXRange(0, duracion_ejeX, padding=0)
        self.plot_item.getAxis('bottom').setLabel("Tiempo (s)")
        
        # Rango Y
        A_margen = A * 1.1 
        self.plot_item.setYRange(-A_margen, A_margen, padding=0)
        self.plot_item.getAxis('left').setLabel("Amplitud")

        # Se eliminan todas las líneas de configuración de QChart (removeAxis, addAxis, attachAxis)
       

    def play_signal(self):
        """Play the generated signal through the selected output device"""
        self.btn_generar.setVisible(False)
        self.btn_pausa.setVisible(True)
        
        if not hasattr(self, 'signal_data') or self.signal_data is None:
            print("No hay señal generada para reproducir")
            return
            
        try:
            import sounddevice as sd
            
            # Get the selected output device index from the model
            output_device = self.vController.cModel.getDispositivoSalidaActual()
            
            if output_device is None:
                QMessageBox.warning(self, "Error", "No se ha seleccionado un dispositivo de salida.")
                self.btn_generar.setVisible(True)
                self.btn_pausa.setVisible(False)
                return
                
            print(f"Reproduciendo señal en el dispositivo {output_device}...")
            
            # Obtener la duración de la señal
            duracion_ms = int(float(self.dur_input.text()) * 1000)  # Convertir a milisegundos
            
            # Iniciar el timer para que termine la reproducción automáticamente
            self.timer_reproduccion.start(duracion_ms)
            
            # Play the signal
            sd.play(self.signal_data, self.sample_rate, device=output_device)
            
        except Exception as e:
            print(f"Error al reproducir la señal: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo reproducir la señal: {str(e)}")
            # En caso de error, restaurar los botones
            self.btn_generar.setVisible(True)
            self.btn_pausa.setVisible(False)
            
    def closeEvent(self, event):
        # Detener cualquier reproducción y timer al cerrar
        if hasattr(self, 'timer_reproduccion') and self.timer_reproduccion.isActive():
            self.timer_reproduccion.stop()
        
        try:
            import sounddevice as sd
            sd.stop()
        except:
            pass
            
        self.vController.ventanas_abiertas["generador"] = None
        event.accept()