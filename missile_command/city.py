
import pygame
from drawable_entity import DrawableEntity


class City(DrawableEntity):
  CITY_COLOR = pygame.Color(0, 0, 255)

  def __init__(self, ctx, x, y):
    self.ctx = ctx
    self.x = x
    self.y = y

    w, h = self.ctx.get_size()
    bw = w / 15
    bh = h / 30
    self.rect = (self.x - bw/2, self.y - bh/2, bw, bh)

    self.broken = False

  def update(self):
    pass

  def draw(self):
    if not self.broken:
      pygame.draw.rect(self.ctx, self.CITY_COLOR, self.rect)

  def reset(self):
    self.broken = False
