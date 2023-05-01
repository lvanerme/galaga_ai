import spritesheet
import constants
from random import random
from random import randrange
from tensorflow import random_normal_initializer
from tensorflow import Variable
from main import play_game
from sprites.ai_player import AI_Player


# w_init = tf.random_normal_initializer()
# w = tf.Variable(initial_value=w_init(shape=(12,), dtype='float32'), trainable=True)


# Chromosome = k1, k2, b1, b2
def gen_seed(net_units, pop_size) -> list:
    pop = []
    for _ in range(pop_size):
        # weights for one chromosome
        input_hidden_w_init, hidden_b_init, hidden_output_w_init, output_b_init = random_normal_initializer(), random_normal_initializer(), random_normal_initializer(), random_normal_initializer()
        input_hidden_ws_tf = Variable(initial_value = input_hidden_w_init(shape=(12, net_units), dtype='float32'), trainable=True)
        hidden_bs_tf = Variable(initial_value = hidden_b_init(shape=(net_units,), dtype='float32'), trainable=True)
        hidden_output_ws_tf = Variable(initial_value = hidden_output_w_init(shape=(net_units, 4), dtype='float32'), trainable=True)
        output_bs_tf = Variable(initial_value = output_b_init(shape=(4,), dtype='float32'), trainable=True)
        
        input_hidden_ws, hidden_bs, hidden_output_ws, output_bs = [], [], [], []
        for row in input_hidden_ws_tf:
            for val in row: input_hidden_ws.append(val.numpy())
                
        for val in hidden_bs_tf: hidden_bs.append(val.numpy())
        
        for row in hidden_output_ws_tf:
            for val in row: hidden_output_ws.append(val.numpy())
            
        for val in output_bs_tf: output_bs.append(val.numpy())
            
        pop.append(AI_Player(input_hidden_ws, hidden_bs, hidden_output_ws, output_bs))
        
    return pop


def crossover(c1, c2):
    pass


def ga(pop_size, cross_rate=0.7, mut_rate=0.03, max_iters=4000, net_units=8):
    # gen start pop
    pop = gen_seed(net_units, pop_size)
    for player in pop: play_game(player)        
    
    # NOTE: should be replaced with tourney once fully ready
    c1, c2, new_c = randrange(0, pop_size), randrange(0, pop_size), None
    
    if random() <= cross_rate: new_c = crossover(c1, c2)
    else: new_c = c1 if c1.score >= c2.score else c2 
    
    
ga(2)