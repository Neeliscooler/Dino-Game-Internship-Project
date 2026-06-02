"""
Dino Game in Python
A game similar to the famous Chrome Dino Game, built using pygame-ce.
Made by intern: @Neel Verma, no one or nothing else. 🤖
Overall Modifications: Added lives, post-hit invincibility, double jumping, power ups (Invincibility, Triple Jump, Time Slow, Egg Bomb, and Extra Life),
Coins, more enemies, On screen HUD(score and lives), and a game over screen which displays the highscore.

"""

import pygame
from sys import exit
from random import randint, choice

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption('Dino Runner')
clock = pygame.time.Clock()
running = True 

# Audio assets (IN PROGRESS!)
#bg_music = pygame.mixer.Sound('audio/music.wav')
#bg_music.play(loops = -1)
#jump_sound = pygame.mixer.Sound('audio/jump.mp3')
#jump_sound.set_volume(0.5)

# Game state variables
is_playing = True  
GROUND_Y = 300  
JUMP_GRAVITY_START_SPEED = -20  
players_gravity_speed = 0  
jump_count = 0  

# Difficulty and speed scaling
game_speed = 5  
difficulty_level = 0  

# Lives and invincibility variables
lives = 3  
invincible_timer = 0  
INVINCIBLE_DURATION = 1500  

# Power-up active timestamps
egg_clear_stocked_until = 0  # Screen clear with 'W'
slow_mo_until = 0            # Slow-Mo effect
triple_jump_until = 0         # Triple jump effect (15 seconds)

# Load background and font assets
SKY_SURF = pygame.image.load("graphics/level/sky.png").convert()
GROUND_SURF = pygame.image.load("graphics/level/ground.png").convert()
game_font = pygame.font.Font(pygame.font.get_default_font(), 50)
small_font = pygame.font.Font(pygame.font.get_default_font(), 20)  
score_surf = game_font.render("SCORE?", False, "Black")
score_rect = score_surf.get_rect(center=(400, 50))

# Load player assets
player_walk_1 = pygame.image.load("graphics/player/player_walk_1.png").convert_alpha()
player_walk_2 = pygame.image.load("graphics/player/player_walk_2.png").convert_alpha()
player_walk_list = [player_walk_1, player_walk_2]
player_index = 0.0  
player_jump = pygame.image.load('graphics/player/player_jump.png').convert_alpha()

player_surf = player_walk_list[int(player_index)]
player_rect = player_surf.get_rect(bottomleft=(25, GROUND_Y))

# Load egg assets
egg_1 = pygame.image.load("graphics/egg-enemies/egg_1.png").convert_alpha()
egg_2 = pygame.image.load("graphics/egg-enemies/egg_2.png").convert_alpha()
egg_list = [egg_1, egg_2]
egg_index = 0.0  

egg_surf = egg_list[int(egg_index)]
egg_rect = egg_surf.get_rect(bottomleft=(800, GROUND_Y))

# Load sunny side up assets
resize_sunnyside_up_1 = pygame.transform.scale(pygame.image.load("graphics/egg-enemies/sunnyside_up_1.png"), (100, 100)).convert_alpha()
resize_sunnyside_up_2 = pygame.transform.scale(pygame.image.load("graphics/egg-enemies/sunnyside_up_2.png"), (100, 100)).convert_alpha()

sunnyside_up_list = [resize_sunnyside_up_1, resize_sunnyside_up_2]
sunnyside_up_index = 0.0

# Load coin asset
coin_surf = pygame.image.load("graphics/collectibles/coin.png").convert_alpha()

obstacle_rect_list = []
powerup_rect_list = []  

# Custom timers for spawning
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)

powerup_timer = pygame.USEREVENT + 2
pygame.time.set_timer(powerup_timer, 40000)  # Spawns every 40 seconds

# Score tracking
high_score = 0
start_time = 0
score = 0


# GAME FUNCTIONS

def display_score():
    global score, score_surf, score_rect
    current_time = pygame.time.get_ticks() - start_time
    score = current_time // 1000  

    score_surf = game_font.render(f"SCORE: {score}", False, "Black")
    score_rect = score_surf.get_rect(center=(400, 50))

    pygame.draw.rect(screen, "#c0e8ec", score_rect)
    pygame.draw.rect(screen, "#c0e8ec", score_rect, 10)
    screen.blit(score_surf, score_rect)
    return score


def obstacle_movement(obstacle_list):
    if obstacle_list:
        for active_obs in obstacle_list:
            active_obs.x -= current_speed
            
        for active_obs in obstacle_list:
            if active_obs.bottom == GROUND_Y:
                screen.blit(egg_surf, active_obs)
            elif active_obs.bottom == 210:
                screen.blit(sunnyside_up_surf, active_obs)
            else:
                screen.blit(coin_surf, active_obs)

        obstacle_list = [obs for obs in obstacle_list if obs.right > 0]
        return obstacle_list
    else:
        return []


