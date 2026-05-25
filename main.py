"""
Dino Game in Python
A game similar to the famous Chrome Dino Game, built using pygame-ce.
Made by intern: @Neel Verma, no one or nothing else.
"""

import pygame

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

# Load level assets
SKY_SURF = pygame.image.load("graphics/level/sky.png").convert()
GROUND_SURF = pygame.image.load("graphics/level/ground.png").convert()
game_font = pygame.font.Font(pygame.font.get_default_font(), 50)
score_surf = game_font.render("SCORE?", False, "Black")
score_rect = score_surf.get_rect(center=(400, 50))

# Load sprite assets
player_surf = pygame.image.load("graphics/player/player_walk_1.png").convert_alpha()
player_rect = player_surf.get_rect(bottomleft=(25, GROUND_Y))
egg_surf = pygame.image.load("graphics/egg/egg_1.png").convert_alpha()
egg_rect = egg_surf.get_rect(bottomleft=(800, GROUND_Y))

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

        else:
            # When player wants to play again by pressing SPACE
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                is_playing = True
                egg_rect.left = 800
                start_time = pygame.time.get_ticks()  # Resets the start time anchor
                score = 0  # Resets score back to zero
                jump_count = 0  # Resets jump count back to zero

    if is_playing:
        screen.fill("purple")  # Wipe the screen

        # Calculates score based on elapsed seconds
        current_time = pygame.time.get_ticks() - start_time
        score = current_time // 1000  # Convert milliseconds to seconds

        # Shows font on game screen
        score_surf = game_font.render(f"SCORE: {score}", False, "Black")
        score_rect = score_surf.get_rect(center=(400, 50))

        # Blit the level assets
        screen.blit(SKY_SURF, (0, 0))
        screen.blit(GROUND_SURF, (0, GROUND_Y))
        pygame.draw.rect(screen, "#c0e8ec", score_rect)
        pygame.draw.rect(screen, "#c0e8ec", score_rect, 10)
        screen.blit(score_surf, score_rect)

        # Adjust egg's horizontal location then blit it
        egg_rect.x -= 5
        if egg_rect.right <= 0:
            egg_rect.left = 800
        screen.blit(egg_surf, egg_rect)

        # Adjust player's vertical location then blit it
        players_gravity_speed += 1
        player_rect.y += players_gravity_speed
        if player_rect.bottom >= GROUND_Y:
            player_rect.bottom = GROUND_Y
            jump_count = 0  # Reset jump count when touching the ground
        screen.blit(player_surf, player_rect)

        # When player collides with enemy, game ends
        if egg_rect.colliderect(player_rect):
            is_playing = False
            if score > high_score:
                high_score = score  # Updates high score if current score is higher

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