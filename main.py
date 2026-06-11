"""
Dino Game in Python
A game similar to the famous Chrome Dino Game, built using pygame-ce.
Made by intern: @Neel Verma, no one or nothing else. 🤖
Overall Modifications: Added lives, post-hit invincibility, double jumping, power ups (Invincibility, Triple Jump, Time Slow, Egg Bomb, Extra Life, Score Doubler, King Potion),
Stars which increase the score, more enemies, On screen HUD(score, lives, and star counter), and a game over screen which displays the highscore,
score achieved and stars recieved this run, and a day and night system which changes the background based on the time of each run (day -> sunset -> night -> midnight -> sunset -> day),
audio assets (main menu, game, jump, and defeat screen),
added heart pngs for the player and created a max heart count of 5, added a main menu which is in progress with currently 3 options(Main game, instructions, exit),
added a boss battle with the egg king who spawns 1 additional enemy at a time and can be defeated when hit by an egg bomb twice, the egg king appears again in (100+20*number of egg king defeats) with 1 more hp per egg king defeat
"""

import pygame
from random import randint, choice

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption('Eggpocalypse')
clock = pygame.time.Clock()
running = True

# Audio assets
bg_music = pygame.mixer.Sound('audio/game_music.mp3')
jump_sound = pygame.mixer.Sound('audio/jump.mp3')
jump_sound.set_volume(0.5)
defeat_music = pygame.mixer.Sound('audio/defeat_music.mp3')  # Game over music
main_menu_music = pygame.mixer.Sound('audio/main_menu.mp3')  # Main menu background music
main_menu_music.play(loops=-1)  # Play menu music on loop immediately

# Game state variables
is_playing = False
game_state = 'main_menu'  # Tracks the current screen (menu, instructions, playing, game over)
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
egg_clear_stocked_until = 0   # Bomb power-up (clears the screen with 'W')
slow_mo_until = 0             # Slow motion power-up
triple_jump_until = 0         # Triple jump power-up
explosion_end_time = 0        # When the screen flash explosion effect ends
score_doubler_until = 0       # Score doubler power-up - doubles score gain and star bonus value
king_potion_until = 0         # King potion power-up - combined effect of score doubler, health, and invincibility

# Queue for potions collected while score doubler is active - they activate after score doubler ends
queued_potions = []

# Load background and font assets
sky_day = pygame.image.load("graphics/level/day_sky.png").convert()
sky_sunset = pygame.image.load("graphics/level/sunset_sky.png").convert()
sky_night = pygame.image.load("graphics/level/night_sky.png").convert()
sky_midnight = pygame.image.load("graphics/level/midnight_sky.png").convert()
# Sky cycle: day -> sunset -> night -> midnight -> sunset -> day (midnight wraps back through sunset)
sky_list = [sky_day, sky_sunset, sky_night, sky_midnight, sky_sunset, sky_day]

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
player_heart_surf = pygame.transform.scale(pygame.image.load("graphics/player/player_heart.png"), (35, 35)).convert_alpha()  # Heart image for the health bar

# Load triple jump alternate player assets
tj_walk_1 = pygame.image.load("graphics/player/triplejump_walk_1.png").convert_alpha()
tj_walk_2 = pygame.image.load("graphics/player/triplejump_walk_2.png").convert_alpha()
tj_walk_list = [tj_walk_1, tj_walk_2]
tj_jump = pygame.image.load("graphics/player/triplejump_jump.png").convert_alpha()

player_surf = player_walk_list[int(player_index)]
player_rect = player_surf.get_rect(bottomleft=(25, GROUND_Y))

# Load basic egg assets
egg_1 = pygame.image.load("graphics/egg-enemies/egg_1.png").convert_alpha()
egg_2 = pygame.image.load("graphics/egg-enemies/egg_2.png").convert_alpha()
egg_list = [egg_1, egg_2]
egg_index = 0.0

