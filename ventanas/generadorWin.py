# Importo librerias
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QApplication, QHBoxLayout, QVBoxLayout, QPushButton,
                             QLabel, QLineEdit, QWidget, QMessageBox, QComboBox, QSpinBox)

from PyQt5.QtGui import  QIcon, QPainter
from PyQt5.QtCore import QPointF


# Imports para QChart (solo para la ventana de calibración)
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtCore import Qt
from utils import norm




class GeneradorWin(QMainWindow):
    def __init__(self, vController):
        super().__init__()
        self.setWindowTitle("Generador de señales")
        screen = QApplication.primaryScreen().size()
        self.anchoX = screen.width()
        self.altoY = screen.height()
        self.setGeometry(norm(self.anchoX, self.altoY, 0.4, 0.3, 0.2, 0.4))

        with open("estilos.qss", "r", encoding='utf-8') as f:
            QApplication.instance().setStyleSheet(f.read())
        
        # Widget central y layout principal
        centralWidget = QWidget()
        mainLayout = QVBoxLayout(centralWidget)
        
        configLayout = QHBoxLayout()
        
        self.lbltipoSig = QLabel("Tipo de señal:")
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Senoidal", "Cuadrada", "Triangular", "Ruido Blanco", "Ruido Rosa"])
        configLayout.addWidget(self.lbltipoSig)
        configLayout.addWidget(self.tipo_combo)
        
        self.lblFrecSig = QLabel("Frecuencia (Hz):")
        self.freq_input = QLineEdit("5")
        configLayout.addWidget(self.lblFrecSig)
        configLayout.addWidget(self.freq_input)
        
        self.lblAmpSig = QLabel("Amplitud:")
        self.amp_input = QLineEdit("1")
        configLayout.addWidget(self.lblAmpSig)
        configLayout.addWidget(self.amp_input)

        self.lblDurSig = QLabel("Duración (s):")
        self.dur_input = QLineEdit("0.5")
        configLayout.addWidget(self.lblDurSig)
        configLayout.addWidget(self.dur_input)

        self.lblDutyCicleSig = QLabel("Duty cicle (%):")
        self.duty_input = QSpinBox()
        self.duty_input.setRange(0, 99)
        self.duty_input.setValue(1)  # Valor por defecto
        configLayout.addWidget(self.lblDutyCicleSig)
        configLayout.addWidget(self.duty_input)
        self.lblDutyCicleSig.setVisible(False)
        self.duty_input.setVisible(False)
        
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
        self.chartGenSig.setTitle("Señal Generada")
        self.chartGenSig.legend().hide()

        self.chartGenSig_view = QChartView(self.chartGenSig)
        self.chartGenSig_view.setRenderHint(QPainter.Antialiasing)
        
        self.tipo_combo.currentIndexChanged.connect(self.mostra_duty_cicle)
        self.tipo_combo.currentIndexChanged.connect(self.mostrar_frecuencia)
        self.tipo_combo.currentIndexChanged.connect(self.generar_senal)
        self.dur_input.textChanged.connect(self.generar_senal)
        self.freq_input.textChanged.connect(self.generar_senal)
        self.amp_input.textChanged.connect(self.generar_senal)
        self.duty_input.valueChanged.connect(self.generar_senal)
        

        mainLayout.addLayout(configLayout)
        self.lbl_error_gen_sig = QLabel("")
        self.lbl_error_gen_sig.setAlignment(Qt.AlignCenter)
        mainLayout.addWidget(self.lbl_error_gen_sig)
        self.lbl_error_gen_sig.setVisible(False)
        mainLayout.addWidget(self.chartGenSig_view)

        for boton in [self.btn_generar, self.btn_pausa]:
            boton.setProperty("class", "ventanasSec")

        for txt in [self.freq_input, self.amp_input, self.dur_input, self.duty_input]:
            txt.setProperty("class", "ventanasSec")
            
        for lbl in [self.lbltipoSig, self.lblFrecSig, self.lblAmpSig, self.lblDurSig, self.lblDutyCicleSig]:
            lbl.setProperty("class", "ventanasSecLabelDestacado")  

        self.lbl_error_gen_sig.setProperty("class", "errorLbl") 

        for combo in [self.tipo_combo]:
                combo.setProperty("class", "ventanasSec") 
            
        self.setCentralWidget(centralWidget)
    
    def mostra_duty_cicle(self):
        if self.tipo_combo.currentText() == "Cuadrada":
            self.lblDutyCicleSig.setVisible(True)
            self.duty_input.setVisible(True)
        else:
            self.lblDutyCicleSig.setVisible(False)
            self.duty_input.setVisible(False)

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
            if T <= 0 or T > 15:
                self.lbl_error_gen_sig.setText("La duración debe ser > 0 y <= 15 s.")
                self.lbl_error_gen_sig.setVisible(True)
                return False
            if self.tipo_combo.currentText() == "Cuadrada" and (d < 0 or d > 100):
                self.lbl_error_gen_sig.setText("El duty cycle debe ser entre 0 y 100%.")
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
        try:
            import sounddevice as sd
            sd.stop()  # Detiene cualquier señal en reproducción
            print("Reproducción pausada")
        except Exception as e:
            print(f"Error al pausar la señal: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo pausar la señal: {str(e)}")
            
    def generar_senal(self):
        if not self.verificar_valores_generador():
            return
        tipo = self.tipo_combo.currentText()
        f = float(self.freq_input.text())
        A = float(self.amp_input.text())
        T = float(self.dur_input.text())
        Fs = 44100
        t = np.linspace(0, T, int(Fs*T))

        if tipo == "Senoidal":
            y = A * np.sin(2 * np.pi * f * t)
        elif tipo == "Cuadrada":
            duty = self.duty_input.value() / 100.0  # 0..1
            fase = (f * t) % 1.0                   # 0..1 por ciclo
            y = A * np.where(fase < duty, 1.0, -1.0)
        elif tipo == "Triangular":
            y = A * 2 * np.abs(2 * (t * f - np.floor(t * f + 0.5))) - 1
        elif tipo == "Ruido Blanco":
            y = A * np.random.normal(0, 1, len(t))
        elif tipo == "Ruido Rosa":
            # Método basado en filtrado 1/f
            # FFT-based approach para generar ruido rosa
            N = len(t)
            uneven = N % 2
            X = np.random.randn(N // 2 + 1 + uneven) + 1j * np.random.randn(N // 2 + 1 + uneven)
            S = np.sqrt(np.arange(len(X)) + 1)  # +1 para evitar división por cero
            y = (np.fft.irfft(X / S)).real
            y = y[:N]
            y *= A

        #Normalizar la señal
        y = y / np.max(np.abs(y)) * 1 # para evitar saturación

        #Guardar los datos de la señal
        self.signal_data = y.astype(np.float32)
        self.sample_rate = Fs

        # Graficar la señal
        self.chartGenSig.removeSeries(self.seriesGenSig)
        self.seriesGenSig.clear()
        
        for i in range(len(t)):
            self.seriesGenSig.append(QPointF(t[i], y[i]))
        
        self.chartGenSig.addSeries(self.seriesGenSig)
        self.chartGenSig.createDefaultAxes()
    
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
                return
                
            print(f"Reproduciendo señal en el dispositivo {output_device}...")
            
            # Play the signal
            sd.play(self.signal_data, self.sample_rate, device=output_device)
            
        except Exception as e:
            print(f"Error al reproducir la señal: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo reproducir la señal: {str(e)}")