import pygame
import random
import math

# Setup
pygame.init()
WIDTH, HEIGHT = 600, 600
CENTER = WIDTH // 2, HEIGHT // 2
FPS = 60

# Colors
WHITE = (255, 255, 255)
GOLD = (212, 175, 55)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gerson Shield Fight")
clock = pygame.time.Clock()

# Game state
score = 0
high_score = 0
hp = 3

# Soul & shield
soul_radius = 10
box_size = soul_radius * 4
shield_thickness = 6
frame_thickness = 1
octagon_mode = False
shield_angle = 90

# Timing
arrow_interval = 30
arrow_timer = 0
min_interval = 8
elapsed_time = 0
start_ticks = pygame.time.get_ticks()
upgrade_time = 12000

arrows = []
TRAVEL_TIME = 2.5  # seconds
arrow_spawn_queue = []

arrows_per_sec = 2
max_arrows_per_sec = 4
ramp_start_time = 12000
ramp_interval = 8000
last_ramp_time = ramp_start_time

soul_img = pygame.image.load("assets/soul.png").convert_alpha()
arrow_imgs = {k: pygame.image.load(f"assets/arrow_{d}.png").convert_alpha()
              for k, d in zip([0, 45, 90, 135, 180, 225, 270, 315],
                              ["right", "uright", "up", "uleft", "left", "dleft", "down", "dright"])}

red_arrow_imgs = {k: pygame.image.load(f"assets/red_arrow_{d}.png").convert_alpha()
              for k, d in zip([0, 45, 90, 135, 180, 225, 270, 315],
                              ["right", "uright", "up", "uleft", "left", "dleft", "down", "dright"])}

pygame.mixer.init()
pygame.mixer.music.load("assets/music.ogg")
pygame.mixer.music.set_volume(0.4)

sfx_block = pygame.mixer.Sound("assets/block.wav")
sfx_hit = pygame.mixer.Sound("assets/hurt.wav")
sfx_game_over = pygame.mixer.Sound("assets/game_over.wav")

sfx_block.set_volume(0.2)
sfx_hit.set_volume(0.5)
sfx_game_over.set_volume(0.5)

small_font = pygame.font.SysFont(None, 20)
font = pygame.font.SysFont(None, 30)
large_font = pygame.font.SysFont(None, 40)

DIRECTION_ORDER_8 = [0, 45, 90, 135, 180, 225, 270, 315]
DIRECTIONS = {
    0:  (1, 0), 45: (math.sqrt(0.5), -math.sqrt(0.5)), 90: (0, -1),
    135: (-math.sqrt(0.5), -math.sqrt(0.5)), 180: (-1, 0),
    225: (-math.sqrt(0.5), math.sqrt(0.5)), 270: (0, 1), 315: (math.sqrt(0.5), math.sqrt(0.5))
}

def draw_text(text, x, y, color=WHITE, font_obj=font):
    label = font_obj.render(text, True, color)
    screen.blit(label, (x, y))

def queue_arrow():
    global arrow_spawn_queue, last_arrow_angle
    if octagon_mode:
        roll = random.random()
        index = DIRECTION_ORDER_8.index(last_arrow_angle)
        if roll < 0.25:
            angle = DIRECTION_ORDER_8[(index - 1) % 8]
        elif roll < 0.5:
            angle = DIRECTION_ORDER_8[(index + 1) % 8]
        else:
            angle = random.choice(DIRECTION_ORDER_8)
    else:
        angle = random.choice([0, 90, 180, 270])
    last_arrow_angle = angle

    dx, dy = DIRECTIONS[angle]
    base_dist = WIDTH // 2 + 50
    x = CENTER[0] + dx * base_dist
    y = CENTER[1] + dy * base_dist

    speed = random.uniform(2.5, 5.5)
    dist = speed * TRAVEL_TIME * FPS  # how far it should start away based on speed
    x = CENTER[0] + dx * dist
    y = CENTER[1] + dy * dist

    vx = -dx * speed
    vy = -dy * speed

    arrow_data = {
        'x': x, 'y': y, 'vx': vx, 'vy': vy,
        'angle': angle
    }
    arrow_spawn_queue.append((pygame.time.get_ticks() + int(TRAVEL_TIME * 1000), arrow_data))

def draw_soul():
    rect = soul_img.get_rect(center=CENTER)
    screen.blit(soul_img, rect)

def draw_shield_shape():
    cx, cy = CENTER
    if not octagon_mode:
        half = box_size // 2
        pygame.draw.rect(screen, GREEN, (cx - half, cy - half, box_size, box_size), frame_thickness)
        if shield_angle == 90:
            pygame.draw.line(screen, WHITE, (cx - half, cy - half), (cx + half, cy - half), shield_thickness)
        elif shield_angle == 270:
            pygame.draw.line(screen, WHITE, (cx - half, cy + half), (cx + half, cy + half), shield_thickness)
        elif shield_angle == 180:
            pygame.draw.line(screen, WHITE, (cx - half, cy - half), (cx - half, cy + half), shield_thickness)
        elif shield_angle == 0:
            pygame.draw.line(screen, WHITE, (cx + half, cy - half), (cx + half, cy + half), shield_thickness)
    else:
        r = box_size / math.sqrt(2)
        points = [(cx + r * math.cos(math.radians(45 * i - 22.5)),
                   cy - r * math.sin(math.radians(45 * i - 22.5))) for i in range(8)]
        pygame.draw.polygon(screen, GREEN, points, frame_thickness)
        idx = list(DIRECTIONS.keys()).index(shield_angle)
        p1, p2 = points[idx], points[(idx + 1) % 8]
        pygame.draw.line(screen, WHITE, p1, p2, shield_thickness)

