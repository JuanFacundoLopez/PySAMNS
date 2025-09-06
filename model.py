#from chunk import Chunk
from funciones import consDisp
import numpy as np
import pyaudio
import time
from funciones.filtPond import filtA, filtC, filtFrecA, filtFrecC
from scipy.fftpack import fft


class modelo:
    def __init__(self, Controller, rate=44100, chunk=1024, device_index=1):          # Constructor del modelo
        self.mController = Controller
        dispEn, dispEnIndice, dispSal, dispSalIndice, dispEnRate = consDisp.consDisp()
        self.dispEn = dispEn
        self.dispEnIndice = dispEnIndice
        self.dispSal = dispSal
        self.dispSalIndice = dispSalIndice
        self.dispEnRate = dispEnRate
        
        #para ponere valorea a las frecuencias
        self.modo_espectro = "lineal"  # Puede ser: "lineal", "octava", "tercio"
        self.ultimas_bandas = None
        self.ultimos_niveles = None

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

        # Arrays para almacenar valores históricos de niveles estadísticos
        # Filtro Z
        self.recorderLeqZ = np.empty(0)
        self.recorderL01Z = np.empty(0)
        self.recorderL10Z = np.empty(0)
        self.recorderL50Z = np.empty(0)
        self.recorderL90Z = np.empty(0)
        self.recorderL99Z = np.empty(0)
        
        # Filtro C
        self.recorderLeqC = np.empty(0)
        self.recorderL01C = np.empty(0)
        self.recorderL10C = np.empty(0)
        self.recorderL50C = np.empty(0)
        self.recorderL90C = np.empty(0)
        self.recorderL99C = np.empty(0)
        
        # Filtro A
        self.recorderLeqA = np.empty(0)
        self.recorderL01A = np.empty(0)
        self.recorderL10A = np.empty(0)
        self.recorderL50A = np.empty(0)
        self.recorderL90A = np.empty(0)
        self.recorderL99A = np.empty(0)

        self.SignalFrecA = np.empty(0)
        self.SignalFrecC = np.empty(0)
        self.SignalFrecZ = np.empty(0)
        self.signaldataA = np.empty(0)
        self.signaldataC = np.empty(0)
        self.signaldataZ = np.empty(0)

        self.Fs = rate

        # Atributos para calibración relativa
        self.ruta_archivo_calibracion = None
        self.offset_calibracion_spl = 0.0

        # --------------------Codigo Yamili-------------------------
        self.rate = rate
        self.chunk = chunk
        self.device_index = device_index  # Guardar el device_index original
        self.device_index_salida = 0  # Dispositivo de salida por defecto
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
            if self.device_index is not None:
                try:
                    device_info = self.pyaudio_instance.get_device_info_by_index(self.device_index)
                except Exception:
                    raise ValueError(f"Dispositivo con índice {self.device_index} no encontrado")
                
                if device_info['maxInputChannels'] <= 0:
                    raise ValueError(f"El dispositivo {device_info['name']} no soporta entrada de audio")

            self.stream = self.pyaudio_instance.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=self.device_index,
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
    
    def initialize_audio_stream(self, device_index=None, rate=None, chunk=None):
        """Inicializa o reinicializa el stream de audio con los parámetros especificados"""
        try:
            # Cerrar stream existente si hay uno
            if hasattr(self, 'stream') and self.stream is not None:
                self.stream.close()
            
            # Actualizar parámetros si se proporcionan
            if rate is not None:
                self.rate = rate
            if chunk is not None:
                self.chunk = chunk
            if device_index is not None:
                self.device_index = device_index  # Actualizar el device_index del modelo
            
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
            
            # Reinicializar buffers y datos cuando se cambia el dispositivo
            self.buffer = []
            self.normalized_all = []
            self.times = []
            self.start_time = None
                
        except Exception as e:
            raise Exception(f"Error al inicializar el stream de audio: {str(e)}")
    
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
        
    def setNivelesZ(self, recorderPicoZ=0, recorderInstZ=0, recorderFastZ=0, recorderSlowZ=0, mode='a'):
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
    def setNivelesC(self, recorderPicoC=0, recorderInstC=0, recorderFastC=0, recorderSlowC=0, mode='a'):
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

    def set_ruta_archivo_calibracion(self, ruta):
        self.ruta_archivo_calibracion = ruta

    def get_ruta_archivo_calibracion(self):
        return self.ruta_archivo_calibracion

    def set_calibracion_offset_spl(self, offset):
        self.offset_calibracion_spl = offset

    def get_calibracion_offset_spl(self):
        return self.offset_calibracion_spl

    def aplicar_calibracion_spl(self, valor_dbfs):
        return valor_dbfs + self.offset_calibracion_spl

    def getDispositivosEntradaRate(self):
        return self.dispEnRate
    
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
    
    def getDispositivoActual(self):
        """Retorna el índice del dispositivo de entrada actualmente configurado en el modelo."""
        if hasattr(self, 'device_index'):
            return self.device_index
        return None
    
    def getDispositivoSalidaActual(self):
        """Retorna el índice del dispositivo de salida actualmente en uso"""
        # Usar el device_index_salida almacenado en el modelo
        if hasattr(self, 'device_index_salida'):
            return self.device_index_salida
        return None
    
    def setDispositivoSalida(self, device_index_salida):
        """Establece el dispositivo de salida"""
        self.device_index_salida = device_index_salida
    def getNivelesA(self, NP='A'):
        pico = self.aplicar_calibracion_spl(self.recorderPicoA)
        inst = self.aplicar_calibracion_spl(self.recorderInstA)
        fast = self.aplicar_calibracion_spl(self.recorderFastA)
        slow = self.aplicar_calibracion_spl(self.recorderSlowA)
        
        if NP == 'P':
            return pico
        if NP == 'I':
            return inst
        if NP == 'F':
            return fast
        if NP == 'S':
            return slow
        if NP == 'A':
            return (pico, inst, fast, slow)
            
    def getNivelesC(self, NP='A'):
        pico = self.aplicar_calibracion_spl(self.recorderPicoC)
        inst = self.aplicar_calibracion_spl(self.recorderInstC)
        fast = self.aplicar_calibracion_spl(self.recorderFastC)
        slow = self.aplicar_calibracion_spl(self.recorderSlowC)

        if NP == 'P':
            return pico
        if NP == 'I':
            return inst
        if NP == 'F':
            return fast
        if NP == 'S':
            return slow
        if NP == 'A':
            return (pico, inst, fast, slow)

    def getNivelesZ(self, NP='A'):
        pico = self.aplicar_calibracion_spl(self.recorderPicoZ)
        inst = self.aplicar_calibracion_spl(self.recorderInstZ)
        fast = self.aplicar_calibracion_spl(self.recorderFastZ)
        slow = self.aplicar_calibracion_spl(self.recorderSlowZ)

        if NP == 'P':
            return pico
        if NP == 'I':
            return inst
        if NP == 'F':
            return fast
        if NP == 'S':
            return slow
        if NP == 'A':
            return (pico, inst, fast, slow)
    def getCalibracionAutomatica(self):
        return self.cal
        
    # ====== Niveles Equivalentes (Leq) y Percentiles ======
    def calculate_leq_and_percentiles(self):
        """
        Calcula los niveles equivalentes (Leq) y percentiles estadísticos
        para los filtros A, C y Z usando los valores Fast.
        
        Returns:
            dict: Diccionario con los resultados para cada filtro (A, C, Z)
        """
        results = {}
        
        # Para cada tipo de filtro (A, C, Z)
        for filtro in ['A', 'C', 'Z']:
            # Obtener los datos Fast del filtro correspondiente
            fast_data = getattr(self, f'recorderFast{filtro}')
            
            # Si no hay datos, establecer valores por defecto
            if len(fast_data) == 0:
                results[f'Leq{filtro}'] = 0.0
                results[f'L01{filtro}'] = 0.0
                results[f'L10{filtro}'] = 0.0
                results[f'L50{filtro}'] = 0.0
                results[f'L90{filtro}'] = 0.0
                results[f'L99{filtro}'] = 0.0
                continue
                
            # Calcular Leq (RMS de los valores Fast)
            leq = self._calculate_leq(fast_data)
            
            # Calcular percentiles
            percentiles = self._calculate_percentiles(fast_data)
            
            # Aplicar calibración
            leq_calibrado = self.aplicar_calibracion_spl(leq) if hasattr(self, 'aplicar_calibracion_spl') else leq
            percentiles_calibrados = {k: self.aplicar_calibracion_spl(v) if hasattr(self, 'aplicar_calibracion_spl') else v 
                                    for k, v in percentiles.items()}
            
            # Guardar resultados
            results[f'Leq{filtro}'] = leq_calibrado
            for p_name, p_value in percentiles_calibrados.items():
                results[f'L{p_name}{filtro}'] = p_value
            
            # Guardar en atributos de la clase
            setattr(self, f'Leq{filtro}', leq_calibrado)
            for p_name, p_value in percentiles_calibrados.items():
                setattr(self, f'L{p_name}{filtro}', p_value)
        
        return results
    
    def _calculate_leq(self, data):
        """
        Calcula el nivel equivalente (Leq) como el RMS de los datos.
        
        Args:
            data (numpy.ndarray): Vector con los niveles de presión sonora.
            
        Returns:
            float: Nivel equivalente en dB.
        """
        if len(data) == 0:
            return 0.0
            
        # Convertir de dB a presión cuadrática
        p_squared = 10 ** (data / 10)
        
        # Calcular media cuadrática
        mean_p_squared = np.mean(p_squared)
        
        # Convertir de vuelta a dB
        leq = 10 * np.log10(mean_p_squared) if mean_p_squared > 0 else -np.inf
        
        return leq if np.isfinite(leq) else 0.0
    
    def _calculate_percentiles(self, data):
        """
        Calcula los percentiles estadísticos L01, L10, L50, L90, L99.
        
        Args:
            data (numpy.ndarray): Vector con los niveles de presión sonora.
            
        Returns:
            dict: Diccionario con los percentiles calculados.
        """
        if len(data) == 0:
            return {'01': 0.0, '10': 0.0, '50': 0.0, '90': 0.0, '99': 0.0}
            
        # Calcular percentiles usando numpy
        percentiles = {
            '01': float(np.percentile(data, 1)),
            '10': float(np.percentile(data, 10)),
            '50': float(np.percentile(data, 50)),  # Mediana
            '90': float(np.percentile(data, 90)),
            '99': float(np.percentile(data, 99))
        }
        
        return percentiles
    
    def update_statistical_levels_history(self, stats):
        """
        Actualiza los arrays históricos de niveles estadísticos con los nuevos valores calculados.
        
        Args:
            stats (dict): Diccionario con los niveles estadísticos calculados
        """
        # Función auxiliar para agregar valor a un array con límite de tamaño
        def append_with_limit(array, value, max_size=1000):
            new_array = np.append(array, value)
            if len(new_array) > max_size:
                new_array = new_array[-max_size:]  # Mantener solo los últimos max_size valores
            return new_array
        
        # Actualizar arrays del filtro Z
        if 'LeqZ' in stats:
            self.recorderLeqZ = append_with_limit(self.recorderLeqZ, stats['LeqZ'])
        if 'L01Z' in stats:
            self.recorderL01Z = append_with_limit(self.recorderL01Z, stats['L01Z'])
        if 'L10Z' in stats:
            self.recorderL10Z = append_with_limit(self.recorderL10Z, stats['L10Z'])
        if 'L50Z' in stats:
            self.recorderL50Z = append_with_limit(self.recorderL50Z, stats['L50Z'])
        if 'L90Z' in stats:
            self.recorderL90Z = append_with_limit(self.recorderL90Z, stats['L90Z'])
        if 'L99Z' in stats:
            self.recorderL99Z = append_with_limit(self.recorderL99Z, stats['L99Z'])
        
        # Actualizar arrays del filtro C
        if 'LeqC' in stats:
            self.recorderLeqC = append_with_limit(self.recorderLeqC, stats['LeqC'])
        if 'L01C' in stats:
            self.recorderL01C = append_with_limit(self.recorderL01C, stats['L01C'])
        if 'L10C' in stats:
            self.recorderL10C = append_with_limit(self.recorderL10C, stats['L10C'])
        if 'L50C' in stats:
            self.recorderL50C = append_with_limit(self.recorderL50C, stats['L50C'])
        if 'L90C' in stats:
            self.recorderL90C = append_with_limit(self.recorderL90C, stats['L90C'])
        if 'L99C' in stats:
            self.recorderL99C = append_with_limit(self.recorderL99C, stats['L99C'])
        
        # Actualizar arrays del filtro A
        if 'LeqA' in stats:
            self.recorderLeqA = append_with_limit(self.recorderLeqA, stats['LeqA'])
        if 'L01A' in stats:
            self.recorderL01A = append_with_limit(self.recorderL01A, stats['L01A'])
        if 'L10A' in stats:
            self.recorderL10A = append_with_limit(self.recorderL10A, stats['L10A'])
        if 'L50A' in stats:
            self.recorderL50A = append_with_limit(self.recorderL50A, stats['L50A'])
        if 'L90A' in stats:
            self.recorderL90A = append_with_limit(self.recorderL90A, stats['L90A'])
        if 'L99A' in stats:
            self.recorderL99A = append_with_limit(self.recorderL99A, stats['L99A'])
    
