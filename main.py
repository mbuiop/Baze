import pygame
import sys
import math
import random
from pygame.locals import *

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Shooting Game")

# Colors
BACKGROUND = (10, 20, 30)
GRID_COLOR = (40, 60, 80)
GUN_COLOR = (180, 180, 200)
GUN_DETAIL = (120, 120, 140)
TARGET_COLOR = (220, 80, 60)
BULLET_COLOR = (255, 215, 0)
TEXT_COLOR = (220, 220, 220)
UI_BG = (30, 40, 50, 180)
UI_BORDER = (70, 130, 180)

# Game variables
score = 0
lives = 3
level = 1
game_over = False
game_won = False

# Gun properties
gun_x = WIDTH // 2
gun_y = HEIGHT - 100
gun_width = 40
gun_height = 80
gun_angle = 0

# Bullets
bullets = []
bullet_speed = 10
bullet_radius = 5

# Targets
targets = []
target_spawn_timer = 0
target_spawn_delay = 60  # frames

# Touch controls
touch_areas = {
    "left": pygame.Rect(0, HEIGHT//2, WIDTH//3, HEIGHT//2),
    "right": pygame.Rect(2*WIDTH//3, HEIGHT//2, WIDTH//3, HEIGHT//2),
    "shoot": pygame.Rect(WIDTH//3, HEIGHT//2, WIDTH//3, HEIGHT//2)
}

# Fonts
font_large = pygame.font.SysFont(None, 72)
font_medium = pygame.font.SysFont(None, 48)
font_small = pygame.font.SysFont(None, 36)

# Particle system for explosions
particles = []

class Target:
    def __init__(self):
        self.size = random.randint(30, 60)
        self.x = random.randint(self.size, WIDTH - self.size)
        self.y = random.randint(50, HEIGHT // 3)
        self.z = random.randint(1, 5)  # 3D depth
        self.speed_x = random.uniform(-1.5, 1.5) * (6 - self.z) / 2
        self.speed_y = random.uniform(0.2, 0.8) * (6 - self.z) / 2
        self.color = (
            random.randint(150, 255),
            random.randint(50, 150),
            random.randint(50, 150)
        self.hit = False
        self.hit_timer = 0
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Bounce off walls
        if self.x < self.size or self.x > WIDTH - self.size:
            self.speed_x *= -1
            
        # Reset if off screen
        if self.y > HEIGHT + self.size:
            self.reset()
            
        # Update hit effect
        if self.hit:
            self.hit_timer += 1
            if self.hit_timer > 15:
                self.reset()
                
    def reset(self):
        self.size = random.randint(30, 60)
        self.x = random.randint(self.size, WIDTH - self.size)
        self.y = -self.size
        self.z = random.randint(1, 5)
        self.speed_x = random.uniform(-1.5, 1.5) * (6 - self.z) / 2
        self.speed_y = random.uniform(0.2, 0.8) * (6 - self.z) / 2
        self.color = (
            random.randint(150, 255),
            random.randint(50, 150),
            random.randint(50, 150))
        self.hit = False
        self.hit_timer = 0
        
    def draw(self, surface):
        # Draw 3D cube
        depth = self.size * self.z / 5
        offset = depth / 2
        
        # Front face
        front_rect = pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)
        pygame.draw.rect(surface, self.color, front_rect)
        pygame.draw.rect(surface, (255, 255, 255), front_rect, 2)
        
        # Top face
        top_points = [
            (self.x - self.size//2, self.y - self.size//2),
            (self.x - self.size//2 + offset, self.y - self.size//2 - offset),
            (self.x + self.size//2 + offset, self.y - self.size//2 - offset),
            (self.x + self.size//2, self.y - self.size//2)
        ]
        pygame.draw.polygon(surface, (min(255, self.color[0] + 40), min(255, self.color[1] + 40), min(255, self.color[2] + 40)), top_points)
        pygame.draw.polygon(surface, (255, 255, 255), top_points, 2)
        
        # Side face
        side_points = [
            (self.x + self.size//2, self.y - self.size//2),
            (self.x + self.size//2 + offset, self.y - self.size//2 - offset),
            (self.x + self.size//2 + offset, self.y + self.size//2 - offset),
            (self.x + self.size//2, self.y + self.size//2)
        ]
        pygame.draw.polygon(surface, (max(0, self.color[0] - 40), max(0, self.color[1] - 40), max(0, self.color[2] - 40)), side_points)
        pygame.draw.polygon(surface, (255, 255, 255), side_points, 2)
        
        # Hit effect
        if self.hit:
            pygame.draw.circle(surface, (255, 255, 200), (self.x, self.y), self.size + self.hit_timer, 3)
            
    def get_rect(self):
        return pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)

class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = bullet_speed
        self.radius = bullet_radius
        self.trail = []
        
    def update(self):
        # Move bullet
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        # Add to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)
            
        # Return True if bullet is out of screen
        return (self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT)
        
    def draw(self, surface):
        # Draw trail
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = 100 + i * 30
            radius = self.radius * i / len(self.trail)
            pygame.draw.circle(surface, (255, 200, 50, alpha), (int(trail_x), int(trail_y)), int(radius))
            
        # Draw bullet
        pygame.draw.circle(surface, BULLET_COLOR, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 150, 50), (int(self.x), int(self.y)), self.radius - 2)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 6)
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-3, 3)
        self.life = 30
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.size = max(0, self.size - 0.1)
        
    def draw(self, surface):
        alpha = min(255, self.life * 8)
        pygame.draw.circle(surface, (*self.color, alpha), (int(self.x), int(self.y)), int(self.size))

def create_explosion(x, y, color):
    for _ in range(30):
        particles.append(Particle(x, y, color))

def draw_gun(surface, x, y, angle):
    # Draw gun base
    pygame.draw.circle(surface, GUN_DETAIL, (x, y), gun_width // 1.5)
    pygame.draw.circle(surface, GUN_COLOR, (x, y), gun_width // 1.8)
    
    # Calculate gun barrel position
    end_x = x + math.cos(angle) * gun_height
    end_y = y + math.sin(angle) * gun_height
    
    # Draw gun barrel
    pygame.draw.line(surface, GUN_COLOR, (x, y), (end_x, end_y), gun_width // 2)
    pygame.draw.line(surface, GUN_DETAIL, (x, y), (end_x, end_y), gun_width // 4)
    
    # Draw gun tip
    pygame.draw.circle(surface, GUN_DETAIL, (int(end_x), int(end_y)), gun_width // 3)

def draw_background(surface):
    # Draw gradient background
    for y in range(0, HEIGHT, 2):
        color_value = max(0, min(255, 30 + y // 4))
        pygame.draw.line(surface, (10, color_value//2, color_value), (0, y), (WIDTH, y))
    
    # Draw grid for 3D effect
    for x in range(0, WIDTH, 40):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y), 1)

def draw_ui(surface):
    # Draw score panel
    pygame.draw.rect(surface, UI_BG, (10, 10, 250, 120), 0, 15)
    pygame.draw.rect(surface, UI_BORDER, (10, 10, 250, 120), 3, 15)
    
    score_text = font_medium.render(f"Score: {score}", True, TEXT_COLOR)
    level_text = font_medium.render(f"Level: {level}", True, TEXT_COLOR)
    surface.blit(score_text, (30, 30))
    surface.blit(level_text, (30, 75))
    
    # Draw lives
    pygame.draw.rect(surface, UI_BG, (WIDTH - 260, 10, 250, 70), 0, 15)
    pygame.draw.rect(surface, UI_BORDER, (WIDTH - 260, 10, 250, 70), 3, 15)
    
    lives_text = font_medium.render(f"Lives: {lives}", True, TEXT_COLOR)
    surface.blit(lives_text, (WIDTH - 230, 30))
    
    # Draw touch control areas
    pygame.draw.rect(surface, (40, 100, 180, 100), touch_areas["left"], 0, 20)
    pygame.draw.rect(surface, (180, 60, 60, 100), touch_areas["shoot"], 0, 20)
    pygame.draw.rect(surface, (40, 100, 180, 100), touch_areas["right"], 0, 20)
    
    left_text = font_small.render("MOVE LEFT", True, (220, 220, 255))
    shoot_text = font_small.render("SHOOT", True, (255, 220, 220))
    right_text = font_small.render("MOVE RIGHT", True, (220, 220, 255))
    
    surface.blit(left_text, (touch_areas["left"].centerx - left_text.get_width()//2, 
                           touch_areas["left"].centery - left_text.get_height()//2))
    surface.blit(shoot_text, (touch_areas["shoot"].centerx - shoot_text.get_width()//2, 
                           touch_areas["shoot"].centery - shoot_text.get_height()//2))
    surface.blit(right_text, (touch_areas["right"].centerx - right_text.get_width()//2, 
                           touch_areas["right"].centery - right_text.get_height()//2))

def draw_game_over(surface):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    
    if game_won:
        text = font_large.render("YOU WIN!", True, (100, 255, 100))
    else:
        text = font_large.render("GAME OVER", True, (255, 100, 100))
    
    surface.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 80))
    
    score_text = font_medium.render(f"Final Score: {score}", True, TEXT_COLOR)
    surface.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
    
    restart_text = font_medium.render("Press R to Restart", True, TEXT_COLOR)
    surface.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 80))

def reset_game():
    global score, lives, level, game_over, game_won, bullets, targets, particles
    score = 0
    lives = 3
    level = 1
    game_over = False
    game_won = False
    bullets = []
    targets = []
    particles = []
    
    # Create initial targets
    for _ in range(5):
        targets.append(Target())

# Initial game setup
reset_game()

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            
        if event.type == KEYDOWN:
            if event.key == K_r and (game_over or game_won):
                reset_game()
            if event.key == K_ESCAPE:
                running = False
                
        # Touch controls
        if event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if touch_areas["left"].collidepoint(mouse_pos):
                gun_x = max(gun_width, gun_x - 20)
            elif touch_areas["right"].collidepoint(mouse_pos):
                gun_x = min(WIDTH - gun_width, gun_x + 20)
            elif touch_areas["shoot"].collidepoint(mouse_pos):
                # Create a new bullet
                bullets.append(Bullet(gun_x, gun_y, gun_angle))
                
        # Keyboard controls for testing
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                gun_x = max(gun_width, gun_x - 20)
            if event.key == K_RIGHT:
                gun_x = min(WIDTH - gun_width, gun_x + 20)
            if event.key == K_SPACE:
                bullets.append(Bullet(gun_x, gun_y, gun_angle))
    
    # Update gun angle to point toward mouse
    mouse_x, mouse_y = pygame.mouse.get_pos()
    gun_angle = math.atan2(mouse_y - gun_y, mouse_x - gun_x)
    
    if not game_over and not game_won:
        # Spawn new targets
        target_spawn_timer += 1
        if target_spawn_timer >= target_spawn_delay:
            target_spawn_timer = 0
            if len(targets) < 5 + level:
                targets.append(Target())
        
        # Update targets
        for target in targets:
            target.update()
            
        # Update bullets
        for bullet in bullets[:]:
            if bullet.update():
                bullets.remove(bullet)
                continue
                
            # Check for collisions
            for target in targets:
                if not target.hit:
                    # Simple distance-based collision
                    dist = math.sqrt((bullet.x - target.x)**2 + (bullet.y - target.y)**2)
                    if dist < bullet.radius + target.size//2:
                        target.hit = True
                        bullets.remove(bullet)
                        score += int(100 * target.z)  # More points for closer targets
                        create_explosion(target.x, target.y, target.color)
                        break
                        
        # Check for missed targets
        for target in targets:
            if target.y > HEIGHT and not target.hit:
                lives -= 1
                target.reset()
                if lives <= 0:
                    game_over = True
                    
        # Update particles
        for particle in particles[:]:
            particle.update()
            if particle.life <= 0:
                particles.remove(particle)
                
        # Level progression
        if score > level * 1000:
            level += 1
            target_spawn_delay = max(20, 60 - level * 5)
            
        # Win condition
        if level >= 10:
            game_won = True
    
    # Drawing
    screen.fill(BACKGROUND)
    draw_background(screen)
    
    # Draw particles
    for particle in particles:
        particle.draw(screen)
    
    # Draw targets
    for target in targets:
        target.draw(screen)
    
    # Draw bullets
    for bullet in bullets:
        bullet.draw(screen)
    
    # Draw gun
    draw_gun(screen, gun_x, gun_y, gun_angle)
    
    # Draw UI
    draw_ui(screen)
    
    # Draw game over screen
    if game_over or game_won:
        draw_game_over(screen)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()