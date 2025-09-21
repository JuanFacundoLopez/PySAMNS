from model import modelo
from view import vista
from ventanas.calibracionWin import CalibracionWin
from ventanas.generadorWin import GeneradorWin
from ventanas.configDispWin import ConfigDispWin
from ventanas.configuracionWin import ConfiguracionWin
from ventanas.programarWin import ProgramarWin
from ventanas.grabacionesWin import GrabacionesWin

from db import leer_todas_grabaciones, actualizar_estado
from datetime import datetime, timedelta
import os

from PyQt5.QtWidgets import QFileDialog
from pyqtgraph.Qt import QtCore
import struct
import sounddevice as sd
import soundfile as sf
# from pyaudio import PyAudio, paInt16
import pyaudio
# from scipy.fftpack import fft

import numpy as np 

# import sys
# sys.path.append('./funciones')

from funciones.grabacionSAMNS import grabacion
from funciones.calibracionSAMNS import compute_thd
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
        self.cCalWin = CalibracionWin(self,self.cVista)         # Ventana de calibración

        self.ventanas_abiertas = {
            "calibracion": None,
            "generador": None,
            "config_disp": None,
            "configuracion": None,
            "programar": None,
            "grabaciones": None,
        }
        self.signal_frec_muestreo = None
        self.frecuencia_muestreo_actual = 8000
        
        self.timer_grabacion_automatica = QtCore.QTimer()
        self.timer_grabacion_automatica.timeout.connect(self.verificar_grabaciones_programadas)
        self.timer_grabacion_automatica.start(10000)  # cada 10 segundos

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_view)
        self.msCounter = 0
        self.start_time = None  # Add start time tracking
        
        # Arrays para mantener el seguimiento de tiempos de niveles estadísticos
        self.stat_times_z = np.array([])
        self.stat_times_c = np.array([])
        self.stat_times_a = np.array([])
        self.last_stat_update_time = 0
        self.stat_update_interval = 0.1  # Actualizar estadísticas cada 100ms para una visualización más suave
        self.stat_window_size = 10  # Número de puntos para el promedio móvil
        self.stat_window = []  # Ventana para el promedio móvil
        
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
        #self.wf_data = np.array(0)*2

        
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
        SignalfileName = QFileDialog.getOpenFileName( 
                None,
                "Seleccionar archivo de audio", 
                "", 
                "Archivos de audio (*.wav);;Todos los archivos (*)"
            )
        
        # Read wav file
        Fs, x = wavread(SignalfileName[0])
        #print("Fs:", Fs)
        #print("Shape de x:", x.shape)
        #print("Primeros datos:", x[:10])
        #print("maxX:", maxX)
        #print("signaldata:", signaldata[:10])
        if x.ndim > 1:
            x = x.mean(axis=1)  # Convertir a mono si es estéreo
        maxX = np.max(np.abs(x))
        if maxX == 0:
            signaldata = x  # Evitar división por cero
        else:
            signaldata = x / maxX

        if Fs > 44000: # validacion de la entrada de datos
            self.cModel.setFs(Fs) # Guardo en base de datos/modelo
            #print("Fs fue correctamente cargado")
        else:
            print("Fs es invalido " + str(Fs))
        if len(signaldata) > 2:# validacion de la entrada de datos
            self.cModel.setSignalData(signaldata)  # Guardo en base de datos/modelo      
            #print("Datos guardados en el modelo:", self.cModel.getSignalData()[:10])
            #print("signaldata fue correctamente cargado")
        else:
            print("signaldata es invalido")

        # Hago una peticion a modelo y mando informacion a la vista 
        # para que los datos levantados sean cargados
        self.graficar()

    def probar_frecuencias_entrada(self, device_index, lista_frecuencias, canales=1):
        from funciones.consDisp import probar_frecuencias_entrada
        return probar_frecuencias_entrada(device_index, lista_frecuencias, canales)

    def graficar(self):                             # Funcion para graficar las señales
        #print(f"DEBUG: Función graficar llamada")
        #print(f"DEBUG: btnTiempo.isChecked(): {self.cVista.btnTiempo.isChecked()}")
        #print(f"DEBUG: btnFrecuencia.isChecked(): {self.cVista.btnFrecuencia.isChecked()}")
        #print(f"DEBUG: btnNivel.isChecked(): {self.cVista.btnNivel.isChecked()}")
        
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
            #print("DEBUG: Entrando en sección de nivel")
            # Nivel - Crear eje de tiempo real basado en la frecuencia de muestreo
            # Obtener datos del modelo
            (dataVectorPicoZ, dataVectorInstZ, dataVectorFastZ, dataVectorSlowZ) = self.cModel.getNivelesZ()
            (dataVectorPicoC, dataVectorInstC, dataVectorFastC, dataVectorSlowC) = self.cModel.getNivelesC()
            (dataVectorPicoA, dataVectorInstA, dataVectorFastA, dataVectorSlowA) = self.cModel.getNivelesA()
            
            #print(f"DEBUG: Datos obtenidos - Z: {len(dataVectorPicoZ)}, C: {len(dataVectorPicoC)}, A: {len(dataVectorPicoA)}")
            
            # Crear eje de tiempo real sincronizado
            # Usar el tiempo de inicio real pero con intervalos consistentes
            timeNivelData = np.array([])  # Initialize timeNivelData as empty array
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
            except Exception as e:
                #print(f"DEBUG: Error en cálculo de tiempo: {e}")
                # Fallback al método basado en chunks
                chunk_duration = self.cModel.chunk / self.cModel.rate
                timeNivelData = np.arange(len(dataVectorPicoZ)) * chunk_duration
        
            #print(f"DEBUG: Tiempo real usado - {len(timeNivelData)} puntos, rango: {timeNivelData[0]:.2f}s - {timeNivelData[-1]:.2f}s" if len(timeNivelData) > 0 else "DEBUG: No hay datos de tiempo")
            
            # Solo graficar si hay datos
            if len(timeNivelData) > 0:
                #print(f"DEBUG: Hay {len(timeNivelData)} puntos de tiempo")
                #print(f"DEBUG: Checkboxes Z - Pico: {self.cVista.cbNivPicoZ.isChecked()}, Inst: {self.cVista.cbNivInstZ.isChecked()}, Fast: {self.cVista.cbNivFastZ.isChecked()}, Slow: {self.cVista.cbNivSlowZ.isChecked()}")
                #print(f"DEBUG: Datos Z - Pico: {len(dataVectorPicoZ)}, Inst: {len(dataVectorInstZ)}, Fast: {len(dataVectorFastZ)}, Slow: {len(dataVectorSlowZ)}")
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
                    # Agregar margen de 5 dB arriba y abajo para el nuevo rango
                    y_min = min_db - 5
                    y_max = max_db + 5
                    self.cVista.waveform1.setYRange(y_min, y_max, padding=0)
                
                # Vista de filtro Z
                if self.cVista.cbNivPicoZ.isChecked() and len(dataVectorPicoZ) > 0:             
                    self.cVista.ptNivZPico.setData(timeNivelData, dataVectorPicoZ)
                if self.cVista.cbNivInstZ.isChecked() and len(dataVectorInstZ) > 0:
                    self.cVista.ptNivZInst.setData(timeNivelData, dataVectorInstZ)
                if self.cVista.cbNivFastZ.isChecked() and len(dataVectorFastZ) > 0:
                    #print(f"DEBUG FAST Z: Graficando {len(timeNivelData)} puntos, datos: {dataVectorFastZ}")
                    #print(f"DEBUG FAST Z: Plot object: {self.cVista.ptNivZFast}")
                    self.cVista.ptNivZFast.setData(timeNivelData, dataVectorFastZ)
                    #print(f"DEBUG FAST Z: setData llamado")
                    # Forzar actualización del gráfico
                    self.cVista.waveform1.replot()
                    #print(f"DEBUG FAST Z: replot llamado")
                if self.cVista.cbNivSlowZ.isChecked() and len(dataVectorSlowZ) > 0:
                    #print(f"DEBUG SLOW Z: Graficando {len(timeNivelData)} puntos, datos: {dataVectorSlowZ}")
                    #print(f"DEBUG SLOW Z: Plot object: {self.cVista.ptNivZSlow}")
                    self.cVista.ptNivZSlow.setData(timeNivelData, dataVectorSlowZ)
                    #print(f"DEBUG SLOW Z: setData llamado")
                    # Forzar actualización del gráfico
                    self.cVista.waveform1.replot()
                    #print(f"DEBUG SLOW Z: replot llamado")
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
        
        # Obtener el tiempo real transcurrido desde el inicio
        current_time = time.time()
        if not hasattr(self, 'start_time') or self.start_time is None:
            self.start_time = current_time
            elapsed_real_time = 0.0
        else:
            elapsed_real_time = current_time - self.start_time
        
        # Calcular estadísticas periódicamente según el intervalo definido
        current_time = time.time()
        if current_time - self.last_stat_update_time >= self.stat_update_interval:
            stats = self.cModel.calculate_leq_and_percentiles()
            
            # Agregar a la ventana de promediado
            self.stat_window.append(stats)
            if len(self.stat_window) > self.stat_window_size:
                self.stat_window.pop(0)
            
            # Calcular promedio de la ventana
            if self.stat_window:
                avg_stats = {}
                for key in stats.keys():
                    values = [d[key] for d in self.stat_window if key in d]
                    if values:
                        avg_stats[key] = sum(values) / len(values)
                
                # Actualizar el modelo con los valores promediados
                self.cModel.update_statistical_levels_history(avg_stats)
                self.last_stat_update_time = current_time
            
            # Actualizar los tiempos de las estadísticas
            stat_count = len(self.cModel.recorderLeqZ)
            if stat_count > 0:
                self.stat_times_z = np.linspace(0, elapsed_real_time, stat_count)
            
            stat_count = len(self.cModel.recorderLeqC)
            if stat_count > 0:
                self.stat_times_c = np.linspace(0, elapsed_real_time, stat_count)
                
            stat_count = len(self.cModel.recorderLeqA)
            if stat_count > 0:
                self.stat_times_a = np.linspace(0, elapsed_real_time, stat_count)
        
        # Crear eje de tiempo usando el tiempo real transcurrido
        try:
            # Calcular el intervalo de tiempo promedio por muestra de nivel
            if len(pico_z) > 1:
                time_interval = elapsed_real_time / len(pico_z)
                tiempos = np.arange(len(pico_z)) * time_interval
            else:
                tiempos = np.array([elapsed_real_time])
        except Exception as e:
            #print(f"DEBUG: Error en cálculo de tiempo en get_nivel_data: {e}")
            # Fallback al método anterior si hay error
            chunk_duration = self.cModel.chunk / self.cModel.rate
            tiempos = np.arange(len(pico_z)) * chunk_duration
        
        # Función auxiliar para crear estructura de datos estadísticos con tiempos
        def create_stat_data(values, times):
            if len(values) == 0:
                return {}
            return {
                'data': np.array(values),
                'times': np.array(times[:len(values)])  # Asegurar que los tiempos coincidan con los datos
            }
            
        # Organizar datos en estructura para la vista
        niveles_z = {
            'pico': pico_z,
            'inst': inst_z,
            'fast': fast_z,
            'slow': slow_z,
            # Estructura de datos estadísticos con sus propios tiempos
            'leq': create_stat_data(self.cModel.recorderLeqZ, self.stat_times_z),
            'l01': create_stat_data(self.cModel.recorderL01Z, self.stat_times_z),
            'l10': create_stat_data(self.cModel.recorderL10Z, self.stat_times_z),
            'l50': create_stat_data(self.cModel.recorderL50Z, self.stat_times_z),
            'l90': create_stat_data(self.cModel.recorderL90Z, self.stat_times_z),
            'l99': create_stat_data(self.cModel.recorderL99Z, self.stat_times_z)
        }
        
        niveles_c = {
            'pico': pico_c,
            'inst': inst_c,
            'fast': fast_c,
            'slow': slow_c,
            # Estructura de datos estadísticos con sus propios tiempos
            'leq': create_stat_data(self.cModel.recorderLeqC, self.stat_times_c),
            'l01': create_stat_data(self.cModel.recorderL01C, self.stat_times_c),
            'l10': create_stat_data(self.cModel.recorderL10C, self.stat_times_c),
            'l50': create_stat_data(self.cModel.recorderL50C, self.stat_times_c),
            'l90': create_stat_data(self.cModel.recorderL90C, self.stat_times_c),
            'l99': create_stat_data(self.cModel.recorderL99C, self.stat_times_c)
        }
        
        niveles_a = {
            'pico': pico_a,
            'inst': inst_a,
            'fast': fast_a,
            'slow': slow_a,
            # Estructura de datos estadísticos con sus propios tiempos
            'leq': create_stat_data(self.cModel.recorderLeqA, self.stat_times_a),
            'l01': create_stat_data(self.cModel.recorderL01A, self.stat_times_a),
            'l10': create_stat_data(self.cModel.recorderL10A, self.stat_times_a),
            'l50': create_stat_data(self.cModel.recorderL50A, self.stat_times_a),
            'l90': create_stat_data(self.cModel.recorderL90A, self.stat_times_a),
            'l99': create_stat_data(self.cModel.recorderL99A, self.stat_times_a)
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

    def reset_all_data(self):
        """Detiene los temporizadores, los flujos y restablece todos los datos en el controlador, el modelo y la vista."""
        # Detener procesos
        self.timer.stop()
        if hasattr(self.cModel, 'stream') and self.cModel.stream.is_active():
            self.cModel.stream.stop_stream()
        
        self.device_active = False

        # Restablecer datos del controlador
        self.setGainZero()
        self.start_time = None
        self.msCounter = 0
        self.last_stat_update_time = 0
        self.stat_times_z = np.array([])
        self.stat_times_c = np.array([])
        self.stat_times_a = np.array([])

        # Restablecer datos del modelo
        self.cModel.setNivelesZ(mode='r')
        self.cModel.setNivelesC(mode='r')
        self.cModel.setNivelesA(mode='r')
        self.cModel.buffer = []
        self.cModel.normalized_all = []
        self.cModel.times = []
        self.cModel.start_time = None
        
        # Reset statistical levels
        self.cModel.recorderLeqZ = np.empty(0)
        self.cModel.recorderL01Z = np.empty(0)
        self.cModel.recorderL10Z = np.empty(0)
        self.cModel.recorderL50Z = np.empty(0)
        self.cModel.recorderL90Z = np.empty(0)
        self.cModel.recorderL99Z = np.empty(0)
        
        self.cModel.recorderLeqC = np.empty(0)
        self.cModel.recorderL01C = np.empty(0)
        self.cModel.recorderL10C = np.empty(0)
        self.cModel.recorderL50C = np.empty(0)
        self.cModel.recorderL90C = np.empty(0)
        self.cModel.recorderL99C = np.empty(0)
        
        self.cModel.recorderLeqA = np.empty(0)
        self.cModel.recorderL01A = np.empty(0)
        self.cModel.recorderL10A = np.empty(0)
        self.cModel.recorderL50A = np.empty(0)
        self.cModel.recorderL90A = np.empty(0)
        self.cModel.recorderL99A = np.empty(0)

        # Actualizar la vista
        self.cVista.cronometroGrabacion.setText("0:00 s")
        self.graficar()
        
    def dalePlay(self):                            # Comunicacion con la Vista
        if self.cVista.btngbr.isChecked() == False:
            # Acción de DETENER: detiene todo y resetea.
            self.reset_all_data()
        else:
            # Acción de INICIAR: resetea todo y comienza de nuevo.
            self.reset_all_data()
            self.timer.start(30) 
            self.device_active = True
            self.cModel.stream.start_stream()

    def update_view(self):                           # Cronometro
         # Actualizar dispositivo 1 si está activo
        if self.device_active:
            try:
                # Get audio data from the model
                audio_data = self.cModel.get_audio_data()
                
                # Check if we got valid data
                if audio_data and len(audio_data) >= 7:  # Ensure we have all expected return values
                    current_data1, all_data1, norm_current1, norm_all1, times1, fft_freqs1, fft_db1 = audio_data
                    
                    if len(current_data1) > 0:  # Verify we have data to process
                        # Convertir datos a float32 normalizado (-1 a 1)
                        normalized_data = current_data1.astype(np.float32) / (32767.0/2)
                        
                        # Procesar con los filtros de ponderación
                        self.cModel.setSignalData(normalized_data)
                        
                        # Calcular FFT
                        fft_freqs, fft_db = self.cModel.calculate_fft(current_data1)
                        
                        # Actualizar la vista
                        self.cVista.update_plot(1, current_data1, all_data1, norm_current1, norm_all1, 
                                             self.device1_name, times1, fft_freqs, fft_db)
                        
                        # Procesar datos para el gráfico de nivel si está activo
                        if self.cVista.btnNivel.isChecked():
                            self.wf_data = normalized_data
                            if len(self.wf_data) > 0:
                                self.grabar()
                            
            except Exception as e:
                #print(f"Error al actualizar dispositivo 1: {e}")
                self.device_active = False
        else:
            print("No se inicio grabacion")

        if self.start_time is None:
            self.start_time = time.time()
            self.times = []  # Resetear el tiempo cuando se inicia un nuevo stream

        current_time = time.time()
        time_diff = current_time - self.start_time
        time_diff_str = f"{time_diff:.2f}"
        self.cVista.cronometroGrabacion.setText(time_diff_str + ' s ')

    def calRelativaAFondoDeEscala(self):
        """
        Calibración relativa a fondo de escala:
        Genera tonos de 1kHz variando amplitud de 0.1 a 1.0,
        mide THD en la captura y se detiene cuando THD > 1%.
        """
        import numpy as np
        import pyaudio
        import time

        # --- 1. Verificación de dispositivos ---
        try:
            input_device_index = self.cModel.getDispositivoActual()
            output_device_index = self.cModel.getDispositivoSalidaActual()
            if output_device_index is None:
                QMessageBox.warning(
                    self.ventanas_abiertas["calibracion"],
                    "Error de Dispositivo",
                    "No se ha seleccionado un dispositivo de salida."
                )
                return False
        except Exception as e:
            QMessageBox.warning(
                self.ventanas_abiertas["calibracion"],
                "Error de Dispositivo",
                f"Error al obtener dispositivos: {str(e)}"
            )
            return False

        # --- 2. Parámetros ---
        fs = self.RATE
        duracion = 2.0  # segundos por paso
        amplitudes = np.arange(0.1, 1, 0.1)
        freq = 1000
        umbral_thd = 1.0  # 1 %
        frames_per_buffer = 1024

        # --- 3. Inicializar PyAudio ---
        p = pyaudio.PyAudio()
        try:
            output_stream = p.open(format=pyaudio.paFloat32, channels=1, rate=fs,
                                output=True, output_device_index=output_device_index,
                                frames_per_buffer=frames_per_buffer)
        except Exception as e:
            QMessageBox.warning(
                self.ventanas_abiertas["calibracion"],
                "Error de Audio",
                f"No se pudo abrir el dispositivo de salida: {str(e)}"
            )
            return False

        try:
            input_stream = p.open(format=pyaudio.paFloat32, channels=1, rate=fs,
                                input=True, input_device_index=input_device_index,
                                frames_per_buffer=frames_per_buffer)
        except Exception as e:
            output_stream.close()
            QMessageBox.warning(
                self.ventanas_abiertas["calibracion"],
                "Error de Audio",
                f"No se pudo abrir el dispositivo de entrada: {str(e)}"
            )
            return False

        # --- 4. Variables de calibración ---
        ultima_amp_valida, ultimo_thd, ultimo_nivel = None, None, None

        # --- 5. Función auxiliar: calcular THD ---
        def compute_thd(signal, fs, f0=1000, harmonics=10, side_bins=1):
            """
            Muestra fundamental, armónicos y THD (%). No devuelve nada.
            - Ventana Hann con normalización coherente.
            - Integra ±side_bins alrededor de cada armónico.
            """
            n = len(signal)
            if n == 0:
                print("Señal vacía."); return
            window = np.hanning(n)
            coherent_gain = np.sum(window) / n
            S = np.fft.rfft(signal * window)
            freqs = np.fft.rfftfreq(n, 1.0/fs)

            # Magnitud normalizada a amplitud pico ≈ amplitud temporal de la senoidal
            mag = np.abs(S) * (2.0 / (n * coherent_gain))  # equiv. a 2/sum(window)

            # Fundamental (bin más cercano a f0)
            idx_f0 = int(np.argmin(np.abs(freqs - f0)))
            # Integramos ±side_bins alrededor del pico
            lo = max(0, idx_f0 - side_bins); hi = min(len(mag)-1, idx_f0 + side_bins)
            fund_amp = np.sqrt(np.sum(mag[lo:hi+1]**2))
            fund_freq = freqs[idx_f0]
            fund_amp = max(fund_amp, 1e-15)  # evitar div/0

            #print(f"Fundamental: {fund_freq:.2f} Hz -> {fund_amp:.6f}")

            harm_amps = []
            for h in range(2, harmonics+1):
                target = h * f0
                if target >= fs/2:
                    break
                idx = int(np.argmin(np.abs(freqs - target)))
                lo = max(0, idx - side_bins); hi = min(len(mag)-1, idx + side_bins)
                a = np.sqrt(np.sum(mag[lo:hi+1]**2))
                f = freqs[idx]
                dBc = 20.0*np.log10(max(a,1e-15)/fund_amp)
                harm_amps.append(a)
                #print(f"Armónico {h}: {f:.2f} Hz -> {a:.6f}  ({dBc:.1f} dBc)")

            if harm_amps:
                thd = np.sqrt(np.sum(np.array(harm_amps)**2)) / fund_amp
            else:
                thd = 0.0
            #print(f"THD: {thd*100:.4f} %\n")
            return thd*100

        # --- 6. Bucle de calibración ---
        try:
            for amp in amplitudes:
                # Generar señal
                t = np.linspace(0, duracion, int(fs*duracion), endpoint=False)
                signal = (amp * np.sin(2*np.pi*freq*t)).astype(np.float32)

                # Reproducir
                output_stream.write(signal.tobytes())

                # Capturar
                frames = []
                for _ in range(int(fs*duracion/frames_per_buffer)):
                    data = input_stream.read(frames_per_buffer, exception_on_overflow=False)
                    frames.append(np.frombuffer(data, dtype=np.float32))
                capturado = np.concatenate(frames)

                # Evitar transitorios
                #capturado = capturado[len(capturado)//10:]

                # Calcular métricas
                thd = compute_thd(capturado, fs, f0=freq)
                rms = np.sqrt(np.mean(capturado**2))
                nivel_dbfs = 20*np.log10(rms) if rms > 0 else -np.inf

                #print(f"Amplitud: {amp:.1f}, THD: {thd:.3f}%, Nivel: {nivel_dbfs:.2f} dBFS")

                if thd < umbral_thd:
                    ultima_amp_valida, ultimo_thd, ultimo_nivel = amp, thd, nivel_dbfs
                else:
                    #print("THD superó el 1%, deteniendo calibración.")
                    break

                time.sleep(0.2)

        except Exception as e:
            #print(f"Error durante calibración: {e}")
            return False

        finally:
            output_stream.stop_stream()
            output_stream.close()
            input_stream.stop_stream()
            input_stream.close()
            p.terminate()

        # --- 7. Resultados ---
        if ultima_amp_valida is not None:
            cal_db = 20*np.log10(max(1e-6, ultima_amp_valida))
            self.cModel.setCalibracionAutomatica(cal_db)
            self.cModel.set_calibracion_offset_spl(cal_db)

            self.ventanas_abiertas["calibracion"].txtValorRef.setText(f"{cal_db:.2f}")
            QMessageBox.information(
                self.ventanas_abiertas["calibracion"],
                "Calibración Exitosa",
                f"Amplitud: {ultima_amp_valida:.2f}\n"
                f"THD: {ultimo_thd:.3f}%\n"
                f"Nivel: {ultimo_nivel:.2f} dBFS\n"
                f"Offset: {cal_db:.2f} dB"
            )
            return True
        else:
            QMessageBox.warning(
                self.ventanas_abiertas["calibracion"],
                "Error de Calibración",
                "No se pudo completar la calibración. Verifique la conexión del micrófono."
            )
            return False

    def establecer_ruta_archivo_calibracion(self, ruta):
        """Guarda la ruta del archivo de calibración en el modelo."""
        self.cModel.set_ruta_archivo_calibracion(ruta)
        #print(f"Ruta de archivo de calibración establecida en: {ruta}")

    def reproducir_audio_calibracion(self):
        """Lee y reproduce el archivo de audio de referencia."""
        try:
            ruta = self.cModel.get_ruta_archivo_calibracion()
            if not ruta:
                QMessageBox.warning(self.ventanas_abiertas["calibracion"], "Archivo no encontrado", "Por favor, seleccione un archivo de referencia .wav primero.")
                return

            # Leer el archivo de audio
            data, samplerate = sf.read(ruta, dtype='float32')
            
            # Obtener dispositivo de salida
            output_device_index = self.cModel.getDispositivoSalidaActual()
            if output_device_index is None:
                QMessageBox.warning(self.ventanas_abiertas["calibracion"], "Error de Dispositivo", "No se ha seleccionado un dispositivo de salida.")
                return

            # Reproducir el audio
            sd.play(data, samplerate, device=output_device_index)
            QMessageBox.information(self.ventanas_abiertas["calibracion"], "Reproducción", f"Reproduciendo {ruta}...")

        except Exception as e:
            QMessageBox.critical(self.ventanas_abiertas["calibracion"], "Error de Reproducción", f"No se pudo reproducir el archivo de audio: {str(e)}")
            #print(f"Error en reproducir_audio_calibracion: {e}")

    def calFuenteReferenciaInterna(self):
        """
        Orquesta el proceso de calibración externa: mide el nivel de la señal de entrada 
        mientras se reproduce el tono de referencia y calcula el offset.
        """
        try:
            # 1. Obtener el nivel de referencia dBSPL del usuario
            ref_spl_text = self.cVista.calWin.txtValorRefExterna.text()
            if not ref_spl_text:
                QMessageBox.warning(self.ventanas_abiertas["calibracion"], "Entrada Inválida", "Por favor, ingrese un valor de referencia en dBSPL.")
                return False
            ref_spl = float(ref_spl_text)

            # 2. Iniciar una grabación corta para medir el nivel dBFS
            QMessageBox.information(self.ventanas_abiertas["calibracion"], "Medición en Curso", 
                                    "Se medirá el nivel de entrada durante 3 segundos.\n" 
                                    "Asegúrese de que su tono de referencia esté sonando y presione OK.")
            
            self.cModel.stream.start_stream()
            
            # Acumular datos durante unos segundos
            grabacion_data = []
            tiempo_inicio = time.time()
            while time.time() - tiempo_inicio < 3:  # Grabar por 3 segundos
                try:
                    audio_data = self.cModel.get_audio_data()
                    if audio_data and len(audio_data) >= 7:
                        current_data, _, _, _, _, _, _ = audio_data
                        if len(current_data) > 0:
                            grabacion_data.append(current_data.astype(np.float32) / (32767.0/2))
                except Exception as e:
                    print(f"Error al capturar audio: {e}")
                time.sleep(0.01) # Pequeña pausa

            self.cModel.stream.stop_stream()

            if not grabacion_data:
                QMessageBox.critical(self.ventanas_abiertas["calibracion"], "Error de Medición", "No se pudieron capturar datos de audio.")
                return False

            # Concatenar y procesar los datos grabados
            audio_completo = np.concatenate(grabacion_data)
            
            # 3. Calcular el nivel en dBFS
            # Usamos la función del modelo que calcula dB sobre datos normalizados
            medido_dbfs = self.cModel.calculate_db(audio_completo)
            
            # 4. Actualizar la interfaz con el valor medido
            self.cVista.lblNivelMedidoFS.setText(f"{medido_dbfs:.2f} dBFS")

            # 5. Calcular el offset
            offset = ref_spl - medido_dbfs
            
            # 6. Guardar el offset en el modelo
            self.cModel.set_calibracion_offset_spl(offset)
            
            # 7. Actualizar la interfaz con el offset
            self.cVista.lblFactorAjuste.setText(f"{offset:.2f} dB")

            QMessageBox.information(self.ventanas_abiertas["calibracion"], "Calibración Completa", 
                                   f"Calibración finalizada con éxito.\n\n"
                                   f"Nivel de Referencia: {ref_spl:.2f} dBSPL\n"
                                   f"Nivel Medido: {medido_dbfs:.2f} dBFS\n"
                                   f"Factor de Ajuste: {offset:.2f} dB")
            return True

        except ValueError:
            QMessageBox.warning(self.ventanas_abiertas["calibracion"], "Entrada Inválida", "El valor de referencia debe ser un número.")
            return False
        except Exception as e:
            QMessageBox.critical(self.ventanas_abiertas["calibracion"], "Error de Calibración", f"Ocurrió un error inesperado: {str(e)}")
            #print(f"Error en iniciar_calibracion_relativa: {e}")
            return False

    def calFuenteCalibracionExterna(self):
        try:
            valor_ref_str = self.ventanas_abiertas["calibracion"].txtValorRef.text()
            #print(f"DEBUG: Valor de referencia ingresado: '{valor_ref_str}'")
            valor_ref_str_cleaned = valor_ref_str.strip()
            if not valor_ref_str_cleaned:
                raise ValueError("El valor de referencia no puede estar vacío.")
            
            valor_para_float = valor_ref_str_cleaned.replace(',', '.')
            #print(f"DEBUG: Valor después de limpiar y reemplazar comas: '{valor_para_float}'")
            
            ref_level = float(valor_para_float)
            #print(f"DEBUG: Valor convertido a float exitosamente: {ref_level}")

        except (ValueError, AttributeError) as e:
            #print(f"DEBUG: Error al convertir a float. EXCEPCIÓN: {e}")
            QMessageBox.warning(self.ventanas_abiertas["calibracion"], "Error de Entrada", "Por favor, ingrese un valor de referencia numérico válido.")
            return

        # Obtener dispositivos de entrada y salida seleccionados
        try:
            input_device_index = self.cModel.getDispositivoActual()
            output_device_index = self.cModel.getDispositivoSalidaActual()
            
            if output_device_index is None:
                QMessageBox.warning(self.ventanas_abiertas["calibracion"], "Error de Dispositivo", "No se ha seleccionado un dispositivo de salida.")
                return
        except Exception as e:
            QMessageBox.warning(self.ventanas_abiertas["calibracion"], "Error de Dispositivo", f"Error al obtener dispositivos: {str(e)}")
            return

        # Parámetros de la señal
        frecuencia = 1000  # 1 kHz
        frecuencia_muestreo = self.RATE  # 44.1 kHz, estándar de audio
        duracion = 3  # 3 segundos
        amplitud = 0.8  # Amplitud normalizada (reducida para evitar distorsión)
        frames_per_buffer = 512

        # Generar el arreglo de tiempos
        t = np.linspace(0, duracion, int(frecuencia_muestreo * duracion), endpoint=False)

        # Generar la onda senoidal
        onda_senoidal = amplitud * np.sin(2 * np.pi * frecuencia * t)

        try:
            # Iniciar la captura de audio
            self.cModel.stream.start_stream()
            
            # Reproducir la onda con sounddevice (no bloqueante) para permitir captura concurrente
            #print(f"Reproduciendo tono de {frecuencia} Hz en dispositivo {output_device_index}")
            try:
                import sounddevice as sd  # Asegurar disponibilidad local
            except Exception:
                raise RuntimeError("El backend de reproducción 'sounddevice' no está disponible.")
            sd.play(onda_senoidal.astype(np.float32), samplerate=frecuencia_muestreo,
                    device=output_device_index, blocking=False)
            
            # Capturar audio durante la reproducción
            captured_audio = []
            start_time = time.time()
            
            while time.time() - start_time < duracion + 0.5:  # Añadir 0.5s extra
                try:
                    audio_data = self.cModel.get_audio_data()
                    if audio_data and len(audio_data) >= 7:
                        current_data, _, _, _, _, _, _ = audio_data
                        if len(current_data) > 0:
                            # Convertir a float32 y normalizar (-1.0 a 1.0)
                            normalized_data = current_data.astype(np.float32) / (32767.0/2)
                            captured_audio.extend(normalized_data)
                    time.sleep(0.01)  # Pequeña pausa para no saturar el CPU
                except Exception as e:
                    #print(f"Error durante la captura de audio: {e}")
                    break
            
            # Asegurar fin de reproducción y cerrar captura
            try:
                sd.wait()
            except Exception:
                pass
            self.cModel.stream.stop_stream()
            
            if not captured_audio:
                raise ValueError("No se capturó audio. Verifique la conexión del micrófono.")
                
            # Convertir a array de numpy
            captured_audio = np.array(captured_audio)
            
            # Calcular el nivel RMS en dBSPL
            rms = np.sqrt(np.mean(captured_audio**2))
            rms_db = 20 * np.log10(rms/0.00002)  # Evitar log(0)
            #calcular dBFS
            rms_dbfs = 20 * np.log10(rms/1.0)
            
            # Calcular el factor de calibración
            cal = ref_level - rms_db

            #calcular offset
            offset = ref_level - rms_dbfs
            
            #print(f"Nivel de referencia: {ref_level} dB")
            #print(f"Nivel RMS medido: {rms_db:.2f} dB")
            #print(f"Factor de calibración: {cal:.2f} dB")
            
            # Guardar el factor de calibración
            self.cModel.setCalibracionAutomatica(cal)

            # Guardar el offset en el modelo
            self.cModel.set_calibracion_offset_spl(offset)
            
            # # Actualizar la UI
            # self.cVista.txtValorRef.setText(f"{cal:.2f}")
            
            # Mostrar mensaje de éxito
            QMessageBox.information(
                self.ventanas_abiertas["calibracion"],
                "Calibración Exitosa",
                f"Calibración relativa completada.\n\n"
                f"Nivel de referencia: {ref_level:.2f} dB\n"
                f"Nivel medido: {rms_db:.2f} dB\n"
                f"Factor de ajuste: {cal:.2f} dB"
            )
            
        except Exception as e:
            error_msg = f"Error durante la calibración: {str(e)}"
            #print(error_msg)
            QMessageBox.critical(self.ventanas_abiertas["calibracion"], "Error de Calibración", error_msg)

    def actualizar_limite_desde_fs(self, fs):
        self.frecuencia_muestreo_actual = fs
    
    def set_frecuencia_muestreo_actual(self, fs):
        self.frecuencia_muestreo_actual = fs
    
    def get_frecuencia_muestreo_actual(self):
        return self.frecuencia_muestreo_actual
    
    def abrir_calibracion(self):
        if self.ventanas_abiertas["calibracion"] is None:
            self.ventanas_abiertas["calibracion"] = CalibracionWin(self, self.cVista)
        self.ventanas_abiertas["calibracion"].showNormal()
        self.ventanas_abiertas["calibracion"].raise_()
        self.ventanas_abiertas["calibracion"].activateWindow()

    def abrir_generador(self):
        if self.ventanas_abiertas["generador"] is None:
            self.ventanas_abiertas["generador"] = GeneradorWin(self)
        self.ventanas_abiertas["generador"].showNormal()
        self.ventanas_abiertas["generador"].raise_()
        self.ventanas_abiertas["generador"].activateWindow()

    def abrir_config_disp(self):
        if self.ventanas_abiertas["config_disp"] is None:
            if self.ventanas_abiertas["calibracion"] is not None:
                config_disp = ConfigDispWin(self, self.ventanas_abiertas["calibracion"])
            else:
                config_disp = ConfigDispWin(self, None)
            self.ventanas_abiertas["config_disp"] = config_disp

            # ✅ Guardamos la instancia, no la señal
            self.config_disp_instancia = config_disp
            self.config_disp_instancia.frecuenciaMuestreoCambiada.connect(self.set_frecuencia_muestreo_actual)

        self.ventanas_abiertas["config_disp"].showNormal()
        self.ventanas_abiertas["config_disp"].raise_()
        self.ventanas_abiertas["config_disp"].activateWindow()

    def abrir_configuracion(self):
        if self.ventanas_abiertas["configuracion"] is None:
            config_win = ConfiguracionWin(self.cVista, self)
            self.ventanas_abiertas["configuracion"] = config_win

            # ✅ Conectamos desde la instancia real, no señal suelta
            if hasattr(self, "config_disp_instancia"):
                self.config_disp_instancia.frecuenciaMuestreoCambiada.connect(
                    config_win.actualizarLimiteXMaxEspectro
                )

        self.ventanas_abiertas["configuracion"].showNormal()
        self.ventanas_abiertas["configuracion"].raise_()
        self.ventanas_abiertas["configuracion"].activateWindow()

    def abrir_programar(self):
        if self.ventanas_abiertas["programar"] is None:
            self.ventanas_abiertas["programar"] = ProgramarWin(self)
        self.ventanas_abiertas["programar"].showNormal()
        self.ventanas_abiertas["programar"].raise_()
        self.ventanas_abiertas["programar"].activateWindow()
        
    def abrir_grabaciones(self):
        if self.ventanas_abiertas["grabaciones"] is None:
            self.ventanas_abiertas["grabaciones"] = GrabacionesWin(self)
        self.ventanas_abiertas["grabaciones"].showNormal()
        self.ventanas_abiertas["grabaciones"].raise_()
        self.ventanas_abiertas["grabaciones"].activateWindow()

    def aceptar_calibracion(self):
        self.cModel.activar_calibracion(True)
        if self.ventanas_abiertas["calibracion"]:
            self.ventanas_abiertas["calibracion"].close()
            
    def verificar_grabaciones_programadas(self):
        ahora = datetime.now()
        registros = leer_todas_grabaciones()
        for registro in registros:
            id_reg, fecha_ini, hora_ini, fecha_fin, hora_fin, duracion, ext, estado, ruta = registro
            if estado == "Pendiente":
                fecha_hora_inicio = datetime.strptime(f"{fecha_ini} {hora_ini}", "%Y-%m-%d %H:%M:%S")
                fecha_hora_fin = datetime.strptime(f"{fecha_fin} {hora_fin}", "%Y-%m-%d %H:%M:%S")
                if fecha_hora_inicio <= ahora <= fecha_hora_inicio + timedelta(seconds=10):  # margen de 10s
                    #print(f"[INFO] Iniciando grabación automática: {id_reg}")
                    self.iniciar_grabacion_automatica(id_reg, duracion, ruta, ext)
    
    def iniciar_grabacion_automatica(self, id_reg, duracion_str, ruta, ext):
        # Preparar duración
        h, m, s = map(int, duracion_str.split(":"))
        duracion_seg = h * 3600 + m * 60 + s

        # Crear nombre de archivo
        nombre_archivo = f"grabacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
        path_completo = os.path.join(ruta, nombre_archivo)

        try:
            # Iniciar grabación
            #print(f"[INFO] Grabando {duracion_seg}s en {path_completo}")
            self.grabar_audio_y_guardar(path_completo, duracion_seg)

            # Actualizar estado a 'realizada'
            actualizar_estado(id_reg, "realizada")

            # Reproducir en vista (como grabación manual)
            from scipy.io.wavfile import read as wavread
            Fs, data = wavread(path_completo)
            if data.ndim > 1:
                data = data.mean(axis=1)
            max_val = np.max(np.abs(data))
            normalizado = data / max_val if max_val > 0 else data
            self.cModel.setSignalData(normalizado)
            self.graficar()

        except Exception as e:
            print(f"[ERROR] Falló la grabación automática: {e}")
    
    def grabar_audio_y_guardar(self, path_completo, duracion):
        import sounddevice as sd
        import soundfile as sf

        fs = self.frecuencia_muestreo_actual
        #print(f"[INFO] Grabando a {fs} Hz...")
        grabacion = sd.rec(int(duracion * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()  # esperar a que termine

        sf.write(path_completo, grabacion, fs)

