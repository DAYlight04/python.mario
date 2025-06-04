#游戏部件--金币    ----继承pygame中里的精灵类
import pygame
from .. import tools,setup
from .. import constants as C

class FlashingCoin(pygame.sprite.Sprite):    #建立闪烁金币类 ，继承了pygame的精灵类，会调用精灵类的启动方法----金币不止出现在屏幕上，还会作为游戏道具
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.frames = []
        self.frame_index=0
        frame_rects=[(1,160,5,8),(9,160,5,8),(17,160,5,8),(9,160,5,8)]   #忽明忽暗,方框的左上角位置，和方框的宽高
        self.load_frames(frame_rects)     #载入图片
        self.image=self.frames[self.frame_index]
        self.rect=self.image.get_rect()    #指定了一个皮肤和用来表示他位置的方框
        self.rect.x=280
        self.rect.y=58
        self.timer=0    #游戏帧超过多少个就把金币换成下一个，呈现动画效果

    def load_frames(self,frame_rects):   #载入图片的方法，将帧存入列表里
        sheet = setup.GRAPHICS['item_objects']
        for frame_rect in frame_rects:
            self.frames.append(tools.get_image(sheet,*frame_rect,(0,0,0),C.BG_MULTI))    #  *代表解包的意思，将列表中的xy宽高放进函数时会变成变量

    def update(self):
        self.current_time=pygame.time.get_ticks()   #获取当前时间
        frame_durations=[375,125,125,125]   #四种金币停留的时间

        if self.timer==0:    #如果为timer为0，调为当前时间
            self.timer=self.current_time
        elif self.current_time-self.timer >frame_durations[self.frame_index]:    #如果当前时间减去计时器的时间大于这个所在帧（金币图案）应有的时间，那么帧数+1
            self.frame_index+=1
            self.frame_index%=4
            self.timer=self.current_time      #每换一帧，将当前时间设置为计时器时间

        self.image=self.frames[self.frame_index]    #帧率在变，将图片更改为对应帧率的图片


