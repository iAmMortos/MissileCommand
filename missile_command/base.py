
import pygame
from drawable_entity import DrawableEntity


class Base(DrawableEntity):
  BASE_COLOR = pygame.Color(255, 255, 0)
  AMMO_COLOR = pygame.Color(0, 0, 255)

  def __init__(self, ctx, x, y):
    self.ctx = ctx
    self.x = x
    self.y = y

    self.broken = False
    self.ammo_max = 10
    self.ammo = self.ammo_max

    w, h = ctx.get_size()

    base_top = h - int(h / 10)
    base_half = int(w / 9) / 2
    base_top_half = base_half / 2
    self.poly_points = [(self.x - base_half, self.y),
                        (self.x - base_top_half, base_top),
                        (self.x + base_top_half, base_top),
                        (self.x + base_half, self.y)]

    self.ammo_rects = []
    ammo_radius = w / 100
    ammo_counter = self.ammo_max
    num_ammo_pep_row = 1
    while ammo_counter > 0:
      for i in range(num_ammo_pep_row):
        self.ammo_rects.append((
          self.x - ((num_ammo_pep_row - 2 * i) * ammo_radius) + ammo_radius/2,
          h - (h/10) + (num_ammo_pep_row * ammo_radius),
          ammo_radius,
          ammo_radius
        ))
        ammo_counter -= 1
        if ammo_counter == 0:
          break
      num_ammo_pep_row += 1

  def update(self):
    pass

  def draw(self):
    pygame.draw.polygon(self.ctx, self.BASE_COLOR, self.poly_points)
    for r_idx in range(self.ammo):
      pygame.draw.ellipse(self.ctx, self.AMMO_COLOR, self.ammo_rects[r_idx])

  def reset(self):
    self.ammo = self.ammo_max
    self.broken = False
