#关卡
from .. components import info
import pygame
from .. import tools,setup
from .. import constants as C
from .. components import  player,stuff,brick,box,enemy
import os
import json

class Level:
    def start(self,game_info):
        self.game_info=game_info
        self.finished=False
        self.next='game_over'
        self.info=info.Info('level',self.game_info)
        self.load_map_data()
        self.setup_background()
        self.setup_start_position()
        self.setup_player()
        self.setup_ground_items()
        self.setup_bricks_and_boxes()   #加载砖块和宝箱
        self.setup_enemies()          #设置敌人
        self.setup_checkpoints()     #设置检查点，当mario出现到某个位置是，怪物开始刷新

    def load_map_data(self):     #载入关卡信息
        file_name='level_1.json'
        file_path=os.path.join('source/data/maps',file_name)
        with open(file_path) as f:
            self.map_data=json.load(f)

    def setup_background(self):   #画面背景
        self.image_name=self.map_data['image_name']
        self.background=setup.GRAPHICS[self.image_name]
        rect=self.background.get_rect()
        self.background=pygame.transform.scale(self.background,(int(rect.width*C.BG_MULTI),
                                                                int(rect.height*C.BG_MULTI)))
        self.background_rect=self.background.get_rect()
        self.game_window=setup.SCREEN.get_rect()   #设置游戏窗口，滑动的游戏窗口 大小和屏幕一致
        self.game_ground=pygame.Surface((self.background_rect.width,self.background_rect.height))   #游戏场景大小和背景图一致

    def setup_start_position(self):   #设置初始位置,指定地图开始和结束的位置，玩家初始的x，y坐标
        self.position=[]
        for data in self.map_data['maps']:
            self.position.append((data['start_x'],data['end_x'],data['player_x'],data['player_y']))
        self.start_x,self.end_x,self.player_x,self.player_y=self.position[0]

    def setup_player(self):   #把玩家初始化
        self.player=player.Player('mario')   #
        self.player.rect.x=self.game_window.x+self.player_x     #palyer_x指的是玩家相对窗口的位置
        self.player.rect.bottom=self.player_y     #y指的是玩家脚的位置

    def setup_ground_items(self):     #设置地面物品
        self.ground_items_group=pygame.sprite.Group()   #pygame里面的精灵组，可以存放多个精灵
        for name in ['ground','pipe','step']:   #读取json文件，读出每个物件的坐标和大小，并用item类实例
            for item in self.map_data[name]:
                self.ground_items_group.add(stuff.Item(item['x'],item['y'],item['width'],item['height'],name))

    def setup_bricks_and_boxes(self):   #加载砖块和宝箱
        self.brick_group=pygame.sprite.Group()   #砖块组
        self.box_group=pygame.sprite.Group()   #宝箱组
        self.coin_group=pygame.sprite.Group()    #开出的金币组
        self.powerup_group=pygame.sprite.Group()     #开出的强化组

        if 'brick' in self.map_data:    #如果砖块在json文件里，遍历每一行得到x，y
            for brick_data in self.map_data['brick']:
                x,y=brick_data['x'],brick_data['y']
                brick_type=brick_data['type']
                if brick_type==0:
                    if 'brick_num' in brick_data:    #如果有num，说明在水下世界
                        # TODO batch bricks
                        pass
                    else:
                        self.brick_group.add(brick.Brick(x,y,brick_type,None))   #如果不在水下世界，作为精灵加入
                elif brick_type==1:
                    self.brick_group.add(brick.Brick(x,y,brick_type,self.coin_group))
                else:
                    self.brick_group.add(brick.Brick(x,y,brick_type,self.powerup_group))

        if 'box' in self.map_data:  # 如果砖块在json文件里，遍历每一行得到x，y
            for box_data in self.map_data['box']:
                x, y = box_data['x'], box_data['y']
                box_type = box_data['type']
                if box_type==1:
                    self.box_group.add(box.Box(x, y, box_type,self.coin_group))  # 如果不在水下世界，作为精灵加入
                else:
                    self.box_group.add(box.Box(x,y,box_type,self.powerup_group))

    def setup_enemies(self):      #设置敌人
        self.dying_group=pygame.sprite.Group()    #死亡组类
        self.shell_group=pygame.sprite.Group()
        self.enemy_group=pygame.sprite.Group()
        self.enemy_group_dict={}    #用字典存放敌人
        for enemy_group_data in self.map_data['enemy']:    #放入野怪
            group=pygame.sprite.Group()
            for enemy_group_id,enemy_list in enemy_group_data.items():
                for enemy_data in enemy_list:
                    group.add(enemy.create_enemy(enemy_data))
                self.enemy_group_dict[enemy_group_id]=group

    def setup_checkpoints(self):    #设置检查点，当mario到某个位置时怪物开始刷新
        self.checkpoint_group=pygame.sprite.Group()
        for item in self.map_data['checkpoint']:
            x,y,w,h=item['x'],item['y'],item['width'],item['height']
            checkpoint_type=item['type']
            enemy_groupid=item.get('enemy_groupid')
            self.checkpoint_group.add(stuff.Checkpoint(x,y,w,h,checkpoint_type,enemy_groupid))    #通过stuff的检查点类实例化


    def update(self,surface,keys):
        self.current_time=pygame.time.get_ticks()
        self.player.update(keys)
        if self.player.dead:
            if self.current_time-self.player.death_timer>3000:
                self.finished=True   #结束当前游戏阶段
                self.update_game_info()   #死亡后信息更新
        elif self.is_frozen():
            pass
        elif self.player.success:
            if self.current_time-self.player.success_timer>2000:
                self.finished=True
        else:
            self.update_player_position()
            self.check_checkpoints()
            self.check_if_go_die()   #检查是否死亡
            self.check_if_go_success()    #检测是否成功
            self.update_game_window()   #更新游戏窗口
            self.info.update()    #x信息更新
            self.brick_group.update()
            self.box_group.update()
            self.enemy_group.update(self)
            self.dying_group.update(self)
            self.shell_group.update(self)
            self.coin_group.update()
            self.powerup_group.update(self)
        self.draw(surface)

    def is_frozen(self):    #判断场景是否冻结（变身过程中其他场景不变
        return self.player.state in ['small to big',['big to small'],['big to fire'],['fire to small']]

    def update_player_position(self):    #玩家 角色位置更新
        #x dicition
        self.player.rect.x+=self.player.x_vel
        if self.player.rect.x<self.start_x:   #防止玛丽不跑到屏幕外，也不能走回头
           self.player.rect.x=self.start_x
        elif self.player.rect.right>self.end_x:    # #防止马里奥超过地图的末尾，
            self.player.rect.right=self.end_x
        self.check_x_collision()   #水平方向碰撞检测

        #y dicition
        if not self.player.dead:    #如果死亡，不用再进行y方向的碰撞检测
            self.player.rect.y+=self.player.y_vel
            self.check_y_collision()

    def check_x_collision(self):
        check_group=pygame.sprite.Group(self.ground_items_group,self.brick_group,self.box_group)
        collided_sprite=pygame.sprite.spritecollideany(self.player,check_group)    #检查一个精灵是否与精灵组里的任意另一个精灵 有碰撞,有则返回物体
        if collided_sprite:
            self.adjust_player_x(collided_sprite)  #如果碰撞，给其马里奥位置调整
        if self.player.hurt_immune:
            return

        enemy = pygame.sprite.spritecollideany(self.player, self.enemy_group)  # 如果撞到敌人，敌人die
        if enemy:
            if self.player.big:    #如果角色为大
                self.player.state='big2small'
                self.player.hurt_immune=True  #伤害免疫
            else:
                self.player.go_die()

        shell=pygame.sprite.spritecollideany(self.player, self.shell_group)
        if shell:
            if shell.state=='slide':
                self.player.go_die()
            else:
                if self.player.rect.x<shell.rect.x:
                    shell.x_vel=10
                    shell.rect.x+=40
                    shell.direction=1
                else:
                    shell.x_vel=-10
                    shell.rect.x-=40
                    shell.direction=0
                shell.state='slide'   #滑行

        powerup=pygame.sprite.spritecollideany(self.player,self.powerup_group)    #如果碰到强化类
        if powerup:
            powerup.kill()
            if powerup.name=='mushroom':
                self.player.state='small to big'

    def check_y_collision(self):    #y方向碰撞检测
        group_item=pygame.sprite.spritecollideany(self.player,self.ground_items_group)   #地面上的物品碰撞检测
        brick=pygame.sprite.spritecollideany(self.player,self.brick_group)      #砖块碰撞检测
        box=pygame.sprite.spritecollideany(self.player,self.box_group)     #宝箱碰撞检测
        enemy = pygame.sprite.spritecollideany(self.player, self.enemy_group)  # 如果撞到敌人，敌人die,敌人碰撞检测
        if brick and box:    #距离判断，看mario里砖块更近还是宝箱
            to_brick=abs(self.player.rect.centerx-brick.rect.centerx)
            to_box=abs(self.player.rect.centerx-box.rect.centerx)
            if to_brick>to_box:
                brick=None
            else:
                box=None
        if group_item:
            self.adjust_player_y(group_item)    #调整
        elif brick:
            self.adjust_player_y(brick)
        elif box:
            self.adjust_player_y(box)
        elif enemy:
            if self.player.hurt_immune:
                return
            self.enemy_group.remove(enemy)
            if enemy.name=='koopa':
                self.shell_group.add(enemy)  #如果是乌龟
            else:
                self.dying_group.add(enemy)
            if self.player.y_vel<0:    #敌人死法
                how='bumped'     #从下往上顶
            else:
                how='trampled'     #从上往下踩
                self.player.state='jump'    #踩到后mario会跳起来
                self.player.rect.bottom=enemy.rect.top
                self.player.y_vel=self.player.jump_vel*0.8

            enemy.go_die(how,1 if self.player.face_right else -1)
        self.check_will_fall(self.player)

    def adjust_player_x(self,sprite):   #调整马里奥
        if self.player.rect.x<sprite.rect.x:    #判断碰撞方向
            self.player.rect.right=sprite.rect.left
        else:
            self.player.rect.left=sprite.rect.right
        self.player.x_vel=0

    def adjust_player_y(self,sprite):
        if self.player.rect.bottom<sprite.rect.bottom:    #从上往下撞
            self.player.y_vel=0     #反弹速度
            self.player.rect.bottom=sprite.rect.top
            self.player.state='walk'
        else:   #从下往上撞
            self.player.y_vel=7    #
            self.player.rect.top = sprite.rect.bottom
            self.player.state='fall'

            self.is_enemy_on(sprite)   #判断敌人是否在上面

            if sprite.name=='box':
                if sprite.state=='rest':
                    sprite.go_bumped()
            if sprite.name=='brick':
                if self.player.big and sprite.brick_type==0:   #Mario为变大状态且砖块为空
                    sprite.smashed(self.dying_group)    #砖块能被顶碎
                else:
                    sprite.go_bumped()

    def is_enemy_on(self,sprite):
        sprite.rect.y-=2
        enemy=pygame.sprite.spritecollideany(sprite,self.enemy_group)
        if enemy:
            self.enemy_group.remove(enemy)
            self.dying_group.add(enemy)
            if sprite.rect.centerx>enemy.rect.centerx:
                enemy.go_die('bumped',-1)
            else:
                enemy.go_die('bumped',1)
        sprite.rect.y+=2

    def check_will_fall(self,sprite):    #降落检查
        sprite.rect.y+=1     #判断下面是否还有可以掉的空间，看其是否还有下落的空间
        check_group=pygame.sprite.Group(self.ground_items_group,self.brick_group,self.box_group)
        collided_sprite=pygame.sprite.spritecollideany(sprite,check_group)
        if not collided_sprite and sprite.state!='jump' and not self.is_frozen():
            sprite.state='fall'
        sprite.rect.y-=1

    def update_game_window(self):   #游戏窗口更新代码
        third=self.game_window.x+self.game_window.width/3  #计算窗口的三分之一
        if self.player.x_vel>0 and self.player.rect.centerx>third and self.game_window.right<self.end_x:   #如果马里奥位置超出三分之一,且游戏窗口不能超过地图的末尾
            self.game_window.x+=self.player.x_vel     #用窗口滑动代替主角的移动
            self.start_x=self.game_window.x

    def draw(self,surface):
        #blit方法是将目标图层的特定部分画到原图层的指定位置，第一个参数为目标图层，第三个参数为特定部分，第二个参数为目标图层的左上角
        self.game_ground.blit(self.background,self.game_window,self.game_window)   #把背景和人物绘制到gameground中
        self.game_ground.blit(self.player.image,self.player.rect)
        self.powerup_group.draw(self.game_ground)
        self.brick_group.draw(self.game_ground)
        self.box_group.draw(self.game_ground)
        self.enemy_group.draw(self.game_ground)
        self.dying_group.draw(self.game_ground)
        self.shell_group.draw(self.game_ground)
        self.coin_group.draw(self.game_ground)

        surface.blit(self.game_ground,(0,0),self.game_window)   #将game_ground渲染到屏幕
        self.info.draw(surface)

    def check_checkpoints(self):    #检查一下每一个检查点
        checkpoint=pygame.sprite.spritecollideany(self.player,self.checkpoint_group)    #如果检查点被碰到了
        if checkpoint:
            if checkpoint.checkpoint_type==0:     #并且检查点的类型为0，释放对应的野怪
                self.enemy_group.add(self.enemy_group_dict[str(checkpoint.enemy_groupid)])
            checkpoint.kill()   #如果检查点被触碰过了，检查点消失
    def check_if_go_die(self):
        if self.player.rect.y>C.SCREEN_H:
            self.player.go_die()

    def check_if_go_success(self):
        if self.player.rect.x>3274*C.BG_MULTI:
            self.player.go_success()
            self.next='win'


    def update_game_info(self):
        if self.player.dead:    #如果死亡
            self.game_info['lives']-=1
        if self.game_info['lives']==0:
            self.next='game_over'
        else:
            self.next='load_screen'