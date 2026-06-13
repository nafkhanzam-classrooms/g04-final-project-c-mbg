from words import get_random_word
import threading
import time
from config import ROUND_TIME

current_drawer = None
current_word = ""
drawer_index = 0
round_id = 0

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

_timer_started_for_round = -1

def start_timer(send_timer_func, timeout_callback=None):
    global _timer_started_for_round
    if _timer_started_for_round == round_id:
        return
    _timer_started_for_round = round_id
    
    current_round = round_id
    def countdown():
        remaining = ROUND_TIME
        while remaining >= 0:
            if current_round != round_id:
                return
            send_timer_func(
                remaining
            )

            time.sleep(1)
            remaining -= 1
        
        if current_round == round_id and timeout_callback:
            timeout_callback()

    threading.Thread(
        target=countdown,
        daemon=True
    ).start()