egg_surf = egg_list[int(egg_index)]
egg_rect = egg_surf.get_rect(bottomleft=(800, GROUND_Y))

# Load egg knight asset frame walk lists
egg_knight_1 = pygame.transform.scale(pygame.image.load("graphics/egg-enemies/egg_knight_1.png"), (100, 100)).convert_alpha()
egg_knight_2 = pygame.transform.scale(pygame.image.load("graphics/egg-enemies/egg_knight_2.png"), (100, 100)).convert_alpha()
egg_knight_list = [egg_knight_1, egg_knight_2]
egg_knight_index = 0.0
egg_knight_surf = egg_knight_list[int(egg_knight_index)]

# Load sunny side up assets
resize_sunnyside_up_1 = pygame.transform.scale(pygame.image.load("graphics/egg-enemies/sunnyside_up_1.png"), (100, 100)).convert_alpha()
resize_sunnyside_up_2 = pygame.transform.scale(pygame.image.load("graphics/egg-enemies/sunnyside_up_2.png"), (100, 100)).convert_alpha()

sunnyside_up_list = [resize_sunnyside_up_1, resize_sunnyside_up_2]
sunnyside_up_index = 0.0
sunnyside_up_surf = sunnyside_up_list[int(sunnyside_up_index)]

# Load eggsaucer assets
eggsaucer_1 = pygame.transform.scale(pygame.image.load("graphics/egg-enemies/eggsaucer_1.png"), (100, 60)).convert_alpha()
eggsaucer_2 = pygame.transform.scale(pygame.image.load("graphics/egg-enemies/eggsaucer_2.png"), (100, 60)).convert_alpha()
eggsaucer_list = [eggsaucer_1, eggsaucer_2]
eggsaucer_index = 0.0
eggsaucer_surf = eggsaucer_list[int(eggsaucer_index)]

# Load egg king boss assets
egg_king_1 = pygame.transform.scale(pygame.image.load("graphics/egg-enemies/egg_king_1.png"), (120, 150)).convert_alpha()
egg_king_2 = pygame.transform.scale(pygame.image.load("graphics/egg-enemies/egg_king_2.png"), (125, 150)).convert_alpha()
egg_king_list = [egg_king_1, egg_king_2]
egg_king_index = 0.0

# Load star assets - two frames for animation
star_1_surf = pygame.transform.scale(pygame.image.load("graphics/collectibles/star_1.png"), (70, 70)).convert_alpha()
star_2_surf = pygame.transform.scale(pygame.image.load("graphics/collectibles/star_2.png"), (70, 70)).convert_alpha()
star_anim_list = [star_1_surf, star_2_surf]
star_index = 0.0  # Tracks current star animation frame

# Load potion png assets - replacing all filler shapes with actual artwork
egg_bomb_potion_surf = pygame.transform.scale(pygame.image.load("graphics/collectibles/egg_bomb_potion.png"), (50, 50)).convert_alpha()
invincibility_potion_surf = pygame.transform.scale(pygame.image.load("graphics/collectibles/invincibility_potion.png"), (50, 50)).convert_alpha()
triplejump_potion_surf = pygame.transform.scale(pygame.image.load("graphics/collectibles/triplejump_potion.png"), (50, 50)).convert_alpha()
score_doubler_potion_surf = pygame.transform.scale(pygame.image.load("graphics/collectibles/score_doubler_potion.png"), (50, 50)).convert_alpha()  # Score doubler potion image
king_potion_surf = pygame.transform.scale(pygame.image.load("graphics/collectibles/king_potion.png"), (50, 50)).convert_alpha()  # King potion image
extra_life_potion_surf = pygame.transform.scale(pygame.image.load("graphics/collectibles/extra_life_potion.png"), (50, 50)).convert_alpha()

# Load egg bomb explosion effect asset
egg_bomb_explosion_surf = pygame.transform.scale(pygame.image.load("graphics/collectibles/egg_bomb_explosion.png"), (200, 200)).convert_alpha()

