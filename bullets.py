# Author: TK
# Date: Edited 2026-01-16
# Description: Bullet class for shooting
import math

class Bullet:
    def __init__(self, x: float, y: float, vx: float, vy: float):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        
        self.radius = 4
        self.lifetime = 0.0
        self.max_lifetime = 2.5 # backup
        
    @staticmethod
    def from_player(player, speed: float = 420.0):
        fx, fy = player.forward_vector()
        
        # spawn bullet in triangle
        spawn_dist = player.radius + 6
        bx = player.x + fx * spawn_dist
        by = player.y + fy * spawn_dist
        
        return Bullet(bx, by, fx * speed, fy * speed)
    
    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime += dt
        
    def is_dead(self, world_w: int, world_h: int) -> bool:
        if self.lifetime >= self.max_lifetime:
            return True
        if self.x < -self.radius or self.x > world_w + self.radius:
            return True
        if self.y < -self.radius or self.y > world_h + self.radius:
            return True
        return False