import sqlite3

DB_FILE = "registros.db"

def crear_tabla():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fin TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def guardar_registro(fecha, inicio, fin):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO registros (fecha, hora_inicio, hora_fin) VALUES (?, ?, ?)",
        (fecha, inicio, fin)
    )
    conn.commit()
    conn.close()

def leer_registros():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT fecha, hora_inicio, hora_fin FROM registros")
    registros = cursor.fetchall()
    conn.close()
    return registros