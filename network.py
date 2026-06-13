from protocol import send_message
from players import (clients, clients_lock, scores)
import game


def broadcast(message):
    with clients_lock:
        current_clients = list(
            clients.values()
        )

    for conn in current_clients:
        send_message(
            conn,
            message
        )


def send_player_list():
    with clients_lock:
        player_names = list(
            clients.keys()
        )
    broadcast({
        "type": "player_list",
        "players": player_names
    })


def send_scoreboard():
    broadcast({
        "type": "scoreboard",
        "scores": scores
    })


def send_roles(roles):
    if roles is None:
        return
    
    for username, role in roles.items():
        conn = clients[username]
        send_message(
            conn,
            {
                "type": "role",
                "role": role
            }
        )

        if role == "drawer":
            send_message(
                conn,
                {
                    "type": "word",
                    "word": game.current_word
                }
            )
        else:
            send_message(
                conn,
                {
                    "type": "word",
                    "word": "??????"
                }
            )

def send_timer(seconds):
    broadcast({
        "type": "timer",
        "time": seconds
    })

def handle_timeout():
    broadcast({
        "type": "system",
        "message": f"Waktu habis! Kata yang benar adalah {game.current_word.upper()}."
    })
    with clients_lock:
        roles = game.next_round(list(clients.keys()))
        if roles is not None:
            game.increase_round()
            game.start_timer(send_timer, handle_timeout)
    
    if roles is not None:
        send_roles(roles)
    else:
        broadcast({
            "type": "system",
            "message": "Pemain tidak cukup. Menunggu pemain lain..."
        })
        
    broadcast({
        "type": "clear_canvas"
    })