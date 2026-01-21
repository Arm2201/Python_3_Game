class Player:
    def __init__(self, id, x, y, speed=4, size=20):
        self.id = id
        self.x = x
        self.y = y
        self.speed = speed
        self.size = size
        self.score = 0

    def move(self, left, right, up, down, rotate, game_field):
        if left:
            self.x -= self.speed
        if right:
            self.x += self.speed
        if up:
            self.y -= self.speed
        if down:
            self.y += self.speed

        self.x, self.y, _, _ = game_field.clamp(self.x, self.y)

    def get_bounding_box(self):
        s = self.size // 2
        return (self.x - s, self.y - s, self.x + s, self.y + s)


class NPC:
    def __init__(self, x, y, speed_x=2, speed_y=2, size=20):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.size = size

    def move(self, game_field):
        self.x += self.speed_x
        self.y += self.speed_y

        self.x, self.y, hit_x, hit_y = game_field.clamp(self.x, self.y)
        if hit_x:
            self.speed_x *= -1
        if hit_y:
            self.speed_y *= -1

    def get_bounding_box(self):
        s = self.size // 2
        return (self.x - s, self.y - s, self.x + s, self.y + s)
