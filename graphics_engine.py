# Author: TK
# Date: Edited 2026-01-15
# Description: Graphic engine class
import math
import pygame
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

    def tick(self) -> float:
        dt_ms = self.clock.tick(self.fps)
        return dt_ms / 1000.0

    def draw_player(self, player):
        # Draw a triangle pointing in player.angle
        fx = math.cos(player.angle)
        fy = math.sin(player.angle)

        # triangle points
        nose = (player.x + fx * player.radius, player.y + fy * player.radius)

        # perpendicular vector for base width
        px = -fy
        py = fx
        base_dist = player.radius * 0.75

        left = (player.x - fx * (player.radius * 0.6) + px * base_dist,
                player.y - fy * (player.radius * 0.6) + py * base_dist)
        right = (player.x - fx * (player.radius * 0.6) - px * base_dist,
                 player.y - fy * (player.radius * 0.6) - py * base_dist)

        pygame.draw.polygon(self.screen, (60, 200, 60), [nose, left, right])

    def draw_npc(self, npc):
        pygame.draw.circle(self.screen, (200, 60, 60), (int(npc.x), int(npc.y)), npc.radius)

    def draw_bullet(self, bullet):
        pygame.draw.circle(self.screen, (220, 220, 80), (int(bullet.x), int(bullet.y)), bullet.radius)

    def render(self, player, npcs, bullets, hud_lines):
        self.screen.fill((0, 0, 0))

        # Draw bullets behind entities or in front — your call
        for b in bullets:
            self.draw_bullet(b)

        for n in npcs:
            self.draw_npc(n)

        self.draw_player(player)

        # HUD
        y = 8
        for line in hud_lines:
            surf = self.font.render(line, True, (220, 220, 220))
            self.screen.blit(surf, (8, y))
            y += 20

        pygame.display.flip()
