import sys
import pygame as pg
from pygame.locals import *
from data.World import *

pg.init()

#Thông số màn hình
sc_width = 1000
sc_height = 700

#Số khung hình trên giây (Frame per second)
fps = 60

#FONT chữ và màu chữ
FONT = pg.font.SysFont("Sans", 20)
FONT_WIN = pg.font.SysFont("Sans", 100)
TEXT_COLOR = (0, 0, 0)

#Biến thời gian
start_time = None
clock = pg.time.Clock()

#Hiển thị lên màn hình
screen = pg.display.set_mode((sc_width, sc_height))
pg.display.set_caption('EXILE')

#Thông số trò chơi
tile_size = 50
end_game  = 0
level = 0
main_menu = True

#Load ảnh
background_img = pg.image.load('resources/graphics/enviroment/background.png')
restart_img = pg.image.load('resources/graphics/enviroment/restart_button.png')
start_img = pg.image.load('resources/graphics/enviroment/start_button.png')
exit_img = pg.image.load('resources/graphics/enviroment/exit_button.png')

class Player():
    def __init__(self, x, y):
        self.restart(x, y)
    
    def update(self, end_game):
        dx = 0
        dy = 0
        walk_cooldown = 20
        column_thresh = 20

        if end_game == 0:
            #Nhận phím bấm
            key = pg.key.get_pressed()
            if key[pg.K_SPACE] and self.jump == False and self.multi_jump == False:
                self.velocity_y = -16
                self.jump = True
                self.multi_jump = True
            if key[pg.K_SPACE] ==  False:
                self.jump = False
            # if self.jump == False:
            #     self.jump = True
            if key[pg.K_LEFT]:
                dx -= 3
                self.cout += 3
                self.direct = - 1
            if key[pg.K_RIGHT]:
                dx += 3
                self.cout += 3
                self.direct = 1
            if key[pg.K_LEFT] == False and key[pg.K_RIGHT] == False:
                self.cout = 0
                self.index = 0
                if self.direct == 1:
                    self.image = self.move_right[self.index]
                if self.direct == -1:
                    self.image = self.move_left[self.index]

            #Trọng lực
            self.velocity_y += 1
            if self.velocity_y > 10:
                self.velocity_y = 10
            dy += self.velocity_y
            
            
        #Xử lí va chạm
            self.multi_jump = True
            for tile in world.tile_list:
                #Kiểm tra va chạm theo trục x
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                #Kiểm tra va chạm theo trục y
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #check if below the ground i.e. jumping               
                    if self.velocity_y < 0:
                        # rectangle date lưu trữ tại index 1
                        # image lưu trữ tại index 0
                        dy = tile[1].bottom - self.rect.top
                        self.velocity_y = 0
                    #check if above the ground i.e. falling
                    elif self.velocity_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.velocity_y = 0
                        self.multi_jump = False

            
            # Xử lí va chạm với bẫy
            if pg.sprite.spritecollide(self, trap_group, False):
                self.velocity_y = 10
                end_game = -1

            #Xử lí va chạm với enemy
            if pg.sprite.spritecollide(self, enemy_group, False):
                self.velocity_y = 10
                end_game = -1

            #Xử lí va chạm với cửa
            if pg.sprite.spritecollide(self, hatch_group, False):
                end_game = 1

            #Xử lí va chạm với move_platform
            for platform in platform_group:
				#collision in the x direction
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
				#collision in the y direction
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below platform
                    if abs((self.rect.top + dy) - platform.rect.bottom) < column_thresh:
                        self.velocity_y = 0
                        dy = platform.rect.bottom - self.rect.top
					#check if above platform
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < column_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.multi_jump = False
                        dy = 0
					#move sideways with the platform
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction
        
                
            #Xử lí animation
            if self.cout > walk_cooldown:
                self.cout = 0
                self.index += 1
                if self.index >= len(self.move_right):
                    self.index = 0
                if self.direct == 1:
                    self.image = self.move_right[self.index]
                if self.direct == -1:
                    self.image = self.move_left[self.index]

            #Update chuyển động
            self.rect.x += dx
            self.rect.y += dy

            if self.rect.bottom > sc_height:
                self.rect.x = 10

        elif end_game == -1:
            self.image = self.ghost_img
            if self.rect.y > -100:
                self.rect.y -= 5

        #Vẽ nhân vật lên màn hình
        screen.blit(self.image, self.rect)
        # pg.draw.rect(screen,(255, 255, 255), self.rect, 2)

        return end_game


    def restart(self, x, y):
        self.move_right = []
        self.move_left = []
        self.index = 0
        self.cout = 0
        for i in range(0, 12):
            img_right = pg.image.load(f'resources/graphics/player/player_m_right_{i}.png')
            img_right = pg.transform.scale(img_right,(40, 80))
            img_left = pg.image.load(f'resources/graphics/player/player_m_left_{i}.png')
            img_left = pg.transform.scale(img_left,(40, 80))
            self.move_right.append(img_right)
            self.move_left.append(img_left)

        self.ghost_img = pg.image.load('resources/graphics/player/ghost_2.png')       
        self.image = self.move_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.velocity_y = 0
        self.jump = False
        self.direct = 0
        self.multi_jump = True

