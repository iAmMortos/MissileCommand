
import gym
from gym import spaces
from missile_command import MissileCommand
import numpy as np


class McEnv(gym.Env):
  metadata = {'render.modes': ['human']}
  STEPSIZE = 8

  def __init__(self):
    super().__init__()
    self.mc = MissileCommand(no_ui=True, controller='agent')
    self.action_space = spaces.Discrete(self.mc.grid_width * self.mc.grid_height + 1)
    self.observation_space = spaces.Box(low=0, high=255, shape=(self.mc.HEIGHT, self.mc.WIDTH, 3), dtype=np.uint8)

  def step(self, action):
    self._take_action(action)
    # self.status = self.env.step()
    reward = self.mc.points
    ob = self.mc.get_image()
    episode_over = self.mc.round_over
    return ob, reward, episode_over, {}

  def reset(self):
    self.mc.reset_environment()

  def render(self, mode='human'):
    pass

  def _take_action(self, action):
    self.mc.step(step_size=self.STEPSIZE, action=action)

  def _get_reward(self):
    if not self.mc.round_over:
      return 0
    else:
      return self.mc.points
