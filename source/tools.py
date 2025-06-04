#工具代码
import pygame
import random
import os

class Game:
    def __init__(self,state_dict,start_state):   #初始化游戏,且将传入的参数保存
        pygame.init()
        pygame.display.set_mode((800,600))   #设置屏幕大小
        self.screen=pygame.display.get_surface()   #h获得屏幕
        self.clock=pygame.time.Clock()
        self.keys=pygame.key.get_pressed()
        self.state_dict=state_dict
        self.state=self.state_dict[start_state]

    def update(self):    #单独的更新方法
        if self.state.finished:     #判断当前阶段是否结束
            game_info=self.state.game_info
            next_state=self.state.next
            self.state.finished=False
            self.state=self.state_dict[next_state]
            self.state.start(game_info)
        self.state.update(self.screen,self.keys)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.display.quit()
                    quit()
                elif event.type==pygame.KEYDOWN:
                    self.keys=pygame.key.get_pressed()
                elif event.type==pygame.KEYUP:
                    self.keys=pygame.key.get_pressed()

            self.update()

            pygame.display.update()
            self.clock.tick(60)  #控制游戏的帧数率，代表每秒钟60帧

def load_graphics(path,accept=('.jpg','.png','bmp','.gif')):    #加载图片，一次加载所有图片到一个字典里，第一个为文件的路径，第二个为接收文件的后缀
    graphics={}    #图片空字典
    for pic in os.listdir(path):    #遍历文件夹
        name,ext=os.path.splitext(pic)    #分拆文件，拆成文件名和后缀两部分
        if ext.lower() in accept:
            img=pygame.image.load(os.path.join(path,pic))   #载入图片
            if img.get_alpha():    #如果图片是带有透明底的，转化成标准的，否则转化成普通的图片
                img=img.convert_alpha()
            else:
                img=img.convert()
        graphics[name]=img   #将其放到字典里
    return graphics

def get_image(sheet,x,y,width,height,colorkey,scale):    #从加载好的 图片里获取某些图片，传入图片的左上角坐标和图片方框的长宽，colorkey快速抠图的底色，scale是放大倍数
    image=pygame.Surface((width,height))   #创建和方框一样的空图层
    image.blit(sheet,(0,0),(x,y,width,height))  #0,0代表画到哪个v位置，x，y，w，h代表sheet里哪个区域要取出来，用blit方法往自己画图，图片来自传入的sheet
    image.set_colorkey(colorkey)  #对底色快速抠图
    image=pygame.transform.scale(image,(int(width*scale),int(height*scale)))  #放大图片
    return image

