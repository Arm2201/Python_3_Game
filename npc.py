# Edited by TK on 2024-06-15
# Wriiten by Arm
# Description: NPC class

class NPC:
    def __init__(self, x: int, y: int, vx: int = 1, vy: int = 1, char: str = "N"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.char = char

    def update(self, grid_w: int, grid_h: int) -> None:
        self.x += self.vx
        self.y += self.vy

        # Bounce X
        if self.x < 0:
            self.x = 0
            self.vx *= -1
        elif self.x >= grid_w - 1:
            self.x = grid_w - 1
            self.vx *= -1
            
        # Bounce Y
        if self.y <= 0:
            self.y = 0
            self.vy *= -1
        elif self.y >= grid_h - 1:
            self.y = grid_h - 1
            self.vy *= -1