# -------------- funcion codigo YAMILI-----------------
    def normalize_data(self, data):
        """Normaliza los datos a un rango de -1 a 1"""
        return data / self.max_int16

    # def calculate_db(self, data):
    #     """Calcula el nivel en decibelios"""
    #     normalized = self.normalize_data(data)
    #     rms = np.sqrt(np.mean(normalized**2))
    #     if rms < 1e-10:  # Evitar log(0)
    #         return -100.0
    #     db = 20 * np.log10(rms / self.reference)
    #     return max(-100.0, min(db, 0.0))  # Limitar entre -100 y 0 dB

    def calculate_fft(self, data):
        """Calcula la FFT de los datos de audio y devuelve la magnitud en dBFS"""
        if len(data) == 0:
            return [], []
        
        # Aplicar ventana de Hann para reducir el leakage espectral
        window = np.hanning(len(data))
        window_gain = np.mean(window**2)  # Factor de corrección de la ventana
        
        # Calcular FFT
        fft_data = np.fft.rfft(data * window)
        N = len(data)
        
        # Calcular magnitud y escalar correctamente
        fft_magnitude = np.abs(fft_data) / (N * np.sqrt(window_gain))
        
        # Convertir a dBFS (decibeles relativos a full scale)
        fft_magnitude_db = 20 * np.log10(np.maximum(fft_magnitude / self.max_int16, 1e-10))
        
        # Obtener frecuencias correspondientes
        fft_freqs = np.fft.rfftfreq(N, d=1.0/self.rate)
        
        # Filtrar frecuencias positivas
        valid = fft_freqs > 0
        return fft_freqs[valid], fft_magnitude_db[valid]

    def calcular_tercios_octava(self, fft_freqs, fft_magnitude_db):
        """
        Calcula los niveles en bandas de tercio de octava a partir de la FFT en tiempo real.
        Usa valores en dB y toma el promedio energético (RMS) de los valores en cada banda.
        Devuelve:   bandas: frecuencias centrales de cada banda
                    niveles: nivel promedio en dB de cada banda
        """
        # Frecuencias centrales típicas de tercios de octava (20 Hz a 20 kHz)
        fcs = [16, 20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000]
        bandas = []
        niveles = []
        
        for i, fc in enumerate(fcs):
            # Definir el rango de frecuencias para esta banda
            if i == 0:
                f_low = 0
                f_high = (16 + 20) / 2
            elif i == len(fcs) - 1:
                f_low = (16000 + 20000) / 2
                f_high = fft_freqs[-1] if len(fft_freqs) > 0 else 20000
            else:
                f_low = (fcs[i-1] + fc) / 2
                f_high = (fc + fcs[i+1]) / 2
                
            # Encontrar los índices de frecuencias que están en este rango
            indices = np.where((fft_freqs >= f_low) & (fft_freqs < f_high))[0]
            
            if len(indices) > 0:
                # Convertir de dB a magnitud, promediar y volver a dB (promedio energético)
                magnitudes = 10 ** (fft_magnitude_db[indices] / 20)  # dB a magnitud
                rms = np.sqrt(np.mean(magnitudes ** 2))  # RMS en magnitud
                nivel_db = 20 * np.log10(max(rms, 1e-6))  # De vuelta a dB con piso de -120 dB
                bandas.append(fc)
                niveles.append(nivel_db)
            else:
                # Si no hay datos en esta banda, asignar -120 dB
                bandas.append(fc)
                niveles.append(-120.0)
                
        self.modo_espectro = "tercio"
        self.ultimas_bandas = np.array(bandas)
        self.ultimos_niveles = np.array(niveles)
        return self.ultimas_bandas, self.ultimos_niveles

    def calcular_octavas(self, fft_freqs, fft_magnitude_db):
        """
        Calcula los niveles en bandas de octava a partir de la FFT.
        Usa valores en dB y toma el promedio energético (RMS) de los valores en cada banda.
        
        Devuelve:
            bandas: frecuencias centrales de cada banda
            niveles: nivel promedio en dB de cada banda
        """
        # Frecuencias centrales típicas de bandas de octava (20 Hz a 20 kHz)
        fcs = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
        
        bandas = []
        niveles = []
        
        for i, fc in enumerate(fcs):
            # En bandas de octava, el ancho se define como fc / √2 a fc * √2
            f_low = fc / np.sqrt(2)
            f_high = fc * np.sqrt(2)
            
            # Buscar los índices dentro de ese rango
            indices = np.where((fft_freqs >= f_low) & (fft_freqs < f_high))[0]
            
            if len(indices) > 0:
                # Convertir de dB a magnitud, promediar y volver a dB (promedio energético)
                magnitudes = 10 ** (fft_magnitude_db[indices] / 20)  # dB a magnitud
                rms = np.sqrt(np.mean(magnitudes ** 2))  # RMS en magnitud
                nivel_db = 20 * np.log10(max(rms, 1e-6))  # De vuelta a dB con piso de -120 dB
                bandas.append(fc)
                niveles.append(nivel_db)
            else:
                # Si no hay datos en esta banda, asignar -120 dB
                bandas.append(fc)
                niveles.append(-120.0)
        
        self.modo_espectro = "octava"
        self.ultimas_bandas = np.array(bandas)
        self.ultimos_niveles = np.array(niveles)
        return self.ultimas_bandas, self.ultimos_niveles

    def get_bandas_y_niveles(self):
        return self.ultimas_bandas, self.ultimos_niveles

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
            # current_db = self.calculate_db(current_data)
            
            # Convertir normalized_all a array numpy para mejor rendimiento
            normalized_all_array = np.concatenate(self.normalized_all)
            
            # Calcular FFT para el espectro de frecuencia
            fft_freqs, fft_db = self.calculate_fft(current_data)
            
            # return current_data, all_data, normalized_current, normalized_all_array, current_db, self.times, fft_freqs, fft_db
            return current_data, all_data, normalized_current, normalized_all_array, self.times, fft_freqs, fft_db

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
        