from PyQt5.QtWidgets import (QMainWindow, QApplication, QHBoxLayout, QVBoxLayout, QPushButton,
                             QLabel, QLineEdit, QGroupBox, QWidget, QMessageBox, QComboBox)

from PyQt5.QtGui import QIcon
from utils import norm
from funciones.consDisp import probar_frecuencias_entrada, frecuencias_comunes


class ConfigDispWin(QMainWindow):
    def __init__(self, vController, parent_cal_win=None):
        super().__init__()
        self.setWindowTitle("Configuración de dispositivos")
        self.setWindowIcon(QIcon('img/LogoCINTRA1.png'))
        screen = QApplication.primaryScreen().size()
        self.anchoX = screen.width()
        self.altoY = screen.height()
        self.setGeometry(norm(self.anchoX, self.altoY, 0.4, 0.4, 0.2, 0.2))

        with open("estilos.qss", "r", encoding='utf-8') as f:
            QApplication.instance().setStyleSheet(f.read())
        
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
        
        self.cmbDispositivosEntrada.currentIndexChanged.connect(self.actualizarFrecuenciaMuestreoEntrada)
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
        self.cmbBuffer.addItems(["128","256", "512", "1024", "2048", "4096", "8192"])
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
            
        self.actualizarFrecuenciasEntrada(self.cmbDispositivosEntrada.currentIndex())

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
        except Exception as e:
            print(f"Error al calcular latencia: {e}")
            self.lblLatencia.setText("Error") 
    def actualizarFrecuenciaMuestreoEntrada(self, idx):
        # Obtener la frecuencia de muestreo predeterminada del dispositivo seleccionado
        frec_muestreo = self.vController.cModel.getDispositivosEntradaRate()
        if idx < len(frec_muestreo):
            self.txtRate.setText(str(int(frec_muestreo[idx])))
        else:
            self.txtRate.setText("")
    
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
            
            # Cambiar el dispositivo de entrada si es diferente al actual
            if device_index_entrada != dispositivo_entrada_actual:
                print(f"Cambiando dispositivo de entrada de {dispositivo_entrada_actual} a {device_index_entrada}")
                
                # Cerrar el stream actual si existe
                if hasattr(self.vController.cModel, 'stream') and self.vController.cModel.stream is not None:
                    print("Cerrando stream actual...")
                    self.vController.cModel.stream.close()
                
                # Reinicializar el stream con el nuevo dispositivo
                print("Inicializando nuevo stream...")
                self.vController.cModel.initialize_audio_stream(device_index_entrada, rate, chunk)
                
                # Verificar que el cambio se aplicó correctamente
                nuevo_dispositivo_entrada = self.vController.cModel.getDispositivoActual()
                print(f"Dispositivo entrada después del cambio: {nuevo_dispositivo_entrada}")
                
                if nuevo_dispositivo_entrada == device_index_entrada:
                    print("✅ Cambio de dispositivo de entrada exitoso")
                    
                    
                else:
                    print("⚠️ El cambio de dispositivo de entrada no se aplicó correctamente")
            else:
                print("No se requiere cambio de dispositivo de entrada")
            
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
            
            self.close()
            
        except Exception as e:
            print(f"Error al aplicar configuración: {e}")
            QMessageBox.critical(self, "Error", f"Error al aplicar configuración de dispositivo: {e}")
        