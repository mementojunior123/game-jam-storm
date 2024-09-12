import pygame
from game.sprite import Sprite
from core.core import core_object

from utils.animation import Animation
from utils.pivot_2d import Pivot2D

from game.projectiles import BaseProjectile
from game.enemy import Zombie
from utils.helpers import make_upgrade_bar, reset_upgrade_bar
from utils.ui.ui_sprite import UiSprite
from utils.my_timer import Timer
from dataclasses import dataclass
from game.weapons import FiringModes, WeaponStats, WeaponBuff, WeaponBuffTypes, WEAPONS


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

    death_anim : Animation = Animation.get_animation("player_death")

    def __init__(self) -> None:
        super().__init__()
        self.max_hp : int
        self.hp : int

        self.main_heart : UiSprite|None = None
        self.ui_healthbar : UiSprite|None = None

        self.shot_cooldown : Timer|None
        self.weapon : WeaponStats

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

        element.max_hp = 5 * (1 + core_object.storage.vitality_level * 0.2)
        element.hp = element.max_hp
        

        element.weapon = WEAPONS['normal']
        element.weapon.reset()
        element.weapon.apply_perma_buff(WeaponBuff(WeaponBuffTypes.firerate_mult, 0.2 * core_object.storage.firerate_level))
        element.weapon.apply_perma_buff(WeaponBuff(WeaponBuffTypes.dmg_mult, 0.2 * core_object.storage.damage_level))
        element.shot_cooldown = Timer(element.weapon.firerate, core_object.game.game_timer.get_time)

        bar_image = make_upgrade_bar(150, 25, 1)
        element.ui_healthbar = UiSprite(bar_image, bar_image.get_rect(topright = (950, 20)), 0, 'healthbar')
        core_object.main_ui.add(element.ui_healthbar)
        element.update_healthbar()
        element.main_heart = UiSprite(Player.ui_heart_image, Player.ui_heart_image.get_rect(topright = (793, 15)), 
                                      0, f'heart', colorkey=[0, 255, 0], zindex=1)
        #core_object.main_ui.add(element.main_heart)
        return element
    
    def update(self, delta: float):
        if not core_object.game.is_nm_state(): return
        self.input_action()
        self.do_movement(delta)
        self.do_collisions()
    
    def input_action(self):
        if (pygame.key.get_pressed())[pygame.K_SPACE] and (self.weapon.fire_mode == FiringModes.auto):
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
        self.update_healthbar()
    
    def shoot(self):
        if not self.shot_cooldown.isover(): return
        player_to_mouse_vector = pygame.Vector2(pygame.mouse.get_pos()) - self.position
        shot_direction = player_to_mouse_vector.normalize()
        BaseProjectile.spawn(self.position, 7, shot_direction, BaseProjectile.TEAMS.friendly, self.weapon.damage)
        self.shot_cooldown.set_duration(self.weapon.firerate)
    
    def update_healthbar(self):
        hp_percent : float = self.hp / self.max_hp
        colors = {'Dark Green' : 0.8, 'Green' : 0.6, 'Yellow' : 0.4, 'Orange' : 0.2, 'Red' : -1}
        for color, value in colors.items():
            if hp_percent > value:
                break
        reset_upgrade_bar(self.ui_healthbar.surf, 1, 150, 25)
        pygame.draw.rect(self.ui_healthbar.surf, color, (3, 3, pygame.math.lerp(0, 150, hp_percent), 25))

    
    def handle_key_event(self, event : pygame.Event):
        if event.type != pygame.KEYDOWN: return
        if not core_object.game.is_nm_state(): return
        if event.key == pygame.K_SPACE:
            self.shoot()
    
    def handle_mouse_event(self, event : pygame.Event):
        if event.type != pygame.MOUSEBUTTONDOWN: return
        if not core_object.game.is_nm_state(): return
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
        self.shot_cooldown = None
        self.weapon = None

        self.main_heart = None
        self.ui_healthbar = None
    

Sprite.register_class(Player)

def make_connections():
    core_object.event_manager.bind(pygame.KEYDOWN, Player.receive_key_event)
    core_object.event_manager.bind(pygame.MOUSEBUTTONDOWN, Player.receive_mouse_event)

def remove_connections():
    core_object.event_manager.unbind(pygame.KEYDOWN, Player.receive_key_event)
    core_object.event_manager.unbind(pygame.MOUSEBUTTONDOWN, Player.receive_mouse_event)