from pynput import keyboard
import time
from player import Player
from npc import NPC
from graphics_engine import GraphicsEngine
from game_engine import GameEngine 
# pip install pynput

class KBPoller:
    def on_press(self, key):
        try:
            ch = key.char.lower()
            self.pressed.add(ch)
        except AttributeError:
            pass

    def on_release(self, key):
        try:
            ch = key.char.lower()
            self.pressed.remove(ch)
        except AttributeError:
            pass

    def __init__(self):
        self.pressed = set()

        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start()

running = True

player_x = 10
player_y = 10

npc_x = 20
npc_y = 20
npc_vx = 1 
npc_vy = 2 

x_min = 0
x_max = 100
y_min = 0
y_max = 100

kb = KBPoller()

def scan_keys():
    return kb.pressed

def render_state():
    print("player is at:", player_x, player_y , "| npc is at:", npc_x, npc_y)

def update_state(keys):
    global player_x, player_y, running

    if "a" in keys:
        player_x -= 1
    if "d" in keys:
        player_x += 1
    if "w" in keys:
        player_y -= 1
    if "s" in keys:
        player_y += 1
    if "q" in keys:
        running = False

    if player_x < x_min:
        player_x = x_min
    if player_x > x_max:
        player_x = x_max
    if player_y < y_min:
        player_y = y_min
    if player_y > y_max:
        player_y = y_max

def update_npc():
    global npc_x, npc_y, npc_vx, npc_vy
    
    npc_x += npc_vx
    npc_y += npc_vy
    
    if npc_x < x_min:
        npc_x = x_min
        npc_vx = -npc_vx
    elif npc_x > x_max:
        npc_x = x_max
        npc_vx = -npc_vx
    
    if npc_y < y_min:
        npc_y = y_min
        npc_vy = -npc_vy
    elif npc_y > y_max:
        npc_y = y_max
        npc_vy = -npc_vy
        
while running:
    # read/check for user actions (input)
    # update game state (physics, AI, etc)
    # render game state (graphics)

    render_state()
    keys = scan_keys()

    update_state(keys)
    update_npc()
    
    time.sleep(0.1)