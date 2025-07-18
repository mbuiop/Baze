import pygame
import sys
import math
import random
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# تنظیمات اولیه
WIDTH, HEIGHT = 1200, 800
FPS = 60
BACKGROUND_COLOR = (0.05, 0.05, 0.1, 1.0)

# تنظیمات بازی
PLAYER_SPEED = 8
BULLET_SPEED = 15
ENEMY_SPAWN_RATE = 60  # فریم‌ها
MAX_ENEMIES = 20
WAVE_SIZE = 10

# رنگ‌ها
PLAYER_COLOR = (0.2, 0.6, 1.0, 1.0)
BULLET_COLOR = (1.0, 0.8, 0.2, 1.0)
ENEMY_COLORS = [
    (0.8, 0.2, 0.2, 1.0),
    (0.2, 0.8, 0.2, 1.0),
    (0.2, 0.2, 0.8, 1.0),
    (0.8, 0.8, 0.2, 1.0),
    (0.8, 0.2, 0.8, 1.0)
]
UI_COLOR = (0.1, 0.1, 0.2, 0.8)
TEXT_COLOR = (1.0, 1.0, 1.0, 1.0)
BUTTON_COLOR = (0.3, 0.3, 0.6, 1.0)
BUTTON_HOVER_COLOR = (0.4, 0.4, 0.8, 1.0)

class Player:
    def __init__(self):
        self.x = 0
        self.y = -5
        self.z = -20
        self.size = 2
        self.speed = PLAYER_SPEED
        self.rotation = 0
        self.health = 100
        self.score = 0
        self.lives = 3
        self.invincible = 0
        self.color = PLAYER_COLOR
        self.last_shot = 0
        self.shoot_delay = 10

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotation, 0, 1, 0)
        glColor4f(*self.color)
        
        # بدنه کشتی
        glBegin(GL_TRIANGLES)
        # نوک
        glVertex3f(0, self.size/2, 0)
        glVertex3f(-self.size/2, -self.size/2, 0)
        glVertex3f(self.size/2, -self.size/2, 0)
        
        # بال‌ها
        glVertex3f(-self.size, -self.size/2, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, -self.size/2, 0)
        
        glVertex3f(self.size, -self.size/2, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, -self.size/2, 0)
        glEnd()
        
        # موتورها
        glColor4f(1.0, 0.5, 0.0, 1.0)
        glBegin(GL_QUADS)
        glVertex3f(-self.size/3, -self.size/2, -0.5)
        glVertex3f(-self.size/3, -self.size/2 - 0.5, -0.5)
        glVertex3f(self.size/3, -self.size/2 - 0.5, -0.5)
        glVertex3f(self.size/3, -self.size/2, -0.5)
        glEnd()
        
        glPopMatrix()

    def move(self, dx, dz):
        self.x += dx * self.speed
        self.z += dz * self.speed
        
        # محدودیت حرکتی
        self.x = max(-20, min(20, self.x))
        self.z = max(-30, min(-10, self.z))

    def shoot(self, bullets):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_delay:
            self.last_shot = current_time
            bullets.append(Bullet(self.x, self.y, self.z, self.rotation))
            return True
        return False

class Bullet:
    def __init__(self, x, y, z, rotation):
        self.x = x
        self.y = y
        self.z = z
        self.speed = BULLET_SPEED
        self.rotation = rotation
        self.size = 0.3
        self.color = BULLET_COLOR
        self.distance = 0

    def update(self):
        rad = math.radians(self.rotation)
        self.x += math.sin(rad) * self.speed
        self.z += math.cos(rad) * self.speed
        self.distance += self.speed
        
        # برگرداندن True اگر گلوله از محدوده خارج شود
        return (abs(self.x) > 50 or abs(self.z) > 50 or self.distance > 100)

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glColor4f(*self.color)
        
        # گلوله
        glBegin(GL_TRIANGLE_FAN)
        for i in range(360):
            angle = math.radians(i)
            glVertex3f(
                math.cos(angle) * self.size,
                math.sin(angle) * self.size,
                0
            )
        glEnd()
        
        glPopMatrix()

