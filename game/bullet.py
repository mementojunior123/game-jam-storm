import pygame
from game.sprite import Sprite
from core.core import core_object

from utils.pivot_2d import Pivot2D
import random

class Bullet(Sprite):
    inactive_elements : list['Bullet'] = []
    active_elements : list['Bullet'] = []

    test_image : pygame.Surface = pygame.surface.Surface((8, 8))
    test_image.set_colorkey([0, 255, 0])
    test_image.fill([0, 255, 0])
    pygame.draw.circle(test_image, "Red", (4, 4), 4)

    test_image2 : pygame.Surface = pygame.Surface((8, 8))
    test_image2.set_colorkey([0, 255, 0])
    test_image2.fill([0, 255, 0])
    pygame.draw.rect(test_image2, "Red", (0, 0, 8, 8))

    game_area : pygame.Rect = pygame.Rect(0, 0, *core_object.main_display.get_size())

    def __init__(self) -> None:
        super().__init__()
        self.velocity : pygame.Vector2
        Bullet.inactive_elements.append(self)
    
    @classmethod
    def spawn(cls, pos : pygame.Vector2, speed : float, direction : pygame.Vector2):
        element = cls.inactive_elements[0]

        element.image = cls.test_image if random.randint(0, 1) else cls.test_image2
        element.mask = pygame.mask.from_surface(element.image)
        element.rect = element.image.get_rect()

        element.position = pos.copy()
        element.align_rect()
        element.zindex = 100
        element.pivot = Pivot2D(element._position, element.image, (0, 255, 0))

        element.velocity = direction * speed
        element.align_rect()
        cls.unpool(element)
        return element
    
    def update(self, delta: float):
        self.position += self.velocity * delta
        if not self.rect.colliderect(Bullet.game_area):
            self.kill_instance_safe()
    
    def clean_instance(self):
        self.image = None
        self.mask = None
        self.rect = None
        self.pivot = None
        self._position = pygame.Vector2(0,0)
        self.zindex = None

        self.velocity = None