obstacle_rect_list = []
powerup_rect_list = []

# Custom timers for spawning
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)

# Score tracking
high_score = 0
start_time = 0
score = 0
bonus_score = 0
stars_collected = 0   # Stars collected this run (replaces coins)
total_stars = 0       # Total stars collected across all games (replaces total coins)

# Boss progression tracking
egg_king_active = False
egg_king_hp = 0
egg_king_defeated_count = 0
egg_king_next_spawn_score = 100
last_powerup_score = 0

# Clickable button areas for the main menu
play_rect = pygame.Rect(0, 0, 0, 0)
inst_rect = pygame.Rect(0, 0, 0, 0)
quit_rect = pygame.Rect(0, 0, 0, 0)


# GAME FUNCTIONS

def display_score():
    """Calculates the current score based on time and draws it to the screen HUD. Score is doubled when score doubler or king potion is active."""
    global score, score_surf, score_rect
    current_time = pygame.time.get_ticks() - start_time

    # Double the raw score if score doubler or king potion is currently active
    if current_ticks < score_doubler_until or current_ticks < king_potion_until:
        score = ((current_time // 1000) * 2) + bonus_score
    else:
        score = (current_time // 1000) + bonus_score

    score_surf = game_font.render(f"SCORE: {score}", False, "Black")
    score_rect = score_surf.get_rect(center=(400, 50))

    pygame.draw.rect(screen, "#c0e8ec", score_rect)
    pygame.draw.rect(screen, "#c0e8ec", score_rect, 10)
    screen.blit(score_surf, score_rect)
    return score


def spawn_obstacle(spawn_choice, x_pos):
    """Creates an obstacle or collectible and adds its hitboxes to the tracking list."""
    if spawn_choice == 'sunnyside_up':
        rect = sunnyside_up_list[0].get_rect(midbottom=(x_pos, 210))
        obstacle_rect_list.append({'rect': rect, 'type': 'sunnyside_up'})
    elif spawn_choice == 'eggsaucer':
        rect = eggsaucer_list[0].get_rect(midbottom=(x_pos, 120))
        obstacle_rect_list.append({'rect': rect, 'type': 'eggsaucer'})
    elif spawn_choice == 'star':
        rect = star_anim_list[0].get_rect(midbottom=(x_pos, 180))
        obstacle_rect_list.append({'rect': rect, 'type': 'star'})
    elif spawn_choice == 'egg_knight':
        rect = egg_knight_list[0].get_rect(midbottom=(x_pos, GROUND_Y))  # Set egg knight position on the ground
        obstacle_rect_list.append({'rect': rect, 'type': 'egg_knight'})
    else:
        rect = egg_list[0].get_rect(midbottom=(x_pos, GROUND_Y))
        obstacle_rect_list.append({'rect': rect, 'type': 'egg'})


def obstacle_movement(obstacle_list):
    """Moves all active obstacles to the left and draws them based on their type."""
    if obstacle_list:
        for active_obs in obstacle_list:
            active_obs['rect'].x -= current_speed

        for active_obs in obstacle_list:
            obs_rect = active_obs['rect']
            obs_type = active_obs['type']

            if obs_type == 'egg':
                screen.blit(egg_surf, obs_rect)
            elif obs_type == 'egg_knight':
                screen.blit(egg_knight_surf, obs_rect)  # Draw egg knight
            elif obs_type == 'sunnyside_up':
                screen.blit(sunnyside_up_surf, obs_rect)
            elif obs_type == 'star':
                # Draw the current star animation frame
                screen.blit(star_anim_list[int(star_index)], obs_rect)
            elif obs_type == 'eggsaucer':
                beam_color = "Yellow" if (pygame.time.get_ticks() // 200) % 2 == 0 else "Orange"
                beam_rect = pygame.Rect(obs_rect.left, obs_rect.bottom, obs_rect.width, GROUND_Y - obs_rect.bottom)
                beam_surf = pygame.Surface((beam_rect.width, beam_rect.height), pygame.SRCALPHA)
                if beam_color == "Yellow":
                    beam_surf.fill((255, 255, 0, 80))
                else:
                    beam_surf.fill((255, 165, 0, 80))
                screen.blit(beam_surf, beam_rect)

                screen.blit(eggsaucer_surf, obs_rect)

        obstacle_list = [obs for obs in obstacle_list if obs['rect'].right > 0]
        return obstacle_list
    else:
        return []


def collisions(player, obstacles):
    """Handles collisions between the player, items, and hazards, including invincibility math."""
    global lives, is_playing, high_score, invincible_timer, score, stars_collected, bonus_score
    if obstacles:
        for active_obs in obstacles[:]:
            obs_rect = active_obs['rect']
            obs_type = active_obs['type']
            if obs_rect.colliderect(player):
                if obs_type == 'star':
                    # Stars collected give double bonus when score doubler or king potion is active
                    if current_ticks < score_doubler_until or current_ticks < king_potion_until:
                        bonus_score += 2
                        stars_collected += 2
                    else:
                        bonus_score += 1
                        stars_collected += 1
                    obstacles.remove(active_obs)
                elif obs_type == 'egg_knight':
                    if current_ticks >= invincible_timer:
                        lives -= 1
                        if lives <= 0:
                            is_playing = False
                            if score > high_score:
                                high_score = score
                        else:
                            invincible_timer = current_ticks + INVINCIBLE_DURATION  # Activate post-hit invincibility
                            obstacles.remove(active_obs)  # Remove obstacle after hit
                            break
                    else:
                        obstacles.remove(active_obs)  # Clear obstacle if player is already invincible
                        break
                else:
                    if current_ticks >= invincible_timer:
                        lives -= 1
                        if lives <= 0:
                            is_playing = False
                            if score > high_score:
                                high_score = score
                        else:
                            invincible_timer = current_ticks + INVINCIBLE_DURATION  # Activate post-hit invincibility
                            obstacles.remove(active_obs)  # Remove obstacle after hit
                            break
                    else:
                        obstacles.remove(active_obs)  # Clear obstacle if player is already invincible
                        break
        return is_playing
    return True


def player_animation():
    """Swaps animation frames based on running or jumping status."""
    global player_index, player_surf

    # Use different player textures if the triple jump power-up is active
    current_walk_list = tj_walk_list if current_ticks < triple_jump_until else player_walk_list
    current_jump_surf = tj_jump if current_ticks < triple_jump_until else player_jump

    if player_rect.bottom >= GROUND_Y:
        player_index += 0.15
        if player_index >= len(current_walk_list):
            player_index = 0
        player_surf = current_walk_list[int(player_index)]
    else:
        player_surf = current_jump_surf


def apply_potion(p_type):
    """Activates a potion effect immediately. Called directly or when dequeued after score doubler ends."""
    global invincible_timer, triple_jump_until, egg_clear_stocked_until, slow_mo_until, lives, score_doubler_until, king_potion_until

    if p_type == 'invincible':
        invincible_timer = current_ticks + 15000        # 15s Invincibility
    elif p_type == 'heart':
        if lives < 5:                                    # Max capacity capped at 5 hearts
            lives += 1                                   # Add 1 life
    elif p_type == 'egg_clear':
        # Stack an additional 20 seconds if the egg bomb timer is already running
        if current_ticks < egg_clear_stocked_until:
            egg_clear_stocked_until += 20000
        else:
            egg_clear_stocked_until = current_ticks + 28000   # Held for 28s max on fresh pickup
    elif p_type == 'slow_mo':
        slow_mo_until = current_ticks + 10000           # 10s Slow-Mo
    elif p_type == 'triple_jump':
        triple_jump_until = current_ticks + 15000       # 15s Triple Jump
    elif p_type == 'score_doubler':
        score_doubler_until = current_ticks + 15000     # 15s Score Doubler
    elif p_type == 'king_potion':
        # King potion grants score doubler, health, and invincibility simultaneously for 10 seconds
        king_potion_until = current_ticks + 10000
        score_doubler_until = current_ticks + 10000     # Doubles score for the king potion duration
        invincible_timer = current_ticks + 10000        # Full invincibility for the king potion duration
        if lives < 5:
            lives += 1                                   # Also grants one extra life like the heart potion


def draw_main_menu():
    """Draws the main menu background, title, and buttons."""
    global play_rect, inst_rect, quit_rect
    screen.fill("black")

    # Show total stars and current high score
    total_stars_surf = small_font.render(f"Total Stars: {total_stars}", True, "Yellow")
    screen.blit(total_stars_surf, (20, 20))

    highest_score_surf = small_font.render(f"Highest Score: {high_score}", True, "White")
    screen.blit(highest_score_surf, (800 - highest_score_surf.get_width() - 20, 20))

    # Game title setup
    title_surf = game_font.render("Eggpocalypse", True, "Red")
    title_rect = title_surf.get_rect(center=(400, 100))
    screen.blit(title_surf, title_rect)

    # Show interactive text buttons
    play_surf = game_font.render("Play Game", True, "Green")
    play_rect = play_surf.get_rect(center=(400, 200))
    screen.blit(play_surf, play_rect)

    inst_surf = game_font.render("Instructions", True, "Cyan")
    inst_rect = inst_surf.get_rect(center=(400, 270))
    screen.blit(inst_surf, inst_rect)

    quit_surf = game_font.render("Quit Game", True, "Orange")
    quit_rect = quit_surf.get_rect(center=(400, 340))
    screen.blit(quit_surf, quit_rect)


def draw_instructions():
    """Draws the instructions screen text and controls."""
    screen.fill("black")

    # Show instructions title
    inst_title_surf = game_font.render("Instructions", True, "Cyan")
    screen.blit(inst_title_surf, inst_title_surf.get_rect(center=(400, 60)))

    # Text strings for objectives and key controls
    txt1 = small_font.render("SPACE / MOUSE CLICK - Jump (Double / Triple Jump available with powerups)", True, "White")
    txt2 = small_font.render("W KEY - Fire Egg Bomb screen clear hazard wipe tool", True, "White")
    txt3 = small_font.render("OBJECTIVE - Dodge breaking eggs, gather stars, and grab potions!", True, "White")
    txt4 = small_font.render("Press M to go back to the Main Menu", True, "Yellow")

    screen.blit(txt1, txt1.get_rect(center=(400, 150)))
    screen.blit(txt2, txt2.get_rect(center=(400, 200)))
    screen.blit(txt3, txt3.get_rect(center=(400, 250)))
    screen.blit(txt4, txt4.get_rect(center=(400, 330)))


def reset_game():
    """Resets all game state variables to start a completely fresh match."""
    global is_playing, game_state, obstacle_rect_list, powerup_rect_list, egg_clear_stocked_until, slow_mo_until, triple_jump_until, explosion_end_time, start_time, score, bonus_score, stars_collected, jump_count, player_index, egg_index, eggsaucer_index, lives, invincible_timer, game_speed, difficulty_level
    global egg_king_active, egg_king_hp, egg_king_defeated_count, egg_king_next_spawn_score, egg_king_index, last_powerup_score, egg_knight_index
    global score_doubler_until, king_potion_until, queued_potions
    is_playing = True
    game_state = 'playing'
    obstacle_rect_list.clear()
    powerup_rect_list.clear()

    # Reset powerup timers
    egg_clear_stocked_until = 0
    slow_mo_until = 0
    triple_jump_until = 0
    explosion_end_time = 0    # Clear explosion visual effect timer
    score_doubler_until = 0   # Clear score doubler timer
    king_potion_until = 0     # Clear king potion timer
    queued_potions.clear()    # Clear any potions that were queued behind the score doubler

    # Reset game mechanics and trackers
    start_time = pygame.time.get_ticks()
    score = 0
    bonus_score = 0
    stars_collected = 0       # Reset stars collected for this run
    jump_count = 0
    player_index = 0.0
    egg_index = 0.0
    eggsaucer_index = 0.0
    egg_knight_index = 0.0    # Reset animation tracker for egg knight
    lives = 3
    invincible_timer = 0
    game_speed = 5
    difficulty_level = 0

    # Reset boss fight info
    egg_king_active = False
    egg_king_hp = 0
    egg_king_defeated_count = 0
    egg_king_next_spawn_score = 100
    egg_king_index = 0.0
    last_powerup_score = 0

    pygame.time.set_timer(obstacle_timer, 1500)
    bg_music.play(loops=-1)


# MAIN GAME LOOP

while running:
    current_ticks = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif game_state == 'main_menu':
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    main_menu_music.stop()  # Stop menu background music before starting game
                    reset_game()
                elif inst_rect.collidepoint(event.pos):
                    game_state = 'instructions'
                elif quit_rect.collidepoint(event.pos):
                    running = False

        elif game_state == 'instructions':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                game_state = 'main_menu'

        elif game_state == 'playing':
            # Press 'W' to use screen clear bomb
            if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                if current_ticks < egg_clear_stocked_until:
                    obstacle_rect_list = [obs for obs in obstacle_rect_list if obs['type'] not in ('egg', 'egg_knight', 'sunnyside_up', 'eggsaucer', 'star')]
                    egg_clear_stocked_until = 0
                    explosion_end_time = current_ticks + 600  # Show explosion effect for 0.6 seconds

                    if egg_king_active:
                        egg_king_hp -= 1
                        if egg_king_hp <= 0:
                            egg_king_active = False
                            egg_king_defeated_count += 1
                            egg_king_next_spawn_score = score + 100 + (20 * egg_king_defeated_count)

            # Handle jumping (Space or Mouse Click)
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
                    or event.type == pygame.MOUSEBUTTONDOWN):
                # Set jump limits based on active powerup status
                max_jumps = 3 if current_ticks < triple_jump_until else 2
                if player_rect.bottom >= GROUND_Y or jump_count < max_jumps:
                    players_gravity_speed = JUMP_GRAVITY_START_SPEED
                    jump_sound.play()  # Play jump sound
                    jump_count += 1

            # Spawn obstacles/collectibles
            if event.type == obstacle_timer:
                if egg_king_active:
                    egg_enemies_pool = ['egg', 'sunnyside_up', 'eggsaucer']
                    if score >= 100:
                        egg_enemies_pool.append('egg_knight')

                    # Boss phase spawns only one additional enemy per tick instead of two
                    spawn_obstacle(choice(egg_enemies_pool), randint(900, 1050))
                else:
                    spawn_choices = ['sunnyside_up', 'egg', 'egg', 'egg', 'eggsaucer', 'star']
                    if score >= 100:
                        spawn_choices.append('egg_knight')
                    spawn_choice = choice(spawn_choices)
                    spawn_obstacle(spawn_choice, randint(900, 1100))

        elif game_state == 'game_over':
            # Restart game on SPACE press
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                defeat_music.stop()  # Stop game over music
                reset_game()
            # Return to main menu on M key press
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                defeat_music.stop()  # Stop game over music
                main_menu_music.play(loops=-1)  # Loop main menu music
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
        # Sky cycle order: day -> sunset -> night -> midnight -> sunset -> day, each phase lasting 50 seconds
        sky_index = ((pygame.time.get_ticks() - start_time) // 50000) % len(sky_list)
        screen.blit(sky_list[sky_index], (0, 0))
        screen.blit(GROUND_SURF, (0, GROUND_Y))
        score = display_score()

        # Check if the Egg King boss should spawn
        if score >= egg_king_next_spawn_score and not egg_king_active:
            egg_king_active = True
            egg_king_hp = 2 + (1 * egg_king_defeated_count)

        # Spawn a power-up every 40 score points
        if score >= last_powerup_score + 40:
            last_powerup_score = (score // 40) * 40
            # Always force an egg_clear drop during boss phase; otherwise pick from the full potion pool
            p_type = 'egg_clear' if egg_king_active else choice(['invincible', 'heart', 'egg_clear', 'slow_mo', 'triple_jump', 'score_doubler', 'king_potion'])
            p_rect = pygame.Rect(0, 0, 30, 30)
            p_rect.midbottom = (randint(900, 1100), GROUND_Y)
            powerup_rect_list.append({'rect': p_rect, 'type': p_type})

        # Render stars collected section directly below the score
        stars_hud_surf = small_font.render(f"Stars earned: {stars_collected}", False, "Black")
        stars_hud_rect = stars_hud_surf.get_rect(center=(400, 95))
        screen.blit(stars_hud_surf, stars_hud_rect)

        # Render lives icons on screen
        for i in range(lives):
            heart_rect = player_heart_surf.get_rect(topleft=(20 + (i * 40), 20))  # Draw player hearts horizontally
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

        # Handle egg knight animation status tracker
        egg_knight_index += 0.15  # Animate egg knight
        if egg_knight_index >= len(egg_knight_list): egg_knight_index = 0
        egg_knight_surf = egg_knight_list[int(egg_knight_index)]

        # Advance the star animation frame each tick
        star_index += 0.08
        if star_index >= len(star_anim_list): star_index = 0

        # Draw and animate the floating boss if active
        if egg_king_active:
            egg_king_index += 0.05
            if egg_king_index >= len(egg_king_list): egg_king_index = 0
            egg_king_surf = egg_king_list[int(egg_king_index)]
            egg_king_rect = egg_king_surf.get_rect(center=(680, 150))
            screen.blit(egg_king_surf, egg_king_rect)

        sunnyside_up_index += 0.05
        if sunnyside_up_index >= len(sunnyside_up_list): sunnyside_up_index = 0
        sunnyside_up_surf = sunnyside_up_list[int(sunnyside_up_index)]

        eggsaucer_index += 0.1
        if eggsaucer_index >= len(eggsaucer_list): eggsaucer_index = 0
        eggsaucer_surf = eggsaucer_list[int(eggsaucer_index)]

        # Render active powerup tokens using their actual potion png artwork
        for pu in powerup_rect_list:
            if pu['type'] == 'invincible':
                screen.blit(invincibility_potion_surf, pu['rect'])
            elif pu['type'] == 'heart':
                screen.blit(extra_life_potion_surf, pu['rect'])
            elif pu['type'] == 'egg_clear':
                screen.blit(egg_bomb_potion_surf, pu['rect'])
            elif pu['type'] == 'slow_mo':
                # Slow mo retains a labeled circle since no dedicated png was specified
                pygame.draw.circle(screen, "Cyan", pu['rect'].center, 15)
                lbl_surf = small_font.render("S", True, "White")
                screen.blit(lbl_surf, lbl_surf.get_rect(center=pu['rect'].center))
            elif pu['type'] == 'triple_jump':
                screen.blit(triplejump_potion_surf, pu['rect'])
            elif pu['type'] == 'score_doubler':
                screen.blit(score_doubler_potion_surf, pu['rect'])   # Draw score doubler potion png
            elif pu['type'] == 'king_potion':
                screen.blit(king_potion_surf, pu['rect'])            # Draw king potion png

        # Apply gravity mechanics and anti-gravity beam adjustments
        player_under_beam = False
        for obs in obstacle_rect_list:
            if obs['type'] == 'eggsaucer':
                obs_rect = obs['rect']
                if player_rect.right > obs_rect.left and player_rect.left < obs_rect.right:
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

        # Check if the score doubler just expired and drain the queued potion list
        score_doubler_just_ended = current_ticks >= score_doubler_until and score_doubler_until != 0 and len(queued_potions) > 0
        if score_doubler_just_ended:
            for queued_type in queued_potions:
                apply_potion(queued_type)   # Activate every potion that was held in queue
            queued_potions.clear()
            score_doubler_until = 0         # Zero out the timer so this block doesn't re-trigger

        # Handle collecting powerups
        for pu in powerup_rect_list[:]:
            if player_rect.colliderect(pu['rect']):
                p_type = pu['type']
                # Potions other than score_doubler and king_potion are queued when score doubler is active
                score_doubler_active = current_ticks < score_doubler_until
                if score_doubler_active and p_type not in ('score_doubler', 'king_potion'):
                    queued_potions.append(p_type)   # Hold the potion until the score doubler ends
                else:
                    apply_potion(p_type)            # Apply the potion immediately
                powerup_rect_list.remove(pu)

        # Check hazard hit collisions
        is_playing = collisions(player_rect, obstacle_rect_list)

        # Trigger game over mechanics if player ran out of lives
        if not is_playing:
            game_state = 'game_over'
            total_stars += stars_collected   # Add this run's stars to the all-time total
            bg_music.stop()
            defeat_music.play(loops=-1)  # Play game over music on loop

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
        if current_ticks < score_doubler_until:
            rem = (score_doubler_until - current_ticks) // 1000
            ui_surf = small_font.render(f"SCORE DOUBLER: {rem}s", True, "Gold")
            screen.blit(ui_surf, (20, hud_y))
            hud_y += 25
            # Show how many potions are waiting in queue so the player knows they have a backlog
            if len(queued_potions) > 0:
                queue_surf = small_font.render(f"  QUEUED POTIONS: {len(queued_potions)}", True, "Gold")
                screen.blit(queue_surf, (20, hud_y))
                hud_y += 25
        if current_ticks < king_potion_until:
            rem = (king_potion_until - current_ticks) // 1000
            ui_surf = small_font.render(f"KING POTION: {rem}s", True, "Violet")
            screen.blit(ui_surf, (20, hud_y))
            hud_y += 25

        # Render full screen egg bomb explosion if active
        if current_ticks < explosion_end_time:
            explosion_scaled = pygame.transform.scale(egg_bomb_explosion_surf, (800, 800))

            # Get the display surface
            screen_rect = screen.get_rect()
            explosion_rect = explosion_scaled.get_rect(center=screen_rect.center)

            # Blit using the centered rectangle
            screen.blit(explosion_scaled, explosion_rect)

    # Game Over screen assets
    elif game_state == 'game_over':
        screen.fill("black")

        game_over_surf = game_font.render("GAME OVER!", False, "Red")
        game_over_rect = game_over_surf.get_rect(center=(400, 60))

        current_score_surf = small_font.render(f"SCORE ACHIEVED: {score}", False, "Light Blue")
        current_score_rect = current_score_surf.get_rect(center=(400, 130))

        # Display stars earned this run instead of coins
        current_stars_surf = small_font.render(f"STARS EARNED: {stars_collected}", False, "Yellow")
        current_stars_rect = current_stars_surf.get_rect(center=(400, 175))

        high_score_surf = game_font.render(f"HIGH SCORE: {high_score}", False, "White")
        high_score_rect = high_score_surf.get_rect(center=(400, 240))

        restart_surf = small_font.render("Press SPACE to Play Again", False, "Gray")
        restart_rect = restart_surf.get_rect(center=(400, 310))

        menu_surf = small_font.render("Press M to Return to Main Menu", False, "Gray")
        menu_rect = menu_surf.get_rect(center=(400, 350))

        screen.blit(game_over_surf, game_over_rect)
        screen.blit(current_score_surf, current_score_rect)
        screen.blit(current_stars_surf, current_stars_rect)
        screen.blit(high_score_surf, high_score_rect)
        screen.blit(restart_surf, restart_rect)
        screen.blit(menu_surf, menu_rect)

    pygame.display.update()
    clock.tick(60)

pygame.quit()