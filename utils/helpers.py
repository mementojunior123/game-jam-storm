import pygame
from math import copysign
from typing import Callable, Any, Union
from random import random
from collections import OrderedDict

def to_roman(num : int) -> str:

    roman = OrderedDict()
    roman[1000] = "M"
    roman[900] = "CM"
    roman[500] = "D"
    roman[400] = "CD"
    roman[100] = "C"
    roman[90] = "XC"
    roman[50] = "L"
    roman[40] = "XL"
    roman[10] = "X"
    roman[9] = "IX"
    roman[5] = "V"
    roman[4] = "IV"
    roman[1] = "I"

    def roman_num(num):
        for r in roman.keys():
            x, y = divmod(num, r)
            yield roman[r] * x
            num -= (r * x)
            if num <= 0:
                break

    return "".join([a for a in roman_num(num)])

ColorType = Union[list[int], tuple[int, int, int], pygame.Color]

class Task:
    def __init__(self, callback : Callable, *args, **kwargs) -> None:
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
    
    def execute(self):
        self.callback(*self.args, **self.kwargs)

def scale_surf(surf : pygame.Surface, scale : float):
    return pygame.transform.scale_by(surf, scale)

def rotate_around_pivot(image : pygame.Surface, rect : pygame.Rect, angle : float, 
                        anchor : pygame.Vector2 = None, offset : pygame.Vector2= None, return_new_pos = False):
    
    if anchor:
        real_anchor_point = anchor or pygame.Vector2(rect.center) + offset
        offset= offset or real_anchor_point - pygame.Vector2(rect.center)

    elif offset:
        real_anchor_point = offset + pygame.Vector2(rect.center)
        offset = offset

    new_offset = offset.rotate(angle)
    old_center = rect.center

    new_image = pygame.transform.rotate(image, -angle)
    new_rect = new_image.get_rect(center = old_center)
    new_pos = real_anchor_point - new_offset
    new_rect.center = round(new_pos)
    if return_new_pos:
        return new_image, new_rect, new_pos
    else:
        return new_image, new_rect

def rotate_around_center(image : pygame.Surface, pos : pygame.Vector2, angle : float) -> tuple[pygame.Surface, pygame.Rect]:
    new_image = pygame.transform.rotate(image, -angle)
    new_rect = new_image.get_rect(center = round(pos))
    return new_image, new_rect

def rotate_around_pivot_accurate(image : pygame.Surface, pos : pygame.Vector2, angle : float, 
                        anchor : pygame.Vector2 = None, offset : pygame.Vector2 = None, debug = False):
    
    if anchor is not None:
        real_anchor_point = anchor
        offset = offset or (real_anchor_point - pos).rotate(-angle)

    elif offset is not None:
        real_anchor_point = pos + offset.rotate(angle)
        offset = offset
    else:
        raise ValueError('Either offset or anchor must be provided')
    new_offset = offset.rotate(angle)

    new_image = pygame.transform.rotate(image, -angle)  
    new_pos = real_anchor_point - new_offset


    new_rect = new_image.get_rect(center = round(new_pos))
    if debug:
        return new_image, new_rect, new_pos, [real_anchor_point]
    else:
        return new_image, new_rect, new_pos

def sign(x):
    return copysign(1, x)
def is_sorted(iterable : list[object], key : Callable[[object], float|int]):
    current_val = key(iterable[0])
    for obj in iterable:
        val = key(obj)
        if val < current_val: return False
    return True

def average(values : list[float]):
    return sum(values) / len(values)

def random_float(a : float, b : float):
    return pygame.math.lerp(a, b, random())
