import pygame

class PyGameInputController:
    def get_pressed_keys(self):
        pressed = set()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pressed.add("q")

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            pressed.add("left")
        if keys[pygame.K_d]:
            pressed.add("right")
        if keys[pygame.K_w]:
            pressed.add("up")
        if keys[pygame.K_s]:
            pressed.add("down")

        return pressed
