# Script para construir el ejecutable de PySAMNS

# Configuración
$env:PYTHONIOENCODING = "utf-8"
$projectDir = $PSScriptRoot
$distDir = "$projectDir\dist"
$buildDir = "$projectDir\build"
$specFile = "$projectDir\PySAMNS.spec"

# Crear directorios si no existen
if (-not (Test-Path -Path $distDir)) {
    New-Item -ItemType Directory -Path $distDir | Out-Null
}
if (-not (Test-Path -Path $buildDir)) {
    New-Item -ItemType Directory -Path $buildDir | Out-Null
}

# Instalar dependencias
Write-Host "Instalando dependencias..."
pip install -r requirements.txt

# Limpiar builds anteriores
Write-Host "Limpiando builds anteriores..."
if (Test-Path -Path $distDir) {
    Remove-Item -Path "$distDir\*" -Recurse -Force
}
if (Test-Path -Path $buildDir) {
    Remove-Item -Path "$buildDir\*" -Recurse -Force
}

# Construir el ejecutable
Write-Host "Construyendo el ejecutable..."
pyinstaller --clean --noconfirm $specFile

# Verificar si la compilación fue exitosa
if ($LASTEXITCODE -eq 0) {
    Write-Host "¡Compilación completada con éxito!" -ForegroundColor Green
    Write-Host "El ejecutable se encuentra en: $distDir\PySAMNS" -ForegroundColor Cyan
    
    # Abrir el directorio de salida
    explorer $distDir
} else {
    Write-Host "Error durante la compilación. Código de salida: $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}
