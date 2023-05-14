import pygame
import random
import spritesheet
import constants

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
KILLALL = pygame.USEREVENT + 4

import math

class Gameplay(BaseState):
    def __init__(self, players: list):
        super(Gameplay, self).__init__()
        # pygame.time.set_timer(ADDENEMY, 450)
        # pygame.time.set_timer(ENEMYSHOOTS, 1000)
        pygame.time.set_timer(FREEZE, 1000)
        self.addenemy_timer = 0
        self.enemyshoots_timer = 0
        self.total_updates = 0

        self.rect = pygame.Rect((0, 0), (80, 80))
        self.next_state = "GAME_OVER"
        self.sprites = spritesheet.SpriteSheet(constants.SPRITE_SHEET)
        self.explosion_sprites = spritesheet.SpriteSheet(constants.SPRITE_SHEET_EXPLOSION)
        self.control_points1 = ControlPointCollectionFactory.create_collection1()
        self.control_points2 = ControlPointCollectionFactory.create_collection2()
        self.control_points3 = ControlPointCollectionFactory.create_collection3()
        self.control_points4 = ControlPointCollectionFactory.create_collection4()
        self.path_point_selector = PathPointSelector(self.control_points1)
        self.path_point_selector.create_path_point_mapping()
        self.mover = ControlHandlerMover(self.control_points1, self.path_point_selector)
        self.control_sprites = pygame.sprite.Group()
        self.add_control_points()
        
        self.all_sprites = pygame.sprite.Group()
        self.players = players
        player_num = 1
        for player in self.players:
            player.start(spritesheet.SpriteSheet(constants.SPRITE_SHEET))
            self.all_sprites.add(player)
            player.player_num = player_num
            player_num += 1

        # self.player.start(spritesheet.SpriteSheet(constants.SPRITE_SHEET))
        # self.all_sprites = pygame.sprite.Group()
        # self.all_sprites.add(self.player)            

        self.wave_count = 0
        self.enemies = 0
        self.number_of_enemies = 13
        self.high_score = 0
        # self.freeze = False

        self.all_enemies = pygame.sprite.Group()
        # self.all_rockets = pygame.sprite.Group()
        self.enemy_rockets = pygame.sprite.Group()
        # self.shoot_sound = pygame.mixer.Sound("./assets/sounds/13 Fighter Shot1.mp3")
        # self.kill_sound = pygame.mixer.Sound("./assets/sounds/kill.mp3")
        self.show_control = False
        self.mover.align_all()

    def startup(self):
        pass
        # pygame.mixer.music.load('./assets/sounds/02 Start Music.mp3')
        # pygame.mixer.music.play()
        # # NOTE: commented out this line to get game to initialize with given values in gameplay
        # # self.player = AI_Player(-1,-1,-1,-1)
        # self.all_sprites = pygame.sprite.Group()
        # player_num = 1
        # for player in self.players:
        #     self.all_sprites.add(player)
        #     player.player_num = player_num
        #     player_num += 1

        # self.wave_count = 0
        # self.enemies = 0
        # self.number_of_enemies = 10
        # # self.freeze = False

        # self.all_enemies = pygame.sprite.Group()
        # self.enemy_rockets = pygame.sprite.Group()
        # self.shoot_sound = pygame.mixer.Sound("./assets/sounds/13 Fighter Shot1.mp3")
        # self.kill_sound = pygame.mixer.Sound("./assets/sounds/kill.mp3")
        # self.show_control = False
        # self.mover.align_all()

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
            self.done = True
            for player in self.players:
                if not player.freeze:
                    self.done = False
        if event.type == KILLALL:
            self.done = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                self.control_points1.save_control_points()
                self.done = True

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

        for player in self.players:
            player.available_enemies.add(enemy1)
            player.available_enemies.add(enemy2)

    def shoot_rocket(self, player):
        rocket = Rocket(self.sprites, 0, -15, player.player_num)
        rocket.rect.centerx = player.rect.centerx
        player.rockets.add(rocket)
        # self.all_rockets.add(rocket)
        self.all_sprites.add(rocket)
        # self.shoot_sound.play()

    def enemy_shoots(self):
        for player in self.players:
            if not player.freeze:
                nr_of_enemies = len(self.all_enemies)
                if nr_of_enemies > 0:
                    enemy_index = random.randint(0, nr_of_enemies - 1)
                    start_rocket = None
                    for index, enemy in enumerate(self.all_enemies):
                        if index == enemy_index:
                            start_rocket = enemy.rect.center

                    if start_rocket[1] < 400:
                        ySpeed = 7
                        dx = player.rect.centerx - start_rocket[0]
                        dy = player.rect.centery - start_rocket[1]

                        number_of_steps = dy / ySpeed
                        xSpeed = dx / number_of_steps

                        rocket = Rocket(self.sprites, xSpeed, ySpeed, player.player_num)
                        rocket.rect.centerx = start_rocket[0]
                        rocket.rect.centery = start_rocket[1]

                        self.enemy_rockets.add(rocket)
                        self.all_sprites.add(rocket)
                        player.targeted_rockets.add(rocket)

    def draw(self, screen):
        self.total_updates += 1
        self.addenemy_timer += 1
        self.enemyshoots_timer += 1
        if self.addenemy_timer == 8: 
            pygame.event.post(pygame.event.Event(ADDENEMY))
            self.addenemy_timer = 0
        if self.enemyshoots_timer == 17: 
            pygame.event.post(pygame.event.Event(ENEMYSHOOTS))
            self.enemyshoots_timer = 0
        if self.total_updates == 15000:
            pygame.event.post(pygame.event.Event(KILLALL))

        for entity in self.all_sprites:
            if type(entity) == AI_Player: continue
            entity.update(None)

        for entity in self.control_sprites:
            if type(entity) == AI_Player: continue
            entity.update(None)

        for entity in self.all_sprites:
            screen.blit(entity.get_surf(), entity.rect)
            if type(entity) == Rocket or type(entity) == AI_Player:
                text = self.font.render(f"{entity.player_num}", True, (255,0,0))
                if entity.player_num == 1:
                    screen.blit(text, (entity.rect.center[0]-15, entity.rect.center[1]))
                else: screen.blit(text, (entity.rect.center[0], entity.rect.center[1]))

        text = self.font.render(f'{self.total_updates}', True, (255,0,0))
        screen.blit(text, (900, 10))    

        # if self.show_control:
        #     for entity in self.control_sprites:
        #         screen.blit(entity.get_surf(), entity.rect)

        #     self.drawPath(screen)
        #     self.draw_control_lines(screen)

        self.draw_score(screen)

        # Draw info to screen
        # self.draw_info(screen)

        # Get info and pass it to AI
        for player in self.players:
            if player.kill_countdown <= 0:
                player.freeze = True
                player.kill()
    
            if not player.freeze:
                player_x, player_y = self.get_player_info(player)
                enemy1_coords, enemy2_coords = self.get_closest_enemies(player_x, player_y)
                rocket1_coords, rocket2_coords, rocket3_coords = self.get_closest_rockets(player_x, player_y)
                dist_to_left, dist_to_right = player.rect.left, (constants.SCREEN_WIDTH - player.rect.right)
                # can_move_left = 1 if player.rect.left > 0 else 0
                # can_move_right = 1 if (constants.SCREEN_WIDTH - player.rect.right) > 0 else 0
                shoot = player.update(player_x, player_y, enemy1_coords, enemy2_coords, rocket1_coords, rocket2_coords, rocket3_coords, dist_to_left, dist_to_right)
                if shoot and len(player.rockets) < 2: self.shoot_rocket(player)

        for player in self.players:
            if not player.freeze:
                result = pygame.sprite.groupcollide(player.rockets, player.available_enemies, True, False)
                if result:
                    player.kill_countdown += 100
                    for key in result:
                        cur_enemy = result[key][0]
                        player.score += 120
                        cur_enemy.remove(player.available_enemies)
                        cur_enemy.times_hit += 1
                        if cur_enemy.times_hit == len(self.players): cur_enemy.kill()

                        # if self.player.score > self.high_score:
                        #     self.high_score = self.player.score
                        
                        # self.all_sprites.add(Explosion(self.explosion_sprites, key.rect[0], key.rect[1]))

        for player in self.players:
            if not player.freeze:
                result = pygame.sprite.spritecollideany(player, player.targeted_rockets)
                if result:
                    # self.all_sprites.add(Explosion(self.explosion_sprites, result.rect[0], result.rect[1]))
                    player.freeze = True
                    player.kill()

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
        score_y = 10
        for num, player in enumerate(self.players):
            font = pygame.font.Font(None, 15)
            score = font.render(f"Player {num+1} score: {player.score}", True, (255, 255, 255))
            screen.blit(score, (10, score_y))
            score_y += 15


        # score = self.font.render('SCORE', True, (255, 20, 20))
        # screen.blit(score, (constants.SCREEN_WIDTH / 2 - 300 - score.get_rect().width / 2, 10))
        # score = self.font.render(str(self.high_score), True, (255, 255, 255))
        # screen.blit(score, (constants.SCREEN_WIDTH / 2 - 300 - score.get_rect().width / 2, 40))

        # score = self.font.render('HIGH SCORE', True, (255, 20, 20))
        # screen.blit(score, (constants.SCREEN_WIDTH / 2 - score.get_rect().width / 2, 10))
        # score = self.font.render(str(self.high_score), True, (255, 255, 255))
        # screen.blit(score, (constants.SCREEN_WIDTH / 2 - score.get_rect().width / 2, 40))


    def get_player_info(self, player):
        return player.rect.x, player.rect.y
    
    
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
        
        
       