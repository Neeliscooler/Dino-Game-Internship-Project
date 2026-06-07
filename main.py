"""
Dino Game in Python
A game similar to the famous Chrome Dino Game, built using pygame-ce.
Made by intern: @Neel Verma, no one or nothing else. 🤖
Overall Modifications: Added lives, post-hit invincibility, double jumping, power ups (Invincibility, Triple Jump, Time Slow, Egg Bomb, and Extra Life),
Coins, stars which increase the score, more enemies, On screen HUD(score, lives, and coin counter), and a game over screen which displays the highscore,
score achieved and coins recieved this run, and a day and night system which changes the background based on the time of each run, audio assets (main menu, game, jump, and defeat screen),
added heart pngs for the playerand created a max heart count of 5, added a main menu which is in progress with currently 3 options(Main game, instructions, exit),

"""

import pygame
from sys import exit
from random import randint, choice

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption('Eggpocalypse')
clock = pygame.time.Clock()
running = True 

# Audion assets
bg_music = pygame.mixer.Sound('audio/game_music.mp3')
jump_sound = pygame.mixer.Sound('audio/jump.mp3')
jump_sound.set_volume(0.5)
defeat_music = pygame.mixer.Sound('audio/defeat_music.mp3')  # Load defeat screen audio soundtrack asset
main_menu_music = pygame.mixer.Sound('audio/main_menu.mp3')  # Load main menu route asset for background loop tracking
main_menu_music.play(loops = -1)  # Initiate menu loop immediately at program startup initialization route

# Game state variables
is_playing = False  
game_state = 'main_menu' # Controls the active user interface route screen state
GROUND_Y = 300  
JUMP_GRAVITY_START_SPEED = -20  
players_gravity_speed = 0  
jump_count = 0  

# Difficulty and speed scaling
game_speed = 5  
current_speed = 5  
difficulty_level = 0  

# Lives and invincibility variables
lives = 3  
invincible_timer = 0  
INVINCIBLE_DURATION = 1500  

# Power-up active timestamps
egg_clear_stocked_until = 0  # Screen clear with 'W'
slow_mo_until = 0            # Slow-Mo effect
triple_jump_until = 0         # Triple jump effect (15 seconds)
explosion_end_time = 0       # Screen bomb explosion flash timestamp

# Load background and font assets
sky_day = pygame.image.load("graphics/level/day_sky.png").convert()
sky_sunset = pygame.image.load("graphics/level/sunset_sky.png").convert()
sky_night = pygame.image.load("graphics/level/night_sky.png").convert()
sky_midnight = pygame.image.load("graphics/level/midnight_sky.png").convert()
sky_list = [sky_day, sky_sunset, sky_night, sky_midnight]  # List of sky backgrounds for shifting time

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
player_heart_surf = pygame.transform.scale(pygame.image.load("graphics/player/player_heart.png"), (35, 35)).convert_alpha()  # Load heart graphic asset for HUD health tracking

# Load triple jump alternate player assets
tj_walk_1 = pygame.transform.scale(pygame.image.load("graphics/player/triplejump_walk_1.png"), (100,100)).convert_alpha()
tj_walk_2 = pygame.transform.scale(pygame.image.load("graphics/player/triplejump_walk_2.png"), (100, 100)).convert_alpha()
tj_walk_list = [tj_walk_1, tj_walk_2]
tj_jump =  pygame.transform.scale(pygame.image.load("graphics/player/triplejump_jump.png"), (100, 100)).convert_alpha()

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
sunnyside_up_surf = sunnyside_up_list[int(sunnyside_up_index)]  # Fixed: Initialized early to prevent NameError crash

# Load eggsaucer assets
eggsaucer_1 = pygame.transform.scale(pygame.image.load("graphics/egg-enemies/eggsaucer_1.png"), (100, 60)).convert_alpha()
eggsaucer_2 = pygame.transform.scale(pygame.image.load("graphics/egg-enemies/eggsaucer_2.png"), (100, 60)).convert_alpha()
eggsaucer_list = [eggsaucer_1, eggsaucer_2]
eggsaucer_index = 0.0
eggsaucer_surf = eggsaucer_list[int(eggsaucer_index)]

