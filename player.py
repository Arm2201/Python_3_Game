# Edited by TK on 2026-01-15
# Written by Arm
# Description: Player class

import math
class Player:
    def __init__(self, x: float, y: float, speed: float = 220.0):
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = 14
        # angle = 0 means facing right
        self.angle = 0.0
        self.turn_speed = 3.5 # radians per second
        
        # radius for collision
        self.radius = 14
        
    def rotate(self, direction: int, dt: float) -> None:
        # direction: -1 for left, 1 for right
        self.angle += direction * self.turn_speed * dt
        
    def move(self, dx: int, dy: int, dt: int, world_w: int, world_h: int) -> None:
        
        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt

        self.x = max(0, min(self.x, world_w - self.radius))
        self.y = max(0, min(self.y, world_h - self.radius))
        
    def forward_vector(self):
        return math.cos(self.angle), math.sin(self.angle)
    