class Enemy:
    def __init__(self, level):
        self.size = random.uniform(1.0, 3.0)
        self.speed = random.uniform(1.0, 3.0) + level * 0.2
        self.rotation = random.uniform(0, 360)
        self.health = int(self.size * 2)
        self.max_health = self.health
        self.color = random.choice(ENEMY_COLORS)
        self.value = int(self.size * 10)
        
        # موقعیت اولیه
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(20, 40)
        self.x = math.sin(angle) * distance
        self.y = random.uniform(-5, 5)
        self.z = math.cos(angle) * distance
        
        # هدفگیری به سمت بازیکن
        dx = -self.x
        dz = -self.z
        self.rotation = math.degrees(math.atan2(dx, dz))

    def update(self, player):
        # حرکت به سمت بازیکن
        rad = math.radians(self.rotation)
        self.x += math.sin(rad) * self.speed
        self.z += math.cos(rad) * self.speed
        
        # برگرداندن True اگر دشمن به بازیکن برخورد کند
        distance = math.sqrt((self.x - player.x)**2 + (self.z - player.z)**2)
        return distance < (self.size + player.size)

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotation, 0, 1, 0)
        glColor4f(*self.color)
        
        # بدنه دشمن
        glBegin(GL_QUADS)
        # جلو
        glVertex3f(-self.size, -self.size, -self.size)
        glVertex3f(self.size, -self.size, -self.size)
        glVertex3f(self.size, self.size, -self.size)
        glVertex3f(-self.size, self.size, -self.size)
        
        # عقب
        glVertex3f(-self.size, -self.size, self.size)
        glVertex3f(self.size, -self.size, self.size)
        glVertex3f(self.size, self.size, self.size)
        glVertex3f(-self.size, self.size, self.size)
        
        # چپ
        glVertex3f(-self.size, -self.size, -self.size)
        glVertex3f(-self.size, -self.size, self.size)
        glVertex3f(-self.size, self.size, self.size)
        glVertex3f(-self.size, self.size, -self.size)
        
        # راست
        glVertex3f(self.size, -self.size, -self.size)
        glVertex3f(self.size, -self.size, self.size)
        glVertex3f(self.size, self.size, self.size)
        glVertex3f(self.size, self.size, -self.size)
        
        # بالا
        glVertex3f(-self.size, self.size, -self.size)
        glVertex3f(self.size, self.size, -self.size)
        glVertex3f(self.size, self.size, self.size)
        glVertex3f(-self.size, self.size, self.size)
        
        # پایین
        glVertex3f(-self.size, -self.size, -self.size)
        glVertex3f(self.size, -self.size, -self.size)
        glVertex3f(self.size, -self.size, self.size)
        glVertex3f(-self.size, -self.size, self.size)
        glEnd()
        
        glPopMatrix()

class Particle:
    def __init__(self, x, y, z, color):
        self.x = x
        self.y = y
        self.z = z
        self.color = color
        self.size = random.uniform(0.1, 0.5)
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-2, 2)
        self.speed_z = random.uniform(-2, 2)
        self.life = random.randint(20, 40)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.z += self.speed_z
        self.life -= 1
        self.size = max(0, self.size - 0.02)
        return self.life <= 0

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glColor4f(*self.color, self.life/40)
        
        glBegin(GL_QUADS)
        glVertex3f(-self.size, -self.size, 0)
        glVertex3f(self.size, -self.size, 0)
        glVertex3f(self.size, self.size, 0)
        glVertex3f(-self.size, self.size, 0)
        glEnd()
        
        glPopMatrix()

class Star:
    def __init__(self):
        self.x = random.uniform(-50, 50)
        self.y = random.uniform(-50, 50)
        self.z = random.uniform(-100, 100)
        self.size = random.uniform(0.01, 0.05)
        self.speed = random.uniform(0.1, 0.5)
        self.color = (
            random.uniform(0.5, 1.0),
            random.uniform(0.5, 1.0),
            random.uniform(0.5, 1.0),
            1.0
        )

    def update(self):
        self.z += self.speed
        if self.z > 100:
            self.z = -100
            self.x = random.uniform(-50, 50)
            self.y = random.uniform(-50, 50)

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glColor4f(*self.color)
        
        glBegin(GL_QUADS)
        glVertex3f(-self.size, -self.size, 0)
        glVertex3f(self.size, -self.size, 0)
        glVertex3f(self.size, self.size, 0)
        glVertex3f(-self.size, self.size, 0)
        glEnd()
        
        glPopMatrix()

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.hovered = False

    def draw(self, surface, font):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=10)
        
        text_surf = font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered

    def is_clicked(self, pos, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

def init_gl():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # نورپردازی
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (WIDTH/HEIGHT), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def draw_text(surface, text, position, font, color=TEXT_COLOR):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)

