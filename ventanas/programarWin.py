from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import ( QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QSpinBox, QLabel, QPushButton, QApplication, QDateEdit, QMessageBox,
                            QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox)
from PyQt5.QtCore import QTime, pyqtSignal, QDate, QDateTime
from PyQt5.QtGui import QIcon
from utils import norm
from db import guardar_registro, leer_proximas_grabaciones, borrar_registro
from datetime import timedelta




class ProgramarWin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Programar grabación automática")
        screen = QApplication.primaryScreen().size()
        anchoX = screen.width()
        altoY = screen.height()
        self.setGeometry(norm(anchoX, altoY, 0.35, 0.15, 0.3, 0.4))

        with open("estilos.qss", "r", encoding='utf-8') as f:
            QApplication.instance().setStyleSheet(f.read())
            
        central_widget = QWidget()
        layoutVInicio = QVBoxLayout()
        layoutHInicio = QHBoxLayout()
        layoutVFin = QVBoxLayout()
        layoutHFin = QHBoxLayout()
        layoutVDuracion = QVBoxLayout()
        layoutHorizontal = QVBoxLayout()
        layout = QVBoxLayout(central_widget)
        
        # lbl_info = QLabel(
        #     "Se programará la grabación automática de audio\n"
        #     "para el día y rango de tiempo seleccionados"
        # )
        # lbl_info.setStyleSheet("font-size: 14pt; font-weight: bold;")
        # lbl_info.setWordWrap(True)
        # layout.addWidget(lbl_info)

        # Selector de fecha Inicio
        group_box_inicio = QGroupBox("Inicio")
        group_box_inicio.setLayout(layoutVInicio)

        self.lbl_date_start = QLabel("Fecha:")
        self.date_start_picker = QDateEdit()
        self.date_start_picker.setCalendarPopup(True)
        self.date_start_picker.setDate(QDate.currentDate())
        layoutHInicio.addWidget(self.lbl_date_start)
        layoutHInicio.addWidget(self.date_start_picker)
        layoutVInicio.addLayout(layoutHInicio)

        # Picker de tiempo de inicio
        #self.lbl_time_start = QLabel("Hora de inicio:")
        #layoutVInicio.addWidget(self.lbl_time_start)
        self.start_picker = CustomTimePicker()
        layoutVInicio.addWidget(self.start_picker)
        
        # Selector de fecha Fin
        group_box_fin = QGroupBox("Fin")
        group_box_fin.setLayout(layoutVFin)

        self.lbl_date_end = QLabel("Fecha:")
        self.date_end_picker = QDateEdit()
        self.date_end_picker.setCalendarPopup(True)
        self.date_end_picker.setDate(QDate.currentDate())
        layoutHFin.addWidget(self.lbl_date_end)
        layoutHFin.addWidget(self.date_end_picker)
        layoutVFin.addLayout(layoutHFin)

        # Picker de tiempo de fin
        self.end_picker = CustomTimePicker()
        layoutVFin.addWidget(self.end_picker)

        #selector de duracion
        group_box_duracion = QGroupBox("Duración")
        group_box_duracion.setLayout(layoutVDuracion)
        
        self.duracion_picker = CustomTimePicker(esDuracion=True)
        layoutVDuracion.addWidget(self.duracion_picker)


        
        # Botón para guardar la programación 
        mas_img_path = "img/mas.png"
        self.save_btn = QPushButton("")
        self.save_btn.setIcon(QIcon(mas_img_path))
        self.save_btn.clicked.connect(self.guardar_registro)
        
        borrar_img_path = "img/borrar.png"
        
        # Tabla de registros
        self.lbl_table_title = QLabel("Próximas grabaciones programadas:")
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Fecha inicio", "Hora inicio", "Fecha fin", "Hora fin","Duracion", "Eliminar"
        ])
        self.table.setMinimumHeight(250)  # <-- Ajusta el valor según lo que necesites
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layoutHorizontal.addWidget(group_box_inicio)
        layoutHorizontal.addWidget(group_box_fin)
        layoutHorizontal.addWidget(group_box_duracion)
        layout.addLayout(layoutHorizontal)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.lbl_table_title)
        layout.addWidget(self.table)


        self.setCentralWidget(central_widget)

        self.cargar_registros()

        # Conectar señales para sincronización
        self.date_start_picker.dateChanged.connect(self.actualizar_duracion_desde_fechas)
        self.start_picker.hour_spin.valueChanged.connect(self.actualizar_duracion_desde_fechas)
        self.start_picker.minute_spin.valueChanged.connect(self.actualizar_duracion_desde_fechas)
        self.start_picker.second_spin.valueChanged.connect(self.actualizar_duracion_desde_fechas)

        self.date_end_picker.dateChanged.connect(self.actualizar_duracion_desde_fechas)
        self.end_picker.hour_spin.valueChanged.connect(self.actualizar_duracion_desde_fechas)
        self.end_picker.minute_spin.valueChanged.connect(self.actualizar_duracion_desde_fechas)
        self.end_picker.second_spin.valueChanged.connect(self.actualizar_duracion_desde_fechas)

        self.duracion_picker.days_spin.valueChanged.connect(self.actualizar_fin_desde_duracion)
        self.duracion_picker.hour_spin.valueChanged.connect(self.actualizar_fin_desde_duracion)
        self.duracion_picker.minute_spin.valueChanged.connect(self.actualizar_fin_desde_duracion)
        self.duracion_picker.second_spin.valueChanged.connect(self.actualizar_fin_desde_duracion)

        # Inicializar fecha/hora de inicio y fin
        ahora = QDateTime.currentDateTime()
        inicio_dt = ahora.addSecs(3600)  # +1 hora
        fin_dt = ahora.addSecs(7200)     # +2 horas

        self.date_start_picker.setDate(inicio_dt.date())
        self.start_picker.set_time(inicio_dt.time())

        self.date_end_picker.setDate(fin_dt.date())
        self.end_picker.set_time(fin_dt.time())

        # Inicializar duración: 0 días, 1 hora, 0 minutos, 0 segundos
        self.duracion_picker.days_spin.setValue(0)
        self.duracion_picker.hour_spin.setValue(1)
        self.duracion_picker.minute_spin.setValue(0)
        self.duracion_picker.second_spin.setValue(0)

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
        
        guardar_registro(datos["fecha_inicio"], datos["inicio"],datos["fecha_fin"], datos["fin"], datos["duracion"])
        QMessageBox.information(self, "Éxito", "Registro guardado correctamente.")
        self.cargar_registros()


    def get_programacion(self):
        return {
            "fecha_inicio": self.date_start_picker.date().toString("yyyy-MM-dd"),
            "inicio": self.start_picker.get_time().toString("HH:mm:ss"),
            "fecha_fin": self.date_end_picker.date().toString("yyyy-MM-dd"),
            "fin": self.end_picker.get_time().toString("HH:mm:ss"),
            "duracion": f"{self.duracion_picker.days_spin.value()}d {self.duracion_picker.hour_spin.value():02d}:{self.duracion_picker.minute_spin.value():02d}:{self.duracion_picker.second_spin.value():02d}"
        }
    
    def cargar_registros(self):
        registros = leer_proximas_grabaciones()
        self.table.setRowCount(len(registros))
        for row, (id_registro, fechaIni, inicio, fechaFin, fin, duracion) in enumerate(registros):
            self.table.setItem(row, 0, QTableWidgetItem(fechaIni))
            self.table.setItem(row, 1, QTableWidgetItem(inicio))
            self.table.setItem(row, 2, QTableWidgetItem(fechaFin))
            self.table.setItem(row, 3, QTableWidgetItem(fin))
            self.table.setItem(row, 4, QTableWidgetItem(duracion))
            # Botón de borrar
            btn_borrar = QPushButton()
            btn_borrar.setIcon(QIcon("img/borrar.png"))
            btn_borrar.clicked.connect(
                lambda checked, r=(id_registro, fechaIni, inicio, fechaFin, fin, duracion): self.confirmar_borrado(r)
            )
            self.table.setCellWidget(row, 5, btn_borrar)

    def confirmar_borrado(self, registro):
        id_registro, fechaIni, inicio, fechaFin, fin, duracion = registro
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Confirmar eliminación")
        msg.setText(
            f"¿Desea eliminar este registro?\n\n"
            f"Fecha inicio: {fechaIni}\n"
            f"Hora inicio: {inicio}\n"
            f"Fecha fin: {fechaFin}\n"
            f"Hora fin: {fin}\n"
            f"Duracion: {duracion}"
        )
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        ret = msg.exec_()
        if ret == QMessageBox.Ok:
            borrar_registro(id_registro)
            QMessageBox.information(self, "Eliminado", "Registro eliminado correctamente.")
            self.cargar_registros()

    def actualizar_duracion_desde_fechas(self):
        # Obtener QDateTime de inicio y fin
        inicio_dt = QDateTime(
            self.date_start_picker.date(),
            self.start_picker.get_time()
        )
        fin_dt = QDateTime(
            self.date_end_picker.date(),
            self.end_picker.get_time()
        )
        # Calcular diferencia en segundos
        secs = inicio_dt.secsTo(fin_dt)
        if secs < 0:
            secs = 0
        duracion = timedelta(seconds=secs)
        dias = duracion.days
        horas = duracion.seconds // 3600
        minutos = (duracion.seconds % 3600) // 60
        segundos = duracion.seconds % 60
        # Actualizar spinboxes de duración
        self.duracion_picker.days_spin.blockSignals(True)
        self.duracion_picker.hour_spin.blockSignals(True)
        self.duracion_picker.minute_spin.blockSignals(True)
        self.duracion_picker.second_spin.blockSignals(True)
        self.duracion_picker.days_spin.setValue(dias)
        self.duracion_picker.hour_spin.setValue(horas)
        self.duracion_picker.minute_spin.setValue(minutos)
        self.duracion_picker.second_spin.setValue(segundos)
        self.duracion_picker.days_spin.blockSignals(False)
        self.duracion_picker.hour_spin.blockSignals(False)
        self.duracion_picker.minute_spin.blockSignals(False)
        self.duracion_picker.second_spin.blockSignals(False)

    def actualizar_fin_desde_duracion(self):
        # Obtener QDateTime de inicio
        inicio_dt = QDateTime(
            self.date_start_picker.date(),
            self.start_picker.get_time()
        )
        # Obtener duración
        dias = self.duracion_picker.days_spin.value()
        horas = self.duracion_picker.hour_spin.value()
        minutos = self.duracion_picker.minute_spin.value()
        segundos = self.duracion_picker.second_spin.value()
        duracion = timedelta(days=dias, hours=horas, minutes=minutos, seconds=segundos)
        # Calcular QDateTime de fin
        fin_dt = inicio_dt.addSecs(int(duracion.total_seconds()))
        # Actualizar campos de fin
        self.date_end_picker.blockSignals(True)
        self.end_picker.hour_spin.blockSignals(True)
        self.end_picker.minute_spin.blockSignals(True)
        self.end_picker.second_spin.blockSignals(True)
        self.date_end_picker.setDate(fin_dt.date())
        self.end_picker.set_time(fin_dt.time())
        self.date_end_picker.blockSignals(False)
        self.end_picker.hour_spin.blockSignals(False)
        self.end_picker.minute_spin.blockSignals(False)
        self.end_picker.second_spin.blockSignals(False)

