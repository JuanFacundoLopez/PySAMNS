import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QHBoxLayout, QVBoxLayout, QPushButton,
                             QLabel, QLineEdit, QGroupBox, QWidget, QMessageBox, QComboBox)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from utils import norm
from funciones.consDisp import probar_frecuencias_entrada, frecuencias_comunes


class ConfigDispWin(QMainWindow):
    frecuenciaMuestreoCambiada = pyqtSignal(int)
    
    def __init__(self, vController, parent_cal_win=None):
        super().__init__()
        self.setWindowTitle("Configuración de dispositivos")
        self.setWindowIcon(QIcon('img/LogoCINTRA1.png'))
        screen = QApplication.primaryScreen().size()
        self.anchoX = screen.width()
        self.altoY = screen.height()
        self.setGeometry(norm(self.anchoX, self.altoY, 0.4, 0.4, 0.2, 0.2))

        # Handle stylesheet path for both development and frozen executable
        if getattr(sys, 'frozen', False):
            # If running as compiled executable
            base_path = sys._MEIPASS
        else:
            # If running in development
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        # Path to stylesheet
        estilos_path = os.path.join(base_path, 'estilos.qss')
        
        try:
            with open(estilos_path, "r", encoding='utf-8') as f:
                QApplication.instance().setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Warning: Could not load stylesheet at {estilos_path}")
        
        self.vController = vController
        self.parent_cal_win = parent_cal_win
        
        
        # Widget central y layout principal
        centralWidget = QWidget()
        mainLayout = QVBoxLayout(centralWidget)

        # Layout de selección de dispositivo Entrada
        dispGroupEntrada = QGroupBox("Dispositivo de entrada")
        dispLayoutEntrada = QHBoxLayout()
        self.cmbDispositivosEntrada = QComboBox()
        # Obtener lista de dispositivos del modelo
        dispositivosEntrada = self.vController.cModel.getDispositivosEntrada('nombre')
        self.cmbDispositivosEntrada.addItems(dispositivosEntrada)
        
        # Obtener el dispositivo actual y seleccionarlo en el ComboBox
        dispositivo_actual = self.vController.cModel.getDispositivoActual()
        if dispositivo_actual is not None:
            # Buscar el índice del dispositivo actual en la lista de dispositivos
            indices = self.vController.cModel.getDispositivosEntrada('indice')
            try:
                idx_actual = indices.index(dispositivo_actual)
                self.cmbDispositivosEntrada.setCurrentIndex(idx_actual)
            except ValueError:
                # Si no se encuentra el dispositivo actual, usar el primer dispositivo
                self.cmbDispositivosEntrada.setCurrentIndex(0)
        else:
            # Si no hay dispositivo actual, usar el primer dispositivo
            self.cmbDispositivosEntrada.setCurrentIndex(0)
        
        # La conexión currentIndexChanged ahora solo va a actualizarFrecuenciasEntrada (línea 132)
        #self.cmbDispositivosEntrada.currentIndexChanged.connect(self.actualizarFrecuenciaMuestreoEntrada)
        #self.lblSelEnt = QLabel("Seleccionar:")
        #dispLayoutEntrada.addWidget(self.lblSelEnt)
        dispLayoutEntrada.addWidget(self.cmbDispositivosEntrada)
        dispGroupEntrada.setLayout(dispLayoutEntrada)
        mainLayout.addWidget(dispGroupEntrada)
        
        # Layout de selección de dispositivo Salida
        dispGroupSalida = QGroupBox("Dispositivo de salida")
        dispLayoutSalida = QHBoxLayout()
        self.cmbDispositivosSalida = QComboBox()
        # Obtener lista de dispositivos de salida del modelo
        dispositivosSalida = self.vController.cModel.getDispositivosSalida('nombre')
        self.cmbDispositivosSalida.addItems(dispositivosSalida)
        
        # Obtener el dispositivo de salida actual y seleccionarlo en el ComboBox
        dispositivo_salida_actual = self.vController.cModel.getDispositivoSalidaActual()
        if dispositivo_salida_actual is not None:
            # Buscar el índice del dispositivo actual en la lista de dispositivos
            indicesSalida = self.vController.cModel.getDispositivosSalida('indice')
            try:
                idx_actual = indicesSalida.index(dispositivo_salida_actual)
                self.cmbDispositivosSalida.setCurrentIndex(idx_actual)
            except ValueError:
                # Si no se encuentra el dispositivo actual, usar el primer dispositivo
                self.cmbDispositivosSalida.setCurrentIndex(0)
        else:
            # Si no hay dispositivo actual, usar el primer dispositivo
            self.cmbDispositivosSalida.setCurrentIndex(0)
        
        #self.lblSelSal= QLabel("Seleccionar:")
        #dispLayoutSalida.addWidget(self.lblSelSal)
        dispLayoutSalida.addWidget(self.cmbDispositivosSalida)
        dispGroupSalida.setLayout(dispLayoutSalida)
        mainLayout.addWidget(dispGroupSalida)
        
        # Layout de configuración de rate y chunk
        rateChunkGroup = QGroupBox("Parámetros de audio")
        rateChunkLayoutVert = QVBoxLayout()
        rateChunkLayoutH1 = QHBoxLayout()
        rateChunkLayoutH2 = QHBoxLayout()
        #self.txtRate = QLineEdit(str(self.vController.cModel.rate))
        #self.txtRate.setEnabled(False)  # Deshabilitado para evitar cambios
        self.cmbRate = QComboBox()
        #self.txtChunk = QLineEdit(str(self.vController.cModel.chunk))
        self.cmbBuffer = QComboBox()
        self.cmbBuffer.addItems(["2048", "4096", "8192"])
        self.lblRate = QLabel("Frecuencia de muestreo (Hz):")
        rateChunkLayoutH1.addWidget(self.lblRate)
        rateChunkLayoutH1.addWidget(self.cmbRate)
        self.lblChunk = QLabel("Buffer (samp):")
        rateChunkLayoutH1.addWidget(self.lblChunk)
        rateChunkLayoutH1.addWidget(self.cmbBuffer)
        self.lblLatenciaTitle = QLabel("Latencia dada:")
        self.lblLatencia = QLabel("N/A")
        rateChunkLayoutH2.addWidget(self.lblLatenciaTitle)
        rateChunkLayoutH2.addWidget(self.lblLatencia)
        rateChunkLayoutVert.addLayout(rateChunkLayoutH1)
        rateChunkLayoutVert.addLayout(rateChunkLayoutH2)
        rateChunkGroup.setLayout(rateChunkLayoutVert)
        mainLayout.addWidget(rateChunkGroup)
        
        # Conectar señales DESPUÉS de inicializar valores
        self.cmbDispositivosEntrada.currentIndexChanged.connect(self.actualizarFrecuenciasEntrada)
        self.cmbBuffer.currentIndexChanged.connect(self.actualizarLatencia)
        self.cmbRate.currentIndexChanged.connect(self.actualizarLatencia)

        # Botones Agregar y Cancelar
        botonesLayout = QHBoxLayout()
        self.btnDispAgregar = QPushButton("Aplicar")
        self.btnDispAgregar.clicked.connect(self.aplicarConfiguracionDispositivo)
        self.btnDispCancelar = QPushButton("Cancelar")
        self.btnDispCancelar.clicked.connect(self.close)
        botonesLayout.addWidget(self.btnDispCancelar)
        botonesLayout.addWidget(self.btnDispAgregar)
        mainLayout.addLayout(botonesLayout)

        for boton in [self.btnDispAgregar, self.btnDispCancelar]:
            boton.setProperty("class", "ventanasSec")
        
        for lbl in [self.lblChunk, self.lblRate, self.lblLatenciaTitle]:
            lbl.setProperty("class", "ventanasSecLabelDestacado")
            
        for cmb in [self.cmbDispositivosEntrada, self.cmbDispositivosSalida, self.cmbBuffer, self.cmbRate]:
            cmb.setProperty("class", "ventanasSec")
        
        # IMPORTANTE: Bloquear señales mientras inicializamos para evitar triggers no deseados
        self.cmbDispositivosEntrada.blockSignals(True)
        self.cmbRate.blockSignals(True)
        self.cmbBuffer.blockSignals(True)
        
        # Inicializar frecuencias del dispositivo actual
        self.actualizarFrecuenciasEntrada(self.cmbDispositivosEntrada.currentIndex())
        
        # Seleccionar el buffer actual del modelo
        # Forzar un mínimo de 2048 para que no aparezca 1024 ni valores menores
        buffer_actual_val = int(getattr(self.vController.cModel, "chunk", 2048))
        if buffer_actual_val < 2048:
            buffer_actual_val = 2048
            # Opcional: actualizar también el modelo para mantener coherencia
            try:
                self.vController.cModel.chunk = buffer_actual_val
            except Exception:
                pass

        buffer_actual = str(buffer_actual_val)
        idx_buffer = self.cmbBuffer.findText(buffer_actual)
        if idx_buffer >= 0:
            self.cmbBuffer.setCurrentIndex(idx_buffer)
        else:
            # Si por alguna razón el valor no está, seleccionar el primer elemento (2048)
            self.cmbBuffer.setCurrentIndex(0)
        
        # Desbloquear señales después de inicializar todo
        self.cmbDispositivosEntrada.blockSignals(False)
        self.cmbRate.blockSignals(False)
        self.cmbBuffer.blockSignals(False)

        self.setCentralWidget(centralWidget)

    def actualizarLatencia(self):
        try:
            buffer = int(self.cmbBuffer.currentText())
            rate_text = self.cmbRate.currentText()
            if not rate_text.isdigit() or int(rate_text) == 0:
                self.lblLatencia.setText("N/A")
                return
            rate = int(rate_text)
            latencia_ms = buffer / rate * 1000
            self.lblLatencia.setText(f"{latencia_ms:.2f} ms")

            # Emitir señal
            self.frecuenciaMuestreoCambiada.emit(rate)

        except Exception as e:
            print(f"Error al calcular latencia: {e}")
            self.lblLatencia.setText("Error")
            
            
    # La función actualizarFrecuenciaMuestreoEntrada ya no es necesaria
    # porque actualizarFrecuenciasEntrada maneja la actualización del cmbRate
    
    def actualizarFrecuenciasEntrada(self, idx):
        try:
            # Obtener el índice real del dispositivo de entrada
            indices_entrada = self.vController.cModel.getDispositivosEntrada('indice')
            if idx >= len(indices_entrada):
                return
            device_index = indices_entrada[idx]

            # Usar el controller para acceder a la función de prueba de frecuencias
            frecuencias_validas = self.vController.probar_frecuencias_entrada(device_index, frecuencias_comunes)

            # Actualizar el comboBox de frecuencias
            self.cmbRate.clear()
            if frecuencias_validas:
                for f in frecuencias_validas:
                    self.cmbRate.addItem(str(int(f)))
                
                # Seleccionar la frecuencia actual del modelo
                rate_actual = str(self.vController.cModel.rate)
                idx_rate = self.cmbRate.findText(rate_actual)
                if idx_rate >= 0:
                    self.cmbRate.setCurrentIndex(idx_rate)
                else:
                    # Si la frecuencia actual no está en la lista de válidas, seleccionar la primera
                    self.cmbRate.setCurrentIndex(0)
            else:
                self.cmbRate.addItem("Ninguna compatible")
            self.actualizarLatencia()
        except Exception as e:
            print(f"Error al actualizar frecuencias de entrada: {e}")
            self.cmbRate.clear()
            self.cmbRate.addItem("Error")

               
    def aplicarConfiguracionDispositivo(self):
        try:
            # Obtener valores seleccionados
            dispositivo_entrada_idx = self.cmbDispositivosEntrada.currentIndex()
            dispositivo_salida_idx = self.cmbDispositivosSalida.currentIndex()
            rate = int(self.cmbRate.currentText())
            chunk = int(self.cmbBuffer.currentText())
            
            # Obtener el índice real del dispositivo de entrada seleccionado
            indices_entrada = self.vController.cModel.getDispositivosEntrada('indice')
            device_index_entrada = indices_entrada[dispositivo_entrada_idx] if dispositivo_entrada_idx < len(indices_entrada) else None
            
            # Obtener el índice real del dispositivo de salida seleccionado
            indices_salida = self.vController.cModel.getDispositivosSalida('indice')
            device_index_salida = indices_salida[dispositivo_salida_idx] if dispositivo_salida_idx < len(indices_salida) else None
            
            # Obtener el dispositivo actual antes del cambio
            dispositivo_entrada_actual = self.vController.cModel.getDispositivoActual()
            dispositivo_salida_actual = self.vController.cModel.getDispositivoSalidaActual()
            
            print(f"Dispositivo entrada actual: {dispositivo_entrada_actual}")
            print(f"Dispositivo entrada seleccionado: {device_index_entrada}")
            print(f"Dispositivo salida actual: {dispositivo_salida_actual}")
            print(f"Dispositivo salida seleccionado: {device_index_salida}")
            print(f"Rate: {rate}, Chunk: {chunk}")
            
            # Cambiar el dispositivo de entrada o, si es el mismo, al menos actualizar rate/chunk
            try:
                if device_index_entrada != dispositivo_entrada_actual:
                    print(f"Cambiando dispositivo de entrada de {dispositivo_entrada_actual} a {device_index_entrada}")
                else:
                    print("Actualizando parámetros de audio (rate/chunk) para el mismo dispositivo de entrada")

                # initialize_audio_stream maneja el cierre del stream anterior y valida parámetros
                print("Inicializando / actualizando stream de entrada...")
                self.vController.cModel.initialize_audio_stream(device_index_entrada, rate, chunk)

                # Verificar que el cambio se aplicó correctamente
                nuevo_dispositivo_entrada = self.vController.cModel.getDispositivoActual()
                print(f"Dispositivo entrada después del cambio: {nuevo_dispositivo_entrada}")

                if nuevo_dispositivo_entrada == device_index_entrada:
                    print("✅ Parámetros de entrada aplicados correctamente")
                else:
                    print("⚠️ El cambio de dispositivo de entrada no se aplicó correctamente")
                    QMessageBox.warning(
                        self,
                        "Advertencia",
                        "El dispositivo se configuró pero puede que no esté funcionando correctamente.",
                    )
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Error al configurar dispositivo/parámetros de entrada: {error_msg}")

                # Mensaje más amigable para el usuario
                if "Unanticipated host error" in error_msg or "-9999" in error_msg:
                    QMessageBox.critical(
                        self,
                        "Error de Dispositivo",
                        f"No se pudo inicializar el dispositivo de audio seleccionado.\n\n"
                        f"Posibles causas:\n"
                        f"• El dispositivo está siendo usado por otra aplicación\n"
                        f"• Los parámetros (Rate: {rate} Hz, Buffer: {chunk}) no son compatibles\n"
                        f"• El dispositivo no está disponible\n\n"
                        f"Intenta:\n"
                        f"• Cerrar otras aplicaciones que usen audio\n"
                        f"• Seleccionar una frecuencia diferente\n"
                        f"• Probar con otro dispositivo",
                    )
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Error al cambiar dispositivo de entrada o parámetros de audio:\n{error_msg}",
                    )
                return  # No continuar si falla la configuración de entrada
            
            # Cambiar el dispositivo de salida si es diferente al actual
            if device_index_salida != dispositivo_salida_actual:
                print(f"Cambiando dispositivo de salida de {dispositivo_salida_actual} a {device_index_salida}")
                
                # Actualizar el dispositivo de salida en el modelo
                self.vController.cModel.setDispositivoSalida(device_index_salida)
                
                # Verificar que el cambio se aplicó correctamente
                nuevo_dispositivo_salida = self.vController.cModel.getDispositivoSalidaActual()
                print(f"Dispositivo salida después del cambio: {nuevo_dispositivo_salida}")
                
                if nuevo_dispositivo_salida == device_index_salida:
                    print("✅ Cambio de dispositivo de salida exitoso")
                    # Actualizar el label con el nuevo nombre del dispositivo de salida
                    if self.parent_cal_win is not None:
                        self.parent_cal_win.actualizarNombreDispositivoSalida()
                else:
                    print("⚠️ El cambio de dispositivo de salida no se aplicó correctamente")
            else:
                print("No se requiere cambio de dispositivo de salida")
                
            # Actualizar el label con el nuevo nombre del dispositivo
            if self.parent_cal_win is not None:
                self.parent_cal_win.actualizarNombreDispositivos()

            # --- Sincronizar parámetros FFT por defecto con la configuración del dispositivo ---
            # De esta forma, el "número de muestras" (chunk) elegido aquí queda guardado
            # y se usa como valor por defecto en los gráficos/FFT, hasta que
            # la ventana de configuración de gráfico lo cambie explícitamente.
            try:
                if hasattr(self.vController, "cVista"):
                    self.vController.cVista.var_fft_rate = rate
                    self.vController.cVista.var_fft_n_samples = chunk
            except Exception as e:
                print(f"Advertencia al actualizar parámetros FFT en la vista: {e}")

            self.close()
            
        except Exception as e:
            print(f"Error al aplicar configuración: {e}")
            QMessageBox.critical(self, "Error", f"Error al aplicar configuración de dispositivo: {e}")


    def closeEvent(self, event):
        self.vController.ventanas_abiertas["config_disp"] = None
        event.accept()        