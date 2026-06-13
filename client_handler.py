import logging
import game
from protocol import (send_message, receive_message, perform_handshake)
from players import (clients, clients_lock, scores)
from network import (broadcast, send_player_list, send_scoreboard, send_roles, send_timer, handle_timeout)
from game import (assign_roles, next_round)

def handle_client(conn, addr):

    username = None

    try:
        if not perform_handshake(conn):
            conn.close()
            return

        join_packet = receive_message(
            conn
        )

        if join_packet is None:
            conn.close()
            return

        if join_packet.get(
            "type"
        ) != "join":

            conn.close()
            return

        username = (
            join_packet
            .get("name", "")
            .strip()
        )

        if username == "":
            conn.close()
            return

        with clients_lock:

            if username in clients:

                send_message(
                    conn,
                    {
                        "type": "error",
                        "message":
                        "Nama sudah dipakai."
                    }
                )

                conn.close()
                return

            is_reconnect = username in scores
            clients[username] = conn
            if not is_reconnect:
                scores[username] = 0

        print(
            f"[JOIN] {username}"
        )

        logging.info(
            f"{username} joined"
        )

        send_message(
            conn,
            {
                "type": "join_success"
            }
        )

        msg_join = "masuk kembali" if is_reconnect else "bergabung"
        broadcast({
            "type": "system",
            "message":
            f"{username} {msg_join} ke room."
        })

        send_player_list()

        with clients_lock:
            player_count = len(clients)

            if player_count >= 2 and (game.current_drawer not in clients):
                roles = assign_roles(list(clients.keys()))
            else:
                roles = None
                if game.current_drawer in clients and game.current_drawer != username:
                    send_roles({username: "guesser"})

        if roles is not None:
            send_roles(roles)
            game.increase_round()
            game.start_timer(send_timer, handle_timeout)
        elif player_count < 2:
            broadcast({
                "type": "system",
                "message": "Menunggu pemain lain untuk memulai game... (Minimal 2 pemain)"
            })

        send_scoreboard()

        while True:

            packet = receive_message(
                conn
            )

            if packet is None:
                break

            packet_type = packet.get(
                "type"
            )

            # ==================
            # CHAT
            # ==================

            if packet_type == "chat":

                text = (
                    packet
                    .get("message", "")
                    .strip()
                )

                if text == "":
                    continue

                if (
                    username != game.current_drawer
                    and text.lower()
                    ==
                    game.current_word.lower()
                ):
                    # BUG FIX #7: update skor di dalam lock agar tidak ada
                    # race condition jika dua pemain menebak benar bersamaan.
                    with clients_lock:
                        scores[username] = scores.get(username, 0) + 10

                    broadcast({
                        "type": "system",
                        "message":
                        f"{username} berhasil menebak kata {game.current_word.upper()}!"
                    })

                    send_scoreboard()

                    with clients_lock:

                        roles = next_round(
                            list(clients.keys())
                        )
                        if roles is not None:
                            game.increase_round()
                            game.start_timer(send_timer, handle_timeout)

                    if roles is not None:
                        send_roles(roles)

                    broadcast({
                        "type": "clear_canvas"
                    })

                    continue

                logging.info(
                    f"{username}: {text}"
                )

                broadcast({
                    "type": "chat",
                    "sender": username,
                    "message": text
                })

            # ==================
            # DRAW
            # ==================

            elif packet_type == "draw":

                if username != game.current_drawer:
                    continue

                broadcast({
                    "type": "draw",
                    "x1": packet["x1"],
                    "y1": packet["y1"],
                    "x2": packet["x2"],
                    "y2": packet["y2"]
                })

            # ==================
            # PING
            # ==================

            elif packet_type == "ping":

                send_message(
                    conn,
                    {
                        "type": "pong",
                        "timestamp": packet.get("timestamp")
                    }
                )

    except Exception as e:

        print(
            "[ERROR]",
            e
        )
        logging.error(f"{username} error: {e}")

    finally:

        if username:

            with clients_lock:

                clients.pop(
                    username,
                    None
                )

                # Skor tidak dihapus untuk mendukung reconnect
                player_count = len(clients)

            broadcast({
                "type": "system",
                "message":
                f"{username} keluar dari room."
            })

            if player_count < 2:
                game.increase_round()
                broadcast({
                    "type": "system",
                    "message": "Pemain kurang dari 2. Permainan dihentikan sementara."
                })
                broadcast({
                    "type": "clear_canvas"
                })

            send_player_list()
            send_scoreboard()

        conn.close()