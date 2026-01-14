# Arm

class Player:
    def __init__(self, x, y, speed=1):
        self.x = x
        self.y = y
        self.speed = speed

    def move(self, keys, x_min, x_max, y_min, y_max):
        if "a" in keys:
            self.x -= self.speed
        if "d" in keys:
            self.x += self.speed
        if "w" in keys:
            self.y -= self.speed
        if "s" in keys:
            self.y += self.speed

        # clamp to screen
        self.x = max(x_min, min(self.x, x_max))
        self.y = max(y_min, min(self.y, y_max))


