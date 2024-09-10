import pygame
from game.sprite import Sprite
from core.core import core_object

from utils.animation import Animation
from utils.pivot_2d import Pivot2D

from game.projectiles import BaseProjectile
from game.enemy import Zombie
from utils.ui.ui_sprite import UiSprite
from utils.my_timer import Timer

class Player(Sprite):
    active_elements : list['Player'] = []
    inactive_elements : list['Player'] = []
    offset = 0
    test_image : pygame.Surface = pygame.surface.Surface((50, 50))
    test_image.set_colorkey([0, 0, 255])
    test_image.fill([0, 0, 255])
    pygame.draw.circle(test_image, "Green", (25, 25), 25)

    ui_heart_image : pygame.Surface = pygame.image.load("assets/graphics/ui/heart_green_colorkey.png")
    ui_heart_image.set_colorkey([0, 255, 0])
    ui_heart_image = pygame.transform.scale_by(ui_heart_image, 0.1)

    def __init__(self) -> None:
        super().__init__()
        self.max_hp : int
        self.hp : int
        self.ui_hearts : list[UiSprite] = []

        self.shot_cooldown : Timer|None
        self.dynamic_mask = True
        Player.inactive_elements.append(self)

    @classmethod
    def spawn(cls, new_pos : pygame.Vector2):
        element = cls.inactive_elements[0]
        cls.unpool(element)

        element.image = cls.test_image
        element.rect = element.image.get_rect()

        element.position = new_pos
        element.align_rect()
        element.zindex = 50

        element.pivot = Pivot2D(element._position, element.image, (0, 0, 255))

        element.hp = 3
        element.max_hp = 3
        element.update_ui_hearts()

        element.shot_cooldown = Timer(0.35, core_object.game.game_timer.get_time)
        
        return element
    
    def update(self, delta: float):
        self.input_action()
        self.do_movement(delta)
        self.do_collisions()
    
    def input_action(self):
        if (pygame.key.get_pressed())[pygame.K_SPACE]:
            self.shoot()
    
    def do_movement(self, delta : float):
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
    
    def do_collisions(self):
        enemies : list[Zombie] = self.get_all_colliding(Zombie)
        for enemy in enemies:
            if not isinstance(enemy, Zombie): continue
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
        self.update_ui_hearts()
    
    def shoot(self):
        if not self.shot_cooldown.isover(): return
        player_to_mouse_vector = pygame.Vector2(pygame.mouse.get_pos()) - self.position
        shot_direction = player_to_mouse_vector.normalize()
        BaseProjectile.spawn(self.position, 7, shot_direction, BaseProjectile.TEAMS.friendly)
        self.shot_cooldown.restart()
    
    def new_ui_heart(self, index : int):
        x_pos = 950 - index * 60
        new_sprite = UiSprite(Player.ui_heart_image, Player.ui_heart_image.get_rect(), 0, f'heart{index}', colorkey=[0, 255, 0])
        new_sprite.rect.top = 15
        new_sprite.rect.right = x_pos
        return new_sprite
    
    def update_ui_hearts(self):
        self.clear_ui_hearts()
        if self.hp > 0:
            self.ui_hearts = [self.new_ui_heart(i) for i in range(self.hp)]
            for heart in self.ui_hearts: core_object.main_ui.add(heart)
    
    def clear_ui_hearts(self):
        for ui_sprite in self.ui_hearts:
            core_object.main_ui.remove(ui_sprite)
        self.ui_hearts.clear()

    
    def handle_key_event(self, event : pygame.Event):
        if event.type != pygame.KEYDOWN: return
        if core_object.game.state == core_object.game.STATES.paused: return
        if core_object.game.state == core_object.game.STATES.transition: return
        if event.key == pygame.K_SPACE:
            self.shoot()
    
    def handle_mouse_event(self, event : pygame.Event):
        if event.type != pygame.MOUSEBUTTONDOWN: return
        if core_object.game.state == core_object.game.STATES.paused: return
        if core_object.game.state == core_object.game.STATES.transition: return
        if event.button == 1:
            self.shoot()

    @classmethod
    def receive_key_event(cls, event : pygame.Event):
        for element in cls.active_elements:
            element.handle_key_event(event)
    
    @classmethod
    def receive_mouse_event(cls, event : pygame.Event):
        for element in cls.active_elements:
            element.handle_mouse_event(event)
    
    def clean_instance(self):
        self.image = None
        self.rect = None
        self.pivot = None
        self._position = pygame.Vector2(0,0)
        self.zindex = None

        self.hp = None
        self.max_hp = None
        self.clear_ui_hearts()
        self.shot_cooldown = None
    

Sprite.register_class(Player)

def make_connections():
    core_object.event_manager.bind(pygame.KEYDOWN, Player.receive_key_event)
    core_object.event_manager.bind(pygame.MOUSEBUTTONDOWN, Player.receive_mouse_event)

def remove_connections():
    core_object.event_manager.unbind(pygame.KEYDOWN, Player.receive_key_event)
    core_object.event_manager.unbind(pygame.MOUSEBUTTONDOWN, Player.receive_mouse_event)