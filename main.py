import random
import os
import pygame
from pygame.constants import QUIT, K_DOWN, K_UP, K_LEFT, K_RIGHT, K_r
import json

pygame.init()

FPS = pygame.time.Clock()

HEIGHT = 800
WIDTH = 1200

FONT = pygame.font.SysFont('Verdana', 20)

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_BLUE = (0, 0, 255)

main_display = pygame.display.set_mode((WIDTH, HEIGHT))

bg = pygame.transform.scale(pygame.image.load('background.png'), (WIDTH, HEIGHT))
bg_X1 = 0
bg_X2 = bg.get_width()
bg_move = 3

IMAGE_PATH = "Goose"
PLAYER_IMAGES = os.listdir(IMAGE_PATH)

player_size = (20, 20)
player = pygame.image.load("player.png").convert_alpha()
player_rect = player.get_rect()
player_rect.topleft = (20, HEIGHT // 2)  

player_move_down = [0, 4]
player_move_right = [4, 0]
player_move_left = [-4, 0]
player_move_up = [0, -4]

def create_enemy():
    enemy = pygame.image.load("enemy.png").convert_alpha()
    enemy_rect = enemy.get_rect()
    enemy_rect.x = WIDTH
    enemy_rect.y = random.randint(20, HEIGHT - enemy_rect.height - 20)
    enemy_speed = [-random.uniform(4.0, 6.0), 0]
    return [enemy, enemy_rect, enemy_speed]

def create_bonus():
    bonus_size = (20, 20)
    bonus = pygame.image.load('bonus.png').convert_alpha()
    bonus_rect = bonus.get_rect()
    bonus_rect.x = random.randint(20, WIDTH - bonus_rect.width - 20)
    bonus_rect.y = -bonus_rect.height
    bonus_speed = [0, random.uniform(2.0, 3.0)]
    return [bonus, bonus_rect, bonus_speed]

CREATE_ENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(CREATE_ENEMY, random.randint(1000, 3000))

CREATE_BONUS = pygame.USEREVENT + 2
pygame.time.set_timer(CREATE_BONUS, 2200)

CHANGE_IMAGE = pygame.USEREVENT + 3
pygame.time.set_timer(CHANGE_IMAGE, 250)

enemies = []
bonuses = []

score = 0
best_score = 0

try:
    with open('best_score.json', 'r') as file:
        best_score = json.load(file)
except FileNotFoundError:
    pass

best_score_text = FONT.render("Best: " + str(best_score), True, COLOR_BLACK)

image_index = 0
game_over = False

while not game_over:
    FPS.tick(120)

    for event in pygame.event.get():
        if event.type == QUIT:
            game_over = True
        if event.type == CREATE_ENEMY:
            enemies.append(create_enemy())
        if event.type == CREATE_BONUS:
            bonuses.append(create_bonus())
        if event.type == CHANGE_IMAGE:
            player = pygame.image.load(os.path.join(IMAGE_PATH, PLAYER_IMAGES[image_index]))
            image_index += 1
            if image_index >= len(PLAYER_IMAGES):
                image_index = 0

    bg_X1 -= bg_move
    bg_X2 -= bg_move

    if bg_X1 < -bg.get_width():
        bg_X1 = bg.get_width()

    if bg_X2 < -bg.get_width():
        bg_X2 = bg.get_width()

    main_display.blit(bg, (bg_X1, 0))
    main_display.blit(bg, (bg_X2, 0))

    keys = pygame.key.get_pressed()

    if keys[K_DOWN] and player_rect.bottom < HEIGHT:
        player_rect = player_rect.move(player_move_down)

    if keys[K_RIGHT] and player_rect.right < WIDTH:
        player_rect = player_rect.move(player_move_right)

    if keys[K_UP] and player_rect.top > 0:
        player_rect = player_rect.move(player_move_up)

    if keys[K_LEFT] and player_rect.left > 0:
        player_rect = player_rect.move(player_move_left)

    for enemy in enemies:
        enemy[1] = enemy[1].move(enemy[2])
        main_display.blit(enemy[0], enemy[1])

        if player_rect.colliderect(enemy[1]):
            game_over = True

    for bonus in bonuses:
        bonus[1] = bonus[1].move(bonus[2])
        main_display.blit(bonus[0], bonus[1])

        if player_rect.colliderect(bonus[1]):
            score += 1
            bonuses.pop(bonuses.index(bonus))

    if score > best_score:
        best_score = score
        best_score_text = FONT.render("Best: " + str(best_score), True, COLOR_BLACK)

    main_display.blit(FONT.render("Score: " + str(score), True, COLOR_BLACK), (20, 20))
    main_display.blit(best_score_text, (WIDTH - 100, 20))
    main_display.blit(player, player_rect)

    pygame.display.flip()

    if game_over:
        main_display.fill(COLOR_WHITE)
        restart_text = FONT.render("Press 'R' to restart", True, COLOR_BLACK)
        restart_rect = restart_text.get_rect()
        restart_rect.center = (WIDTH // 2, HEIGHT // 2)
        main_display.blit(restart_text, restart_rect)
        pygame.display.flip()

        waiting_for_restart = True
        while waiting_for_restart:
            for event in pygame.event.get():
                if event.type == QUIT:
                    waiting_for_restart = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    game_over = False
                    player_rect.topleft = (20, HEIGHT // 2)
                    score = 0
                    enemies.clear()
                    bonuses.clear()
                    waiting_for_restart = False

with open('best_score.json', 'w') as file:
    json.dump(best_score, file)
