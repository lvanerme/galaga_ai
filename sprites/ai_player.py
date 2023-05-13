import numpy as np
import constants
import tensorflow as tf

from keras import Input
from keras import Sequential
from keras.layers import Dense
from re import split as resplit
from sprites.player import Player
from main import play_game


class AI_Player(Player):
    def __init__(self, input_hidden_ws: list, hidden_bs: list, hidden_ws2: list, hidden_bs2: list, hidden_output_ws: list, output_bs: list):
        # NOTE: keep track of lengths here
        # super().__init__(sprites)
        self.input_hidden_ws = input_hidden_ws
        self.hidden_bs = hidden_bs
        self.hidden_ws2 = hidden_ws2
        self.hidden_bs2 = hidden_bs2
        self.hidden_output_ws = hidden_output_ws
        self.output_bs = output_bs
        self.model = self.configure_model(input_hidden_ws, hidden_bs, hidden_ws2, hidden_bs2, hidden_output_ws, output_bs)
        self.updates_survived = 0
        self.player_num = 0
    
    
    def start(self, sprites):
        super().__init__(sprites)
    
    
    def get_event(self, event):
        pass
    
    
    def update(self, player_x, player_y, enemy1_coords, enemy2_coords, rocket1_coords, rocket2_coords, rocket3_coords, dist_to_left, dist_to_right):
        self.updates_survived += 1          # TODO: timeout at certain point...
        
        e1_x, e1_y = enemy1_coords
        e2_x, e2_y = enemy2_coords
        r1_x, r1_y = rocket1_coords
        r2_x, r2_y = rocket2_coords
        r3_x, r3_y = rocket3_coords

        data_array = np.array([player_x, player_y, e1_x, e1_y, e2_x, e2_y, r1_x, r1_y, r2_x, r2_y, r3_x, r3_y, dist_to_left, dist_to_right], dtype='int64')
        data_array = data_array.reshape(1,-1)
        results = self.model(data_array, training=False)
        # results = self.model.predict(data_array, verbose=0)
        move = np.argmax(results)

        if move == 0: self.rect.move_ip(-5, 0)       # Left
        elif move == 1: self.rect.move_ip(5, 0)      # Right
        
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > constants.SCREEN_WIDTH: self.rect.right = constants.SCREEN_WIDTH
            
        return move == 3        # Shoot rocket else stay still


    def configure_model(self, input_hidden_ws, hidden_bs, hidden_ws2, hidden_bs2, hidden_output_ws, output_bs):
        model = Sequential()
        model.add(Input((14, )))
        model.add(Dense(units=8, activation = 'sigmoid'))
        model.add(Dense(units=6, activation = 'sigmoid'))
        model.add(Dense(units=4, activation = 'relu'))
        
        hidden_weights = [np.array(input_hidden_ws).reshape(14,8), np.array(hidden_bs)]
        hidden_weights2 = [np.array(hidden_ws2).reshape(8,6), np.array(hidden_bs2)]
        output_weights = [np.array(hidden_output_ws).reshape(6,4), np.array(output_bs)]
        # hidden_weights = np.array([input_hidden_ws, hidden_bs]).reshape(12, 8)
        # output_weights = np.array([hidden_output_ws, output_bs]).reshape(8, 4)
        model.layers[0].set_weights(hidden_weights)
        model.layers[1].set_weights(hidden_weights2)
        model.layers[2].set_weights(output_weights)

        model.compile(loss = 'categorical_crossentropy', optimizer = 'adam')
        return model
    
    
    def test_model(self, filename: str):
        data, players, player_metadata = open(filename, 'r').read().splitlines(), [], []
        for i in range(0, len(data), 7):    # currently 6 sets of weights in NN
            all_weights = []
            metadata = data[i].split()
            player_metadata.append([metadata[5], metadata[7]])
            for j in range(i+1, i+7):
                weights_str, weights_float = resplit('\[|\]', data[j])[1].split(','), []
                for w in weights_str: weights_float.append(float(w))
                all_weights.append(weights_float)
            input_hidden_ws, hidden_bs, hidden_ws2, hidden_bs2, hidden_output_ws, output_bs = all_weights
            players.append(AI_Player(input_hidden_ws, hidden_bs, hidden_ws2, hidden_bs2, hidden_output_ws, output_bs))
        
        for p in range(len(players)):
            gen, score = player_metadata[p] 
            print(f'{gen = }\t{score = }')
            play_game([players[p]], show=True)   # play each player individually...TODO: show generation of individual?
            
    def test_model_old(self, filename: str):
        data, players = open(filename, 'r').read().splitlines(), []
        for i in range(0, len(data), 6):    # currently 6 sets of weights in NN
            all_weights = []
            for j in range(i, i+6):
                weights_str, weights_float = resplit('\[|\]', data[j])[1].split(','), []
                for w in weights_str: weights_float.append(float(w))
                all_weights.append(weights_float)
            input_hidden_ws, hidden_bs, hidden_ws2, hidden_bs2, hidden_output_ws, output_bs = all_weights
            players.append(AI_Player(input_hidden_ws, hidden_bs, hidden_ws2, hidden_bs2, hidden_output_ws, output_bs))
        
        for player in range(players):
            play_game([player], show=True)   # play each player individually...TODO: show generation of individual?
