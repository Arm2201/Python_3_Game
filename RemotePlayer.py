# Author: TK
# Date: 2026-01-21
# Description: RemotePlayer class for networked multiplayer

class RemotePlayer:
    def __init__(self, pid: int):
        self.pid = pid
        self.x = 0.0
        self.y = 0.0
        self.angle = 0.0
        self.radius = 14
        self.hp = 100
        self.score = 0
        
    def apply_state(self, st: dict):
        self.x = float(st["x"])
        self.y = float(st["y"])
        self.angle = float(st["angle"])
        self.hp = int(st["hp", 100])
        self.score = int(st["score", 0])
        
    