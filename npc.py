# Arm

class NPC:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def update(self, x_min, x_max, y_min, y_max):
        self.x += self.vx
        self.y += self.vy

        if self.x < x_min or self.x > x_max:
            self.vx = -self.vx

        if self.y < y_min or self.y > y_max:
            self.vy = -self.vy

        self.x = max(x_min, min(self.x, x_max))
        self.y = max(y_min, min(self.y, y_max))

