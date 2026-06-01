"""
Dino Game in Python
A game similar to the famous Chrome Dino Game, built using pygame-ce.
Made by intern: @Neel Verma, no one or nothing else. 🤖
Modifications: Dynamic powerup mechanics and HUD status meters added.
"""

import pygame
from sys import exit
from random import randint, choice

# Initialize Pygame and create a window
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption('Dino Runner')
clock = pygame.time.Clock()
running = True  # Pygame main loop, kills pygame when False

# Audio assets integrated from example code( IN PROGRESS!)
#bg_music = pygame.mixer.Sound('audio/music.wav')
#bg_music.play(loops = -1)
#jump_sound = pygame.mixer.Sound('audio/jump.mp3')
#jump_sound.set_volume(0.5)

# Game state variables
is_playing = True  # Whether in game or in menu
GROUND_Y = 300  # The Y-coordinate of the ground level
JUMP_GRAVITY_START_SPEED = -20  # The speed at which the player jumps
players_gravity_speed = 0  # The current speed at which the player falls
jump_count = 0  # Tracks how many jumps the player has made in mid-air

# Difficulty and speed scaling variables
game_speed = 5  # Base speed at which obstacles travel horizontally
difficulty_level = 0  # Tracks current stage of dynamic speed scaling

# Lives tracking variables
lives = 3  # Start with 3 lives
invincible_timer = 0  # Tracks how long the player stays invincible after getting hit
INVINCIBLE_DURATION = 1500  # Player is immune for 1.5 seconds (1500 milliseconds) after hit

# New Power-up active timestamps & timers
egg_clear_stocked_until = 0  # Active inventory window for clearing screen with 'W' (38s)
slow_mo_until = 0           # Active timestamp for Slow-Mo shoes bonus powerup (10s)

# Load level assets
SKY_SURF = pygame.image.load("graphics/level/sky.png").convert()
GROUND_SURF = pygame.image.load("graphics/level/ground.png").convert()
game_font = pygame.font.Font(pygame.font.get_default_font(), 50)
small_font = pygame.font.Font(pygame.font.get_default_font(), 20)  # Added for tracking timers/labels
score_surf = game_font.render("SCORE?", False, "Black")
score_rect = score_surf.get_rect(center=(400, 50))

# Load sprite assets
player_walk_1 = pygame.image.load("graphics/player/player_walk_1.png").convert_alpha()
player_walk_2 = pygame.image.load("graphics/player/player_walk_2.png").convert_alpha()
player_walk_list = [player_walk_1, player_walk_2]
player_index = 0.0  # Float tracker to control animation speed
player_jump = pygame.image.load('graphics/player/player_jump.png').convert_alpha()

player_surf = player_walk_list[int(player_index)]
player_rect = player_surf.get_rect(bottomleft=(25, GROUND_Y))

# Load egg assets and animation variables
egg_1 = pygame.image.load("graphics/egg-enemies/egg_1.png").convert_alpha()
egg_2 = pygame.image.load("graphics/egg-enemies/egg_2.png").convert_alpha()
egg_list = [egg_1, egg_2]
egg_index = 0.0  # Float tracker to control egg animation speed

egg_surf = egg_list[int(egg_index)]
egg_rect = egg_surf.get_rect(bottomleft=(800, GROUND_Y))

# Load sunny side up assets, resizing it, and tracking lists for obstacle variance
resize_sunnyside_up_1 = pygame.transform.scale(pygame.image.load("graphics/egg-enemies/sunnyside_up_1.png"), (100, 100)).convert_alpha()
resize_sunnyside_up_2 = pygame.transform.scale(pygame.image.load("graphics/egg-enemies/sunnyside_up_2.png"), (100, 100)).convert_alpha()

# Use the scaled surfaces directly in the list
sunnyside_up_list = [resize_sunnyside_up_1, resize_sunnyside_up_2]
sunnyside_up_index = 0.0
obstacle_rect_list = []
powerup_rect_list = []  # List containing dictionary mappings for tracking active on-screen powerups

# Timers 
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)

powerup_timer = pygame.USEREVENT + 2
pygame.time.set_timer(powerup_timer, 40000)  # Fires custom spawn event exactly every 40 seconds

# Score tracking variables
high_score = 0
start_time = 0
score = 0


# --- REFACTORED FUNCTIONS FROM TEMPLATE EXAMPLE ---

