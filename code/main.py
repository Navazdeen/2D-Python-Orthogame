import pygame
import sys
from utils import settings
from sprites import Player, Generic
from random import randint
from pytmx.util_pygame import load_pygame


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(settings.WINSIZE)
        pygame.display.set_caption("Mystic Mountain")
        self.clock = pygame.time.Clock()
        self.isrunning = True
        self.all_sprites = pygame.sprite.Group()
        self.collide_sprites = pygame.sprite.Group()
        self.setup()

    def setup(self):
        for i in range(10):
            Generic(
                (randint(100, settings.WIDTH), randint(100, settings.HEIGHT)),
                pygame.Surface((32, 32)),
                [self.all_sprites, self.collide_sprites],
            )
        self.player = Player(
            pos=(100, 100),
            state_dict={
                "idle": [
                    pygame.Surface((32, 32)),
                    pygame.Surface((32, 32)),
                    pygame.Surface((32, 32)),
                    pygame.Surface((32, 32)),
                ]
            },
            groups=[self.all_sprites],
            z=1,
            collide_sprites=self.collide_sprites,
        )

    def update(self):
        self.screen.fill("white")
        self.all_sprites.update(self.clock.tick(settings.FPS) / 1000)
        self.all_sprites.draw(self.screen)
        pygame.display.flip()
        self.clock.tick(settings.FPS)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.isrunning = False
                sys.exit()

    def run(self):
        while self.isrunning:
            self.check_events()
            self.update()


if __name__ == "__main__":
    game = Game()
    game.run()
