# Written by Captain
# Edited by TK on 2024-06-18
# Description: Game engine class
import random
import pygame
from npc import choose_npc_class
from score_system import ScoreSystem


def circles_collide(x1, y1, r1, x2, y2, r2) -> bool:
    dx = x1 - x2
    dy = y1 - y2
    return (dx*dx + dy*dy) <= (r1 + r2) * (r1 + r2)

class GameEngine:
    def __init__(self, player, graphics):
        self.player = player
        self.gfx = graphics
        self.scoring = ScoreSystem(combo_window=1.25, streak_step=5, max_multiplier=6)

        self.running = True

        self.npcs = []
        self.bullets = []

        # NPC auto-spawn
        self.spawn_timer = 0.0
        self.spawn_every = 1.5  # seconds

        # Fire control
        self.fire_cooldown = 0.0
        self.fire_rate = 0.18  # seconds per shot

        # World size (pixels)
        self.world_w = graphics.width
        self.world_h = graphics.height

        # start with some NPCs
        for _ in range(5):
            self.spawn_npc_random()

    def spawn_npc_random(self):
        x = random.randint(40, self.world_w - 40)
        y = random.randint(40, self.world_h - 40)
        
        cls = choose_npc_class(self.scoring.score)
        self.npcs.append(cls.spawn(x, y))

    def spawn_npc_at(self, x: int, y: int):
        x = max(40, min(x, self.world_w - 40))
        y = max(40, min(y, self.world_h - 40))

        cls = choose_npc_class(self.scoring.score)
        self.npcs.apped(cls.spawn(x, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

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
            self.fire_cooldown = self.fire_rate

    def update(self, dt):
        # Auto-spawn NPCs
        now = pygame.time.get_ticks() / 1000.0
        self.scoring.update_time(now)
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

        # Bullet-NPC collision (remove both)
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
                    destroyed = npc.take_hit()
                    if destroyed:
                        self.scoring.on_hit(now, npc.points)
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

            hud = [
                "WASD move | LEFT/RIGHT rotate | SPACE fire | ESC to quit",
                f"Score: {self.scoring.score}",
                f"Streak: {self.scoring.streak}   Multi: x{self.scoring.multiplier()}",
                f"NPCs: {len(self.npcs)}   Bullets: {len(self.bullets)}",
                "Small = 2  Medium = 4  Large = 8  Boss = 25 (multi-hit) | Left click spawns"
            ]
            
            self.gfx.render(self.player, self.npcs, self.bullets, hud)

        pygame.quit()