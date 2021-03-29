
import gym
import numpy as np
import random
from IPython.display import clear_output
from time import sleep
import pickle, bz2
import mcenv


class QTrain(object):
  def __init__(self, env):
    self.env = env
    self.q_table = np.zeros([*self.env.observation_space.shape, self.env.action_space.n], dtype=np.float32)
    self.epochs = 0
    self.alpha = 0.1
    self.gamma = 0.6
    self.epsilon = 0.1

  def train(self):

    for i in range(1, 100001):
      state = self.env.reset()

      self.epochs, penalties, reward = 0, 0, 0
      done = False

      while not done:
        if random.uniform(0, 1) < self.epsilon:
          action = self.env.action_space.sample()
        else:
          action = np.argmax(self.q_table[state])

        next_state, reward, done, info = self.env.step(action)

        old_value = self.q_table[state, action]
        next_max = np.max(self.q_table[next_state])

        new_value = (1 - self.alpha) * old_value + self.alpha * (reward + self.gamma * next_max)
        self.q_table[state, action] = new_value

        if reward == -10:
          penalties += 1

        state = next_state
        self.epochs += 1

      if i % 100 == 0:
        clear_output(wait=True)
        print(f"Episode: {i}")

    print("Training finished.")

  def export_weights(self, file):
    with bz2.BZ2File(file, 'wb') as f:
      pickle.dump(self.q_table, f)
    print(f"Exported weights to [{file}]")

  def export_environment(self, file):
    with bz2.BZ2File(file, 'wb') as f:
      pickle.dump(self.env, f)
    print(f"Exported environment to [{file}]")


if __name__ == '__main__':
  qt = QTrain(mcenv.McEnv())
  qt.train()
  qt.export_weights('data/mc_weights.pkl')
  qt.export_environment('data/mc_env.pkl')
