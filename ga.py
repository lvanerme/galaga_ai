import numpy as np
from game import Game
import tensorflow as tf
from tensorflow import random_normal_initializer
from tensorflow import Variable


class Chromosome():
    def __init__(self, net_units, ws, bs):
        self.net_units = net_units
        self.ws = ws
        self.bs = bs
        self.score = None


# w_init = tf.random_normal_initializer()
# w = tf.Variable(initial_value=w_init(shape=(12,), dtype='float32'), trainable=True)


# Chromosome = k1, k2, b1, b2
def gen_seed(net_units, pop_size):
    pop = []
    # weights for one chromosome
    input_hidden_init = random_normal_initializer()
    ws = Variable(initial_value = input_hidden_init(shape=(12, net_units), dtype='float32'), trainable=True)
    
    hidden_output_init = random_normal_initializer()
    bs = Variable(initial_value = hidden_output_init(shape=(net_units + 4,), dtype='float32'), trainable=True)
    c = Chromosome(net_units, ws, bs)


def ga(pop_size, cross_rate, mut_rate, max_iters):
    # gen start pop
    pass
    
    
gen_seed(4, 100)