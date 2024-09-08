import pygame
import random
from utils.ui.ui_sprite import UiSprite
from utils.ui.textsprite import TextSprite
from utils.ui.base_ui_elements import BaseUiElements
import utils.tween_module as TweenModule
import utils.interpolation as interpolation
from utils.my_timer import Timer
from utils.ui.brightness_overlay import BrightnessOverlay
from math import floor
class Menu:
    font_40 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 40)
    font_50 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 50)
    font_60 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 60)
    font_70 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 70)
    font_150 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 150)

    def __init__(self) -> None:
        self.stage : int
        self.stages : list[list[UiSprite]]
        self.bg_color = (94, 129, 162)
        
    def init(self):

        window_size = core_object.main_display.get_size()
        centerx = window_size[0] // 2

        self.stage = 1
        
        self.stage_data : list[dict] = [None, {}]
        self.stages = [None, 
        [BaseUiElements.new_text_sprite('Game Title', (Menu.font_60, 'Black', False), 0, 'midtop', (centerx, 50)),
        BaseUiElements.new_button('BlueButton', 'Play', 1, 'midbottom', (centerx, window_size[1] - 15), (0.5, 1.4), 
        {'name' : 'play_button'}, (Menu.font_40, 'Black', False))], #stage 1
        ]
        self.bg_color = (94, 129, 162)
    
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
        sprite_list = [sprite for sprite in self.stages[self.stage] if sprite.visible == True]
        sprite_list.sort(key = lambda sprite : sprite.zindex)
        for sprite in sprite_list:
            sprite.draw(display)
        
    
    def update(self, delta : float):
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
                    pygame.event.post(pygame.Event(core_object.START_GAME, {}))
                   
    
    def handle_mouse_event(self, event : pygame.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos : tuple = event.pos
            sprite : UiSprite
            for sprite in self.stages[self.stage]:
                if type(sprite) != UiSprite: continue
                if sprite.rect.collidepoint(mouse_pos):
                    sprite.on_click()