# Edited by TK on 2026-01-15
# Written by Arm
# Description: Player class
class Player:
    def __init__(self, x: int, y: int, speed: int = 1, char: str = "P"):
        self.x = x
        self.y = y
        self.speed = speed
        self.char = char

    def move(self, dx: int, dy: int, grid_w: int, grid_h: int) -> None:
        
        self.x += dx * self.speed
        self.y += dy * self.speed

        self.x = max(0, min(self.x, grid_w - 1))
        self.y = max(0, min(self.y, grid_h - 1))


