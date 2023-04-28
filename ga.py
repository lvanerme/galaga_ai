import spritesheet
import constants
import struct
from main import play_game
from random import random, randrange, choices
from tensorflow import random_normal_initializer, Variable
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


def crossover(c1: AI_Player, c2: AI_Player):
    i_to_h_w_len, h_b_len, h_to_o_w_len, o_b_len = len(c1.input_hidden_ws), len(c1.hidden_bs), len(c1.hidden_output_ws), len(c1.output_bs)
    
    # combine all weight lists into one array
    combined1 = c1.input_hidden_ws + c1.hidden_bs + c1.hidden_output_ws + c1.output_bs
    combined2 = c2.input_hidden_ws + c2.hidden_bs + c2.hidden_output_ws + c2.output_bs
    combined_len = i_to_h_w_len + h_b_len + h_to_o_w_len + o_b_len
    new_c = [None for _ in range(combined_len)]
    
    low = randrange(0, (combined_len - 1))
    high = randrange(low, combined_len)
    
    # fill crossover range from c1
    for i in range(low, high): new_c[i] = combined1[i]
    
    # fill remaining spots from c2
    j = high
    while None in new_c:
        j = j % combined_len
        new_c[j] = combined2[j]
        j += 1
    
    # split back into weight arrays
    index = i_to_h_w_len
    new_input_hidden_ws = [new_c[w1] for w1 in range(i_to_h_w_len)]
    new_hidden_bs = [new_c[b1] for b1 in range(index, (index + h_b_len))]
    index += h_b_len
    new_hidden_output_ws = [new_c[w2] for w2 in range(index, (index + h_to_o_w_len))]
    index += h_to_o_w_len
    new_output_bs = [new_c[b2] for b2 in range(index, (index + o_b_len))]
    
    return AI_Player(new_input_hidden_ws, new_hidden_bs, new_hidden_output_ws, new_output_bs)
    
    
def ntourney(scores: list, N: int):
    options = choices(scores, weights=scores, k=N)
    return max(options)

    
    """_summary_
    def crossover(c1, c2):
    x1, y1 = c1
    x2, y2 = c2
    
    combined1 = f"{format(x1, '016b')}{format(y1, '016b')}"
    combined2 = f"{format(x2, '016b')}{format(y2, '016b')}"
    
    amount = random.randint(0,31)
    combined1_split1, combined1_split2 = combined1[:amount], combined1[amount:]
    combined2_split1, combined2_split2 = combined2[:amount], combined2[amount:]
    
    new1, new2 = f'{combined1_split1}{combined2_split2}', f'{combined2_split1}{combined1_split2}'
    newX1, newY1 = int(new1[:16], 2), int(new1[16:], 2)
    newX2, newY2 = int(new2[:16], 2), int(new2[16:], 2)
    
    return [newX1, newY1], [newX2, newY2]
    """
def weights_to_bin(c1: AI_Player, c2: AI_Player):
    bin1, bin2 = '', ''
    for i,val in enumerate(c1.input_hidden_ws):
        b1 = bin(struct.unpack('!i', struct.pack('!f', val))[0]).replace('b', '').replace('-', '')
        b2 = bin(struct.unpack('!i', struct.pack('!f', c2.input_hidden_ws[i]))[0]).replace('b', '').replace('-', '')
        bin1 += b1.rjust(32, '0')
        bin2 += b2.rjust(32, '0')
    
    for i,val in enumerate(c1.hidden_bs):
        b1 = bin(struct.unpack('!i', struct.pack('!f', val))[0]).replace('b', '').replace('-', '')
        b2 = bin(struct.unpack('!i', struct.pack('!f', c2.hidden_bs[i]))[0]).replace('b', '').replace('-', '')
        bin1 += b1.rjust(32, '0')
        bin2 += b2.rjust(32, '0')
    
    for i,val in enumerate(c1.hidden_output_ws):
        b1 = bin(struct.unpack('!i', struct.pack('!f', val))[0]).replace('b', '').replace('-', '')
        b2 = bin(struct.unpack('!i', struct.pack('!f', c2.hidden_output_ws[i]))[0]).replace('b', '').replace('-', '')
        bin1 += b1.rjust(32, '0')
        bin2 += b2.rjust(32, '0')
        
    for i,val in enumerate(c1.output_bs):
        b1 = bin(struct.unpack('!i', struct.pack('!f', val))[0]).replace('b', '').replace('-', '')
        b2 = bin(struct.unpack('!i', struct.pack('!f', c2.output_bs[i]))[0]).replace('b', '').replace('-', '')
        bin1 += b1.rjust(32, '0')
        bin2 += b2.rjust(32, '0')
        
    return bin1, bin2


def ga(pop_size, cross_rate=0.7, mut_rate=0.03, max_iters=4000, net_units=8, N=2):
    # gen start pop
    pop = gen_seed(net_units, pop_size)
    for player in pop: play_game(player)  
    scores = [p.score for p in pop]      
    
    # NOTE: should be replaced with tourney once fully ready
    # i1, i2 = randrange(0, pop_size), randrange(0, pop_size)
    # c1, c2, new_c = pop[i1], pop[i2], None
    new_pop, new_len = [], 0
    while new_len < pop_size:
        i1, i2 = choices(scores, weights=scores, k=N), choices(scores, weights=scores, k=N)
        c1, c2 = pop[scores.index(max(i1))], pop[scores.index(max(i2))]
        
        if random() <= cross_rate: new_c = crossover(c1, c2)
        else: new_c = c1 if c1.score >= c2.score else c2 
        
        new_pop.append(new_c)
        new_len += 1
        
        for player in new_pop: play_game(player)
        new_scores = [p.score for p in pop]
        scores = new_scores
    
    
ga(3)