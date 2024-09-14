import pygame
from game.sprite import Sprite
from core.core import core_object
from utils.pivot_2d import Pivot2D
from game.projectiles import BaseProjectile, PeirceProjectile
from utils.helpers import load_alpha_to_colorkey, scale_surf, tuple_vec_average
from utils.ui.textsprite import TextSprite

class ZombieCluster:
    def __init__(self) -> None:
        self.zombies : set[BaseZombie] = set()
    
    def get_count(self) -> int:
        return len(self.zombies)
    
    @staticmethod
    def combine(clusters : list['ZombieCluster']):
        new_cluster = ZombieCluster()
        for cluster in clusters:
            new_cluster.zombies = new_cluster.zombies.union([*cluster.zombies])
        return new_cluster

class BaseZombie(Sprite):
    inactive_elements : list["BaseZombie"] = []
    active_elements : list['BaseZombie'] = []

    test_image : pygame.Surface = pygame.surface.Surface((50, 50))
    test_image.set_colorkey([0, 0, 255])
    test_image.fill([0, 0, 255])
    pygame.draw.circle(test_image, "Red", (25, 25), 25)
    ui_clusters : list[TextSprite] = []
    def __init__(self) -> None:
        super().__init__()
        self.dynamic_mask = True
        self.speed : float
        self.max_hp : int
        self.hp : int
        BaseZombie.inactive_elements.append(self)
    
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
    
    @classmethod
    def pool(cls, element):
        '''Transfers an element from active to inactive state. Nothing changes if the element is already inactive.'''
        if element in BaseZombie.active_elements:
            BaseZombie.active_elements.remove(element)
        
        if element in Sprite.active_elements:
            Sprite.active_elements.remove(element)
        
        if element not in BaseZombie.inactive_elements:
            BaseZombie.inactive_elements.append(element)

        if element not in Sprite.inactive_elements:
            Sprite.inactive_elements.append(element)
    
    @classmethod
    def unpool(cls, element):
        '''Transfers an element from inactive to active state. Nothing changes if the element is already active.'''
        if element not in BaseZombie.active_elements:
            BaseZombie.active_elements.append(element)
        
        if element not in Sprite.active_elements:
            Sprite.active_elements.append(element)


        if element in BaseZombie.inactive_elements:
            BaseZombie.inactive_elements.remove(element)

        if element in Sprite.inactive_elements:
            Sprite.inactive_elements.remove(element)   
    
    def update(self, delta: float):
        if not core_object.game.is_nm_state(): return
        player_direction : pygame.Vector2 = (core_object.game.player.position - self.position).normalize()
        self.position += player_direction * self.speed * delta
        self.do_collisions()
    
    def do_collisions(self):
        bullets : list[BaseProjectile] = self.get_all_colliding([BaseProjectile.active_elements])
        for bullet in bullets:
            if not isinstance(bullet, BaseProjectile):continue
            if not bullet.is_hostile(bullet.TEAMS.enemy):continue          
            if isinstance(bullet, PeirceProjectile): 
                if self in bullet.hit_memory:
                    continue
                else:
                    bullet.hit_memory.add(self)
            alive : bool = self.take_damage(bullet.damage)
            bullet.when_hit()
            if not alive: break
    
    @classmethod
    def update_class(cls, delta: float):
        clusters : dict[tuple[float, float], ZombieCluster] = {}
        grouped_clusters : dict[tuple[float, float], int] = {}
        for i, zombie in enumerate(BaseZombie.active_elements):
            zombie_pos = zombie.position
            result = ZombieCluster()
            result.zombies.add(zombie)
            for j, other_zombie in enumerate(BaseZombie.active_elements):
                if i >= j: continue
                if other_zombie == zombie: continue
                other_zombie_pos = other_zombie.position
                distance_squared = (zombie_pos - other_zombie_pos).magnitude_squared()
                if distance_squared <= 18 * 18:
                    result.zombies.add(other_zombie)
            if result.get_count() >= 2: clusters[(zombie_pos.x, zombie_pos.y)] = result
        
        banned_clusters : list[tuple[float, float]] = []
        for i, cluster in enumerate(clusters):
            if cluster in banned_clusters: continue
            group : list[tuple[float, float]] = [cluster]
            for j, other_cluster in enumerate(clusters):
                if i >= j: continue
                if cluster == other_cluster: continue
                if other_cluster in banned_clusters: continue
                distance_squared = (cluster[0] - other_cluster[0]) ** 2 + (cluster[1] - other_cluster[1]) ** 2
                if distance_squared < 18 * 18:
                    group.append(other_cluster)
                    banned_clusters.append(other_cluster)

            banned_clusters.append(cluster)
            grouped_clusters[tuple_vec_average(group)] = ZombieCluster.combine([clusters[pos] for pos in group]).get_count()
        cls.clear_clusters()
        for cluster in grouped_clusters:
            count : int = grouped_clusters[cluster]
            cls.create_cluster(cluster, count)
            


    @classmethod
    def clear_clusters(cls):
        for cluster in cls.ui_clusters:
            core_object.main_ui.remove(cluster)
        cls.ui_clusters.clear()
    
    @classmethod
    def create_cluster(cls, pos : tuple[float, float], count : int):
        new_sprite = TextSprite(pos, 'midbottom', 0, f'X{count}', None, None, None, 0, (core_object.game.font_50, 'White', False), 
                                ('Black', 2), colorkey=[0, 255, 0])
        core_object.main_ui.add(new_sprite)
        cls.ui_clusters.append(new_sprite)
                
    
    def take_damage(self, damage : int) -> bool:
        self.hp -= damage
        if self.hp <= 0:
            self.die()
            return False
        return True
    
    def die(self):
        self.kill_instance_safe()
        

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
    
    @classmethod
    def class_cleanup(self):
        self.clear_clusters()

