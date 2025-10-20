import pygame
import random
import math
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("جنگنده مدرن - Modern Fighter")

# Colors
BLACK = (0, 0, 0)
DARK_BLUE = (10, 20, 50)
BLUE = (30, 144, 255)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GREEN = (50, 205, 50)
ORANGE = (255, 165, 0)

# Load images (using pygame drawing for simplicity)
def create_fighter():
    surf = pygame.Surface((60, 40), pygame.SRCALPHA)
    # Main body
    pygame.draw.polygon(surf, BLUE, [(0, 20), (60, 10), (60, 30), (0, 20)])
    # Cockpit
    pygame.draw.ellipse(surf, DARK_BLUE, (40, 15, 15, 10))
    # Wings
    pygame.draw.polygon(surf, BLUE, [(20, 0), (30, 10), (20, 10)])
    pygame.draw.polygon(surf, BLUE, [(20, 40), (30, 30), (20, 30)])
    # Engine glow
    for i in range(3):
        pygame.draw.polygon(surf, YELLOW, [(0, 18+i), (10, 17+i), (0, 18+i)])
        pygame.draw.polygon(surf, ORANGE, [(0, 20+i), (8, 19+i), (0, 20+i)])
    return surf

def create_enemy():
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.rect(surf, RED, (0, 0, 30, 30))
    pygame.draw.polygon(surf, RED, [(15, 30), (0, 40), (30, 40)])
    pygame.draw.circle(surf, WHITE, (15, 15), 8)
    return surf

def create_bullet():
    surf = pygame.Surface((5, 10), pygame.SRCALPHA)
    pygame.draw.rect(surf, YELLOW, (0, 0, 5, 10))
    pygame.draw.rect(surf, ORANGE, (0, 0, 5, 5))
    return surf

def create_explosion(radius):
    surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    pygame.draw.circle(surf, ORANGE, (radius, radius), radius)
    pygame.draw.circle(surf, YELLOW, (radius, radius), radius//2)
    return surf

# Game classes
class Fighter:
    def __init__(self):
        self.image = create_fighter()
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT-100))
        self.speed = 8
        self.health = 100
        self.last_shot = 0
        self.shoot_delay = 200  # milliseconds

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

    def shoot(self, current_time):
        if current_time - self.last_shot > self.shoot_delay:
            self.last_shot = current_time
            return Bullet(self.rect.centerx, self.rect.top)
        return None

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Enemy:
    def __init__(self):
        self.image = create_enemy()
        self.rect = self.image.get_rect(center=(random.randint(30, WIDTH-30), -30))
        self.speed = random.randint(2, 5)
        self.health = 10

    def update(self):
        self.rect.y += self.speed
        return self.rect.top > HEIGHT

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Bullet:
    def __init__(self, x, y):
        self.image = create_bullet()
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed
        return self.rect.bottom < 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Particle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, random.randint(2, 6), random.randint(2, 6))
        self.color = random.choice([RED, ORANGE, YELLOW])
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-2, 2)
        self.lifetime = random.randint(20, 40)

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        self.lifetime -= 1
        return self.lifetime <= 0

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.2, 1.0)
        
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
            
    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.size)

# Game setup
fighter = Fighter()
enemies = []
bullets = []
particles = []
stars = [Star() for _ in range(100)]
score = 0
enemy_spawn_timer = 0
game_over = False
font = pygame.font.SysFont(None, 36)

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    current_time = pygame.time.get_ticks()
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                bullet = fighter.shoot(current_time)
                if bullet:
                    bullets.append(bullet)
            if event.key == pygame.K_r and game_over:
                # Reset game
                fighter = Fighter()
                enemies = []
                bullets = []
                particles = []
                score = 0
                game_over = False
    
    if not game_over:
        # Get keyboard state
        keys = pygame.key.get_pressed()
        
        # Update fighter
        fighter.update(keys)
        
        # Auto-shooting
        if keys[pygame.K_SPACE]:
            bullet = fighter.shoot(current_time)
            if bullet:
                bullets.append(bullet)
        
        # Spawn enemies
        enemy_spawn_timer += 1
        if enemy_spawn_timer >= 60:  # Spawn every 60 frames
            enemies.append(Enemy())
            enemy_spawn_timer = 0
        
        # Update enemies
        for enemy in enemies[:]:
            if enemy.update():
                enemies.remove(enemy)
            # Check collision with fighter
            if enemy.rect.colliderect(fighter.rect):
                fighter.health -= 10
                enemies.remove(enemy)
                # Create explosion particles
                for _ in range(20):
                    particles.append(Particle(enemy.rect.centerx, enemy.rect.centery))
                if fighter.health <= 0:
                    game_over = True
        
        # Update bullets
        for bullet in bullets[:]:
            if bullet.update():
                bullets.remove(bullet)
            else:
                # Check collision with enemies
                for enemy in enemies[:]:
                    if bullet.rect.colliderect(enemy.rect):
                        enemy.health -= 5
                        if enemy.health <= 0:
                            enemies.remove(enemy)
                            score += 10
                            # Create explosion particles
                            for _ in range(20):
                                particles.append(Particle(enemy.rect.centerx, enemy.rect.centery))
                        if bullet in bullets:
                            bullets.remove(bullet)
                        break
        
        # Update particles
        for particle in particles[:]:
            if particle.update():
                particles.remove(particle)
    
    # Update stars
    for star in stars:
        star.update()
    
    # Drawing
    screen.fill(BLACK)
    
    # Draw stars
    for star in stars:
        star.draw(screen)
    
    # Draw game objects
    if not game_over:
        fighter.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
    
    # Draw particles
    for particle in particles:
        particle.draw(screen)
    
    # Draw HUD
    health_text = font.render(f"سلامت: {fighter.health}", True, GREEN)
    score_text = font.render(f"امتیاز: {score}", True, YELLOW)
    screen.blit(health_text, (10, 10))
    screen.blit(score_text, (10, 50))
    
    # Draw controls info
    controls_text = font.render("جهت‌ها: حرکت | فاصله: شلیک", True, WHITE)
    screen.blit(controls_text, (WIDTH - controls_text.get_width() - 10, 10))
    
    # Game over screen
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        game_over_text = font.render("بازی تمام شد!", True, RED)
        final_score_text = font.render(f"امتیاز نهایی: {score}", True, YELLOW)
        restart_text = font.render("برای شروع مجدد R را فشار دهید", True, GREEN)
        
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(final_score_text, (WIDTH//2 - final_score_text.get_width()//2, HEIGHT//2))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
