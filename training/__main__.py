import logging
import tensorflow as tf
from tf_agents.agents.reinforce.reinforce_agent import ReinforceAgent
from tf_agents.drivers.dynamic_episode_driver import DynamicEpisodeDriver
from tf_agents.environments import tf_py_environment
from tf_agents.networks.actor_distribution_network import ActorDistributionNetwork
from tf_agents.policies.policy_saver import PolicySaver
from tf_agents.replay_buffers.tf_uniform_replay_buffer import TFUniformReplayBuffer
from tf_agents.utils import common

from .environment import OthelloEnvironment

# logging.basicConfig(level=logging.INFO)

# ----------------------------- Hyper-parameters -----------------------------

num_iterations = 250
collect_episodes_per_iteration = 2
replay_buffer_capacity = 2000
fc_layer_params = (100,)
learning_rate = 1e-3
batch_size = 64

checkpoint_dir = "./checkpoints"
policy_dir = "./policy"

# ----------------------------------------------------------------------------

train_env = tf_py_environment.TFPyEnvironment(OthelloEnvironment())

actor_net = ActorDistributionNetwork(
    train_env.observation_spec(),
    train_env.action_spec(),
    fc_layer_params=fc_layer_params,
)

agent = ReinforceAgent(
    train_env.time_step_spec(),
    train_env.action_spec(),
    actor_network=actor_net,
    optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
    train_step_counter=tf.Variable(0),
)
agent.initialize()

replay_buffer = TFUniformReplayBuffer(
    data_spec=agent.collect_data_spec,
    batch_size=train_env.batch_size,
    max_length=replay_buffer_capacity,
)

collect_driver = DynamicEpisodeDriver(
    train_env,
    agent.collect_policy,
    observers=[replay_buffer.add_batch],
    num_episodes=collect_episodes_per_iteration,
)

# Initial data collection
collect_driver.run()

# Dataset generates trajectories with shape [BxTx...] where
# T = n_step_update + 1.
dataset = replay_buffer.as_dataset(
    num_parallel_calls=3,
    sample_batch_size=batch_size,
    num_steps=2,
    single_deterministic_pass=False,
).prefetch(3)

iterator = iter(dataset)

# Optimize by wrapping some of the code in a graph using TF function.
agent.train = common.function(agent.train)

train_checkpointer = common.Checkpointer(
    ckpt_dir=checkpoint_dir,
    agent=agent,
    policy=agent.policy,
    replay_buffer=replay_buffer,
    train_step_counter=agent.train_step_counter,
)

tf_policy_saver = PolicySaver(agent.policy)


def train_one_iteration():
    # Collect a few steps using collect_policy and save to the replay buffer.
    collect_driver.run()

    # Sample a batch of data from the buffer and update the agent's network.
    experience, unused_info = next(iterator)
    train_loss = agent.train(experience)

    iteration = agent.train_step_counter.numpy()
    print(f"iteration: {iteration} loss: {train_loss.loss}")


print("Training one iteration....")
train_one_iteration()
tf_policy_saver.save(policy_dir)


train_env.close()
