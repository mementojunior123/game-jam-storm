import pygame
from core.core import core_object
from utils.my_timer import Timer
from typing import Callable
from dataclasses import dataclass
import dataclasses

from game.projectiles import BaseProjectile


class FiringModes:
    auto = 'Automatic'
    burst = 'Burst'
    single = 'Single'

class BaseWeapon:
    def __init__(self, stats : 'WeaponStats', time_source : Callable[[], float]|None = None, name : str|None = None) -> None:
        self.stats : WeaponStats = stats
        self.unique_name : str|None = name
        self.team : str = BaseProjectile.TEAMS.friendly
        self.shot_cooldown : Timer = Timer(self.stats.firerate, time_source)
    
    def get_game_source(self):
        self.shot_cooldown.time_source = core_object.game.game_timer.get_time
    
    def reset_shot_cooldown(self):
        self.shot_cooldown.set_duration(self.stats.firerate)
    
    def ready_shot_cooldown(self):
        self.shot_cooldown.set_duration(0)
    
    def shoot(self, shot_origin : pygame.Vector2, shot_direction : pygame.Vector2):
        if not self.shot_cooldown.isover(): return
        BaseProjectile.spawn(shot_origin, self.stats.projectile_speed, shot_direction, self.team, self.stats.damage)
        self.reset_shot_cooldown()

class ShotgunWeapon(BaseWeapon):
    def __init__(self, stats: 'WeaponStats', pellet_count : int, spread : float, time_source: Callable[[], float] | None = None, name : str|None = None) -> None:
        super().__init__(stats, time_source, name)
        self.pellet_count : int = pellet_count
        self.bullet_spread : float = spread
    
    def shoot(self, shot_origin : pygame.Vector2, shot_direction : pygame.Vector2):
        if not self.shot_cooldown.isover(): return
        angles : list[float] = [pygame.math.lerp(-self.bullet_spread, self.bullet_spread, i / (self.pellet_count - 1)) for i in range(self.pellet_count)]
        for angle in angles:
            BaseProjectile.spawn(shot_origin, self.stats.projectile_speed, shot_direction.rotate(angle), self.team, self.stats.damage)
        self.reset_shot_cooldown()

@dataclass
class WeaponStats:
    base_damage : int
    base_firerate : float
    fire_mode : str
    projectile_speed : float
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


WEAPONS : dict[str, BaseWeapon] = {
    'Pistol' : BaseWeapon(WeaponStats(3, 0.35, FiringModes.auto, 7)),
    'Rifle' : BaseWeapon(WeaponStats(2, 0.2, FiringModes.auto, 7)),
    'Shotgun' : ShotgunWeapon(WeaponStats(2, 0.5, FiringModes.single, 7), 5, 20)
}