def game_intro(screen, clock, font_large, font_medium):
    title_text = font_large.render("SPACE SHOOTER 3D", True, (100, 200, 255))
    subtitle_text = font_medium.render("یک بازی سه بعدی با گرافیک خفن", True, (200, 200, 100))
    
    start_button = Button(WIDTH//2 - 100, HEIGHT//2, 200, 50, "شروع بازی")
    quit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 80, 200, 50, "خروج")
    
    stars = [Star() for _ in range(200)]
    
    intro = True
    while intro:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            if start_button.is_clicked(mouse_pos, event):
                return True
            if quit_button.is_clicked(mouse_pos, event):
                return False
        
        # به‌روزرسانی ستاره‌ها
        for star in stars:
            star.update()
        
        # رندر سه بعدی
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(0, 0, 5, 0, 0, 0, 0, 1, 0)
        
        # رسم ستاره‌ها
        for star in stars:
            star.draw()
        
        # رندر UI
        pygame.display.flip()
        screen.fill((0, 0, 0, 0))
        
        # رسم متن
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//4))
        screen.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, HEIGHT//4 + 80))
        
        # بررسی وضعیت دکمه‌ها
        start_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)
        
        # رسم دکمه‌ها
        start_button.draw(screen, font_medium)
        quit_button.draw(screen, font_medium)
        
        pygame.display.flip()
        clock.tick(FPS)

