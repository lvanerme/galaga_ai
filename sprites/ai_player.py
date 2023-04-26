import pygame
import numpy
import tensorflow as tf
from sprites.player import Player
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense


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

        data_array = numpy.array([player_x, player_y, e1_x, e1_y, e2_x, e2_y, r1_x, r1_y, r2_x, r2_y, r3_x, r3_y])
        results = self.model.predict(data_array)
        move = numpy.argmax(results)

        if move == 0:
            #Left
            self.rect.move_ip(-5, 0)
        elif move == 1:
            #Right
            self.rect.move_ip(5,0)
        # If 2 - do nothing
        elif move == 3:
            #Shoot rocket
            return True
        return False


    def configure_model(layer1_w, layer2_w, b1, b2):
        model = Sequential([
            Dense(units=8, activation = 'sigmoid'),
            Dense(units=4, activation = 'relu')
        ])
        # model.layers[0].set_weights([k1, b1])
        # model.layers[1].set_weights([k2, b2])

        model.compile(loss = 'categorical_crossentropy', optimizer = 'adam')

        return model
    
# w = tf.Variable(initial_value=w_init(shape=(12,), dtype='float32'), trainable=True)