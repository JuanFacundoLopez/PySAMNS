from chunk import Chunk
from funciones import consDisp
import numpy as np
import pyaudio
import time
from funciones.filtPond import filtA, filtC, filtFrecA, filtFrecC
from scipy.fftpack import fft


class modelo:
    def __init__(self, Controller, rate=44100, chunk=1024, device_index=1):          # Constructor del modelo
        self.mController = Controller
        dispEn, dispEnIndice, dispSal, dispSalIndice = consDisp.consDisp()
        self.dispEn = dispEn
        self.dispEnIndice = dispEnIndice
        self.dispSal = dispSal
        self.dispSalIndice = dispSalIndice

        #Valores de niveles con filtro Z
        self.recorderPicoZ = np.empty(0)
        self.recorderInstZ = np.empty(0)
        self.recorderFastZ = np.empty(0)
        self.recorderSlowZ = np.empty(0)

        #Valores de niveles con filtro C
        self.recorderPicoC = np.empty(0)
        self.recorderInstC = np.empty(0)
        self.recorderFastC = np.empty(0)
        self.recorderSlowC = np.empty(0)

        #Valores de niveles con filtro A
        self.recorderPicoA = np.empty(0)
        self.recorderInstA = np.empty(0)
        self.recorderFastA = np.empty(0)
        self.recorderSlowA = np.empty(0)

        self.SignalFrecA = np.empty(0)
        self.SignalFrecC = np.empty(0)
        self.SignalFrecZ = np.empty(0)
        self.signaldataA = np.empty(0)
        self.signaldataC = np.empty(0)
        self.signaldataZ = np.empty(0)

        self.Fs = 44100

        # --------------------Codigo Yamili-------------------------
        self.rate = rate
        self.chunk = chunk
        device_index = None
        self.format = pyaudio.paInt16
        self.channels = 1
        self.normalized_all = []
        # Limitar a 100 chunks (aproximadamente 2.3 segundos a 44100Hz)
        self.max_chunks = 10000
        self.buffer = []
        self.start_time = None  # Add start time tracking
        self.times = []  # Add times array to track timestamps
        
        # Valores de referencia para normalización y dB
        self.max_int16 = 32767
        self.reference = 1.0  # Referencia para dB (1.0 = 0dB)

        try:
            self.pyaudio_instance = pyaudio.PyAudio()
            
            # Verificar si el dispositivo existe y está disponible
            device_info = None
            if device_index is not None:
                try:
                    device_info = self.pyaudio_instance.get_device_info_by_index(device_index)
                except Exception:
                    raise ValueError(f"Dispositivo con índice {device_index} no encontrado")
                
                if device_info['maxInputChannels'] <= 0:
                    raise ValueError(f"El dispositivo {device_info['name']} no soporta entrada de audio")

            self.stream = self.pyaudio_instance.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk,
                stream_callback=None
            )

            # Verificar si el stream está activo
            if not self.stream.is_active():
                raise ValueError("No se pudo activar el stream de audio")

        except Exception as e:
            if hasattr(self, 'pyaudio_instance'):
                self.pyaudio_instance.terminate()
            raise Exception(f"Error al inicializar el dispositivo de audio: {str(e)}")
        # ------------------Codigo Yamili-------------------
    
