#游戏主菜单
import pygame
from .. import setup
from .. import tools
from .. import constants as C
from .. components import info

class MainMenu:
    def __init__(self):
        game_info={   #游戏初始信息
            'score':0,
            'coin':0,
            'lives':3,
            'player_state':'small'
        }
        self.start(game_info)
    def start(self,game_info):    #使其能被反复调用，实现该状态的重置效果,game_info上一个阶段传过来的游戏信息
        self.game_info=game_info
        self.setup_background()   #设置底图
        self.setup_player()     #设置玩家
        self.setup_cursor()        #设置光标
        self.info=info.Info('main_menu',self.game_info)
        self.finished=False
        self.next='load_screen'    #加载界面

    def setup_background(self):
        self.background=setup.GRAPHICS['level_1']    #获得图片
        self.background_rect=self.background.get_rect()   #获得方框
        self.background=pygame.transform.scale(self.background,(int(self.background_rect.width*C.BG_MULTI),
                                                                int(self.background_rect.height*C.BG_MULTI)))     #放大到屏幕
        self.viewport=setup.SCREEN.get_rect()    #设置滑动窗口
        self.caption=tools.get_image(setup.GRAPHICS['title_screen'],1,60,176,88,(255,0,220),C.BG_MULTI)


    def setup_player(self):
        self.player_image=tools.get_image(setup.GRAPHICS['mario_bros'],178,32,12,16,(0,0,0),C.PLAYER_MULTI)

    def setup_cursor(self):
        self.cursor=pygame.sprite.Sprite()   #将小蘑菇光标变成精灵
        self.cursor.image=tools.get_image(setup.GRAPHICS['item_objects'],24,160,8,8,(0,0,0),C.PLAYER_MULTI)
        rect=self.cursor.image.get_rect()      #光标图标的位置
        rect.x,rect.y=(320,360)
        self.cursor.rect=rect
        self.cursor.state='START'  #初始状态,状态机

    def update_cursor(self,keys): #更新蘑菇光标，获得键盘的按键并作出判断
        if keys[pygame.K_UP]:
            self.cursor.state='START'
            self.cursor.rect.y=360
        elif keys[pygame.K_DOWN]:
            self.cursor.state='EXIT'
            self.cursor.rect.y=405
        elif keys[pygame.K_RETURN]:
            self.reset_game_info()  #游戏信息重置
            if self.cursor.state=='START':
                self.finished=True     #代表这个阶段已经完结
            elif self.cursor.state=='EXIT':
                self.finished=True
                quit()

    def update(self,surface,keys):      #更新绘画

        self.update_cursor(keys)

        surface.blit(self.background,self.viewport)
        surface.blit(self.caption,(170,100))   #将图片caption放在170，100的位置
        surface.blit(self.player_image,(110,490))
        surface.blit(self.cursor.image,self.cursor.rect)

        self.info.update()
        self.info.draw(surface)

    def reset_game_info(self):
        self.game_info.update({
            'score':0,
            'coin':0,
            'lives':3,
            'player_state':'small'
        })