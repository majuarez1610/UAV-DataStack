# ---------------- PARCHE DE COMPATIBILIDAD ----------------
# Esto es necesario para que DroneKit funcione en Python 3.10 o superior
import collections
if not hasattr(collections, 'MutableMapping'):
    import collections.abc
    collections.MutableMapping = collections.abc.MutableMapping
# ----------------------------------------------------------

from dronekit import connect, VehicleMode
import time
import threading

# ---------------- CONEXIÓN ----------------
print("🔌 Conectando al simulador (Mission Planner SITL)...")
# Asegúrate de que el SITL en Mission Planner esté usando el puerto 5763
vehicle = connect('tcp:127.0.0.1:5763', wait_ready=True, timeout=60)
print("✅ Conectado correctamente\n")


# ---------------- TELEMETRÍA ----------------
def mostrar_telemetria():
    while True:
        try:
            lat = vehicle.location.global_frame.lat
            lon = vehicle.location.global_frame.lon
            alt = vehicle.location.global_relative_frame.alt
            batt = vehicle.battery.level
            mode = vehicle.mode.name
            armed = vehicle.armed

            print("\n📡 TELEMETRÍA DRON")
            print(f" Latitud:   {lat:.6f}")
            print(f" Longitud:  {lon:.6f}")
            print(f" Altitud:   {alt:.1f} m")
            print(f" Batería:   {batt if batt is not None else 'N/A'} %")
            print(f" Modo:      {mode}")
            print(f" Armado:    {'✅ Sí' if armed else '❌ No'}")
            print("-" * 45)
        except Exception as e:
            print(f"⚠️ Error leyendo telemetría: {e}")
        
        time.sleep(2)


# ---------------- CAMBIO DE MODO ----------------
def cambiar_modo(nuevo_modo):
    print(f"🔄 Cambiando a modo {nuevo_modo}...")
    vehicle.mode = VehicleMode(nuevo_modo)

    while vehicle.mode.name != nuevo_modo:
        print("⏳ Esperando cambio de modo...")
        time.sleep(1)

    print(f"✅ Modo cambiado a {nuevo_modo}")


# ---------------- AUTO + THROTTLE OVERRIDE ----------------
def auto_con_throttle():
    cambiar_modo("AUTO")

    print("🚀 Aplicando throttle override...")
    # 1600–1700 suele ser suficiente en quad
    vehicle.channels.overrides['3'] = 1650  
    
    time.sleep(5)  # mantener 5 segundos
    
    print("🔓 Liberando override de throttle...")
    vehicle.channels.overrides['3'] = None


# ---------------- ARMAR / DESARMAR ----------------
def armar_dron():
    if not vehicle.is_armable:
        print("⚠️ El dron no está listo para armar (Verifica Pre-Arm checks en MP).")
        return

    print("🟢 Armando dron...")
    vehicle.armed = True

    while not vehicle.armed:
        print("⏳ Esperando armado...")
        time.sleep(1)

    print("✅ Dron armado correctamente")


def desarmar_dron():
    print("🔴 Desarmando dron...")
    vehicle.armed = False

    while vehicle.armed:
        print("⏳ Esperando desarmado...")
        time.sleep(1)

    print("✅ Dron desarmado")


# ---------------- MENÚ INTERACTIVO ----------------
def menu_control():
    while True:
        print("\n🎮 MENÚ CONTROL")
        print("1 → STABILIZE")
        print("2 → LOITER")
        print("3 → AUTO (con throttle)")
        print("4 → LAND")
        print("5 → ARMAR")
        print("6 → DESARMAR")
        print("0 → SALIR")

        opcion = input("Selecciona opción: ")

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
            print("🔴 Cerrando conexión...")
            vehicle.close()
            break
        else:
            print("❌ Opción inválida")


# ---------------- MAIN ----------------
if __name__ == "__main__":
    # Iniciar el hilo de telemetría en segundo plano
    hilo_telemetria = threading.Thread(target=mostrar_telemetria)
    hilo_telemetria.daemon = True
    hilo_telemetria.start()

    menu_control()