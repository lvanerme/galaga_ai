import sys
import pygame

from states.menu import Menu
from states.gameplay import Gameplay
from states.game_over import GameOver
from states.splash import Splash
from game import Game
import constants

def play_game(players=None, show=False):
    # setup mixer to avoid sound lag
    # pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()
    # pygame.mixer.init()
    if show: screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
    else: screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), flags=pygame.HIDDEN)
    
    states = {
        # "MENU": Menu(),
        "SPLASH": Splash(),
        "GAMEPLAY": Gameplay(players),
        "GAME_OVER": GameOver(),
    }

    game = Game(screen, states, "GAMEPLAY")
    game.run()
    pygame.quit()
    # sys.exit()


# play_game()