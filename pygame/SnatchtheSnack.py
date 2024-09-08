import pygame, sys, random

class Block(pygame.sprite.Sprite):
    def __init__(self,path,x_pos,y_pos):
        super().__init__()
        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect(center = (x_pos,y_pos))

class Rabbit(Block):  # Was Player
    def __init__(self,path,x_pos,y_pos,speed):
        super().__init__(path,x_pos,y_pos)
        self.speed = speed
        self.movement = 0

    def screen_constrain(self):
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= screen_height:
            self.rect.bottom = screen_height

    def update(self,carrot_group):
        self.rect.y += self.movement
        self.screen_constrain()

class Carrot(Block):  # Was Ball
    def __init__(self,path,x_pos,y_pos,speed_x,speed_y,rabbits):
        super().__init__(path,x_pos,y_pos)
        self.speed_x = speed_x * random.choice((-1,1))
        self.speed_y = speed_y * random.choice((-1,1))
        self.rabbits = rabbits
        self.active = False
        self.score_time = 0

    def update(self):
        if self.active:
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            self.collisions()
        else:
            self.restart_counter()

    def collisions(self):
        
        if self.rect.top <= 0 or self.rect.bottom >= screen_height:
            pygame.mixer.Sound.play(plob_sound)
            self.speed_y *= -1
            print("Carrot hit top or bottom wall")

        if pygame.sprite.spritecollide(self,self.rabbits,False):
            pygame.mixer.Sound.play(plob_sound)  
            collision_rabbit = pygame.sprite.spritecollide(self,self.rabbits,False)[0].rect
            
            if abs(self.rect.right - collision_rabbit.left) < 10 and self.speed_x > 0:
                self.speed_x *= -1
            if abs(self.rect.left - collision_rabbit.right) < 10 and self.speed_x < 0:
                self.speed_x *= -1
            if abs(self.rect.top - collision_rabbit.bottom) < 10 and self.speed_y < 0:
                self.rect.top = collision_rabbit.bottom
                self.speed_y *= -1
            if abs(self.rect.bottom - collision_rabbit.top) < 10 and self.speed_y > 0:
                self.rect.bottom = collision_rabbit.top
                self.speed_y *= -1

    def reset_carrot(self):  # renamed from reset_ball
        self.active = False
        self.speed_x *= random.choice((-1,1))
        self.speed_y *= random.choice((-1,1))
        self.score_time = pygame.time.get_ticks()
        self.rect.center = (screen_width/2, screen_height/2)
        pygame.mixer.Sound.play(score_sound)

    def restart_counter(self):
        current_time = pygame.time.get_ticks()
        countdown_number = 3

        if current_time - self.score_time <= 700:
            countdown_number = 3
        if 700 < current_time - self.score_time <= 1400:
            countdown_number = 2
        if 1400 < current_time - self.score_time <= 2100:
            countdown_number = 1
        if current_time - self.score_time >= 2100:
            self.active = True

        time_counter = basic_font.render(str(countdown_number),True,accent_color)
        time_counter_rect = time_counter.get_rect(center=(screen_width/2, screen_height/2 + 50))
        pygame.draw.rect(screen,bg_color,time_counter_rect)
        screen.blit(time_counter,time_counter_rect)
        
class OpponentRabbit(Block):  # Was Opponent
    def __init__(self,path,x_pos,y_pos,speed):
        super().__init__(path,x_pos,y_pos)
        self.speed = speed

    def update(self,carrot_group):
        if self.rect.top < carrot_group.sprite.rect.y:
            self.rect.y += self.speed
        if self.rect.bottom > carrot_group.sprite.rect.y:
            self.rect.y -= self.speed
        self.constrain()
    
    def constrain(self):
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= screen_height:
            self.rect.bottom = screen_height

class GameManager:
    def __init__(self,carrot_group,rabbit_group):
        self.player_score = 0
        self.opponent_score = 0
        self.carrot_group = carrot_group
        self.rabbit_group = rabbit_group

    def run_game(self):
        # Drawing the game objects
        self.rabbit_group.draw(screen)
        self.carrot_group.draw(screen)

        # Updating the game objects
        self.rabbit_group.update(self.carrot_group)
        self.carrot_group.update()
        self.reset_carrot()
        self.draw_score()

    def reset_carrot(self):
        if self.carrot_group.sprite.rect.right >= screen_width:
            self.opponent_score += 1
            self.carrot_group.sprite.reset_carrot()
        if self.carrot_group.sprite.rect.left <= 0:
            self.player_score += 1
            self.carrot_group.sprite.reset_carrot()

    def draw_score(self):
        player_score = basic_font.render(str(self.player_score),True,accent_color)
        opponent_score = basic_font.render(str(self.opponent_score),True,accent_color)

        player_score_rect = player_score.get_rect(midleft = (screen_width / 2 + 40,screen_height/2))
        opponent_score_rect = opponent_score.get_rect(midright = (screen_width / 2 - 40,screen_height/2))

        screen.blit(player_score,player_score_rect)
        screen.blit(opponent_score,opponent_score_rect)


# General setup
pygame.mixer.pre_init(44100,-16,2,512)
pygame.init()
clock = pygame.time.Clock()

# Main Window
screen_width = 1280
screen_height = 960
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Rabbit & Carrot Game')

# Global Variables
bg_color = pygame.Color('lightblue3')

accent_color = (27,35,43)
basic_font = pygame.font.Font('freesansbold.ttf', 32)
plob_sound = pygame.mixer.Sound("pong.ogg")
score_sound = pygame.mixer.Sound("score.ogg")
middle_strip = pygame.Rect(screen_width/2 - 2,0,4,screen_height)

# Game objects
player = Rabbit('Rabbit.png',screen_width -40,screen_height//2,5)
opponent = OpponentRabbit('Rabbit.png',40,screen_height//2,5)
rabbit_group = pygame.sprite.Group()
rabbit_group.add(player)
rabbit_group.add(opponent)

carrot = Carrot('veggie.png',screen_width//2,screen_height//2,4,4,rabbit_group)
carrot_sprite = pygame.sprite.GroupSingle()
carrot_sprite.add(carrot)

game_manager = GameManager(carrot_sprite,rabbit_group)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player.movement -= player.speed
            if event.key == pygame.K_DOWN:
                player.movement += player.speed
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                player.movement += player.speed
            if event.key == pygame.K_DOWN:
                player.movement -= player.speed
    
    # Background Stuff
    screen.fill(bg_color)
    pygame.draw.rect(screen,accent_color,middle_strip)
    # pygame.draw.rect(screen,(255,0,0),self.rect,2)
    
    # Run the game
    game_manager.run_game()

    # Rendering
    pygame.display.flip()
    clock.tick(120)