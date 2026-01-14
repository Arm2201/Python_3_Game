# Captain
import time
from pynput import keyboard

class GameEngine:
    def __init__(self, player, npcs, graphics, poller, x_max=20, y_max=10):
        self.player = player
        self.npcs = npcs
        self.graphics = graphics
        self.poller = poller
        self.running = True
        self.x_max = x_max
        self.y_max = y_max

    def update_player(self):
        p = self.poller.pressed
        if 'w' in p:
            self.player.move(0, 1, self.x_max, self.y_max)
        if 's' in p:
            self.player.move(0, -1, self.x_max, self.y_max)
        if 'a' in p:
            self.player.move(-1, 0, self.x_max, self.y_max)
        if 'd' in p:
            self.player.move(1, 0, self.x_max, self.y_max)
        if 'esc' in p:
            self.running = False

    def run(self):
        while self.running:
            self.update_player()
            for npc in self.npcs:
                npc.update(self.x_max, self.y_max)
            self.graphics.render(self.player, self.npcs)
            time.sleep(0.1)