# Setters
    def setChunk(self, chunk):
        self.chunk = chunk
    def setFs(self,Fs):
        self.Fs = Fs
    def setSignalData(self, signaldata):
        signaldataA = filtA(signaldata, self.Fs)
        signaldataC = filtC(signaldata, self.Fs)
        self.signaldataZ = signaldata   
        self.signaldataA = signaldataA
        self.signaldataC = signaldataC
            # Forma de onda en frecuencia
        yf = fft(signaldata)
        yf = np.abs(yf[0:int(self.chunk/2)])
        self.setSignalFrec(yf) #Guardo en modelo
        
    def setNivelesZ(self, recorderPicoZ, recorderInstZ, recorderFastZ, recorderSlowZ, mode='a'):
        if mode == 'a': # voy concatenando los vectores
            self.recorderPicoZ = np.append(self.recorderPicoZ, recorderPicoZ)
            self.recorderInstZ = np.append(self.recorderInstZ, recorderInstZ)
            self.recorderFastZ = np.append(self.recorderFastZ, recorderFastZ)
            self.recorderSlowZ = np.append(self.recorderSlowZ, recorderSlowZ)

        if mode == 'r': # reseteo los vectores a 0
            self.recorderPicoZ = np.empty(0)
            self.recorderInstZ = np.empty(0)
            self.recorderFastZ = np.empty(0)
            self.recorderSlowZ = np.empty(0)
    def setNivelesC(self, recorderPicoC, recorderInstC, recorderFastC, recorderSlowC, mode='a'):
        if mode == 'a':
            self.recorderPicoC = np.append(self.recorderPicoC, recorderPicoC)
            self.recorderInstC = np.append(self.recorderInstC, recorderInstC)
            self.recorderFastC = np.append(self.recorderFastC, recorderFastC)
            self.recorderSlowC = np.append(self.recorderSlowC, recorderSlowC)

        if mode == 'r':
            self.recorderPicoC = np.empty(0)
            self.recorderInstC = np.empty(0)
            self.recorderFastC = np.empty(0)
            self.recorderSlowC = np.empty(0)
    def setNivelesA(self, recorderPicoA = 0, recorderInstA = 0, recorderFastA = 0, recorderSlowA = 0, mode='a'):
        if mode == 'a':
            self.recorderPicoA = np.append(self.recorderPicoA, recorderPicoA)
            self.recorderInstA = np.append(self.recorderInstA, recorderInstA)
            self.recorderFastA = np.append(self.recorderFastA, recorderFastA)
            self.recorderSlowA = np.append(self.recorderSlowA, recorderSlowA)

        if mode == 'r':
            self.recorderPicoA = np.empty(0)
            self.recorderInstA = np.empty(0)
            self.recorderFastA = np.empty(0)
            self.recorderSlowA = np.empty(0)    
    def setSignalFrec(self, SignalFrec):

        SignalFrecC = filtFrecC(SignalFrec, self.Fs)
        SignalFrecA = filtFrecA(SignalFrec, self.Fs)
        self.SignalFrecA = SignalFrecA
        self.SignalFrecC = SignalFrecC
        self.SignalFrecZ = SignalFrec
    def setCalibracionAutomatica(self, k):
        self.cal=k

# Getters
    def getFs(self):
        return self.Fs    
    def getSignalData(self, Mode='Z'):
        if Mode == 'Z':
            return self.signaldataZ
        if Mode == 'C':
            return self.signaldataC
        if Mode == 'A':
            return self.signaldataA
    def getSignalFrec(self, Mode='Z'):
        if Mode=='Z':
            return self.SignalFrecZ
        if Mode=='C':
            return self.SignalFrecC
        if Mode=='A':
            return self.SignalFrecA
    def getDispositivosEntrada(self, mode):
        if mode == 'indice':
            return self.dispEnIndice
        if mode == 'nombre':
            return self.dispEn
    def getDispositivosSalida(self, mode):
        if mode == 'indice':
            return self.dispSalIndice
        if mode == 'nombre':
            return self.dispSal
    def getNivelesA(self, NP='A'):
        if NP == 'P':
            return self.recorderPicoA
        if NP == 'I':
            return self.recorderInstA
        if NP == 'F':
            return self.recorderFastA
        if NP == 'S':
            return self.recorderSlowA
        if NP == 'A':
            return (self.recorderPicoA, self.recorderInstA, self.recorderFastA, self.recorderSlowA)
    def getNivelesC(self, NP='A'):
        if NP == 'P':
            return self.recorderPicoC
        if NP == 'I':
            return self.recorderInstC
        if NP == 'F':
            return self.recorderFastC
        if NP == 'S':
            return self.recorderSlowC
        if NP == 'A':
            return (self.recorderPicoC, self.recorderInstC, self.recorderFastC, self.recorderSlowC)
    def getNivelesZ(self, NP='A'):

        if NP == 'P':
            return self.recorderPicoZ
        if NP == 'I':
            return self.recorderInstZ
        if NP == 'F':
            return self.recorderFastZ
        if NP == 'S':
            return self.recorderSlowZ
        if NP == 'A':
            return (self.recorderPicoZ, self.recorderInstZ, self.recorderFastZ, self.recorderSlowZ)
    def getCalibracionAutomatica(self):

        return self.cal
    
