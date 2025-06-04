#游戏部件--强化
import pygame
from .. import setup,tools
from  .. import  constants as C

def create_powerup(centerx,centery,type):    #根据宝箱的类型和mario的状态产生不同的道具
    '''create powerup based on type and mario status'''
    return Mushroom(centerx,centery)

class Powerup(pygame.sprite.Sprite):    #强化类
    def __init__(self,centerx,centery,frame_rects):
        pygame.sprite.Sprite.__init__(self)

        self.frames=[]
        self.frame_index=0
        for frame_rect in frame_rects:
            self.frames.append(tools.get_image(setup.GRAPHICS['item_objects'],*frame_rect,(0,0,0),2.5))
        self.image=self.frames[self.frame_index]
        self.rect=self.image.get_rect()
        self.rect.centerx=centerx
        self.rect.centery=centery
        self.origin_y=centery-self.rect.height/2     #初始状态下头部的位置

        self.x_vel=0    #x方向的初速度
        self.direction=1    #初始方向，右
        self.y_vel=-1    #y方向的初速度
        self.gravity=1
        self.max_y_vel=8    #最大向下速度

    def update_position(self, level):  # 怪物位置更新
        self.rect.x += self.x_vel
        self.check_x_collisions(level)
        self.rect.y += self.y_vel
        self.check_y_collisions(level)

        if self.rect.x < 0 or self.rect.y > C.SCREEN_H:  # 跑出地图销毁
            self.kill()

    def check_x_collisions(self, level):  # x方向上的碰撞检测
        sprite = pygame.sprite.spritecollideany(self, level.ground_items_group)  # 判断是否碰撞(地面元素，如果碰撞则调转方向
        if sprite:
            if self.direction:
                self.direction = 0
                self.rect.right = sprite.rect.left
            else:
                self.direction = 1
                self.rect.left = sprite.rect.right
            self.x_vel *= -1

    def check_y_collisions(self, level):
        check_group = pygame.sprite.Group(level.ground_items_group, level.box_group, level.brick_group)
        sprite = pygame.sprite.spritecollideany(self, check_group)
        if sprite:
            if self.rect.top < sprite.rect.top:  # 从上往下掉落
                self.rect.bottom = sprite.rect.top
                self.y_vel = 0
                self.state = 'walk'

        level.check_will_fall(self)  # 判断是否掉落

class Mushroom(Powerup):
    def __init__(self,centerx,centery):
        Powerup.__init__(self,centerx,centery,[(0,0,16,16)])
        self.x_vel=2
        self.state='grow'    #初始状态为生长状态
        self.name='mushroom'

    def update(self,level):
        if self.state=='grow':
            self.rect.y+=self.y_vel
            if self.rect.bottom<self.origin_y:
                self.state='walk'
        elif self.state=='walk':
            pass
        elif self.state=='fall':
            if self.y_vel<self.max_y_vel:
                self.y_vel+=self.gravity

        if self.state!='grow':    #非成长状态下调用位置更新
            self.update_position(level)

class Fireflower(Powerup):   #能变成火人的火焰花      #和金币类差不多呀！
    def __init__(self, centerx, centery):
        frame_rects=[(0,32,16,16),(16,32,16,16),(32,32,16,16),(48,32,16,16)]    #火焰花的帧造型
        Powerup.__init__(self, centerx, centery, frame_rects)
        self.x_vel = 2
        self.state = 'grow'  # 初始状态为生长状态
        self.name = 'fireflower'
        self.timer=0    #计时器

    def update(self, level):
        if self.state == 'grow':
            self.rect.y += self.y_vel
            if self.rect.bottom < self.origin_y:
                self.state = 'rest'

        self.current_timer=pygame.time.get_ticks()

        if self.timer==0:
            self.timer=self.current_timer
        if self.current_timer-self.timer>30:
            self.frame_index+=1
            self.frame_index%=len(self.frames)
            self.timer=self.current_timer
            self.image=self.frames[self.frame_index]

