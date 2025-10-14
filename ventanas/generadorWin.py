# Importo librerias
import os
import sys
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QApplication, QHBoxLayout, QVBoxLayout, QPushButton,
                             QLabel, QLineEdit, QWidget, QMessageBox, QComboBox, QSpinBox)

from PyQt5.QtGui import QIcon, QPainter, QBrush
from PyQt5.QtCore import QPointF, QTimer, Qt
from scipy.signal import chirp

# Imports para QChart (solo para la ventana de calibración)
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from utils import norm
import time
from scipy.interpolate import interp1d



class GeneradorWin(QMainWindow):
    def __init__(self, vController):
        self.vController = vController
        super().__init__()
        self.setWindowTitle("Generador de señales")
        self.setWindowIcon(QIcon('img/LogoCINTRA1.png'))
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
        icon_play_path = "img/boton-de-play.png" 
        self.btn_generar.setIcon(QIcon(icon_play_path))
        self.btn_generar.clicked.connect(self.play_signal)
        configLayout.addWidget(self.btn_generar)
        
        self.btn_pausa = QPushButton("Pausar")
        icon_pausa_path = "img/boton-de-pausa.png" 
        self.btn_pausa.setIcon(QIcon(icon_pausa_path))
        self.btn_pausa.setVisible(False)
        self.btn_pausa.clicked.connect(self.pausar_reproduccion)
        configLayout.addWidget(self.btn_pausa)
        
        self.seriesGenSig = QLineSeries()
        self.chartGenSig = QChart()
        self.chartGenSig.addSeries(self.seriesGenSig)
        self.chartGenSig.createDefaultAxes()
        # Establecer el rango del eje X para que sea más largo que 1 (por ejemplo, hasta 10)
        axisX = self.chartGenSig.axisX(self.seriesGenSig)
        if axisX is not None:
            axisX.setRange(0, 10)
        self.chartGenSig.setTitle("Señal generada")
        self.chartGenSig.legend().hide()
        
        
        self.chartGenSig_view = QChartView(self.chartGenSig)
        self.chartGenSig_view.setRenderHint(QPainter.Antialiasing)
        
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
        f = float(self.freq_input.text()) if self.freq_input.isVisible() else 1000
        A = float(self.amp_input.text())
        T = float(self.dur_input.text())
        Fs = 44100
        t = np.linspace(0, T, int(Fs * T))

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
            y = A * np.random.normal(0, 1, len(t))
            y = y / np.max(np.abs(y))
        elif tipo == "Ruido Rosa":
            N = len(t)
            uneven = N % 2
            X = np.random.randn(N // 2 + 1 + uneven) + 1j * np.random.randn(N // 2 + 1 + uneven)
            S = np.sqrt(np.arange(len(X)) + 1)
            y = (np.fft.irfft(X / S)).real
            y = y[:N]
            y /= np.max(np.abs(y))  # normalización a [-1, 1]
            y *= A
        elif tipo in ["Barrido senoidal exponencial", "Barrido senoidal lineal"]:
            N, T = 1000, 0.01  # number of samples and sampling interval for 10 s signal
            t = np.arange(N) * T  # timestamps
            f_ini = float(self.freq_input.text())
            f_fin = float(self.FreFin_input.text())
            method = 'logarithmic' if tipo == "Barrido senoidal exponencial" else 'linear'
            y = A * chirp(t, f0=f_ini, f1=f_fin, t1=10, method=method)
        else:
            return  # Invalid signal type
        
        # Store signal data
        self.signal_data = y.astype(np.float32)
        self.sample_rate = Fs

        # Visualization settings
        if tipo in ["Ruido Blanco", "Ruido Rosa"]:
            duracion_visible = min(0.05, T)
        elif tipo in ["Barrido senoidal exponencial", "Barrido senoidal lineal"]:
            duracion_visible = T
        else:
            num_ciclos_visibles = 5
            duracion_visible = num_ciclos_visibles / f

        # -----------------------
        # Ajuste dinámico del eje X según el tipo de señal
        # -----------------------
        
        # Para ruidos, mostrar siempre 5 segundos fijos
        if tipo in ["Ruido Blanco", "Ruido Rosa"]:
            duracion_visible = min(0.05, T)  # Máximo 5 segundos o la duración total si es menor
        elif tipo in ["Barrido senoidal exponencial", "Barrido senoidal lineal"]:
            # Para barrdidos
            duracion_visible = float(self.dur_input.text())
        else:
            # Para otras señales, mostrar según frecuencia
            num_ciclos_visibles = 5
            duracion_visible = num_ciclos_visibles / f  # ventana de tiempo que muestra 5 ciclos
        
        num_samples_visible = int(Fs * duracion_visible)
        num_samples_visible = min(num_samples_visible, len(t))  # No exceder la longitud total

        t_visible = t[:num_samples_visible]
        y_visible = y[:num_samples_visible]

        # Interpolación visual para evitar aliasing en pantalla (solo si no es ruido)
        if tipo not in ["Ruido Blanco", "Ruido Rosa"]:
            t_interp = np.linspace(t_visible[0], t_visible[-1], int(len(t_visible) * 10))
            interpolador = interp1d(t_visible, y_visible, kind='cubic')
            y_interp = interpolador(t_interp)
        else:
            # Para ruidos, usar los datos originales sin interpolación
            t_interp = t_visible
            y_interp = y_visible

        # Submuestreo para mostrar máximo N puntos
        max_points = 1000
        step = max(1, len(t_interp) // max_points)

        self.chartGenSig.removeSeries(self.seriesGenSig)
        self.seriesGenSig.clear()

        for i in range(0, len(t_interp), step):
            self.seriesGenSig.append(QPointF(t_interp[i], y_interp[i]))

        self.chartGenSig.addSeries(self.seriesGenSig)
        
        # Elimina cualquier eje anterior
        self.chartGenSig.removeAxis(self.chartGenSig.axisX())
        self.chartGenSig.removeAxis(self.chartGenSig.axisY())

        # Crear ejes manualmente
        axisX = QValueAxis()
        axisX.setRange(0, duracion_visible)
        axisX.setTitleText("Tiempo (s)")
        axisX.setTitleVisible(True)
        axisX.setTitleBrush(QBrush(Qt.black))
        axisX.setLabelsBrush(QBrush(Qt.black))  # Etiquetas blancas también
        axisX.setLinePenColor(Qt.black)

        axisY = QValueAxis()
        axisY.setRange(-1, 1)
        axisY.setTitleText("Amplitud normalizada")
        axisY.setTitleVisible(True)
        axisY.setTitleBrush(QBrush(Qt.black))
        axisY.setLabelsBrush(QBrush(Qt.black))
        axisY.setLinePenColor(Qt.black)

        # Agregar ejes al gráfico y asociar la serie
        self.chartGenSig.addAxis(axisX, Qt.AlignBottom)
        self.chartGenSig.addAxis(axisY, Qt.AlignLeft)
        self.seriesGenSig.attachAxis(axisX)
        self.seriesGenSig.attachAxis(axisY)
        
        # For visualization of sweep signals
        if tipo in ["Barrido senoidal exponencial", "Barrido senoidal lineal"]:
            t_visible = t
            y_visible = y
            
            # Create more points for smooth visualization
            t_interp = t_visible
            y_interp = y_visible
            
            # Update axes ranges for better visualization
            self.chartGenSig.removeSeries(self.seriesGenSig)
            self.seriesGenSig.clear()
            
            # Reduce number of points for display
            max_points = 2000
            step = max(1, len(t_interp) // max_points)
            
            for i in range(0, len(t_interp), step):
                self.seriesGenSig.append(QPointF(t_interp[i], y_interp[i]))
                
            self.chartGenSig.addSeries(self.seriesGenSig)
            
            # Create custom axes for sweep signals
            axisX = QValueAxis()
            axisX.setRange(0, T)
            axisX.setTitleText("Tiempo (s)")
            
            axisY = QValueAxis()
            axisY.setRange(-A, A)
            axisY.setTitleText("Amplitud")
            
            self.chartGenSig.removeAxis(self.chartGenSig.axisX())
            self.chartGenSig.removeAxis(self.chartGenSig.axisY())
            self.chartGenSig.addAxis(axisX, Qt.AlignBottom)
            self.chartGenSig.addAxis(axisY, Qt.AlignLeft)
            self.seriesGenSig.attachAxis(axisX)
            self.seriesGenSig.attachAxis(axisY)
       

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