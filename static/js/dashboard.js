const socket = io('/telemetry', {
    transports: ['polling'],
    reconnection: true,
    reconnectionAttempts: Infinity,
    reconnectionDelay: 1000,
});

const map = L.map('map').setView([19.8221, -99.2473], 16);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);
const marker = L.marker([19.8221, -99.2473]).addTo(map);
const path = L.polyline([], { color: '#00d4ff' }).addTo(map);
let follow = true;

const badgeConn = document.getElementById('badge-conn');
const badgeMission = document.getElementById('badge-mission');
const videoFeed = document.getElementById('videoFeed');
const videoPlaceholder = document.getElementById('video-placeholder');
const loginModal = document.getElementById('login-modal');
const loginUser = document.getElementById('login-user');
const loginPass = document.getElementById('login-pass');
const loginSubmit = document.getElementById('login-submit');
const loginCancel = document.getElementById('login-cancel');
const loginMessage = document.getElementById('login-message');
const appMessage = document.getElementById('app-message');

const btnArm = document.getElementById('btn-arm');
const btnDisarm = document.getElementById('btn-disarm');
const btnStabilize = document.getElementById('btn-stabilize');
const btnAuto = document.getElementById('btn-auto');
const btnLand = document.getElementById('btn-land');
const btnMissionStart = document.getElementById('btn-mission-start');

function getToken() {
    return localStorage.getItem('uav_token') || '';
}
function setToken(token) {
    localStorage.setItem('uav_token', token);
}
function hasToken() {
    return !!getToken();
}
function setMessage(el, text, type = '') {
    if (!el) return;
    el.textContent = text || '';
    el.style.color = type === 'error' ? '#ff8a8a' : (type === 'success' ? '#86efac' : '#9ca3af');
}
function enableControls(enabled) {
    [btnArm, btnDisarm, btnStabilize, btnAuto, btnLand, btnMissionStart].forEach(b => b.disabled = !enabled);
}
function showVideoPlaceholder(text = 'Cámara no disponible') {
    videoPlaceholder.textContent = text;
    videoFeed.classList.add('hidden');
    videoPlaceholder.classList.remove('hidden');
    videoFeed.removeAttribute('src');
}
function hideVideoPlaceholder() {
    videoPlaceholder.classList.add('hidden');
    videoFeed.classList.remove('hidden');
}
function setMissionBadge(text, active = false) {
    badgeMission.innerText = text;
    badgeMission.className = active ? 'status-badge active' : 'status-badge waiting';
}
function setLoginBusy(isBusy) {
    loginSubmit.disabled = isBusy;
    loginUser.disabled = isBusy;
    loginPass.disabled = isBusy;
    loginSubmit.textContent = isBusy ? 'Entrando...' : 'Login';
}

socket.on('connect', () => {
    badgeConn.innerText = 'Conectado';
    badgeConn.className = 'status-badge online';
});

socket.on('disconnect', () => {
    badgeConn.innerText = 'Desconectado';
    badgeConn.className = 'status-badge waiting';
});

const ctx = document.getElementById('batteryChart').getContext('2d');
const batteryChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            { label: 'Voltaje', data: [], borderWidth: 2 },
            { label: 'Corriente', data: [], borderWidth: 2 }
        ]
    },
    options: {
        animation: false,
        responsive: true,
        maintainAspectRatio: false
    }
});

socket.on('telemetry.update', function (msg) {
    if (msg.lat == null || msg.lon == null) return;

    document.getElementById('alt-val').innerText = Number(msg.alt || 0).toFixed(2);
    document.getElementById('modo-val').innerText = msg.mode || '---';
    document.getElementById('volt-val').innerText = Number(msg.voltage || 0).toFixed(2);
    document.getElementById('current-val').innerText = Number(msg.current || 0).toFixed(2);

    const pos = [msg.lat, msg.lon];
    marker.setLatLng(pos);
    path.addLatLng(pos);
    if (follow) map.panTo(pos);

    const time = new Date().toLocaleTimeString();
    if (batteryChart.data.labels.length > 40) {
        batteryChart.data.labels.shift();
        batteryChart.data.datasets[0].data.shift();
        batteryChart.data.datasets[1].data.shift();
    }
    batteryChart.data.labels.push(time);
    batteryChart.data.datasets[0].data.push(msg.voltage || 0);
    batteryChart.data.datasets[1].data.push(msg.current || 0);
    batteryChart.update('none');
});

