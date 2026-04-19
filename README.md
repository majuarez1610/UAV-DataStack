UAV-DataStack
=================

Refactor y mejora del prototipo UAV-DataStack. Plataforma web para monitoreo y control (simulado / DroneKit).

Features principales
- Backend modular Flask (application factory)
- Persistencia con Flask-SQLAlchemy (SQLite por defecto)
- Telemetry providers: SimulatedProvider y DroneKitProvider
- Video streaming con OpenCV (VideoService) y endpoint MJPEG (/video_feed) protegido
- Control seguro: endpoints protegidos por token o autenticación de usuarios
- Frontend dashboard: mapa (Leaflet), gráficas (Chart.js), video y controles

Quickstart
1. Crear entorno virtual e instalar dependencias

   python -m venv .venv
   .venv\Scripts\activate    # Windows
   pip install -r requirements.txt

2. Copiar .env.example a .env y configurar

   cp .env.example .env
   # Edita .env: SECRET_KEY, ACCESS_TOKEN (opcional), UAV_CONNECTION si usas simulador SITL

3. Ejecutar en modo desarrollo (simulado por defecto)

   python run.py

4. Abrir http://localhost:5000 y usar el dashboard

API Endpoints
- GET /api/system/status
- GET /api/telemetry/latest
- GET /api/missions
- POST /api/missions/start  (requires token)
- POST /api/missions/stop   (requires token)
- POST /api/uav/arm         (requires token)
- POST /api/uav/disarm      (requires token)
- POST /api/uav/mode        (requires token)
- GET /api/video/status
- GET /video_feed           (MJPEG, requires token)
- POST /api/auth/register
- POST /api/auth/login

Notes
- Controls: puedes usar ACCESS_TOKEN (static) o crear usuarios con /api/auth/register y obtener token con /api/auth/login.
- DroneKit: para usar el proveedor real configura TELEMETRY_PROVIDER=dronekit y UAV_CONNECTION en .env. En development el provider autoarranca.
- Video: si no hay cámara disponible, el frontend mostrará placeholder; el VideoService no aborta la aplicación.

Limitations & Next steps
- Add comprehensive tests (CI), rate limiting, and tighter role-based auth if necesario.
- Consider Flask-Migrate for schema migrations en producción.
