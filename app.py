import collections
if not hasattr(collections, 'MutableMapping'):
    import collections.abc
    collections.MutableMapping = collections.abc.MutableMapping

from flask import Flask, Response, render_template
from flask_socketio import SocketIO
from dronekit import connect
import threading, time, random, cv2

app = Flask(__name__)

# ✅ CONFIGURACIÓN SOCKET CORRECTA
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading",
    logger=True,
    engineio_logger=True
)

# =============================
# VARIABLE GLOBAL
# =============================
vehicle = None

# =============================
# CONEXIÓN AL DRON 
# =============================
def conectar_dron():
    global vehicle
    try:
        print("🔌 Intentando conectar con UAV...")
        vehicle = connect('tcp:127.0.0.1:5763', wait_ready=False)
        print("✅ UAV conectado")
    except Exception as e:
        print(f"❌ Error conectando UAV: {e}")

# =============================
# CONEXIÓN FRONTEND
# =============================
@socketio.on('connect')
def handle_connect():
    print("🟢 Cliente conectado desde el frontend")

# =============================
# FLUJO PRINCIPAL
# =============================
def flujo_mision_uav():
    lat = 19.8221
    lon = -99.2473

    while True:
        try:
            if vehicle and vehicle.location.global_frame.lat is not None:
                lat = vehicle.location.global_frame.lat
                lon = vehicle.location.global_frame.lon
                alt = vehicle.location.global_relative_frame.alt or 0
                modo = vehicle.mode.name
            else:
                # SIMULACIÓN
                lat += random.uniform(-0.0001, 0.0001)
                lon += random.uniform(-0.0001, 0.0001)
                alt = random.uniform(1, 10)
                modo = "SIMULADO"

            datos = {
                "lat": lat,
                "lon": lon,
                "alt": alt,
                "modo": modo,
                "voltaje": round(random.uniform(11.0, 12.6), 2),
                "corriente": round(random.uniform(0.5, 5.0), 2),
                "mision": "ACTIVA"
            }

            socketio.emit('update_data', datos)
            print("📡 Enviando:", datos)

            time.sleep(0.5)

        except Exception as e:
            print("❌ Error:", e)

# =============================
# RUTA PRINCIPAL
# =============================
@app.route("/")
def index():
    return render_template("index.html")

# =============================
# VIDEO
# =============================
def generar_frames():
    cam = cv2.VideoCapture(0)
    while True:
        success, frame = cam.read()
        if not success:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generar_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# =============================
# MAIN
# =============================
if __name__ == '__main__':
    threading.Thread(target=conectar_dron, daemon=True).start()
    threading.Thread(target=flujo_mision_uav, daemon=True).start()

    print("🚀 Servidor iniciando...")
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)