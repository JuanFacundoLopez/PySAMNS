import argparse
import sys

import numpy as np
from sounddevice import query_devices

from funciones.filtPond import filtA, filtC

FS = 44100

TEO_A = {
    10: -70.4, 12.5: -63.4, 16: -56.7, 20: -50.5, 25: -44.7, 31.5: -39.4,
    40: -34.6, 50: -30.2, 63: -26.2, 80: -22.5, 100: -19.1, 125: -16.1,
    160: -13.4, 200: -10.9, 250: -8.6, 315: -6.6, 400: -4.8, 500: -3.2,
    630: -1.9, 800: -0.8, 1000: 0.0, 1250: 0.6, 1600: 1.0, 2000: 1.2,
    2500: 1.3, 3150: 1.2, 4000: 1.0, 5000: 0.5, 6300: -0.1, 8000: -1.1,
    10000: -2.5, 12500: -4.3, 16000: -6.6, 20000: -9.3,
}

TEO_C = {
    10: -14.3, 12.5: -11.2, 16: -8.5, 20: -6.2, 25: -4.4, 31.5: -3.0,
    40: -2.0, 50: -1.3, 63: -0.8, 80: -0.5, 100: -0.3, 125: -0.2,
    160: -0.1, 200: 0.0, 250: 0.0, 315: 0.0, 400: 0.0, 500: 0.0, 630: 0.0,
    800: 0.0, 1000: 0.0, 1250: 0.0, 1600: 0.0, 2000: -0.2, 2500: -0.3,
    3150: -0.5, 4000: -0.8, 5000: -1.3, 6300: -2.0, 8000: -3.0,
    10000: -4.4, 12500: -6.2, 16000: -8.5, 20000: -11.2,
}


def teorico(table, f):
    fs_orden = np.sort(np.array(list(table.keys())))
    vals = np.array([table[k] for k in fs_orden])
    return float(np.interp(f, fs_orden, vals))


def segmento_tono(x, f, dur_max):
    n = len(x)
    ciclos = max(30, int(np.floor(f * dur_max)))
    m = min(n, int(round(ciclos * FS / f)))
    inicio = (n - m) // 2
    return x[inicio:inicio + m]


def amplitud_tono(x, f, dur_max):
    seg = segmento_tono(x, f, dur_max)
    m = len(seg)
    t = np.arange(m) / FS
    ref = np.exp(-2j * np.pi * f * t)
    return 2 * np.abs(np.dot(seg, ref)) / m


def ruido_en_offset(x, f, dur_max, offset=40.0):
    return amplitud_tono(x, f + offset, dur_max)


def medir_tono(x, f, dur_max):
    az = amplitud_tono(x, f, dur_max)
    xa = filtA(x, FS)
    xc = filtC(x, FS)
    aa = amplitud_tono(xa, f, dur_max)
    ac = amplitud_tono(xc, f, dur_max)
    rzn = ruido_en_offset(x, f, dur_max)
    return az, aa, ac, rzn


def atenuacion(amp_filt, amp_z):
    if amp_z <= 0 or amp_filt <= 0:
        return float("nan")
    return 20 * np.log10(amp_filt / amp_z)


def formato_celda(val, teo, tol_ok=2.0, tol_acept=3.0):
    if np.isnan(val):
        return "     nan    "
    diff = abs(val - teo)
    if diff <= tol_ok:
        marca = "OK"
    elif diff <= tol_acept:
        marca = "acept"
    else:
        marca = "revisar"
    return f"{val:7.1f}({marca})"


def cargar_dispositivos():
    disp = query_devices()
    default_in = query_devices(kind="input")["index"]
    default_out = query_devices(kind="output")["index"]
    return default_in, default_out, disp


def prueba_sintetica(frecuencias):
    print()
    print("   == PRUEBA EN SOFTWARE (solo filtros, sin hardware) ==")
    print(f"   {'Freq':>7} {'Teo A-Z':>8} {'Med A-Z':>14} {'Teo C-Z':>8} {'Med C-Z':>14} {'Max|dA|,|dC|':>12}")
    peor = 0.0
    for f in frecuencias:
        n = int(round(FS / f)) * 600
        t = np.arange(n) / FS
        x = 0.8 * np.sin(2 * np.pi * f * t)
        az, aa, ac, _ = medir_tono(x, f, n / FS)
        da = atenuacion(aa, az)
        dc = atenuacion(ac, az)
        ta = teorico(TEO_A, f)
        tc = teorico(TEO_C, f)
        dmax = max(abs(da - ta), abs(dc - tc))
        peor = max(peor, dmax)
        print(f"   {f:7.0f} {ta:8.1f} {formato_celda(da, ta):14} {tc:8.1f} {formato_celda(dc, tc):14} {dmax:9.2f} dB")
    print(f"   Peor desvio (dB): {peor:.2f}")
    return peor


