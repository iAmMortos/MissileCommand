
import numpy as np
import bz2
import pickle


with bz2.BZ2File('data/env.pkl', 'rb') as f:
  env = pickle.load(f)

with bz2.BZ2File('data/q_table.pkl', 'rb') as f:
  q_table = pickle.load(f)

total_epochs, total_penalties = 0, 0
episodes = 100

for _ in range(episodes):
  state = env.reset()
  epochs, penalties, reward = 0, 0, 0

  done = False

  while not done:
    action = np.argmax(q_table[state])
    state, reward, done, info = env.step(action)

    if reward == -10:
      penalties += 1

    epochs += 1

  total_penalties += penalties
  total_epochs += epochs

print(f"Results after {episodes} episodes:")
print(f"Average timesteps per episode: {total_epochs / episodes}")
print(f"Average penalties per episode: {total_penalties / episodes}")

