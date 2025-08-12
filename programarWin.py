from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import ( QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QSpinBox, QLabel, QPushButton, QApplication)
from PyQt5.QtCore import QTime, pyqtSignal
from utils import norm




class ProgramarWin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Programar grabación automática")
        screen = QApplication.primaryScreen().size()
        anchoX = screen.width()
        altoY = screen.height()
        self.setGeometry(norm(anchoX, altoY, 0.4, 0.4, 0.2, 0.2))

        with open("estilos.qss", "r", encoding='utf-8') as f:
            QApplication.instance().setStyleSheet(f.read())
            
        # Widget central
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Texto informativo
        lbl_info = QLabel(
            "Se programará la grabación automática de audio\n"
            "para la siguiente hora y día"
        )
        lbl_info.setStyleSheet("font-size: 14pt; font-weight: bold;")
        lbl_info.setWordWrap(True)
        layout.addWidget(lbl_info)

        self.custom_picker = CustomTimePicker()
        layout.addWidget(self.custom_picker)
        

        self.setCentralWidget(central_widget)


class CustomTimePicker(QWidget):
    """TimePicker personalizado con SpinBoxes"""
    timeChanged = pyqtSignal(QTime)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        
        # Layout horizontal para los controles de tiempo
        time_layout = QHBoxLayout()
        
        # SpinBox para horas
        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 23)
        self.hour_spin.setValue(QTime.currentTime().hour())
        self.hour_spin.setSuffix(" h")
        self.hour_spin.valueChanged.connect(self.on_time_changed)
        
        # SpinBox para minutos
        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 59)
        self.minute_spin.setValue(QTime.currentTime().minute())
        self.minute_spin.setSuffix(" min")
        self.minute_spin.valueChanged.connect(self.on_time_changed)
        
        # SpinBox para segundos
        self.second_spin = QSpinBox()
        self.second_spin.setRange(0, 59)
        self.second_spin.setValue(QTime.currentTime().second())
        self.second_spin.setSuffix(" seg")
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