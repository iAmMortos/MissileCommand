import pygame
import sys
import random
import math

from missile import Missile
from explosion import Explosion
from base import Base
from city import City


class MissileCommand(object):
  INTERCEPTOR_SPEED = 2
  MISSILE_SPEED = 0.4
  MISSILE_WAIT = 300

  WIDTH = 200
  HEIGHT = 200
  GROUND_HEIGHT = int(HEIGHT / 15)
  BASE_HEIGHT = int(HEIGHT / 10)
  WINDOW_TITLE = 'Missile Command'
  NUM_CITIES = 6
  NUM_BASES = 3
  SCENARIO = 'stage1'
  '''
  stage1 - 1 missile; same target; vertical angle
  stage2 - 1 missile; same target; random angle
  stage3 - 1 missile; random target; vertical angle
  stage4 - 1 missile; random target; random angle
  stage5 - multiple missiles; random targets; vertical angles
  stage6 - multiple missiles; random targets; random angles
  special - two missiles that always cross paths simultaneously at a random point on screen
  full_easy - All random; 15 missiles
  full_medium - All random; 20 missiles
  full_hard - All random; 30 missiles
  full_crazy - All random; 40 missiles
  '''

  # TODO: make sure final missile strike gets counted in score. When final missile destroyed a city, that city was still
  # TODO: being counted in the score.

  # Colors
  BACKGROUND_COLOR = pygame.Color(0, 0, 0)
  GROUND_COLOR = pygame.Color(255, 255, 0)

  def __init__(self, no_ui=False, controller='player', force_fire=False, throttle_frames=True):
    # initialize pygame
    pygame.init()

    self.no_ui = no_ui
    self.controller = controller  # 'player' or 'agent'
    self.force_fire = force_fire
    self.throttle_frames = throttle_frames

    # for grid targeting
    self.grid_width = round((self.WIDTH - Explosion.get_max_radius(self.WIDTH) / 2) / Explosion.get_max_radius(self.WIDTH))
    self.grid_height = round((self.HEIGHT - self.BASE_HEIGHT * 1.4) / Explosion.get_max_radius(self.WIDTH))

    if self.no_ui:
      self.ctx = pygame.Surface((self.WIDTH, self.HEIGHT))
    else:
      pygame.display.set_caption(self.WINDOW_TITLE)
      pygame.mouse.set_cursor(*pygame.cursors.diamond)
      self.ctx = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

    half = self.WIDTH / 18
    self.target_xs = [n * self.WIDTH/9 - half for n in range(1, 10)]

    self.points = 0
    self.round_over = True
    self.steps = 0

    self.interceptors = []
    self.missiles = []
    self.explosions = []
    self.cities = [City(self.ctx, self.target_xs[n-1], self.HEIGHT - self.GROUND_HEIGHT) for n in (2, 3, 4, 6, 7, 8)]
    self.bases = [Base(self.ctx, self.target_xs[n-1], self.HEIGHT - self.GROUND_HEIGHT) for n in (1, 5, 9)]
    self.keys = [False for _ in range(3)]

  def draw(self):
    self.ctx.fill(self.BACKGROUND_COLOR)
    pygame.draw.rect(self.ctx, self.GROUND_COLOR, (0, self.HEIGHT - self.GROUND_HEIGHT, self.WIDTH, self.GROUND_HEIGHT))
    for drawable_list in (self.bases, self.cities, self.interceptors, self.missiles, self.explosions):
      for drawable in drawable_list:
        drawable.draw()

    if not self.no_ui:
      pygame.display.update()

  def get_nearest_able_base(self, x, y):
    curbase = None
    y1 = self.HEIGHT * (43 / 48)
    dy = y - y1
    minimum = 100000
    for i, base in enumerate(self.bases):
      if base.ammo > 0 or self.force_fire:
        x1 = base.x
        dx = x1 - x
        temp = math.sqrt(dx**2 + dy**2)
        if temp < minimum:
          minimum = temp
          curbase = base
    return curbase

  def launch_rocket(self, x, y, baseidx=None):
    if y > self.HEIGHT - self.BASE_HEIGHT * 1.4:
      return

    if baseidx is not None:
      base = self.bases[baseidx]
    else:
      base = self.get_nearest_able_base(x, y)

    if base and (base.ammo > 0 or self.force_fire):
      base.ammo = max(base.ammo - 1, 0)
      self.interceptors.append(Missile(self.ctx, base.x, self.HEIGHT - self.BASE_HEIGHT, x, y, self.INTERCEPTOR_SPEED, 0, 'friend'))

  def update(self):
    for updatable_list in (self.bases, self.cities, self.interceptors, self.missiles, self.explosions):
      for updatable in updatable_list:
        updatable.update()

    for explosion in self.explosions:
      if explosion.finished:
        self.explosions.remove(explosion)
        del explosion

  def handle_collisions(self):
    new_exp = []

    for i in self.interceptors:
      if i.cury - i.endy < 0.1:
        new_exp.append(Explosion(self.ctx, i.endx, i.endy))
        self.interceptors.remove(i)
        del i

    for m in self.missiles:
      if m.endy - m.cury < 0.1:
        new_exp.append(Explosion(self.ctx, m.endx, m.endy))
        self.missiles.remove(m)
        for c in self.cities:
          if m.endx == c.x and not c.broken:
            c.broken = True
        for b in self.bases:
          if m.endx == b.x and not b.broken:
            b.broken = True
            b.ammo = 0
        del m

    for e in self.explosions:
      for i in self.interceptors:
        if e.is_inside(i.curx, i.cury):
          new_exp.append(Explosion(self.ctx, i.curx, i.cury))
          self.interceptors.remove(i)
          del i
      for m in self.missiles:
        if e.is_inside(m.curx, m.cury):
          new_exp.append(Explosion(self.ctx, m.curx, m.cury))
          self.missiles.remove(m)
          del m

    self.explosions += new_exp

  def get_random_target_position(self):
    positions = []
    for base in self.bases:
      positions.append((base.x, base.y))
    for city in self.cities:
      positions.append((city.x, city.y))
    return random.choice(positions)

  def generate_scenario_missiles(self, scenario):
    missiles = []

    if scenario == 'stage1':  # 1 missile; same target; vertical angle
      base = self.bases[1]
      missiles.append(Missile(self.ctx, self.WIDTH/2, -3, base.x, base.y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))

    elif scenario == 'stage2':  # 1 missile; same target; random angle
      base = self.bases[1]
      missiles.append(Missile(self.ctx, random.randrange(self.WIDTH), -3, base.x, base.y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))

    elif scenario == 'stage3':  # 1 missile; random target; vertical angle
      x, y = self.get_random_target_position()
      missiles.append(Missile(self.ctx, x, -3, x, y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))

    elif scenario == 'stage4':  # 1 missile; random target; random angle
      x, y = self.get_random_target_position()
      missiles.append(Missile(self.ctx, random.randrange(self.WIDTH), -3, x, y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))

    elif scenario == 'stage5':  # multiple missiles; random targets; vertical angles
      for base in self.bases:
        missiles.append(Missile(self.ctx, base.x, -3, base.x, base.y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))
      for city in self.cities:
        missiles.append(Missile(self.ctx, city.x, -3, city.x, city.y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))

    elif scenario == 'stage6':  # multiple missiles; random targets; random angles
      for base in self.bases:
        missiles.append(Missile(self.ctx, random.randrange(self.WIDTH), -3, base.x, base.y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))
      for city in self.cities:
        missiles.append(Missile(self.ctx, random.randrange(self.WIDTH), -3, city.x, city.y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))

    elif scenario == 'special':  # two missiles that always cross paths simultaneously at a random point on screen
      pass

    elif scenario == 'full_easy':  # All random; 15 missiles
      for base in self.bases:
        missiles.append(Missile(self.ctx, random.randrange(self.WIDTH), -3, base.x, base.y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))
      for city in self.cities:
        missiles.append(Missile(self.ctx, random.randrange(self.WIDTH), -3, city.x, city.y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))
      for i in range(6):
        x, y = self.get_random_target_position()
        missiles.append(Missile(self.ctx, random.randrange(self.WIDTH), -3, x, y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))

    elif scenario == 'full_medium':  # All random; 20 missiles
      for base in self.bases:
        missiles.append(Missile(self.ctx, random.randrange(self.WIDTH), -3, base.x, base.y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))
      for city in self.cities:
        missiles.append(Missile(self.ctx, random.randrange(self.WIDTH), -3, city.x, city.y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))
      for i in range(11):
        x, y = self.get_random_target_position()
        missiles.append(Missile(self.ctx, random.randrange(self.WIDTH), -3, x, y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))

    elif scenario == 'full_hard':  # All random; 30 missiles
      for base in self.bases:
        missiles.append(Missile(self.ctx, random.randrange(self.WIDTH), -3, base.x, base.y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))
      for city in self.cities:
        missiles.append(Missile(self.ctx, random.randrange(self.WIDTH), -3, city.x, city.y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))
      for i in range(21):
        x, y = self.get_random_target_position()
        missiles.append(Missile(self.ctx, random.randrange(self.WIDTH), -3, x, y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))

    elif scenario == 'full_crazy':  # All random; 40 missiles
      for base in self.bases:
        missiles.append(Missile(self.ctx, random.randrange(self.WIDTH), -3, base.x, base.y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))
      for city in self.cities:
        missiles.append(Missile(self.ctx, random.randrange(self.WIDTH), -3, city.x, city.y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))
      for i in range(31):
        x, y = self.get_random_target_position()
        missiles.append(Missile(self.ctx, random.randrange(self.WIDTH), -3, x, y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))

    elif scenario == 'test':
      for i in range(2):
        missiles.append(Missile(self.ctx, random.randrange(self.WIDTH), -3, self.bases[i].x, self.bases[i].y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))
      for city in self.cities:
        missiles.append(Missile(self.ctx, random.randrange(self.WIDTH), -3, city.x, city.y, self.MISSILE_SPEED, random.randrange(self.MISSILE_WAIT), 'foe'))

    return missiles

  def check_game_start(self):
    if self.round_over:
      self.reset_environment()
      self.missiles = self.generate_scenario_missiles(self.SCENARIO)

  def check_game_over(self):
    if not self.missiles:
      self.round_over = True
    return self.round_over

  def calculate_points(self):
    self.points = 0
    for city in self.cities:
      if not city.broken:
        self.points += 100
    for base in self.bases:
      self.points += 5 * base.ammo
    return self.points

  def handle_input(self, action=None):
    if self.controller == 'player':
      keys_pressed = pygame.key.get_pressed()
      x, y = pygame.mouse.get_pos()

      for i, k in enumerate([pygame.K_1, pygame.K_2, pygame.K_3]):
        if keys_pressed[k] and not self.keys[i]:
          self.launch_rocket(x, y, i)
          self.keys[i] = True
        elif not keys_pressed[k]:
          self.keys[i] = False

      for e in pygame.event.get():
        if e.type == pygame.QUIT:
          sys.exit(0)
        elif e.type == pygame.MOUSEBUTTONDOWN:
          self.launch_rocket(x, y)

    elif self.controller == 'agent':
      if action is None or action == 0:  # no-op
        return
      else:
        a = action - 1
        y_idx = a // self.grid_width
        x_idx = a % self.grid_width
        x, y = self.grid_2_pixel(x_idx, y_idx)
        self.launch_rocket(x, y)

  def grid_2_pixel(self, x_idx, y_idx):
    r = Explosion.get_max_radius(self.WIDTH)
    return r / 2 + (x_idx * r), r / 2 + (y_idx * r)

  def step(self, step_size=1, action=0):
    self.check_game_start()
    self.handle_input(action)
    for _ in range(step_size):
      self.update()
      self.handle_collisions()
    self.draw()
    if self.check_game_over():
      self.calculate_points()
      print(self.points)
    self.steps += 1

  def start_game_loop(self):
    # Game loop
    while True:
      self.step()
      if self.throttle_frames:
        pygame.time.Clock().tick(30)

  def reset_environment(self):
    for base in self.bases:
      base.reset()
    for city in self.cities:
      city.reset()
    self.points = 0
    self.missiles = []
    self.interceptors = []
    self.explosions = []
    self.round_over = False
    self.steps = 0

  def get_image(self):
    # RETURNED PIXELS ARE REFERENCES, WILL MODIFY THE ORIGINAL IMAGE
    return pygame.surfarray.array3d(self.ctx)


if __name__ == '__main__':
  mc = MissileCommand(controller='player', no_ui=False)
  mc.start_game_loop()
