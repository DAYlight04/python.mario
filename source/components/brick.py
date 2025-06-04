#游戏部件--砖块
import pygame
from .. import tools,setup
from .. import constants as C
from .powerup import create_powerup

class Brick(pygame.sprite.Sprite):   #继承精灵类
    def __init__(self,x,y,brick_type,group,color=None,name='brick'):
        pygame.sprite.Sprite.__init__(self)
        self.x=x
        self.y=y
        self.brick_type=brick_type
        self.name=name
        self.group=group
        bright_frame_rects=[(16,0,16,16),(48,0,16,16)]   #正常关卡
        dark_frame_rects=[(16,32,16,16),(48,32,16,16)]    #水下关卡

        if not color:
            self.frame_rects=bright_frame_rects
        else:
            self.frame_rects=dark_frame_rects

        self.frames=[]
        for frame_rect in self.frame_rects:      #加载图片放到帧列表里面
            self.frames.append(tools.get_image(setup.GRAPHICS['tile_set'],*frame_rect,(0,0,0),C.BRICK_MULTI))

        self.frame_index=0
        self.image=self.frames[self.frame_index]
        self.rect=self.image.get_rect()
        self.rect.x=self.x
        self.rect.y=self.y     #设置第一帧的图片和在地图的坐标
        self.gravity = C.GRAVITY

        self.state = 'rest'  # 默认状态为休息状态

    def update(self):  # 更新砖块
        self.current_time = pygame.time.get_ticks()
        self.handle_state()

    def handle_state(self):
        if self.state == 'rest':  # 休息状态
            self.rest()
        elif self.state == 'bumped':  # 被顶起的状态
            self.bumped()
        elif self.state == 'open':  # 被打开的状态
            self.open()

    def rest(self):  # 休息状态，砖块只有一个造型
        pass

    def go_bumped(self):
        self.y_vel = -7
        self.state = 'bumped'

    def bumped(self):  # 被顶起的状态
        self.rect.y += self.y_vel
        self.y_vel += self.gravity    #被顶起不会改变帧

        if self.rect.y > self.y + 5:
            self.rect.y = self.y

            if self.brick_type==0:
                self.state = 'rest'
            elif self.brick_type==1:
                self.state='open'
            else:
                self.group.add(create_powerup(self.rect.centerx,self.rect.centery,self.brick_type))

    def open(self):  # 打开状态
        self.frame_index=1

    def smashed(self,group):
        debris=[     #碎片列表信息，位置坐标和炸裂后各方向速度
            (self.rect.x,self.rect.y,-2,-10),
            (self.rect.x, self.rect.y, 2, -10),
            (self.rect.x, self.rect.y, -2, -5),
            (self.rect.x, self.rect.y, 2, 5),
        ]
        for d in debris:
            group.add(Debris(*d))
        self.kill()

class Debris(pygame.sprite.Sprite):
    def __init__(self,x,y,x_vel,y_vel):
        pygame.sprite.Sprite.__init__(self)
        self.image=tools.get_image(setup.GRAPHICS['tile_set'],68,20,8,8,(0,0,0),C.BRICK_MULTI)
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.x_vel=x_vel
        self.y_vel=y_vel
        self.gravity=C.GRAVITY

    def update(self,*args):   #额外传入了一个参数
        self.rect.x+=self.x_vel
        self.rect.y+=self.y_vel
        self.y_vel+=self.gravity
        if self.rect.y>C.SCREEN_H:
            self.kill()

