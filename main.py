"""
Dino Game in Python
A game similar to the famous Chrome Dino Game, built using pygame-ce.
Made by intern: @Neel Verma, no one or nothing else. 🤖
"""

import pygame
from random import randint, choice

# Initialize Pygame and create a window
pygame.init()
screen = pygame.display.set_mode((800, 400))
clock = pygame.time.Clock()
running = True  # Pygame main loop, kills pygame when False

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

# Load level assets
SKY_SURF = pygame.image.load("graphics/level/sky.png").convert()
GROUND_SURF = pygame.image.load("graphics/level/ground.png").convert()
game_font = pygame.font.Font(pygame.font.get_default_font(), 50)
score_surf = game_font.render("SCORE?", False, "Black")
score_rect = score_surf.get_rect(center=(400, 50))

# Load sprite assets
player_walk_1 = pygame.image.load("graphics/player/player_walk_1.png").convert_alpha()
player_walk_2 = pygame.image.load("graphics/player/player_walk_2.png").convert_alpha()
player_walk_list = [player_walk_1, player_walk_2]
player_index = 0.0  # Float tracker to control animation speed

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

# Audio assets(IN PROGRESS)
#bg_music = pygame.mixer.Sound('audio/music.wav')
#bg_music.play(loops=-1)
#jump_sound = pygame.mixer.Sound('audio/jump.mp3')
#jump_sound.set_volume(0.5)

# Timer 
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)

# Score tracking variables
high_score = 0
start_time = 0
score = 0

