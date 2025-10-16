import subprocess
import os
from power_guard import keep_awake, allow_sleep
import atexit
from controller import controlador
from db import crear_tabla

def enable_lab_mode():
    """Configure system power settings for lab mode using Windows API."""
    try:
        # Set high performance power plan
        subprocess.run(['powercfg', '/setactive', 'SCHEME_MIN'], check=True)
        # Disable sleep modes
        subprocess.run(['powercfg', '/change', 'standby-timeout-ac', '0'], check=True)
        subprocess.run(['powercfg', '/change', 'standby-timeout-dc', '0'], check=True)
        # Disable display timeout
        subprocess.run(['powercfg', '/change', 'monitor-timeout-ac', '0'], check=True)
        subprocess.run(['powercfg', '/change', 'monitor-timeout-dc', '0'], check=True)
        print("✅ Lab mode activated successfully")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Warning: Could not fully configure lab mode: {e}")

def restore_lab_mode():
    """Restore default power settings."""
    try:
        # Restore balanced power plan
        subprocess.run(['powercfg', '/setactive', 'SCHEME_BALANCED'], check=True)
        # Set reasonable defaults (30 minutes for display, 1 hour for sleep)
        subprocess.run(['powercfg', '/change', 'standby-timeout-ac', '60'], check=True)
        subprocess.run(['powercfg', '/change', 'standby-timeout-dc', '30'], check=True)
        subprocess.run(['powercfg', '/change', 'monitor-timeout-ac', '30'], check=True)
        subprocess.run(['powercfg', '/change', 'monitor-timeout-dc', '15'], check=True)
        print("✅ Normal power settings restored")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Warning: Could not fully restore power settings: {e}")

if __name__ == "__main__":
    keep_awake()
    atexit.register(allow_sleep)
    atexit.register(restore_lab_mode)  # restaurar cuando se cierre el programa

    enable_lab_mode()  # activar modo laboratorio

    crear_tabla()
    SAMNS = controlador()
    SAMNS.cVista.animation()