def display_score():
    global score, score_surf, score_rect
    # Calculates score based on elapsed seconds
    current_time = pygame.time.get_ticks() - start_time
    score = current_time // 1000  # Convert milliseconds to seconds

    # Shows font on game screen
    score_surf = game_font.render(f"SCORE: {score}", False, "Black")
    score_rect = score_surf.get_rect(center=(400, 50))

    pygame.draw.rect(screen, "#c0e8ec", score_rect)
    pygame.draw.rect(screen, "#c0e8ec", score_rect, 10)
    screen.blit(score_surf, score_rect)
    return score


def obstacle_movement(obstacle_list):
    if obstacle_list:
        # Move regular stage hazards
        for active_obs in obstacle_list:
            active_obs.x -= current_speed
            
        # Render stage hazards
        for active_obs in obstacle_list:
            if active_obs.bottom == GROUND_Y:
                screen.blit(egg_surf, active_obs)
            elif active_obs.bottom == 210:
                screen.blit(sunnyside_up_surf, active_obs)
            else:
                pygame.draw.circle(screen, "Gold", active_obs.center, 15)
                pygame.draw.circle(screen, "White", (active_obs.center[0] - 4, active_obs.center[1] - 4), 4)

        obstacle_list = [obs for obs in obstacle_list if obs.right > 0]
        return obstacle_list
    else:
        return []


def collisions(player, obstacles):
    global lives, is_playing, high_score, invincible_timer, score
    if obstacles:
        # When player collides with enemy, handle life loss
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
    # Player Animation & Ground logic
    if player_rect.bottom >= GROUND_Y:
        player_index += 0.15  # Increase this decimal to speed up the animation
        if player_index >= len(player_walk_list):
            player_index = 0
        player_surf = player_walk_list[int(player_index)]
    else:
        player_surf = player_jump


# --- MAIN GAME LOOP ---

