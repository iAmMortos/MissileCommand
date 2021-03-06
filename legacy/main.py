import pygame
import sys
import random

from missileLEGACY import Missile
from explosionLEGACY import Explosion
from launcher import Launcher
import math 


pygame.init()
pygame.mouse.set_cursor(*pygame.cursors.diamond)

# INFO = pygame.display.Info()
# WIDTH = int(INFO.current_h * 0.5)
# HEIGHT = int(INFO.current_h * 0.5)
WIDTH = 480
HEIGHT = 480

GROUND_HEIGHT = int(HEIGHT / 15)
SHELTER_HEIGHT = int(HEIGHT / 10)

s = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Missile Command')
clock = pygame.time.Clock()

level = 0

half = WIDTH/18
shelter_positions = [WIDTH/9 - half, 2*WIDTH/9 - half, 3*WIDTH/9 - half, 4*WIDTH/9 - half, 5*WIDTH/9 - half,
                     6*WIDTH/9 - half, 7*WIDTH/9 - half, 8*WIDTH/9 - half, 9*WIDTH/9 - half]

enemy_missiles = []
points = 0
player_missiles = []
explosion_list = []
shelter = [True, True, True, True, True, True]
launcher_list = [Launcher(0), Launcher(1), Launcher(2)]
launcher_positions = [WIDTH/9 - half, 5*WIDTH/9 - half, 9*WIDTH/9 - half]
keys_down = [False, False, False]

# colors_list = [pygame.Color(0, 255, 0), pygame.Color(255, 0, 0), pygame.Color(255, 255, 0),
#                pygame.Color(0, 255, 255), pygame.Color(255, 0, 255), pygame.Color(255, 255, 255),
#                pygame.Color(0, 0, 255)]

ENEMY_MISSILE_COLOR = pygame.Color(255, 0, 0)
ENEMY_MISSILE_TRAIL_COLOR = pygame.Color(127, 0, 0)
FRIENDLY_MISSILE_COLOR = pygame.Color(0, 255, 0)
FRIENDLY_MISSILE_TRAIL_COLOR = pygame.Color(0, 127, 0)
EXPLOSION_COLOR = pygame.Color(255, 0, 255)


