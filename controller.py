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
        self.RATE = 44100  # Agregar RATE para compatibilidad con grabacionSAMNS
        self.c = 0  # Contador para el callback
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
        print(f"DEBUG: Función graficar llamada")
        print(f"DEBUG: btnTiempo.isChecked(): {self.cVista.btnTiempo.isChecked()}")
        print(f"DEBUG: btnFrecuencia.isChecked(): {self.cVista.btnFrecuencia.isChecked()}")
        print(f"DEBUG: btnNivel.isChecked(): {self.cVista.btnNivel.isChecked()}")
        
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
            print("DEBUG: Entrando en sección de nivel")
            # Nivel - Crear eje de tiempo real basado en la frecuencia de muestreo
            # Obtener datos del modelo
            (dataVectorPicoZ, dataVectorInstZ, dataVectorFastZ, dataVectorSlowZ) = self.cModel.getNivelesZ()
            (dataVectorPicoC, dataVectorInstC, dataVectorFastC, dataVectorSlowC) = self.cModel.getNivelesC()
            (dataVectorPicoA, dataVectorInstA, dataVectorFastA, dataVectorSlowA) = self.cModel.getNivelesA()
            
            print(f"DEBUG: Datos obtenidos - Z: {len(dataVectorPicoZ)}, C: {len(dataVectorPicoC)}, A: {len(dataVectorPicoA)}")
            
            # Crear eje de tiempo real sincronizado
            # Usar el tiempo de inicio real pero con intervalos consistentes
            try:
                # Obtener el tiempo real transcurrido desde el inicio
                if hasattr(self.cModel, 'start_time') and self.cModel.start_time is not None:
                    elapsed_real_time = time.time() - self.cModel.start_time
                    # Calcular el intervalo de tiempo promedio por muestra de nivel
                    if len(dataVectorPicoZ) > 1:
                        time_interval = elapsed_real_time / len(dataVectorPicoZ)
                        timeNivelData = np.arange(len(dataVectorPicoZ)) * time_interval
                    else:
                        timeNivelData = np.array([elapsed_real_time])
                else:
                    # Fallback al método basado en chunks
                    chunk_duration = self.cModel.chunk / self.cModel.rate
                    timeNivelData = np.arange(len(dataVectorPicoZ)) * chunk_duration
                    
            except Exception as e:
                print(f"DEBUG: Error en cálculo de tiempo: {e}")
                # Fallback al método anterior si hay error
                chunk_duration = self.cModel.chunk / self.cModel.rate
                timeNivelData = np.arange(len(dataVectorPicoZ)) * chunk_duration
        
            print(f"DEBUG: Tiempo real usado - {len(timeNivelData)} puntos, rango: {timeNivelData[0]:.2f}s - {timeNivelData[-1]:.2f}s")
            
            # Solo limpiar los plots que no se van a usar (comentado temporalmente para debug)
            # if not self.cVista.cbNivPicoZ.isChecked():
            #     self.cVista.ptNivZPico.clear()
            # if not self.cVista.cbNivInstZ.isChecked():
            #     self.cVista.ptNivZInst.clear()
            # if not self.cVista.cbNivFastZ.isChecked():
            #     self.cVista.ptNivZFast.clear()
            # if not self.cVista.cbNivSlowZ.isChecked():
            #     self.cVista.ptNivZSlow.clear()
            # if not self.cVista.cbNivPicoC.isChecked():
            #     self.cVista.ptNivCPico.clear()
            # if not self.cVista.cbNivInstC.isChecked():
            #     self.cVista.ptNivCInst.clear()
            # if not self.cVista.cbNivFastC.isChecked():
            #     self.cVista.ptNivCFast.clear()
            # if not self.cVista.cbNivSlowC.isChecked():
            #     self.cVista.ptNivCSlow.clear()
            # if not self.cVista.cbNivPicoA.isChecked():
            #     self.cVista.ptNivAPico.clear()
            # if not self.cVista.cbNivInstA.isChecked():
            #     self.cVista.ptNivAInst.clear()
            # if not self.cVista.cbNivFastA.isChecked():
            #     self.cVista.ptNivAFast.clear()
            # if not self.cVista.cbNivSlowA.isChecked():
            #     self.cVista.ptNivASlow.clear()
            
            # Solo graficar si hay datos
            if len(timeNivelData) > 0:
                print(f"DEBUG: Hay {len(timeNivelData)} puntos de tiempo")
                print(f"DEBUG: Checkboxes Z - Pico: {self.cVista.cbNivPicoZ.isChecked()}, Inst: {self.cVista.cbNivInstZ.isChecked()}, Fast: {self.cVista.cbNivFastZ.isChecked()}, Slow: {self.cVista.cbNivSlowZ.isChecked()}")
                print(f"DEBUG: Datos Z - Pico: {len(dataVectorPicoZ)}, Inst: {len(dataVectorInstZ)}, Fast: {len(dataVectorFastZ)}, Slow: {len(dataVectorSlowZ)}")
                if len(dataVectorFastZ) > 0:
                    print(f"DEBUG: Valores Fast Z: {dataVectorFastZ}")
                if len(dataVectorSlowZ) > 0:
                    print(f"DEBUG: Valores Slow Z: {dataVectorSlowZ}")
                
                # Ajustar el rango del eje X automáticamente
                max_time = timeNivelData[-1] if len(timeNivelData) > 0 else 10
                self.cVista.waveform1.setXRange(0, max_time + 1, padding=0)
                
                # Ajustar el rango del eje Y automáticamente basado en los datos
                all_data = []
                if self.cVista.cbNivPicoZ.isChecked() and len(dataVectorPicoZ) > 0:
                    all_data.extend(dataVectorPicoZ)
                if self.cVista.cbNivInstZ.isChecked() and len(dataVectorInstZ) > 0:
                    all_data.extend(dataVectorInstZ)
                if self.cVista.cbNivFastZ.isChecked() and len(dataVectorFastZ) > 0:
                    all_data.extend(dataVectorFastZ)
                if self.cVista.cbNivSlowZ.isChecked() and len(dataVectorSlowZ) > 0:
                    all_data.extend(dataVectorSlowZ)
                
                if len(all_data) > 0:
                    min_db = min(all_data)
                    max_db = max(all_data)
                    # Agregar margen de 5 dB arriba y abajo
                    y_min = max(-150, min_db - 5)
                    y_max = min(0, max_db + 5)
                    self.cVista.waveform1.setYRange(y_min, y_max, padding=0)
                
                # Vista de filtro Z
                if self.cVista.cbNivPicoZ.isChecked() and len(dataVectorPicoZ) > 0:             
                    self.cVista.ptNivZPico.setData(timeNivelData, dataVectorPicoZ)
                if self.cVista.cbNivInstZ.isChecked() and len(dataVectorInstZ) > 0:
                    self.cVista.ptNivZInst.setData(timeNivelData, dataVectorInstZ)
                if self.cVista.cbNivFastZ.isChecked() and len(dataVectorFastZ) > 0:
                    print(f"DEBUG FAST Z: Graficando {len(timeNivelData)} puntos, datos: {dataVectorFastZ}")
                    print(f"DEBUG FAST Z: Plot object: {self.cVista.ptNivZFast}")
                    self.cVista.ptNivZFast.setData(timeNivelData, dataVectorFastZ)
                    print(f"DEBUG FAST Z: setData llamado")
                    # Forzar actualización del gráfico
                    self.cVista.waveform1.replot()
                    print(f"DEBUG FAST Z: replot llamado")
                if self.cVista.cbNivSlowZ.isChecked() and len(dataVectorSlowZ) > 0:
                    print(f"DEBUG SLOW Z: Graficando {len(timeNivelData)} puntos, datos: {dataVectorSlowZ}")
                    print(f"DEBUG SLOW Z: Plot object: {self.cVista.ptNivZSlow}")
                    self.cVista.ptNivZSlow.setData(timeNivelData, dataVectorSlowZ)
                    print(f"DEBUG SLOW Z: setData llamado")
                    # Forzar actualización del gráfico
                    self.cVista.waveform1.replot()
                    print(f"DEBUG SLOW Z: replot llamado")
                else:
                    print(f"DEBUG SLOW Z: NO se grafica - checkbox: {self.cVista.cbNivSlowZ.isChecked()}, datos: {len(dataVectorSlowZ)}")

                # Vista de filtro C
                if self.cVista.cbNivPicoC.isChecked() and len(dataVectorPicoC) > 0:
                    self.cVista.ptNivCPico.setData(timeNivelData, dataVectorPicoC)
                if self.cVista.cbNivInstC.isChecked() and len(dataVectorInstC) > 0:
                    self.cVista.ptNivCInst.setData(timeNivelData, dataVectorInstC)
                if self.cVista.cbNivFastC.isChecked() and len(dataVectorFastC) > 0:
                    self.cVista.ptNivCFast.setData(timeNivelData, dataVectorFastC)
                if self.cVista.cbNivSlowC.isChecked() and len(dataVectorSlowC) > 0:
                    self.cVista.ptNivCSlow.setData(timeNivelData, dataVectorSlowC)

                # Vista de filtro A
                if self.cVista.cbNivPicoA.isChecked() and len(dataVectorPicoA) > 0:
                    self.cVista.ptNivAPico.setData(timeNivelData, dataVectorPicoA)
                if self.cVista.cbNivInstA.isChecked() and len(dataVectorInstA) > 0:
                    self.cVista.ptNivAInst.setData(timeNivelData, dataVectorInstA)
                if self.cVista.cbNivFastA.isChecked() and len(dataVectorFastA) > 0:
                    self.cVista.ptNivAFast.setData(timeNivelData, dataVectorFastA)
                if self.cVista.cbNivSlowA.isChecked() and len(dataVectorSlowA) > 0:
                    self.cVista.ptNivASlow.setData(timeNivelData, dataVectorSlowA)

    def get_nivel_data(self):
        """Obtiene los datos de nivel del modelo y los prepara para la vista"""
        # Obtener datos del modelo
        (pico_z, inst_z, fast_z, slow_z) = self.cModel.getNivelesZ()
        (pico_c, inst_c, fast_c, slow_c) = self.cModel.getNivelesC()
        (pico_a, inst_a, fast_a, slow_a) = self.cModel.getNivelesA()
        
        # Crear eje de tiempo usando el tiempo real transcurrido
        try:
            # Obtener el tiempo real transcurrido desde el inicio
            if hasattr(self.cModel, 'start_time') and self.cModel.start_time is not None:
                elapsed_real_time = time.time() - self.cModel.start_time
                # Calcular el intervalo de tiempo promedio por muestra de nivel
                if len(pico_z) > 1:
                    time_interval = elapsed_real_time / len(pico_z)
                    tiempos = np.arange(len(pico_z)) * time_interval
                else:
                    tiempos = np.array([elapsed_real_time])
            else:
                # Fallback al método basado en chunks
                chunk_duration = self.cModel.chunk / self.cModel.rate
                tiempos = np.arange(len(pico_z)) * chunk_duration
        except Exception as e:
            print(f"DEBUG: Error en cálculo de tiempo en get_nivel_data: {e}")
            # Fallback al método anterior si hay error
            chunk_duration = self.cModel.chunk / self.cModel.rate
            tiempos = np.arange(len(pico_z)) * chunk_duration
        
        # Organizar datos en estructura para la vista
        niveles_z = {
            'pico': pico_z,
            'inst': inst_z,
            'fast': fast_z,
            'slow': slow_z
        }
        
        niveles_c = {
            'pico': pico_c,
            'inst': inst_c,
            'fast': fast_c,
            'slow': slow_c
        }
        
        niveles_a = {
            'pico': pico_a,
            'inst': inst_a,
            'fast': fast_a,
            'slow': slow_a
        }
    
        return tiempos, niveles_z, niveles_c, niveles_a

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
        # Procesar los datos de audio
        self.grabar()
        return (self.wf_data.tobytes(), pyaudio.paContinue)

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
            # Resetear los datos de nivel en el modelo
            self.cModel.setNivelesZ(0, 0, 0, 0, mode='r')
            self.cModel.setNivelesC(0, 0, 0, 0, mode='r')
            self.cModel.setNivelesA(0, 0, 0, 0, mode='r')
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
                    # Calcular FFT
                    fft_freqs, fft_db = self.cModel.calculate_fft(current_data1)
                    self.cVista.update_plot(1, current_data1, all_data1, norm_current1, norm_all1, db1, self.device1_name, times1, fft_freqs, fft_db)
                    
                    # Procesar datos para el gráfico de nivel si está activo
                    if self.cVista.btnNivel.isChecked():
                        # Convertir los datos de audio int16 a float32 normalizados para compatibilidad con grabacionSAMNS
                        # Los datos vienen como int16 (-32768 a 32767), necesitamos normalizarlos a float32 (-1 a 1)
                        normalized_data = current_data1.astype(np.float32) / 32767.0
                        self.wf_data = normalized_data
                        self.grabar()
                        
            except Exception as e:
                print(f"Error al actualizar dispositivo 1: {e}")
                self.device_active = False
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