import sqlite3
from datetime import datetime

def inicializar_db():
    conexion = sqlite3.connect('telemetria.db')
    cursor = conexion.cursor()

    # TABLA PARA EL HISTORIAL DE VUELO (TRAYECTORIA)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telemetria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            lat REAL,
            lon REAL,
            alt REAL,
            modo TEXT
        )
    ''')
    
    # TABLA PARA LAS MUESTRAS DE AGUA (SENSORES)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS muestras_agua (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            ph REAL,
            turbidez REAL,
            oxigenoD REAL,
            conductividad REAL,
            lat REAL,
            lon REAL
        )
    ''')
    
    conexion.commit()
    conexion.close()

def guardar_telemetria(data):
    conexion = sqlite3.connect('telemetria.db')
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO telemetria (timestamp, lat, lon, alt, modo)
        VALUES (?, ?, ?, ?, ?)
    ''', (datetime.now().strftime("%H:%M:%S"), data['lat'], data['lon'], data['alt'], data['modo']))
    conexion.commit()
    conexion.close()

def guardar_muestra_agua(data):
    conexion = sqlite3.connect('telemetria.db')
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO muestras_agua (timestamp, ph, turbidez, oxigenoD, conductividad, lat, lon)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().strftime("%H:%M:%S"), 
        data['ph'], 
        data['turbidez'], 
        data['oxigenoD'], 
        data['conductividad'], 
        data['lat'], 
        data['lon']
    ))
    conexion.commit()
    conexion.close()