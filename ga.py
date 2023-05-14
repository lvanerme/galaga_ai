import math
import time
import struct
import numpy as np
from main import play_game
from sys import maxsize as MAXSIZE
from random import random, randrange, randint, uniform, choice, choices
from tensorflow import random_normal_initializer, Variable
from sprites.ai_player import AI_Player


def gen_seed(net_units, net_units2, pop_size) -> list:
    pop = []
    for _ in range(pop_size):
        # weights for one chromosome
        input_hidden_w_init, hidden_b_init, hidden_w2_init, hidden_b2_init, hidden_output_w_init, output_b_init = random_normal_initializer(), random_normal_initializer(), random_normal_initializer(), random_normal_initializer(), random_normal_initializer(), random_normal_initializer()
        input_hidden_ws_tf = Variable(initial_value = input_hidden_w_init(shape=(14, net_units), dtype='float32'), trainable=True)
        hidden_bs_tf = Variable(initial_value = hidden_b_init(shape=(net_units,), dtype='float32'), trainable=True)
        hidden_ws_tf2 = Variable(initial_value = hidden_w2_init(shape=(net_units, net_units2), dtype='float32'), trainable=True)
        hidden_bs_tf2 = Variable(initial_value = hidden_b2_init(shape=(net_units2,), dtype='float32'), trainable=True)
        hidden_output_ws_tf = Variable(initial_value = hidden_output_w_init(shape=(net_units2, 4), dtype='float32'), trainable=True)
        output_bs_tf = Variable(initial_value = output_b_init(shape=(4,), dtype='float32'), trainable=True)
        
        input_hidden_ws, hidden_bs, hidden_ws2, hidden_bs2, hidden_output_ws, output_bs = [], [], [], [], [], []
        for row in input_hidden_ws_tf:
            for val in row: input_hidden_ws.append(val.numpy())
                
        for val in hidden_bs_tf: hidden_bs.append(val.numpy())
        
        for row in hidden_ws_tf2: 
            for val in row: hidden_ws2.append(val.numpy())
        
        for row in hidden_bs_tf2: hidden_bs2.append(val.numpy())
        
        for row in hidden_output_ws_tf:
            for val in row: hidden_output_ws.append(val.numpy())
            
        for val in output_bs_tf: output_bs.append(val.numpy())
        pop.append(AI_Player(input_hidden_ws, hidden_bs, hidden_ws2, hidden_bs2, hidden_output_ws, output_bs))
        
    return pop


def parse_weight_list(i_to_h_w_len, h_b_len, h_to_h_w_len, h_b2_len, h_to_o_w_len, o_b_len, combined:list):
    index = i_to_h_w_len
    new_input_hidden_ws = [combined[w1] for w1 in range(i_to_h_w_len)]
    new_hidden_bs = [combined[b1] for b1 in range(index, (index + h_b_len))]
    index += h_b_len
    new_hidden_ws2 = [combined[w2] for w2 in range(index, (index + h_to_h_w_len))]
    index += h_to_h_w_len
    new_hidden_bs2 = [combined[b2] for b2 in range(index, (index + h_b2_len))]
    index += h_b2_len
    new_hidden_output_ws = [combined[w3] for w3 in range(index, (index + h_to_o_w_len))]
    index += h_to_o_w_len
    new_output_bs = [combined[b3] for b3 in range(index, (index + o_b_len))]
    
    return AI_Player(new_input_hidden_ws, new_hidden_bs, new_hidden_ws2, new_hidden_bs2, new_hidden_output_ws, new_output_bs)


def mutation(c: AI_Player):
    i_to_h_w_len, h_b_len, h_to_h_w_len, h_b2_len, h_to_o_w_len, o_b_len = len(c.input_hidden_ws), len(c.hidden_bs), len(c.hidden_ws2), len(c.hidden_bs2), len(c.hidden_output_ws), len(c.output_bs)
    combined_len = i_to_h_w_len + h_b_len + h_to_h_w_len + h_b2_len + h_to_o_w_len + o_b_len
    combined = c.input_hidden_ws + c.hidden_bs + c.hidden_ws2 + c.hidden_bs2 + c.hidden_output_ws + c.output_bs
    
    num_mutations = randint(1, math.floor(combined_len / 5))
    indices = [i for i in range(combined_len)]
    genes = [np.random.choice(indices, replace=False) for _ in range(num_mutations)]       # grab num_mutations random genes
    for gene in genes:
        change = uniform(0.001, 0.1)        # how much to change the value by
        if randint(0,1) == 1: change = -change
        combined[gene] += change
    
    return parse_weight_list(i_to_h_w_len, h_b_len, h_to_h_w_len, h_b2_len, h_to_o_w_len, o_b_len, combined)


def crossover(c1: AI_Player, c2: AI_Player):
    i_to_h_w_len, h_b_len, h_to_h_w_len, h_b2_len, h_to_o_w_len, o_b_len = len(c1.input_hidden_ws), len(c1.hidden_bs), len(c1.hidden_ws2), len(c1.hidden_bs2), len(c1.hidden_output_ws), len(c1.output_bs)
    
    # combine all weight lists into one array
    combined1 = c1.input_hidden_ws + c1.hidden_bs + c1.hidden_ws2 + c1.hidden_bs2 + c1.hidden_output_ws + c1.output_bs
    combined2 = c2.input_hidden_ws + c2.hidden_bs + c2.hidden_ws2 + c2.hidden_bs2 + c2.hidden_output_ws + c2.output_bs
    combined_len = i_to_h_w_len + h_b_len + h_to_h_w_len + h_b2_len + h_to_o_w_len + o_b_len
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
    return parse_weight_list(i_to_h_w_len, h_b_len, h_to_h_w_len, h_b2_len, h_to_o_w_len, o_b_len, new_c)


