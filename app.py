# Parche de compatibilidad para Python 3.13.5
import collections
if not hasattr(collections, 'MutableMapping'):
    import collections.abc
    collections.MutableMapping = collections.abc.MutableMapping

from flask import Flask, Response
from flask_socketio import SocketIO
from dronekit import connect
import threading
import time
import random
import cv2
from database import inicializar_db, guardar_telemetria, guardar_muestra_agua

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Inicializar base de datos
inicializar_db()

# Conexión al dron (Puerto 5763)
print("🔌 Conectando con UAV en puerto 5763...")
vehicle = connect('tcp:127.0.0.1:5763', wait_ready=True)

def flujo_backend():
    while True:
        if vehicle:
            # Telemetría base
            lat = vehicle.location.global_frame.lat
            lon = vehicle.location.global_frame.lon
            alt = vehicle.location.global_relative_frame.alt
            modo = vehicle.mode.name
            
            # Guardar trayectoria siempre
            datos_vuelo = {"lat": lat, "lon": lon, "alt": alt, "modo": modo}
            guardar_telemetria(datos_vuelo)

            # Lógica de muestreo a 1 metro
            if alt <= 1.1:
                print(f"🧪 [MUESTREANDO] Altura: {alt:.2f}m. Obteniendo parametros...")
                datos_sensores = {
                    "ph": round(random.uniform(7.0, 7.8), 2),
                    "turbidez": round(random.uniform(1.2, 3.5), 2),
                    "oxigenoD": round(random.uniform(6.0, 9.0), 2),
                    "conductividad": round(random.uniform(300, 450), 1),
                    "lat": lat,
                    "lon": lon
                }
                # Guardar en la tabla de muestras
                guardar_muestra_agua(datos_sensores)
                # Emitir a la interfaz
                socketio.emit('update_data', {**datos_vuelo, **datos_sensores, "muestreando": True})
            else:
                # Si está arriba, enviamos valores en cero
                socketio.emit('update_data', {**datos_vuelo, "ph": 0, "oxigenoD": 0, "muestreando": False})

        time.sleep(1)

# Streaming de video
def generar_frames():
    cam = cv2.VideoCapture(0)
    while True:
        success, frame = cam.read()
        if not success: break
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generar_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    threading.Thread(target=flujo_backend, daemon=True).start()
    socketio.run(app, port=5000, debug=True, use_reloader=False)