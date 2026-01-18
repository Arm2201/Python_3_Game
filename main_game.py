# Author: TK
# Date: Edited 2026-01-18
# Description: Main game

from player import Player
from graphics_engine import GraphicsEngine
from game_engine import GameEngine

def main():
    width = 1000
    height = 600

    gfx = GraphicsEngine(width, height, fps=60)
    player = Player(x=width/2, y=height/2, speed=260.0)

    game = GameEngine(player, gfx)
    game.run()

if __name__ == "__main__":
    main()