async function initVideo() {
    const token = getToken();
    if (!token) {
        showVideoPlaceholder('Inicia sesión para ver la cámara');
        return;
    }

    try {
        const res = await fetch('/api/video/status', { cache: 'no-store' });
        const data = await res.json();

        if (!data.ok || !data.video || !data.video.opened) {
            showVideoPlaceholder('Cámara no disponible');
            return;
        }

        hideVideoPlaceholder();
        videoFeed.src = `/video_feed?access_token=${encodeURIComponent(token)}&t=${Date.now()}`;
        videoFeed.onerror = () => showVideoPlaceholder('Sin frames de la cámara');
    } catch (err) {
        console.error(err);
        showVideoPlaceholder('Error al consultar video');
    }
}

async function doLogin() {
    const user = loginUser.value.trim();
    const pass = loginPass.value.trim();

    if (!user || !pass) {
        setMessage(loginMessage, 'Usuario y contraseña requeridos', 'error');
        return;
    }

    setLoginBusy(true);
    setMessage(loginMessage, 'Verificando credenciales...', '');

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user, password: pass })
        });

        const j = await res.json();
        if (j.ok && j.token) {
            setToken(j.token);
            loginModal.classList.add('hidden');
            enableControls(true);
            setMessage(appMessage, 'Sesión iniciada correctamente', 'success');
            setMessage(loginMessage, '', '');
            await initVideo();
        } else {
            setMessage(loginMessage, 'Login fallido: ' + (j.error || 'credenciales inválidas'), 'error');
        }
    } catch (e) {
        console.error(e);
        setMessage(loginMessage, 'Error al iniciar sesión', 'error');
    } finally {
        setLoginBusy(false);
    }
}

loginSubmit.addEventListener('click', doLogin);
loginPass.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') doLogin();
});
loginCancel.addEventListener('click', () => {
    loginModal.classList.add('hidden');
    setMessage(appMessage, 'Login cancelado', '');
});

async function authPost(url, body = null) {
    const token = getToken();
    const options = {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    };
    if (body) {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(body);
    }
    const res = await fetch(url, options);
    const data = await res.json();
    if (!res.ok) {
        throw new Error(data.error || data.message || 'Error en la solicitud');
    }
    return data;
}

btnArm.addEventListener('click', async () => {
    try {
        const j = await authPost('/api/uav/arm');
        setMessage(appMessage, j.message || 'ARM ejecutado', 'success');
    } catch (e) {
        setMessage(appMessage, e.message, 'error');
    }
});

btnDisarm.addEventListener('click', async () => {
    try {
        const j = await authPost('/api/uav/disarm');
        setMessage(appMessage, j.message || 'DISARM ejecutado', 'success');
    } catch (e) {
        setMessage(appMessage, e.message, 'error');
    }
});

btnStabilize.addEventListener('click', async () => {
    try {
        const j = await authPost('/api/uav/mode', { mode: 'STABILIZE' });
        setMessage(appMessage, j.message || 'Modo STABILIZE enviado', 'success');
    } catch (e) {
        setMessage(appMessage, e.message, 'error');
    }
});

btnAuto.addEventListener('click', async () => {
    try {
        const j = await authPost('/api/uav/mode', { mode: 'AUTO' });
        setMessage(appMessage, j.message || 'Modo AUTO enviado', 'success');
    } catch (e) {
        setMessage(appMessage, e.message, 'error');
    }
});

btnLand.addEventListener('click', async () => {
    try {
        const j = await authPost('/api/uav/mode', { mode: 'LAND' });
        setMessage(appMessage, j.message || 'Modo LAND enviado', 'success');
    } catch (e) {
        setMessage(appMessage, e.message, 'error');
    }
});

btnMissionStart.addEventListener('click', async () => {
    try {
        const j = await authPost('/api/uav/mission_start');
        setMessage(appMessage, j.message || 'Mission Start enviado', 'success');
        setMissionBadge('Misión: Activa', true);
    } catch (e) {
        setMessage(appMessage, e.message, 'error');
    }
});

map.on('dragstart', () => {
    follow = false;
});

if (hasToken()) {
    enableControls(true);
    loginModal.classList.add('hidden');
    setMessage(appMessage, 'Sesión restaurada', 'success');
    initVideo();
} else {
    enableControls(false);
    showVideoPlaceholder('Inicia sesión para ver la cámara');
    loginModal.classList.remove('hidden');
}
