from tf_agents.environments import tf_py_environment

from .environment import OthelloEnvironment

train_env = tf_py_environment.TFPyEnvironment(OthelloEnvironment())

train_env.close()