Sprite.register_class(BaseZombie)

class NormalZombie(BaseZombie):
    test_image : pygame.Surface = load_alpha_to_colorkey('assets/graphics/enemy/normal/main.png', [73, 197, 2])
    inactive_elements : list['NormalZombie'] = []
    active_elements : list['NormalZombie'] = []
    def __init__(self) -> None:
        super().__init__()
        NormalZombie.inactive_elements.append(self)
    
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
        

    @classmethod
    def pool(cls, element):
        '''Transfers an element from active to inactive state. Nothing changes if the element is already inactive.'''
        super().pool(element)
        if element in NormalZombie.active_elements:
            NormalZombie.active_elements.remove(element)
        
        if element not in NormalZombie.inactive_elements:
            NormalZombie.inactive_elements.append(element)
    
    @classmethod
    def unpool(cls, element):
        '''Transfers an element from inactive to active state. Nothing changes if the element is already active.'''
        super().unpool(element)
        if element not in NormalZombie.active_elements:
            NormalZombie.active_elements.append(element)


        if element in NormalZombie.inactive_elements:
            NormalZombie.inactive_elements.remove(element)

class QuickZombie(BaseZombie):
    inactive_elements : list['NormalZombie'] = []
    active_elements : list['NormalZombie'] = []

    test_image : pygame.Surface = load_alpha_to_colorkey('assets/graphics/enemy/quick/main.png', [73, 197, 2])
    def __init__(self) -> None:
        super().__init__()
        QuickZombie.inactive_elements.append(self)
    
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
        

    @classmethod
    def pool(cls, element):
        '''Transfers an element from active to inactive state. Nothing changes if the element is already inactive.'''
        super().pool(element)
        if element in QuickZombie.active_elements:
            QuickZombie.active_elements.remove(element)
        
        if element not in QuickZombie.inactive_elements:
            QuickZombie.inactive_elements.append(element)
    
    @classmethod
    def unpool(cls, element):
        '''Transfers an element from inactive to active state. Nothing changes if the element is already active.'''
        super().unpool(element)
        if element not in QuickZombie.active_elements:
            QuickZombie.active_elements.append(element)


        if element in QuickZombie.inactive_elements:
            QuickZombie.inactive_elements.remove(element)

class TankZombie(BaseZombie):
    inactive_elements : list['NormalZombie'] = []
    active_elements : list['NormalZombie'] = []

    test_image : pygame.Surface = load_alpha_to_colorkey('assets/graphics/enemy/tank/main.png', [73, 197, 2])
    def __init__(self) -> None:
        super().__init__()
        TankZombie.inactive_elements.append(self)
    
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
        

    @classmethod
    def pool(cls, element):
        '''Transfers an element from active to inactive state. Nothing changes if the element is already inactive.'''
        super().pool(element)
        if element in TankZombie.active_elements:
            TankZombie.active_elements.remove(element)
        
        if element not in TankZombie.inactive_elements:
            TankZombie.inactive_elements.append(element)
    
    @classmethod
    def unpool(cls, element):
        '''Transfers an element from inactive to active state. Nothing changes if the element is already active.'''
        super().unpool(element)
        if element not in TankZombie.active_elements:
            TankZombie.active_elements.append(element)


        if element in TankZombie.inactive_elements:
            TankZombie.inactive_elements.remove(element)

class ZombieTypes:
    normal = 'normal'
    quick = 'quick'
    tank = 'tank'
    zombie_dict = {normal : NormalZombie, quick : QuickZombie, tank : TankZombie}

    @staticmethod
    def convert(ztype : str):
        return ZombieTypes.zombie_dict[ztype]