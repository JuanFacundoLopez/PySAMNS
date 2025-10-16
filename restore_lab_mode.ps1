# restore_lab_mode.ps1
Write-Host "♻️ Restaurando configuración normal..."

# Activar nuevamente la hibernación
powercfg /hibernate on

# Restaurar suspensión automática (por ejemplo, 30 minutos)
powercfg /change standby-timeout-ac 30
powercfg /change standby-timeout-dc 15

# Restaurar apagado de pantalla (10 minutos)
powercfg /change monitor-timeout-ac 10
powercfg /change monitor-timeout-dc 5

# Restaurar suspensión selectiva de USB
powercfg -setacvalueindex SCHEME_CURRENT SUB_USB USBSELECTIVE SUSPEND_ENABLED
powercfg -setdcvalueindex SCHEME_CURRENT SUB_USB USBSELECTIVE SUSPEND_ENABLED
powercfg /setactive SCHEME_CURRENT

Write-Host "✅ Configuración de energía restaurada."
