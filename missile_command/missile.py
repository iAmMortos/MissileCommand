
import pygame
import math
from drawable_entity import DrawableEntity


class Missile(DrawableEntity):
  MISSILE_COLOR = pygame.Color(255, 0, 0)
  MISSILE_TRAIL_COLOR = pygame.Color(127, 0, 0)
  INTERCEPTOR_COLOR = pygame.Color(0, 255, 0)
  INTERCEPTOR_TRAIL_COLOR = pygame.Color(0, 127, 0)

  def __init__(self, ctx, startx, starty, endx, endy, speed, wait, owner):
    self.ctx = ctx
    self.startx = startx
    self.starty = starty
    self.endx = endx
    self.endy = endy
    self.speed = speed
    self.wait = wait
    self.owner = owner

    self.curx = startx
    self.cury = starty

  def update(self):
    if self.wait <= 0:
      dx = self.curx - self.endx
      dy = self.cury - self.endy
      pit = math.sqrt(dx**2 + dy**2)
      self.curx -= self.speed * dx / pit
      self.cury -= self.speed * dy / pit
    else:
      self.wait -= 1

  def draw(self):
    color = self.MISSILE_COLOR if self.owner == 'foe' else self.INTERCEPTOR_COLOR
    trail_color = self.MISSILE_TRAIL_COLOR if self.owner == 'foe' else self.INTERCEPTOR_TRAIL_COLOR

    pygame.draw.line(self.ctx, trail_color, (self.startx, self.starty), (self.curx, self.cury), 1)
    pygame.draw.ellipse(self.ctx, color, (self.curx - 1.5, self.cury - 1.5, 4, 4), 0)

    if self.owner == 'friend':
      pygame.draw.line(self.ctx, color, (self.endx - 5, self.endy - 5), (self.endx + 5, self.endy + 5))
      pygame.draw.line(self.ctx, color, (self.endx + 5, self.endy - 5), (self.endx - 5, self.endy + 5))
