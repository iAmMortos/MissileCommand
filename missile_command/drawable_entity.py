
from abc import ABC, abstractmethod


class DrawableEntity(ABC):
  @abstractmethod
  def update(self):
    pass

  @abstractmethod
  def draw(self):
    pass