def draw():
    s.fill((0, 0, 0))
    pygame.draw.rect(s, pygame.Color(255, 255, 0), (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))

    # LAUNCHERS
    for ss in range(len(launcher_list)):
        pygame.draw.polygon(s, pygame.Color(255, 255, 0),
                            [(ss * WIDTH / 2 - SHELTER_HEIGHT/2 + GROUND_HEIGHT - (GROUND_HEIGHT * ss), HEIGHT - SHELTER_HEIGHT),
                             (ss * WIDTH / 2 + SHELTER_HEIGHT/2 + GROUND_HEIGHT - (GROUND_HEIGHT * ss), HEIGHT - SHELTER_HEIGHT),
                             (ss * WIDTH / 2 + SHELTER_HEIGHT + GROUND_HEIGHT - (GROUND_HEIGHT * ss), HEIGHT),
                             (ss * WIDTH / 2 - SHELTER_HEIGHT + GROUND_HEIGHT - (GROUND_HEIGHT * ss), HEIGHT)])
        counter = launcher_list[ss].ammo
        number = 1
        while counter > 0:
            for j in range(number):
                pygame.draw.ellipse(s, (0, 0, 255),
                                    (launcher_positions[ss] - ((number - 2 * j) * WIDTH/100) + WIDTH/200,
                                     HEIGHT - SHELTER_HEIGHT + ((number-1) * WIDTH/100),
                                     WIDTH/100,
                                     WIDTH/100))
                counter = counter-1
                if counter == 0:
                    break
            number = number+1

    # SHELTERS
    launcher_pos = 1
    for i in range(len(shelter)):
        if shelter[i]:
            pygame.draw.rect(s, pygame.Color(0, 0, 255), ((i+launcher_pos) * WIDTH/9 + SHELTER_HEIGHT/4, HEIGHT - GROUND_HEIGHT*1.2, SHELTER_HEIGHT/2, SHELTER_HEIGHT/3))
        if (i + 1) % 3 == 0:
            launcher_pos = launcher_pos+1

    # PLAYER MISSILES
    for p in player_missiles:
        pygame.draw.line(s, FRIENDLY_MISSILE_TRAIL_COLOR, (p.start_x, p.start_y), (p.current_x, p.current_y), 1)
        pygame.draw.ellipse(s, FRIENDLY_MISSILE_COLOR, (p.current_x-1.5, p.current_y-1.5, 4, 4), 0)
        col = FRIENDLY_MISSILE_COLOR
        pygame.draw.line(s, col, (p.end_x-5, p.end_y-5),
                         (p.end_x+5, p.end_y+5), 1)
        pygame.draw.line(s, col, (p.end_x+5, p.end_y-5),
                         (p.end_x-5, p.end_y+5), 1)
        p.move()

    # ENEMY MISSILES
    for p in enemy_missiles:
        pygame.draw.line(s, ENEMY_MISSILE_TRAIL_COLOR, (p.start_x, p.start_y), (p.current_x, p.current_y), 1)
        pygame.draw.ellipse(s, ENEMY_MISSILE_COLOR, (p.current_x-1.5, p.current_y-1.5, 4, 4), 0)

        p.move()

    # EXPLOSIONS
    for w in explosion_list:
        if w.expires:
            w.frame -= 2
            if w.frame == 0:
                explosion_list.remove(w)
                del w
                continue
        elif w.frame == 1500:
            w.expires = True
        else:
            w.frame += 1
        pygame.draw.ellipse(s, EXPLOSION_COLOR, (w.poz_x-w.frame/60, w.poz_y-w.frame/60, w.frame/30, w.frame/30), 0)
        
    pygame.display.update()


def designate_launcher(x, y):
    minimum_x = 10
    y1 = HEIGHT - 50
    dy = y-y1
    minimum = 100000
    if launcher_list[0].ammo > 0:
        x1 = launcher_positions[0]
        dx = x1-x
        temp = math.sqrt(dx*dx + dy*dy)
        if temp < minimum:
            minimum = temp
            minimum_x = x1
    if launcher_list[1].ammo > 0:
        x1 = launcher_positions[1]
        dx = x1-x
        temp = math.sqrt(dx*dx + dy*dy)
        if temp < minimum:
            minimum = temp
            minimum_x = x1
    if launcher_list[2].ammo > 0:
        x1 = launcher_positions[2]
        dx = x1-x
        temp = math.sqrt(dx*dx + dy*dy)
        if temp < minimum:
            minimum = temp
            minimum_x = x1
    return minimum_x


def launch_rocket(x, y, launcher=None):
    if y > HEIGHT-SHELTER_HEIGHT*1.4:
        return

    if launcher is not None:
        launcher_position = launcher_positions[launcher]
    else:
        launcher_position = designate_launcher(x, y)

    if launcher_position == launcher_positions[0] and launcher_list[0].ammo > 0:
        launcher_list[0].ammo -= 1
    elif launcher_position == launcher_positions[1] and launcher_list[1].ammo > 0:
        launcher_list[1].ammo -= 1
    elif launcher_position == launcher_positions[2] and launcher_list[2].ammo > 0:
        launcher_list[2].ammo -= 1
    else:
        return

    player_missiles.append(Missile(launcher_position, HEIGHT - SHELTER_HEIGHT, x, y, 0.2, 0))


