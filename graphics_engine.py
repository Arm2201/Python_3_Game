# Author: TK
# Date: Edited 2026-01-18
# Description: Graphic engine class
import math
import pygame
from settings import BG, HUD_text, HUD_Dim, Bar_BG, Bar_fill, Bullet_color, HUD_Pad, HUD_Bar_w, HUD_Bar_h
class GraphicsEngine:
    def __init__(self, width: int, height: int, fps: int = 60):
        pygame.init()
        self.width = width
        self.height = height
        self.fps = fps

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Triangle shooter")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.font_big = pygame.font.SysFont(None, 34)

    def tick(self) -> float:
        dt_ms = self.clock.tick(self.fps)
        return dt_ms / 1000.0
    
    def draw_bullet(self, b, ox, oy):
        pygame.draw.circle(self.screen, Bullet_color, (int (b.x + ox), int(b.y + oy)), b.radius)

    def draw_particle(self, p, ox, oy):
        pygame.draw.circle(self.screen, p.color, (int(p.x + ox), int(p.y + oy)), p.radius)

    def draw_npc(self, npc, ox, oy):
        pygame.draw.circle(self.screen, npc.color, (int(npc.x + ox), int(npc.y + oy)), npc.radius)

        # Optional HP bar for boss-like NPCs
        if getattr(npc, "hp_max", 1) > 1:
            w = npc.radius * 2
            h = 6
            x = int(npc.x + ox - npc.radius)
            y = int(npc.y + oy - npc.radius - 12)
            pygame.draw.rect(self.screen, Bar_BG, pygame.Rect(x, y, w, h))
            filled = int(w * (npc.hp / npc.hp_max))
            pygame.draw.rect(self.screen, Bar_fill, pygame.Rect(x, y, filled, h))

    def draw_player(self, player, ox, oy, color = (60, 200, 60)):
        fx = math.cos(player.angle)
        fy = math.sin(player.angle)

        nose = (player.x + ox + fx * player.radius, player.y + oy + fy * player.radius)
        px = -fy
        py = fx
        base_dist = player.radius * 0.75

        left = (player.x + ox - fx * (player.radius * 0.6) + px * base_dist,
                player.y + oy - fy * (player.radius * 0.6) + py * base_dist)
        right = (player.x + ox - fx * (player.radius * 0.6) - px * base_dist,
                 player.y + oy - fy * (player.radius * 0.6) - py * base_dist)

        pygame.draw.polygon(self.screen, color, [nose, left, right])

    def draw_hud(self, score, streak, mult, combo_ratio, paused, npc_count):
        x = HUD_Pad
        y = HUD_Pad

        title = self.font_big.render(f"Score: {score}", True, HUD_text)
        self.screen.blit(title, (x, y))
        y += 36

        line = self.font.render(f"Streak: {streak}   Mult: x{mult}   NPCs: {npc_count}", True, HUD_text)
        self.screen.blit(line, (x, y))
        y += 24

        # Combo timer bar
        pygame.draw.rect(self.screen, Bar_BG, pygame.Rect(x, y, HUD_Bar_w, HUD_Bar_h))
        fill_w = int(HUD_Bar_w * combo_ratio)
        pygame.draw.rect(self.screen, Bar_fill, pygame.Rect(x, y, fill_w, HUD_Bar_h))
        y += 18

        hint = self.font.render("WASD move | LEFT/RIGHT rotate | SPACE fire | P pause | R restart | ESC quit", True, HUD_Dim)
        self.screen.blit(hint, (x, y))

        if paused:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            msg = self.font_big.render("PAUSED (Press P to resume)", True, HUD_text)
            self.screen.blit(msg, (self.width // 2 - msg.get_width() // 2, self.height // 2 - 20))

    def render(self, players, npcs, bullets, particles, hud_data, offset=(0, 0)):
        ox, oy = offset

        self.screen.fill(BG)

        # Particles behind
        for p in particles:
            self.draw_particle(p, ox, oy)
        
        for b in bullets:
            self.draw_bullet(b, ox, oy)

        for n in npcs:
            self.draw_npc(n, ox, oy)

        for i, pl in enumerate(players):
            col = (60, 200, 60) if i == 0 else (80, 160, 255)
            self.draw_player(pl, ox, oy, color = col)

        self.draw_hud(**hud_data)

        pygame.display.flip()