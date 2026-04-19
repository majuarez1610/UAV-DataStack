// Dashboard frontend logic
const socket = io('/telemetry');

// Map
const map = L.map('map').setView([19.8221, -99.2473], 16);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19}).addTo(map);
const marker = L.marker([19.8221, -99.2473]).addTo(map);
const path = L.polyline([], { color: '#00d4ff' }).addTo(map);
let follow = true;

socket.on('connect', ()=>{ console.log('Connected to telemetry namespace'); document.getElementById('badge-conn').innerText='Conectado'; document.getElementById('badge-conn').className='status-badge online' })
socket.on('disconnect', ()=>{ console.log('Disconnected'); document.getElementById('badge-conn').innerText='Desconectado'; document.getElementById('badge-conn').className='status-badge waiting' })

// Charts
const ctx = document.getElementById('batteryChart').getContext('2d');
const batteryChart = new Chart(ctx, {type:'line', data:{labels:[], datasets:[{label:'Voltaje', data:[], borderWidth:2},{label:'Corriente', data:[], borderWidth:2}]}});

socket.on('telemetry.update', function(msg){
    if(!msg.lat || !msg.lon) return;
    document.getElementById('alt-val').innerText = (msg.alt || 0).toFixed(2);
    document.getElementById('modo-val').innerText = msg.mode || msg.modo || '---';
    document.getElementById('volt-val').innerText = (msg.voltage || msg.voltaje || 0).toFixed(2);
    document.getElementById('current-val').innerText = (msg.current || msg.corriente || 0).toFixed(2);

    const pos = [msg.lat, msg.lon];
    marker.setLatLng(pos);
    path.addLatLng(pos);
    if(follow) map.panTo(pos);

    const time = new Date().toLocaleTimeString();
    if(batteryChart.data.labels.length > 40){ batteryChart.data.labels.shift(); batteryChart.data.datasets[0].data.shift(); batteryChart.data.datasets[1].data.shift(); }
    batteryChart.data.labels.push(time);
    batteryChart.data.datasets[0].data.push(msg.voltage || msg.voltaje || 0);
    batteryChart.data.datasets[1].data.push(msg.current || msg.corriente || 0);
    batteryChart.update();
});

// Video placeholder
function showVideoPlaceholder(){
    document.getElementById('videoFeed').classList.add('hidden');
    document.getElementById('video-placeholder').classList.remove('hidden');
}

// Controls
const btnArm = document.getElementById('btn-arm');
const btnDisarm = document.getElementById('btn-disarm');
const btnAuto = document.getElementById('btn-auto');
const btnLand = document.getElementById('btn-land');

// Auth token from sessionStorage
function hasToken(){ return !!sessionStorage.getItem('uav_token'); }
function enableControls(enabled){ [btnArm,btnDisarm,btnAuto,btnLand].forEach(b=>b.disabled=!enabled) }

if(hasToken()){
    enableControls(true);
    // set video src with token
    const t = sessionStorage.getItem('uav_token');
    document.getElementById('videoFeed').src = `/video_feed?access_token=${encodeURIComponent(t)}`;
} else {
    // show login modal
    document.getElementById('login-modal').classList.remove('hidden');
}

async function doLogin(){
    const user = document.getElementById('login-user').value;
    const pass = document.getElementById('login-pass').value;
    if(!user || !pass) { alert('Usuario y contraseña requeridos'); return; }
    try{
        const res = await fetch('/api/auth/login', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username: user, password: pass})});
        const j = await res.json();
        if(j.ok && j.token){
            sessionStorage.setItem('uav_token', j.token);
            document.getElementById('login-modal').classList.add('hidden');
            enableControls(true);
            document.getElementById('videoFeed').src = `/video_feed?access_token=${encodeURIComponent(j.token)}`;
            alert('Autenticación OK');
        } else {
            alert('Login fallido: ' + (j.error || JSON.stringify(j)));
        }
    }catch(e){
        alert('Error en login');
        console.error(e);
    }
}

document.getElementById('login-submit').addEventListener('click', doLogin);
document.getElementById('login-cancel').addEventListener('click', ()=>{ document.getElementById('login-modal').classList.add('hidden'); });

btnArm.addEventListener('click', async ()=>{
    if(!confirm('Confirmar ARM?')) return;
    const token = sessionStorage.getItem('uav_token');
    const res = await fetch('/api/uav/arm', {method:'POST', headers:{'Authorization': `Bearer ${token}`}});
    const j = await res.json();
    alert(JSON.stringify(j));
});

// follow toggle when user drags map
map.on('dragstart', ()=>{ follow = false });
