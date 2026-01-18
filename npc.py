# Edited by TK on 2024-06-18
# Wriiten by Arm
# Description: NPC class
import random
class NPCBase:
    """Base class for NPC movement, bouncing, and hit behavior.
    Child classes include radius, points, color"""
    
    Kind = "base"
    radius = 12
    points = 0
    color = (200, 60, 60)
    
    speed_min = 90
    speed_max = 160
    hp_max = 1 
    
    def __init__(self, x: float, y: float, vx: float, vy: float):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.hp = self.hp_max
        
    @classmethod
    def spawn(cls, x: float, y: float):
        # random velocity within class range
        speed_x = random.uniform(cls.speed_min, cls.speed_max)
        speed_y = random.uniform(cls.speed_min, cls.speed_max)
        vx = random.choice([-1, 1]) * speed_x
        vy = random.choice([-1, 1]) * speed_y
        return cls(x, y, vx, vy)

    def update(self, dt, world_w: int, world_h: int) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Bounce on walls (using radius so it never clips outside)
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
    
    def take_hits(self) -> bool:
        """Return True if npc is destroyed by hit.
        Boss uses hp > 1 so it may survive."""
        self.hp -= 1
        return self.hp <= 0

class SmallNPC(NPCBase):
    Kind = "small"
    radius = 8
    points = 2
    color = (80, 180, 255)
    speed_min = 140
    speed_max = 240
    hp_max = 1
    
class MediumNPC(NPCBase):
    Kind = "medium"
    radius = 12
    points = 4
    color = (200, 60, 60)
    speed_min = 90
    speed_max = 160
    hp_max = 1
    
class LargeNPC(NPCBase):
    Kind = "large"
    radius = 18
    points = 8
    color = (160, 90, 220)
    speed_min = 55
    speed_max = 110
    hp_max = 2
    
class BossNPC(NPCBase):
    Kind = "Big Boss"
    radius = 30
    # Base points for multipler
    points = 25
    color = (255, 150, 40)
    speed_min = 35
    speed_max = 70
    hp_max = 7 # needs 7 hits to kill
    
def choose_npc_class(score:int):
    """Spawning logic 
    early game is mostly small/medium, large npcs appear later, boss appears after score hits 150"""
    
    # Boss chance ramps up with score
    if score >= 150 and random.random() < 0.08:
        return BossNPC
    
    # normal spawns
    if score < 80:
        spawn_classes = [SmallNPC, MediumNPC, LargeNPC]
        weights = [0.55, 0.35, 0.10]
    else:
        spawn_classes = [SmallNPC, MediumNPC, LargeNPC]
        weights = [0.40, 0.35, 0.25]
        
    return random.choices(spawn_classes, weights=weights, k=1)[0]

