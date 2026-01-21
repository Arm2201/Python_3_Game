# Author: TK
# Date: Edited 2026-01-18
# Description: Bullet class for shooting
import math
from settings import Bullet_speed, bullet_Max_life, Bullet_radius
class Bullet:
    def __init__(self, x: float, y: float, vx: float, vy: float):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        
        self.radius = Bullet_radius
        self.lifetime = 0.0
        self.max_lifetime = bullet_Max_life
        
    @staticmethod
    def from_player(player):
        fx, fy = player.forward_vector()
        
        # spawn bullet in triangle
        spawn_dist = player.radius + 6
        bx = player.x + fx * spawn_dist
        by = player.y + fy * spawn_dist
        
        return Bullet(bx, by, fx * Bullet_speed, fy * Bullet_speed)
    
    @staticmethod
    def from_net(d: dict):
        """Build a bullet from a server snapshot dict"""
        b = Bullet(float(d["x"]), float(d["y"]), float(d["vx"]), float(d["vy"]))
        # so bullets don't disappear instantly on the client between snapshots
        b.lifetime = 0.0
        return b
    
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