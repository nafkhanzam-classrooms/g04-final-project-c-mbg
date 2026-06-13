from words import get_random_word
import threading
import time
import json
from config import ROUND_TIME

import struct
import hashlib
import base64

def perform_handshake(sock):
    """Perform WebSocket handshake"""
    request = b""
    while b"\r\n\r\n" not in request:
        chunk = sock.recv(1024)
        if not chunk:
            return False
        request += chunk

    headers = request.decode('utf-8').split('\r\n')
    key = None
    for header in headers:
        if header.lower().startswith('sec-websocket-key:'):
            key = header.split(':')[1].strip()
            break

    if not key:
        return False

    magic = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    accept_key = base64.b64encode(hashlib.sha1((key + magic).encode('utf-8')).digest()).decode('utf-8')

    response = (
        "HTTP/1.1 101 Switching Protocols\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Accept: {accept_key}\r\n\r\n"
    )
    sock.sendall(response.encode('utf-8'))
    return True

def send_message(sock, data):
    """Send a JSON-serialized message over WebSocket"""
    try:
        message = json.dumps(data).encode('utf-8')
        length = len(message)
        
        b1 = 0x81  # FIN + Text Frame
        if length <= 125:
            header = bytes([b1, length])
        elif length <= 65535:
            header = bytes([b1, 126]) + struct.pack('>H', length)
        else:
            header = bytes([b1, 127]) + struct.pack('>Q', length)
            
        sock.sendall(header + message)
    except Exception as e:
        print(f"[SEND ERROR] {e}")


def _recv_exact(sock, n):
    data = b''
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data

def receive_message(sock):
    """Receive and deserialize a JSON message from WebSocket"""
    try:
        header = _recv_exact(sock, 2)
        if not header:
            return None

        b1, b2 = header
        opcode = b1 & 0x0f
        mask_flag = b2 & 0x80
        payload_len = b2 & 0x7f

        if opcode == 8:  # Connection Close Frame
            return None

        if payload_len == 126:
            ext_len = _recv_exact(sock, 2)
            if not ext_len: return None
            payload_len = struct.unpack('>H', ext_len)[0]
        elif payload_len == 127:
            ext_len = _recv_exact(sock, 8)
            if not ext_len: return None
            payload_len = struct.unpack('>Q', ext_len)[0]

        if mask_flag:
            masking_key = _recv_exact(sock, 4)
            if not masking_key: return None

        payload = _recv_exact(sock, payload_len)
        if not payload: return None

        if mask_flag:
            unmasked = bytearray(payload_len)
            for i in range(payload_len):
                unmasked[i] = payload[i] ^ masking_key[i % 4]
            payload = unmasked

        if opcode == 1:  # Text frame
            message_str = payload.decode('utf-8')
            return json.loads(message_str)
        else:
            return None

    except Exception as e:
        print(f"[RECEIVE ERROR] {e}")
        return None


current_drawer = None
current_word = ""
drawer_index = 0
round_id = 0
_timer_started_for_round = -1  # BUG FIX #4: track which round already has a timer

def assign_roles(players):
    global current_drawer
    global current_word

    if len(players) < 2:
        return None
    if (
        current_drawer is None
        or current_drawer not in players
    ):
        current_drawer = players[0]

    current_word = get_random_word()
    roles = {}

    for username in players:
        roles[username] = (
            "drawer"
            if username == current_drawer
            else "guesser"
        )
    return roles


def next_round(players):
    global drawer_index
    global current_drawer
    global current_word

    if len(players) < 2:
        return None

    drawer_index = (drawer_index + 1) % len(players)
    current_drawer = players[drawer_index]
    current_word = get_random_word()
    roles = {}

    for username in players:
        roles[username] = (
            "drawer"
            if username == current_drawer
            else "guesser"
        )
    return roles

def increase_round():
    global round_id
    round_id += 1
    return round_id

def start_timer(send_timer_func):
    global _timer_started_for_round

    # BUG FIX #4: jangan mulai timer baru jika ronde ini sudah punya timer.
    # Sebelumnya tiap pemain join memanggil start_timer(), sehingga
    # ada N timer berjalan bersamaan untuk 1 ronde yang sama.
    if _timer_started_for_round == round_id:
        return

    _timer_started_for_round = round_id
    current_round = round_id

    def countdown():
        remaining = ROUND_TIME
        while remaining >= 0:
            if current_round != round_id:
                return
            send_timer_func(remaining)
            time.sleep(1)
            remaining -= 1

    threading.Thread(
        target=countdown,
        daemon=True
    ).start()