# UAV-DataStack

Plataforma web para monitoreo, telemetria, control operativo y video de UAV, construida con Flask, Flask-SocketIO, DroneKit, OpenCV y SQLite.

Este repositorio evoluciona un prototipo academico a una base de arquitectura mas limpia y util para escenarios de laboratorio, pruebas SITL y despliegues tecnicos controlados.

## 1) Alcance del sistema

UAV-DataStack integra en una sola aplicacion:

- Telemetria en tiempo real desde proveedor simulado o DroneKit.
- Persistencia historica de misiones y muestras en SQLite mediante SQLAlchemy.
- Dashboard web con mapa Leaflet, graficas Chart.js y stream MJPEG de video.
- API REST para consulta de estado, misiones y acciones de control.
- Capa de seguridad ligera con token estatico y login por usuario.

## 2) Arquitectura general

El proyecto usa patron Application Factory en `app/__init__.py` y separa responsabilidades por modulos:

- `app/config.py`: configuracion por entorno (`development`, `testing`, `production`).
- `app/extensions.py`: inicializacion diferida de `db`, `socketio` y `cors`.
- `app/models.py`: entidades de persistencia (`Mission`, `Telemetry`, `WaterSample`, `EventLog`, `User`).
- `app/api/`: endpoints REST de estado, autenticacion, control y video.
- `app/services/`: logica de telemetria, control y video.
- `app/services/providers/`: proveedores desacoplados (`SimulatedProvider`, `DroneKitProvider`).
- `app/repositories/`: acceso a datos para misiones y telemetria.
- `app/sockets/`: handlers Socket.IO para namespaces `/telemetry` y `/control`.
- `templates/` + `static/`: interfaz dashboard.

Diagrama de flujo operacional resumido:

1. `run.py` crea la app y arranca provider segun `TELEMETRY_PROVIDER` (en desarrollo).
2. `TelemetryService` recibe payloads del provider.
3. Cada payload se persiste en DB (`telemetry_repo.save_telemetry`).
4. El mismo payload se emite por Socket.IO a `/telemetry` como `telemetry.update`.
5. El frontend consume evento, actualiza mapa, graficas y estado visual.
6. Acciones de control llegan por API (`/api/uav/*`) y delegan a `ControlService`.

## 3) Estructura de carpetas

```text
UAV-DataStack/
|- app/
|  |- api/
|  |- repositories/
|  |- services/
|  |  `- providers/
|  |- sockets/
|  |- utils/
|  |- __init__.py
|  |- config.py
|  |- extensions.py
|  `- models.py
|- static/
|  |- css/
|  `- js/
|- templates/
|- tests/
|- scripts/
|- run.py
|- requirements.txt
|- .env.example
`- README.md
```

> Nota: existen archivos historicos (`app.py`, `database.py`) como referencia del prototipo inicial; el flujo recomendado actual es `run.py` + paquete `app/`.

## 4) Requisitos

- Python 3.11+ (probado con 3.13 en entorno Windows, con parche de compatibilidad para DroneKit).
- Pip actualizado.
- OpenCV con acceso a camara (opcional si se desea video real).
- SITL/Mission Planner opcional para telemetria real.

## 5) Instalacion

### 5.1 Crear entorno virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 5.2 Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 5.3 Configurar variables de entorno

```powershell
Copy-Item .env.example .env
```

Editar `.env` segun entorno.

## 6) Variables de entorno

| Variable | Descripcion | Ejemplo |
|---|---|---|
| `FLASK_ENV` | Entorno logico | `development` |
| `FLASK_DEBUG` | Habilita modo debug (1/0) | `1` |
| `SECRET_KEY` | Firma de tokens de usuario | `cambia-esta-clave` |
| `ACCESS_TOKEN` | Token estatico opcional para proteger rutas | `token_local_seguro` |
| `HOST` | Host del servidor | `0.0.0.0` |
| `PORT` | Puerto HTTP | `5000` |
| `DATABASE_URL` | URL SQLAlchemy | `sqlite:///telemetria.db` |
| `DATABASE_TEST_URL` | DB para pruebas | `sqlite:///:memory:` |
| `UAV_CONNECTION` | Conexion DroneKit/MAVLink | `tcp:127.0.0.1:5763` |
| `TELEMETRY_PROVIDER` | Proveedor (`simulated`/`dronekit`) | `simulated` |
| `VIDEO_SOURCE` | Fuente OpenCV (indice o URL) | `0` |
| `CORS_ORIGINS` | Origenes permitidos CORS | `http://localhost:5000` |
| `TELEMETRY_PERSIST_INTERVAL` | Intervalo de lectura/guardado | `1` |
| `SOCKETIO_ASYNC_MODE` | Modo async explicito Socket.IO | `threading` |

## 7) Ejecucion

### 7.1 Modo simulado (recomendado para pruebas iniciales)

```powershell
python run.py
```

