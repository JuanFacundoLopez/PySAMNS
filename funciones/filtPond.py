# function: xA = filterA(x, fs)
# x - original signal in the time domain
# fs - sampling frequency, Hz
# xA - filtered signal in the time domain
# Note: The A-weighting filter's coefficients 
# are acccording to IEC 61672-1:2002 standard 
# determine the signal length

from math import ceil
import numpy as np
from scipy.fftpack import fft, ifft

def filtA(x,fs):
    xlen = len(x)                   #largo del vector

    NumUniquePts = ceil((xlen+1)/2) # numero de puntos unicos

    X = fft(x)                      # FFT

    X = np.array(X[1:NumUniquePts]) # fft is symmetric, throw away the second half

    f =np.array(range(0, NumUniquePts-1))*fs/xlen # Vector de frecuencia 

# A-weighting coeficientes del filtro
    c1 = 12194.217**2
    c2 = 20.598997**2
    c3 = 107.65265**2
    c4 = 737.86223**2
# Opero el filtro de ponderacion A en el dominio de la frecuencia
    f = f**2
    num = c1 * (f**2)
    den = (f + c2) * np.sqrt((f + c3)*(f + c4))*(f + c1)
    A =  1.2589 * num/den
    XA = X * A # filtrado en el dominio de frecuencia
# reconstruct the whole spectrum
    if xlen % 2 == 0:                           # si el largo del vector es par excluyo los puntos Nyquist 
        XA = np.append(XA, np.conj(XA[xlen:0:-1]))
    else:                                       # si el largo del vector es impar incluyo los puntos Nyquist
        XA = np.append(XA, np.conj(XA[xlen-1:0:-1]))
# IFFT
    xA = np.real(ifft(XA))
    return xA

def filtFrecA(X,fs):
    xlen = len(X)                   #largo del vector
    NumUniquePts = ceil(xlen+1)     # numero de puntos unicos

# frequency vector with NumUniquePts points
    f =np.array(range(0, NumUniquePts-1))*fs/xlen
# A-weighting filter coefficients
    c1 = 12194.217**2
    c2 = 20.598997**2
    c3 = 107.65265**2
    c4 = 737.86223**2

# evaluate the A-weighting filter in the frequency domain
    f = f**2
    num = c1 * (f**2)
    den = (f + c2) * np.sqrt((f + c3)*(f + c4))*(f + c1)
    A =  1.2589 * num/den

# filtering in the frequency domain
    XA = X * A

    return XA

def filtC(x,fs):
    xlen = len(x)                   #largo del vector
    NumUniquePts = ceil((xlen+1)/2) # numero de puntos unicos

    X = fft(x)                      # FFT

    X = np.array(X[1:NumUniquePts]) # Tomo los valores de frecuencia mayores a 0 


    f =np.array(range(0,NumUniquePts-1))*fs/xlen # Creo un vector de frecuencia 

# Coeficientes del filtro C
    c1 = 12194.217**2
    c2 = 20.598997**2

# Opero el filtro de ponderacion C en el dominio de la frecuencia
    f = f**2
    num = c1 * f
    den = (f + c2) * (f + c1) 
    C =  1.0072 * num/den

# filtrado en el dominio de frecuencia
    XC = X * C
# reconstruct the whole spectrum
    if xlen % 2:                             # si el largo del vector es par excluyo los puntos Nyquist 
        XC = np.append(XC, np.conj(XC[xlen:0:-1]))
    else:                                    # si el largo del vector es impar incluyo los puntos Nyquist
        XC = np.append(XC, np.conj(XC[xlen-1:0:-1]))

# IFFT
    xC = np.real(ifft(XC)) # Aplico la transformada rapida inversa de furier
    
    return xC

def filtFrecC(X,fs):
    xlen = len(X)
# number of unique points
    NumUniquePts = ceil(xlen+1)

# frequency vector with NumUniquePts points
    f =np.array(range(0, NumUniquePts-1))*fs/xlen

# C-weighting filter coefficients
    c1 = 12194.217**2
    c2 = 20.598997**2

# evaluate the C-weighting filter in the frequency domain
    f = f**2
    num = c1 * f
    den = (f + c2) * (f + c1) 
    A =  1.0072 * num/den

# filtering in the frequency domain
    XC = X * A

    return XC