while running:
    # Poll for events
    for event in pygame.event.get():
        # pygame.QUIT --> user clicked X to close your window
        if event.type == pygame.QUIT:
            running = False

        elif is_playing:
            # When player wants to jump by pressing SPACE
            if (
                event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE 
                or event.type == pygame.MOUSEBUTTONDOWN
            ):
                # Allow jumping if on the ground, or if they haven't double-jumped yet
                if player_rect.bottom >= GROUND_Y or jump_count < 2:
                    players_gravity_speed = JUMP_GRAVITY_START_SPEED
                    jump_count += 1
                    #jump_sound.play() (IN PROGRESS)

            if event.type == obstacle_timer:
                # Randomize choosing between a high hazard, a ground hazard, or a rare score item
                spawn_choice = choice(['sunnyside_up', 'egg', 'egg', 'egg', 'star'])
                if spawn_choice == 'sunnyside_up':
                    obstacle_rect_list.append(sunnyside_up_list[0].get_rect(midbottom=(randint(900, 1100), 210)))
                elif spawn_choice == 'star':
                    # Create a standalone target rect suspended in the air for a score booster item
                    star_rect = pygame.Rect(0, 0, 30, 30)
                    star_rect.midbottom = (randint(900, 1100), 150)
                    obstacle_rect_list.append(star_rect)
                else:
                    obstacle_rect_list.append(egg_list[0].get_rect(midbottom=(randint(900, 1100), GROUND_Y)))

        else:
            # When player wants to play again by pressing SPACE
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                is_playing = True
                egg_rect.left = 800
                obstacle_rect_list.clear()
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

    if is_playing:

        # Calculates score based on elapsed seconds
        current_time = pygame.time.get_ticks() - start_time
        score = current_time // 1000  # Convert milliseconds to seconds

        # Dynamically scale difficulty and speed as score increases
        game_speed = 5 + (score // 10)
        new_level = score // 15
        if new_level > difficulty_level:
            difficulty_level = new_level
            pygame.time.set_timer(obstacle_timer, max(600, 1500 - (difficulty_level * 150)))

        # Shows font on game screen
        score_surf = game_font.render(f"SCORE: {score}", False, "Black")
        score_rect = score_surf.get_rect(center=(400, 50))

        # Blit the level assets
        screen.blit(SKY_SURF, (0, 0))
        screen.blit(GROUND_SURF, (0, GROUND_Y))
        pygame.draw.rect(screen, "#c0e8ec", score_rect)
        pygame.draw.rect(screen, "#c0e8ec", score_rect, 10)
        screen.blit(score_surf, score_rect)

        # Show remaining lives on the top right
        lives_surf = game_font.render(f"LIVES: {lives}", False, "Red")
        lives_rect = lives_surf.get_rect(topright=(780, 20))
        screen.blit(lives_surf, lives_rect)

        # Adjust egg's horizontal location, animate it, then blit it (IN PROGRESS)
        for active_obs in obstacle_rect_list:
            active_obs.x -= game_speed
        obstacle_rect_list = [obs for obs in obstacle_rect_list if obs.right > 0]
            
        # Animate egg continuously while playing
        egg_index += 0.2  # Increase or decrease this decimal to adjust egg animation speed
        if egg_index >= len(egg_list):
            egg_index = 0
        egg_surf = egg_list[int(egg_index)]
        
        #Moves sunny side up
        sunnyside_up_index += 0.2
        if sunnyside_up_index >= len(sunnyside_up_list):
            sunnyside_up_index = 0
        sunnyside_up_surf = sunnyside_up_list[int(sunnyside_up_index)]

        for active_obs in obstacle_rect_list:
            if active_obs.bottom == GROUND_Y:
                screen.blit(egg_surf, active_obs)
            elif active_obs.bottom == 210:
                screen.blit(sunnyside_up_surf, active_obs)
            else:
                # Draw a shiny golden star collectible using pygame primitives
                pygame.draw.circle(screen, "Gold", active_obs.center, 15)
                pygame.draw.circle(screen, "White", (active_obs.center[0] - 4, active_obs.center[1] - 4), 4)

        # Adjust player's vertical location then blit it
        players_gravity_speed += 1
        player_rect.y += players_gravity_speed
        
        # Player Animation & Ground logic
        if player_rect.bottom >= GROUND_Y:
            player_rect.bottom = GROUND_Y
            jump_count = 0  # Reset jump count when touching the ground
            
            # Animate running when on the ground
            player_index += 0.15  # Increase this decimal to speed up the animation
            if player_index >= len(player_walk_list):
                player_index = 0
            player_surf = player_walk_list[int(player_index)]
        else:
            # Display a static jump/mid-air frame when airborne
            player_surf = player_walk_1
            
        # Flicker effect if player is currently invincible
        current_ticks = pygame.time.get_ticks()
        if current_ticks < invincible_timer:
            # Flashes character image by only turning invisible every other frame
            if (current_ticks // 100) % 2 == 0:
                screen.blit(player_surf, player_rect)
        else:
            screen.blit(player_surf, player_rect)

        # When player collides with enemy, handle life loss
        for egg_rect in obstacle_rect_list[:]:
            if egg_rect.colliderect(player_rect):
                if egg_rect.bottom != GROUND_Y and egg_rect.bottom != 210:
                    # It's a star! Grant bonus score points and clean out tracking object
                    score += 3
                    obstacle_rect_list.remove(egg_rect)
                else:
                    #Check if player is allowed to take damage (not currently invincible)
                    if pygame.time.get_ticks() >= invincible_timer:
                        lives -= 1
                        if lives <= 0:
                            is_playing = False
                            if score > high_score:
                                high_score = score  # Updates high score if current score is higher
                        else:
                            # Give invincibility buffer and reset obstacle position
                            invincible_timer = pygame.time.get_ticks() + INVINCIBLE_DURATION
                            obstacle_rect_list.remove(egg_rect)
                            break

    # When game is over, display game over message
    else:
        screen.fill("black")

        # Render text surfaces for game over screens
        game_over_surf = game_font.render("GAME OVER!", False, "Red")
        game_over_rect = game_over_surf.get_rect(center=(400, 100))
        
        high_score_surf = game_font.render(f"HIGH SCORE: {high_score}", False, "White")
        high_score_rect = high_score_surf.get_rect(center=(400, 200))
        
        restart_surf = game_font.render("Press SPACE to Play Again", False, "Gray")
        restart_rect = restart_surf.get_rect(center=(400, 300))

        # Blit text assets onto the game over screen
        screen.blit(game_over_surf, game_over_rect)
        screen.blit(high_score_surf, high_score_rect)
        screen.blit(restart_surf, restart_rect)

    # flip the display to put your work on screen
    pygame.display.flip()
    clock.tick(60)  # Limits game loop to 60 FPS

pygame.quit()