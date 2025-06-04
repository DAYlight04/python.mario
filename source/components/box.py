#游戏部件--方格
#游戏部件--砖块
import pygame

from .powerup import create_powerup
from .. import tools,setup
from .. import constants as C
from . import powerup

class Box(pygame.sprite.Sprite):   #继承精灵类
    def __init__(self,x,y,box_type,group,name='box'):
        pygame.sprite.Sprite.__init__(self)
        self.x=x
        self.y=y
        self.box_type=box_type
        self.group=group
        self.name=name
        self.frame_rects=[
            (384,0,16,16),
            (400,0,16,16),
            (416,0,16,16),
            (432,0,16,16),
        ]

        self.frames=[]
        for frame_rect in self.frame_rects:      #加载图片放到帧列表里面
            self.frames.append(tools.get_image(setup.GRAPHICS['tile_set'],*frame_rect,(0,0,0),C.BRICK_MULTI))

        self.frame_index=0
        self.image=self.frames[self.frame_index]
        self.rect=self.image.get_rect()
        self.rect.x=self.x
        self.rect.y=self.y     #设置第一帧的图片和在地图的坐标
        self.gravity=C.GRAVITY

        self.state='rest'   #默认状态为休息状态
        self.timer=0

    def update(self):    #更新宝箱
        self.current_time=pygame.time.get_ticks()
        self.handle_state()

    def handle_state(self):
        if self.state=='rest':    #休息状态
            self.rest()
        elif self.state=='bumped':   #被顶起的状态
            self.bumped()
        elif self.state=='open':    #被打开的状态
            self.open()

    def rest(self):    #休息状态，宝箱闪烁
        frame_durations=[400,100,10,50]   #每个帧的持续时间
        if self.current_time-self.timer>frame_durations[self.frame_index]:
            self.frame_index=(self.frame_index+1)%4
            self.timer=self.current_time
        self.image=self.frames[self.frame_index]

    def go_bumped(self):
        self.y_vel=-7
        self.state='bumped'

    def bumped(self):    #被顶起的状态
        self.rect.y+=self.y_vel
        self.y_vel+=self.gravity
        self.frame_index=3
        self.image=self.frames[self.frame_index]

        if self.rect.y>self.y+5:
            self.rect.y=self.y
            self.state='open'

            #被顶起后判断宝箱的类型，开出的物品，tox_type 0，1，2，3 对应空，金币，星星，蘑菇
            if self.box_type==1:
                pass
            else:
                self.group.add(create_powerup(self.rect.centerx,self.rect.centery,self.box_type))

    def open(self):   #打开状态
        pass


