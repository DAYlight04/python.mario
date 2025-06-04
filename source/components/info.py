#游戏信息
import pygame
from .. import constants as C
from . import coin
from .. import  setup,tools
pygame.font.init()

class Info():
    def __init__(self,state,game_info):   #state为阶段，展现游戏不同阶段的信息
        self.state=state
        self.game_info=game_info
        self.create_state_labels()    #创造某个阶段特有的文字
        self.create_info_labels()     #创造通用的信息
        self.flash_coin=coin.FlashingCoin()


    def create_state_labels(self):
        self.state_labels = []     #创建一个列表
        if self.state == 'main_menu':    #条件判断一下，按照不同游戏阶段往列表里面添加不同的文字
            self.state_labels.append((self.create_label('START'),(360,360)))    #前面为文字，后面为位置
            self.state_labels.append((self.create_label('EXIT'), (360, 405)))
        elif self.state=='load_screen':
            self.state_labels.append((self.create_label('WORLD'),(280,200)))
            self.state_labels.append((self.create_label('1 - 1'), (430, 200)))
            self.state_labels.append((self.create_label('X    {}'.format(self.game_info['lives'])), (380,280)))
            self.state_labels.append((self.create_label('Loading...'), (300, 400)))
            self.player_image=tools.get_image(setup.GRAPHICS['mario_bros'],178,32,12,16,(0,0,0),C.BG_MULTI)
        elif self.state == 'game_over':
            self.state_labels.append((self.create_label('GAME OVER'), (280, 300)))
        elif self.state == 'win':
            self.state_labels.append((self.create_label('GAME WIN'), (280, 300)))

    def create_info_labels(self):
        self.info_labels = []
        self.info_labels.append((self.create_label('MARIO'), (130,45)))
        self.info_labels.append((self.create_label('WORLD'), (450,30)))
        self.info_labels.append((self.create_label('1 - 1'), (480,55)))

    def create_label(self,label,size=40,width_scale=1.25,height_scale=1):    #把文字渲染成一张图片，返回
        font=pygame.font.SysFont(C.FONT,size)    #新建一个 字体
        label_image=font.render(label,1,(255,255,255))    #将文字渲染成图片,1代表是否抗锯齿，后面三个文字表示设置成白色
        rect=label_image.get_rect()     #将字体变小产生图片
        label_image=pygame.transform.scale(label_image,(int(rect.width*width_scale),
                                                        int(rect.height*height_scale)))  #将字体放大产生锯齿效果
        return label_image

    def update(self):    #更新，在游戏时实时更新分数
        self.flash_coin.update()

    def draw(self,surface):   #传入图层，在后面往图层里面放文字
        for label in self.state_labels:   #遍历链表
            surface.blit(label[0],label[1])    #用blit绘制，0代表图片，1代表位置
        for label in self.info_labels:
            surface.blit(label[0], label[1])
        surface.blit(self.flash_coin.image,self.flash_coin.rect)

        if self.state=='load_screen':
            surface.blit(self.player_image,(300,270))