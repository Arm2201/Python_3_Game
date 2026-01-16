# Edited by TK on 2024-06-15
# Wriiten by Arm
# Description: NPC class
import random
class NPC:
    def __init__(self, x: float, y: float, vx: float, vy: float, radius: int = 12):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        
    def random_spawn(x: float, y: float):
        # random velocity 
        vx = random.choice([-1, 1]) * random.uniform(80, 160)
        vy = random.choice([-1, 1]) * random.uniform(80, 160)
        return NPC(x, y, vx, vy)

    def update(self, dt, world_w: int, world_h: int) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Bounce on walls
        # Bounce X
        if self.x <= self.radius:
            self.x = self.radius
            self.vx *= -1
        elif self.x >= world_w - self.radius:
            self.x = world_w - self.radius
            self.vx *= -1
            
        # Bounce Y
        if self.y <= self.radius:
            self.y = self.radius
            self.vy *= -1
        elif self.y >= world_h - self.radius:
            self.y = world_h - self.radius
            self.vy *= -1
