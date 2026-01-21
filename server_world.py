# Author: TK
# Date: 21-01-2026
# Description: classes for the game and server world

import random
import math
from dataclasses import dataclass
from typing import Dict, List

from npc import choose_npc_class
from constants import (
    PLAYER_SPEED, PLAYER_RADIUS,
    FIRE_RATE,
    BULLET_SPEED, BULLET_RADIUS, BULLET_MAX_LIFE,
    SPAWN_EVERY, STARTING_NPCS, MAX_NPCS
)

def circles_collide(x1, y1, r1, x2, y2, r2) -> bool:
    dx = x1 - x2
    dy = y1 - y2
    return (dx * dx + dy * dy) <= (r1 + r2) * (r1 + r2)

@dataclass
class InputState:
    up: bool = False
    down: bool = False
    left: bool = False
    right: bool = False
    shoot: bool = False
    angle: float = 0.0
    seq: int = 0

@dataclass
class PlayerState:
    x: float
    y: float
    angle: float = 0.0
    radius: float = PLAYER_RADIUS  
    hp: int = 100
    score: int = 0
    fire_cd: float = 0.0  # cooldown

class World:
    """Server world:
    - moves players based on user input
    - spawns NPCs using choose_npc_class(score)
    - spawns bullets from server only
    - simulates bullets
    - bullets vs npc collisions update score + npc hp/destruction
    """
    def __init__(self, world_w: int, world_h: int):
        self.world_w = world_w
        self.world_h = world_h

        self.tick = 0
        self.time = 0.0

        self.players: Dict[int, PlayerState] = {}
        self.bullets: List[dict] = []   # {x,y,vx,vy,owner,life}
        self.npcs: List[object] = []    # NPC objects from npc.py

        self.spawn_timer = 0.0

    def add_player(self, pid: int):
        # spawn near center, slight offset
        cx = self.world_w * 0.5 + (pid % 5) * 30
        cy = self.world_h * 0.5 + ((pid // 5) % 5) * 30
        self.players[pid] = PlayerState(x=cx, y=cy)

        # start NPCs once first player arrives
        if len(self.players) == 1 and not self.npcs:
            for _ in range(STARTING_NPCS):
                self.spawn_npc_random()

    def remove_player(self, pid: int):
        self.players.pop(pid, None)
        # remove bullets owned by pid
        self.bullets = [b for b in self.bullets if b["owner"] != pid]

    def spawn_npc_random(self):
        if len(self.npcs) >= MAX_NPCS:
            return

        x = random.randint(40, self.world_w - 40)
        y = random.randint(40, self.world_h - 40)

        # difficulty based on best player score
        best_score = max((p.score for p in self.players.values()), default=0)
        cls = choose_npc_class(best_score)
        self.npcs.append(cls.spawn(x, y))

    def _spawn_bullet(self, owner: int, x: float, y: float, angle: float, player_radius: float):
        fx = math.cos(angle)
        fy = math.sin(angle)
        spawn_dist = player_radius + 6
        bx = x + fx * spawn_dist
        by = y + fy * spawn_dist
        self.bullets.append({
            "x": bx, "y": by,
            "vx": fx * BULLET_SPEED,
            "vy": fy * BULLET_SPEED,
            "owner": owner,
            "life": 0.0
        })

    def step(self, dt: float, inputs: Dict[int, InputState]):
        self.tick += 1
        self.time += dt

        # spawn NPCs periodically
        self.spawn_timer += dt
        if self.spawn_timer >= SPAWN_EVERY:
            self.spawn_timer = 0.0
            self.spawn_npc_random()

        # Move NPCs (npc.update already handles bouncing)
        for npc in self.npcs:
            npc.update(dt, self.world_w, self.world_h)

        # Players: move + shoot
        for pid, p in self.players.items():
            inp = inputs.get(pid, InputState())
            p.angle = float(inp.angle)

            dx = (1.0 if inp.right else 0.0) - (1.0 if inp.left else 0.0)
            dy = (1.0 if inp.down else 0.0) - (1.0 if inp.up else 0.0)

            if dx != 0.0 or dy != 0.0:
                length = math.hypot(dx, dy)
                dx /= length
                dy /= length

                p.x += dx * PLAYER_SPEED * dt
                p.y += dy * PLAYER_SPEED * dt

                # clamp center pos
                p.x = max(p.radius, min(p.x, self.world_w - p.radius))
                p.y = max(p.radius, min(p.y, self.world_h - p.radius))

            # fire cooldown
            p.fire_cd = max(0.0, p.fire_cd - dt)
            if inp.shoot and p.fire_cd <= 0.0:
                self._spawn_bullet(pid, p.x, p.y, p.angle, p.radius)
                p.fire_cd = FIRE_RATE

        # Bullets: move + age + prune
        alive = []
        for b in self.bullets:
            b["x"] += b["vx"] * dt
            b["y"] += b["vy"] * dt
            b["life"] += dt

            if b["life"] >= BULLET_MAX_LIFE:
                continue
            if b["x"] < -BULLET_RADIUS or b["x"] > self.world_w + BULLET_RADIUS:
                continue
            if b["y"] < -BULLET_RADIUS or b["y"] > self.world_h + BULLET_RADIUS:
                continue

            alive.append(b)
        self.bullets = alive

        # collisions: bullets vs npcs
        used_bullets = set()
        remaining_npcs = []

        for npc in self.npcs:
            destroyed = False
            for j, b in enumerate(self.bullets):
                if j in used_bullets:
                    continue

                if circles_collide(npc.x, npc.y, npc.radius, b["x"], b["y"], BULLET_RADIUS):
                    used_bullets.add(j)

                    destroyed = npc.take_hits()
                    if destroyed:
                        owner = b["owner"]
                        if owner in self.players:
                            self.players[owner].score += int(getattr(npc, "points", 0))
                    break

            if not destroyed:
                remaining_npcs.append(npc)

        self.npcs = remaining_npcs
        self.bullets = [b for idx, b in enumerate(self.bullets) if idx not in used_bullets]

    def snapshot(self) -> dict:
        npc_out = []
        for n in self.npcs:
            npc_out.append({
                "kind": getattr(n, "Kind", "unknown"),
                "x": n.x, "y": n.y,
                "vx": n.vx, "vy": n.vy,
                "radius": getattr(n, "radius", 12),
                "hp": getattr(n, "hp", 1),
                "hp_max": getattr(n, "hp_max", 1),
                "color": getattr(n, "color", (200, 60, 60)),
                "points": getattr(n, "points", 0),
            })

        return {
            "tick": self.tick,
            "players": {
                str(pid): {
                    "x": p.x, "y": p.y,
                    "angle": p.angle,
                    "hp": p.hp,
                    "score": p.score
                } for pid, p in self.players.items()
            },
            "bullets": [
                {"x": b["x"], "y": b["y"], "vx": b["vx"], "vy": b["vy"], "owner": b["owner"]}
                for b in self.bullets
            ],
            "npcs": npc_out
        }

        