# enable_lab_mode.ps1
Write-Host "🔧 Activando modo laboratorio de medición de audio..."

# 1. Cambiar al plan de energía de alto rendimiento
Write-Host "→ Estableciendo plan de energía: Alto rendimiento"
powercfg /setactive SCHEME_MIN

# 2. Desactivar hibernación
Write-Host "→ Desactivando hibernación"
powercfg /hibernate off

# 3. Desactivar suspensión automática (AC y batería)
Write-Host "→ Desactivando suspensión automática"
powercfg /change standby-timeout-ac 0
powercfg /change standby-timeout-dc 0

# 4. Desactivar apagado de pantalla por inactividad
Write-Host "→ Desactivando apagado de pantalla"
powercfg /change monitor-timeout-ac 0
powercfg /change monitor-timeout-dc 0

# 5. Desactivar suspensión selectiva de USB
Write-Host "→ Desactivando suspensión selectiva de USB"
powercfg -setacvalueindex SCHEME_CURRENT SUB_USB USBSELECTIVE SUSPEND_DISABLED
powercfg -setdcvalueindex SCHEME_CURRENT SUB_USB USBSELECTIVE SUSPEND_DISABLED
powercfg /setactive SCHEME_CURRENT

# 6. (Opcional) Evitar suspensión de disco
Write-Host "→ Evitando suspensión de disco"
powercfg /change disk-timeout-ac 0
powercfg /change disk-timeout-dc 0

# 7. Mostrar confirmación
Write-Host "✅ Modo laboratorio activado. El sistema no entrará en suspensión ni ahorro de energía durante la medición."
