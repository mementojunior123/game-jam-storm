import pygame
from game.sprite import Sprite
from core.core import core_object
from utils.pivot_2d import Pivot2D
from game.projectiles import BaseProjectile

class Zombie(Sprite):
    inactive_elements : list["Zombie"] = []
    active_elements : list['Zombie'] = []

    test_image : pygame.Surface = pygame.surface.Surface((50, 50))
    test_image.set_colorkey([0, 0, 255])
    test_image.fill([0, 0, 255])
    pygame.draw.circle(test_image, "Red", (25, 25), 25)

    def __init__(self) -> None:
        super().__init__()
        self.dynamic_mask = True
        self.speed : float
        self.max_hp : int
        self.hp : int
        Zombie.inactive_elements.append(self)
    
    @classmethod
    def spawn(cls, new_pos : pygame.Vector2, health : int, speed : int = 3):
        element = cls.inactive_elements[0]

        element.image = cls.test_image
        #element.mask = pygame.mask.from_surface(element.image)
        element.rect = element.image.get_rect()

        element.position = new_pos
        element.align_rect()
        element.zindex = 10

        element.pivot = Pivot2D(element._position, element.image, (0, 0, 255))


        element.max_hp = health
        element.hp = health
        element.speed = speed

        cls.unpool(element)
        return element
    
    def update(self, delta: float):
        player_direction : pygame.Vector2 = (core_object.game.player.position - self.position).normalize()
        self.position += player_direction * self.speed * delta
        self.do_collisions()
    
    def do_collisions(self):
        bullets : list[BaseProjectile] = self.get_all_colliding([BaseProjectile.active_elements])
        for bullet in bullets:
            if not isinstance(bullet, BaseProjectile): continue
            if not bullet.is_hostile(bullet.TEAMS.enemy): continue
            bullet.kill_instance()
            alive : bool = self.take_damage(1)
            if not alive: return
    
    def take_damage(self, damage : int) -> bool:
        self.hp -= damage
        if self.hp <= 0:
            self.die()
            return False
        return True
    
    def die(self):
        self.kill_instance()
        

    def clean_instance(self):
        self.image = None
        #self.mask = None
        self.rect = None
        self.pivot = None
        self._position = pygame.Vector2(0,0)
        self.zindex = None

        self.speed = None
        self.max_hp = None
        self.hp = None

Sprite.register_class(Zombie)

class ZombieTypes:
    zombie_dict = {'normal' : Zombie}
    normal = 'normal'

    @staticmethod
    def convert(ztype : str):
        return ZombieTypes.zombie_dict[ztype]