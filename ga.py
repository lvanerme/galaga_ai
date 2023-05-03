import spritesheet
import constants
import math
import struct
import numpy as np
from main import play_game
from sys import maxsize
from random import random, randrange, randint, uniform, choices
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
        input_hidden_ws_tf = Variable(initial_value = input_hidden_w_init(shape=(14, net_units), dtype='float32'), trainable=True)
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


def parse_weight_list(i_to_h_w_len, h_b_len, h_to_o_w_len, o_b_len, combined:list):
    index = i_to_h_w_len
    new_input_hidden_ws = [combined[w1] for w1 in range(i_to_h_w_len)]
    new_hidden_bs = [combined[b1] for b1 in range(index, (index + h_b_len))]
    index += h_b_len
    new_hidden_output_ws = [combined[w2] for w2 in range(index, (index + h_to_o_w_len))]
    index += h_to_o_w_len
    new_output_bs = [combined[b2] for b2 in range(index, (index + o_b_len))]
    
    return AI_Player(new_input_hidden_ws, new_hidden_bs, new_hidden_output_ws, new_output_bs)


def mutation(c: AI_Player):
    i_to_h_w_len, h_b_len, h_to_o_w_len, o_b_len = len(c.input_hidden_ws), len(c.hidden_bs), len(c.hidden_output_ws), len(c.output_bs)
    combined_len = i_to_h_w_len + h_b_len + h_to_o_w_len + o_b_len
    combined = c.input_hidden_ws + c.hidden_bs + c.hidden_output_ws + c.output_bs
    
    num_mutations = randint(1, math.floor(combined_len / 7))    # Will be 1 - 20 assuming a 8-node hidden layer....possibly hard code once finalized
    indices = [i for i in range(combined_len)]
    genes = [np.random.choice(indices, replace=False) for _ in range(num_mutations)]       # grab num_mutations random genes
    for gene in genes:
        change = uniform(0.001, 0.1)        # how much to change the value by
        if randint(0,1) == 1: change = -change
        combined[gene] += change
    
    return parse_weight_list(i_to_h_w_len, h_b_len, h_to_o_w_len, o_b_len, combined)


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
    return parse_weight_list(i_to_h_w_len, h_b_len, h_to_o_w_len, o_b_len, new_c)


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


def calc_fitness_scores(players: list):
    sum_scores, sum_times, max_score, min_score, max_time, min_time, num_players = 0, 0, -1, maxsize, -1, maxsize, len(players)
    for p in players:
        s, t = p.score, p.updates_survived
        sum_scores += s
        sum_times += t
        
        if s >= max_score: max_score = s
        if s <= min_score: min_score = s
        if t >= max_time: max_time = t
        if t <= min_time: min_time = t
    
    mean_score, mean_time = (sum_scores / num_players), (sum_times / num_players)
    
    fitness_scores = []
    for p in players:
        if max_score == 0: score = 0
        else: score = (p.score - mean_score) / (max_score - min_score)
        
        time = (p.updates_survived - mean_time) / (max_time - min_time)
        fitness_scores.append((score + time) / 2)
        
    return fitness_scores
        

def ga(pop_size, cross_rate=0.7, mut_rate=0.03, max_iters=4000, net_units=8, N=2):
    # gen start pop
    players = gen_seed(net_units, pop_size)
    for player in players: play_game(player)  
    scores = calc_fitness_scores(players)
    pop = [(p,s) for p,s in sorted(zip(players,scores), key=lambda x: x[1], reverse=True)]     # create list of tuples containing AI_Player and its associated score, sorted by score
    best_score = pop[0][1]      
    
    # main loop
    num_iters = 0
    while num_iters < max_iters:
        # new_players, new_len = [pop[i][0] for i in range(5)], 5         # grab 5 best from previous gen and automatically add them to new_pop
        new_players, new_len = [], 0
        for player in new_players: 
            if random() <= mut_rate: player = mutation(player)
        
        # gen new pop
        while new_len < pop_size:
            # tourney for new chromosome
            cs = choices(pop, weights=scores, k=N)
            new_c, max_score = None, -1
            for c in cs:
                s = c[1]
                if s > max_score:
                    new_c = c[0]
                    max_score = s
            
            if random() <= mut_rate: new_c = mutation(new_c)
            
            # No crossover?
            # if random() <= cross_rate: new_c = crossover(c1, c2)
            # else: new_c = c1 if c1.score >= c2.score else c2 
            
            new_players.append(new_c)
            new_len += 1
        
        # pop = new_pop
        for player in new_players: play_game(player)
        scores = calc_fitness_scores(new_players)
        pop = [(p,s) for p,s in sorted(zip(new_players,scores), key=lambda x: x[1], reverse=True)]     # create list of tuples containing AI_Player and its associated score, sorted by score

        # eval gen
        gen_max, count = max(scores), 0
        if gen_max > best_score: best_score = gen_max
        for score in scores:
            if score == gen_max: count += 1
        
        percent_max = count / pop_size
        gen_avg = np.average(scores)
        # if p:   # should we print stats?
        print(f'{num_iters = }\n\t{best_score = }\t{gen_avg = }\tconsensus rate = {percent_max}')
        num_iters += 1

    
ga(3, mut_rate=0.3)