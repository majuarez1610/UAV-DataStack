const map = L.map('map').setView([19.8221, -99.2473], 16);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19
}).addTo(map);

const marker = L.marker([19.8221, -99.2473]).addTo(map);
const path = L.polyline([], { color: '#00d4ff' }).addTo(map);

// ✅ SOCKET 
const socket = io("http://localhost:5000", {
    transports: ["websocket"],
    reconnection: true
});

// ✅ LOGS DE CONEXIÓN
socket.on("connect", () => {
    console.log("🟢 Conectado al backend");
});

socket.on("disconnect", () => {
    console.log("🔴 Desconectado");
});

// GRÁFICA
const ctx = document.getElementById('batteryChart').getContext('2d');

const batteryChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            { label: 'Voltaje', data: [], borderWidth: 2 },
            { label: 'Corriente', data: [], borderWidth: 2 }
        ]
    }
});

// DATOS
socket.on('update_data', function(msg) {

    console.log("DATA:", msg);

    if (!msg.lat || !msg.lon) return;

    document.getElementById('alt-val').innerText = msg.alt.toFixed(2);
    document.getElementById('modo-val').innerText = msg.modo;

    const tag = document.getElementById('mision-tag');
    tag.innerText = msg.mision;

    const pos = [msg.lat, msg.lon];
    marker.setLatLng(pos);
    path.addLatLng(pos);
    map.panTo(pos);

    const time = new Date().toLocaleTimeString();

    if (batteryChart.data.labels.length > 20) {
        batteryChart.data.labels.shift();
        batteryChart.data.datasets[0].data.shift();
        batteryChart.data.datasets[1].data.shift();
    }

    batteryChart.data.labels.push(time);
    batteryChart.data.datasets[0].data.push(msg.voltaje || 0);
    batteryChart.data.datasets[1].data.push(msg.corriente || 0);

    batteryChart.update();
});

// BOTONES
function stabilize(){ console.log("STABILIZE"); }
function loiter(){ console.log("LOITER"); }
function autoMode(){ console.log("AUTO"); }
function land(){ console.log("LAND"); }