class CustomTimePicker(QWidget):
    """TimePicker personalizado con SpinBoxes"""
    timeChanged = pyqtSignal(QTime)
    
    def __init__(self, esDuracion=False):
        super().__init__()
        self.esDuracion = esDuracion
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Layout vertical para los controles de tiempo
        time_layout = QHBoxLayout()
        
        # SpinBox para horas
        self.days_spin = QSpinBox()
        self.days_spin.setRange(0, 23)
        self.days_spin.setValue(QTime.currentTime().hour())
        #self.days_spin.valueChanged.connect(self.on_time_changed)

        # SpinBox para horas
        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 23)
        self.hour_spin.setValue(QTime.currentTime().hour())
        #self.hour_spin.valueChanged.connect(self.on_time_changed)
        
        # SpinBox para minutos
        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 59)
        self.minute_spin.setValue(QTime.currentTime().minute())
        #self.minute_spin.valueChanged.connect(self.on_time_changed)
        
        # SpinBox para segundos
        self.second_spin = QSpinBox()
        self.second_spin.setRange(0, 59)
        self.second_spin.setValue(QTime.currentTime().second())
        #self.second_spin.valueChanged.connect(self.on_time_changed)
        
        if self.esDuracion:
            time_layout.addWidget(QLabel("Dias:"))
            time_layout.addWidget(self.days_spin)
            time_layout.addWidget(QLabel("Horas:"))
            time_layout.addWidget(self.hour_spin)
            time_layout.addWidget(QLabel("Minutos:"))
            time_layout.addWidget(self.minute_spin)
            time_layout.addWidget(QLabel("Segundos:"))
            time_layout.addWidget(self.second_spin)
        else:
            time_layout.addWidget(QLabel("Hora:"))
            time_layout.addWidget(self.hour_spin)
            time_layout.addWidget(QLabel("Minuto:"))
            time_layout.addWidget(self.minute_spin)
            time_layout.addWidget(QLabel("Segundo:"))
            time_layout.addWidget(self.second_spin)
        
        layout.addLayout(time_layout)
        
        # Botones de control
        button_layout = QHBoxLayout()
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def on_time_changed(self):
        time = QTime(self.hour_spin.value(), self.minute_spin.value(), self.second_spin.value())
        self.time_label.setText(f"Tiempo seleccionado: {time.toString('HH:mm:ss')}")
        self.timeChanged.emit(time)
    
    def get_time(self):
        if self.esDuracion:
            return timedelta(
                days=self.days_spin.value(),
                hours=self.hour_spin.value(),
                minutes=self.minute_spin.value(),
                seconds=self.second_spin.value()
            )
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