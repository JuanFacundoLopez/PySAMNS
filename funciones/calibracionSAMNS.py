import numpy as np


def compute_thd(signal: np.ndarray, fs: int, f0: float, max_harmonics: int = 10) -> float:
    """
    Calcula la distorsión armónica total (THD) en porcentaje.

    Parámetros:
    - signal: arreglo 1D con la señal en el dominio del tiempo (float, rango -1..1 recomendado)
    - fs: frecuencia de muestreo en Hz
    - f0: frecuencia fundamental esperada (Hz)
    - max_harmonics: cantidad de armónicos a considerar (por defecto 10)

    Devuelve:
    - THD como porcentaje (0..100)
    """
    if signal is None or len(signal) == 0 or fs <= 0 or f0 <= 0:
        return 100.0

    # Quitar DC y aplicar ventana para minimizar fugas espectrales
    x = signal.astype(np.float64) - np.mean(signal)
    window = np.hanning(len(x))
    xw = x * window

    # FFT de magnitud
    spectrum = np.fft.rfft(xw)
    mag = np.abs(spectrum)
    freqs = np.fft.rfftfreq(len(xw), d=1.0 / fs)

    # Encontrar el índice más cercano a la fundamental
    k0 = int(np.argmin(np.abs(freqs - f0)))
    if k0 <= 0 or k0 >= len(mag):
        return 100.0

    fundamental = mag[k0]
    if fundamental <= 1e-12:
        return 100.0

    # Sumar potencia de armónicos válidos dentro del rango de Nyquist
    harmonics_power = 0.0
    for h in range(2, max_harmonics + 1):
        fh = h * f0
        if fh >= fs / 2:
            break
        kh = int(np.argmin(np.abs(freqs - fh)))
        harmonics_power += mag[kh] ** 2

    thd = np.sqrt(harmonics_power) / fundamental
    return float(thd * 100.0)


