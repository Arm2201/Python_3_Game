import time
from pynput import keyboard

class KBPoller:
    def on_press(self, key):
        if hasattr(key, 'char') and key.char:
            self.pressed.add(key.char.lower())
        else:
            self.pressed.add(key)

    def on_release(self, key):
        if hasattr(key, 'char') and key.char:
            self.pressed.discard(key.char.lower())
        else:
            self.pressed.discard(key)

    def __init__(self):
        self.pressed = set()
        keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        ).start()


running = True

x_max = 20
y_max = 10

player_x = 0
player_y = 0

npc_x = 5
npc_y = 3
npc_dx = 1
npc_dy = 2


def render_state():
    print(
        f"\rPlayer: ({player_x},{player_y}) | NPC: ({npc_x},{npc_y})",
        end=""
    )


def update_player(poller):
    global player_x, player_y, running

    if 'w' in poller.pressed and player_y < y_max - 1:
        player_y += 1
    if 's' in poller.pressed and player_y > 0:
        player_y -= 1
    if 'a' in poller.pressed and player_x > 0:
        player_x -= 1
    if 'd' in poller.pressed and player_x < x_max - 1:
        player_x += 1
    if keyboard.Key.esc in poller.pressed:
        running = False


def update_npc():
    global npc_x, npc_y, npc_dx, npc_dy

    npc_x += npc_dx
    npc_y += npc_dy

    if npc_x >= x_max - 1 or npc_x <= 0:
        npc_dx *= -1

    if npc_y >= y_max - 1 or npc_y <= 0:
        npc_dy *= -1


poller = KBPoller()

while running:
    update_player(poller)
    update_npc()
    render_state()
    time.sleep(0.1)
