#游戏部件--敌人
import pygame
from .. import setup,tools
from .. import constants as C

def create_enemy(enemy_data):    #创建怪兽,根据json中敌人的种类选择创建哪个类的实例
    enemy_type=enemy_data['type']
    x,y_bottom,direction,color=enemy_data['x'],enemy_data['y'],enemy_data['direction'],enemy_data['color']

    if enemy_type==0:
        enemy=Goomba(x,y_bottom,direction,'goomba',color)
    elif enemy_type==1:
        enemy=Koopa(x,y_bottom,direction,'koopa',color)

    return enemy

class Enemy(pygame.sprite.Sprite):
    def __init__(self,x,y_bottom,direction,name,frame_rects):
        pygame.sprite.Sprite.__init__(self)
        self.direction=direction
        self.name=name
        self.frame_index=0
        self.left_frames=[]   #向左移动帧
        self.right_frames=[]     #向右移动帧

        self.load_frames(frame_rects)
        self.frames=self.left_frames if self.direction==0 else self.right_frames
        self.image=self.frames[self.frame_index]
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.bottom=y_bottom

        self.timer=0
        self.x_vel=-1*C.ENEMY_SPEED if direction==0 else C.ENEMY_SPEED
        self.y_vel=0
        self.gravity=C.GRAVITY
        self.state='walk'     #初始状态为行走

    def load_frames(self,frame_rects):     #加载图片帧
        for frame_rect in frame_rects:
            left_frame=tools.get_image(setup.GRAPHICS['enemies'],*frame_rect,(0,0,0),C.ENEMY_MULTI)
            right_frame=pygame.transform.flip(left_frame,True,False)    #左右反转
            self.left_frames.append(left_frame)     #加入到字典中
            self.right_frames.append(right_frame)

    def update(self,level):      #让怪物动起来
        self.current_time=pygame.time.get_ticks()
        self.handle_states(level)
        self.update_position(level)    #更新位置

    def handle_states(self,level):    #处理怪物状态
        if self.state=='walk':
            self.walk()
        elif self.state=='fall':
            self.fall()
        elif self.state=='die':
            self.die()
        elif self.state=='trampled':
            self.trampled(level)
        elif self.state=='slide':
            self.slide()

        if self.direction:
            self.image=self.right_frames[self.frame_index]
        else:
            self.image=self.left_frames[self.frame_index]

    def walk(self):    #行走状态
        if self.current_time-self.timer>125:
            self.frame_index=(self.frame_index+1)%2
            self.image=self.frames[self.frame_index]
            self.timer=self.current_time

    def fall(self):    #下落状态
        if self.y_vel<10:
            self.y_vel+=self.gravity

    def die(self):     #死亡
        self.rect.x+=self.x_vel    #调整位置和速度
        self.rect.y+=self.y_vel
        self.y_vel+=self.gravity
        if self.rect.y>C.SCREEN_H:    #如果调出屏幕外，消失
            self.kill()

    def trampled(self,level):
        pass

    def slide(self):
        pass

    def update_position(self,level):    #怪物位置更新
        self.rect.x+=self.x_vel
        self.check_x_collisions(level)
        self.rect.y+=self.y_vel
        if self.state!='die':   #如果为死亡，不再进行y方向上的碰撞检测
            self.check_y_collisions(level)

    def check_x_collisions(self,level):     #x方向上的碰撞检测
        sprite=pygame.sprite.spritecollideany(self,level.ground_items_group)    #判断是否碰撞(地面元素，如果碰撞则调转方向
        if sprite:
            if self.direction:
                self.direction=0
                self.rect.right=sprite.rect.left
            else:
                self.direction=1
                self.rect.left=sprite.rect.right
            self.x_vel*=-1
        if self.state=='slide':
            enemy=pygame.sprite.spritecollideany(self,level.enemy_group)
            if enemy:
                enemy.go_die(how='slided',direction=self.direction)
                level.enemy_group.remove(enemy)
                level.dying_group.add(enemy)

    def check_y_collisions(self,level):
        check_group=pygame.sprite.Group(level.ground_items_group,level.box_group,level.brick_group)
        sprite=pygame.sprite.spritecollideany(self,check_group)
        if sprite:
            if self.rect.top<sprite.rect.top:      #从上往下掉落
                self.rect.bottom=sprite.rect.top
                self.y_vel=0
                self.state='walk'

        level.check_will_fall(self)   #判断是否掉落

    def go_die(self,how,direction=1):    #敌人死亡
        self.death_timer=self.current_time    #死亡时间
        if how in ['bumped','slided']:   #死因为被顶起,被子弹击中，被无敌mario碰到
            self.x_vel=C.ENEMY_SPEED*direction     #判断死亡方向
            self.y_vel=-8
            self.gravity=0.6
            self.state='die'
            self.frame_index=2
        elif how=='trampled':
            self.state='trampled'


class Goomba(Enemy):    #蘑菇怪
    def __init__(self,x,y_bottom,direction,name,color):      #加载帧图片
        bright_frame_rects=[(0,16,16,16),(16,16,16,16),(32,16,16,16)]
        dark_frame_rects=[(0,48,16,16),(16,48,16,16),(32,48,16,16)]

        if not color:
            frame_rects=bright_frame_rects
        else:
            frame_rects=dark_frame_rects

        Enemy.__init__(self,x,y_bottom,direction,name,frame_rects)

    def trampled(self,level):
        self.x_vel=0
        self.frame_index=2
        if self.death_timer==0:
            self.death_timer=self.current_time
        if self.current_time-self.death_timer>500:
            self.kill()

class Koopa(Enemy):    #乌龟怪类
    def __init__(self, x, y_bottom, direction, name, color):
        bright_frame_rects = [(96, 9, 16, 22), (112, 9, 16, 22), (160, 9, 16, 22)]
        dark_frame_rects = [(96, 72, 16, 22), (112, 72, 16, 22), (160, 72, 16, 22)]

        if not color:
            frame_rects = bright_frame_rects
        else:
            frame_rects = dark_frame_rects

        Enemy.__init__(self, x, y_bottom, direction, name, frame_rects)
        self.shell_timer=0    #龟壳状态计时器

    def trampled(self,level):
        self.x_vel=0
        self.frame_index=2

        if self.shell_timer==0:
            self.shell_timer=self.current_time
        if self.current_time-self.shell_timer>5000:
            self.state='walk'
            self.x_vel=-C.ENEMY_SPEED if self.direction==0 else C.ENEMY_SPEED
            level.enemy_group.add(self)
            level.shell_group.remove(self)
            self.shell_timer=0


    def slide(self):
        pass