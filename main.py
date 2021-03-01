import time
from tqdm import tqdm
from tetris import Tetris

from dqn import DQNAgent
from rl.policy import LinearAnnealedPolicy, BoltzmannQPolicy, EpsGreedyQPolicy
from memory import SequentialMemory
from core import Processor
from callbacks import FileLogger, ModelIntervalCheckpoint, WandbLogger

from tensorflow.keras.models import *
from tensorflow.keras.layers import *
from tensorflow.keras.losses import *
from tensorflow.keras.optimizers import *

WINDOW_LENGTH = 1
"""
model = Sequential()
model.add(Conv2D(32, 4, 2, activation = 'relu', input_shape = (20, 10, 4)))
model.add(Conv2D(64, 2, 2, activation = 'relu'))
model.add(Flatten())
model.add(Dense(256, activation = 'relu'))
model.add(Dense(3))
"""
model = Sequential()
model.add(Dense(128, activation = 'relu', input_shape = (241,)))
model.add(Dense(128, activation = 'relu'))
model.add(Dense(128, activation = 'relu'))
model.add(Dense(128, activation = 'relu'))
model.add(Dense(3))
"""
inputs = Input(shape = (20, 10, 4))
x = Conv2D(32, 4, 2, activation = 'relu')(inputs)
x = Conv2D(64, 2, 2, activation = 'relu')(x)
x = Flatten()(x)
x = Dense(256, activation = 'relu')(x)
q = Dense(3)(x)
model = Model(inputs, q)
"""
model.summary()

optimizer = Adam(learning_rate = 0.001)

memory = SequentialMemory(limit         = 20000,
                          window_length = WINDOW_LENGTH)

policy = LinearAnnealedPolicy(EpsGreedyQPolicy(),
                              attr       = 'eps',
                              value_max  = 1.0,
                              value_min  = 0.1,
                              value_test = 0.05,
                              nb_steps   = 1000000)

dqn = DQNAgent(model               = model,
               nb_actions          = 3,
               policy              = policy,
               memory              = memory,
               nb_steps_warmup     = 2000,
               gamma               = 0.95,
               target_model_update = 2000,
               train_interval      = 1,
               delta_clip          = 1.0)

dqn.compile(optimizer, metrics = ['mae'])

env = Tetris()

start = time.time()

weights_filename = 'dqn_{}_tetris_weights.h5'.format(start)
checkpoint_weights_filename = 'dqn_{}_tetris_weights_.h5'.format(start)
log_filename = 'dqn_tetris_log.json'
callbacks = [ModelIntervalCheckpoint(checkpoint_weights_filename, interval = 250000)]
callbacks += [FileLogger(log_filename, interval = 100)]
callbacks += [WandbLogger()]
dqn.fit(env, callbacks = callbacks, nb_steps = 1750000, log_interval = 10000)
dqn.save_weights(weights_filename, overwrite = True)


"""
env = Tetris()

for episode in tqdm(range(1000), "Episode"):
    env.reset()
    while not env.terminal:
        action = env.action_space.sample()
        observation, reward, terminal, info = env.step(action)
        # env.render()

env.close()
"""