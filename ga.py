import spritesheet
import constants
import math
import time
import struct
import numpy as np
from main import play_game
from sys import maxsize
from random import random, randrange, randint, uniform, choice, choices
from tensorflow import random_normal_initializer, Variable
from sprites.ai_player import AI_Player
from copy import deepcopy


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

    if max_time - min_time == 0: max_time += 1
    
    mean_score, mean_time = (sum_scores / num_players), (sum_times / num_players)
    
    fitness_scores = []
    for p in players:
        if max_score == min_score: score = max_score
        else: score = (p.score - mean_score) / (max_score - min_score)
        
        if max_time == min_time: time = max_time
        else: time = (p.updates_survived - mean_time) / (max_time - min_time)
        fitness_scores.append((score + time) / 2)
        
    return fitness_scores, max_score, max_time
        

def ga(pop_size, cross_rate=0.7, mut_rate=0.03, max_iters=20, net_units=8, N=2):
    # gen start pop
    start = time.time()
    players = gen_seed(net_units, pop_size)
    #Grab subset of population to make game run faster
    NUM_PLAYERS = 50
    for i in range(0, pop_size-1, NUM_PLAYERS):
        sub_players = players[i:i+NUM_PLAYERS]
        play_game(sub_players)

    scores, max_score, max_time = calc_fitness_scores(players)
    pop = [(p,s) for p,s in sorted(zip(players,scores), key=lambda x: x[1], reverse=True)]     # create list of tuples containing AI_Player and its associated score, sorted by score
    best_score = pop[0][1]
    
    del players      
    
    # main loop
    num_iters = 0
    out_file = open("output_basic.txt", "w")
    while num_iters < max_iters:
        new_players, new_len = [], 0
        # new_players, new_len = [pop[i][0] for i in range(5)], 5         # grab 5 best from previous gen and automatically add them to new_pop
        for player in new_players: 
            if random() <= cross_rate: player = crossover(player, choice(pop)[0])
            if random() <= mut_rate: player = mutation(player)
        
        # gen new pop
        while new_len < pop_size:
            # tourney for new chromosome
            new_c = None
            if np.sum(scores) == 0: new_c = pop[randrange(pop_size)][0]
            else: 
                cs = choices(pop, weights=scores, k=N)
                max_score = -1
                for c in cs:
                    s = c[1]
                    if s > max_score:
                        new_c = c[0]
                        max_score = s
            
            c = AI_Player(new_c.input_hidden_ws, new_c.hidden_bs, new_c.hidden_output_ws, new_c.output_bs)
            del new_c
            
            if random() <= cross_rate: c = crossover(c, choice(pop)[0])
            if random() <= mut_rate: c = mutation(c)
            
            new_players.append(c)
            new_len += 1
        
        del pop

        # for i in range(0, pop_size-1, 2):
        #     sub_players = [new_players[i], new_players[i+1]]
        #     play_game(sub_players)
        for i in range(0, pop_size-1, NUM_PLAYERS):
            sub_players = new_players[i:i+NUM_PLAYERS]
            play_game(sub_players)


        scores, new_max_score, new_max_time = calc_fitness_scores(new_players)
        pop = [(p,s) for p,s in sorted(zip(new_players,scores), key=lambda x: x[1], reverse=True)]     # create list of tuples containing AI_Player and its associated score, sorted by score
        if new_max_score > max_score: max_score = new_max_score
        if new_max_time > max_time: max_time = new_max_time

        # eval gen
        gen_max, count = max(scores), 0
        if gen_max > best_score: best_score = gen_max
        for score in scores:
            if score == gen_max: count += 1
        
        percent_max = count / pop_size
        gen_avg = np.average(scores)
        # if p:   # should we print stats?
        # print(f'{num_iters = }\n\t{best_score = }\t{gen_avg = }\tconsensus rate = {percent_max}')
        print(f"{num_iters = }\n\tbest fitness score = {'{:.2f}'.format(best_score)}\tgen_avg = {'{:.2f}'.format(gen_avg)}\tconsensus rate = {percent_max}\t{max_score = }\t{max_time = }\n")

        out_file.write(f'{num_iters = }\n\tbest fitness score = {best_score}\t{gen_avg = }\tconsensus rate = {percent_max}\t{max_score = }\t{max_time = }\n')
        num_iters += 1

    end = time.time()
    out_file.write(f'{start = }\t{end = }\n')
    out_file.close()


    
ga(100, mut_rate=0.3, cross_rate=0.3, max_iters=100)