# -------------- funcion codigo YAMILI-----------------
    def normalize_data(self, data):
        """Normaliza los datos a un rango de -1 a 1"""
        return data / self.max_int16

    def calculate_db(self, data):
        """Calcula el nivel en decibelios"""
        normalized = self.normalize_data(data)
        rms = np.sqrt(np.mean(normalized**2))
        if rms < 1e-10:  # Evitar log(0)
            return -100.0
        db = 20 * np.log10(rms / self.reference)
        return max(-100.0, min(db, 0.0))  # Limitar entre -100 y 0 dB

    def calculate_fft(self, data):
        """Calcula la FFT (Transformada Rápida de Fourier) de los datos de audio y devuelve la magnitud en dB"""
        if len(data) == 0:
            return [], []
        fft_data = np.fft.rfft(data)
        N = len(data)
        fft_magnitude = np.abs(fft_data) / N  # Normalización por número de muestras
        fft_freqs = np.fft.rfftfreq(N, d=1.0/self.rate)
        valid = fft_freqs > 0
        fft_freqs = fft_freqs[valid]
        fft_magnitude = fft_magnitude[valid]
        # Convertir a dB
        # fft_magnitude_db = 20 * np.log10(fft_magnitude + 1e-12)  # Evita log(0)
        return fft_freqs, fft_magnitude

    def calcular_tercios_octava(self, fft_freqs, fft_magnitude):
        """
        Calcula los niveles en bandas de tercio de octava a partir de la FFT en tiempo real.
        Usa la amplitud (no dB) y toma el promedio de todos los valores desde cada banda hasta la siguiente.
        Devuelve:
            bandas: frecuencias centrales de cada banda
            niveles: nivel promedio de amplitud de cada banda
        """
        # Frecuencias centrales típicas de tercios de octava (20 Hz a 20 kHz)
        fcs = [16, 20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000]
        bandas = []
        niveles = []
        for i, fc in enumerate(fcs):
            # Definir el rango de frecuencias para esta banda
            if i == 0:
                # Para la primera banda (16 Hz), usar desde 0 hasta la mitad entre 16 y 20
                f_low = 0
                f_high = (16 + 20) / 2
            elif i == len(fcs) - 1:
                # Para la última banda (20000 Hz), usar desde la mitad entre 16000 y 20000 hasta el máximo
                f_low = (16000 + 20000) / 2
                f_high = fft_freqs[-1] if len(fft_freqs) > 0 else 20000
            else:
                # Para las bandas intermedias, usar desde la mitad entre la banda anterior y actual
                # hasta la mitad entre la banda actual y la siguiente
                f_low = (fcs[i-1] + fc) / 2
                f_high = (fc + fcs[i+1]) / 2
            
            # Encontrar los índices de frecuencias que están en este rango
            indices = np.where((fft_freqs >= f_low) & (fft_freqs < f_high))[0]
            
            if len(indices) > 0:
                # Calcular el promedio de las amplitudes en esta banda
                # Usar la magnitud directamente (amplitud) en lugar de dB
                nivel_promedio = np.mean(fft_magnitude[indices])
                bandas.append(fc)
                niveles.append(nivel_promedio)
            else:
                # Si no hay datos en esta banda, asignar 0
                bandas.append(fc)
                niveles.append(0.0)
        
        return np.array(bandas), np.array(niveles)


    def get_audio_data(self):
        try:
            # Verificar si el stream está activo
            if not self.stream.is_active():
                raise Exception("Stream de audio no activo")

            # Iniciar start_time si no está establecido
            if self.start_time is None:
                self.start_time = time.time()
                self.normalized_all = []  # Volver a inicializar normalized_all cuando se inicia un nuevo stream
                self.times = []  # Resetear el tiempo cuando se inicia un nuevo stream
            # Leer nuevo chunk de audio
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            if not data:
                raise Exception("No se recibieron datos del dispositivo")

            # Luego de cada lectura de audio se calcula la diferencia de tiempo
            current_time = time.time()
            time_diff = current_time - self.start_time
            self.times.append(time_diff)

            # Comparar current_data con data, para verificar que no se vea afectada la amplitud de onda
            current_data = np.frombuffer(data, dtype=np.int16)
            print("current_data max:", np.max(current_data), "min:", np.min(current_data))
            # Verificar que la conversión mantiene la amplitud de la onda
            # Convertir data (bytes) a int16 para comparar amplitudes
            data_as_int16 = np.frombuffer(data, dtype=np.int16)
            
            # Comparar las amplitudes máximas y mínimas de la onda
            if (np.max(current_data) != np.max(data_as_int16) or 
                np.min(current_data) != np.min(data_as_int16) or
                np.mean(np.abs(current_data)) != np.mean(np.abs(data_as_int16))):
                print(f"Advertencia: Posible pérdida de amplitud en la conversión")
                print(f"Data max: {np.max(data_as_int16)}, Current max: {np.max(current_data)}")
                print(f"Data min: {np.min(data_as_int16)}, Current min: {np.min(current_data)}")
                print(f"Data mean abs: {np.mean(np.abs(data_as_int16)):.2f}, Current mean abs: {np.mean(np.abs(current_data)):.2f}")
            
            # Verificar que los valores están dentro del rango esperado para int16
            if np.any(current_data < -32768) or np.any(current_data > 32767):
                raise Exception("Error en la conversión de datos: valores fuera de rango")
            
            # Verificar si los datos son válidos
            if len(current_data) == 0 or np.all(current_data == 0):
                raise Exception("Datos de audio inválidos o silenciosos")
            
            # Agregar el nuevo chunk al buffer
            self.buffer.append(current_data)
            
            # Mantener solo los últimos max_chunks
            if len(self.buffer) > self.max_chunks:
                self.buffer.pop(0)  # Eliminar el chunk más antiguo
                self.times.pop(0)  # Remove corresponding time
                self.normalized_all.pop(0)
            
            # Concatenar todos los chunks en un solo array
            all_data = np.concatenate(self.buffer)
            
            # Calcular valores normalizados y dB
            normalized_current = self.normalize_data(current_data)
            self.normalized_all.append(normalized_current)
            current_db = self.calculate_db(current_data)
            
            # Convertir normalized_all a array numpy para mejor rendimiento
            normalized_all_array = np.concatenate(self.normalized_all)
            
            # Calcular FFT para el espectro de frecuencia
            fft_freqs, fft_db = self.calculate_fft(current_data)
            
            return current_data, all_data, normalized_current, normalized_all_array, current_db, self.times, fft_freqs, fft_db

        except Exception as e:
            print(f"Error en get_audio_data: {e}")
            empty_current = np.zeros(self.chunk)
            empty_all = np.zeros(self.chunk * len(self.buffer) if self.buffer else self.chunk)
            return empty_current, empty_all, empty_current, empty_all, -100.0, [], [], []
        
    def close(self):
        try:
            if hasattr(self, 'stream') and self.stream is not None:
                if self.stream.is_active():
                    self.stream.stop_stream()
                self.stream.close()
            if hasattr(self, 'pyaudio_instance') and self.pyaudio_instance is not None:
                self.pyaudio_instance.terminate()
            self.buffer = []
        except Exception as e:
            print(f"Error al cerrar el audio: {e}")
        