# function: xA = filterA(x, fs)
# x - original signal in the time domain
# fs - sampling frequency, Hz
# xA - filtered signal in the time domain
# Note: The A-weighting filter's coefficients 
# are acccording to IEC 61672-1:2002 standard 
# determine the signal length

import numpy as np
from scipy.fftpack import fft, ifft

def filtA(x,fs):
    xlen = len(x)

    X = fft(x)

    f = np.fft.fftfreq(xlen, 1.0/fs)

    c1 = 12194.217**2
    c2 = 20.598997**2
    c3 = 107.65265**2
    c4 = 737.86223**2

    f2 = f**2
    num = c1 * f2**2
    den = (f2 + c2) * np.sqrt((f2 + c3)*(f2 + c4))*(f2 + c1)
    A = 1.2589 * num/den
    XA = X * A

    xA = np.real(ifft(XA))
    return xA

def filtFrecA(X,fs):
    xlen = len(X)

    f = np.array(range(0, xlen))*fs/(2*xlen)

    c1 = 12194.217**2
    c2 = 20.598997**2
    c3 = 107.65265**2
    c4 = 737.86223**2

    f = f**2
    num = c1 * (f**2)
    den = (f + c2) * np.sqrt((f + c3)*(f + c4))*(f + c1)
    A = 1.2589 * num/den

    XA = X * A

    return XA

def filtC(x,fs):
    xlen = len(x)

    X = fft(x)

    f = np.fft.fftfreq(xlen, 1.0/fs)

    c1 = 12194.217**2
    c2 = 20.598997**2

    f2 = f**2
    num = c1 * f2
    den = (f2 + c2) * (f2 + c1)
    C =  1.0072 * num/den

    XC = X * C

    xC = np.real(ifft(XC))

    return xC

def filtFrecC(X,fs):
    xlen = len(X)

    f = np.array(range(0, xlen))*fs/(2*xlen)

    c1 = 12194.217**2
    c2 = 20.598997**2

    f = f**2
    num = c1 * f
    den = (f + c2) * (f + c1)
    C =  1.0072 * num/den

    XC = X * C

    return XC