# Edited by TK on 2026-01-15
# Adjusted the code to run on pygame 

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

grid_w = 40
grid_h = 20

kb = KBPoller()

def scan_keys():
    return kb.pressed

def render_state():
    print("player is at:", player_x, player_y , "| npc is at:", npc_x, npc_y)

def clampToGrid(x, y):
    x = max(x_min, min(x, grid_w - 1))
    y = max(y_min, min(y, grid_h - 1))
    return x, y


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
        
    # Clamps payer to grid bounds
    player_x, player_y = clampToGrid(player_x, player_y)

def update_npc():
    global npc_x, npc_y, npc_vx, npc_vy
    
    npc_x += npc_vx
    npc_y += npc_vy
    
    if npc_x <= 0:
        npc_x = 0
        npc_vx *= -1
    elif npc_x >= grid_w - 1:
        npc_x = grid_w - 1
        npc_vx *= -1
    
    if npc_y <= 0:
        npc_y = 0
        npc_vy *= -1
    elif npc_y > grid_h - 1:
        npc_y = grid_h - 1
        npc_vy *= -1
        
while running:
    
    render_state()
    keys = scan_keys()

    update_state(keys)
    update_npc()
    
    time.sleep(0.1)
