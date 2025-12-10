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
            duracion TEXT NOT NULL,
            extencion TEXT NOT NULL DEFAULT '.wav',
            estado TEXT NOT NULL DEFAULT 'Pendiente',
            ruta TEXT NOT NULL,
            cal_tipo TEXT,
            cal_offset REAL,
            cal_factor REAL,
            cal_ruta TEXT,
            disp_entrada_nombre TEXT,
            disp_entrada_indice INTEGER,
            disp_salida_nombre TEXT,
            disp_salida_indice INTEGER
        )
    """)
    conn.commit()
    conn.close()

def guardar_registro(fechaIni, inicio, fechaFin, fin, duracion, extencion, ruta):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Verificar si hay superposición con grabaciones existentes
    cursor.execute("""
        SELECT COUNT(*) FROM registros 
        WHERE (fecha_inicio = ? AND hora_inicio < ? AND fecha_fin = ? AND hora_fin > ?)
           OR (fecha_inicio < ? AND fecha_fin > ?)
    """, (fechaIni, inicio, fechaFin, fin, fechaFin, inicio))
    
    if cursor.fetchone()[0] > 0:
        conn.close()
        raise ValueError("El periodo de grabación se superpone con otra grabación existente.")
    
    cursor.execute(
        "INSERT INTO registros (fecha_inicio, hora_inicio, fecha_fin, hora_fin, duracion, extencion, estado, ruta) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (fechaIni, inicio, fechaFin, fin, duracion, extencion, 'Pendiente', ruta)
    )
    conn.commit()
    conn.close()

def leer_registros_basicos():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT fecha_inicio, hora_inicio,fecha_fin, hora_fin, duracion FROM registros")
    registros = cursor.fetchall()
    conn.close()
    return registros

def leer_registros_completos():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT fecha_inicio, hora_inicio,fecha_fin, hora_fin, duracion, extencion, estado,ruta FROM registros")
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

def leer_todas_grabaciones():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, fecha_inicio, hora_inicio, fecha_fin, hora_fin, duracion, extencion, estado, ruta
        FROM registros 
        ORDER BY fecha_inicio, hora_inicio
    """)
    todas_grabaciones = cursor.fetchall()
    conn.close()
    return todas_grabaciones

def actualizar_estado(id_registro, nuevo_estado):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE registros SET estado = ? WHERE id = ?", (nuevo_estado, id_registro))
    conn.commit()
    conn.close()

def borrar_registro(id_registro):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM registros WHERE id = ?", (id_registro,))
    conn.commit()
    conn.close()
    
def actualizar_info_cal(id_registro,
                             cal_tipo=None,
                             cal_offset=None,
                             cal_factor=None,
                             cal_ruta=None,
                             disp_entrada_nombre=None,
                             disp_entrada_indice=None,
                             disp_salida_nombre=None,
                             disp_salida_indice=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Construir dinámicamente SET según parámetros no None
    updates = []
    params = []
    mapping = {
        'cal_tipo': cal_tipo,
        'cal_offset': cal_offset,
        'cal_factor': cal_factor,
        'cal_ruta': cal_ruta,
        'disp_entrada_nombre': disp_entrada_nombre,
        'disp_entrada_indice': disp_entrada_indice,
        'disp_salida_nombre': disp_salida_nombre,
        'disp_salida_indice': disp_salida_indice
    }
    for col, val in mapping.items():
        if val is not None:
            updates.append(f"{col} = ?")
            params.append(val)
    if not updates:
        conn.close()
        return
    params.append(id_registro)
    sql = f"UPDATE registros SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(sql, tuple(params))
    conn.commit()
    conn.close()