def update_arrows():
    global hp, score
    cx, cy = CENTER
    block_radius = box_size / 2 + 10
    hit_radius = box_size / 2 - 10
    for arrow in arrows[:]:
        arrow['x'] += arrow['vx']
        arrow['y'] += arrow['vy']
        dx = arrow['x'] - cx
        dy = arrow['y'] - cy
        dist = math.hypot(dx, dy)
        if dist < hit_radius:
            if arrow['angle'] != shield_angle:
                hp -= 1
                sfx_hit.play()
            arrows.remove(arrow)
        elif dist < block_radius:
            if arrow['angle'] == shield_angle:
                score += 1
                sfx_block.play()
                arrows.remove(arrow)

def draw_arrows():
    center_x = screen.get_width() // 2
    center_y = screen.get_height() // 2

    min_dist = float('inf')
    closest_index = -1
    for i, arrow in enumerate(arrows):
        dx = arrow['x'] - center_x
        dy = arrow['y'] - center_y
        dist = dx * dx + dy * dy  # No need for sqrt for comparison
        if dist < min_dist:
            min_dist = dist
            closest_index = i

    for i, arrow in enumerate(arrows):
        angle = arrow['angle']
        img = red_arrow_imgs[angle] if i == closest_index else arrow_imgs[angle]
        rect = img.get_rect(center=(arrow['x'], arrow['y']))
        screen.blit(img, rect)

def get_direction_from_keys(keys):
    if not octagon_mode:
        if keys[pygame.K_UP]: return 90
        if keys[pygame.K_DOWN]: return 270
        if keys[pygame.K_LEFT]: return 180
        if keys[pygame.K_RIGHT]: return 0
    else:
        up, down, left, right = keys[pygame.K_UP], keys[pygame.K_DOWN], keys[pygame.K_LEFT], keys[pygame.K_RIGHT]
        if up and left: return 135
        if up and right: return 45
        if down and left: return 225
        if down and right: return 315
        if up: return 90
        if down: return 270
        if left: return 180
        if right: return 0
    return None

# Start screen state
start_screen = True
running = True
game_over = False

while running:
    screen.fill(BLACK)
    dt = clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if start_screen:
                start_screen = False
                pygame.mixer.music.play(-1)
                start_ticks = pygame.time.get_ticks()
            elif game_over and event.key == pygame.K_r:
                arrows.clear()
                score, hp = 0, 3
                arrow_timer = 0
                shield_angle = 90
                arrows_per_sec = 2
                octagon_mode = False
                last_ramp_time = pygame.time.get_ticks() + (ramp_start_time - 0)
                start_ticks = pygame.time.get_ticks()
                arrow_spawn_queue = []
                game_over = False
                pygame.mixer.music.play(-1)

    if start_screen:
        draw_text("GERSON SHIELD FIGHT", WIDTH//2 - 160, HEIGHT//2 - 60, GREEN, large_font)
        draw_text("Use arrow keys to rotate the shield.", WIDTH//2 - 170, HEIGHT//2 - 20)
        draw_text("Block arrows from hitting the soul.", WIDTH//2 - 170, HEIGHT//2 + 10)
        draw_text("Press any key to start!", WIDTH//2 - 120, HEIGHT//2 + 60, GOLD)
        draw_text("Made by\nLennyTheSniper", WIDTH//2 - 290, HEIGHT//2 + 260, font_obj=small_font)
    elif not game_over:
        elapsed_time = pygame.time.get_ticks() - start_ticks
        if pygame.time.get_ticks() >= ramp_start_time and pygame.time.get_ticks() - last_ramp_time >= ramp_interval:
            if arrows_per_sec < max_arrows_per_sec:
                arrows_per_sec += 0.05
                last_ramp_time = pygame.time.get_ticks()
        arrow_interval = int(FPS / arrows_per_sec)
        if elapsed_time >= upgrade_time:
            octagon_mode = True
        arrow_timer += 1
        if arrow_timer >= arrow_interval:
            queue_arrow()
            arrow_timer = 0

        now = pygame.time.get_ticks()
        for item in arrow_spawn_queue[:]:
            spawn_time, arrow = item
            if now >= spawn_time:
                arrows.append(arrow)
                arrow_spawn_queue.remove(item)
        keys = pygame.key.get_pressed()
        dir_angle = get_direction_from_keys(keys)
        if dir_angle is not None:
            shield_angle = dir_angle
        update_arrows()
        draw_arrows()
        draw_soul()
        draw_shield_shape()
        draw_text(f"Score: {score}", 10, 10)
        draw_text(f"High Score: {high_score}", 10, 35)
        draw_text(f"HP: {hp}", 10, 60)
        draw_text(f"Time: {elapsed_time // 1000}", 10, 85)
        if hp <= 0:
            game_over = True
            pygame.mixer.music.stop()
            sfx_game_over.play()
            high_score = max(high_score, score)
    else:
        draw_text("GAME OVER", WIDTH // 2 - 70, HEIGHT // 2 - 30, RED)
        draw_text("Press R to Restart", WIDTH // 2 - 100, HEIGHT // 2)
        draw_text(f"Score: {score}", WIDTH // 2 - 45, HEIGHT // 2 + 40, font_obj=small_font)
        draw_text(f"High Score: {high_score}", WIDTH // 2 - 60, HEIGHT // 2 + 60, font_obj=small_font)

    pygame.display.flip()

pygame.quit()