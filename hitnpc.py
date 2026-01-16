import pygame
import math
import random

#INPUT
class KBPoller:
    def __init__(self):
        self.pressed = set()

    def poll(self):
        keys = pygame.key.get_pressed()
        self.pressed.clear()

        if keys[pygame.K_a]: self.pressed.add("a")
        if keys[pygame.K_d]: self.pressed.add("d")
        if keys[pygame.K_w]: self.pressed.add("w")
        if keys[pygame.K_s]: self.pressed.add("s")
        if keys[pygame.K_q]: self.pressed.add("q")
        if keys[pygame.K_LEFT]: self.pressed.add("left")
        if keys[pygame.K_RIGHT]: self.pressed.add("right")
        if keys[pygame.K_SPACE]: self.pressed.add("fire")


class InputController:
    def __init__(self, kb_poller):
        self.kb_poller = kb_poller

    def get_pressed_keys(self):
        self.kb_poller.poll()
        return self.kb_poller.pressed


#GAME LOGIC
class GameField:
    def __init__(self, x_min, y_min, x_max, y_max):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

    def inside(self, x, y):
        return self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max

    def clamp(self, x, y):
        return (
            max(self.x_min, min(self.x_max, x)),
            max(self.y_min, min(self.y_max, y)),
        )


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 300
        self.angle = 0.0
        self.rot_speed = 3.0  # rad/sec

    def move(self, left, right, up, down, game_field, dt):
        self.x += self.speed * dt * (right - left)
        self.y += self.speed * dt * (down - up)
        self.x, self.y = game_field.clamp(self.x, self.y)

    def rotate(self, left, right, dt):
        self.angle += self.rot_speed * dt * (right - left)

    def fire(self):
        return Bullet(self.x, self.y, self.angle)


class NPC:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed_x = random.randint(-200, 200)
        self.speed_y = random.randint(-200, 200)

    def move(self, game_field, dt):
        self.x += self.speed_x * dt
        self.y += self.speed_y * dt

        if not game_field.inside(self.x, self.y):
            self.speed_x *= -1
            self.speed_y *= -1


class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.speed = 600
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed

    def move(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt


def hit(a, b, radius):
    return math.hypot(a.x - b.x, a.y - b.y) < radius


#GRAPHICS
class GraphicsEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("GameEngine + pygame")
        self.clock = pygame.time.Clock()
        self.dt = 0

    def start_frame(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        self.screen.fill("black")

    def draw_player(self, player):
        pygame.draw.circle(self.screen, "red", (int(player.x), int(player.y)), 40)
        end_x = player.x + math.cos(player.angle) * 50
        end_y = player.y + math.sin(player.angle) * 50
        pygame.draw.line(self.screen, "white",
                         (player.x, player.y), (end_x, end_y), 4)

    def draw_npc(self, npc):
        pygame.draw.circle(self.screen, "blue", (int(npc.x), int(npc.y)), 40)

    def draw_bullet(self, bullet):
        pygame.draw.circle(self.screen, "yellow",
                           (int(bullet.x), int(bullet.y)), 6)

    def show_frame(self):
        pygame.display.flip()
        self.dt = self.clock.tick(60) / 1000


#ENGINE
class GameEngine:
    def __init__(self, graphics, input_ctrl, game_field, player):
        self.graphics = graphics
        self.input = input_ctrl
        self.game_field = game_field
        self.player = player
        self.npcs = []
        self.bullets = []
        self.running = True

    def update(self, keys):
        self.player.move(
            "a" in keys, "d" in keys,
            "w" in keys, "s" in keys,
            self.game_field, self.graphics.dt
        )

        self.player.rotate("left" in keys, "right" in keys, self.graphics.dt)

        if "fire" in keys:
            self.bullets.append(self.player.fire())

        for npc in self.npcs:
            npc.move(self.game_field, self.graphics.dt)

        for bullet in self.bullets[:]:
            bullet.move(self.graphics.dt)
            if not self.game_field.inside(bullet.x, bullet.y):
                self.bullets.remove(bullet)

        for bullet in self.bullets[:]:
            for npc in self.npcs[:]:
                if hit(bullet, npc, 40):
                    self.bullets.remove(bullet)
                    self.npcs.remove(npc)
                    break

        if "q" in keys:
            self.running = False

    def render(self):
        self.graphics.start_frame()
        self.graphics.draw_player(self.player)

        for npc in self.npcs:
            self.graphics.draw_npc(npc)

        for bullet in self.bullets:
            self.graphics.draw_bullet(bullet)

        self.graphics.show_frame()

    def run(self):
        while self.running:
            keys = self.input.get_pressed_keys()

            if pygame.mouse.get_pressed()[0]:
                x, y = pygame.mouse.get_pos()
                self.npcs.append(NPC(x, y))

            self.update(keys)
            self.render()


#MAIN
if __name__ == "__main__":
    field = GameField(0, 0, 1280, 720)
    player = Player(640, 360)

    graphics = GraphicsEngine()
    input_ctrl = InputController(KBPoller())

    game = GameEngine(graphics, input_ctrl, field, player)
    game.run()