def collisions(player, obstacles):
    global lives, is_playing, high_score, invincible_timer, score
    if obstacles:
        for egg_rect in obstacles[:]:
            if egg_rect.colliderect(player):
                if egg_rect.bottom != GROUND_Y and egg_rect.bottom != 210:
                    score += 3
                    obstacles.remove(egg_rect)
                else:
                    if current_ticks >= invincible_timer:
                        lives -= 1
                        if lives <= 0:
                            is_playing = False
                            if score > high_score:
                                high_score = score
                        else:
                            invincible_timer = current_ticks + INVINCIBLE_DURATION
                            obstacles.remove(egg_rect)
                            break
        return is_playing
    return True


def player_animation():
    global player_index, player_surf
    if player_rect.bottom >= GROUND_Y:
        player_index += 0.15  
        if player_index >= len(player_walk_list):
            player_index = 0
        player_surf = player_walk_list[int(player_index)]
    else:
        player_surf = player_jump


# MAIN GAME LOOP

while running:
    current_ticks = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            exit()

        elif is_playing:
            # Press 'W' to use screen clear bomb
            if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                if current_ticks < egg_clear_stocked_until:
                    obstacle_rect_list = [obs for obs in obstacle_rect_list if obs.bottom not in (GROUND_Y, 210)]
                    egg_clear_stocked_until = 0  

            # Handle jumping (Space or Mouse Click)
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE 
                or event.type == pygame.MOUSEBUTTONDOWN):
                # Set jump limit based on active power-up status
                max_jumps = 3 if current_ticks < triple_jump_until else 2
                if player_rect.bottom >= GROUND_Y or jump_count < max_jumps:
                    players_gravity_speed = JUMP_GRAVITY_START_SPEED
                    #IN PROGRESS
                    #jump_sound.play()
                    jump_count += 1

            # Spawn obstacles
            if event.type == obstacle_timer:
                spawn_choice = choice(['sunnyside_up', 'egg', 'egg', 'egg', 'coin'])
                if spawn_choice == 'sunnyside_up':
                    obstacle_rect_list.append(sunnyside_up_list[0].get_rect(midbottom=(randint(900, 1100), 210)))
                elif spawn_choice == 'coin':
                    obstacle_rect_list.append(coin_surf.get_rect(midbottom=(randint(900, 1100), 150)))
                else:
                    obstacle_rect_list.append(egg_list[0].get_rect(midbottom=(randint(900, 1100), GROUND_Y)))

            # Spawn powerups
            if event.type == powerup_timer:
                p_type = choice(['invincible', 'heart', 'egg_clear', 'slow_mo', 'triple_jump'])
                p_rect = pygame.Rect(0, 0, 30, 30)
                p_rect.midbottom = (randint(900, 1100), GROUND_Y)
                powerup_rect_list.append({'rect': p_rect, 'type': p_type})

        else:
            # Restart game on SPACE press
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                is_playing = True
                egg_rect.left = 800
                obstacle_rect_list.clear()
                powerup_rect_list.clear()  
                
                # Reset powerup limits
                egg_clear_stocked_until = 0
                slow_mo_until = 0
                triple_jump_until = 0
                
                start_time = pygame.time.get_ticks()  
                score = 0  
                jump_count = 0  
                player_index = 0.0  
                egg_index = 0.0  
                lives = 3  
                invincible_timer = 0  
                game_speed = 5  
                difficulty_level = 0  
                pygame.time.set_timer(obstacle_timer, 1500)  
                pygame.time.set_timer(powerup_timer, 40000)  

    if is_playing:
        # Increase speed and spawn rates as score grows
        game_speed = 5 + (score // 10)
        new_level = score // 15
        if new_level > difficulty_level:
            difficulty_level = new_level
            pygame.time.set_timer(obstacle_timer, max(600, 1500 - (difficulty_level * 150)))

        # Handle slow motion speed reduction
        current_speed = game_speed // 2 if current_ticks < slow_mo_until else game_speed

        # Render background and score
        screen.blit(SKY_SURF, (0, 0))
        screen.blit(GROUND_SURF, (0, GROUND_Y))
        score = display_score()

        # Render lives section of screen
        lives_surf = game_font.render(f"LIVES: {lives}", False, "Red")
        lives_rect = lives_surf.get_rect(topright=(780, 20))
        screen.blit(lives_surf, lives_rect)

        # Move and clean up obstacles
        obstacle_rect_list = obstacle_movement(obstacle_rect_list)
            
        # Move powerup items
        for pu in powerup_rect_list:
            pu['rect'].x -= current_speed
        powerup_rect_list = [pu for pu in powerup_rect_list if pu['rect'].right > 0]

        # Handle sprite animations
        egg_index += 0.2  
        if egg_index >= len(egg_list): egg_index = 0
        egg_surf = egg_list[int(egg_index)]
        
        sunnyside_up_index += 0.05
        if sunnyside_up_index >= len(sunnyside_up_list): sunnyside_up_index = 0
        sunnyside_up_surf = sunnyside_up_list[int(sunnyside_up_index)]

        # Render active powerup tokens on screen
        for pu in powerup_rect_list:
            if pu['type'] == 'invincible': color, label = "Blue", "I"
            elif pu['type'] == 'heart': color, label = "Pink", "H"
            elif pu['type'] == 'egg_clear': color, label = "Purple", "W"
            elif pu['type'] == 'slow_mo': color, label = "Cyan", "S"
            elif pu['type'] == 'triple_jump': color, label = "Orange", "T"
            
            pygame.draw.circle(screen, color, pu['rect'].center, 15)
            lbl_surf = small_font.render(label, True, "White")
            lbl_rect = lbl_surf.get_rect(center=pu['rect'].center)
            screen.blit(lbl_surf, lbl_rect)

        # Apply gravity and update player vertical position
        players_gravity_speed += 1
        player_rect.y += players_gravity_speed
        
        if player_rect.bottom >= GROUND_Y:
            player_rect.bottom = GROUND_Y
            jump_count = 0  
        
        player_animation()
            
        # Handle invincibility flash/flicker effect
        if current_ticks < invincible_timer:
            if (current_ticks // 100) % 2 == 0:
                screen.blit(player_surf, player_rect)
        else:
            screen.blit(player_surf, player_rect)

        # Handle collecting powerups
        for pu in powerup_rect_list[:]:
            if player_rect.colliderect(pu['rect']):
                if pu['type'] == 'invincible':
                    invincible_timer = current_ticks + 15000  # 15s Invincibility
                elif pu['type'] == 'heart':
                    lives += 1                               # +1 Life
                elif pu['type'] == 'egg_clear':
                    egg_clear_stocked_until = current_ticks + 38000  # Held for 38s max
                elif pu['type'] == 'slow_mo':
                    slow_mo_until = current_ticks + 10000           # 10s Slow-Mo
                elif pu['type'] == 'triple_jump':
                    triple_jump_until = current_ticks + 15000       # 15s Triple Jump
                powerup_rect_list.remove(pu)

        # Check hazard hit collisions
        is_playing = collisions(player_rect, obstacle_rect_list)

        # Render Active Powerup Timers on Left side of screen
        hud_y = 80
        if current_ticks < invincible_timer and (invincible_timer - current_ticks) > INVINCIBLE_DURATION:
            rem = (invincible_timer - current_ticks) // 1000
            ui_surf = small_font.render(f"INVINCIBLE: {rem}s", True, "Blue")
            screen.blit(ui_surf, (20, hud_y))
            hud_y += 25
        if current_ticks < egg_clear_stocked_until:
            rem = (egg_clear_stocked_until - current_ticks) // 1000
            ui_surf = small_font.render(f"EGG BOMB READY [W]: {rem}s", True, "Purple")
            screen.blit(ui_surf, (20, hud_y))
            hud_y += 25
        if current_ticks < slow_mo_until:
            rem = (slow_mo_until - current_ticks) // 1000
            ui_surf = small_font.render(f"SLOW-MO MODIFIER: {rem}s", True, "Cyan")
            screen.blit(ui_surf, (20, hud_y))
            hud_y += 25
        if current_ticks < triple_jump_until:
            rem = (triple_jump_until - current_ticks) // 1000
            ui_surf = small_font.render(f"TRIPLE JUMP: {rem}s", True, "Orange")
            screen.blit(ui_surf, (20, hud_y))
            hud_y += 25

    # Game Over screen assets
    else:
        screen.fill("black")

        game_over_surf = game_font.render("GAME OVER!", False, "Red")
        game_over_rect = game_over_surf.get_rect(center=(400, 100))
        
        high_score_surf = game_font.render(f"HIGH SCORE: {high_score}", False, "White")
        high_score_rect = high_score_surf.get_rect(center=(400, 200))
        
        restart_surf = game_font.render("Press SPACE to Play Again", False, "Gray")
        restart_rect = restart_surf.get_rect(center=(400, 300))

        screen.blit(game_over_surf, game_over_rect)
        screen.blit(high_score_surf, high_score_rect)
        screen.blit(restart_surf, restart_rect)

    pygame.display.update()
    clock.tick(60)  

pygame.quit()