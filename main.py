import subprocess
import os
from power_guard import keep_awake, allow_sleep
import atexit
from controller import controlador
from db import crear_tabla

def enable_lab_mode():
    """Ejecuta el script PowerShell que configura el modo laboratorio."""
    script_path = os.path.join(os.path.dirname(__file__), "enable_lab_mode.ps1")
    try:
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path], check=True)
    except Exception as e:
        print(f"⚠️ No se pudo aplicar el modo laboratorio: {e}")

def restore_lab_mode():
    """Restaura configuración de energía normal."""
    script_path = os.path.join(os.path.dirname(__file__), "restore_lab_mode.ps1")
    try:
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path], check=True)
    except Exception as e:
        print(f"⚠️ No se pudo restaurar configuración: {e}")

if __name__ == "__main__":
    keep_awake()
    atexit.register(allow_sleep)
    atexit.register(restore_lab_mode)  # restaurar cuando se cierre el programa

    enable_lab_mode()  # activar modo laboratorio

    crear_tabla()
    SAMNS = controlador()
    SAMNS.cVista.animation()
