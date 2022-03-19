import numpy as np
import tensorflow as tf
from tf_agents.networks import network
from tf_agents.specs.tensor_spec import TensorSpec


class ActionNet(network.Network):
    def __init__(self, input_tensor_spec: TensorSpec, output_tensor_spec: TensorSpec):
        super().__init__(
            input_tensor_spec=input_tensor_spec, state_spec=(), name="ActionNet"
        )
        self._output_tensor_spec = output_tensor_spec
        self._sub_layers = [
            tf.keras.layers.Dense(16, activation=tf.nn.tanh),
            tf.keras.layers.Dense(8, activation=tf.nn.tanh),
            tf.keras.layers.Dense(1, activation=tf.nn.tanh),
        ]

    def call(self, observations, step_type, network_state):
        del step_type

        output = tf.cast(observations, dtype=np.float32)
        for layer in self._sub_layers:
            output = layer(output)
        actions = tf.reshape(output, [-1] + self._output_tensor_spec.shape.as_list())

        # Scale and shift actions to the correct range if necessary.
        return (actions + 1) / 2, network_state