def middle_point(x, y, wx, wy, r):
    p = ((math.pow((x - wx), 2) // math.pow(r+1, 2)) + 
         (math.pow((y - wy), 2) // math.pow(r+1, 2))) 
  
    return p


def collision():
    for p in player_missiles:
        if p.current_y-p.end_y < 0.1:
            temp = Explosion(p.current_x, p.current_y)
            explosion_list.append(temp)
            player_missiles.remove(p)
            del p
            continue
        
        for w in explosion_list:
            if middle_point(p.current_x, p.current_y, w.poz_x, w.poz_y, w.frame / 60) < 1:
                temp = Explosion(p.current_x, p.current_y)
                explosion_list.append(temp)
                player_missiles.remove(p)
                del p
                break

    for p in enemy_missiles:
        if p.current_y-p.end_y > -0.1:
            temp = Explosion(p.current_x, p.current_y)
            explosion_list.append(temp)
            if p.end_x == shelter_positions[0]:
                launcher_list[0].ammo = 0
            elif p.end_x == shelter_positions[1]:
                shelter[0] = False
            elif p.end_x == shelter_positions[2]:
                shelter[1] = False
            elif p.end_x == shelter_positions[3]:
                shelter[2] = False
            elif p.end_x == shelter_positions[4]:
                launcher_list[1].ammo = 0
            elif p.end_x == shelter_positions[5]:
                shelter[3] = False
            elif p.end_x == shelter_positions[6]:
                shelter[4] = False
            elif p.end_x == shelter_positions[7]:
                shelter[5] = False
            elif p.end_x == shelter_positions[8]:
                launcher_list[2].ammo = 0
            lose()
            enemy_missiles.remove(p)
            del p
            continue
        
        for w in explosion_list:
            if middle_point(p.current_x, p.current_y, w.poz_x, w.poz_y, w.frame / 60) < 1:
                temp = Explosion(p.current_x, p.current_y)
                explosion_list.append(temp)
                enemy_missiles.remove(p)
                del p
                break


def new_level():
    if not enemy_missiles:
        launcher_list[0].ammo = 10
        launcher_list[1].ammo = 10
        launcher_list[2].ammo = 10
        explosion_list.clear()
        global points
        points += 1
        for i in range(10):
            temp = Missile(random.randrange(WIDTH), 0,
                           random.choice(shelter_positions), HEIGHT - GROUND_HEIGHT, 0.04, random.randrange(4000))
            enemy_missiles.append(temp)


def lose():
    if True in shelter:
        return
    del explosion_list[:]
    del player_missiles[:]
    del enemy_missiles[:]
    global points
    draw()
    large_text = pygame.font.SysFont("consolas", int(HEIGHT * 0.035))
    text_surface = large_text.render("Survived waves : " + str(points) +
                                     " Press space to start again", True, (255, 0, 0))
    text_rect = text_surface.get_rect()
    text_rect.center = ((WIDTH / 2), (HEIGHT / 2))
    s.blit(text_surface, text_rect)
    
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    launcher_list[0].ammo = 10
                    launcher_list[1].ammo = 10
                    launcher_list[2].ammo = 10
                    shelter[0] = True
                    shelter[1] = True
                    shelter[2] = True
                    shelter[3] = True
                    shelter[4] = True
                    shelter[5] = True
                    points = 0
                    main()


def main():

    while True:
        collision()
        draw()
        new_level()
        keys_pressed = pygame.key.get_pressed()

        x, y = pygame.mouse.get_pos()

        if keys_pressed[pygame.K_1] and not keys_down[0]:
            launch_rocket(x, y, 0)
            keys_down[0] = True
        elif not keys_pressed[pygame.K_1]:
            keys_down[0] = False

        if keys_pressed[pygame.K_2] and not keys_down[1]:
            launch_rocket(x, y, 1)
            keys_down[1] = True
        elif not keys_pressed[pygame.K_2]:
            keys_down[1] = False

        if keys_pressed[pygame.K_3] and not keys_down[2]:
            launch_rocket(x, y, 2)
            keys_down[2] = True
        elif not keys_pressed[pygame.K_3]:
            keys_down[2] = False

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit(0)
            elif e.type == pygame.MOUSEBUTTONDOWN:
                launch_rocket(x, y)
        clock.tick(500)


main()

