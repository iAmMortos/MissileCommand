
import numpy as np
import bz2, pickle


class QTest(object):
  def __init__(self, envpkl, qtablepkl, episodes):
    self.env = self.import_environment(envpkl)
    self.q_table = self.import_weights(qtablepkl)
    self.total_epochs = 0
    self.total_penalties = 0
    self.episodes = episodes

  def import_environment(self, file):
    with bz2.BZ2File(file, 'rb') as f:
      env = pickle.load(f)
    print(f'Environment imported from [{file}]')
    return env

  def import_weights(self, file):
    with bz2.BZ2File(file, 'rb') as f:
      q_table = pickle.load(f)
    print(f'Weights imported from [{file}]')
    return q_table

  def test(self):
    self.total_epochs, self.total_penalties = 0, 0

    for _ in range(self.episodes):
      state = self.env.reset()
      epochs, penalties, reward = 0, 0, 0

      done = False

      while not done:
        action = np.argmax(self.q_table[state])
        state, reward, done, info = self.env.step(action)

        if reward == -10:
          penalties += 1

        epochs += 1

      self.total_penalties += penalties
      self.total_epochs += epochs

    print(f"Results after {self.episodes} episodes:")
    print(f"Average timesteps per episode: {self.total_epochs / self.episodes}")
    print(f"Average penalties per episode: {self.total_penalties / self.episodes}")


if __name__ == '__main__':
  qt = QTest('data/env.pkl', 'data/q_table.pkl', episodes=100)
  qt.test()
