import time
import pygame

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

    def move(self, left, right, up, down, game_field, dt):
        self.x += self.speed_x * dt * (right - left)
        self.y += self.speed_y * dt * (down - up)
        self.x, self.y, _, _ = game_field.clamp(self.x, self.y)


class NPC:
    def __init__(self, x, y, speed_x=200, speed_y=150):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y

    def move(self, game_field, dt):
        self.x += self.speed_x * dt
        self.y += self.speed_y * dt

        self.x, self.y, x_edge, y_edge = game_field.clamp(self.x, self.y)

        if x_edge:
            self.speed_x = -self.speed_x
        if y_edge:
            self.speed_y = -self.speed_y


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
        self.npc = npc
        self.running = True

    def update_state(self, pressed_keys):
        self.npc.move(self.game_field, self.graph_engine.dt)
        self.player.move(
            "a" in pressed_keys,
            "d" in pressed_keys,
            "w" in pressed_keys,
            "s" in pressed_keys,
            self.game_field,
            self.graph_engine.dt,
        )

        if "q" in pressed_keys:
            self.running = False

    def render_state(self):
        self.graph_engine.start_frame()
        self.graph_engine.render_circle(self.player.x, self.player.y, 40, "red")
        self.graph_engine.render_circle(self.npc.x, self.npc.y, 40, "blue")
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
    npc = NPC(200, 200)

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
