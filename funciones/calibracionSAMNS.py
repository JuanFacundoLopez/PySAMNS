import numpy as np

def _goertzel_mag(x: np.ndarray, fs: int, f: float) -> float:
    """Magnitud (lineal) del tono f en la señal x usando Goertzel (robusto a desalineación de bin)."""
    N = len(x)
    if N == 0 or fs <= 0 or f <= 0 or f >= fs/2:
        return 0.0
    k = int(round(f * N / fs))
    w = 2.0*np.pi*k/N
    coeff = 2.0*np.cos(w)
    s0 = s1 = s2 = 0.0
    for n in range(N):
        s0 = x[n] + coeff*s1 - s2
        s2, s1 = s1, s0
    # magnitud coherente (escala relativa; para THD la escala absoluta no importa)
    return np.sqrt(s1*s1 + s2*s2 - coeff*s1*s2) / N

def compute_thd(signal: np.ndarray,
                    fs: int,
                    f0_expected: float = 1000.0,
                    max_harmonics: int = 10,
                    search_pct: float = 0.15,
                    min_level_dbfs: float = -40.0):
    """
    THD para calibración con micrófono.
    - Busca la fundamental cerca de f0_expected; si no es confiable, usa Goertzel.
    - Armónicos medidos con Goertzel (robusto a desajustes de frecuencia).
    Devuelve: (thd_pct, f0_detectada, nivel_dbfs)
    """
    if signal is None or len(signal) == 0 or fs <= 0:
        return 100.0, None, None

    # Normalizar y ventana
    x = signal.astype(np.float64)
    x -= np.mean(x)
    window = np.hanning(len(x))
    xw = x * window

    # Nivel RMS en dBFS (referencia 1.0 full scale)
    rms = np.sqrt(np.mean(x**2))
    nivel_dbfs = 20*np.log10(max(rms, 1e-12))
    if nivel_dbfs < min_level_dbfs:
        # Nivel muy bajo: el ruido domina, evita falsos THD altos
        return 100.0, None, nivel_dbfs

    # FFT solo para localizar pico CERCA de f0_expected (no el pico global)
    spectrum = np.fft.rfft(xw)
    mag = np.abs(spectrum)
    freqs = np.fft.rfftfreq(len(xw), 1.0/fs)
    mag[0] = 0.0

    fmin = f0_expected * (1.0 - search_pct)
    fmax = f0_expected * (1.0 + search_pct)
    band = (freqs >= fmin) & (freqs <= fmax)
    k0 = None
    if np.any(band):
        # Pico dentro de la ventana esperada
        k0 = np.argmax(mag[band]) + np.where(band)[0][0]
        f0_detectada = freqs[k0]
        V1_fft = mag[k0]
    else:
        f0_detectada = f0_expected
        V1_fft = 0.0

    # Fundamental por Goertzel (más robusto)
    V1 = _goertzel_mag(xw, fs, f0_detectada if k0 is not None else f0_expected)
    if V1 <= 1e-12:
        return 100.0, f0_detectada, nivel_dbfs

    # Potencia de armónicos por Goertzel (más estable que buscar bins)
    harmonics_power = 0.0
    base_f = f0_detectada if k0 is not None else f0_expected
    for h in range(2, max_harmonics + 1):
        fh = h * base_f
        if fh >= fs / 2:
            break
        Vh = _goertzel_mag(xw, fs, fh)
        harmonics_power += Vh * Vh

    thd = np.sqrt(harmonics_power) / V1
    return float(thd * 100.0), float(base_f), float(nivel_dbfs)