while running:
    current_ticks = pygame.time.get_ticks()

    # Poll for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            exit()

        elif is_playing:
            # Handle unique 'W' click logic to clear all enemy eggs on screen
            if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                if current_ticks < egg_clear_stocked_until:
                    # Clean out all egg threats from the obstacle tracker list
                    obstacle_rect_list = [obs for obs in obstacle_rect_list if obs.bottom not in (GROUND_Y, 210)]
                    egg_clear_stocked_until = 0  # Powerup consumed!

            # When player wants to jump by pressing SPACE or MOUSECLICK
            if (
                event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE 
                or event.type == pygame.MOUSEBUTTONDOWN
            ):
                # Hardcoded jump threshold restriction back to a maximum of 2 jumps (Double Jump)
                if player_rect.bottom >= GROUND_Y or jump_count < 2:
                    players_gravity_speed = JUMP_GRAVITY_START_SPEED
                    #IN PROGRESS
                    #jump_sound.play()
                    jump_count += 1

            if event.type == obstacle_timer:
                spawn_choice = choice(['sunnyside_up', 'egg', 'egg', 'egg', 'star'])
                if spawn_choice == 'sunnyside_up':
                    obstacle_rect_list.append(sunnyside_up_list[0].get_rect(midbottom=(randint(900, 1100), 210)))
                elif spawn_choice == 'star':
                    star_rect = pygame.Rect(0, 0, 30, 30)
                    star_rect.midbottom = (randint(900, 1100), 150)
                    obstacle_rect_list.append(star_rect)
                else:
                    obstacle_rect_list.append(egg_list[0].get_rect(midbottom=(randint(900, 1100), GROUND_Y)))

            # Power up spawner
            if event.type == powerup_timer:
                p_type = choice(['invincible', 'heart', 'egg_clear', 'slow_mo'])
                p_rect = pygame.Rect(0, 0, 30, 30)
                p_rect.midbottom = (randint(900, 1100), GROUND_Y)
                powerup_rect_list.append({'rect': p_rect, 'type': p_type})

        else:
            # When player wants to play again by pressing SPACE
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                is_playing = True
                egg_rect.left = 800
                obstacle_rect_list.clear()
                powerup_rect_list.clear()  # Purge remaining items
                
                # Reset powerup effect limits
                egg_clear_stocked_until = 0
                slow_mo_until = 0
                
                start_time = pygame.time.get_ticks()  # Resets the start time anchor
                score = 0  # Resets score back to zero
                jump_count = 0  # Tracks how many jumps the player has made in mid-air
                player_index = 0.0  # Resets animation state
                egg_index = 0.0  # Resets egg animation state
                lives = 3  # Start with 3 lives
                invincible_timer = 0  # Tracks how long the player stays invincible after getting hit
                game_speed = 5  # Resets obstacle tracking speed back to base value
                difficulty_level = 0  # Resets difficulty progression thresholds
                pygame.time.set_timer(obstacle_timer, 1500)  # Resets base spawn delays
                pygame.time.set_timer(powerup_timer, 40000)  # Resets base powerup loop cycle

    if is_playing:
        # Dynamically scale difficulty and speed as score increases
        game_speed = 5 + (score // 10)
        new_level = score // 15
        if new_level > difficulty_level:
            difficulty_level = new_level
            pygame.time.set_timer(obstacle_timer, max(600, 1500 - (difficulty_level * 150)))

        # Determine effective horizontal update velocity (Apply Slow-Mo reduction if powerup is active)
        current_speed = game_speed // 2 if current_ticks < slow_mo_until else game_speed

        # Blit the level assets
        screen.blit(SKY_SURF, (0, 0))
        screen.blit(GROUND_SURF, (0, GROUND_Y))
        
        # Display performance evaluation score
        score = display_score()

        # Show remaining lives on the top right
        lives_surf = game_font.render(f"LIVES: {lives}", False, "Red")
        lives_rect = lives_surf.get_rect(topright=(780, 20))
        screen.blit(lives_surf, lives_rect)

        # Move and render regular stage hazards
        obstacle_rect_list = obstacle_movement(obstacle_rect_list)
            
        # Move powerups currently sliding across ground level
        for pu in powerup_rect_list:
            pu['rect'].x -= current_speed
        powerup_rect_list = [pu for pu in powerup_rect_list if pu['rect'].right > 0]

        # Animate egg continuously while playing
        egg_index += 0.2  # Increase or decrease this decimal to adjust egg animation speed
        if egg_index >= len(egg_list):
            egg_index = 0
        egg_surf = egg_list[int(egg_index)]
        
        # Moves sunny side up
        sunnyside_up_index += 0.2
        if sunnyside_up_index >= len(sunnyside_up_list):
            sunnyside_up_index = 0
        sunnyside_up_surf = sunnyside_up_list[int(sunnyside_up_index)]

        # Render active powerup tokens with graphical primitives
        for pu in powerup_rect_list:
            if pu['type'] == 'invincible': color, label = "Blue", "I"
            elif pu['type'] == 'heart': color, label = "Pink", "H"
            elif pu['type'] == 'egg_clear': color, label = "Purple", "W"
            elif pu['type'] == 'slow_mo': color, label = "Cyan", "S"
            
            pygame.draw.circle(screen, color, pu['rect'].center, 15)
            lbl_surf = small_font.render(label, True, "White")
            lbl_rect = lbl_surf.get_rect(center=pu['rect'].center)
            screen.blit(lbl_surf, lbl_rect)

        # Adjust player's vertical location then blit it
        players_gravity_speed += 1
        player_rect.y += players_gravity_speed
        
        if player_rect.bottom >= GROUND_Y:
            player_rect.bottom = GROUND_Y
            jump_count = 0  # Reset jump count when touching the ground
        
        # Process active animation rendering conditions
        player_animation()
            
        # Flicker effect if player is currently invincible
        if current_ticks < invincible_timer:
            if (current_ticks // 100) % 2 == 0:
                screen.blit(player_surf, player_rect)
        else:
            screen.blit(player_surf, player_rect)

        # Handle powerup dynamic modifications / collection tracking
        for pu in powerup_rect_list[:]:
            if player_rect.colliderect(pu['rect']):
                if pu['type'] == 'invincible':
                    invincible_timer = current_ticks + 15000  # Grant 15 seconds invincibility
                elif pu['type'] == 'heart':
                    lives += 1                               # Extra heart modifier
                elif pu['type'] == 'egg_clear':
                    egg_clear_stocked_until = current_ticks + 38000  # Held for 38 seconds max
                elif pu['type'] == 'slow_mo':
                    slow_mo_until = current_ticks + 10000           # 10 seconds of slow motion
                powerup_rect_list.remove(pu)

        # Process obstacle object hit detection mechanics
        is_playing = collisions(player_rect, obstacle_rect_list)

        # Render Active UI Buff HUD status tracking on left side
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

    # When game is over, display game over message
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
    clock.tick(60)  # Limits game loop to 60 FPS

pygame.quit()