from collections import deque
import os

import numpy as np
import tensorflow as tf


class DQNAgent:
    """
    Multi Layer Perceptron with Experience Replay
    """

    def __init__(self, enable_actions):
        # parameters
        self.name = os.path.splitext(os.path.basename(__file__))[0]
        self.enable_actions = enable_actions
        self.n_actions = len(self.enable_actions)
        self.minibatch_size = 8
        self.replay_memory_size = 1000
        self.learning_rate = 0.001
        self.discount_factor = 0.9
        self.exploration = 0.003
        self.model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
        self.model_name = "{}.ckpt".format("trade")
        # replay memory
        self.D = deque(maxlen=self.replay_memory_size)

        # model
        self.init_model()

        # variables
        self.current_loss = 0.0

    def init_model(self):
        # input layer (1 x 5)
        self.x = tf.placeholder(tf.float32, [None, 5])

        # fully connected layer (32)
        W_fc1 = tf.Variable(tf.truncated_normal([5, 32], stddev=0.01))
        b_fc1 = tf.Variable(tf.zeros([32]))
        h_fc1 = tf.nn.relu(tf.matmul(self.x, W_fc1) + b_fc1)

        # output layer (n_actions)
        W_out = tf.Variable(tf.truncated_normal([32, self.n_actions], stddev=0.01))
        b_out = tf.Variable(tf.zeros([self.n_actions]))
        self.y = tf.matmul(h_fc1, W_out) + b_out

        # loss function
        self.y_ = tf.placeholder(tf.float32, [None, self.n_actions])
        self.loss = tf.reduce_mean(tf.square(self.y_ - self.y))

        # train operation
        optimizer = tf.train.RMSPropOptimizer(self.learning_rate)
        self.training = optimizer.minimize(self.loss)

        # saver
        self.saver = tf.train.Saver()

        # session
        self.sess = tf.Session()
        self.sess.run(tf.global_variables_initializer())

    def Q_values(self, state):
        # Q(state, action) of all actions
        return self.sess.run(self.y, feed_dict={self.x: [state]})[0]

    def select_action(self, state, epsilon):
        max_amount = 10
        if np.random.rand() <= epsilon:
            # random
            if state[3] >= max_amount:
                select_action = (self.enable_actions[0], self.enable_actions[2])
            elif state[4] >= max_amount:
                select_action = (self.enable_actions[0], self.enable_actions[1])
            else:
                select_action = self.enable_actions
            action = np.random.choice(select_action)
        else:
            # max_action Q(state, action)
            action = self.enable_actions[np.argmax(self.Q_values(state))]
        #bind action judge
        if (state[3] >= max_amount) & (action == 1) :
            action = 0
        elif (state[4] >= max_amount) & (action == 2) :
            action = 0

        return action

    def store_experience(self, state, action, reward, state_1):
        self.D.append((state, action, reward, state_1))

    def experience_replay(self):
        state_minibatch = []
        y_minibatch = []

        # sample random minibatch
        minibatch_size = min(len(self.D), self.minibatch_size)
        minibatch_indexes = np.random.randint(0, len(self.D), minibatch_size)

        for j in minibatch_indexes:
            state_j, action_j, reward_j, state_j_1 = self.D[j]
            action_j_index = self.enable_actions.index(action_j)

            y_j = self.Q_values(state_j)

            # reward_j + gamma * max_action' Q(state', action')
            y_j[action_j_index] = reward_j + self.discount_factor * np.max(self.Q_values(state_j_1))  # NOQA

            state_minibatch.append(state_j)
            y_minibatch.append(y_j)

        # training
        self.sess.run(self.training, feed_dict={self.x: state_minibatch, self.y_: y_minibatch})

        # for log
        self.current_loss = self.sess.run(self.loss, feed_dict={self.x: state_minibatch, self.y_: y_minibatch})

    def load_model(self, model_path=None):
        if model_path:
            # load from model_path
            self.saver.restore(self.sess, model_path)
        else:
            # load from checkpoint
            checkpoint = tf.train.get_checkpoint_state(self.model_dir)
            if checkpoint and checkpoint.model_checkpoint_path:
                self.saver.restore(self.sess, checkpoint.model_checkpoint_path)

    def save_model(self):
        self.saver.save(self.sess, os.path.join(self.model_dir, self.model_name))
