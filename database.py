import sqlite3
from datetime import datetime

def inicializar_db():
    conexion = sqlite3.connect('telemetria.db')
    cursor = conexion.cursor()

    # 1. TABLA DE MISIONES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS misiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            fecha_inicio TEXT,
            fecha_fin TEXT
        )
    ''')

    # 2. TABLA DE TELEMETRÍA (Guardado continuo)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telemetria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mision_id INTEGER,
            timestamp TEXT,
            lat REAL, lon REAL, alt REAL, modo TEXT,
            FOREIGN KEY(mision_id) REFERENCES misiones(id)
        )
    ''')
    
    # 3. TABLA DE MUESTRAS (Solo en el punto de interés)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS muestras_agua (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mision_id INTEGER,
            timestamp TEXT,
            ph REAL, turbidez REAL, oxigenoD REAL, conductividad REAL,
            lat REAL, lon REAL,
            FOREIGN KEY(mision_id) REFERENCES misiones(id)
        )
    ''')
    
    conexion.commit()
    conexion.close()

def crear_mision(nombre):
    conexion = sqlite3.connect('telemetria.db')
    cursor = conexion.cursor()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('INSERT INTO misiones (nombre, fecha_inicio) VALUES (?, ?)', (nombre, fecha))
    mision_id = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return mision_id

def finalizar_mision(mision_id):
    conexion = sqlite3.connect('telemetria.db')
    cursor = conexion.cursor()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('UPDATE misiones SET fecha_fin = ? WHERE id = ?', (fecha, mision_id))
    conexion.commit()
    conexion.close()

def guardar_telemetria(mision_id, data):
    conexion = sqlite3.connect('telemetria.db')
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO telemetria (mision_id, timestamp, lat, lon, alt, modo)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (mision_id, datetime.now().strftime("%H:%M:%S"), data['lat'], data['lon'], data['alt'], data['modo']))
    conexion.commit()
    conexion.close()

def guardar_muestra_agua(mision_id, data):
    conexion = sqlite3.connect('telemetria.db')
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO muestras_agua (mision_id, timestamp, ph, turbidez, oxigenoD, conductividad, lat, lon)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (mision_id, datetime.now().strftime("%H:%M:%S"), data['ph'], data['turbidez'], data['oxigenoD'], data['conductividad'], data['lat'], data['lon']))
    conexion.commit()
    conexion.close()