
import math
import pygame
from drawable_entity import DrawableEntity


class Explosion(DrawableEntity):
  EXPLOSION_COLOR = pygame.Color(255, 0, 255)

  def __init__(self, ctx, x, y):
    w, h = ctx.get_size()
    self.x = x
    self.y = y
    self.expired = False
    self.finished = False
    self.ctx = ctx
    self.max_radius = Explosion.get_max_radius(w)
    self.expand_step = (1/1500) * w
    self.shrink_step = self.expand_step * 2
    self.radius = self.expand_step

  def update(self):
    if self.expired:
      self.radius -= self.shrink_step
      if self.radius <= 0:
        self.finished = True
    elif self.radius >= self.max_radius:
      self.expired = True
    else:
      self.radius += self.expand_step

  def draw(self):
    if not self.finished:
      pygame.draw.ellipse(self.ctx, self.EXPLOSION_COLOR, (self.x - self.radius,
                                                           self.y - self.radius,
                                                           self.radius * 2,
                                                           self.radius * 2), 0)

  @staticmethod
  def get_max_radius(width):
    return (25 / 480) * width

  def is_inside(self, x, y):
    dx = x - self.x
    dy = y - self.y
    dh = math.sqrt(dx**2 + dy**2)
    # p = ((x - wx) ** 2 // (r + 1) ** 2 + (y - wy) ** 2 // (r + 1) ** 2)
    return dh <= self.radius + 1
