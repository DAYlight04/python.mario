#游戏部件--物品
import  pygame

class Item(pygame.sprite.Sprite):     #创建物品游戏部件且为精灵类
    def __init__(self,x,y,w,h,name):
        pygame.sprite.Sprite.__init__(self)   #用自身创建精灵类
        self.image=pygame.Surface((w,h)).convert()    #添加空图层，各自有一个宽高，方便做碰撞检测
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.name=name

class Checkpoint(Item):     #检查点类
    def __init__(self,x,y,w,h,checkpoint_type,enemy_groupid=None,name='checkpoint'):
        Item.__init__(self,x,y,w,h,name)
        self.checkpoint_type=checkpoint_type
        self.enemy_groupid=enemy_groupid