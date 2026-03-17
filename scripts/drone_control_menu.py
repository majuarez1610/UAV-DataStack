# ---------------- PARCHE DE COMPATIBILIDAD ----------------
import collections
if not hasattr(collections, 'MutableMapping'):
    import collections.abc
    collections.MutableMapping = collections.abc.MutableMapping
# ----------------------------------------------------------

from dronekit import connect, VehicleMode
import time
import threading
import os

# ---------------- CONEXIÓN ----------------
print("🔌 Conectando al simulador (Mission Planner SITL)...")
vehicle = connect('tcp:127.0.0.1:5762', wait_ready=True, timeout=60)

# ---------------- FUNCIÓN PARA LIMPIAR PANTALLA ----------------
def limpiar_pantalla():
    # 'cls' para Windows, 'clear' para Linux/Mac
    os.system('cls' if os.name == 'nt' else 'clear')

# ---------------- TELEMETRÍA (ACTUALIZADA) ----------------
def mostrar_interfaz():
    while True:
        try:
            limpiar_pantalla()
            
            # Datos del dron
            lat = vehicle.location.global_frame.lat
            lon = vehicle.location.global_frame.lon
            alt = vehicle.location.global_relative_frame.alt
            batt = vehicle.battery.level
            mode = vehicle.mode.name
            armed = vehicle.armed

            print("=" * 45)
            print(f"📡 ESTATUS DEL DRON EN TIEMPO REAL")
            print("=" * 45)
            print(f" 📍 Posición:  {lat:.6f}, {lon:.6f}")
            print(f" 📏 Altitud:   {alt:.1f} m")
            print(f" 🔋 Batería:   {batt if batt is not None else 'N/A'} %")
            print(f" 🕹️  Modo:      {mode}")
            print(f" 🛡️  Armado:    {'✅ SÍ' if armed else '❌ NO'}")
            print("=" * 45)
            
            # Mostrar el menú fijo abajo
            print("\n🎮 MENÚ DE CONTROL INTERACTIVO")
            print(" [1] STABILIZE   [2] LOITER   [3] AUTO (+Throttle)")
            print(" [4] LAND        [5] ARMAR    [6] DESARMAR")
            print(" [0] SALIR")
            print("-" * 45)
            print("Escribe una opción y presiona Enter: ", end="", flush=True)

        except Exception as e:
            print(f"⚠️ Error: {e}")
        
        time.sleep(2) # Se actualiza cada 2 segundos

# ---------------- LÓGICA DE CONTROL ----------------
def cambiar_modo(nuevo_modo):
    vehicle.mode = VehicleMode(nuevo_modo)

def auto_con_throttle():
    cambiar_modo("AUTO")
    vehicle.channels.overrides['3'] = 1650  
    time.sleep(5)
    vehicle.channels.overrides['3'] = None

def armar_dron():
    if vehicle.is_armable:
        vehicle.armed = True

def desarmar_dron():
    vehicle.armed = False

# ---------------- MAIN ----------------
if __name__ == "__main__":
    # Iniciamos la interfaz en un hilo
    hilo_interfaz = threading.Thread(target=mostrar_interfaz)
    hilo_interfaz.daemon = True
    hilo_interfaz.start()

    while True:
        # El input ahora solo espera la opción sin imprimir texto extra
        opcion = input()

        if opcion == "1":
            cambiar_modo("STABILIZE")
        elif opcion == "2":
            cambiar_modo("LOITER")
        elif opcion == "3":
            auto_con_throttle()
        elif opcion == "4":
            cambiar_modo("LAND")
        elif opcion == "5":
            armar_dron()
        elif opcion == "6":
            desarmar_dron()
        elif opcion == "0":
            print("\n🔴 Cerrando conexión...")
            vehicle.close()
            break