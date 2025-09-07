from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import ( QMainWindow, QVBoxLayout,  
                            QWidget,  QLabel, QPushButton, QApplication,  QMessageBox,
                            QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog )
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from utils import norm
from db import leer_todas_grabaciones, actualizar_estado, borrar_registro
from datetime import timedelta
import os


class GrabacionesWin(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.setWindowTitle("Mediciones automática")
        self.setWindowIcon(QIcon('img/LogoCINTRA1.png'))
        screen = QApplication.primaryScreen().size()
        anchoX = screen.width()
        altoY = screen.height()
        self.setGeometry(norm(anchoX, altoY, 0.15, 0.15, 0.7, 0.4))

        self.vController = controller
        
        with open("estilos.qss", "r", encoding='utf-8') as f:
            QApplication.instance().setStyleSheet(f.read())
            
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        # Tabla de registros
        self.lbl_table_title = QLabel("Grabaciones programadas:")
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Fecha inicio", "Hora inicio", "Fecha fin", "Hora fin","Duración","Extención","Ubicación", "Estado", "Eliminar", "Abrir"
        ])
        self.table.setMinimumHeight(250)  # <-- Ajusta el valor según lo que necesites
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.table)
        
        self.setCentralWidget(central_widget)
        
        self.cargar_registros()
        
    def cargar_registros(self):
        registros = leer_todas_grabaciones()
        self.table.setRowCount(len(registros))
        for row, (id_registro, fechaIni, inicio, fechaFin, fin, duracion, ext, estado, ruta) in enumerate(registros):
            valores = [fechaIni, inicio, fechaFin, fin, duracion, ext, ruta, estado]
            for col, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # 🔒 Hacer la celda no editable
                self.table.setItem(row, col, item)

            # Botón de borrar
            btn_borrar = QPushButton()
            btn_borrar.setIcon(QIcon("img/borrar.png"))
            btn_borrar.clicked.connect(
                lambda checked, r=(id_registro, fechaIni, inicio, fechaFin, fin, duracion): self.confirmar_borrado(r)
            )
            self.table.setCellWidget(row, 8, btn_borrar)

            # Botón de abrir ubicación
            btn_ubi = QPushButton()
            btn_ubi.setIcon(QIcon("img/carpeta-abierta.png"))
            btn_ubi.clicked.connect(lambda _, ruta=ruta: self.abrir_explorador_en_ruta(ruta))
            self.table.setCellWidget(row, 9, btn_ubi)
    
    
    def abrir_explorador_en_ruta(self, ruta):
        
        if os.path.exists(ruta):
            carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta", ruta)
            if carpeta:
                print("Carpeta seleccionada:", carpeta)
        else:
            print("La ruta no existe:", ruta)
            
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
            f"Duración: {duracion}"
        )
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        ret = msg.exec_()
        if ret == QMessageBox.Ok:
            borrar_registro(id_registro)
            QMessageBox.information(self, "Eliminado", "Registro eliminado correctamente.")
            self.cargar_registros()    
    
    def closeEvent(self, event):
        self.vController.ventanas_abiertas["grabaciones"] = None
        event.accept()