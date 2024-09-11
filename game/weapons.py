import pygame
from core.core import core_object
from utils.my_timer import Timer
from dataclasses import dataclass
import dataclasses


class FiringModes:
    auto = 'Automatic'
    burst = 'Burst'
    single = 'Single'

@dataclass
class WeaponStats:
    name : str
    base_damage : int
    base_firerate : float
    fire_mode : str
    burst_info : None|dict = None

    damage_mult : float|int = 1
    damage_bonus : float|int = 0

    firerate_mult : float = 1
    firerate_bonus : float = 0

    buffs : list['WeaponBuff'] = dataclasses.field(default_factory=lambda : [])
    perma_buffs : list['WeaponBuff'] = dataclasses.field(default_factory=lambda : [])

    @property
    def firerate(self):
        return (self.base_firerate / self.firerate_mult) - self.firerate_bonus
    @property
    def damage(self):
        return round((self.base_damage * self.damage_mult) + self.damage_bonus)
    
    def reset(self):
        self.clear_buffs()
        self.perma_buffs.clear()
        self.damage_mult = 1
        self.damage_bonus = 0
        self.firerate_mult = 1
        self.firerate_bonus = 0
        
    
    def apply_buff(self, new_buff : 'WeaponBuff'):
        new_buff.apply(self)
    
    def apply_perma_buff(self, new_buff : 'WeaponBuff'):
        new_buff.apply(self, do_append=False)
        self.perma_buffs.append(new_buff)
    
    def update_buffs(self):
        to_del : list[WeaponBuff] = []
        for buff in self.buffs:
            if buff.timer.isover():
                to_del.append(buff)
        for buff in to_del:
            buff.remove(self)

    def clear_buffs(self):
        while self.buffs:
            self.buffs[0].remove(self)

class WeaponBuff:
    def __init__(self, buff_type : str, value : float, time : float = -1) -> None:
        self.type : str = buff_type
        self.value : float = value
        self.timer : Timer = Timer(time, time_source=core_object.game.game_timer.get_time)

    def apply(self, weapon : WeaponStats, do_append : bool = True):
        if do_append: weapon.buffs.append(self)
        match self.type:
            case WeaponBuffTypes.dmg_mult:
                weapon.damage_mult += self.value
            
            case WeaponBuffTypes.dmg_bonus:
                weapon.damage_bonus += self.value
            
            case WeaponBuffTypes.firerate_mult:
                weapon.firerate_mult += self.value
            
            case WeaponBuffTypes.firerate_bonus:
                weapon.firerate_bonus += self.value

    def remove(self, weapon : WeaponStats, do_remove : bool = True):
        if self not in weapon.buffs: return
        if do_remove: weapon.buffs.remove(self)
        match self.type:
            case WeaponBuffTypes.dmg_mult:
                weapon.damage_mult += self.value
            
            case WeaponBuffTypes.dmg_bonus:
                weapon.damage_bonus += self.value
            
            case WeaponBuffTypes.firerate_mult:
                weapon.firerate_bonus += self.value
            
            case WeaponBuffTypes.firerate_bonus:
                weapon.firerate_bonus += self.value

class WeaponBuffTypes:
    dmg_mult = 'damage_mult'
    dmg_bonus = 'damage_bonus'
    firerate_mult = 'firerate_mult'
    firerate_bonus = 'firerate_bonus'


WEAPONS : dict[str, WeaponStats] = {
    'normal' : WeaponStats('normal', 2, 0.35, FiringModes.auto)
}