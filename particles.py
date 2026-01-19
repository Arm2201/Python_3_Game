# Author: TK
# Date: 18-01-2026
# Description: class to create hit particles at x, y locations

import random

class Particle:
    def __init__(self, x, y, vx, vy, life, radius, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.radius = radius
        self.color = color
        self.age = 0.0
        
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt
        
    def dead(self):
        return self.age >= self.life
    
def spawn_hit_particles(x, y, base_color, count=14):
        """Creates a burst of small partices at x, y."""
        parts = []
        for _ in range(count):
            vx = random.uniform(-220, 220)
            vy = random.uniform(-220, 220)
            life = random.uniform(0.18, 0.35)
            radius = random.randint(2, 4)
            parts.append(Particle(x, y, vx, vy, life, radius, base_color))
        return parts
    