def game_loop(screen, clock, font, font_large):
    # تنظیمات اولیه OpenGL
    init_gl()
    
    # ایجاد بازیگران
    player = Player()
    bullets = []
    enemies = []
    particles = []
    stars = [Star() for _ in range(200)]
    
    # متغیرهای بازی
    wave = 1
    enemy_spawn_timer = 0
    game_over = False
    level_complete = False
    level_start_time = pygame.time.get_ticks()
    
    # حلقه اصلی بازی
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        # مدیریت رویدادها
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            
            if game_over and event.type == KEYDOWN:
                if event.key == K_r:
                    return True  # بازی مجدد
                if event.key == K_q:
                    return False  # خروج
            
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
        
        # دریافت وضعیت کیبورد
        keys = pygame.key.get_pressed()
        dx, dz = 0, 0
        if keys[K_LEFT] or keys[K_a]:
            dx = -1
        if keys[K_RIGHT] or keys[K_d]:
            dx = 1
        if keys[K_UP] or keys[K_w]:
            dz = -1
        if keys[K_DOWN] or keys[K_s]:
            dz = 1
        if keys[K_SPACE]:
            player.shoot(bullets)
        
        player.move(dx, dz)
        
        # به‌روزرسانی موقعیت دوربین بر اساس موقعیت بازیکن
        glLoadIdentity()
        camera_x = player.x
        camera_y = player.y + 5
        camera_z = player.z + 10
        gluLookAt(camera_x, camera_y, camera_z, 
                 player.x, player.y, player.z - 10, 
                 0, 1, 0)
        
        # به‌روزرسانی گلوله‌ها
        for bullet in bullets[:]:
            if bullet.update():
                bullets.remove(bullet)
        
        # تولید دشمنان جدید
        if not game_over and not level_complete:
            enemy_spawn_timer += 1
            if enemy_spawn_timer >= ENEMY_SPAWN_RATE and len(enemies) < MAX_ENEMIES:
                enemy_spawn_timer = 0
                enemies.append(Enemy(wave))
        
        # به‌روزرسانی دشمنان
        for enemy in enemies[:]:
            if enemy.update(player):
                enemies.remove(enemy)
                player.health -= 10
                if player.health <= 0:
                    player.lives -= 1
                    player.health = 100
                    player.invincible = 120  # 2 ثانیه مصونیت
                    
                    if player.lives <= 0:
                        game_over = True
        
        # بررسی برخورد گلوله‌ها با دشمنان
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                dx = bullet.x - enemy.x
                dy = bullet.y - enemy.y
                dz = bullet.z - enemy.z
                distance = math.sqrt(dx*dx + dy*dy + dz*dz)
                
                if distance < (bullet.size + enemy.size):
                    enemy.health -= 10
                    
                    # ایجاد ذرات انفجار
                    for _ in range(20):
                        particles.append(Particle(
                            enemy.x, enemy.y, enemy.z,
                            enemy.color
                        ))
                    
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        player.score += enemy.value
                    
                    if bullet in bullets:
                        bullets.remove(bullet)
                    break
        
        # به‌روزرسانی ذرات
        for particle in particles[:]:
            if particle.update():
                particles.remove(particle)
        
        # به‌روزرسانی ستاره‌ها
        for star in stars:
            star.update()
        
        # بررسی پایان سطح
        if not enemies and len(enemies) == 0 and enemy_spawn_timer > ENEMY_SPAWN_RATE * 3:
            level_complete = True
            wave += 1
            player.score += 1000 * wave
            level_start_time = current_time
        
        # به‌روزرسانی مصونیت
        if player.invincible > 0:
            player.invincible -= 1
            player.color = (1.0, 0.5, 0.5, 1.0) if player.invincible % 10 < 5 else PLAYER_COLOR
        else:
            player.color = PLAYER_COLOR
        
        # پاک کردن صفحه
        glClearColor(*BACKGROUND_COLOR)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # رسم ستاره‌ها
        for star in stars:
            star.draw()
        
        # رسم بازیگران
        player.draw()
        for bullet in bullets:
            bullet.draw()
        for enemy in enemies:
            enemy.draw()
        for particle in particles:
            particle.draw()
        
        # رندر UI
        screen.fill((0, 0, 0, 0))
        
        # نوار وضعیت
        pygame.draw.rect(screen, UI_COLOR, (10, 10, 300, 80), border_radius=10)
        pygame.draw.rect(screen, (255, 50, 50, 200), (30, 40, player.health * 2.4, 20), border_radius=5)
        pygame.draw.rect(screen, (200, 200, 200), (30, 40, 240, 20), 2, border_radius=5)
        
        draw_text(screen, f"امتیاز: {player.score}", (20, 15), font)
        draw_text(screen, f"سطح: {wave}", (WIDTH - 120, 15), font)
        draw_text(screen, f"جان: {player.lives}", (WIDTH - 300, 15), font)
        
        # نمایش وضعیت بازی
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            
            game_over_text = font_large.render("GAME OVER", True, (255, 50, 50))
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
            
            score_text = font.render(f"امتیاز نهایی: {player.score}", True, TEXT_COLOR)
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + 20))
            
            restart_text = font.render("R - بازی مجدد   Q - خروج", True, TEXT_COLOR)
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 80))
        
        elif level_complete:
            if current_time - level_start_time < 3000:  # نمایش به مدت 3 ثانیه
                level_text = font_large.render(f"سطح {wave} تکمیل شد!", True, (50, 255, 100))
                screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//2 - 25))
            else:
                level_complete = False
                enemy_spawn_timer = 0
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return False

def main():
    # مقداردهی اولیه PyGame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("بازی سه بعدی تیراندازی - Space Shooter 3D")
    
    # تنظیم آیکون
    icon_surface = pygame.Surface((32, 32))
    pygame.draw.circle(icon_surface, (100, 200, 255), (16, 16), 16)
    pygame.draw.polygon(icon_surface, (200, 200, 100), [(16, 5), (10, 27), (22, 27)])
    pygame.display.set_icon(icon_surface)
    
    clock = pygame.time.Clock()
    
    # بارگذاری فونت‌ها
    font = pygame.font.SysFont("Arial", 24)
    font_large = pygame.font.SysFont("Arial", 48)
    font_medium = pygame.font.SysFont("Arial", 36)
    
    # نمایش صفحه آغازین
    if game_intro(screen, clock, font_large, font_medium):
        # شروع حلقه بازی
        restart = True
        while restart:
            restart = game_loop(screen, clock, font, font_large)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()


