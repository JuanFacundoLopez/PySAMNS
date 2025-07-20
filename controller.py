from model import modelo
from view import vista

from PyQt5.QtWidgets import QFileDialog
from pyqtgraph.Qt import QtCore
import struct
# from pyaudio import PyAudio, paInt16
import pyaudio
# from scipy.fftpack import fft

import numpy as np 

# import sys
# sys.path.append('./funciones')

from funciones.grabacionSAMNS import grabacion
from scipy.signal import butter

# from matplotlib import pyplot as plt 
import time

from PyQt5.QtWidgets import * 

#import funciones de scipy
from scipy.io.wavfile import read as wavread

class controlador():

    def __init__(self):                             # Constructor del controlador
        self.cModel = modelo(self)                  # Conecto la referencia del modelo 
        self.cVista = vista(self)                   # Conecto la referencia de la vista 

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_view)
        self.msCounter = 0
        self.start_time = None  # Add start time tracking
        #    Setear todas las ganancias en Cero
        self.device_active = False
        self.device1_name = "Nombre del dispositivo de audio"
        self.setGainZero()

        #Filtro pasa bajos
        self.rate = 44100 #evitar, se debe pasar el chunck predefinido
        nyq = self.rate/2
        normal_cutoff = 100 / nyq #Cutoff = 100
        (self.b, self.a) = butter(1, normal_cutoff, btype='low', analog=False)

        
    def setGainZero(self):                          # Seteo los valores a cero (inicialización)
        self.gainZP = 0.000000001
        self.gainZI = 0.000000001
        self.gainZF = 0.000000001
        self.gainZS = 0.000000001

        self.gainCP = 0.000000001
        self.gainCI = 0.000000001
        self.gainCF = 0.000000001
        self.gainCS = 0.000000001

        self.gainAP = 0.000000001
        self.gainAI = 0.000000001
        self.gainAF = 0.000000001
        self.gainAS = 0.000000001

        # Arreglos para filtro Z
        self.dataVectorPicoZ = np.array([])
        self.dataVectorInstZ = np.array([])
        self.dataVectorFastZ = np.array([])
        self.dataVectorSlowZ = np.array([])      

        # Arreglos para filtro C
        self.dataVectorPicoC = np.array([])
        self.dataVectorInstC = np.array([])
        self.dataVectorFastC = np.array([])
        self.dataVectorSlowC = np.array([])

        # Arreglos para filtro A
        self.dataVectorPicoA = np.array([])
        self.dataVectorInstA = np.array([])
        self.dataVectorFastA = np.array([])
        self.dataVectorSlowA = np.array([])      

        self.cModel.setNivelesA(0,0,0,0, mode='r')
        self.cModel.setNivelesC(0,0,0,0, mode='r')
        self.cModel.setNivelesZ(0,0,0,0, mode='r')

    def importSignal(self):                         # Funcion de importar señal
        # QFileDialog.getOpenFileName() sirve para abrir 
        # una ventana de windows para buscar el archivo que quiero
        SignalfileName = QFileDialog.getOpenFileName()
        
        # Read wav file
        Fs,x = wavread(SignalfileName[0])
        maxX=int(max(x))
        signaldata=x/maxX

        if Fs > 44000: # validacion de la entrada de datos
            self.cModel.setFs(Fs) # Guardo en base de datos/modelo
            print("Fs fue correctamente cargado")
        else:
            print("Fs es invalido " + str(Fs))
        if len(signaldata) > 2:# validacion de la entrada de datos
            self.cModel.setSignalData(signaldata)  # Guardo en base de datos/modelo      
            print("signaldata fue correctamente cargado")
        else:
            print("signaldata es invalido")

        # Hago una peticion a modelo y mando informacion a la vista 
        # para que los datos levantados sean cargados
        self.graficar()

    def graficar(self):                             # Funcion para graficar las señales
        if self.cVista.btnTiempo.isChecked():
            # Tiempo
            if self.cVista.r0.isChecked():
                data = self.cModel.getSignalData('A')
                x = np.arange(len(data))
                self.cVista.ptdomTiempo.setData(x, data)
            elif self.cVista.r1.isChecked():
                data = self.cModel.getSignalData('C')
                x = np.arange(len(data))
                self.cVista.ptdomTiempo.setData(x, data)
            elif self.cVista.r2.isChecked():
                data = self.cModel.getSignalData('Z')
                x = np.arange(len(data))
                self.cVista.ptdomTiempo.setData(x, data)

        elif self.cVista.btnFrecuencia.isChecked():
            # Espectro
            if self.cVista.r0.isChecked():
                yf_data = self.cModel.getSignalFrec('A')
                f = np.linspace(0, int(self.cModel.rate/2), int(self.cModel.chunk/2))
                self.cVista.ptdomEspect.setData(f, yf_data)
            elif self.cVista.r1.isChecked():
                yf_data = self.cModel.getSignalFrec('C')
                f = np.linspace(0, int(self.cModel.rate/2), int(self.cModel.chunk/2))
                self.cVista.ptdomEspect.setData(f, yf_data)
            elif self.cVista.r2.isChecked():
                yf_data = self.cModel.getSignalFrec('Z')
                f = np.linspace(0, int(self.cModel.rate/2), int(self.cModel.chunk/2))
                self.cVista.ptdomEspect.setData(f, yf_data)

        elif self.cVista.btnNivel.isChecked():
            # Nivel
            timeNivelData = np.arange(0, len(self.dataVectorPicoZ))
            
            # Vista de filtro Z
            (dataVectorPicoZ, dataVectorInstZ, dataVectorFastZ, dataVectorSlowZ) = self.cModel.getNivelesZ()
            
            if self.cVista.cbNivPicoZ.isChecked():             
                self.cVista.ptNivZPico.setData(timeNivelData, dataVectorPicoZ)
            elif self.cVista.cbNivInstZ.isChecked():
                self.cVista.ptNivZInst.setData(timeNivelData, dataVectorInstZ)
            elif self.cVista.cbNivFastZ.isChecked():
                self.cVista.ptNivZFast.setData(timeNivelData, dataVectorFastZ)
            elif self.cVista.cbNivSlowZ.isChecked():
                self.cVista.ptNivZSlow.setData(timeNivelData, dataVectorSlowZ)

            # Vista de filtro C
            (dataVectorPicoC, dataVectorInstC, dataVectorFastC, dataVectorSlowC) = self.cModel.getNivelesC()
            
            if self.cVista.cbNivPicoC.isChecked():
                self.cVista.ptNivCPico.setData(timeNivelData, dataVectorPicoC)
            elif self.cVista.cbNivInstC.isChecked():
                self.cVista.ptNivCInst.setData(timeNivelData, dataVectorInstC)
            elif self.cVista.cbNivFastC.isChecked():
                self.cVista.ptNivCFast.setData(timeNivelData, dataVectorFastC)
            elif self.cVista.cbNivSlowC.isChecked():
                self.cVista.ptNivCSlow.setData(timeNivelData, dataVectorSlowC)

            # Vista de filtro A
            (dataVectorPicoA, dataVectorInstA, dataVectorFastA, dataVectorSlowA) = self.cModel.getNivelesA()
            
            if self.cVista.cbNivPicoA.isChecked():
                self.cVista.ptNivAPico.setData(timeNivelData, dataVectorPicoA)
            elif self.cVista.cbNivInstA.isChecked():
                self.cVista.ptNivAInst.setData(timeNivelData, dataVectorInstA)
            elif self.cVista.cbNivFastA.isChecked():
                self.cVista.ptNivAFast.setData(timeNivelData, dataVectorFastA)
            elif self.cVista.cbNivSlowA.isChecked():
                self.cVista.ptNivASlow.setData(timeNivelData, dataVectorSlowA)

    def callback(self, in_data, frame_count, time_info, status):    # Stream de audio
        in_data = struct.unpack( "f"*frame_count, in_data )
        #To keep this function fast, just copy out to samples_rx
        self.wf_data = np.array(in_data)*2
        
        if self.c < 20:
            self.wf_data = np.zeros(1024)+0.001
        else:
            if self.c < 100:
                self.wf_data = np.ones(1024)
            else:
                self.wf_data = np.zeros(1024)+0.001

        self.c+=1
        # print(self.wf_data)
        # self.grabar()
        return (self.grabar(), pyaudio.paContinue)  

    def grabar(self):                               # Monitoreo en tiempo real
        grabacion(self)
        self.graficar()
        
    def dalePlay(self):                            # Comunicacion con la Vista

        if self.cVista.btngbr.isChecked() == False:
            self.timer.stop() 
            self.cVista.btngbr.setText('Grabar')
            self.cModel.stream.stop_stream() #Verificar estas funciones
            # self.stream.close()
        else:
            self.setGainZero()
            self.cVista.btngbr.setText('Stop')  
            self.msCounter = 0
            self.timer.start(30) 
            self.device_active = True
            self.cModel.stream.start_stream() #Verificar estas funciones

    def update_view(self):                           # Cronometro
         # Actualizar dispositivo 1 si está activo
        if self.device_active:
            try:
                current_data1, all_data1, norm_current1, norm_all1, db1, times1 = self.cModel.get_audio_data()
                if len(current_data1) > 0:  # Verificar si hay datos
                    self.cVista.update_plot(1, current_data1, all_data1, norm_current1, norm_all1, db1, self.device1_name, times1)
            except Exception as e:
                print(f"Error al actualizar dispositivo 1: {e}")
                self.device1_active = False
        else:
            print("No se inicio grabacion")

        if self.start_time is None:
            self.start_time = time.time()
            # self.normalized_all = []  # Volver a inicializar normalized_all cuando se inicia un nuevo stream
            self.times = []  # Resetear el tiempo cuando se inicia un nuevo stream

        current_time = time.time()
        time_diff = current_time - self.start_time
        time_diff_str = f"{time_diff:.2f}"
        self.cVista.cronometroGrabacion.setText(time_diff_str + ' s ')

    def calAutomatica(self):                        # Funcion de calibracion
        self.stream.start_stream()
        time.sleep(3.0)
        self.stream.stop_stream()
        NZ=self.cModel.getNivelesZ('P')
        cal = NZ[-1]-93.97 # ultimo valor de la adquisicion Pico retado 20*log10(0.00002)
        self.cModel.setCalibracionAutomatica(cal)
        print(cal)