# Load coin asset
coin_surf = pygame.image.load("graphics/collectibles/coin.png").convert_alpha()

# Load star asset
star_surf = pygame.transform.scale(pygame.image.load("graphics/collectibles/star.png"), (70, 70)).convert_alpha()

# load power up related assets
egg_bomb_explosion_surf = pygame.transform.scale(pygame.image.load("graphics/collectibles/egg_bomb_explosion.png"), (200,200)).convert_alpha()
extra_life_potion_surf = pygame.transform.scale(pygame.image.load("graphics/collectibles/extra_life_potion.png"), (100, GROUND_Y)).convert_alpha()

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
bonus_score = 0
coins_collected = 0
total_coins = 0 # Persistent tally of all coins gathered across gameplay runs

# Main menu interactable screen coordinate boundaries
play_rect = pygame.Rect(0, 0, 0, 0)
inst_rect = pygame.Rect(0, 0, 0, 0)
quit_rect = pygame.Rect(0, 0, 0, 0)


# GAME FUNCTIONS

def display_score():
    """Calculates the runtime score based on game ticks and draws it to the screen HUD."""
    global score, score_surf, score_rect
    current_time = pygame.time.get_ticks() - start_time
    score = (current_time // 1000) + bonus_score  

    score_surf = game_font.render(f"SCORE: {score}", False, "Black")
    score_rect = score_surf.get_rect(center=(400, 50))

    pygame.draw.rect(screen, "#c0e8ec", score_rect)
    pygame.draw.rect(screen, "#c0e8ec", score_rect, 10)
    screen.blit(score_surf, score_rect)
    return score


def obstacle_movement(obstacle_list):
    """Updates coordinate position of enemies and draws them based on their spawn heights."""
    if obstacle_list:
        for active_obs in obstacle_list:
            active_obs.x -= current_speed
            
        for active_obs in obstacle_list:
            if active_obs.bottom == GROUND_Y:
                screen.blit(egg_surf, active_obs)
            elif active_obs.bottom == 210:
                screen.blit(sunnyside_up_surf, active_obs)
            elif active_obs.bottom == 180:
                screen.blit(star_surf, active_obs)  # Render star collectible
            elif active_obs.bottom == 120:
                beam_color = "Yellow" if (pygame.time.get_ticks() // 200) % 2 == 0 else "Orange"
                beam_rect = pygame.Rect(active_obs.left, active_obs.bottom, active_obs.width, GROUND_Y - active_obs.bottom)
                beam_surf = pygame.Surface((beam_rect.width, beam_rect.height), pygame.SRCALPHA)
                if beam_color == "Yellow":
                    beam_surf.fill((255, 255, 0, 80))
                else:
                    beam_surf.fill((255, 165, 0, 80))
                screen.blit(beam_surf, beam_rect)
                
                screen.blit(eggsaucer_surf, active_obs)
            else:
                screen.blit(coin_surf, active_obs)

        obstacle_list = [obs for obs in obstacle_list if obs.right > 0]
        return obstacle_list
    else:
        return []


def collisions(player, obstacles):
    """Checks hitbox collisions between the player, coins, enemis, and filters invincibility logic."""
    global lives, is_playing, high_score, invincible_timer, score, coins_collected, bonus_score
    if obstacles:
        for egg_rect in obstacles[:]:
            if egg_rect.colliderect(player):
                if egg_rect.bottom == 180:
                    bonus_score += 1
                    obstacles.remove(egg_rect)
                elif egg_rect.bottom == 150:
                    coins_collected += 1
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
    """Swaps walking frames based on ground state or overrides with the jump surface asset."""
    global player_index, player_surf
    
    # Determine the correct sheet depending on triple jump status
    current_walk_list = tj_walk_list if current_ticks < triple_jump_until else player_walk_list
    current_jump_surf = tj_jump if current_ticks < triple_jump_until else player_jump

    if player_rect.bottom >= GROUND_Y:
        player_index += 0.15  
        if player_index >= len(current_walk_list):
            player_index = 0
        player_surf = current_walk_list[int(player_index)]
    else:
        player_surf = current_jump_surf


def draw_main_menu():
    """Renders the menu background title screen metrics and button layout."""
    global play_rect, inst_rect, quit_rect
    screen.fill("black")
    
    # Render top left total coins and top right high score values
    total_coins_surf = small_font.render(f"Total Coins: {total_coins}", True, "Yellow")
    screen.blit(total_coins_surf, (20, 20))
    
    highest_score_surf = small_font.render(f"Highest Score: {high_score}", True, "White")
    screen.blit(highest_score_surf, (800 - highest_score_surf.get_width() - 20, 20))
    
    # Game title display configuration
    title_surf = game_font.render("Eggpocalypse", True, "Red")
    title_rect = title_surf.get_rect(center = (400, 100))
    screen.blit(title_surf, title_rect)
    
    # Generate navigation selection buttons positions tracking data labels
    play_surf = game_font.render("Play Game", True, "Green")
    play_rect = play_surf.get_rect(center = (400, 200))
    screen.blit(play_surf, play_rect)
    
    inst_surf = game_font.render("Instructions", True, "Cyan")
    inst_rect = inst_surf.get_rect(center = (400, 270))
    screen.blit(inst_surf, inst_rect)
    
    quit_surf = game_font.render("Quit Game", True, "Orange")
    quit_rect = quit_surf.get_rect(center = (400, 340))
    screen.blit(quit_surf, quit_rect)


def draw_instructions():
    """Renders gameplay objective specifications and controller mapping guides."""
    screen.fill("black")
    
    # Title display layout positioning metrics setup routine
    inst_title_surf = game_font.render("Instructions", True, "Cyan")
    screen.blit(inst_title_surf, inst_title_surf.get_rect(center = (400, 60)))
    
    # Informative textual descriptions drawing elements allocations list details
    txt1 = small_font.render("SPACE / MOUSE CLICK - Jump (Double / Triple Jump available with powerups)", True, "White")
    txt2 = small_font.render("W KEY - Fire Egg Bomb screen clear hazard wipe tool", True, "White")
    txt3 = small_font.render("OBJECTIVE - Dodge breaking eggs, gather gold coins and score stars!", True, "White")
    txt4 = small_font.render("Press M to go back to the Main Menu", True, "Yellow")
    
    screen.blit(txt1, txt1.get_rect(center = (400, 150)))
    screen.blit(txt2, txt2.get_rect(center = (400, 200)))
    screen.blit(txt3, txt3.get_rect(center = (400, 250)))
    screen.blit(txt4, txt4.get_rect(center = (400, 330)))


def reset_game():
    """Resets all simulation parameters and handles standard baseline runtime allocations initialization."""
    global is_playing, game_state, obstacle_rect_list, powerup_rect_list, egg_clear_stocked_until, slow_mo_until, triple_jump_until, explosion_end_time, start_time, score, bonus_score, coins_collected, jump_count, player_index, egg_index, eggsaucer_index, lives, invincible_timer, game_speed, difficulty_level
    is_playing = True
    game_state = 'playing'
    obstacle_rect_list.clear()
    powerup_rect_list.clear()  
    
    # Reset powerup limits
    egg_clear_stocked_until = 0
    slow_mo_until = 0
    triple_jump_until = 0
    explosion_end_time = 0  # Clear blast visual trackers
    
    # Reset internal tracker systems
    start_time = pygame.time.get_ticks()  
    score = 0  
    bonus_score = 0
    coins_collected = 0
    jump_count = 0  
    player_index = 0.0  
    egg_index = 0.0  
    eggsaucer_index = 0.0
    lives = 3  
    invincible_timer = 0  
    game_speed = 5  
    difficulty_level = 0  
    pygame.time.set_timer(obstacle_timer, 1500)  
    pygame.time.set_timer(powerup_timer, 40000)
    bg_music.play(loops = -1)


# MAIN GAME LOOP

while running:
    current_ticks = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            exit()

        elif game_state == 'main_menu':
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    main_menu_music.stop()  # Stop menu soundtrack right before setting up playing parameters
                    reset_game()
                elif inst_rect.collidepoint(event.pos):
                    game_state = 'instructions'
                elif quit_rect.collidepoint(event.pos):
                    running = False
                    pygame.quit()
                    exit()

        elif game_state == 'instructions':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                game_state = 'main_menu'

        elif game_state == 'playing':
            # Press 'W' to use screen clear bomb
            if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                if current_ticks < egg_clear_stocked_until:
                    obstacle_rect_list = [obs for obs in obstacle_rect_list if obs.bottom not in (GROUND_Y, 210, 120, 180)]
                    egg_clear_stocked_until = 0  
                    explosion_end_time = current_ticks + 600  # Set duration timer for full screen flash

            # Handle jumping (Space or Mouse Click)
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE 
                or event.type == pygame.MOUSEBUTTONDOWN):
                # Set jump limit based on active power-up status
                max_jumps = 3 if current_ticks < triple_jump_until else 2
                if player_rect.bottom >= GROUND_Y or jump_count < max_jumps:
                    players_gravity_speed = JUMP_GRAVITY_START_SPEED
                    #plays jump sound effect when jumping
                    jump_sound.play()
                    jump_count += 1

            # Spawn obstacles/collectibles
            if event.type == obstacle_timer:
                spawn_choice = choice(['sunnyside_up', 'egg', 'egg', 'egg', 'coin', 'eggsaucer', 'star'])
                if spawn_choice == 'sunnyside_up':
                    obstacle_rect_list.append(sunnyside_up_list[0].get_rect(midbottom=(randint(900, 1100), 210)))
                elif spawn_choice == 'eggsaucer':
                    obstacle_rect_list.append(eggsaucer_list[0].get_rect(midbottom=(randint(900, 1100), 120)))
                elif spawn_choice == 'coin':
                    obstacle_rect_list.append(coin_surf.get_rect(midbottom=(randint(900, 1100), 150)))
                elif spawn_choice == 'star':
                    obstacle_rect_list.append(star_surf.get_rect(midbottom=(randint(900, 1100), 180)))
                else:
                    obstacle_rect_list.append(egg_list[0].get_rect(midbottom=(randint(900, 1100), GROUND_Y)))

            # Spawn powerups
            if event.type == powerup_timer:
                p_type = choice(['invincible', 'heart', 'egg_clear', 'slow_mo', 'triple_jump'])
                p_rect = pygame.Rect(0, 0, 30, 30)
                p_rect.midbottom = (randint(900, 1100), GROUND_Y)
                powerup_rect_list.append({'rect': p_rect, 'type': p_type})

        elif game_state == 'game_over':
            # Restart game on SPACE press
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    defeat_music.stop()  # Turn off game over screen tracking track prior to starting new clean simulation run
                    reset_game()
            # Return to main menu on M key press
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                defeat_music.stop()  # Terminate playback channel layout configurations for post run screen asset
                main_menu_music.play(loops = -1)  # Re-initiate background music loop routing path for title screen
                game_state = 'main_menu'

        if game_state == 'main_menu':
            draw_main_menu()

        elif game_state == 'instructions':
            draw_instructions()

    if game_state == 'playing':
        # Increase speed and spawn rates as score grows
        game_speed = 5 + (score // 10)
        new_level = score // 15
        if new_level > difficulty_level:
            difficulty_level = new_level
            pygame.time.set_timer(obstacle_timer, max(600, 1500 - (difficulty_level * 150)))

        # Handle slow motion speed reduction
        current_speed = game_speed // 2 if current_ticks < slow_mo_until else game_speed

        # Render background and score
        sky_index = ((pygame.time.get_ticks() - start_time) // 50000) % len(sky_list)  # Calculate active sky index based on 50 second loop interval
        screen.blit(sky_list[sky_index], (0, 0))
        screen.blit(GROUND_SURF, (0, GROUND_Y))
        score = display_score()

        # Render coins section directly below the score
        coins_hud_surf = small_font.render(f"Coins collected: {coins_collected}", False, "Black")
        coins_hud_rect = coins_hud_surf.get_rect(center=(400, 95))
        screen.blit(coins_hud_surf, coins_hud_rect)

        # Render lives section of screen
        for i in range(lives):
            heart_rect = player_heart_surf.get_rect(topleft=(20 + (i * 40), 20))  # Render individual heart graphic sprites horizontally along the screen boundary
            screen.blit(player_heart_surf, heart_rect)

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

        eggsaucer_index += 0.1
        if eggsaucer_index >= len(eggsaucer_list): eggsaucer_index = 0
        eggsaucer_surf = eggsaucer_list[int(eggsaucer_index)]

        # Render active powerup tokens on screen
        for pu in powerup_rect_list:
            if pu['type'] == 'invincible': color, label = "Blue", "I"
            elif pu['type'] == 'heart': color, label = "Pink", "H"
            elif pu['type'] == 'egg_clear': color, label = "Purple", "W"
            elif pu['type'] == 'slow_mo': color, label = "Cyan", "S"
            elif pu['type'] == 'triple_jump': color, label = "Orange", "T"
            
            if pu['type'] == 'heart':
                potion_scaled = pygame.transform.scale(extra_life_potion_surf, (100, 100))
                screen.blit(potion_scaled, pu['rect'])
            else:
                pygame.draw.circle(screen, color, pu['rect'].center, 15)
                lbl_surf = small_font.render(label, True, "White")
                lbl_rect = lbl_surf.get_rect(center=pu['rect'].center)
                screen.blit(lbl_surf, lbl_rect)

        # Apply gravity mechanics and anti-gravity beam adjustments
        player_under_beam = False
        for obs in obstacle_rect_list:
            if obs.bottom == 120:
                if player_rect.right > obs.left and player_rect.left < obs.right:
                    player_under_beam = True
                    break

        if player_under_beam:
            players_gravity_speed += 1
            player_rect.y += players_gravity_speed * 0.5
        else:
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
                    if lives < 5:  # Cap health pool up to 5 hearts maximum
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

        # Handle runtime termination state logic route modifications
        if not is_playing:
            game_state = 'game_over'
            total_coins += coins_collected
            bg_music.stop()
            defeat_music.play(loops = -1)  # Fire defeat loop system right when transitions shift to game over overlay assets

        # Render Active Powerup Timers on Left side of screen
        hud_y = 120
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

        # Render full screen egg bomb explosion if active
        if current_ticks < explosion_end_time:
            explosion_scaled = pygame.transform.scale(egg_bomb_explosion_surf, (1000, 800))
            screen.blit(explosion_scaled, (0, 0))  # Overlay explosion graphics layer

    # Game Over screen assets
    elif game_state == 'game_over':
        screen.fill("black")

        game_over_surf = game_font.render("GAME OVER!", False, "Red")
        game_over_rect = game_over_surf.get_rect(center=(400, 60))
        
        current_score_surf = small_font.render(f"SCORE ACHIEVED: {score}", False, "Light Blue")
        current_score_rect = current_score_surf.get_rect(center=(400, 130))

        current_coins_surf = small_font.render(f"COINS COLLECTED: {coins_collected}", False, "Yellow")
        current_coins_rect = current_coins_surf.get_rect(center=(400, 175))

        high_score_surf = game_font.render(f"HIGH SCORE: {high_score}", False, "White")
        high_score_rect = high_score_surf.get_rect(center=(400, 240))
        
        restart_surf = small_font.render("Press SPACE to Play Again", False, "Gray")
        restart_rect = restart_surf.get_rect(center=(400, 310))

        menu_surf = small_font.render("Press M to Return to Main Menu", False, "Gray")
        menu_rect = menu_surf.get_rect(center=(400, 350))

        screen.blit(game_over_surf, game_over_rect)
        screen.blit(current_score_surf, current_score_rect)
        screen.blit(current_coins_surf, current_coins_rect)
        screen.blit(high_score_surf, high_score_rect)
        screen.blit(restart_surf, restart_rect)
        screen.blit(menu_surf, menu_rect)

    pygame.display.update()
    clock.tick(60)  

pygame.quit()