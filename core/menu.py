import pygame
from utils.helpers import ColorType, scale_surf, to_roman, Callable
import random
from utils.ui.ui_sprite import UiSprite
from utils.ui.textsprite import TextSprite
from utils.ui.base_ui_elements import BaseUiElements
import utils.tween_module as TweenModule
import utils.interpolation as interpolation
from utils.my_timer import Timer
from utils.ui.brightness_overlay import BrightnessOverlay
from math import floor

class BaseMenu:
    font_40 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 40)
    font_50 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 50)
    font_60 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 60)
    font_70 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 70)
    font_150 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 150)

    def __init__(self) -> None:
        self.stage : int
        self.stages : list[list[UiSprite]]
        self.bg_color : ColorType|str
        self.temp : dict[UiSprite, Timer] = {}
        
    def init(self):
        self.bg_color = (94, 129, 162)
        self.stage = 1
        self.stage_data : list[dict] = [None, {}]
        self.stages = [None, []]
    
    def add_temp(self, element : UiSprite, time : float|Timer, override = False, time_source : Callable[[], float]|None = None, time_scale : float = 1):
        if element not in self.temp or override == True:
            timer = time if type(time) == Timer else Timer(time, time_source, time_scale)
            self.temp[element] = timer
    def alert_player(self, text : str):
        text_sprite = TextSprite(pygame.Vector2(core_object.main_display.get_width() // 2, 90), 'midtop', 0, text, 
                        text_settings=(core_object.menu.font_60, 'White', False), text_stroke_settings=('Black', 2), colorkey=(0,255,0))
        
        text_sprite.rect.bottom = -5
        text_sprite.position = pygame.Vector2(text_sprite.rect.center)
        temp_y = text_sprite.rect.centery
        self.add_temp(text_sprite, 5)
        TInfo = TweenModule.TweenInfo
        goal1 = {'rect.centery' : 50, 'position.y' : 50}
        info1 = TInfo(interpolation.quad_ease_out, 0.5)
        goal2 = {'rect.centery' : temp_y, 'position.y' : temp_y}
        info2 = TInfo(interpolation.quad_ease_in, 0.8)
        
        on_screen_time = 2
        info_wait = TInfo(lambda t : t, on_screen_time)
        goal_wait = {}

        chain = TweenModule.TweenChain(text_sprite, [(info1, goal1), (info_wait, goal_wait), (info2, goal2)], True)
        chain.register()
        chain.play()

    def add_connections(self):
        core_object.event_manager.bind(pygame.MOUSEBUTTONDOWN, self.handle_mouse_event)
        core_object.event_manager.bind(UiSprite.TAG_EVENT, self.handle_tag_event)
    
    def remove_connections(self):
        core_object.event_manager.unbind(pygame.MOUSEBUTTONDOWN, self.handle_mouse_event)
        core_object.event_manager.unbind(UiSprite.TAG_EVENT, self.handle_tag_event)
    
    def __get_core_object(self):
        global core_object
        from core.core import core_object

    def render(self, display : pygame.Surface):
        sprite_list = [sprite for sprite in (self.stages[self.stage] + list(self.temp.keys())) if sprite.visible == True]
        sprite_list.sort(key = lambda sprite : sprite.zindex)
        for sprite in sprite_list:
            sprite.draw(display)
        
    
    def update(self, delta : float):
        to_del = []
        for item in self.temp:
            if self.temp[item].isover(): to_del.append(item)
        for item in to_del:
            self.temp.pop(item)

        stage_data = self.stage_data[self.stage]
        match self.stage:
            case 1:
                pass
    
    def prepare_entry(self, stage : int = 1):
        self.add_connections()
        self.stage = stage
    
    def prepare_exit(self):
        self.stage = 0
        self.remove_connections()
        self.temp.clear()
    
    def goto_stage(self, new_stage : int):
        self.stage = new_stage

    def launch_game(self):
        new_event = pygame.event.Event(core_object.START_GAME, {})
        pygame.event.post(new_event)

    def get_sprite(self, stage, tag):
        """Returns the 1st sprite with a corresponding tag.
        None is returned if it was not found in the stage."""
        if tag is None or stage is None: return None

        the_list = self.stages[stage]
        for sprite in the_list:
            if sprite.tag == tag:
                return sprite
        return None
    
    def get_sprite_by_name(self, stage, name):
        """Returns the 1st sprite with a corresponding name.
        None is returned if it was not found in the stage."""
        if name is None or stage is None: return None

        the_list = self.stages[stage]
        sprite : UiSprite
        for sprite in the_list:
            if sprite.name == name:
                return sprite
        return None

    def get_sprite_index(self, stage, name = None, tag = None):
        '''Returns the index of the 1st occurence of sprite with a corresponding name or tag.
        None is returned if the sprite is not found'''
        if name is None and tag is None: return None
        the_list = self.stages[stage]
        sprite : UiSprite
        for i, sprite in enumerate(the_list):
            if sprite.name == name and name is not None:
                return i
            if sprite.tag == tag and tag is not None:
                return i
        return None
    
    def find_and_replace(self, new_sprite : UiSprite, stage : int, name : str|None = None, tag : int|None = None, sprite : UiSprite|None = None) -> bool:
        found : bool = False
        for index, sprite in enumerate(self.stages[stage]):
            if sprite == new_sprite and sprite is not None:
                found = True
                break
            if sprite.tag == tag and tag is not None:
                found = True
                break
            if sprite.name == name and name is not None:
                found = True
                break
        
        if found:
            self.stages[stage][index] = new_sprite
        return found
    
    def handle_tag_event(self, event : pygame.Event):
        if event.type != UiSprite.TAG_EVENT:
            return
        tag : int = event.tag
        name : str = event.name
        trigger_type : str = event.trigger_type
        stage_data = self.stage_data[self.stage]
        match self.stage:
            case 1:
                pass
                   
    
    def handle_mouse_event(self, event : pygame.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos : tuple = event.pos
            sprite : UiSprite
            for sprite in self.stages[self.stage]:
                if type(sprite) != UiSprite: continue
                if sprite.rect.collidepoint(mouse_pos):
                    sprite.on_click()

def make_upgrade_bar(width : int = 100, length : int = 20, count = 5, border : int = 3, border_color : str|ColorType = 'Black', 
                     bg_color : str|ColorType = (90, 90, 90)):
    surf = pygame.surface.Surface((width + border * 2, (length + border) * count + border))
    surf.fill(border_color)
    pygame.draw.rect(surf, bg_color, (border, border, width, (length + border) * count - border))
    for i in range(count):
        pygame.draw.rect(surf, border_color, (0, (border + length) * i, width + border * 2, border))
    return surf

def paint_upgrade_bar(surf : pygame.Surface, index : int, width : int = 100, length : int = 20, border : int = 3, color : str|ColorType = 'Green'):
    pygame.draw.rect(surf, color, (border, (length + border) * index + border, width, length))

def reset_upgrade_bar(surf : pygame.Surface, count : int = 5, width : int = 100, length : int = 20, border : int = 3, bg_color : str|ColorType = (90, 90, 90)):
    for index in range(count):
        pygame.draw.rect(surf, bg_color, (border, (length + border) * index + border, width, length))

class Menu(BaseMenu):     
    def init(self):
        self.bg_color = (94, 129, 162)
        self.stage = 1
        self.stage_data : list[dict] = [None, {}, {}]
        window_size = core_object.main_display.get_size()
        centerx = window_size[0] // 2
        upgrade_bar_surf1 = make_upgrade_bar()
        self.stages = [None, 
        [BaseUiElements.new_text_sprite('StormZ Day', (Menu.font_60, 'Black', False), 0, 'midtop', (centerx, 50)),
        BaseUiElements.new_button('BlueButton', 'Play', 1, 'midbottom', (centerx, window_size[1] - 15), (0.5, 1.4), 
        {'name' : 'play_button'}, (Menu.font_40, 'Black', False))], #stage 1
        [BaseUiElements.new_text_sprite('Upgrades', (Menu.font_60, 'Black', False), 0, 'midtop', (centerx, 50)),
        BaseUiElements.new_button('BlueButton', 'Ready', 1, 'bottomright', (945, window_size[1] - 15), (0.5, 1.4), 
        {'name' : 'ready_button'}, (Menu.font_40, 'Black', False)),
        TextSprite(pygame.Vector2(115, 155), 'midtop', 0, 'Firerate I\nCost : 2', 'firerate_upg_title', {}, {}, 0, (Menu.font_50, 'Black', False), colorkey=[0, 255, 0]),
        UiSprite(upgrade_bar_surf1, upgrade_bar_surf1.get_rect(midtop = (115, 250)), 0, 'firerate_upg_bar'),
        BaseUiElements.new_button('BlueButton', 'Buy', 1, 'midtop', (115, 375), (0.35, 1), 
        {'name' : 'buy_firerate'}, (Menu.font_40, 'Black', False)),

        ]
        ]
    
    def enter_stage2(self):
        self.stage = 2
        self.update_firerate_level_stage2()
    
    def update_firerate_level_stage2(self):
        firerate_upg_bar = self.get_sprite_by_name(2, 'firerate_upg_bar')
        reset_upgrade_bar(firerate_upg_bar.surf)
        for i in range(core_object.storage.firerate_level):
            paint_upgrade_bar(firerate_upg_bar.surf, i)
            if i >= 4: break
        firerate_upg_title : TextSprite = self.get_sprite_by_name(2, 'firerate_upg_title')
        firerate_level : int = core_object.storage.firerate_level
        if core_object.storage.firerate_level >= 5:
            new_button = BaseUiElements.new_button('BlueButton', 'MAXED', 1, 'midtop', (115, 375), (0.35, 1), 
                                                   {'name' : 'buy_firerate'}, (Menu.font_40, 'Black', False))
            self.find_and_replace(new_button, 2, name='buy_firerate')
            firerate_upg_title.text = f'Firerate {'MAXED'}\nCost : MAXED'
        else:
            new_button = BaseUiElements.new_button('BlueButton', 'Buy', 1, 'midtop', (115, 375), (0.35, 1), 
                                                   {'name' : 'buy_firerate'}, (Menu.font_40, 'Black', False))
            self.find_and_replace(new_button, 2, name='buy_firerate')
            firerate_upg_title.text = f'Firerate {to_roman(firerate_level + 1)}\nCost : {core_object.storage.COST_TABLE['Firerate'][firerate_level]}'


    def exit_stage2(self):
        pass
    
    def update(self, delta : float):
        stage_data = self.stage_data[self.stage]
        match self.stage:
            case _: pass
    
    def handle_tag_event(self, event : pygame.Event):
        if event.type != UiSprite.TAG_EVENT:
            return
        tag : int = event.tag
        name : str = event.name
        trigger_type : str = event.trigger_type
        stage_data = self.stage_data[self.stage]
        match self.stage:
            case 1:
                if name == "play_button":
                    self.enter_stage2()
            case 2:
                if name == 'buy_firerate':
                    core_object.storage.firerate_level += 1 if core_object.storage.firerate_level < 5 else 0
                    self.update_firerate_level_stage2()
                if name == 'ready_button':
                    self.launch_game()
                   