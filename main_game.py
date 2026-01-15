from player import Player
from npc import NPC
from graphics_engine import GraphicsEngine
from game_engine import GameEngine

def main():
    grid_w = 40
    grid_h = 20

    gfx = GraphicsEngine(grid_w, grid_h, cell_size=32, fps=60)

    player = Player(x=10, y=10, speed=1)
    npcs = [
        NPC(x=20, y=10, vx=1, vy=2),
        NPC(x = 5, y = 5, vx = 2, vy = 1),
        NPC(x = 30, y = 15, vx = 1, vy = -1),
        NPC(x = 10, y = 3, vx = -1, vy = -1)
    ]

    game = GameEngine(player, npcs, gfx)
    game.run()

if __name__ == "__main__":
    main()
