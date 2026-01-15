# Author: TK
# Date: Edited 2026-01-15
# Description: Graphic engine class
import pygame

class GraphicsEngine:
    def __init__(self, grid_w: int, grid_h: int, cell_size: int = 32, fps: int = 60):
        pygame.init()
        
        self.grid_w = grid_w
        self.grid_h = grid_h
        self.cell_size = cell_size
        self.fps = fps
        
        self. screen_w = grid_w * cell_size
        self.screen_h = grid_h * cell_size
        
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        pygame.display.set_caption("Grid Game (Prototype)")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        
    def tick(self) -> float:
        """Limit frame rate and return dt in secs."""
        dt_ms = self.clock.tick(self.fps)
        return dt_ms / 1000.0
    
    def _draw_grid_lines(self) -> None:
        for x in range(self.grid_w + 1):
            pygame.draw.line(
                self.screen,
                (35, 35, 35),
                (x * self.cell_size, 0),
                (x * self.cell_size, self.screen_h)
            )
        
        for y in range(self.grid_h + 1):
            pygame.draw.line(
                self.screen,
                (35, 35, 35),
                (0, y * self.cell_size),
                (self.screen_w, y * self.cell_size)
            )
    
    def render(self, player, npcs, hud_text: str = "WASD to move | ESC to quit") -> None:
        
        # Bg 
        self.screen.fill((0, 0, 0))
        
        # Grid 
        self._draw_grid_lines()
        
        # Draw Npcs (red clr)
        for npc in npcs:
            r = pygame.Rect(
                npc.x * self.cell_size,
                npc.y * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            
            pygame.draw.rect(self.screen, (200, 0, 0), r)
            
        
        # Draw Player (green clr)
        pr = pygame.Rect(
            player.x * self.cell_size,
            player.y * self.cell_size,
            self.cell_size,
            self.cell_size
        )
        
        pygame.draw.rect(self.screen, (0, 200, 0), pr)
        
        # HUD text
        text_surf = self.font.render(hud_text, True, (220, 220, 220))
        self.screen.blit(text_surf, (8, 8))
        
        pygame.display.flip()
        