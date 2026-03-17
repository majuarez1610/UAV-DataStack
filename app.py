import collections
if not hasattr(collections, 'MutableMapping'):
    import collections.abc
    collections.MutableMapping = collections.abc.MutableMapping

from flask import Flask, Response
from flask_socketio import SocketIO
from dronekit import connect
import threading, time, random, cv2, sys
import database as db

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
db.inicializar_db()

print("🔌 Conectando con UAV en puerto 5763...")
# wait_ready=False para evitar el error de timeout inicial
vehicle = connect('tcp:127.0.0.1:5763', wait_ready=False)

def flujo_mision_uav():
    mision_id = None
    objetivo_alcanzado = False

    try:
        while True:
            if vehicle:
                alt = vehicle.location.global_relative_frame.alt
                
                # Aduana de seguridad para NoneType
                if alt is None:
                    print("⏳ Esperando telemetría...", end='\r')
                    time.sleep(1)
                    continue

                lat = vehicle.location.global_frame.lat
                lon = vehicle.location.global_frame.lon
                modo = vehicle.mode.name
                armado = vehicle.armed
                datos_vuelo = {"lat": lat, "lon": lon, "alt": alt, "modo": modo}

                # --- LÓGICA DE MISIONES ---
                if armado and mision_id is None:
                    mision_id = db.crear_mision(f"Mision_{random.randint(100,999)}")
                    print(f"\n📝 [Misión] {mision_id} Iniciada....")

                if mision_id:
                    # Guardado constante en DB (Telemetría de toda la misión)
                    db.guardar_telemetria(mision_id, datos_vuelo)

                    # --- MENSAJES DE CONSOLA E INTERACCIÓN ---
                    if alt > 1.5:
                        if objetivo_alcanzado:
                            print(f"\n✅ [INFO] Muestreo finalizado. Continuando ruta...")
                            objetivo_alcanzado = False
                        print(f"🛰️ [NAVEGACIÓN] Dirigiéndome al punto de interés... Alt: {alt:.2f}m", end='\r')

                    elif 0.5 < alt <= 1.2:
                        if not objetivo_alcanzado:
                            print(f"\n📍 [OBJETIVO] Punto alcanzado ({alt:.2f}m). Recolectando datos químicos...")
                            objetivo_alcanzado = True
                        
                        # Guardar muestra de agua
                        datos_agua = {
                            "ph": round(random.uniform(7.1, 7.8), 2),
                            "turbidez": round(random.uniform(1.0, 3.0), 2),
                            "oxigenoD": round(random.uniform(7.0, 9.0), 2),
                            "conductividad": round(random.uniform(300, 450), 1),
                            "lat": lat, "lon": lon
                        }
                        db.guardar_muestra_agua(mision_id, datos_agua)
                        socketio.emit('update_data', {**datos_vuelo, **datos_agua, "mision": mision_id})
                    
                    elif alt < 0.3:
                        print(f"🛬 [DESCENSO] Aproximación a tierra... Alt: {alt:.2f}m     ", end='\r')

                # --- CIERRE DE MISIÓN ---
                if not armado and mision_id is not None:
                    db.finalizar_mision(mision_id)
                    print(f"\n🏁 [FINALIZADO] Misión {mision_id} cerrada. Tiempos guardados.")
                    mision_id = None
                    objetivo_alcanzado = False

                # Streaming al frontend
                socketio.emit('update_data', {**datos_vuelo, "mision": mision_id})

            time.sleep(1)

    except Exception as e:
        print(f"\n❌ Error: {e}")

# --- VIDEO FEED ---
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
    t = threading.Thread(target=flujo_mision_uav, daemon=True)
    t.start()
    try:
        socketio.run(app, port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\nServidor apagado.")