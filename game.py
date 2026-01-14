import time
<<<<<<< HEAD
from player import Player
from npc import NPC
from graphics_engine import GraphicsEngine
from game_engine import GameEngine 
# pip install pynput
=======
from pynput import keyboard
>>>>>>> 3fa0687e0cb0175fcde99aab7b13e4c0cdd66479

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

<<<<<<< HEAD
# NPC (position)
npc_x = 20
npc_y = 20
npc_vx = 1 # moves +1 in x direction each frame
npc_vy = 2 # moves +2 in y direction each frame

x_min = 0
x_max = 100
y_min = 0
y_max = 100
=======
player_x = 0
player_y = 0
>>>>>>> 3fa0687e0cb0175fcde99aab7b13e4c0cdd66479

npc_x = 5
npc_y = 3
npc_dx = 1
npc_dy = 2


def render_state():
<<<<<<< HEAD
    print("player is at:", player_x, player_y , "| npc is at:", npc_x, npc_y)
=======
    print(
        f"\rPlayer: ({player_x},{player_y}) | NPC: ({npc_x},{npc_y})",
        end=""
    )
>>>>>>> 3fa0687e0cb0175fcde99aab7b13e4c0cdd66479


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

def update_npc():
    global npc_x, npc_y, npc_vx, npc_vy
    
    # to move npc
    npc_x += npc_vx
    npc_y += npc_vy
    
    # Bounce on left/right
    if npc_x < x_min:
        npc_x = x_min
        npc_vx = -npc_vx
    elif npc_x > x_max:
        npc_x = x_max
        npc_vx = -npc_vx
        
    # Bounce on top/bottom
    if npc_y < y_min:
        npc_y = y_min
        npc_vy = -npc_vy
    elif npc_y > y_max:
        npc_y = y_max
        npc_vy = -npc_vy
        
while running:
    update_player(poller)
    update_npc()
    render_state()
<<<<<<< HEAD
    keys = scan_keys()

    update_state(keys)
    update_npc()
    
=======
>>>>>>> 3fa0687e0cb0175fcde99aab7b13e4c0cdd66479
    time.sleep(0.1)
