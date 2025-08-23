from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import ( QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QSpinBox, QLabel, QPushButton, QApplication, QDateEdit, QMessageBox,
                            QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import QTime, pyqtSignal, QDate
from PyQt5.QtGui import QIcon
from utils import norm
from db import  guardar_registro, leer_proximas_grabaciones




class ProgramarWin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Programar grabación automática")
        screen = QApplication.primaryScreen().size()
        anchoX = screen.width()
        altoY = screen.height()
        self.setGeometry(norm(anchoX, altoY, 0.35, 0.35, 0.3, 0.3))

        with open("estilos.qss", "r", encoding='utf-8') as f:
            QApplication.instance().setStyleSheet(f.read())
            
        central_widget = QWidget()
        layoutVInicio = QVBoxLayout()
        layoutVFin = QVBoxLayout()
        layoutVDuracion = QVBoxLayout()
        layoutHorizontal = QHBoxLayout()
        layout = QVBoxLayout(central_widget)
        
        lbl_info = QLabel(
            "Se programará la grabación automática de audio\n"
            "para el día y rango de tiempo seleccionados"
        )
        lbl_info.setStyleSheet("font-size: 14pt; font-weight: bold;")
        lbl_info.setWordWrap(True)
        layout.addWidget(lbl_info)

        # Selector de fecha Inicio
        self.date_start_picker = QDateEdit()
        self.date_start_picker.setCalendarPopup(True)
        self.date_start_picker.setDate(QDate.currentDate())
        layoutVInicio.addWidget(QLabel("Selecciona el día de Inicio:"))
        layoutVInicio.addWidget(self.date_start_picker)

        # Picker de tiempo de inicio
        layoutVInicio.addWidget(QLabel("Hora de inicio:"))
        self.start_picker = CustomTimePicker()
        layoutVInicio.addWidget(self.start_picker)

        "selector de duracion"
        self.duracion_label = QLabel("Duración de la grabación:")
        
        
        
        # Selector de fecha Fin
        self.date_end_picker = QDateEdit()
        self.date_end_picker.setCalendarPopup(True)
        self.date_end_picker.setDate(QDate.currentDate())
        layoutVFin.addWidget(QLabel("Selecciona el día de Fin:"))
        layoutVFin.addWidget(self.date_end_picker)

        # Picker de tiempo de fin
        layoutVFin.addWidget(QLabel("Hora de fin:"))
        self.end_picker = CustomTimePicker()
        layoutVFin.addWidget(self.end_picker)

        
        
        # Botón para guardar la programación 
        mas_img_path = "img/mas.png"
        self.save_btn = QPushButton("")
        self.save_btn.setIcon(QIcon(mas_img_path))
        self.save_btn.clicked.connect(self.guardar_registro)
        layout.addWidget(self.save_btn)

        # Tabla de registros
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Fecha inicio", "Hora inicio", "Fecha fin", "Hora fin"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(QLabel("Proximas grabaciones:"))
        layout.addWidget(self.table)


        self.setCentralWidget(central_widget)

        self.cargar_registros()

    def guardar_registro(self):
        datos = self.get_programacion()
        # Obtener fecha y hora actual
        ahora = QDate.currentDate().toString("yyyy-MM-dd") + " " + QTime.currentTime().toString("HH:mm:ss")
        inicio = datos["fecha_inicio"] + " " + datos["inicio"]
        fin = datos["fecha_fin"] + " " + datos["fin"]
        
        # Validar que inicio sea mayor al actual
        from datetime import datetime
        formato = "%Y-%m-%d %H:%M:%S"
        if datetime.strptime(inicio, formato) <= datetime.strptime(ahora, formato):
            QMessageBox.warning(self, "Error", "La fecha y hora de inicio deben ser posteriores al momento actual.")
            return

        if datetime.strptime(fin, formato) <= datetime.strptime(inicio, formato):
            QMessageBox.warning(self, "Error", "La fecha y hora de fin deben ser posteriores a la fecha y hora de inicio.")
            return
        
        guardar_registro(datos["fecha_inicio"], datos["inicio"],datos["fecha_fin"], datos["fin"])
        QMessageBox.information(self, "Éxito", "Registro guardado correctamente.")
        self.cargar_registros()


    def get_programacion(self):
        return {
            "fecha_inicio": self.date_start_picker.date().toString("yyyy-MM-dd"),
            "inicio": self.start_picker.get_time().toString("HH:mm:ss"),
            "fecha_fin": self.date_end_picker.date().toString("yyyy-MM-dd"),
            "fin": self.end_picker.get_time().toString("HH:mm:ss")
        }
    
    def cargar_registros(self):
        registros = leer_proximas_grabaciones()
        self.table.setRowCount(len(registros))
        for row, (fechaIni, inicio,fechaFin, fin) in enumerate(registros):
            self.table.setItem(row, 0, QTableWidgetItem(fechaIni))
            self.table.setItem(row, 1, QTableWidgetItem(inicio))
            self.table.setItem(row, 2, QTableWidgetItem(fechaFin))
            self.table.setItem(row, 3, QTableWidgetItem(fin))



class CustomTimePicker(QWidget):
    """TimePicker personalizado con SpinBoxes"""
    timeChanged = pyqtSignal(QTime)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        
        # Layout horizontal para los controles de tiempo
        time_layout = QVBoxLayout()
        
        # SpinBox para horas
        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 23)
        self.hour_spin.setValue(QTime.currentTime().hour())
        #self.hour_spin.setSuffix(" h")
        self.hour_spin.valueChanged.connect(self.on_time_changed)
        
        # SpinBox para minutos
        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 59)
        self.minute_spin.setValue(QTime.currentTime().minute())
        #self.minute_spin.setSuffix(" min")
        self.minute_spin.valueChanged.connect(self.on_time_changed)
        
        # SpinBox para segundos
        self.second_spin = QSpinBox()
        self.second_spin.setRange(0, 59)
        self.second_spin.setValue(QTime.currentTime().second())
        #self.second_spin.setSuffix(" seg")
        self.second_spin.valueChanged.connect(self.on_time_changed)
        
        time_layout.addWidget(QLabel("Hora:"))
        time_layout.addWidget(self.hour_spin)
        time_layout.addWidget(QLabel("Minuto:"))
        time_layout.addWidget(self.minute_spin)
        time_layout.addWidget(QLabel("Segundo:"))
        time_layout.addWidget(self.second_spin)
        
        layout.addLayout(time_layout)
        
        # Mostrar tiempo seleccionado
        current_time = QTime(self.hour_spin.value(), self.minute_spin.value(), self.second_spin.value())
        self.time_label = QLabel(f"Tiempo seleccionado: {current_time.toString('HH:mm:ss')}")
        layout.addWidget(self.time_label)
        
        # Botones de control
        button_layout = QHBoxLayout()
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def on_time_changed(self):
        time = QTime(self.hour_spin.value(), self.minute_spin.value(), self.second_spin.value())
        self.time_label.setText(f"Tiempo seleccionado: {time.toString('HH:mm:ss')}")
        self.timeChanged.emit(time)
    
    def get_time(self):
        return QTime(self.hour_spin.value(), self.minute_spin.value(), self.second_spin.value())
    
    def set_time(self, time):
        self.hour_spin.setValue(time.hour())
        self.minute_spin.setValue(time.minute())
        self.second_spin.setValue(time.second())
    
    def set_current_time(self):
        current = QTime.currentTime()
        self.set_time(current)
    
    def reset_time(self):
        self.set_time(QTime(0, 0, 0))