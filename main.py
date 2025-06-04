#游戏主入口
import pygame
from source import tools,setup
from source.state import main_menu,load_screen,level

def main():
    state_dict={       #将页面变成为字典
        'main_menu':main_menu.MainMenu(),   #初始化主菜单界面，初始化实例
        'load_screen':load_screen.LoadScreen(),
        'level':level.Level(),
        'game_over': load_screen.GameOver(),
        'win':load_screen.Gamewin()
    }
    game=tools.Game(state_dict,'main_menu')
    game.run()    #让这个游戏运行

if __name__=='__main__':
    main()
