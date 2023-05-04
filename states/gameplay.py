import pygame
import random
import spritesheet
import constants
from starfield import StarField

from .base_state import BaseState
from sprites.ai_player import AI_Player
from sprites.rocket import Rocket
from sprites.enemy import Enemy
from sprites.control_point import ControlPoint
from sprites.explosion import Explosion

from bezier.control_point_collection_factory import ControlPointCollectionFactory
from bezier.path_point_calculator import PathPointCalculator
from bezier.control_handler_mover import ControlHandlerMover
from bezier.path_point_selector import PathPointSelector
ADDENEMY = pygame.USEREVENT + 1
ENEMYSHOOTS = pygame.USEREVENT + 2
FREEZE = pygame.USEREVENT + 3

import math

class Gameplay(BaseState):
    def __init__(self, player:AI_Player=None):
        super(Gameplay, self).__init__()
        pygame.time.set_timer(ADDENEMY, 450)
        pygame.time.set_timer(ENEMYSHOOTS, 1000)
        pygame.time.set_timer(FREEZE, 2000)

        self.rect = pygame.Rect((0, 0), (80, 80))
        self.next_state = "GAME_OVER"
        self.sprites = spritesheet.SpriteSheet(constants.SPRITE_SHEET)
        self.explosion_sprites = spritesheet.SpriteSheet(constants.SPRITE_SHEET_EXPLOSION)
        self.starfield = StarField()
        self.control_points1 = ControlPointCollectionFactory.create_collection1()
        self.control_points2 = ControlPointCollectionFactory.create_collection2()
        self.control_points3 = ControlPointCollectionFactory.create_collection3()
        self.control_points4 = ControlPointCollectionFactory.create_collection4()
        self.path_point_selector = PathPointSelector(self.control_points1)
        self.path_point_selector.create_path_point_mapping()
        self.mover = ControlHandlerMover(self.control_points1, self.path_point_selector)
        self.control_sprites = pygame.sprite.Group()
        self.add_control_points()
        self.player = AI_Player(self.sprites,-1,-1,-1,-1) if not player else player
        self.player.start(spritesheet.SpriteSheet(constants.SPRITE_SHEET))
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        
        # Uncomment for player two
        # self.player2 = AI_Player(self.sprites,-1,-1,-1,-1)
        # self.all_sprites.add(self.player2)

        self.wave_count = 0
        self.enemies = 0
        self.number_of_enemies = 13
        # self.score = 0
        self.high_score = 0
        self.freeze = False

        self.all_enemies = pygame.sprite.Group()
        self.all_rockets = pygame.sprite.Group()
        self.enemy_rockets = pygame.sprite.Group()
        self.shoot_sound = pygame.mixer.Sound("./assets/sounds/13 Fighter Shot1.mp3")
        self.kill_sound = pygame.mixer.Sound("./assets/sounds/kill.mp3")
        self.show_control = False
        self.mover.align_all()

    def startup(self):
        pygame.mixer.music.load('./assets/sounds/02 Start Music.mp3')
        pygame.mixer.music.play()
        # NOTE: commented out this line to get game to initialize with given values in gameplay
        # self.player = AI_Player(-1,-1,-1,-1)
        self.all_sprites = pygame.sprite.Group()

        # Uncomment for player two
        # self.player2 = AI_Player(self.sprites,-1,-1,-1,-1)
        # self.all_sprites.add(self.player2)

        self.all_sprites.add(self.player)
        self.wave_count = 0
        self.enemies = 0
        self.number_of_enemies = 10
        # self.score = 0
        self.freeze = False

        self.all_enemies = pygame.sprite.Group()
        self.all_rockets = pygame.sprite.Group()
        self.enemy_rockets = pygame.sprite.Group()
        self.shoot_sound = pygame.mixer.Sound("./assets/sounds/13 Fighter Shot1.mp3")
        self.kill_sound = pygame.mixer.Sound("./assets/sounds/kill.mp3")
        self.show_control = False
        self.mover.align_all()

    def add_control_points(self):
        for quartet_index in range(self.control_points1.number_of_quartets()):
            for point_index in range(4):
                quartet = self.control_points1.get_quartet(quartet_index)
                point = quartet.get_point(point_index)
                self.control_sprites.add(ControlPoint(
                    point.x, point.y, (255, 120, 120), quartet_index, point_index,
                    self.control_points1, self.mover))

    def get_event(self, event):
        for entity in self.all_sprites:
            entity.get_event(event)

        if event.type == pygame.QUIT:
            self.quit = True
        if event.type == ADDENEMY:
            if self.enemies < self.number_of_enemies:
                self.add_enemy()
            elif len(self.all_enemies) == 0:
                self.enemies = 0
                self.wave_count += 1
                if self.wave_count > 2:
                    self.wave_count = 0
        if event.type == ENEMYSHOOTS:
            self.enemy_shoots()
        if event.type == FREEZE:
            if self.freeze:
                self.done = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                self.control_points1.save_control_points()
                self.done = True
            if event.key == pygame.K_s:
                self.show_control = not self.show_control
            if event.key == pygame.K_SPACE:
                if len(self.all_rockets) < 2:
                    self.shoot_rocket()

    def add_enemy(self):
        self.enemies += 1
        if self.wave_count == 0:
            enemy1 = Enemy(self.sprites, self.control_points1, self.wave_count)
            enemy2 = Enemy(self.sprites, self.control_points2, self.wave_count)
        else:
            enemy1 = Enemy(self.sprites, self.control_points3, self.wave_count)
            enemy2 = Enemy(self.sprites, self.control_points4, self.wave_count)

        self.all_enemies.add(enemy1)
        self.all_sprites.add(enemy1)
        self.all_enemies.add(enemy2)
        self.all_sprites.add(enemy2)

    def shoot_rocket(self):
        rocket = Rocket(self.sprites, 0, -15)
        rocket.rect.centerx = self.player.rect.centerx
        self.all_rockets.add(rocket)
        self.all_sprites.add(rocket)
        self.shoot_sound.play()

    def enemy_shoots(self):
        nr_of_enemies = len(self.all_enemies)
        if nr_of_enemies > 0:
            enemy_index = random.randint(0, nr_of_enemies - 1)
            start_rocket = None
            for index, enemy in enumerate(self.all_enemies):
                if index == enemy_index:
                    start_rocket = enemy.rect.center

            if start_rocket[1] < 400:
                ySpeed = 7
                dx = self.player.rect.centerx - start_rocket[0]
                dy = self.player.rect.centery - start_rocket[1]

                number_of_steps = dy / ySpeed
                xSpeed = dx / number_of_steps

                rocket = Rocket(self.sprites, xSpeed, ySpeed)
                rocket.rect.centerx = start_rocket[0]
                rocket.rect.centery = start_rocket[1]

                self.enemy_rockets.add(rocket)
                self.all_sprites.add(rocket)

    def draw(self, screen):
        self.starfield.render(screen)
        # pressed_keys = pygame.key.get_pressed()
        for entity in self.all_sprites:
            if type(entity) == AI_Player: continue
            entity.update(None)

        for entity in self.control_sprites:
            if type(entity) == AI_Player: continue
            entity.update(None)

        for entity in self.all_sprites:
            screen.blit(entity.get_surf(), entity.rect)

        # if self.show_control:
        #     for entity in self.control_sprites:
        #         screen.blit(entity.get_surf(), entity.rect)

        #     self.drawPath(screen)
        #     self.draw_control_lines(screen)

        self.draw_score(screen)

        # Draw info to screen
        self.draw_info(screen)

        # Get info and pass it to AI
        player_x, player_y = self.get_player_info()
        enemy1_coords, enemy2_coords = self.get_closest_enemies(player_x, player_y)
        rocket1_coords, rocket2_coords, rocket3_coords = self.get_closest_rockets(player_x, player_y)
        dist_to_left, dist_to_right = self.player.rect.left, (constants.SCREEN_WIDTH - self.player.rect.right)
        shoot = self.player.update(player_x, player_y, enemy1_coords, enemy2_coords, rocket1_coords, rocket2_coords, rocket3_coords, dist_to_left, dist_to_right)
        if shoot and len(self.all_rockets) < 2: self.shoot_rocket()

        # Uncomment for player two
        # player2_x, player2_y = self.player2.rect.x, self.player2.rect.y
        # enemy1_coords, enemy2_coords = self.get_closest_enemies(player2_x, player2_y)
        # rocket1_coords, rocket2_coords, rocket3_coords = self.get_closest_rockets(player2_x, player2_y)
        # shoot = self.player2.update(player2_x, player2_y, enemy1_coords, enemy2_coords, rocket1_coords, rocket2_coords, rocket3_coords)
        # # if shoot and len(self.all_rockets) < 2: self.shoot_rocket()

        result = pygame.sprite.groupcollide(self.all_rockets, self.all_enemies, True, True)
        if result:
            for key in result:
                self.player.score += 120
                if self.player.score > self.high_score:
                    self.high_score = self.player.score
                self.all_sprites.add(Explosion(self.explosion_sprites, key.rect[0], key.rect[1]))
                self.kill_sound.play()

        result = pygame.sprite.spritecollideany(self.player, self.enemy_rockets)
        if result:
            self.all_sprites.add(Explosion(self.explosion_sprites, result.rect[0], result.rect[1]))
            self.all_sprites.add(Explosion(self.explosion_sprites, result.rect[0] - 30, result.rect[1] - 30))
            self.all_sprites.add(Explosion(self.explosion_sprites, result.rect[0] + 30, result.rect[1] + 30))
            self.all_sprites.add(Explosion(self.explosion_sprites, result.rect[0], result.rect[1] - 30))
            self.kill_sound.play()
            self.freeze = True
            self.player.kill()

    def drawPath(self, screen):
        calculator = PathPointCalculator()
        bezier_timer = 0
        previous_path_point = None
        while bezier_timer < self.control_points1.number_of_quartets():
            control_point_index = int(bezier_timer)
            path_point = calculator.calculate_path_point(
                self.control_points1.get_quartet(control_point_index), bezier_timer)
            if previous_path_point is None:
                previous_path_point = path_point

            pygame.draw.line(screen, (255, 255, 255), (previous_path_point.xpos,
                             previous_path_point.ypos), (path_point.xpos, path_point.ypos))
            previous_path_point = path_point
            bezier_timer += 0.005

    def draw_control_lines(self, screen):
        for pair in self.path_point_selector.get_control_point_pairs():
            pygame.draw.line(screen, (255, 255, 255), pair[0], pair[1])

    def draw_score(self, screen):
        score = self.font.render('SCORE', True, (255, 20, 20))
        screen.blit(score, (constants.SCREEN_WIDTH / 2 - 300 - score.get_rect().width / 2, 10))
        score = self.font.render(str(self.high_score), True, (255, 255, 255))
        screen.blit(score, (constants.SCREEN_WIDTH / 2 - 300 - score.get_rect().width / 2, 40))

        score = self.font.render('HIGH SCORE', True, (255, 20, 20))
        screen.blit(score, (constants.SCREEN_WIDTH / 2 - score.get_rect().width / 2, 10))
        score = self.font.render(str(self.high_score), True, (255, 255, 255))
        screen.blit(score, (constants.SCREEN_WIDTH / 2 - score.get_rect().width / 2, 40))


    def get_player_info(self):
        return self.player.rect.x, self.player.rect.y
    
    
    def get_closest_enemies(self, player_x, player_y):
        closest_enemy_1, closest_enemy_1_coords = float('inf'), []
        closest_enemy_2, closest_enemy_2_coords = float('inf'), []
        
        for enemy in self.all_enemies:
            enemy_x, enemy_y = enemy.rect.x, enemy.rect.y
            pyth_a, pyth_b = (player_x - enemy_x) ** 2, (player_y - enemy_y) ** 2
            distance = math.sqrt(pyth_a + pyth_b)
            
            if distance < closest_enemy_1: 
                closest_enemy_1 = distance
                closest_enemy_1_coords = [enemy_x, enemy_y]
            elif distance < closest_enemy_2:
                closest_enemy_2 = distance
                closest_enemy_2_coords = [enemy_x, enemy_y]
                
        if closest_enemy_1_coords == []: closest_enemy_1_coords = [-1, -1]
        if closest_enemy_2_coords == []: closest_enemy_2_coords = [-1, -1]
        return closest_enemy_1_coords, closest_enemy_2_coords
    
    def get_closest_rockets(self, player_x, player_y):
        closest_rocket_1, closest_rocket_1_coords = float('inf'), []
        closest_rocket_2, closest_rocket_2_coords = float('inf'), []
        closest_rocket_3, closest_rocket_3_coords = float('inf'), []

        for rocket in self.enemy_rockets:
            rocket_x, rocket_y = rocket.rect.x, rocket.rect.y

            pyth_a, pyth_b = (player_x - rocket_x) ** 2, (player_y - rocket_y) ** 2
            distance = math.sqrt(pyth_a + pyth_b)

            if distance < closest_rocket_1: 
                closest_rocket_1 = distance
                closest_rocket_1_coords = [rocket_x, rocket_y]
            elif distance < closest_rocket_2: 
                closest_rocket_2 = distance
                closest_rocket_2_coords = [rocket_x, rocket_y]
            elif distance < closest_rocket_3: 
                closest_rocket_3 = distance
                closest_rocket_3_coords = [rocket_x, rocket_y]
                
        if closest_rocket_1_coords == []: closest_rocket_1_coords = [-1,-1]
        if closest_rocket_2_coords == []: closest_rocket_2_coords = [-1,-1]
        if closest_rocket_3_coords == []: closest_rocket_3_coords = [-1,-1]
        return closest_rocket_1_coords, closest_rocket_2_coords, closest_rocket_3_coords


    def draw_rocket_info(self, screen, player_x, player_y, r1_coords, r2_coords, r3_coords):
        new_font = pygame.font.Font(None, 25)
        rocket_info_y = 625
        if r1_coords:
            x, y = r1_coords
            rocket_1_info = new_font.render(f"Closest Rocket 1: {x}, {y}", True, (255,0,0))
            screen.blit(rocket_1_info, (10, 625))
            pygame.draw.line(screen, (255,0,0), (player_x, player_y), (x,y))
        if r2_coords:
            x, y = r2_coords
            rocket_2_info = new_font.render(f"Closest Rocket 2: {x}, {y}", True, (255,0,0))
            screen.blit(rocket_2_info, (10, 650))
            pygame.draw.line(screen, (255,0,0), (player_x, player_y), (x,y))

        if r3_coords:
            x, y = r3_coords
            rocket_3_info = new_font.render(f"Closest Rocket 3: {x}, {y}", True, (255,0,0))
            screen.blit(rocket_3_info, (10, 675))
            pygame.draw.line(screen, (255,0,0), (player_x, player_y), (x,y))
    
    
    def draw_closest_enemies(self, screen, player_x, player_y, e1_coords, e2_coords):
        new_font = pygame.font.Font(None, 25)
        if e1_coords:
            x, y = e1_coords
            enemy_1_info = new_font.render(f"Closest Enemy 1: {x}, {y}", True, (0,0,255))
            screen.blit(enemy_1_info, (10, 575))
            pygame.draw.line(screen, (0,0,255), (player_x, player_y), (x, y))
            
        if e2_coords:
            x, y = e2_coords
            enemy_1_info = new_font.render(f"Closest Enemy 2: {x}, {y}", True, (0,0,255))
            screen.blit(enemy_1_info, (10, 600))
            pygame.draw.line(screen, (0,0,255), (player_x, player_y), (x, y))
            

    def draw_info(self, screen):
        new_font = pygame.font.Font(None, 25)
        player_x, player_y = self.get_player_info()
        
        # write player coords
        player_info = new_font.render(f"Player coords: ({player_x}, {player_y})", True, (255,255,255))
        screen.blit(player_info, (10, 550))

        e1_coords, e2_coords = self.get_closest_enemies(player_x, player_y)
        self.draw_closest_enemies(screen, player_x, player_y, e1_coords, e2_coords)
        r1_coords, r2_coords, r3_coords = self.get_closest_rockets(player_x, player_y)
        self.draw_rocket_info(screen, player_x, player_y, r1_coords, r2_coords, r3_coords)
        
        
       