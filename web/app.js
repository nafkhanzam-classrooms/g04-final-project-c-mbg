const loginContainer = document.getElementById('login-container');
const gameContainer = document.getElementById('game-container');
const btnJoin = document.getElementById('btn-join');
const usernameInput = document.getElementById('username');
const serverIpInput = document.getElementById('server-ip');
const loginError = document.getElementById('login-error');

const roleDisplay = document.getElementById('role-display');
const wordDisplay = document.getElementById('word-display');
const timerDisplay = document.getElementById('timer-display');
const playersList = document.getElementById('players-list');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const btnSend = document.getElementById('btn-send');

const canvas = document.getElementById('drawing-board');
const ctx = canvas.getContext('2d');
const overlay = document.getElementById('overlay');

let ws;
let pingInterval;
let isDrawer = false;
let myName = "";
let isDrawing = false;
let lastX = 0;
let lastY = 0;

// Resize canvas dynamically
function resizeCanvas() {
    const parent = canvas.parentElement;
    canvas.width = parent.clientWidth;
    canvas.height = parent.clientHeight;
    // Set style properties
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.lineWidth = 4;
    ctx.strokeStyle = '#000000';
}
window.addEventListener('resize', resizeCanvas);

btnJoin.addEventListener('click', () => {
    myName = usernameInput.value.trim();
    if (!myName) {
        loginError.textContent = "Nama tidak boleh kosong!";
        return;
    }
    connectWebSocket();
});

usernameInput.addEventListener('keypress', (e) => {
    if(e.key === 'Enter') btnJoin.click();
});

function connectWebSocket() {
    let ip = serverIpInput.value.trim() || '127.0.0.1';
    
    // Jika user tidak memasukkan port (misal hanya 127.0.0.1), tambahkan otomatis :9999
    if (!ip.includes(':')) {
        ip += ':9999';
    }
    
    ws = new WebSocket(`ws://${ip}`);

    ws.onopen = () => {
        ws.send(JSON.stringify({ type: 'join', name: myName }));
        
        pingInterval = setInterval(() => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
            }
        }, 2000);
    };

    ws.onmessage = (event) => {
        const packet = JSON.parse(event.data);
        handlePacket(packet);
    };

    ws.onclose = () => {
        clearInterval(pingInterval);
        alert("Terputus dari server!");
        location.reload();
    };

    ws.onerror = (error) => {
        loginError.textContent = "Gagal menyambung ke server.";
        console.error(error);
    };
}

function handlePacket(packet) {
    switch (packet.type) {
        case 'join_success':
            loginContainer.classList.remove('active');
            setTimeout(() => {
                loginContainer.classList.add('hidden');
                gameContainer.classList.remove('hidden');
                resizeCanvas();
            }, 500);
            break;
        case 'error':
            loginError.textContent = packet.message;
            ws.close();
            break;
        case 'system':
            addChatMessage(`[Sistem] ${packet.message}`, true);
            break;
        case 'chat':
            addChatMessage(`${packet.sender}: ${packet.message}`);
            break;
        case 'role':
            isDrawer = packet.role.toLowerCase() === 'drawer';
            roleDisplay.textContent = isDrawer ? "Menggambar" : "Menebak";
            roleDisplay.style.background = isDrawer ? "rgba(0, 242, 254, 0.2)" : "rgba(255, 255, 255, 0.2)";
            roleDisplay.style.color = isDrawer ? "#00f2fe" : "#fff";
            
            if (isDrawer) {
                overlay.style.pointerEvents = 'none';
                overlay.style.opacity = '0';
                overlay.style.display = 'none';
                chatInput.disabled = true;
                btnSend.disabled = true;
                chatInput.placeholder = "Kamu sedang menggambar...";
            } else {
                overlay.style.pointerEvents = 'none';
                overlay.style.opacity = '0';
                overlay.style.display = 'none';
                chatInput.disabled = false;
                btnSend.disabled = false;
                chatInput.placeholder = "Tebak kata...";
            }
            break;
        case 'word':
            wordDisplay.textContent = packet.word.split('').join(' ');
            break;
        case 'timer':
            timerDisplay.textContent = `${packet.time}s`;
            if(packet.time <= 10) {
                timerDisplay.style.background = "rgba(255, 0, 0, 0.5)";
            } else {
                timerDisplay.style.background = "rgba(255, 71, 87, 0.2)";
            }
            break;
        case 'scoreboard':
            updateScoreboard(packet.scores);
            break;
        case 'draw':
            drawLine(packet.x1, packet.y1, packet.x2, packet.y2, false);
            break;
        case 'clear_canvas':
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            break;
        case 'pong':
            if (packet.timestamp) {
                const latency = Date.now() - packet.timestamp;
                const pingDisplay = document.getElementById('ping-display');
                if (pingDisplay) {
                    pingDisplay.textContent = `Ping: ${latency} ms`;
                    if (latency < 100) pingDisplay.style.color = '#00f2fe';
                    else if (latency < 300) pingDisplay.style.color = '#ffd700';
                    else pingDisplay.style.color = '#ff4757';
                }
            }
            break;
    }
}

function updateScoreboard(scores) {
    playersList.innerHTML = '';
    // Sort players by score
    const sorted = Object.entries(scores).sort((a, b) => b[1] - a[1]);
    
    sorted.forEach(([name, score], index) => {
        const li = document.createElement('li');
        li.className = 'player-item';
        li.innerHTML = `
            <span class="player-rank">#${index + 1}</span>
            <span class="player-name">${name}</span>
            <span class="player-score">${score} pt</span>
        `;
        playersList.appendChild(li);
    });
}

function addChatMessage(msg, isSystem = false) {
    const div = document.createElement('div');
    div.className = 'chat-msg' + (isSystem ? ' system' : '');
    div.textContent = msg;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

btnSend.addEventListener('click', () => {
    const text = chatInput.value.trim();
    if (text && ws) {
        ws.send(JSON.stringify({ type: 'chat', message: text }));
        chatInput.value = '';
    }
});

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') btnSend.click();
});

// Drawing logic
function getMousePos(e) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    return {
        x: (e.clientX - rect.left) * scaleX,
        y: (e.clientY - rect.top) * scaleY
    };
}

canvas.addEventListener('mousedown', (e) => {
    if (!isDrawer) return;
    isDrawing = true;
    const pos = getMousePos(e);
    lastX = pos.x;
    lastY = pos.y;
});

canvas.addEventListener('mousemove', (e) => {
    if (!isDrawing || !isDrawer) return;
    const pos = getMousePos(e);
    drawLine(lastX, lastY, pos.x, pos.y, true);
    lastX = pos.x;
    lastY = pos.y;
});

canvas.addEventListener('mouseup', () => isDrawing = false);
canvas.addEventListener('mouseout', () => isDrawing = false);

function drawLine(x1, y1, x2, y2, emit) {
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
    ctx.closePath();

    if (!emit || !ws) return;
    
    ws.send(JSON.stringify({
        type: 'draw',
        x1: x1,
        y1: y1,
        x2: x2,
        y2: y2
    }));
}