Con `TELEMETRY_PROVIDER=simulated`, se generan datos y se persisten automaticamente en desarrollo.

### 7.2 Modo DroneKit (SITL o UAV real)

1. Configura `TELEMETRY_PROVIDER=dronekit`.
2. Configura `UAV_CONNECTION` con endpoint MAVLink correcto.
3. Arranca `python run.py`.

## 8) Seguridad operativa implementada

- Endpoints criticos protegidos con decorador `require_token`.
- Dos mecanismos de acceso:
  - `ACCESS_TOKEN` estatico por entorno.
  - Token firmado por usuario (`/api/auth/login`) con expiracion (max_age de 3600s).
- Login de dashboard para habilitar controles y stream de video.
- Namespace `/control` en Socket.IO validado por token estatico.

## 9) API REST actual

### 9.1 Estado y consulta

| Metodo | Endpoint | Proteccion | Uso |
|---|---|---|---|
| `GET` | `/api/system/status` | Publico | Estado general (uav/db/video) |
| `GET` | `/api/telemetry/latest` | Publico | Ultimos puntos de telemetria |
| `GET` | `/api/missions` | Publico | Lista de misiones |
| `GET` | `/api/video/status` | Publico | Estado del servicio de video |

### 9.2 Misiones

| Metodo | Endpoint | Proteccion | Payload |
|---|---|---|---|
| `POST` | `/api/missions/start` | Token | `{ "name": "Mision X" }` |
| `POST` | `/api/missions/stop` | Token | `{ "mission_id": 1 }` |

### 9.3 Control UAV

| Metodo | Endpoint | Proteccion | Payload |
|---|---|---|---|
| `POST` | `/api/uav/arm` | Token | none |
| `POST` | `/api/uav/disarm` | Token | none |
| `POST` | `/api/uav/mode` | Token | `{ "mode": "AUTO" }` |
| `POST` | `/api/uav/mission_start` | Token | none |

### 9.4 Autenticacion

| Metodo | Endpoint | Proteccion | Payload |
|---|---|---|---|
| `POST` | `/api/auth/register` | Publico | `{ "username": "u", "password": "p" }` |
| `POST` | `/api/auth/login` | Publico | `{ "username": "u", "password": "p" }` |

### 9.5 Video

| Metodo | Endpoint | Proteccion | Uso |
|---|---|---|---|
| `GET` | `/video_feed` | Token | Stream MJPEG |

## 10) Socket.IO

- Namespace `/telemetry`:
  - Emite: `telemetry.update`.
  - Uso: dashboard en vivo.
- Namespace `/control`:
  - Requiere token estatico (`ACCESS_TOKEN`) en handshake.
  - Evento recibido: `control.command`.
  - Evento respuesta: `control.ack`.

## 11) Pruebas

Ejecutar pruebas unitarias actuales:

```powershell
pytest -q
```

Cobertura inicial incluida:

- Endpoints base de sistema.
- Requisito de token en inicio de mision.
- Repositorios de mision y telemetria.

## 12) Flujo de uso recomendado del dashboard

1. Abrir `http://localhost:5000`.
2. Iniciar sesion desde modal (`/api/auth/login`) o usar token estatico.
3. Verificar estado de conexion y video.
4. Monitorear mapa, altitud, modo, voltaje y corriente.
5. Ejecutar acciones de control segun estado de UAV.

## 13) Solucion de problemas

- Video no aparece:
  - Revisar `VIDEO_SOURCE`.
  - Confirmar permisos de camara del sistema.
  - Consultar `GET /api/video/status`.
- No conecta DroneKit:
  - Validar `UAV_CONNECTION`.
  - Confirmar puerto SITL activo.
  - Revisar logs en consola de `run.py`.
- Token invalido:
  - Verificar `SECRET_KEY` estable.
  - Confirmar expiracion del token de usuario.
- UI sin telemetria:
  - Verificar socket `/telemetry`.
  - Confirmar provider activo en logs.

## 14) Limitaciones actuales

- No hay control de roles (solo autenticacion ligera).
- Falta paginacion/filtros para historico de telemetria.
- Falta migraciones formales (se usa `db.create_all()`).
- Endpoints avanzados de historial por mision aun no expuestos.

## 15) Roadmap recomendado

- Migraciones con Flask-Migrate/Alembic.
- Rate limiting por endpoint critico.
- Auditoria mas estricta de comandos UAV.
- Endpoints completos de historico por mision y muestras.
- Integracion CI (pruebas + lint + seguridad).

## 16) Documentacion por carpetas

Cada bloque principal tiene su propia guia detallada:

- `app/README.md`
- `app/api/README.md`
- `app/services/README.md`
- `app/services/providers/README.md`
- `app/repositories/README.md`
- `app/sockets/README.md`
- `app/utils/README.md`
- `static/README.md`
- `templates/README.md`
- `tests/README.md`
- `scripts/README.md`

Estas guias explican responsabilidades, contratos y forma de extension de cada modulo.