def calc_fitness_scores(players: list):
    sum_scores, sum_times, num_players = 0, 0, len(players)
    max_score, min_score, max_time, min_time, max_score_idx, max_time_idx = -1, MAXSIZE, -1, MAXSIZE, 0, 0
    for i,p in enumerate(players):
        s, t = p.score, p.updates_survived
        sum_scores += s
        sum_times += t
        
        if s >= max_score: 
            max_score = s
            max_score_idx = i
        if s <= min_score: min_score = s
        if t >= max_time: 
            max_time = t
            max_time_idx = i
        if t <= min_time: min_time = t

    if max_time - min_time == 0: max_time += 1
    if max_score - min_score == 0: max_score += 1
    
    mean_score, mean_time = (sum_scores / num_players), (sum_times / num_players)
    
    fitness_scores = []
    for p in players:
        if max_score == min_score: score = max_score
        else: score = (p.score - mean_score) / (max_score - min_score)  # normalize scores
        
        if max_time == min_time: time = max_time
        else: time = (p.updates_survived - mean_time) / (max_time - min_time)   # normalize times
        fitness_scores.append((score + time) / 2)   # score is evenly weighted between scores and time
        
    return fitness_scores, max_score, max_time, max_score_idx, max_time_idx
        

def ga(pop_size, cross_rate=0.7, mut_rate=0.03, max_iters=20, net_units=8, net_units2=6, N=2):
    start = time.time()
    players = gen_seed(net_units, net_units2, pop_size)
    #Grab subset of population to make game run faster
    NUM_PLAYERS = 35
    for i in range(0, pop_size-1, NUM_PLAYERS):
        sub_players = players[i:i+NUM_PLAYERS]
        play_game(sub_players)

    scores, best_score, max_time, max_score_idx, max_time_idx = calc_fitness_scores(players)
    pop = [(p,s) for p,s in sorted(zip(players,scores), key=lambda x: x[1], reverse=True)]     # create list of tuples containing AI_Player and its associated score, sorted by score
    best_player = dict(gen=0,s=pop[0][1],p=pop[max_score_idx][0])
    best_players, best_score, best_time = [best_player], pop[max_score_idx][0].score, pop[max_time_idx][0].updates_survived
    del players      
    
    # main loop
    num_iters = 0
    out_file = open('output_basic.txt', 'w')
    while num_iters < max_iters:
        # new_players, new_len = [], 0
        new_players, new_len = [pop[i][0] for i in range(5)], 5         # grab 5 best from previous gen and automatically add them to new_pop
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
            
            c = AI_Player(new_c.input_hidden_ws, new_c.hidden_bs, new_c.hidden_ws2, new_c.hidden_bs2, new_c.hidden_output_ws, new_c.output_bs)
            del new_c
            
            if random() <= cross_rate: c = crossover(c, choice(pop)[0])
            if random() <= mut_rate: c = mutation(c)
            
            new_players.append(c)
            new_len += 1
        
        del pop

        for i in range(0, pop_size, NUM_PLAYERS):
            sub_players = new_players[i:i+NUM_PLAYERS]
            play_game(sub_players)

        # eval gen
        scores, new_best_score, new_max_time, best_score_idx, best_time_idx = calc_fitness_scores(new_players)
        pop = [(p,s) for p,s in sorted(zip(new_players,scores), key=lambda x: x[1], reverse=True)]     # create list of tuples containing AI_Player and its associated score, sorted by score
        update = (num_iters % 10) == 0
        if new_best_score > best_score: 
            best_score = new_best_score
            if update: best_players.append(dict(gen=num_iters,s=best_score,t=best_time,p=pop[best_score_idx][0]))
        if new_max_time > best_time: 
            best_time = new_max_time
            if update: best_players.append(dict(gen=num_iters,s=best_score,t=best_time,p=pop[best_time_idx][0]))

        gen_max, count = pop[0][1], 0
        # if gen_max > best_score: best_score = gen_max # I think this is done above?
        for score in scores:
            if score == gen_max: count += 1
            
        percent_max = count / pop_size
  
        print(f"{num_iters = }\n\tconsensus rate = {percent_max}\t{best_score = }\t{max_time = }\n")

        out_file.write(f"{num_iters = }\n\tconsensus rate = {percent_max}\t{best_score = }\t{max_time = }\n")
        num_iters += 1

    end = time.time()
    out_file.write(f'{start = }\t{end = }\ttotal time = {end - start}')
    out_file.close()
    
    # save best player's weights for preview
    out_player = open('best_player.txt', 'w')
    for chromosome in best_players:
        gen, s, p, t = chromosome['gen'], chromosome['s'], chromosome['p'], chromosome['t']
        out_player.write(f'Best player of generation {gen} score = {s} time = {t}\n')
        out_player.write(f'input_hidden_ws = {p.input_hidden_ws}\nhidden_bs = {p.hidden_bs}\nhidden_ws2 = {p.hidden_ws2}\nhidden_bs2 = {p.hidden_bs2}\nhidden_output_ws = {p.hidden_output_ws}\noutput_bs = {p.output_bs}\n')
    out_player.close()

    
ga(105, mut_rate=0.3, cross_rate=0.6, max_iters=100, N = 10)