def prueba_hardware(frecuencias, dev_in, dev_out, dur=4.0, amp=0.3):
    import sounddevice as sd

    n = int(FS * dur)
    t = np.arange(n) / FS
    npad = int(0.05 * FS)
    fade = np.hanning(2 * npad)

    print()
    print("   == PRUEBA FISICA (parlante -> microfono) ==")
    print(f"   Entrada: {query_devices(dev_in)['name']}")
    print(f"   Salida : {query_devices(dev_out)['name']}")
    print(f"   {'Freq':>7} {'Z amp':>8} {'Teo A-Z':>8} {'Med A-Z':>15} {'Teo C-Z':>8} {'Med C-Z':>15} {'SNR dB':>7}")
    for f in frecuencias:
        tono = amp * np.sin(2 * np.pi * f * t)
        tono[:npad] *= fade[:npad]
        tono[-npad:] *= fade[-npad:]
        rec = sd.playrec(tono.astype(np.float32), FS, device=(dev_in, dev_out),
                         channels=1, dtype="float32")
        sd.wait()
        rec = rec.astype(np.float64)

        if rec.size == 0 or not np.isfinite(rec).all():
            print(f"   {f:7.0f}  falla en la captura -> omitido")
            continue

        pico = np.max(np.abs(rec))
        clip = "  [CLIP]" if pico > 0.95 else ""
        az, aa, ac, rzn = medir_tono(rec, f, dur=2.5)
        snr = np.nan if rzn <= 0 else 20 * np.log10(max(az, 1e-12) / max(rzn, 1e-12))
        da = atenuacion(aa, az)
        dc = atenuacion(ac, az)
        ta = teorico(TEO_A, f)
        tc = teorico(TEO_C, f)
        snr_txt = f"{snr:6.1f}" if np.isfinite(snr) else "   n/a"
        print(f"   {f:7.0f} {az:8.3f} {ta:8.1f} {formato_celda(da, ta):15} {tc:8.1f} {formato_celda(dc, tc):15} {snr_txt}{clip}")

    print()
    print("   Interpretacion: 'Med A-Z' / 'Med C-Z' son las atenuaciones medidas")
    print("   (nivel filtrado vs. nivel Z sin filtrar). Se comparan con IEC 61672-1.")
    print("   La respuesta del parlante/microfono se cancela en el cociente.")
    print("   Si el parlante no reproduce bien <200 Hz o >8 kHz el resultado sera ruidoso.")
    print("   Colocar el microfono cerca (5-20 cm) del parlante, sin obstrucciones ni feedback.")


def main():
    p = argparse.ArgumentParser(description="Verificacion de filtros A/C/Z de PySAMNS")
    p.add_argument("--sintetico", action="store_true",
                   help="Prueba en software: valida solo los filtros, sin mic/parlante")
    p.add_argument("--in", dest="dev_in", type=int, default=None, help="Indice dispositivo entrada")
    p.add_argument("--out", dest="dev_out", type=int, default=None, help="Indice dispositivo salida")
    p.add_argument("--frec", nargs="+", type=float,
                   default=[125, 250, 500, 1000, 2000, 4000, 8000],
                   help="Frecuencias de prueba (Hz)")
    args = p.parse_args()

    if args.sintetico:
        prueba_sintetica(args.frec)
        return

    dev_in = args.dev_in
    dev_out = args.dev_out
    if dev_in is None:
        dev_in = query_devices(kind="input")["index"]
    if dev_out is None:
        dev_out = query_devices(kind="output")["index"]

    if sdp_index_no_valido(dev_in, input_=True) or sdp_index_no_valido(dev_out, input_=False):
        print("Revisa los indices con: python -m sounddevice")
        sys.exit(1)

    prueba_sintetica(args.frec)
    prueba_hardware(args.frec, dev_in, dev_out)


def sdp_index_no_valido(idx, input_=True):
    try:
        info = query_devices(idx)
        canales = info["max_input_channels"] if input_ else info["max_output_channels"]
        return canales <= 0
    except Exception:
        return True


if __name__ == "__main__":
    main()