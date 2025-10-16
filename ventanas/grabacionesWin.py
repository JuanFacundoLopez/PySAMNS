import sys
import os
from PyQt5.QtCore import QTime, Qt
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QLabel, 
                            QPushButton, QApplication, QMessageBox, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QFileDialog)
from PyQt5.QtGui import QIcon
from utils import norm
from db import leer_todas_grabaciones, actualizar_estado, borrar_registro
from datetime import timedelta


class GrabacionesWin(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.setWindowTitle("Mediciones automática")
        
        # Set window icon with path that works in both dev and frozen environments
        if getattr(sys, 'frozen', False):
            # If running as compiled executable
            self.icon_path = os.path.join(sys._MEIPASS, 'img', 'LogoCINTRA1.png')
            self.borrar_icon = os.path.join(sys._MEIPASS, 'img', 'borrar.png')
            self.folder_icon = os.path.join(sys._MEIPASS, 'img', 'carpeta-abierta.png')
        else:
            # If running in development
            self.icon_path = os.path.join('img', 'LogoCINTRA1.png')
            self.borrar_icon = os.path.join('img', 'borrar.png')
            self.folder_icon = os.path.join('img', 'carpeta-abierta.png')
            
        self.setWindowIcon(QIcon(self.icon_path))
        screen = QApplication.primaryScreen().size()
        anchoX = screen.width()
        altoY = screen.height()
        self.setGeometry(norm(anchoX, altoY, 0.15, 0.15, 0.7, 0.4))

        self.vController = controller
        
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
            btn_borrar.setIcon(QIcon(self.borrar_icon))
            btn_borrar.clicked.connect(
                lambda checked, r=(id_registro, fechaIni, inicio, fechaFin, fin, duracion): self.confirmar_borrado(r)
            )
            self.table.setCellWidget(row, 8, btn_borrar)

            # Botón de abrir ubicación
            btn_ubi = QPushButton()
            btn_ubi.setIcon(QIcon(self.folder_icon))
            btn_ubi.clicked.connect(lambda _, ruta=ruta: self.abrir_explorador_en_ruta(ruta))
            self.table.setCellWidget(row, 9, btn_ubi)
    
    
    def abrir_explorador_en_ruta(self, ruta):
        
        if os.path.exists(ruta):
            os.startfile(ruta)  # Abre el explorador en la ruta
        else:
            QMessageBox.warning(self, "Error", f"La ruta no existe: {ruta}")
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