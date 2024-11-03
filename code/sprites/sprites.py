from typing import Any, Dict, List
import pygame
from pygame.sprite import Group
from utils import settings


class Generic(pygame.sprite.Sprite):
    def __init__(
        self,
        pos: tuple[int, int] | pygame.Vector2,
        surf: pygame.Surface,
        groups: List[pygame.sprite.Group] | pygame.sprite.Group,
        z: int = 0,
    ):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(
            -self.rect.width * 0.2, -self.rect.height * 0.75
        )


class AnimatedSprite(Generic):
    def __init__(
        self,
        pos: tuple[int, int] | pygame.Vector2,
        frames: List[pygame.Surface],
        groups: List[pygame.sprite.Group] | pygame.sprite.Group,
        z: int = 0,
        animation_speed: float = 200,  # in milliseconds
    ):
        self.frame_index = 0
        self.frames = frames
        self.animation_speed = animation_speed
        self.current_time = pygame.time.get_ticks()
        super().__init__(pos, self.frames[0], groups, z)

    def animate(self) -> None:
        if pygame.time.get_ticks() - self.current_time > self.animation_speed:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
            self.current_time = pygame.time.get_ticks()

    def update(self, dt: int | float):
        self.animate()


class CharacterSprite(AnimatedSprite):
    def __init__(
        self,
        pos: tuple[int, int] | pygame.Vector2,
        state_dict: Dict[str, List[pygame.Surface]],
        groups: List[pygame.sprite.Group] | pygame.sprite.Group,
        z: int = 0,
        animation_speed: float = 200,  # in milliseconds
    ):
        self.direction = pygame.math.Vector2()
        self.state_dict = state_dict
        self.state = "idle"
        super().__init__(pos, self.state_dict[self.state], groups, z, animation_speed)

    def setState(self, state: str):
        if state != self.state:
            self.state = state
            self.frame_index = 0
            self.frame = self.state_dict[self.state]


class Player(CharacterSprite):
    def __init__(
        self,
        pos: tuple[int, int] | pygame.Vector2,
        state_dict: Dict[str, List[pygame.Surface]],
        groups: List[pygame.sprite.Group] | pygame.sprite.Group,
        z: int = 0,
        animation_speed: float = 200,  # in milliseconds
        collide_sprites: Group = None,
    ):
        super().__init__(pos, state_dict, groups, z, animation_speed)
        self.speed = settings.PLAYER_SPEED
        self.collide_sprites: List[Generic] = collide_sprites or Group()

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.direction.x = -1
        elif keys[pygame.K_RIGHT]:
            self.direction.x = 1
        else:
            self.direction.x = 0

        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if self.direction:
            self.direction = self.direction.normalize()

    def collision(self, direction: str):
        if direction == "horizontal":
            for sprite in self.collide_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
                    self.rect.centerx = self.hitbox.centerx
                    self.direction.x = 0
        if direction == "vertical":
            for sprite in self.collide_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom
                    self.rect.centery = self.hitbox.centery
                    self.direction.y = 0

    def move(self, dt: int | float):
        self.hitbox.x += self.direction.x * self.speed * dt
        self.collision("horizontal")
        self.hitbox.y += self.direction.y * self.speed * dt
        self.collision("vertical")
        self.rect.center = self.hitbox.center

    def update(self, dt: int | float):
        self.input()
        self.move(dt)
        self.animate()

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)


class EnemySimple(AnimatedSprite):
    def __init__(
        self,
        pos: tuple[int, int] | pygame.Vector2,
        frames: List[pygame.Surface],
        groups: List[pygame.sprite.Group] | pygame.sprite.Group,
        player: CharacterSprite,
        z: int = 0,
        animation_speed: float = 200,  # in milliseconds
        collide_sprites: Group = None,
    ):
        super().__init__(pos, frames, groups, z, animation_speed)
        self.collide_sprites: List[Generic] = collide_sprites or Group()
        self.direction = pygame.math.Vector2()
        self.rect.center = pos
        self.hitbox = self.rect.copy().inflate(
            -self.rect.width * 0.2, -self.rect.height * 0.75
        )
        self.player = player
        self.speed = settings.ENEMY_SPEED

    def collision(self, direction: str):
        if direction == "horizontal":
            for sprite in self.collide_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
                    self.rect.centerx = self.hitbox.centerx
                    self.direction.x = 0
        if direction == "vertical":
            for sprite in self.collide_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom
                    self.rect.centery = self.hitbox.centery
                    self.direction.y = 0

    def move(
        self,
        dt: int | float,
        target: pygame.Rect = None,
    ):
        threshold = 1  # Adjust based on game scale

        target = target or self.player.hitbox
        if abs(target.centerx - self.hitbox.centerx) > threshold:
            self.direction.x = 1 if target.centerx > self.hitbox.centerx else -1
        else:
            self.direction.x = 0

        if abs(target.centery - self.hitbox.centery) > threshold:
            self.direction.y = 1 if target.centery > self.hitbox.centery else -1
        else:
            self.direction.y = 0

        if self.direction.length_squared() > 0.1:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * self.speed * dt
        self.collision("horizontal")
        self.hitbox.y += self.direction.y * self.speed * dt
        self.collision("vertical")
        self.rect.center = self.hitbox.center

    def update(self, dt: int | float):
        self.move(dt)
        self.animate()


class EnemyAdvanced(EnemySimple):
    def __init__(
        self,
        pos: tuple[int, int] | pygame.Vector2,
        frames: List[pygame.Surface],
        groups: List[pygame.sprite.Group] | pygame.sprite.Group,
        player: CharacterSprite,
        z: int = 0,
        animation_speed: float = 200,  # in milliseconds
        collide_sprites: Group = None,
    ):
        super().__init__(
            pos, frames, groups, player, z, animation_speed, collide_sprites
        )
        self.initial_rect = self.rect.copy()
        self.speed = settings.ENEMY_SPEED * 1.5
        # create enemy radius circle which is used to detect player is within the enemy raidus
        self.radius = 100
        self.radius_circle = pygame.draw.circle(
            pygame.display.get_surface(),
            "red",
            self.rect.center,
            self.radius,
            1,
        )

    def move_to(self, target: pygame.Rect, dt: int | float):
        # move towards the player
        if target.center != self.rect.center:
            super().move(dt, target)

    def move(self, dt: int | float):
        self.radius_circle.center = self.rect.center
        # check if there is a collision between player and radius circle
        if self.radius_circle.colliderect(self.player.hitbox):
            # if player is within enemy range, move towards the player
            super().move(dt)
        else:
            self.move_to(self.initial_rect, dt)

    def draw(self, screen: pygame.Surface):
        print("called")
        screen.blit(self.image, self.rect)