class World():
    def __init__(self, data):
   
        self.tile_list = []

        #Load ảnh
        dirt_img = pg.image.load('resources/graphics/enviroment/dirt.png')
        grass_img = pg.image.load('resources/graphics/enviroment/grass.png')

        row_count = 0
        for row in data:
            column_count = 0
            for tile in row:
                if tile == 1:
                    img = pg.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = column_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pg.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = column_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    enemy = Enemy_wolf_1(column_count * tile_size, row_count * tile_size + 12)
                    enemy_group.add(enemy)
                if tile == 7:
                    enemy = Enemy_wolf_2(column_count * tile_size, row_count * tile_size + 12)
                    enemy_group.add(enemy)
                if tile == 4:
                    trap = Trap(column_count * tile_size, row_count * tile_size)
                    trap_group.add(trap)
                if tile == 5:
                    hatch = Hatch(column_count * tile_size , row_count * tile_size)
                    hatch_group.add(hatch)
                if tile == 6:
                    platform = Platform(column_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 8:
                    platform = Platform(column_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                column_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            # pg.draw.rect(screen, (255, 255, 255), tile[1], 2)

class Platform(pg.sprite.Sprite):
	def __init__(self, x, y, move_x, move_y):
		pg.sprite.Sprite.__init__(self)
		img = pg.image.load('resources/graphics/enviroment/grass.png')
		self.image = pg.transform.scale(img, (tile_size, tile_size))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_counter = 0
		self.move_direction = 1
		self.move_x = move_x
		self.move_y = move_y

	def update(self):
		self.rect.x += self.move_direction * self.move_x
		self.rect.y += self.move_direction * self.move_y
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1


class Trap(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        img = pg.image.load('resources/graphics/enviroment/trap.png')
        self.image = pg.transform.scale(img,(tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Hatch(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        img = pg.image.load('resources/graphics/enviroment/hatch.png')
        self.image = pg.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy_wolf_1(pg.sprite.Sprite):  
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.wolf_move_right = []
        self.wolf_move_left = []
        self.index = 0

        for i in range(1, 7):
            img_right = pg.image.load(f'resources/graphics/Enemy/Wolf_sping/enemy_wolf_right_{i}.png')
            img_right = pg.transform.scale(img_right,(75, 38))
            img_left = pg.image.load(f'resources/graphics/Enemy/Wolf_sping/enemy_wolf_left_{i}.png')
            img_left = pg.transform.scale(img_left,(75, 38))
            self.wolf_move_right.append(img_right)
            self.wolf_move_left.append(img_left)
        self.image = self.wolf_move_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direct = 1
        self.move_count = 0
        
    def update(self):

        self.rect.x += self.move_direct
        
        self.move_count += 1       
        if self.move_count > 100:
            self.move_direct *= -1
            self.move_count  *= -1 

        if self.move_direct > 0:
            self.image = self.wolf_move_right[self.index]
        if self.move_direct < 0:
            self.image = self.wolf_move_left[self.index]
        
       
        self.index += 1
        if self.index >= len(self.wolf_move_right):
            self.index = 0

class Enemy_wolf_2(pg.sprite.Sprite):  
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.wolf_move_right = []
        self.wolf_move_left = []
        self.index = 0

        for i in range(1, 7):
            img_right = pg.image.load(f'resources/graphics/Enemy/Wolf_sping/enemy_wolf_right_{i}.png')
            img_right = pg.transform.scale(img_right,(75, 38))
            img_left = pg.image.load(f'resources/graphics/Enemy/Wolf_sping/enemy_wolf_left_{i}.png')
            img_left = pg.transform.scale(img_left,(75, 38))
            self.wolf_move_right.append(img_right)
            self.wolf_move_left.append(img_left)
        self.image = self.wolf_move_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direct = 1
        self.move_count = 0

    def update(self):

        self.rect.x += self.move_direct
        
        self.move_count += 1       
        if self.move_count > 75:
            self.move_direct *= -1
            self.move_count  = 0

        if self.move_direct > 0:
            self.image = self.wolf_move_right[self.index]
        if self.move_direct < 0:
            self.image = self.wolf_move_left[self.index]
        
       
        self.index += 1
        if self.index >= len(self.wolf_move_right):
            self.index = 0

class Button():
    def __init__(self, x, y, img):
        self.img = img
        self.rect = self.img.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        click = False

        #mouse click
        pos = pg.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pg.mouse.get_pressed()[0] == 1 and self.clicked == False:
                click = True
                self.clicked = True
        if pg.mouse.get_pressed()[0] == 0:
            self.clicked = False
        #draw
        screen.blit(self.img, self.rect)
        return click

player = Player(10, sc_height - 130)
trap_group = pg.sprite.Group()
platform_group = pg.sprite.Group()
hatch_group = pg.sprite.Group()
enemy_group = pg.sprite.Group()
fb_group = pg.sprite.Group()

world = World(world_data_2)

# Tạo button
restart_button = Button(sc_width //2 - 50, sc_height//2, restart_img )
start_button = Button(sc_width //2 - 100, sc_height//2 -200, start_img )
exit_button = Button(sc_width //2 - 100, sc_height//2 - 50, exit_img )

def time_over(end_time):
    time_played = (end_time - start_time)//1000
    return time_played

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

run = True
while run: 
    clock.tick(fps)

    screen.blit(background_img,(0,0))

    if main_menu == True:
        if start_button.draw():
            main_menu = False
            start_time = pg.time.get_ticks()
        if exit_button.draw():
            run = False

    else:
        world.draw()
        platform_group.draw(screen)
        hatch_group.draw(screen)
        trap_group.draw(screen)
        enemy_group.draw(screen)

        end_game = player.update(end_game)

        if end_game == 0:
            platform_group.update()
            enemy_group.update()

        if end_game == -1:
            start_time = False
            if restart_button.draw():
                player.restart(10, sc_height - 130)
                end_game = 0
                start_time = True
                start_time = pg.time.get_ticks()
        
        if end_game == 1:
            screen.blit(background_img,(0,0))
            draw_text("YOU WIN!", FONT_WIN, TEXT_COLOR, 330, 200)
            start_time = False
            if restart_button.draw():
                player.restart(10, sc_height - 130)
                end_game = 0
                start_time = True
                start_time = pg.time.get_ticks()
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.QUIT()
            sys.exit()
        if event.type == pg.KEYDOWN:
            if event.key == K_q:
                pg.QUIT()
                sys.exit()
    if start_time:
        end_time = pg.time.get_ticks()
        time_since_survived = (end_time - start_time)//1000
        message = 'TIME PLAYED: ' + str(time_since_survived)
        screen.blit(FONT.render(message, True, TEXT_COLOR), (20, 20))
    
    pg.display.update()
    