#载入界面
from .. components import  info
import  pygame

class LoadScreen:
    def start(self,game_info):
        self.game_info=game_info
        self.finished=False
        self.next='level'
        self.duration=2000
        self.timer=0     #加载界面持续时长判断
        self.info=info.Info('load_screen',self.game_info)

    def update(self,surface,keys):
        self.draw(surface)
        if self.timer==0:      #如果时间为0，设置为当前时间
            self.timer=pygame.time.get_ticks()
        elif pygame.time.get_ticks()-self.timer>self.duration:     #如果当前时间超过时间段，则状态为真,该界面结束
            self.finished=True
            self.timer=0

    def draw(self,surface):
        surface.fill((0,0,0))
        self.info.draw(surface)

class GameOver(LoadScreen):
    def start(self,game_info):
        self.game_info=game_info
        self.finished=False
        self.next='main_menu'
        self.duration=4000
        self.timer=0
        self.info=info.Info('game_over',self.game_info)

class Gamewin(LoadScreen):
    def start(self,game_info):
        self.game_info=game_info
        self.finished=False
        self.next='main_menu'
        self.duration=4000
        self.timer=0
        self.info=info.Info('win',self.game_info)