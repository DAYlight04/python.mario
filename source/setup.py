#游戏启动代码
import pygame
from . import constants as C
from . import tools

pygame.init()
SCREEN=pygame.display.set_mode((C.SCREEN_W, C.SCREEN_H))  #设置屏幕大小

GRAPHICS=tools.load_graphics('resources/graphics')