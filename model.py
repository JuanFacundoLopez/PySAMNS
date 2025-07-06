from chunk import Chunk
from funciones import consDisp
import numpy as np
import sys
sys.path.append('C:/Users/Facu/Desktop/SAMNS PyVersion pygraph/SAMNS PyVersion pygraph/funciones')
sys.path.append('C:/Users/Facu/Desktop/SAMNS PyVersion pygraph/SAMNS PyVersion pygraph')  # Add this line
from filtPond import filtA, filtC, filtFrecA, filtFrecC
from scipy.fftpack import fft


class modelo:

    def __init__(self,Controller):          # Constructor del modelo
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

        self.CHUNK = 1024

    
# Setters
    def setChunk(self, chunk):
        self.CHUNK = chunk
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
        yf = np.abs(yf[0:int(self.CHUNK/2)])
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