# Written by Captain
# Edited by TK on 2024-06-18
# Description: Game engine class
import random
import pygame
import math

from settings import (spawn_every, Starting_NPCs, Max_NPCs,
                      Fire_rate, Shake_duration, Shake_Strength,
                      Combo_window, Streak_step, Max_multiplier)
from npc import choose_npc_class
from bullets import Bullet
from score_system import ScoreSystem
from particles import spawn_hit_particles


def circles_collide(x1, y1, r1, x2, y2, r2) -> bool:
    dx = x1 - x2
    dy = y1 - y2
    return (dx*dx + dy*dy) <= (r1 + r2) * (r1 + r2)

class GameEngine:
    def __init__(self, player, graphics):
        self.player = player
        self.gfx = graphics

        self.world_w = graphics.width
        self.world_h = graphics.height
        
        self.running = True
        self.paused = False
        
        # camera shake
        self.shake_time = 0.0
        self.shake_strength = 0.0
        
        self.reset() # build game state 
        
    def reset(self):
        # core collections
        self.npcs = []
        self.bullets = []
        self.particles = []
        
        # scoring
        self.scoring = ScoreSystem(Combo_window, Streak_step, Max_multiplier)
        
        # timers
        self.spawn_timer = 0.0
        self.spawn_every = spawn_every
        
        self.fire_cooldown = 0.0
        self.Fire_rate = Fire_rate

        # start with some NPCs
        for _ in range(Starting_NPCs):
            self.spawn_npc_random()
            
    def start_shake(self, strength = Shake_Strength, duration = Shake_duration):
        self.shake_strength = strength
        self.shake_time = duration
        
    def get_shake_offset(self, dt):
        if self.shake_time <= 0:
            return (0, 0)
        self.shake_time -= dt
        ox = random.uniform(-self.shake_strength, self.shake_strength)
        oy = random.uniform(-self.shake_strength, self.shake_strength)
        return (ox, oy)

    def spawn_npc_random(self):
        if len(self.npcs) >= Max_NPCs:
            return 
        
        x = random.randint(40, self.world_w - 40)
        y = random.randint(40, self.world_h - 40)
        
        cls = choose_npc_class(self.scoring.score)
        self.npcs.append(cls.spawn(x, y))

    def spawn_npc_at(self, x: int, y: int):
        if len(self.npcs) >= Max_NPCs:
            return 
        
        x = max(40, min(x, self.world_w - 40))
        y = max(40, min(y, self.world_h - 40))

        cls = choose_npc_class(self.scoring.score)
        self.npcs.append(cls.spawn(x, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.reset()

            # Spawn NPC on mouse click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                self.spawn_npc_at(mx, my)

    def handle_input(self, dt: float):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            self.running = False

        # Orientation (rotate)
        rot_dir = 0
        if keys[pygame.K_LEFT]:
            rot_dir -= 1
        if keys[pygame.K_RIGHT]:
            rot_dir += 1
        if rot_dir != 0:
            self.player.rotate(rot_dir, dt)

        # Movement (WASD)
        dx = 0
        dy = 0
        if keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1

        # Normalize diagonal movement so it's not faster
        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length
            self.player.move(dx, dy, dt, self.world_w, self.world_h)

        # Fire (space)
        self.fire_cooldown = max(0.0, self.fire_cooldown - dt)
        if keys[pygame.K_SPACE] and self.fire_cooldown <= 0.0:
            self.bullets.append(Bullet.from_player(self.player))
            self.fire_cooldown = self.Fire_rate

    def update(self, dt):
        if self.paused:
            return
        
        
        now = pygame.time.get_ticks() / 1000.0
        self.scoring.update_time(now)
        
        # Auto-spawn NPCs
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_every:
            self.spawn_timer = 0.0
            self.spawn_npc_random()

        # Update NPCs
        for npc in self.npcs:
            npc.update(dt, self.world_w, self.world_h)

        # Update bullets + remove dead ones
        alive_bullets = []
        for b in self.bullets:
            b.update(dt)
            if not b.is_dead(self.world_w, self.world_h):
                alive_bullets.append(b)
        self.bullets = alive_bullets
        
        # update particles
        alive_particles = []
        for p in self.particles:
            p.update(dt)
            if not p.dead():
                alive_particles.append(p)
        self.particles = alive_particles
        
        # collisions: bullets and npcs
        def circles_collide(x1, y1, r1, x2, y2, r2):
            dx = x1 - x2
            dy = y1 - y2
            return (dx * dx + dy * dy) <= (r1 + r2) * (r1 + r2)

        remaining_npcs = []
        used_bullets = set()

        for npc in self.npcs:
            destroyed = False
            for j, b in enumerate(self.bullets):
                if j in used_bullets:
                    continue
                
                if circles_collide(npc.x, npc.y, npc.radius, b.x, b.y, b.radius):
                    used_bullets.add(j)
                    
                    # reduce hp; only destroy if hp hits 0
                    destroyed = npc.take_hits()
                    if destroyed:
                        self.scoring.on_hit(now, npc.points)
                        # particles + shake on kill
                        self.particles.extend(spawn_hit_particles(npc.x, npc.y, npc.color, count = 16))
                        self.start_shake()
                    break
                
            if not destroyed:
                remaining_npcs.append(npc)

        # keep bullets that did not hit
        self.bullets = [b for idx, b in enumerate(self.bullets) if idx not in used_bullets]
        self.npcs = remaining_npcs

    def run(self):
        while self.running:
            dt = self.gfx.tick()
            
            self.handle_events()
            self.handle_input(dt)
            self.update(dt)

            now = pygame.time.get_ticks() / 1000.0
            hud_data = {
                "score": self.scoring.score,
                "streak": self.scoring.streak,
                "mult": self.scoring.multiplier(),
                "combo_ratio": self.scoring.combo_ratio(now),
                "paused": self.paused,
                "npc_count": len(self.npcs),
            }
            
            offset = self.get_shake_offset(dt)
            self.gfx.render(
                self.player,
                self.npcs,
                self.bullets,
                self.particles,
                hud_data, offset=offset
            )
            
        pygame.quit()
        