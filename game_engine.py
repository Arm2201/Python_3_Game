# Written by Captain
# Edited by TK on 2024-06-15
# Description: Game engine class

import pygame
import time
class GameEngine:
    def __init__(self, player, npcs, graphics):
        self.player = player
        self.npcs = npcs
        self.graphics = graphics
        self.running = True
        
        self.grid_w = graphics.grid_w
        self.grid_h = graphics.grid_h
        
    def handle_events_and_input(self) -> None:
        # close the window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
        keys = pygame.key.get_pressed()
        
        # quit
        if keys[pygame.K_ESCAPE]:
            self.running = False
            
        # Movement 
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

        if dx != 0 or dy != 0:
            self.player.move(dx, dy, self.grid_w, self.grid_h)

    def update(self, dt: float) -> None:
        # NPC movement and bounce
        for npc in self.npcs:
            npc.update(self.grid_w, self.grid_h)

    def run(self) -> None:
        while self.running:
            dt = self.graphics.tick()
            self.handle_events_and_input()
            self.update(dt)
            self.graphics.render(self.player, self.npcs)

        pygame.quit()
