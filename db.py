import sqlite3
from datetime import datetime

DB_FILE = "registros.db"

def crear_tabla():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_inicio TEXT NOT NULL,
            hora_inicio TEXT NOT NULL,
            fecha_fin TEXT NOT NULL,
            hora_fin TEXT NOT NULL,
            duracion TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def guardar_registro(fechaIni, inicio,fechaFin, fin, duracion):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO registros (fecha_inicio, hora_inicio,fecha_fin, hora_fin, duracion) VALUES (?, ?, ?,?, ?)",
        (fechaIni, inicio,fechaFin, fin, duracion)
    )
    conn.commit()
    conn.close()

def leer_registros():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT fecha_inicio, hora_inicio,fecha_fin, hora_fin, duracion FROM registros")
    registros = cursor.fetchall()
    conn.close()
    return registros

def leer_proximas_grabaciones():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    ahora = datetime.now()
    fecha_actual = ahora.strftime("%Y-%m-%d")
    hora_actual = ahora.strftime("%H:%M:%S")
    cursor.execute("""
        SELECT id, fecha_inicio, hora_inicio, fecha_fin, hora_fin, duracion
        FROM registros 
        WHERE (fecha_inicio > ?)
           OR (fecha_inicio = ? AND hora_inicio > ?)
    """, (fecha_actual, fecha_actual, hora_actual))
    proximas_grabaciones = cursor.fetchall()
    conn.close()
    return proximas_grabaciones

def borrar_registro(id_registro):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM registros WHERE id = ?", (id_registro,))
    conn.commit()
    conn.close()