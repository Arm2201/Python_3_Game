import time
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

        if keys[pygame.K_a]:
            self.pressed.add("a")
        if keys[pygame.K_d]:
            self.pressed.add("d")
        if keys[pygame.K_w]:
            self.pressed.add("w")
        if keys[pygame.K_s]:
            self.pressed.add("s")
        if keys[pygame.K_q]:
            self.pressed.add("q")
        if keys[pygame.K_LEFT]:
            self.pressed.add("left")
        if keys[pygame.K_RIGHT]:
            self.pressed.add("right")
        if keys[pygame.K_SPACE]:
            self.pressed.add("fire")


class InputController:
    def __init__(self, kb_poller: KBPoller):
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

    def clamp(self, x, y):
        return (
            max(self.x_min, min(self.x_max, x)),
            max(self.y_min, min(self.y_max, y)),
            self.x_min > x or self.x_max < x,
            self.y_min > y or self.y_max < y,
        )


class Player:
    def __init__(self, x, y, speed_x=300, speed_y=300):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.angle = 0.0
        self.rot_speed = 3.0

    def move(self, left, right, up, down, game_field, dt):
        self.x += self.speed_x * dt * (right - left)
        self.y += self.speed_y * dt * (down - up)
        self.x, self.y, _, _ = game_field.clamp(self.x, self.y)

    def rotate(self, left, right, dt):
        self.angle += self.rot_speed * dt * (right - left)

    def fire(self):
        return Bullet(self.x, self.y, self.angle)


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
        return (
            self.x - self.size // 2,
            self.y - self.size // 2,
            self.x + self.size // 2,
            self.y + self.size // 2
        )


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


def resolve_collision(a, b, radius):
    dx = a.x - b.x
    dy = a.y - b.y
    dist = math.hypot(dx, dy)

    if dist == 0:
        return

    overlap = (radius * 2) - dist
    if overlap > 0:
        nx = dx / dist
        ny = dy / dist

        a.x += nx * overlap / 2
        a.y += ny * overlap / 2
        b.x -= nx * overlap / 2
        b.y -= ny * overlap / 2


#GRAPHICS (pygame)
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
        self.screen.fill("purple")

    def render_circle(self, x, y, radius, color):
        pygame.draw.circle(
            self.screen,
            pygame.Color(color),
            (int(x), int(y)),
            radius
        )

    def draw_player(self, player):
        pygame.draw.circle(
            self.screen,
            "red",
            (int(player.x), int(player.y)),
            40
        )

        end_x = player.x + math.cos(player.angle) * 50
        end_y = player.y + math.sin(player.angle) * 50

        pygame.draw.line(
            self.screen,
            "white",
            (player.x, player.y),
            (end_x, end_y),
            4
        )

    def draw_bullet(self, bullet):
        pygame.draw.circle(
            self.screen,
            "yellow",
            (int(bullet.x), int(bullet.y)),
            6
        )

    def show_frame(self):
        pygame.display.flip()
        self.dt = self.clock.tick(60) / 1000


#ENGINE
class GameEngine:
    def __init__(self, graph_engine, input_controller, game_field, player, npc):
        self.graph_engine = graph_engine
        self.input_controller = input_controller
        self.game_field = game_field
        self.player = player
        self.npcs = npc
        self.bullets = []
        self.running = True

    def update_state(self, pressed_keys):
        for npc in self.npcs:
            npc.move(self.game_field, self.graph_engine.dt)

        self.player.move(
            "a" in pressed_keys,
            "d" in pressed_keys,
            "w" in pressed_keys,
            "s" in pressed_keys,
            self.game_field,
            self.graph_engine.dt,
        )

        self.player.rotate(
            "left" in pressed_keys,
            "right" in pressed_keys,
            self.graph_engine.dt,
        )

        if "fire" in pressed_keys:
            self.bullets.append(self.player.fire())

        for bullet in self.bullets[:]:
            bullet.move(self.graph_engine.dt)

            if bullet.x < 0 or bullet.x > 1280 or bullet.y < 0 or bullet.y > 720:
                self.bullets.remove(bullet)

        for bullet in self.bullets[:]:
            for npc in self.npcs[:]:
                if math.hypot(bullet.x - npc.x, bullet.y - npc.y) < 40:
                    self.bullets.remove(bullet)
                    self.npcs.remove(npc)
                    break

        if "q" in pressed_keys:
            self.running = False

    def render_state(self):
        self.graph_engine.start_frame()

        self.graph_engine.draw_player(self.player)

        for npc in self.npcs:
            self.graph_engine.render_circle(npc.x, npc.y, 40, "blue")

        for bullet in self.bullets:
            self.graph_engine.draw_bullet(bullet)

        self.graph_engine.show_frame()

    def run_game(self):
        while self.running:
            pressed_keys = self.input_controller.get_pressed_keys()
            self.update_state(pressed_keys)
            self.render_state()


#MAIN
if __name__ == "__main__":
    game_field = GameField(0, 0, 1280, 720)

    player = Player(640, 360)

    npc = []
    for i in range(6):
        npc.append(
            NPC(
                random.randint(100, 1100),
                random.randint(100, 600),
                random.randint(-200, 200),
                random.randint(-200, 200),
            )
        )

    graphics = GraphicsEngine()
    input_controller = InputController(KBPoller())

    game = GameEngine(
        graphics,
        input_controller,
        game_field,
        player,
        npc
    )

    game.run_game()
