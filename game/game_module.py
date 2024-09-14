import pygame
from dataclasses import dataclass
from typing import Any
from math import floor
from random import shuffle, choice, choices
import random
from utils.ui.textsprite import TextSprite
import utils.interpolation as interpolation
import utils.tween_module as TweenModule
from utils.my_timer import Timer
from game.sprite import Sprite
from utils.helpers import average, random_float, Union, Task, make_right_arrow
from utils.ui.ui_sprite import UiSprite
from utils.ui.brightness_overlay import BrightnessOverlay
from utils.animation import Animation, AnimationTrack

class GameStates:
    def __init__(self) -> None:
        self.transition = 'Transition'
        self.normal = 'Normal'
        self.paused = 'Paused'

class BreakObjectives:
    right_edge = 'RightWall'

@dataclass
class WaveInfo:
    spawn_delay : float
    zombie_count : dict[str, int]

    zombie_per_heat : int = 1

    def copy(self):
        return WaveInfo(self.spawn_delay, self.zombie_count.copy(), self.zombie_per_heat)
    
    def is_zombie_remaining(self) -> bool:
        for zombie_count in self.zombie_count.values():
            if zombie_count != 0: return True
        return False

    

class Game:
    font_40 = pygame.Font('assets/fonts/Pixeltype.ttf', 40)
    font_50 = pygame.Font('assets/fonts/Pixeltype.ttf', 50)
    font_60 = pygame.Font('assets/fonts/Pixeltype.ttf', 60)
    font_70 = pygame.Font('assets/fonts/Pixeltype.ttf', 70)
    
    def __init__(self) -> None:
        self.STATES : GameStates = GameStates()

        self.active : bool = False
        self.state : None|str = None
        self.prev_state : None|str = None
        self.game_timer : Timer|None = None
        self.game_data : dict|None = {}

        self.player : Union['Player', None] = None
        self.background : Union['Background', None] = None
        self.enemies : list['BaseZombie']|None = None

        self.enemy_timer : Timer|None = None
        self.diff_table : dict[int, WaveInfo] = {
            1 : WaveInfo(1.5, {'normal' : 10}, 1),
            2 : WaveInfo(1.35, {'normal' : 8, 'quick' : 1, 'tank' : 1}, 1),
            3 : WaveInfo(1.2, {'normal' : 5, 'quick' : 3, 'tank' : 2}, 1),
            4 : WaveInfo(1.1, {'normal' : 8, 'quick' : 4, 'tank' : 3}, 1),
            5 : WaveInfo(1, {'normal' : 10, 'quick' : 5, 'tank' : 5}, 1),
            6 : WaveInfo(0.9, {'normal' : 8, 'quick' : 6, 'tank' : 6}, 1),
            7 : WaveInfo(0.8, {'normal' : 5, 'quick' : 8, 'tank' : 7}, 1),
            8 : WaveInfo(0.7, {'normal' : 5, 'quick' : 10, 'tank' : 10}, 1),
            9 : WaveInfo(0.6, {'normal' : 10, 'quick' : 10, 'tank' : 10}, 1),
            10 : WaveInfo(0.5, {'normal' : 10, 'quick' : 15, 'tank' : 12}, 1),
            11 : WaveInfo(0.5, {'normal' : 90000}, 5),
        }
        self.current_wave : WaveInfo|None = None
        self.current_wave_num : int|None = None
        self.break_timer : Timer|None = None
        self.break_alerted : bool = False
        self.break_objective : str|None = None

        self.score : int|None = None
        self.wave_count : int|None = None
        self.current_area : int|None = None

    def is_nm_state(self):
        return (self.state == self.STATES.normal)

    def start_game(self):
        self.active = True
        self.state = self.STATES.normal
        self.prev_state = None
        self.game_timer = Timer(-1)
        self.game_data = {}
        self.make_connections()

        self.current_wave = self.diff_table[1].copy()
        self.current_wave_num = 1
        self.wave_count = 1
        self.current_area = 0
        self.score = 0
        self.enemy_timer = Timer(self.current_wave.spawn_delay, time_source=self.game_timer.get_time)
        self.break_timer = Timer(-1, time_source=self.game_timer.get_time)
        self.break_alerted = False
        self.break_objective = None

        self.player = Player.spawn(pygame.Vector2(random.randint(0, 960),random.randint(0, 540)))
        self.background = Background.spawn(0)
        self.enemies = BaseZombie.active_elements
        self.show_wave(1)
    
    def empty_wave(self, event : pygame.Event|None = None):
        if self.current_wave:
            for k in self.current_wave.zombie_count:
                self.current_wave.zombie_count[k] = 0

        

    def make_connections(self):
        core_object.event_manager.bind(pygame.KEYDOWN, self.handle_key_event)
        
        game.player.make_connections()

    def remove_connections(self):
        core_object.event_manager.unbind(pygame.KEYDOWN, self.handle_key_event)

        game.player.remove_connections()

    def handle_key_event(self, event : pygame.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                if self.state == self.STATES.paused:
                    self.unpause()
                elif self.state == self.STATES.normal:
                    self.pause()
            elif event.key == pygame.K_LCTRL:
                if core_object.IS_DEBUG: self.empty_wave(event)

    def next_wave(self):
        self.current_wave_num += 1
        self.wave_count = self.current_wave_num
        self.current_wave = self.diff_table[self.current_wave_num].copy()
        self.enemy_timer.set_duration(self.current_wave.spawn_delay)
        self.break_timer.set_duration(-1)
        self.break_objective = None
        self.break_alerted = False
        self.show_wave(self.current_wave_num)
    
    def stop_waves(self, objective : str|None = None):
        self.current_wave = None
        self.enemy_timer.set_duration(-1)
        self.break_timer.set_duration(10)
        self.break_objective = objective

    def main_logic(self, delta : float):
        if self.state == self.STATES.transition:
            return
        if not self.player.is_alive():
            if self.state != self.STATES.transition: self.do_gameover()
            return
        if self.current_wave:
            self.active_logic()
        else:
            self.break_logic()
    
    def active_logic(self):
        if self.enemy_timer.isover():
            self.enemy_timer.restart()
            for _ in range(self.current_wave.zombie_per_heat):
                if not self.is_zombie_remaining():
                    break
                zombie_type = self.get_random_zombie_type()
                if self.current_wave.zombie_count[zombie_type] > 0: self.current_wave.zombie_count[zombie_type] -= 1
                self.spawn_enemy(zombie_type)
                if not self.is_zombie_remaining():
                    break
        if not self.is_zombie_remaining():
            self.next_wave_logic()
    
    def break_logic(self):
        if len(BaseZombie.active_elements): 
            self.break_timer.restart()
            return
        if not self.break_alerted: 
            self.alert_player("Next Area!")
            self.break_alerted = True
        if self.break_objective == BreakObjectives.right_edge:
            if self.player.rect.right >= 959:
                self.current_area += 1
                self.start_area_transition(self.current_area)
        elif self.break_timer.isover():
            self.next_wave()
    
    def next_wave_logic(self):
        #print(Zombie.active_elements)
        if not self.current_wave:
            self.next_wave()
        elif self.current_wave_num in [5, 10]:
            if BaseZombie.active_elements: return
            self.stop_waves(objective=BreakObjectives.right_edge)
            arrow_image = make_right_arrow(100, 30, 'Red')
            ui_sprite = UiSprite(arrow_image, arrow_image.get_rect(midright = (955, 270)), 0, 'next_area_arrow')
            core_object.main_ui.add(ui_sprite)
        else:
            self.next_wave()
    
    def transition_to_break(self, break_duration : float, break_objective : str|None = None):
        self.break_timer.set_duration(break_duration)
        self.break_objective = break_objective
        self.state = self.STATES.normal
    
    def get_random_zombie_type(self) -> str:
        if not self.current_wave: return None
        if not self.is_zombie_remaining(): return 'normal'
        zombies_left = self.current_wave.zombie_count
        return choices(list(zombies_left.keys()), list(zombies_left.values()))[0]
    
    def is_zombie_remaining(self) -> bool:
        if not self.current_wave: return False
        return self.current_wave.is_zombie_remaining()


    def spawn_enemy(self, ztype : str):
        spawn_pos : pygame.Vector2
        buffer : int = 60
        if random.randint(0,1):
            spawn_pos = pygame.Vector2((-buffer, 960 + buffer)[random.randint(0,1)], random.randint(-buffer, 540 + buffer))
        else:
            spawn_pos = pygame.Vector2(random.randint(-buffer, 960 + buffer), (-buffer, 540 + buffer)[random.randint(0,1)])

        match ztype:
            case ZombieTypes.normal:
                NormalZombie.spawn(spawn_pos, health=9, speed=3)
            
            case ZombieTypes.quick:
                QuickZombie.spawn(spawn_pos, health=6, speed=5)
            
            case ZombieTypes.tank:
                TankZombie.spawn(spawn_pos, health=20, speed=2)

    
    def show_wave(self, wave_num : int):
        self.alert_player(f'Wave {wave_num}')
    
    def alert_player(self, text : str):
        wave_sprite = TextSprite(pygame.Vector2(core_object.main_display.get_width() // 2, 90), 'midtop', 0, text, 
                        text_settings=(core_object.menu.font_60, 'White', False), text_stroke_settings=('Black', 2), colorkey=(0,255,0))
        
        wave_sprite.rect.bottom = -5
        wave_sprite.position = pygame.Vector2(wave_sprite.rect.center)
        temp_y = wave_sprite.rect.centery
        core_object.main_ui.add_temp(wave_sprite, 5, time_source=self.game_timer.get_time)
        TInfo = TweenModule.TweenInfo
        goal1 = {'rect.centery' : 50, 'position.y' : 50}
        info1 = TInfo(interpolation.quad_ease_out, 0.5)
        goal2 = {'rect.centery' : temp_y, 'position.y' : temp_y}
        info2 = TInfo(interpolation.quad_ease_in, 0.8)
        
        on_screen_time = 2
        info_wait = TInfo(lambda t : t, on_screen_time)
        goal_wait = {}

        chain = TweenModule.TweenChain(wave_sprite, [(info1, goal1), (info_wait, goal_wait), (info2, goal2)], True, self.game_timer.get_time)
        chain.register()
        chain.play()
    
    def start_area_transition(self, new_area : int = 1):
        core_object.main_ui.remove(core_object.main_ui.get_sprite('next_area_arrow'))
        self.state = self.STATES.transition
        self.break_objective = None
        self.current_area = new_area
        track : AnimationTrack = self.player.screen_transition.load(self.player, self.game_timer.get_time)
        fade_time : tuple[float, float] = (2, 0.6)
        anim_time : float = track.data[0].time
        callback = Task(self.fade_in_then_out, fade_time[0], fade_time[1])
        track.play(callback=callback)
        core_object.task_scheduler.schedule_task((fade_time[0] / 2 + anim_time + 0.01, self.game_timer.get_time, 1), setattr, self.player, 'position', pygame.Vector2(480, 270))
        core_object.task_scheduler.schedule_task((fade_time[0] / 2 + anim_time + 0.01, self.game_timer.get_time, 1), self.background.switch_area, self.current_area)
        core_object.task_scheduler.schedule_task((fade_time[0] + fade_time[1] + anim_time + 0.01, self.game_timer.get_time, 1), self.transition_to_break, 1)

    def fade_in_then_out(self, time : float = 2, wait_time : float = 0.01):
        overlay : BrightnessOverlay = BrightnessOverlay(0, pygame.Rect(0,0, *core_object.main_display.get_size()), 0, 'fade_in_overlay', zindex=100)
        overlay.brightness = 0
        TInfo = TweenModule.TweenInfo
        goal1 = {'brightness' : -255}
        info1 = TInfo(interpolation.linear, time / 2)
        goal2 = {'brightness' : 0}
        info2 = TInfo(interpolation.linear, time / 2)
        info_wait = TInfo(lambda t : t, wait_time)
        goal_wait = {}
        chain = TweenModule.TweenChain(overlay, [(info1, goal1), (info_wait, goal_wait), (info2, goal2)], True, self.game_timer.get_time)
        chain.register()
        chain.play()
        core_object.main_ui.add_temp(overlay, time + wait_time + 0.01, True, self.game_timer.get_time)
        
    
    def pause(self):
        if not self.active: return
        if self.state == self.STATES.paused: return 
        if self.state == self.STATES.transition: return
        self.game_timer.pause()
        window_size = core_object.main_display.get_size()
        pause_ui1 = BrightnessOverlay(-60, pygame.Rect(0,0, *window_size), 0, 'pause_overlay', zindex=999)
        pause_ui2 = TextSprite(pygame.Vector2(window_size[0] // 2, window_size[1] // 2), 'center', 0, 'Paused', 'pause_text', None, None, 1000,
                               (self.font_70, 'White', False), ('Black', 2), colorkey=(0, 255, 0))
        core_object.main_ui.add(pause_ui1)
        core_object.main_ui.add(pause_ui2)
        self.prev_state = self.state
        self.state = self.STATES.paused
    
    def unpause(self):
        if not self.active: return
        if self.state != self.STATES.paused: return
        if self.state == self.STATES.transition: return
        self.game_timer.unpause()
        pause_ui1 = core_object.main_ui.get_sprite('pause_overlay')
        pause_ui2 = core_object.main_ui.get_sprite('pause_text')
        if pause_ui1: core_object.main_ui.remove(pause_ui1)
        if pause_ui2: core_object.main_ui.remove(pause_ui2)
        self.state = self.prev_state
        self.prev_state = None
    
    
    def fire_gameover_event(self):
        new_event = pygame.event.Event(core_object.END_GAME, {})
        pygame.event.post(new_event)
    
    def do_gameover(self):
        track : AnimationTrack = Player.death_anim.load(self.player, self.game_timer.get_time)
        track.play(False, callback=Task(self.fire_gameover_event))
        self.state = self.STATES.transition
    
    def end_game(self):
        BaseZombie.class_cleanup()
        self.remove_connections()
        self.cleanup()

    def cleanup(self):
        #Cleanup basic variables
        self.active = False
        self.state = None
        self.prev_state = None
        self.game_timer = None
        self.game_data.clear()

        

        #Cleanup ingame object
        Sprite.kill_all_sprites()

        #Clear game varaibles
        self.player = None
        self.enemies = None

        self.current_wave_num = None
        self.current_wave = None
        self.break_timer = None
        self.break_alerted = False
        self.break_objective = None

        self.score = None
        self.wave_count = None
        self.current_area = None

   
    def init(self):
        global core_object
        from core.core import core_object

        #runtime imports for game classes
        global game

        global TestPlayer      
        import game.test_player
        from game.test_player import TestPlayer

        global Player
        import game.player
        from game.player import Player

        global BaseZombie, NormalZombie, ZombieTypes, QuickZombie, TankZombie
        import game.enemy
        from game.enemy import BaseZombie, NormalZombie, ZombieTypes, QuickZombie, TankZombie

        global BaseProjectile
        import game.projectiles
        from game.projectiles import BaseProjectile

        global Background
        import game.background
        from game.background import Background

        
    
