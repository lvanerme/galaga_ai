import pygame
import numpy as np
from sprites.player import Player
from keras import Input
from keras import Sequential
from keras.layers import Dense

class AI_Player(Player):
    def __init__(self, sprites, k1, k2, b1, b2):
        super().__init__(sprites)
        self.model = self.configure_model(k1, k2, b1, b2)
    
    def update(self, player_x, player_y, enemy1_coords, enemy2_coords, rocket1_coords, rocket2_coords, rocket3_coords):
        e1_x, e1_y = enemy1_coords
        e2_x, e2_y = enemy2_coords
        r1_x, r1_y = rocket1_coords
        r2_x, r2_y = rocket2_coords
        r3_x, r3_y = rocket3_coords

        data_array = [player_x, player_y, e1_x, e1_y, e2_x, e2_y, r1_x, r1_y, r2_x, r2_y, r3_x, r3_y]
        # results = self.model.__call__(data_array)
        results = self.model.predict(data_array, batch_size=12)
        move = np.argmax(results)

        if move == 0: self.rect.move_ip(-5, 0)      # Left
        elif move == 1: self.rect.move_ip(5,0)      # Right
        elif move == 3: return True                 # Shoot rocket
        else: return False                          # Stay still

    def configure_model(self, k1, k2, b1, b2):
        model = Sequential()
        model.add(Input(shape=(12,)))
        model.add(Dense(units=8, activation = 'sigmoid'))
        model.add(Dense(units=4, activation = 'relu'))
        # model.layers[0].set_weights([k1, b1])
        # model.layers[1].set_weights([k2, b2])

        model.compile(loss = 'categorical_crossentropy', optimizer = 'adam')
        print(model.summary())

        return model