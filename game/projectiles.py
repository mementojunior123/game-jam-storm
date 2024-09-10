import pygame
from game.sprite import Sprite
from core.core import core_object

from utils.pivot_2d import Pivot2D
import random

class BulletTeams:
    def __init__(self) -> None:
        self.neutral = 'Neutral'
        self.friendly = 'Friendly'
        self.enemy = 'Zombie'

class BaseProjectile(Sprite):
    inactive_elements : list['BaseProjectile'] = []
    active_elements : list['BaseProjectile'] = []

    test_image : pygame.Surface = pygame.surface.Surface((8, 8))
    test_image.set_colorkey([0, 255, 0])
    test_image.fill([0, 255, 0])
    pygame.draw.circle(test_image, "Red", (4, 4), 4)

    test_image2 : pygame.Surface = pygame.Surface((8, 8))
    test_image2.set_colorkey([0, 255, 0])
    test_image2.fill([0, 255, 0])
    pygame.draw.rect(test_image2, "Red", (0, 0, 8, 8))

    game_area : pygame.Rect = pygame.Rect(0, 0, *core_object.main_display.get_size())
    TEAMS : BulletTeams = BulletTeams()

    def __init__(self) -> None:
        super().__init__()
        self.velocity : pygame.Vector2
        self.team : str
        self.damage : float|int
        BaseProjectile.inactive_elements.append(self)
    
    @classmethod
    def pool(cls, element):
        '''Transfers an element from active to inactive state. Nothing changes if the element is already inactive.'''
        if element in BaseProjectile.active_elements:
            cls.active_elements.remove(element)
        
        if element in Sprite.active_elements:
            Sprite.active_elements.remove(element)
        
        if element not in BaseProjectile.inactive_elements:
            cls.inactive_elements.append(element)

        if element not in Sprite.inactive_elements:
            Sprite.inactive_elements.append(element)
    
    @classmethod
    def unpool(cls, element):
        '''Transfers an element from inactive to active state. Nothing changes if the element is already active.'''

        if element not in BaseProjectile.active_elements:
            cls.active_elements.append(element)
        
        if element not in Sprite.active_elements:
            Sprite.active_elements.append(element)


        if element in BaseProjectile.inactive_elements:
            cls.inactive_elements.remove(element)

        if element in Sprite.inactive_elements:
            Sprite.inactive_elements.remove(element)

    
    @classmethod
    def spawn(cls, pos : pygame.Vector2, speed : float, direction : pygame.Vector2, team : str = 'Friendly',
              damage : float|int = 1):
        element = cls.inactive_elements[0]
        cls.unpool(element)

        element.image = cls.test_image if random.randint(0, 1) else cls.test_image2
        element.mask = pygame.mask.from_surface(element.image)
        element.rect = element.image.get_rect()

        element.position = pos.copy()
        element.align_rect()
        element.zindex = 100
        element.pivot = Pivot2D(element._position, element.image, (0, 255, 0))

        element.velocity = direction * speed
        element.team = team
        element.align_rect()

        element.damage = damage
        
        return element
    
    def is_hostile(self, other_team : str = 'Friendly'):
        lookup_table = {
            self.TEAMS.friendly : {self.TEAMS.friendly : False, self.TEAMS.enemy : True, self.TEAMS.neutral : True},
            self.TEAMS.enemy : {self.TEAMS.friendly : True, self.TEAMS.enemy : False, self.TEAMS.neutral : True},
            self.TEAMS.neutral : {self.TEAMS.friendly : True, self.TEAMS.enemy : True, self.TEAMS.neutral : True}
        }
        return lookup_table[self.team][other_team]
    
    
    def update(self, delta: float):
        self.position += self.velocity * delta
        if not self.rect.colliderect(BaseProjectile.game_area):
            self.kill_instance_safe()
    
    def clean_instance(self):
        self.image = None
        self.mask = None
        self.rect = None
        self.pivot = None
        self._position = pygame.Vector2(0,0)
        self.zindex = None

        self.velocity = None
        self.damage = None
        self.team = None
    
Sprite.register_class(BaseProjectile)