import pygame
from game.sprite import Sprite
from core.core import core_object

from utils.animation import Animation
from utils.pivot_2d import Pivot2D

from game.bullet import Bullet
from game.enemy import Enemy

class Player(Sprite):
    active_elements : list['Player'] = []
    inactive_elements : list['Player'] = []
    offset = 0
    test_image : pygame.Surface = pygame.surface.Surface((50, 50))
    test_image.set_colorkey([0, 0, 255])
    test_image.fill([0, 0, 255])
    pygame.draw.circle(test_image, "Green", (25, 25), 25)

    def __init__(self) -> None:
        super().__init__()
        self.max_hp : int
        self.hp : int
        self.dynamic_mask = True
        Player.inactive_elements.append(self)

    @classmethod
    def spawn(cls, new_pos : pygame.Vector2):
        element = cls.inactive_elements[0]

        element.image = cls.test_image
        element.rect = element.image.get_rect()

        element.position = new_pos
        element.align_rect()
        element.zindex = 50

        element.pivot = Pivot2D(element._position, element.image, (0, 0, 255))

        element.hp = 3
        element.max_hp = 3

        cls.unpool(element)
        return element
    
    def update(self, delta: float):
        keyboard_map = pygame.key.get_pressed()
        move_vector : pygame.Vector2 = pygame.Vector2(0,0)
        speed : int = 7
        if keyboard_map[pygame.K_a]:
            move_vector += pygame.Vector2(-1, 0)
        if keyboard_map[pygame.K_d]:
            move_vector += pygame.Vector2(1, 0)
        if keyboard_map[pygame.K_s]:
            move_vector += pygame.Vector2(0, 1)
        if keyboard_map[pygame.K_w]:
            move_vector += pygame.Vector2(0, -1)
        if move_vector.magnitude() != 0: move_vector.normalize_ip()
        self.position += move_vector * speed * delta
        self.clamp_rect(pygame.Rect(0,0, *core_object.main_display.get_size()))
        self.do_collisions()
    
    def do_collisions(self):
        enemies : list[Enemy] = self.get_all_colliding(Enemy)
        for enemy in enemies:
            if not isinstance(enemy, Enemy): continue
            enemy.kill_instance_safe()
            self.take_damage(1)

    
    def is_alive(self) -> bool:
        return (self.hp > 0)
    
    def can_take_damage(self):
        return True

    def take_damage(self, damage : int):
        if not self.can_take_damage(): return
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
    
    def shoot(self):
        player_to_mouse_vector = pygame.Vector2(pygame.mouse.get_pos()) - self.position
        shot_direction = player_to_mouse_vector.normalize()
        Bullet.spawn(self.position, 7, shot_direction)
    
    def handle_key_event(self, event : pygame.Event):
        if event.key == pygame.K_SPACE:
            self.shoot()

    @classmethod
    def receive_key_event(cls, event : pygame.Event):
        for element in cls.active_elements:
            element.handle_key_event(event)
    
    def clean_instance(self):
        self.image = None
        self.rect = None
        self.pivot = None
        self._position = pygame.Vector2(0,0)
        self.zindex = None

        self.hp = None
        self.max_hp = None
    

Sprite.register_class(Player)

def make_connections():
    core_object.event_manager.bind(pygame.KEYDOWN, Player.receive_key_event)

def remove_connections():
    core_object.event_manager.unbind(pygame.KEYDOWN, Player.receive_key_event)