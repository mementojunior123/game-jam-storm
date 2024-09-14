import pygame
from utils.helpers import ColorType, scale_surf, to_roman, Callable, paint_upgrade_bar, reset_upgrade_bar, make_upgrade_bar
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
    def alert_player(self, text : str, alert_speed : float = 1):
        text_sprite = TextSprite(pygame.Vector2(core_object.main_display.get_width() // 2, 90), 'midtop', 0, text, 
                        text_settings=(core_object.menu.font_60, 'White', False), text_stroke_settings=('Black', 2), colorkey=(0,255,0))
        
        text_sprite.rect.bottom = -5
        text_sprite.position = pygame.Vector2(text_sprite.rect.center)
        temp_y = text_sprite.rect.centery
        self.add_temp(text_sprite, 5)
        TInfo = TweenModule.TweenInfo
        goal1 = {'rect.centery' : 50, 'position.y' : 50}
        info1 = TInfo(interpolation.quad_ease_out, 0.3 / alert_speed)
        goal2 = {'rect.centery' : temp_y, 'position.y' : temp_y}
        info2 = TInfo(interpolation.quad_ease_in, 0.4 / alert_speed)
        
        on_screen_time = 1 / alert_speed
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
        else:
            print('Find and replace failed')
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

class Menu(BaseMenu):
    token_image : pygame.Surface = pygame.image.load('assets/graphics/ui/resized_token_green_colorkey.png')
    token_image.set_colorkey([0, 255, 0])
    token_image = scale_surf(token_image, 0.075)

    def init(self):
        self.bg_color = (94, 129, 162)
        self.stage = 1
        self.stage_data : list[dict] = [None, {}, {}, {}, {}, {}]
        window_size = core_object.main_display.get_size()
        centerx = window_size[0] // 2
        upgrade_bar_surf1 = make_upgrade_bar()
        self.stages = [None, 
        [BaseUiElements.new_text_sprite('StormZ Day', (Menu.font_60, 'Black', False), 0, 'midtop', (centerx, 25)),
        BaseUiElements.new_button('BlueButton', 'Play', 1, 'midbottom', (centerx, window_size[1] - 15), (0.5, 1.4), 
        {'name' : 'play_button'}, (Menu.font_40, 'Black', False))], 

        #stage1 --> stage 2
        [BaseUiElements.new_text_sprite('Upgrades', (Menu.font_60, 'Black', False), 0, 'midtop', (centerx, 25)),
        UiSprite(Menu.token_image, Menu.token_image.get_rect(topright = (955, 15)), 0, 'token_image'),
        TextSprite(pygame.Vector2(903, 40), 'midright', 0, '3', 'token_count', None, None, 0, (Menu.font_50, 'White', False), ('Black', 2), colorkey=[0,255,0]),
        BaseUiElements.new_button('BlueButton', 'Ready', 1, 'bottomright', (940, window_size[1] - 15), (0.4, 1.0), 
        {'name' : 'ready_button'}, (Menu.font_40, 'Black', False)),
        BaseUiElements.new_button('BlueButton', 'Back', 1, 'topleft', (15, 10), (0.4, 1.0), 
        {'name' : 'back_button'}, (Menu.font_40, 'Black', False)),
        BaseUiElements.new_button('BlueButton', 'Next', 1, 'midbottom', (centerx, window_size[1] - 25), (0.4, 1.0), 
        {'name' : 'next_button'}, (Menu.font_40, 'Black', False)),
        
        TextSprite(pygame.Vector2(180, 140), 'midtop', 0, 'Firerate I\nCost : 2', 'firerate_upg_title', 
                   {}, {}, 0, (Menu.font_50, 'Black', False), colorkey=[0, 255, 0]),
        UiSprite(upgrade_bar_surf1, upgrade_bar_surf1.get_rect(midtop = (180, 235)), 0, 'firerate_upg_bar'),
        BaseUiElements.new_button('BlueButton', 'Buy', 1, 'midtop', (180, 360), (0.35, 1), 
        {'name' : 'buy_firerate'}, (Menu.font_40, 'Black', False)),
        
        TextSprite(pygame.Vector2(465, 140), 'midtop', 0, 'Damage I\nCost : 2', 'damage_upg_title', {}, {}, 0, (Menu.font_50, 'Black', False), colorkey=[0, 255, 0]),
        UiSprite(upgrade_bar_surf1.copy(), upgrade_bar_surf1.get_rect(midtop = (465, 235)), 0, 'damage_upg_bar'),
        BaseUiElements.new_button('BlueButton', 'Buy', 1, 'midtop', (465, 360), (0.35, 1), 
        {'name' : 'buy_damage'}, (Menu.font_40, 'Black', False)),

        TextSprite(pygame.Vector2(750, 140), 'midtop', 0, 'Vitality I\nCost : 2', 'vitality_upg_title', {}, {}, 0, (Menu.font_50, 'Black', False), colorkey=[0, 255, 0]),
        UiSprite(upgrade_bar_surf1.copy(), upgrade_bar_surf1.get_rect(midtop = (750, 235)), 0, 'vitality_upg_bar'),
        BaseUiElements.new_button('BlueButton', 'Buy', 1, 'midtop', (750, 360), (0.35, 1), 
        {'name' : 'buy_vitality'}, (Menu.font_40, 'Black', False)),
        ],

        #stage 2 --> stage 3
        [BaseUiElements.new_text_sprite('Weapons', (Menu.font_60, 'Black', False), 0, 'midtop', (centerx, 25)),
         BaseUiElements.new_button('BlueButton', 'Ready', 1, 'bottomright', (940, window_size[1] - 15), (0.4, 1.0), 
        {'name' : 'ready_button'}, (Menu.font_40, 'Black', False)),
        BaseUiElements.new_button('BlueButton', 'Back', 1, 'topleft', (15, 10), (0.4, 1.0), 
        {'name' : 'back_button'}, (Menu.font_40, 'Black', False)),
        BaseUiElements.new_button('BlueButton', 'Prev', 1, 'midbottom', (centerx, window_size[1] - 25), (0.4, 1.0), 
        {'name' : 'prev_button'}, (Menu.font_40, 'Black', False)),
        UiSprite(Menu.token_image, Menu.token_image.get_rect(topright = (955, 15)), 0, 'token_image'),
        TextSprite(pygame.Vector2(903, 40), 'midright', 0, '3', 'token_count', None, None, 0, (Menu.font_50, 'White', False), ('Black', 2), colorkey=[0,255,0]),
        *self.make_weapon_ui('Pistol', (100, 140)), *self.make_weapon_ui('Rifle', (345, 140)), *self.make_weapon_ui('Shotgun', (590, 140)), 
        *self.make_weapon_ui('Piercer', (835, 140))],
        #stage 3 --> stage 4
        [BaseUiElements.new_text_sprite('Results', (Menu.font_60, 'Black', False), 0, 'midtop', (centerx, 25)),
        BaseUiElements.new_button('BlueButton', 'Next', 1, 'midbottom', (centerx, window_size[1] - 15), (0.35, 1), 
        {'name' : 'next_button'}, (Menu.font_40, 'Black', False)),
        TextSprite(pygame.Vector2(centerx, 90), 'midtop', 0, 'Wave:', 'wave_title', None, None, 0, (Menu.font_50, 'Black', False), colorkey=[0,255,0]),
        TextSprite(pygame.Vector2(centerx, 120), 'midtop', 0, '0', 'wave_count', None, None, 0, (Menu.font_50, 'Black', False), colorkey=[0,255,0]),
        TextSprite(pygame.Vector2(560, 120), 'midleft', 0, 'New High!', 'wave_high', {'visible' : False}, None, 0, (Menu.font_50, 'Black', False), colorkey=[0,255,0]),
        TextSprite(pygame.Vector2(centerx, 210), 'midtop', 0, 'Score:', 'wave_title', None, None, 0, (Menu.font_50, 'Black', False), colorkey=[0,255,0]),
        TextSprite(pygame.Vector2(centerx, 240), 'midtop', 0, '0', 'score_count', None, None, 0, (Menu.font_50, 'Black', False), colorkey=[0,255,0]),
        TextSprite(pygame.Vector2(560, 120), 'midleft', 0, 'New High!', 'score_high', {'visible' : False}, None, 0, (Menu.font_50, 'Black', False), colorkey=[0,255,0]),
        TextSprite(pygame.Vector2(centerx, 310), 'midtop', 0, 'Tokens Gained:', 'token_title', None, None, 0, (Menu.font_50, 'Black', False), colorkey=[0,255,0]),
        TextSprite(pygame.Vector2(centerx, 340), 'midtop', 0, '0', 'token_count', None, None, 0, (Menu.font_50, 'Black', False), colorkey=[0,255,0]),
        TextSprite(pygame.Vector2(centerx, 390), 'midtop', 0, 'Current Token Count : 0', 'current_token_count', None, None, 0, (Menu.font_50, 'Black', False), colorkey=[0,255,0]),
        ]
        ]
        #self.get_sprite_by_name(2, 'token_count').rect.topright = (900, 15)
    
    def enter_stage2(self):
        self.stage = 2
        self.update_firerate_level_stage2()
        self.update_damage_level_stage2()
        self.update_vitality_level_stage2()
        self.update_token_count()
    
    def update_firerate_level_stage2(self):
        firerate_upg_bar = self.get_sprite_by_name(2, 'firerate_upg_bar')
        reset_upgrade_bar(firerate_upg_bar.surf)
        for i in range(core_object.storage.firerate_level):
            paint_upgrade_bar(firerate_upg_bar.surf, i)
            if i >= 4: break
        firerate_upg_title : TextSprite = self.get_sprite_by_name(2, 'firerate_upg_title')
        firerate_level : int = core_object.storage.firerate_level
        if core_object.storage.firerate_level >= 5:
            new_button = BaseUiElements.new_button('BlueButton', 'MAXED', 1, 'midtop', (180, 360), (0.35, 1), 
                                                   {'name' : 'buy_firerate'}, (Menu.font_40, 'Black', False))
            self.find_and_replace(new_button, 2, name='buy_firerate')
            firerate_upg_title.text = f'Firerate {'MAXED'}\nCost : MAXED'
        else:
            new_button = BaseUiElements.new_button('BlueButton', 'Buy', 1, 'midtop', (180, 360), (0.35, 1), 
                                                   {'name' : 'buy_firerate'}, (Menu.font_40, 'Black', False))
            self.find_and_replace(new_button, 2, name='buy_firerate')
            firerate_upg_title.text = f'Firerate {to_roman(firerate_level + 1)}\nCost : {core_object.storage.COST_TABLE['Firerate'][firerate_level+1]}'
    
    def update_damage_level_stage2(self):
        damage_upg_bar = self.get_sprite_by_name(2, 'damage_upg_bar')
        reset_upgrade_bar(damage_upg_bar.surf)
        for i in range(core_object.storage.damage_level):
            paint_upgrade_bar(damage_upg_bar.surf, i)
            if i >= 4: break
        damage_upg_title : TextSprite = self.get_sprite_by_name(2, 'damage_upg_title')
        damage_level : int = core_object.storage.damage_level
        if core_object.storage.damage_level >= 5:
            new_button = BaseUiElements.new_button('BlueButton', 'MAXED', 1, 'midtop', (465, 360), (0.35, 1), 
                                                   {'name' : 'buy_damage'}, (Menu.font_40, 'Black', False))
            self.find_and_replace(new_button, 2, name='buy_damage')
            damage_upg_title.text = f'Damage {'MAXED'}\nCost : MAXED'
        else:
            new_button = BaseUiElements.new_button('BlueButton', 'Buy', 1, 'midtop', (465, 360), (0.35, 1), 
                                                   {'name' : 'buy_damage'}, (Menu.font_40, 'Black', False))
            self.find_and_replace(new_button, 2, name='buy_damage')
            damage_upg_title.text = f'Damage {to_roman(damage_level + 1)}\nCost : {core_object.storage.COST_TABLE['Damage'][damage_level+1]}'
    
    def update_vitality_level_stage2(self):
        vitality_upg_bar = self.get_sprite_by_name(2, 'vitality_upg_bar')
        reset_upgrade_bar(vitality_upg_bar.surf)
        for i in range(core_object.storage.vitality_level):
            paint_upgrade_bar(vitality_upg_bar.surf, i)
            if i >= 4: break
        vitality_upg_title : TextSprite = self.get_sprite_by_name(2, 'vitality_upg_title')
        vitality_level : int = core_object.storage.vitality_level
        if core_object.storage.vitality_level >= 5:
            new_button = BaseUiElements.new_button('BlueButton', 'MAXED', 1, 'midtop', (750, 360), (0.35, 1), 
                                                   {'name' : 'buy_vitality'}, (Menu.font_40, 'Black', False))
            self.find_and_replace(new_button, 2, name='buy_vitality')
            vitality_upg_title.text = f'Vitality {'MAXED'}\nCost : MAXED'
        else:
            new_button = BaseUiElements.new_button('BlueButton', 'Buy', 1, 'midtop', (750, 360), (0.35, 1), 
                                                   {'name' : 'buy_vitality'}, (Menu.font_40, 'Black', False))
            self.find_and_replace(new_button, 2, name='buy_vitality')
            vitality_upg_title.text = f'Vitality {to_roman(vitality_level + 1)}\nCost : {core_object.storage.COST_TABLE['Vitality'][vitality_level+1]}'
    
    def update_token_count(self, current_stage : int = 2):
        token_count : TextSprite = self.get_sprite_by_name(current_stage, 'token_count')
        token_count.text = f'{core_object.storage.upgrade_tokens}'
        token_count.rect = token_count.surf.get_rect(midright = (906, 40))

    def make_weapon_ui(self, weapon_name : str, midtop : tuple[int, int]|pygame.Vector2) -> tuple[UiSprite]:
        weapon_title_text = f'{weapon_name}\nCost : {core_object.storage.COST_TABLE['Weapons'][weapon_name]}'
        weapon_title = BaseUiElements.new_text_sprite(weapon_title_text, (Menu.font_50, 'Black', False), 0, 'midtop', midtop, name = f'weapon_title_{weapon_name}')
        weapon_interact = BaseUiElements.new_button('BlueButton', 'Buy', 1, 'midtop', (midtop[0], midtop[1] + 80), (0.4, 1), 
                                                    name=f'weapon_interact_{weapon_name}')
        return weapon_title, weapon_interact
    
    def update_weapon_ui_stage4(self, weapon_name : str):
        weapon_title = self.get_sprite_by_name(self.stage, f'weapon_title_{weapon_name}')
        if not weapon_title: return
        midtop : tuple[int, int] = weapon_title.rect.midtop
        interact_text : str
        if weapon_name not in core_object.storage.owned_weapons:
            interact_text = 'Buy'
        elif weapon_name != core_object.storage.weapon_equipped:
            interact_text = 'Equip'
        else:
            interact_text = 'Equipped'
        new_weapon_interact = BaseUiElements.new_button('BlueButton', interact_text, 1, 'midtop', (midtop[0], midtop[1] + 60), 
                                                        (0.4, 1 if interact_text != 'Equipped' else 1),name=f'weapon_interact_{weapon_name}')
        self.find_and_replace(new_weapon_interact, self.stage, name=f'weapon_interact_{weapon_name}')
    

    def exit_stage2(self):
        pass

    def enter_stage3(self):
        self.stage = 3
        for weapon in core_object.storage.ALL_WEAPONS:
            self.update_weapon_ui_stage4(weapon)
        self.update_token_count(self.stage)

    def enter_stage4(self, score : int, wave_count : int, tokens_gained : int):
        prev_highscore : int = core_object.storage.high_score
        prev_wave_record : int = core_object.storage.high_wave
        self.get_sprite_by_name(4, 'wave_count').text = f'{wave_count}'
        self.get_sprite_by_name(4, 'score_count').text = f'{score}'
        self.get_sprite_by_name(4, 'token_count').text = f'{tokens_gained}'
        self.get_sprite_by_name(4, 'wave_high').visible = (wave_count > prev_wave_record)
        self.get_sprite_by_name(4, 'score_high').visible = (score > prev_highscore)
        current_token_count : TextSprite = self.get_sprite_by_name(4, 'current_token_count')
        current_token_count.text = f'Current Token Count : {core_object.storage.upgrade_tokens}'
        current_token_count.rect.centerx = 480
    
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
                    if core_object.storage.firerate_level < 5:
                        cost : int = core_object.storage.COST_TABLE['Firerate'][core_object.storage.firerate_level + 1]
                        if core_object.storage.upgrade_tokens >= cost:
                            core_object.storage.upgrade_tokens -= cost
                            core_object.storage.firerate_level += 1
                            self.update_firerate_level_stage2()
                            self.update_token_count()
                        else:
                            self.alert_player('Not enough tokens!')
                    else:
                        self.alert_player('This stat is already maxed!')
                elif name == 'buy_damage':
                    if core_object.storage.damage_level < 5:
                        cost : int = core_object.storage.COST_TABLE['Damage'][core_object.storage.damage_level + 1]
                        if core_object.storage.upgrade_tokens >= cost:
                            core_object.storage.upgrade_tokens -= cost
                            core_object.storage.damage_level += 1
                            self.update_damage_level_stage2()
                            self.update_token_count()
                        else:
                            self.alert_player('Not enough tokens!')
                    else:
                        self.alert_player('This stat is already maxed!')
                elif name == 'buy_vitality':
                    if core_object.storage.vitality_level < 5:
                        cost : int = core_object.storage.COST_TABLE['Vitality'][core_object.storage.vitality_level + 1]
                        if core_object.storage.upgrade_tokens >= cost:
                            core_object.storage.upgrade_tokens -= cost
                            core_object.storage.vitality_level += 1
                            self.update_vitality_level_stage2()
                            self.update_token_count()
                        else:
                            self.alert_player('Not enough tokens!')
                    else:
                        self.alert_player('This stat is already maxed!')
                elif name == 'ready_button':
                    self.launch_game()
                
                elif name == 'back_button':
                    self.stage = 1
                elif name == 'next_button':
                    self.enter_stage3()
            
            case 3:
                if name == 'back_button':
                    self.stage = 1
                elif name == 'ready_button':
                    self.launch_game()
                elif name == 'prev_button':
                    self.enter_stage2()
                
                elif name[:16] == 'weapon_interact_':
                    weapon_name = name[16:]
                    if weapon_name == core_object.storage.weapon_equipped:
                        self.alert_player('You are already equpping this item!', 1.5)
                    elif weapon_name in core_object.storage.owned_weapons:
                        core_object.storage.weapon_equipped = weapon_name
                    else:
                        cost : int = core_object.storage.COST_TABLE['Weapons'][weapon_name]
                        if core_object.storage.upgrade_tokens >= cost:
                            core_object.storage.upgrade_tokens -= cost
                            self.update_token_count(self.stage)
                            core_object.storage.owned_weapons.append(weapon_name)
                            core_object.storage.weapon_equipped = weapon_name
                        else:
                            self.alert_player('Not enough tokens!')
                    for weapon in core_object.storage.ALL_WEAPONS:
                        self.update_weapon_ui_stage4(weapon)
                    self.update_token_count(self.stage)

            case 4:
                if name == 'next_button':
                    self.stage = 1