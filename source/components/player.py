#游戏部件--主角
import pygame
from .. import tools,setup
from .. import constants as C
import json
import os

class Player(pygame.sprite.Sprite):
    def __init__(self,name):    #初始化可以 写入名字
        pygame.sprite.Sprite.__init__(self)
        self.name=name
        self.load_data()
        self.setup_states()
        self.setup_velocities()
        self.setup_timers()
        self.load_images()

    def load_data(self):    #载入玩家的json文件
        file_name=self.name+'.json'   #玩家名字
        file_path=os.path.join('source/data/player',file_name)    #角色路径
        with open(file_path) as f:   #打开文件
            self.player_data=json.load(f)    #直接加载文件

    def setup_states(self):    #主角的状态
        self.state='stand'  #初始状态为行走，状态机
        self.face_right=True   #脸是否朝右
        self.dead=False      #是否死亡
        self.success=False   #是否成功
        self.big=False     #是否变大
        self.can_jump=True
        self.hurt_immune=False

    def setup_velocities(self):    #设置数值
        speed=self.player_data['speed']      #读出json文件中的速度数据
        self.x_vel=0
        self.y_vel=0

        self.max_walk_vel=speed['max_walk_speed']    #将数值依次设置为玩家的属性，约定均为正值
        self.max_run_vel=speed['max_run_speed']
        self.max_y_vel=speed['max_y_velocity']
        self.jump_vel=speed['jump_velocity']
        self.walk_accel=speed['walk_accel']
        self.run_accel=speed['run_accel']
        self.turn_accel=speed['turn_accel']     #turn 为转身
        self.grivity=C.GRAVITY
        self.anti_gravity=C.ANTI_GRAVITY

        self.max_x_vel=self.max_walk_vel     #设置初始速度
        self.x_accel=self.walk_accel

    def setup_timers(self):      #创建一系列的计时器
        self.walking_timer=0
        self.transition_timer=0
        self.death_timer=0   #记录死亡时间
        self.success_timer=0    #记录成功时间
        self.hurt_immune_timer=0

    def load_images(self):     #载入主角的各种造型,做出运动的效果
        sheet=setup.GRAPHICS['mario_bros']
        frame_rects=self.player_data['image_frames']

        self.right_small_normal_frames=[]
        self.right_big_normal_frames=[]
        self.right_big_fire_frames=[]
        self.left_small_normal_frames = []
        self.left_big_normal_frames = []
        self.left_big_fire_frames = []    #把图片按方向和类型分为几个帧库，最底层

        self.small_normal_frames=[self.right_small_normal_frames,self.left_small_normal_frames]
        self.big_normal_frames=[self.right_big_normal_frames,self.left_big_normal_frames]
        self.big_fire_frames=[self.right_big_fire_frames,self.left_big_fire_frames]   #六个状态的归纳，小的，大的，开火的

        self.all_frames=[
            self.right_small_normal_frames,
            self.right_big_normal_frames,
            self.right_big_fire_frames,
            self.left_small_normal_frames,
            self.left_big_normal_frames,
            self.left_big_fire_frames,
        ]         #全体的集合

        self.right_frames=self.right_small_normal_frames
        self.left_frames=self.left_small_normal_frames     #设置默认的左和右的帧库

        for group,group_frame_rects in frame_rects.items():    #遍历列表，遍历每一帧，遍历键值对，根据图片类型的不同，分门别类的把图片放到帧库
            for frame_rect in group_frame_rects:
                right_image=tools.get_image(sheet,frame_rect['x'],frame_rect['y'],    #用字典的办法取得参数
                                             frame_rect['width'],frame_rect['height'],(0,0,0),C.PLAYER_MULTI)
                left_image=pygame.transform.flip(right_image,True,False)    #将右图左右反转，第一个参数代表左右反转，第二个参数代表上下
                if group=='right_small_normal':    #根据 名称添加到合理的库
                    self.right_small_normal_frames.append(right_image)
                    self.left_small_normal_frames.append(left_image)
                if group=='right_big_normal':
                    self.right_big_normal_frames.append(right_image)
                    self.left_big_normal_frames.append(left_image)
                if group=='right_big_fire':
                    self.right_big_fire_frames.append(right_image)
                    self.left_big_fire_frames.append(left_image)

        self.frame_index = 0
        self.frames=self.right_frames   #初始为向右
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()


    def update(self,keys):    #写清楚是怎么运动的
        self.current_time=pygame.time.get_ticks()   #步行的计时器，进行人物的更新
        self.handle_states(keys)     #处理状态函数
        self.is_hurt_immune()     #免疫时间判断

    def handle_states(self,keys):    #处理状态函数，根据主角状态的不同调用不同方法

        self.can_jump_or_not(keys)    #判断是否能跳跃

        if self.state=='stand':
            self.stand(keys)
        elif self.state=='walk':
            self.walk(keys)
        elif self.state=='jump':
            self.jump(keys)
        elif self.state=='fall':
            self.fall(keys)
        elif self.state=='die':
            self.die(keys)
        elif self.state=='small to big':
            self.smalltobig(keys)
        elif self.state=='big2small':
            self.bigtosmall(keys)

        if self.face_right:
            self.image=self.right_frames[self.frame_index]
        else:
            self.image=self.left_frames[self.frame_index]

    def can_jump_or_not(self,keys):
        if not keys[pygame.K_SPACE]:    #如果space没有按下，则允许跳跃
            self.can_jump=True

    def stand(self,keys):
        self.frame_index=0
        self.x_vel=0
        self.y_vel=0
        if keys[pygame.K_RIGHT]:
            self.face_right=True    #朝鲜右边
            self.state='walk'
        elif keys[pygame.K_LEFT]:
            self.face_right=False
            self.state='walk'
        elif keys[pygame.K_SPACE] and self.can_jump==True:
            self.state='jump'
            self.y_vel=self.jump_vel

    def walk(self,keys):

        if keys[pygame.K_LSHIFT]:   #按下左shift冲刺
            self.max_x_vel=self.max_run_vel   #最大速度设置为最大跑步速度
            self.x_accel=self.run_accel  #最大加速度设置为最大跑步加速度
        else:
            self.max_x_vel=self.max_walk_vel  #最大步行速度
            self.x_accel=self.walk_accel    #最大步行加速度

        if keys[pygame.K_SPACE] and self.can_jump==True:
            self.state='jump'
            self.y_vel=self.jump_vel
        if self.current_time-self.walking_timer>self.calc_frame_duration():    #摆臂间隔，即帧的变化快慢,帧持久函数
            if self.frame_index<3:    #前三帧为步行帧
                self.frame_index+=1
            else:
                self.frame_index=1
            self.walking_timer=self.current_time
        if keys[pygame.K_RIGHT]:   #有   两种情况，1原本向右，2原本向左
            self.face_right=True
            if self.x_vel<0:
                self.frame_index=5     #5代表刹车帧
                self.x_accel=self.turn_accel
            self.x_vel=self.calc_vel(self.x_vel,self.x_accel,self.max_x_vel,True)
        elif keys[pygame.K_LEFT]:
            self.face_right=False
            if self.x_vel>0:
                self.frame_index=5
                self.x_accel=self.turn_accel
            self.x_vel=self.calc_vel(self.x_vel,self.x_accel,self.max_x_vel,False)
        else:     #让人物走着走着停下来
            if self.face_right:  #如果向右走
                self.x_vel-=self.x_accel
                if self.x_vel<=0:
                    self.x_vel=0
                    self.state='stand'
            else:
                self.x_vel+=self.x_accel
                if self.x_vel>0:
                    self.x_vel=0
                    self.state='stand'

    def jump(self,keys):
        self.frame_index=4   #起跳时为第四帧
        self.y_vel+=self.anti_gravity    #起跳时速度变化
        self.can_jump=False    #一旦起跳，则状态为不能起跳

        if self.y_vel>=0:    #速度大于0时开始下落
            self.state='fall'

        if keys[pygame.K_RIGHT]:
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, True)
        elif keys[pygame.K_LEFT]:
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, False)

        if not keys[pygame.K_SPACE]:
            self.state='fall'

    def fall(self,keys):
        self.y_vel=self.calc_vel(self.y_vel,self.grivity,self.max_y_vel)

        if keys[pygame.K_RIGHT]:
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, True)
        elif keys[pygame.K_LEFT]:
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, False)

    def die(self,keys):     #死亡方法，更新坐标
        self.rect.y+=self.y_vel
        self.y_vel+=self.anti_gravity


    def go_die(self):
        self.dead=True
        self.y_vel=self.jump_vel
        self.frame_index=6     #第六个造型为死亡
        self.state='die'
        self.death_timer=self.current_time

    def go_success(self):
        self.success=True
        self.success_timer=self.current_time

    def smalltobig(self,keys):    #mario变大
        frame_dur=65
        sizes=[1,0,1,0,1,2,0,1,2,0,2]      #变大时帧的变化
        frames_and_idx=[(self.small_normal_frames,0),(self.small_normal_frames,7),(self.big_normal_frames,0)]   #造型
        if self.transition_timer==0:    #变身计时器
            self.big=True
            self.transition_timer=self.current_time
            self.changing_idx=0     #变身帧造型序号
        elif self.current_time-self.transition_timer>frame_dur:    #变身间隔
            self.transition_timer=self.current_time
            frames,idx=frames_and_idx[sizes[self.changing_idx]]      #解包
            self.change_player_image(frames,idx)
            self.changing_idx+=1
            if self.changing_idx==len(sizes):    #如果为最后一个帧，设置为行走状态，且mario的样子设置为大的时候
                self.transition_timer = 0
                self.state = 'walk'
                self.right_frames = self.right_big_normal_frames
                self.left_frames = self.left_big_normal_frames

    def bigtosmall(self,keys):    #mario变小
        frame_dur=65
        sizes=[2,1,0,1,0,1,0,1,0]      #变小时帧的变化
        frames_and_idx=[(self.small_normal_frames,8),(self.big_normal_frames,8),(self.big_normal_frames,4)]   #造型
        if self.transition_timer==0:    #变身计时器
            self.big=False
            self.transition_timer=self.current_time
            self.changing_idx=0     #变身帧造型序号
        elif self.current_time-self.transition_timer>frame_dur:    #变身间隔
            self.transition_timer=self.current_time
            frames,idx=frames_and_idx[sizes[self.changing_idx]]      #解包
            self.change_player_image(frames,idx)
            self.changing_idx+=1
            if self.changing_idx==len(sizes):    #如果为最后一个帧，设置为行走状态，且mario的样子设置为大的时候
                self.transition_timer = 0
                self.state = 'walk'
                self.right_frames = self.right_small_normal_frames
                self.left_frames = self.left_small_normal_frames

    def change_player_image(self,frames,idx):    #改变mario帧
        self.frame_index=idx
        if self.face_right:   #根据面部朝向确定对应的帧
            self.right_frames=frames[0]
            self.image=self.right_frames[self.frame_index]
        else:
            self.left_frames=frames[1]
            self.image=self.left_frames[self.frame_index]
        last_frame_bottom=self.rect.bottom    #默认从脚底出发
        last_frame_centerx=self.rect.centerx
        self.rect=self.image.get_rect()
        self.rect.bottom=last_frame_bottom
        self.rect.centerx=last_frame_centerx    #让帧的位置统一

    def calc_vel(self,vel,accel,max_vel,is_position=True):   #计算速度
        if is_position:
            return min(vel+accel,max_vel)
        else:
            return max(vel-accel,-max_vel)

    def calc_frame_duration(self):
        duration=-60/self.max_run_vel*abs(self.x_vel)+80
        return duration

    def is_hurt_immune(self):
        if self.hurt_immune:
            if self.hurt_immune_timer==0:
                self.hurt_immune_timer=self.current_time
                self.blank_image=pygame.Surface((1,1))    #新建空白帧
            elif self.current_time-self.hurt_immune_timer <2000:  #免疫时间为2000
                if (self.current_time-self.hurt_immune_timer)%100<50:   #前一段时间显示空白帧率
                    self.image=self.blank_image

            else:
                self.hurt_immune=False
                self.hurt_immune_timer=0