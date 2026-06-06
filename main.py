import pygame
import random
import math
from collections import deque

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700
CELL_SIZE = 30
FPS = 60

# Colors
DARK_BG = (18, 25, 35)
DARKER_BG = (12, 18, 25)
SNAKE_HEAD_GRADIENT_TOP = (46, 204, 113)
SNAKE_HEAD_GRADIENT_BOTTOM = (39, 174, 96)
SNAKE_BODY_TOP = (88, 214, 141)
SNAKE_BODY_BOTTOM = (72, 187, 120)
APPLE_RED = (231, 76, 60)
APPLE_GREEN = (46, 204, 113)
JOYSTICK_BG = (44, 62, 80)
TEXT_WHITE = (236, 240, 241)
TEXT_GOLD = (241, 196, 15)
PARTICLE_COLOR = (241, 196, 15)
DEEPSEEK_BLUE = (0, 150, 255)
DEEPSEEK_PURPLE = (128, 0, 255)


class ParticleEmitter:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, color, count=20, speed_range=(2, 8)):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(speed_range[0], speed_range[1])
            self.particles.append({
                'x': x, 'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.uniform(0.5, 1.0),
                'max_life': 1.0,
                'size': random.randint(3, 6),
                'color': color,
            })

    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2
            particle['life'] -= 0.02
            particle['size'] = max(1, particle['size'] - 0.1)
            if particle['life'] <= 0:
                self.particles.remove(particle)

    def draw(self, screen):
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / particle['max_life']))
            color = tuple(min(255, c * alpha // 255) for c in particle['color'])
            pygame.draw.circle(screen, color, (int(particle['x']), int(particle['y'])), int(particle['size']))


class IntroScreen:
    def __init__(self, screen):
        self.screen = screen
        self.alpha = 0
        self.progress = 0
        self.particles = ParticleEmitter()
        self.logo_scale = 0.1
        self.logo_rotation = 0
        self.state = "fade_in"
        self.loading_dots = 0
        self.start_time = pygame.time.get_ticks()

    def update(self):
        current_time = pygame.time.get_ticks()

        if self.state == "fade_in":
            self.alpha = min(255, self.alpha + 5)
            if self.alpha >= 255:
                self.state = "logo_animation"
                self.start_time = current_time

        elif self.state == "logo_animation":
            elapsed = (current_time - self.start_time) / 1000
            if elapsed < 1.5:
                self.logo_scale = min(1.0, elapsed / 0.8)
                self.logo_rotation = min(360, elapsed * 240)
            else:
                self.state = "loading"
                self.start_time = current_time

        elif self.state == "loading":
            elapsed = (current_time - self.start_time) / 1000
            self.progress = min(1.0, elapsed / 2.0)
            self.loading_dots = int((current_time / 300) % 4)
            if self.progress >= 1.0:
                self.state = "fade_out"
                self.start_time = current_time

        elif self.state == "fade_out":
            elapsed = (current_time - self.start_time) / 1000
            self.alpha = max(0, 255 - int(elapsed * 255))
            if self.alpha <= 0:
                return False

        if random.random() < 0.3:
            self.particles.emit(
                random.randint(0, WINDOW_WIDTH),
                random.randint(0, WINDOW_HEIGHT),
                DEEPSEEK_BLUE,
                count=1,
                speed_range=(1, 4)
            )
        self.particles.update()
        return True

    def draw(self):
        for y in range(WINDOW_HEIGHT):
            color_value = 5 + (y * 20 // WINDOW_HEIGHT)
            color = (color_value, color_value, color_value + 15)
            pygame.draw.line(self.screen, color, (0, y), (WINDOW_WIDTH, y))

        self.particles.draw(self.screen)

        if self.state in ("fade_in", "fade_out"):
            fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(255 - self.alpha)
            self.screen.blit(fade_surface, (0, 0))

        if self.state in ("logo_animation", "loading", "fade_out"):
            center_x = WINDOW_WIDTH // 2
            center_y = WINDOW_HEIGHT // 2 - 50
            for i in range(3):
                glow_scale = self.logo_scale + i * 0.1
                glow_size = int(200 * glow_scale)
                glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*DEEPSEEK_BLUE, 50 - i * 15),
                                   (glow_size // 2, glow_size // 2), glow_size // 2)
                self.screen.blit(glow_surface,
                                 (center_x - glow_size // 2, center_y - glow_size // 2))

            logo_font = pygame.font.Font("font.ttf", int(80 * self.logo_scale))
            logo_text = logo_font.render("DEEPSEEK", True, DEEPSEEK_BLUE)
            rotated_logo = pygame.transform.rotate(logo_text, self.logo_rotation)
            logo_rect = rotated_logo.get_rect(center=(center_x, center_y))
            self.screen.blit(rotated_logo, logo_rect)

            if self.logo_scale > 0.8:
                subtitle_font = pygame.font.Font("font.ttf", int(30 * self.logo_scale))
                subtitle_text = subtitle_font.render("AI-POWERED GAMING", True, TEXT_WHITE)
                subtitle_rect = subtitle_text.get_rect(center=(center_x, center_y + 60))
                self.screen.blit(subtitle_text, subtitle_rect)

        if self.state == "loading":
            bar_width = 400
            bar_height = 6
            bar_x = WINDOW_WIDTH // 2 - bar_width // 2
            bar_y = WINDOW_HEIGHT // 2 + 100
            pygame.draw.rect(self.screen, (40, 40, 50), (bar_x, bar_y, bar_width, bar_height), border_radius=3)
            progress_width = int(bar_width * self.progress)
            for i in range(progress_width):
                color_ratio = i / bar_width
                color = (
                    int(DEEPSEEK_BLUE[0] * (1 - color_ratio) + DEEPSEEK_PURPLE[0] * color_ratio),
                    int(DEEPSEEK_BLUE[1] * (1 - color_ratio) + DEEPSEEK_PURPLE[1] * color_ratio),
                    int(DEEPSEEK_BLUE[2] * (1 - color_ratio) + DEEPSEEK_PURPLE[2] * color_ratio)
                )
                pygame.draw.line(self.screen, color, (bar_x + i, bar_y), (bar_x + i, bar_y + bar_height))

            dot_text = "." * (self.loading_dots % 4)
            loading_font = pygame.font.Font("font.ttf", 24)
            loading_text = loading_font.render(f"LOADING{dot_text}", True, TEXT_WHITE)
            loading_rect = loading_text.get_rect(center=(WINDOW_WIDTH // 2, bar_y + 25))
            self.screen.blit(loading_text, loading_rect)

        pygame.display.flip()


class PremiumButton:
    def __init__(self, x, y, width, height, text, color, hover_color, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.click_animation = 0
        self.icon = icon
        self.hovered = False
        self.ripple_alpha = 0
        self.ripple_radius = 0

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.current_color = self.hover_color if self.hovered else self.color
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            self.click_animation = 1
            self.ripple_alpha = 150
            self.ripple_radius = 0
            return True
        return False

    def update(self):
        if self.click_animation > 0:
            self.click_animation -= 0.1
        if self.ripple_alpha > 0:
            self.ripple_alpha -= 10
            self.ripple_radius += 5

    def draw(self, screen, font):
        shadow_rect = self.rect.inflate(4, 4)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=15)

        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        for i in range(self.rect.height):
            color_ratio = i / self.rect.height
            color = (
                int(self.current_color[0] * (1 - color_ratio) + self.hover_color[0] * color_ratio),
                int(self.current_color[1] * (1 - color_ratio) + self.hover_color[1] * color_ratio),
                int(self.current_color[2] * (1 - color_ratio) + self.hover_color[2] * color_ratio)
            )
            pygame.draw.line(button_surface, color, (0, i), (self.rect.width, i))

        scale = 1 - self.click_animation * 0.05
        scaled_width = int(self.rect.width * scale)
        scaled_height = int(self.rect.height * scale)
        scaled_x = self.rect.x + (self.rect.width - scaled_width) // 2
        scaled_y = self.rect.y + (self.rect.height - scaled_height) // 2

        screen.blit(button_surface, (scaled_x, scaled_y))
        pygame.draw.rect(screen, (255, 255, 255, 100),
                         (scaled_x, scaled_y, scaled_width, scaled_height), 2, border_radius=12)

        if self.ripple_alpha > 0:
            ripple_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.circle(ripple_surface, (255, 255, 255, self.ripple_alpha),
                               (self.rect.width // 2, self.rect.height // 2), self.ripple_radius)
            screen.blit(ripple_surface, (self.rect.x, self.rect.y))

        text_surface = font.render(self.text, True, TEXT_WHITE)
        text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.centery))

        for offset in range(3):
            glow_surface = font.render(self.text, True, (*self.current_color, 50 - offset * 15))
            glow_rect = glow_surface.get_rect(center=(self.rect.centerx + offset, self.rect.centery + offset))
            screen.blit(glow_surface, glow_rect)

        screen.blit(text_surface, text_rect)

        if self.icon:
            icon_font = pygame.font.Font("font.ttf", 32)
            icon_text = icon_font.render(self.icon, True, TEXT_WHITE)
            icon_rect = icon_text.get_rect(midright=(self.rect.x + 20, self.rect.centery))
            screen.blit(icon_text, icon_rect)


class ModernStartMenu:
    def __init__(self, screen):
        self.screen = screen
        self.particles = ParticleEmitter()
        self.float_offset = 0
        self.background_snakes = []
        self.create_background_snakes()

        center_x = WINDOW_WIDTH // 2
        self.start_button = PremiumButton(center_x - 120, 400, 240, 55, "START GAME",
                                          (46, 204, 113), (39, 174, 96), "▶")
        self.quit_button = PremiumButton(center_x - 120, 470, 240, 55, "QUIT",
                                         (231, 76, 60), (192, 57, 43), "✖")

    def create_background_snakes(self):
        for _ in range(3):
            self.background_snakes.append({
                'segments': [(random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT))],
                'direction': random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)]),
                'color': (random.randint(20, 50), random.randint(100, 150), random.randint(20, 50))
            })

    def update(self):
        self.float_offset = (self.float_offset + 0.02) % (2 * math.pi)
        self.start_button.update()
        self.quit_button.update()

        for snake in self.background_snakes:
            head = snake['segments'][0]
            new_x = head[0] + snake['direction'][0] * 2
            new_y = head[1] + snake['direction'][1] * 2

            if new_x < -100 or new_x > WINDOW_WIDTH + 100:
                snake['direction'] = (random.choice([-1, 1]), random.choice([-1, 0, 1]))
            if new_y < -100 or new_y > WINDOW_HEIGHT + 100:
                snake['direction'] = (random.choice([-1, 0, 1]), random.choice([-1, 1]))

            snake['segments'].insert(0, (new_x, new_y))
            if len(snake['segments']) > 20:
                snake['segments'].pop()

        if random.random() < 0.2:
            self.particles.emit(
                random.randint(0, WINDOW_WIDTH),
                random.randint(0, WINDOW_HEIGHT),
                TEXT_GOLD,
                count=2,
                speed_range=(1, 3)
            )

        self.particles.update()

    def draw_background_snakes(self):
        for snake in self.background_snakes:
            for i, segment in enumerate(snake['segments']):
                alpha = int(30 * (1 - i / len(snake['segments'])))
                pygame.draw.circle(self.screen, (*snake['color'], alpha),
                                   (int(segment[0]), int(segment[1])), 15)

    def draw(self):
        for y in range(WINDOW_HEIGHT):
            color_value = 10 + int(math.sin(self.float_offset + y * 0.01) * 5)
            color = (color_value, color_value + 5, color_value + 15)
            pygame.draw.line(self.screen, color, (0, y), (WINDOW_WIDTH, y))

        self.draw_background_snakes()
        self.particles.draw(self.screen)

        title_font = pygame.font.Font("font.ttf", 100)
        title_shadow = title_font.render("SNAKE LEGENDS", True, (0, 0, 0))
        title_text = title_font.render("SNAKE LEGENDS", True, TEXT_GOLD)

        title_offset = math.sin(self.float_offset) * 5
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 150 + title_offset))

        for offset in range(5):
            shadow_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2 + offset, 150 + title_offset + offset))
            self.screen.blit(title_shadow, shadow_rect)

        self.screen.blit(title_text, title_rect)

        subtitle_font = pygame.font.Font("font.ttf", 36)
        subtitle_text = subtitle_font.render("360° MOVEMENT | PREMIUM SNAKE GAME", True, TEXT_WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 210))

        for i in range(3):
            glow_text = subtitle_font.render("360° MOVEMENT | PREMIUM SNAKE GAME", True, (*TEXT_GOLD, 30 - i * 10))
            glow_rect = glow_text.get_rect(center=(WINDOW_WIDTH // 2 + i, 210 + i))
            self.screen.blit(glow_text, glow_rect)

        self.screen.blit(subtitle_text, subtitle_rect)

        features = [
            ("🎮", "360° Joystick", "Full analog control"),
            ("⚡", "Combo System", "Chain eats for bonus"),
            ("🏆", "Leaderboard", "Beat high scores"),
            ("✨", "Visual Effects", "Stunning graphics")
        ]

        card_width = 160
        card_height = 100
        start_x = (WINDOW_WIDTH - (card_width * 4 + 30)) // 2

        for i, (icon, title, desc) in enumerate(features):
            x = start_x + i * (card_width + 10)
            y = 260

            card_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
            for j in range(card_height):
                color_ratio = j / card_height
                color = (25, 30, 45, 200 - int(color_ratio * 50))
                pygame.draw.line(card_surface, color, (0, j), (card_width, j))

            self.screen.blit(card_surface, (x, y))
            pygame.draw.rect(self.screen, (TEXT_GOLD[0], TEXT_GOLD[1], TEXT_GOLD[2], 100),
                             (x, y, card_width, card_height), 2, border_radius=10)

            icon_font = pygame.font.Font("font.ttf", 40)
            icon_text = icon_font.render(icon, True, TEXT_GOLD)
            icon_rect = icon_text.get_rect(center=(x + card_width // 2, y + 30))
            self.screen.blit(icon_text, icon_rect)

            title_font_small = pygame.font.Font("font.ttf", 18)
            title_surface = title_font_small.render(title, True, TEXT_WHITE)
            title_rect = title_surface.get_rect(center=(x + card_width // 2, y + 60))
            self.screen.blit(title_surface, title_rect)

            desc_font = pygame.font.Font("font.ttf", 14)
            desc_surface = desc_font.render(desc, True, (150, 150, 150))
            desc_rect = desc_surface.get_rect(center=(x + card_width // 2, y + 80))
            self.screen.blit(desc_surface, desc_rect)

        self.start_button.draw(self.screen, pygame.font.Font("font.ttf", 28))
        self.quit_button.draw(self.screen, pygame.font.Font("font.ttf", 28))

        footer_font = pygame.font.Font("font.ttf", 16)
        footer_text = footer_font.render("MADE WITH DEEPSEEK AI - PREMIUM GAMING EXPERIENCE", True, (100, 100, 120))
        footer_rect = footer_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        self.screen.blit(footer_text, footer_rect)


class ModernJoystick:
    def __init__(self, x, y, radius=90):
        self.x = x
        self.y = y
        self.radius = radius
        self.knob_radius = 35
        self.active = False
        self.drag_pos = (x, y)
        self.direction = (0, 0)
        self.angle = 0
        self.intensity = 0
        self.pulse = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dist = math.hypot(mouse_x - self.x, mouse_y - self.y)
            if dist <= self.radius:
                self.active = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.active = False
            self.drag_pos = (self.x, self.y)
            self.direction = (0, 0)
            self.intensity = 0
        elif event.type == pygame.MOUSEMOTION and self.active:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - self.x
            dy = mouse_y - self.y
            dist = math.hypot(dx, dy)
            if dist > self.radius:
                dx = dx * self.radius / dist
                dy = dy * self.radius / dist
                dist = self.radius
            self.drag_pos = (self.x + dx, self.y + dy)
            if dist > 15:
                self.direction = (dx / self.radius, dy / self.radius)
                self.intensity = dist / self.radius
                self.angle = math.atan2(dy, dx)
            else:
                self.direction = (0, 0)
                self.intensity = 0

    def get_direction(self):
        if self.active and self.intensity > 0.15:
            return self.direction
        return (0, 0)

    def get_angle(self):
        if self.active and self.intensity > 0.15:
            return self.angle
        return None

    def update(self):
        self.pulse = (self.pulse + 0.1) % (2 * math.pi)

    def draw(self, screen):
        glow_radius = self.radius + 5 + math.sin(self.pulse) * 2
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*JOYSTICK_BG, 50), (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surface, (self.x - glow_radius, self.y - glow_radius))

        pygame.draw.circle(screen, JOYSTICK_BG, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (100, 120, 140), (int(self.x), int(self.y)), self.radius, 3)

        if self.active and self.intensity > 0:
            for i in range(3):
                progress = (self.pulse + i * 2) % (2 * math.pi) / (2 * math.pi)
                end_x = self.x + self.direction[0] * self.radius * (0.5 + progress * 0.5)
                end_y = self.y + self.direction[1] * self.radius * (0.5 + progress * 0.5)
                pygame.draw.line(screen, (*TEXT_GOLD, 150), (self.x, self.y), (end_x, end_y), 4)

        knob_scale = 1 + self.intensity * 0.15
        knob_r = int(self.knob_radius * knob_scale)
        color_intensity = 100 + int(self.intensity * 155)
        knob_color = (color_intensity, color_intensity, 255)

        pygame.draw.circle(screen, (50, 50, 70), (int(self.drag_pos[0] + 3), int(self.drag_pos[1] + 3)), knob_r)
        pygame.draw.circle(screen, knob_color, (int(self.drag_pos[0]), int(self.drag_pos[1])), knob_r)
        pygame.draw.circle(screen, (255, 255, 255, 150),
                           (int(self.drag_pos[0] - 5), int(self.drag_pos[1] - 5)), knob_r // 3)
        pygame.draw.circle(screen, TEXT_WHITE, (int(self.x), int(self.y)), 6)


class SnakeSegment:
    def __init__(self, x, y, angle=0):
        self.x = x
        self.y = y
        self.angle = angle
        self.wave_offset = random.uniform(0, math.pi * 2)


class SmoothSnake:
    def __init__(self):
        start_x = WINDOW_WIDTH // 2
        start_y = WINDOW_HEIGHT // 2
        self.segments = deque()
        for i in range(3):
            self.segments.append(SnakeSegment(start_x - i * CELL_SIZE, start_y))

        self.direction = (1, 0)
        self.target_angle = 0
        self.current_angle = 0
        self.speed = 4
        self.grow_count = 0
        self.trail_positions = deque(maxlen=50)
        self.invincible_timer = 60
        self.immune_timer = 0

    def update(self, joystick_dir=None, joystick_angle=None):
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.immune_timer > 0:
            self.immune_timer -= 1

        if joystick_dir and joystick_dir != (0, 0):
            if joystick_angle is not None:
                self.target_angle = joystick_angle
                angle_diff = self.target_angle - self.current_angle
                while angle_diff > math.pi:
                    angle_diff -= 2 * math.pi
                while angle_diff < -math.pi:
                    angle_diff += 2 * math.pi
                self.current_angle += angle_diff * 0.15
                self.direction = (math.cos(self.current_angle), math.sin(self.current_angle))

        head = self.segments[0]
        new_x = head.x + self.direction[0] * self.speed
        new_y = head.y + self.direction[1] * self.speed

        if new_x < 0:
            new_x = WINDOW_WIDTH
        elif new_x > WINDOW_WIDTH:
            new_x = 0
        if new_y < 0:
            new_y = WINDOW_HEIGHT
        elif new_y > WINDOW_HEIGHT:
            new_y = 0

        self.trail_positions.appendleft((head.x, head.y))
        if len(self.trail_positions) > 20:
            self.trail_positions.pop()

        new_head = SnakeSegment(new_x, new_y, self.current_angle)
        self.segments.appendleft(new_head)

        if self.grow_count > 0:
            self.grow_count -= 1
        else:
            self.segments.pop()

        for i, segment in enumerate(self.segments):
            segment.wave_offset = (segment.wave_offset + 0.1) % (2 * math.pi)
            if i > 0:
                prev = self.segments[i - 1]
                dx = prev.x - segment.x
                dy = prev.y - segment.y
                dist = math.hypot(dx, dy)
                if dist > CELL_SIZE * 1.2:
                    angle = math.atan2(dy, dx)
                    segment.x += math.cos(angle) * (dist - CELL_SIZE) * 0.3
                    segment.y += math.sin(angle) * (dist - CELL_SIZE) * 0.3

        return new_head

    def grow(self):
        self.grow_count += 2
        self.immune_timer = 30

    def check_self_collision(self):
        if self.invincible_timer > 0 or self.immune_timer > 0:
            return False

        if len(self.segments) > 5:
            head = self.segments[0]
            for i, segment in enumerate(self.segments):
                if i > 5:
                    dist = math.hypot(head.x - segment.x, head.y - segment.y)
                    if dist < CELL_SIZE * 0.5:
                        return True
        return False

    def check_apple_collision(self, apple_rect):
        head = self.segments[0]
        head_rect = pygame.Rect(head.x - CELL_SIZE // 2, head.y - CELL_SIZE // 2, CELL_SIZE, CELL_SIZE)
        return head_rect.colliderect(apple_rect)

    def draw(self, screen):
        for i, (x, y) in enumerate(self.trail_positions):
            alpha = int(50 * (1 - i / len(self.trail_positions)))
            pygame.draw.circle(screen, (*SNAKE_BODY_TOP, alpha), (int(x), int(y)), CELL_SIZE // 2)

        for i, segment in enumerate(self.segments):
            x = int(segment.x - CELL_SIZE // 2)
            y = int(segment.y - CELL_SIZE // 2)

            wave_x = x + math.sin(segment.wave_offset + i) * 2
            wave_y = y + math.cos(segment.wave_offset * 0.7 + i) * 2

            if i == 0:
                head_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                for j in range(CELL_SIZE):
                    color = (
                        SNAKE_HEAD_GRADIENT_TOP[0] + (SNAKE_HEAD_GRADIENT_BOTTOM[0] - SNAKE_HEAD_GRADIENT_TOP[0]) * j // CELL_SIZE,
                        SNAKE_HEAD_GRADIENT_TOP[1] + (SNAKE_HEAD_GRADIENT_BOTTOM[1] - SNAKE_HEAD_GRADIENT_TOP[1]) * j // CELL_SIZE,
                        SNAKE_HEAD_GRADIENT_TOP[2] + (SNAKE_HEAD_GRADIENT_BOTTOM[2] - SNAKE_HEAD_GRADIENT_TOP[2]) * j // CELL_SIZE
                    )
                    pygame.draw.line(head_surface, color, (0, j), (CELL_SIZE, j))

                if (self.invincible_timer > 0 or self.immune_timer > 0) and (pygame.time.get_ticks() // 100) % 2 == 0:
                    flash_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    flash_surface.fill((255, 255, 255, 100))
                    head_surface.blit(flash_surface, (0, 0))

                angle_deg = math.degrees(self.current_angle)
                rotated_head = pygame.transform.rotate(head_surface, -angle_deg)
                head_rect = rotated_head.get_rect(center=(segment.x, segment.y))
                screen.blit(rotated_head, head_rect)

                eye_offset = CELL_SIZE // 3
                eye_size = CELL_SIZE // 6
                eye_angle = self.current_angle
                left_eye_x = segment.x + math.cos(eye_angle + 0.8) * eye_offset
                left_eye_y = segment.y + math.sin(eye_angle + 0.8) * eye_offset
                right_eye_x = segment.x + math.cos(eye_angle - 0.8) * eye_offset
                right_eye_y = segment.y + math.sin(eye_angle - 0.8) * eye_offset

                pygame.draw.circle(screen, TEXT_WHITE, (int(left_eye_x), int(left_eye_y)), eye_size)
                pygame.draw.circle(screen, TEXT_WHITE, (int(right_eye_x), int(right_eye_y)), eye_size)
                pygame.draw.circle(screen, (0, 0, 0),
                                   (int(left_eye_x + math.cos(eye_angle) * 2), int(left_eye_y + math.sin(eye_angle) * 2)),
                                   eye_size // 2)
                pygame.draw.circle(screen, (0, 0, 0),
                                   (int(right_eye_x + math.cos(eye_angle) * 2), int(right_eye_y + math.sin(eye_angle) * 2)),
                                   eye_size // 2)
            else:
                body_color = SNAKE_BODY_TOP if i % 2 == 0 else SNAKE_BODY_BOTTOM
                pygame.draw.rect(screen, body_color, (wave_x, wave_y, CELL_SIZE - 2, CELL_SIZE - 2), border_radius=8)

                scale_color = (40, 180, 100)
                for s in range(2):
                    scale_x = wave_x + CELL_SIZE // 3 + s * CELL_SIZE // 3
                    scale_y = wave_y + CELL_SIZE // 2
                    pygame.draw.circle(screen, scale_color, (int(scale_x), int(scale_y)), 2)


class AnimatedApple:
    def __init__(self):
        self.x = random.randint(CELL_SIZE, WINDOW_WIDTH - CELL_SIZE)
        self.y = random.randint(CELL_SIZE, WINDOW_HEIGHT - CELL_SIZE)
        self.float_offset = 0
        self.rotation = 0
        self.pulse_scale = 0

    def randomize_position(self, snake_segments=None):
        self.x = random.randint(CELL_SIZE, WINDOW_WIDTH - CELL_SIZE)
        self.y = random.randint(CELL_SIZE, WINDOW_HEIGHT - CELL_SIZE)
        if snake_segments:
            for segment in snake_segments:
                dist = math.hypot(self.x - segment.x, self.y - segment.y)
                if dist < CELL_SIZE:
                    self.randomize_position(snake_segments)
                    return

    def update(self):
        self.float_offset = (self.float_offset + 0.05) % (2 * math.pi)
        self.rotation = (self.rotation + 0.05) % (2 * math.pi)
        self.pulse_scale = 1 + math.sin(self.float_offset * 2) * 0.1

    def get_rect(self):
        size = int(CELL_SIZE * 0.7 * self.pulse_scale)
        x = self.x - size // 2
        y = self.y - size // 2 + math.sin(self.float_offset) * 3
        return pygame.Rect(x, y, size, size)

    def draw(self, screen):
        size = int(CELL_SIZE * 0.7 * self.pulse_scale)
        x = self.x - size // 2
        y = self.y - size // 2 + math.sin(self.float_offset) * 3

        glow_size = size + 10
        glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*APPLE_RED, 50), (glow_size, glow_size), glow_size)
        screen.blit(glow_surface, (x - glow_size + size // 2, y - glow_size + size // 2))

        for i in range(size):
            color = (
                APPLE_RED[0] - i * 30 // size,
                APPLE_RED[1] - i * 20 // size,
                APPLE_RED[2] - i * 20 // size
            )
            pygame.draw.line(screen, color, (x + i, y), (x + i, y + size))

        highlight_rect = pygame.Rect(x + 3, y + 3, size // 3, size // 4)
        pygame.draw.rect(screen, (255, 200, 200), highlight_rect, border_radius=4)

        leaf_angle = self.rotation
        leaf_x = x + size - 5
        leaf_y = y - 3
        leaf_points = [
            (leaf_x, leaf_y),
            (leaf_x + math.cos(leaf_angle) * 8, leaf_y + math.sin(leaf_angle) * 8 - 5),
            (leaf_x + math.cos(leaf_angle + 1) * 5, leaf_y + math.sin(leaf_angle + 1) * 5 - 3)
        ]
        pygame.draw.polygon(screen, APPLE_GREEN, leaf_points)
        pygame.draw.line(screen, (101, 67, 33), (leaf_x, leaf_y), (leaf_x - 3, leaf_y - 5), 2)


class GameUI:
    def __init__(self):
        self.font_large = pygame.font.Font("font.ttf", 80)
        self.font_medium = pygame.font.Font("font.ttf", 48)
        self.font_small = pygame.font.Font("font.ttf", 32)
        self.font_tiny = pygame.font.Font("font.ttf", 24)
        self.score_animation = 0
        self.combo = 0
        self.combo_timer = 0

    def update(self):
        if self.score_animation > 0:
            self.score_animation -= 0.1
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0

    def add_score(self, points=1):
        self.score_animation = 1
        self.combo += 1
        self.combo_timer = 60

    def draw_score(self, screen, score, high_score):
        score_bg = pygame.Rect(10, 10, 150, 60)
        pygame.draw.rect(screen, (0, 0, 0, 100), score_bg, border_radius=10)

        score_text = self.font_large.render(str(score), True, TEXT_GOLD)
        score_rect = score_text.get_rect(topleft=(20, 10))
        screen.blit(score_text, score_rect)

        label = self.font_tiny.render("SCORE", True, TEXT_WHITE)
        screen.blit(label, (25, 65))

        high_text = self.font_small.render(f"BEST: {high_score}", True, TEXT_WHITE)
        high_rect = high_text.get_rect(topright=(WINDOW_WIDTH - 20, 20))
        screen.blit(high_text, high_rect)

        if self.combo > 1 and self.combo_timer > 0:
            combo_text = self.font_medium.render(f"x{self.combo} COMBO!", True, TEXT_GOLD)
            combo_rect = combo_text.get_rect(center=(WINDOW_WIDTH // 2, 50))
            screen.blit(combo_text, combo_rect)


class ModernSnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("SNAKE LEGENDS - Premium Snake Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "intro"

        self.intro_screen = IntroScreen(self.screen)
        self.menu_screen = ModernStartMenu(self.screen)

        self.snake = None
        self.apple = None
        self.joystick = None
        self.particle_system = None
        self.ui = None
        self.score = 0
        self.high_score = 0
        self.paused = False

    def init_game(self):
        self.snake = SmoothSnake()
        self.apple = AnimatedApple()
        self.joystick = ModernJoystick(WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100, 90)
        self.particle_system = ParticleEmitter()
        self.ui = GameUI()
        self.score = 0
        self.paused = False
        self.apple.randomize_position(self.snake.segments)

    def add_particle_effect(self, x, y):
        self.particle_system.emit(x, y, PARTICLE_COLOR, 30)

    def update_game(self):
        if self.paused:
            return

        joystick_dir = self.joystick.get_direction()
        joystick_angle = self.joystick.get_angle()

        self.snake.update(joystick_dir, joystick_angle)
        self.apple.update()
        self.particle_system.update()
        self.ui.update()
        self.joystick.update()

        apple_rect = self.apple.get_rect()
        if self.snake.check_apple_collision(apple_rect):
            self.score += 1
            self.ui.add_score()
            self.add_particle_effect(self.apple.x, self.apple.y)
            self.snake.grow()
            self.apple.randomize_position(self.snake.segments)

            flash = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            flash.fill((255, 255, 255))
            flash.set_alpha(100)
            self.screen.blit(flash, (0, 0))
            pygame.display.flip()

            if self.score > self.high_score:
                self.high_score = self.score

        if self.snake.check_self_collision():
            self.game_state = "menu"
            self.menu_screen = ModernStartMenu(self.screen)

    def draw_game(self):
        for y in range(WINDOW_HEIGHT):
            color_value = 12 + (y * 25 // WINDOW_HEIGHT)
            color = (color_value, color_value + 3, color_value + 10)
            pygame.draw.line(self.screen, color, (0, y), (WINDOW_WIDTH, y))

        self.snake.draw(self.screen)
        self.apple.draw(self.screen)
        self.particle_system.draw(self.screen)
        self.joystick.draw(self.screen)
        self.ui.draw_score(self.screen, self.score, self.high_score)

        if self.paused:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(DARK_BG)
            self.screen.blit(overlay, (0, 0))
            pause_font = pygame.font.Font("font.ttf", 80)
            pause_text = pause_font.render("PAUSED", True, TEXT_GOLD)
            pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(pause_text, pause_rect)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if self.game_state == "intro":
                    if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                        self.game_state = "menu"
                        self.menu_screen = ModernStartMenu(self.screen)

                elif self.game_state == "menu":
                    if self.menu_screen.start_button.handle_event(event):
                        self.init_game()
                        self.game_state = "playing"
                    if self.menu_screen.quit_button.handle_event(event):
                        self.running = False

                elif self.game_state == "playing":
                    self.joystick.handle_event(event)
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.paused = not self.paused

            if self.game_state == "intro":
                if not self.intro_screen.update():
                    self.game_state = "menu"
                    self.menu_screen = ModernStartMenu(self.screen)
                self.intro_screen.draw()

            elif self.game_state == "menu":
                self.menu_screen.update()
                self.menu_screen.draw()

            elif self.game_state == "playing":
                self.update_game()
                self.draw_game()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    game = ModernSnakeGame()
    game.run()