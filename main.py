import random
import math
from collections import deque
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line, Rectangle, Translate, Rotate, PushMatrix, PopMatrix
from kivy.core.text import Label as CoreLabel
from kivy.utils import get_color_from_hex

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700
CELL_SIZE = 30
FPS = 60

# Colors (RGB tuples)
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

def rgba(rgb, alpha=255):
    return (rgb[0]/255., rgb[1]/255., rgb[2]/255., alpha/255.)

class ParticleEmitter:
    def __init__(self, widget):
        self.widget = widget
        self.particles = []

    def emit(self, x, y, color, count=20, speed_range=(2,8)):
        for _ in range(count):
            angle = random.uniform(0, math.pi*2)
            speed = random.uniform(speed_range[0], speed_range[1])
            self.particles.append({
                'x':x, 'y':y,
                'vx': math.cos(angle)*speed,
                'vy': math.sin(angle)*speed,
                'life': random.uniform(0.5,1.0),
                'max_life': 1.0,
                'size': random.randint(3,6),
                'color': color,
            })

    def update(self):
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.2
            p['life'] -= 0.02
            p['size'] = max(1, p['size']-0.1)
            if p['life'] <= 0:
                self.particles.remove(p)

    def draw(self):
        with self.widget.canvas:
            for p in self.particles:
                alpha = int(255 * (p['life']/p['max_life']))
                col = tuple(int(c * alpha // 255) for c in p['color'])
                Color(*rgba(col, alpha))
                Ellipse(pos=(p['x']-p['size']/2, p['y']-p['size']/2), size=(p['size'], p['size']))

class IntroScreen(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.alpha = 0
        self.progress = 0
        self.particles = ParticleEmitter(self)
        self.logo_scale = 0.1
        self.logo_rotation = 0
        self.state = "fade_in"
        self.loading_dots = 0
        self.start_time = 0
        self.clock = None

    def start(self):
        self.start_time = Clock.get_time()
        self.clock = Clock.schedule_interval(self.update, 1/30)

    def update(self, dt):
        current_time = Clock.get_time()
        if self.state == "fade_in":
            self.alpha = min(1.0, self.alpha + 0.02)
            if self.alpha >= 1.0:
                self.state = "logo_animation"
                self.start_time = current_time
        elif self.state == "logo_animation":
            elapsed = current_time - self.start_time
            if elapsed < 1.5:
                self.logo_scale = min(1.0, elapsed / 0.8)
                self.logo_rotation = min(360, elapsed * 240)
            else:
                self.state = "loading"
                self.start_time = current_time
        elif self.state == "loading":
            elapsed = current_time - self.start_time
            self.progress = min(1.0, elapsed / 2.0)
            self.loading_dots = int((Clock.get_time()*1000/300) % 4)
            if self.progress >= 1.0:
                self.state = "fade_out"
                self.start_time = current_time
        elif self.state == "fade_out":
            elapsed = current_time - self.start_time
            self.alpha = max(0.0, 1.0 - elapsed)
            if self.alpha <= 0:
                self.clock.cancel()
                App.get_running_app().root.show_menu()
                return
        if random.random() < 0.3:
            self.particles.emit(random.randint(0,WINDOW_WIDTH), random.randint(0,WINDOW_HEIGHT), DEEPSEEK_BLUE, count=1, speed_range=(1,4))
        self.particles.update()
        self.draw()

    def draw(self):
        self.canvas.clear()
        for y in range(0, WINDOW_HEIGHT, 2):
            color_value = 5 + (y*20//WINDOW_HEIGHT)
            col = (color_value/255., color_value/255., (color_value+15)/255.)
            with self.canvas:
                Color(*col)
                Line(points=[0,y,WINDOW_WIDTH,y], width=2)
        self.particles.draw()
        if self.state in ("fade_in","fade_out"):
            with self.canvas:
                Color(0,0,0, 1-self.alpha)
                Rectangle(pos=(0,0), size=(WINDOW_WIDTH,WINDOW_HEIGHT))
        if self.state in ("logo_animation","loading","fade_out"):
            center_x = WINDOW_WIDTH//2
            center_y = WINDOW_HEIGHT//2 - 50
            for i in range(3):
                glow_scale = self.logo_scale + i*0.1
                glow_size = int(200*glow_scale)
                with self.canvas:
                    Color(*rgba(DEEPSEEK_BLUE, 50 - i*15))
                    Ellipse(pos=(center_x-glow_size/2, center_y-glow_size/2), size=(glow_size,glow_size))
            label = CoreLabel(text="DEEPSEEK", font_size=int(80*self.logo_scale), font_name='Roboto', color=DEEPSEEK_BLUE)
            texture = label.texture
            with self.canvas:
                PushMatrix()
                Translate(center_x, center_y)
                Rotate(self.logo_rotation)
                Rectangle(texture=texture, pos=(-texture.width/2, -texture.height/2), size=texture.size)
                PopMatrix()
            if self.logo_scale > 0.8:
                label2 = CoreLabel(text="AI-POWERED GAMING", font_size=int(30*self.logo_scale), font_name='Roboto', color=TEXT_WHITE)
                tex2 = label2.texture
                with self.canvas:
                    Rectangle(texture=tex2, pos=(center_x-tex2.width/2, center_y+60-tex2.height/2), size=tex2.size)
        if self.state == "loading":
            bar_width = 400
            bar_height = 6
            bar_x = WINDOW_WIDTH//2 - bar_width//2
            bar_y = WINDOW_HEIGHT//2 + 100
            with self.canvas:
                Color(0.16,0.16,0.2)
                Rectangle(pos=(bar_x, bar_y), size=(bar_width, bar_height))
                progress_width = int(bar_width * self.progress)
                for i in range(progress_width):
                    ratio = i/bar_width
                    r = int(DEEPSEEK_BLUE[0]*(1-ratio)+DEEPSEEK_PURPLE[0]*ratio)/255.
                    g = int(DEEPSEEK_BLUE[1]*(1-ratio)+DEEPSEEK_PURPLE[1]*ratio)/255.
                    b = int(DEEPSEEK_BLUE[2]*(1-ratio)+DEEPSEEK_PURPLE[2]*ratio)/255.
                    Color(r,g,b)
                    Line(points=[bar_x+i, bar_y, bar_x+i, bar_y+bar_height], width=1)
            dots = "." * (self.loading_dots % 4)
            label3 = CoreLabel(text=f"LOADING{dots}", font_size=24, font_name='Roboto', color=TEXT_WHITE)
            tex3 = label3.texture
            with self.canvas:
                Rectangle(texture=tex3, pos=(WINDOW_WIDTH//2 - tex3.width/2, bar_y+25), size=tex3.size)

class PremiumButton(Widget):
    def __init__(self, text, color, hover_color, icon=None, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.icon = icon
        self.current_color = color
        self.click_animation = 0
        self.ripple_alpha = 0
        self.ripple_radius = 0
        self.hovered = False
        self.register_event_type('on_press')
        self.size_hint = (None, None)
        self.size = (240, 55)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.click_animation = 1
            self.ripple_alpha = 150
            self.ripple_radius = 0
            self.dispatch('on_press')
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        self.hovered = self.collide_point(*touch.pos)
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        self.hovered = False
        return super().on_touch_up(touch)

    def on_press(self):
        pass

    def update(self, dt):
        if self.click_animation > 0:
            self.click_animation -= 0.1
        if self.ripple_alpha > 0:
            self.ripple_alpha -= 10
            self.ripple_radius += 5
        self.current_color = self.hover_color if self.hovered else self.color
        self.draw()

    def draw(self):
        self.canvas.clear()
        w, h = self.size
        # shadow
        with self.canvas:
            Color(0,0,0,0.4)
            Rectangle(pos=(self.x+4, self.y+4), size=(w,h))
        # gradient button
        for i in range(int(h)):
            ratio = i/h
            r = int(self.current_color[0]*(1-ratio) + self.hover_color[0]*ratio)/255.
            g = int(self.current_color[1]*(1-ratio) + self.hover_color[1]*ratio)/255.
            b = int(self.current_color[2]*(1-ratio) + self.hover_color[2]*ratio)/255.
            with self.canvas:
                Color(r,g,b)
                Line(points=[self.x, self.y+i, self.x+w, self.y+i], width=1)
        # border
        with self.canvas:
            Color(1,1,1,0.4)
            Rectangle(pos=(self.x, self.y), size=(w,h))
        # ripple
        if self.ripple_alpha > 0:
            with self.canvas:
                Color(1,1,1, self.ripple_alpha/255.)
                Ellipse(pos=(self.x+w/2-self.ripple_radius, self.y+h/2-self.ripple_radius), size=(self.ripple_radius*2, self.ripple_radius*2))
        # text
        label = CoreLabel(text=self.text, font_size=28, font_name='Roboto', color=TEXT_WHITE)
        tex = label.texture
        with self.canvas:
            Rectangle(texture=tex, pos=(self.x+w/2 - tex.width/2, self.y+h/2 - tex.height/2), size=tex.size)
        if self.icon:
            icon_label = CoreLabel(text=self.icon, font_size=32, font_name='Roboto', color=TEXT_WHITE)
            icon_tex = icon_label.texture
            with self.canvas:
                Rectangle(texture=icon_tex, pos=(self.x+20, self.y+h/2-icon_tex.height/2), size=icon_tex.size)

class ModernStartMenu(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.particles = ParticleEmitter(self)
        self.float_offset = 0
        self.background_snakes = []
        self.create_background_snakes()
        self.start_button = PremiumButton("START GAME", (46,204,113), (39,174,96), "▶", size_hint=(None,None), size=(240,55))
        self.quit_button = PremiumButton("QUIT", (231,76,60), (192,57,43), "✖", size_hint=(None,None), size=(240,55))
        self.add_widget(self.start_button)
        self.add_widget(self.quit_button)
        Clock.schedule_interval(self.update, 1/60)

    def on_size(self, *args):
        self.start_button.pos = (WINDOW_WIDTH//2 - 120, 400)
        self.quit_button.pos = (WINDOW_WIDTH//2 - 120, 470)

    def create_background_snakes(self):
        for _ in range(3):
            self.background_snakes.append({
                'segments': [(random.randint(0,WINDOW_WIDTH), random.randint(0,WINDOW_HEIGHT))],
                'direction': random.choice([(1,0),(-1,0),(0,1),(0,-1)]),
                'color': (random.randint(20,50), random.randint(100,150), random.randint(20,50))
            })

    def update(self, dt):
        self.float_offset = (self.float_offset + 0.02) % (2*math.pi)
        self.start_button.update(dt)
        self.quit_button.update(dt)
        for snake in self.background_snakes:
            head = snake['segments'][0]
            new_x = head[0] + snake['direction'][0]*2
            new_y = head[1] + snake['direction'][1]*2
            if new_x < -100 or new_x > WINDOW_WIDTH+100:
                snake['direction'] = (random.choice([-1,1]), random.choice([-1,0,1]))
            if new_y < -100 or new_y > WINDOW_HEIGHT+100:
                snake['direction'] = (random.choice([-1,0,1]), random.choice([-1,1]))
            snake['segments'].insert(0, (new_x, new_y))
            if len(snake['segments']) > 20:
                snake['segments'].pop()
        if random.random() < 0.2:
            self.particles.emit(random.randint(0,WINDOW_WIDTH), random.randint(0,WINDOW_HEIGHT), TEXT_GOLD, count=2, speed_range=(1,3))
        self.particles.update()
        self.draw()

    def draw_background_snakes(self):
        with self.canvas:
            for snake in self.background_snakes:
                for i,(x,y) in enumerate(snake['segments']):
                    alpha = int(30 * (1 - i/len(snake['segments'])))
                    Color(*rgba(snake['color'], alpha))
                    Ellipse(pos=(x-15, y-15), size=(30,30))

    def draw(self):
        self.canvas.clear()
        for y in range(0, WINDOW_HEIGHT, 2):
            val = 10 + int(math.sin(self.float_offset + y*0.01)*5)
            col = (val/255., (val+5)/255., (val+15)/255.)
            with self.canvas:
                Color(*col)
                Line(points=[0,y,WINDOW_WIDTH,y], width=2)
        self.draw_background_snakes()
        self.particles.draw()
        title_label = CoreLabel(text="SNAKE LEGENDS", font_size=100, font_name='Roboto', color=TEXT_GOLD)
        tex = title_label.texture
        title_offset = math.sin(self.float_offset)*5
        with self.canvas:
            Color(0,0,0)
            for off in range(5):
                Rectangle(texture=tex, pos=(WINDOW_WIDTH//2-tex.width/2+off, 150+title_offset+off-tex.height/2), size=tex.size)
            Color(*rgba(TEXT_GOLD))
            Rectangle(texture=tex, pos=(WINDOW_WIDTH//2-tex.width/2, 150+title_offset-tex.height/2), size=tex.size)
        sub_label = CoreLabel(text="360° MOVEMENT | PREMIUM SNAKE GAME", font_size=36, font_name='Roboto', color=TEXT_WHITE)
        sub_tex = sub_label.texture
        with self.canvas:
            for i in range(3):
                Color(*rgba(TEXT_GOLD, 30 - i*10))
                Rectangle(texture=sub_tex, pos=(WINDOW_WIDTH//2-sub_tex.width/2 + i, 210 + i - sub_tex.height/2), size=sub_tex.size)
            Color(*rgba(TEXT_WHITE))
            Rectangle(texture=sub_tex, pos=(WINDOW_WIDTH//2-sub_tex.width/2, 210 - sub_tex.height/2), size=sub_tex.size)
        features = [("🎮","360° Joystick","Full analog control"),
                    ("⚡","Combo System","Chain eats for bonus"),
                    ("🏆","Leaderboard","Beat high scores"),
                    ("✨","Visual Effects","Stunning graphics")]
        card_w = 160
        card_h = 100
        start_x = (WINDOW_WIDTH - (card_w*4+30))//2
        for i,(icon,title,desc) in enumerate(features):
            x = start_x + i*(card_w+10)
            y = 260
            with self.canvas:
                for j in range(card_h):
                    ratio = j/card_h
                    Color(25/255.,30/255.,45/255., 0.8 - ratio*0.2)
                    Line(points=[x, y+j, x+card_w, y+j], width=1)
                Color(*rgba(TEXT_GOLD, 100))
                Rectangle(pos=(x,y), size=(card_w,card_h))
            icon_label = CoreLabel(text=icon, font_size=40, font_name='Roboto', color=TEXT_GOLD)
            icon_tex = icon_label.texture
            with self.canvas:
                Rectangle(texture=icon_tex, pos=(x+card_w/2 - icon_tex.width/2, y+30 - icon_tex.height/2), size=icon_tex.size)
            t_label = CoreLabel(text=title, font_size=18, font_name='Roboto', color=TEXT_WHITE)
            t_tex = t_label.texture
            with self.canvas:
                Rectangle(texture=t_tex, pos=(x+card_w/2 - t_tex.width/2, y+60 - t_tex.height/2), size=t_tex.size)
            d_label = CoreLabel(text=desc, font_size=14, font_name='Roboto', color=(150,150,150))
            d_tex = d_label.texture
            with self.canvas:
                Rectangle(texture=d_tex, pos=(x+card_w/2 - d_tex.width/2, y+80 - d_tex.height/2), size=d_tex.size)
        footer_label = CoreLabel(text="MADE WITH DEEPSEEK AI - PREMIUM GAMING EXPERIENCE", font_size=16, font_name='Roboto', color=(100,100,120))
        footer_tex = footer_label.texture
        with self.canvas:
            Rectangle(texture=footer_tex, pos=(WINDOW_WIDTH//2 - footer_tex.width/2, WINDOW_HEIGHT-30 - footer_tex.height/2), size=footer_tex.size)

class ModernJoystick(Widget):
    def __init__(self, x, y, radius=90, **kwargs):
        super().__init__(**kwargs)
        self.center = (x, y)
        self.radius = radius
        self.knob_radius = 35
        self.active = False
        self.drag_pos = (x, y)
        self.direction = (0,0)
        self.angle = 0
        self.intensity = 0
        self.pulse = 0
        self.size = (radius*2, radius*2)
        self.pos = (x-radius, y-radius)
        self.register_event_type('on_direction')
        Clock.schedule_interval(self.update_anim, 1/60)

    def update_anim(self, dt):
        self.pulse = (self.pulse + 0.1) % (2*math.pi)
        self.draw()

    def on_touch_down(self, touch):
        if math.hypot(touch.x - self.center[0], touch.y - self.center[1]) <= self.radius:
            self.active = True
            self.drag_pos = (touch.x, touch.y)
            self.update_dir(touch)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.active:
            self.drag_pos = (touch.x, touch.y)
            self.update_dir(touch)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.active:
            self.active = False
            self.direction = (0,0)
            self.intensity = 0
            self.drag_pos = self.center
            self.dispatch('on_direction', (0,0), None)
            return True
        return super().on_touch_up(touch)

    def update_dir(self, touch):
        dx = touch.x - self.center[0]
        dy = touch.y - self.center[1]
        dist = math.hypot(dx, dy)
        if dist > self.radius:
            dx = dx * self.radius / dist
            dy = dy * self.radius / dist
            dist = self.radius
        self.drag_pos = (self.center[0] + dx, self.center[1] + dy)
        if dist > 15:
            self.direction = (dx/self.radius, dy/self.radius)
            self.intensity = dist/self.radius
            self.angle = math.atan2(dy, dx)
        else:
            self.direction = (0,0)
            self.intensity = 0
        self.dispatch('on_direction', self.direction, self.angle if self.intensity>0.15 else None)

    def on_direction(self, dir_vec, angle):
        pass

    def get_direction(self):
        if self.active and self.intensity > 0.15:
            return self.direction
        return (0,0)

    def get_angle(self):
        if self.active and self.intensity > 0.15:
            return self.angle
        return None

    def draw(self):
        self.canvas.clear()
        glow_r = self.radius + 5 + math.sin(self.pulse)*2
        with self.canvas:
            Color(*rgba(JOYSTICK_BG, 50))
            Ellipse(pos=(self.center[0]-glow_r, self.center[1]-glow_r), size=(glow_r*2, glow_r*2))
            Color(*rgba(JOYSTICK_BG))
            Ellipse(pos=(self.center[0]-self.radius, self.center[1]-self.radius), size=(self.radius*2, self.radius*2))
            Color(*rgba((100,120,140)))
            Ellipse(pos=(self.center[0]-self.radius, self.center[1]-self.radius), size=(self.radius*2, self.radius*2), width=3)
        if self.active and self.intensity>0:
            for i in range(3):
                progress = (self.pulse + i*2) % (2*math.pi) / (2*math.pi)
                end_x = self.center[0] + self.direction[0] * self.radius * (0.5+progress*0.5)
                end_y = self.center[1] + self.direction[1] * self.radius * (0.5+progress*0.5)
                with self.canvas:
                    Color(*rgba(TEXT_GOLD, 150))
                    Line(points=[self.center[0], self.center[1], end_x, end_y], width=4)
        knob_scale = 1 + self.intensity*0.15
        knob_r = int(self.knob_radius * knob_scale)
        col_int = 100 + int(self.intensity*155)
        with self.canvas:
            Color(50/255.,50/255.,70/255.)
            Ellipse(pos=(self.drag_pos[0]-knob_r+3, self.drag_pos[1]-knob_r+3), size=(knob_r*2, knob_r*2))
            Color(col_int/255., col_int/255., 1)
            Ellipse(pos=(self.drag_pos[0]-knob_r, self.drag_pos[1]-knob_r), size=(knob_r*2, knob_r*2))
            Color(1,1,1,0.6)
            Ellipse(pos=(self.drag_pos[0]-knob_r//3-5, self.drag_pos[1]-knob_r//3-5), size=(knob_r//1.5, knob_r//1.5))
            Color(*rgba(TEXT_WHITE))
            Ellipse(pos=(self.center[0]-6, self.center[1]-6), size=(12,12))

class SnakeSegment:
    def __init__(self, x, y, angle=0):
        self.x = x
        self.y = y
        self.angle = angle
        self.wave_offset = random.uniform(0, math.pi*2)

class SmoothSnake:
    def __init__(self):
        start_x = WINDOW_WIDTH//2
        start_y = WINDOW_HEIGHT//2
        self.segments = deque()
        for i in range(3):
            self.segments.append(SnakeSegment(start_x - i*CELL_SIZE, start_y))
        self.direction = (1,0)
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
        if joystick_dir and joystick_dir != (0,0) and joystick_angle is not None:
            self.target_angle = joystick_angle
            diff = self.target_angle - self.current_angle
            while diff > math.pi: diff -= 2*math.pi
            while diff < -math.pi: diff += 2*math.pi
            self.current_angle += diff * 0.15
            self.direction = (math.cos(self.current_angle), math.sin(self.current_angle))
        head = self.segments[0]
        new_x = head.x + self.direction[0] * self.speed
        new_y = head.y + self.direction[1] * self.speed
        if new_x < 0: new_x = WINDOW_WIDTH
        elif new_x > WINDOW_WIDTH: new_x = 0
        if new_y < 0: new_y = WINDOW_HEIGHT
        elif new_y > WINDOW_HEIGHT: new_y = 0
        self.trail_positions.appendleft((head.x, head.y))
        new_head = SnakeSegment(new_x, new_y, self.current_angle)
        self.segments.appendleft(new_head)
        if self.grow_count > 0:
            self.grow_count -= 1
        else:
            self.segments.pop()
        for i, seg in enumerate(self.segments):
            seg.wave_offset = (seg.wave_offset + 0.1) % (2*math.pi)
            if i>0:
                prev = self.segments[i-1]
                dx = prev.x - seg.x
                dy = prev.y - seg.y
                dist = math.hypot(dx, dy)
                if dist > CELL_SIZE*1.2:
                    ang = math.atan2(dy, dx)
                    seg.x += math.cos(ang)*(dist-CELL_SIZE)*0.3
                    seg.y += math.sin(ang)*(dist-CELL_SIZE)*0.3

    def grow(self):
        self.grow_count += 2
        self.immune_timer = 30

    def check_self_collision(self):
        if self.invincible_timer>0 or self.immune_timer>0:
            return False
        if len(self.segments)>5:
            head = self.segments[0]
            for i, seg in enumerate(self.segments):
                if i>5 and math.hypot(head.x-seg.x, head.y-seg.y) < CELL_SIZE*0.5:
                    return True
        return False

    def check_apple_collision(self, apple_rect):
        head = self.segments[0]
        head_rect = (head.x - CELL_SIZE//2, head.y - CELL_SIZE//2, CELL_SIZE, CELL_SIZE)
        return (head_rect[0] < apple_rect[0]+apple_rect[2] and
                head_rect[0]+head_rect[2] > apple_rect[0] and
                head_rect[1] < apple_rect[1]+apple_rect[3] and
                head_rect[1]+head_rect[3] > apple_rect[1])

    def draw(self, canvas):
        for i,(x,y) in enumerate(self.trail_positions):
            alpha = int(50*(1-i/len(self.trail_positions)))
            with canvas:
                Color(*rgba(SNAKE_BODY_TOP, alpha))
                Ellipse(pos=(x-CELL_SIZE//2, y-CELL_SIZE//2), size=(CELL_SIZE,CELL_SIZE))
        for i, seg in enumerate(self.segments):
            x = seg.x - CELL_SIZE//2
            y = seg.y - CELL_SIZE//2
            wave_x = x + math.sin(seg.wave_offset+i)*2
            wave_y = y + math.cos(seg.wave_offset*0.7+i)*2
            if i==0:
                # draw head
                for j in range(CELL_SIZE):
                    col = (SNAKE_HEAD_GRADIENT_TOP[0] + (SNAKE_HEAD_GRADIENT_BOTTOM[0]-SNAKE_HEAD_GRADIENT_TOP[0])*j/CELL_SIZE,
                           SNAKE_HEAD_GRADIENT_TOP[1] + (SNAKE_HEAD_GRADIENT_BOTTOM[1]-SNAKE_HEAD_GRADIENT_TOP[1])*j/CELL_SIZE,
                           SNAKE_HEAD_GRADIENT_TOP[2] + (SNAKE_HEAD_GRADIENT_BOTTOM[2]-SNAKE_HEAD_GRADIENT_TOP[2])*j/CELL_SIZE)
                    with canvas:
                        Color(*rgba(col))
                        Line(points=[wave_x, wave_y+j, wave_x+CELL_SIZE, wave_y+j], width=1)
                # eyes
                eye_off = CELL_SIZE//3
                eye_sz = CELL_SIZE//6
                ang = self.current_angle
                left_eye = (seg.x + math.cos(ang+0.8)*eye_off, seg.y + math.sin(ang+0.8)*eye_off)
                right_eye = (seg.x + math.cos(ang-0.8)*eye_off, seg.y + math.sin(ang-0.8)*eye_off)
                with canvas:
                    Color(*rgba(TEXT_WHITE))
                    Ellipse(pos=(left_eye[0]-eye_sz, left_eye[1]-eye_sz), size=(eye_sz*2, eye_sz*2))
                    Ellipse(pos=(right_eye[0]-eye_sz, right_eye[1]-eye_sz), size=(eye_sz*2, eye_sz*2))
                    Color(0,0,0)
                    Ellipse(pos=(left_eye[0]+math.cos(ang)*2 - eye_sz//2, left_eye[1]+math.sin(ang)*2 - eye_sz//2), size=(eye_sz, eye_sz))
                    Ellipse(pos=(right_eye[0]+math.cos(ang)*2 - eye_sz//2, right_eye[1]+math.sin(ang)*2 - eye_sz//2), size=(eye_sz, eye_sz))
            else:
                body_col = SNAKE_BODY_TOP if i%2==0 else SNAKE_BODY_BOTTOM
                with canvas:
                    Color(*rgba(body_col))
                    Rectangle(pos=(wave_x, wave_y), size=(CELL_SIZE-2, CELL_SIZE-2))
                scale_col = (40,180,100)
                for s in range(2):
                    sx = wave_x + CELL_SIZE//3 + s*CELL_SIZE//3
                    sy = wave_y + CELL_SIZE//2
                    with canvas:
                        Color(*rgba(scale_col))
                        Ellipse(pos=(sx-2, sy-2), size=(4,4))

class AnimatedApple:
    def __init__(self):
        self.x = random.randint(CELL_SIZE, WINDOW_WIDTH-CELL_SIZE)
        self.y = random.randint(CELL_SIZE, WINDOW_HEIGHT-CELL_SIZE)
        self.float_offset = 0
        self.rotation = 0
        self.pulse_scale = 0

    def randomize_position(self, snake_segments=None):
        max_attempts = 1000
        for _ in range(max_attempts):
            self.x = random.randint(CELL_SIZE, WINDOW_WIDTH-CELL_SIZE)
            self.y = random.randint(CELL_SIZE, WINDOW_HEIGHT-CELL_SIZE)
            if snake_segments:
                collision = False
                for seg in snake_segments:
                    if math.hypot(self.x-seg.x, self.y-seg.y) < CELL_SIZE:
                        collision = True
                        break
                if not collision:
                    return
        self.x, self.y = CELL_SIZE, CELL_SIZE

    def update(self, dt):
        self.float_offset = (self.float_offset + 0.05) % (2*math.pi)
        self.rotation = (self.rotation + 0.05) % (2*math.pi)
        self.pulse_scale = 1 + math.sin(self.float_offset*2)*0.1

    def get_rect(self):
        size = int(CELL_SIZE*0.7*self.pulse_scale)
        x = self.x - size//2
        y = self.y - size//2 + math.sin(self.float_offset)*3
        return (x, y, size, size)

    def draw(self, canvas):
        size = int(CELL_SIZE*0.7*self.pulse_scale)
        x = self.x - size//2
        y = self.y - size//2 + math.sin(self.float_offset)*3
        # glow
        glow_sz = size+10
        with canvas:
            Color(*rgba(APPLE_RED, 50))
            Ellipse(pos=(x - glow_sz//2 + size//2, y - glow_sz//2 + size//2), size=(glow_sz, glow_sz))
        # apple body
        for i in range(size):
            col = (APPLE_RED[0] - i*30//size,
                   APPLE_RED[1] - i*20//size,
                   APPLE_RED[2] - i*20//size)
            with canvas:
                Color(*rgba(col))
                Line(points=[x+i, y, x+i, y+size], width=1)
        # highlight
        with canvas:
            Color(255/255., 200/255., 200/255.)
            Rectangle(pos=(x+3, y+3), size=(size//3, size//4))
        # leaf
        leaf_ang = self.rotation
        leaf_x = x+size-5
        leaf_y = y-3
        leaf_pts = [(leaf_x, leaf_y),
                    (leaf_x + math.cos(leaf_ang)*8, leaf_y + math.sin(leaf_ang)*8 -5),
                    (leaf_x + math.cos(leaf_ang+1)*5, leaf_y + math.sin(leaf_ang+1)*5 -3)]
        with canvas:
            Color(*rgba(APPLE_GREEN))
            Line(points=[p for pt in leaf_pts for p in pt], width=2)
            Color(101/255., 67/255., 33/255.)
            Line(points=[leaf_x, leaf_y, leaf_x-3, leaf_y-5], width=2)

class GameUI:
    def __init__(self):
        self.score_animation = 0
        self.combo = 0
        self.combo_timer = 0
        self.score = 0
        self.high_score = 0

    def update(self, dt):
        if self.score_animation > 0:
            self.score_animation -= 0.1
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0

    def add_score(self):
        self.score_animation = 1
        self.combo += 1
        self.combo_timer = 60

    def draw(self, canvas, score, high_score):
        self.score = score
        self.high_score = high_score
        with canvas:
            Color(0,0,0,0.4)
            Rectangle(pos=(10,10), size=(150,60))
        label = CoreLabel(text=str(score), font_size=80, font_name='Roboto', color=TEXT_GOLD)
        tex = label.texture
        with canvas:
            Rectangle(texture=tex, pos=(20,10), size=tex.size)
        label2 = CoreLabel(text="SCORE", font_size=24, font_name='Roboto', color=TEXT_WHITE)
        tex2 = label2.texture
        with canvas:
            Rectangle(texture=tex2, pos=(25,65), size=tex2.size)
        label3 = CoreLabel(text=f"BEST: {high_score}", font_size=32, font_name='Roboto', color=TEXT_WHITE)
        tex3 = label3.texture
        with canvas:
            Rectangle(texture=tex3, pos=(WINDOW_WIDTH - tex3.width - 20, 20), size=tex3.size)
        if self.combo > 1 and self.combo_timer > 0:
            label4 = CoreLabel(text=f"x{self.combo} COMBO!", font_size=48, font_name='Roboto', color=TEXT_GOLD)
            tex4 = label4.texture
            with canvas:
                Rectangle(texture=tex4, pos=(WINDOW_WIDTH//2 - tex4.width//2, 50), size=tex4.size)

class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.snake = SmoothSnake()
        self.apple = AnimatedApple()
        self.joystick = ModernJoystick(WINDOW_WIDTH-100, WINDOW_HEIGHT-100, 90)
        self.particles = ParticleEmitter(self)
        self.ui = GameUI()
        self.score = 0
        self.high_score = 0
        self.paused = False
        self.add_widget(self.joystick)
        self.joystick.bind(on_direction=self.on_joystick)
        Clock.schedule_interval(self.update_game, 1/FPS)

    def on_joystick(self, instance, dir_vec, angle):
        self.joystick_dir = dir_vec
        self.joystick_angle = angle

    def update_game(self, dt):
        if self.paused:
            return
        self.snake.update(getattr(self,'joystick_dir',(0,0)), getattr(self,'joystick_angle',None))
        self.apple.update(dt)
        self.particles.update()
        self.ui.update(dt)
        apple_rect = self.apple.get_rect()
        if self.snake.check_apple_collision(apple_rect):
            self.score += 1
            self.ui.add_score()
            self.particles.emit(self.apple.x, self.apple.y, PARTICLE_COLOR, 30)
            self.snake.grow()
            self.apple.randomize_position(self.snake.segments)
            if self.score > self.high_score:
                self.high_score = self.score
            Clock.schedule_once(lambda dt: self.flash(), 0)
        if self.snake.check_self_collision():
            App.get_running_app().root.show_menu()
            return
        self.draw()

    def flash(self):
        with self.canvas:
            Color(1,1,1,0.4)
            Rectangle(pos=(0,0), size=self.size)
        Clock.schedule_once(lambda dt: self.canvas.clear(), 0.05)

    def draw(self):
        self.canvas.clear()
        for y in range(0, WINDOW_HEIGHT, 2):
            val = 12 + (y*25//WINDOW_HEIGHT)
            col = (val/255., (val+3)/255., (val+10)/255.)
            with self.canvas:
                Color(*col)
                Line(points=[0,y,WINDOW_WIDTH,y], width=2)
        self.snake.draw(self.canvas)
        self.apple.draw(self.canvas)
        self.particles.draw()
        self.ui.draw(self.canvas, self.score, self.high_score)
        if self.paused:
            with self.canvas:
                Color(0,0,0,0.7)
                Rectangle(pos=(0,0), size=self.size)
                label = CoreLabel(text="PAUSED", font_size=80, font_name='Roboto', color=TEXT_GOLD)
                tex = label.texture
                Rectangle(texture=tex, pos=(WINDOW_WIDTH//2 - tex.width//2, WINDOW_HEIGHT//2 - tex.height//2), size=tex.size)

class SnakeLegendsApp(App):
    def build(self):
        self.root_layout = FloatLayout(size=(WINDOW_WIDTH, WINDOW_HEIGHT))
        self.intro = IntroScreen(size=(WINDOW_WIDTH, WINDOW_HEIGHT))
        self.menu = ModernStartMenu(size=(WINDOW_WIDTH, WINDOW_HEIGHT))
        self.game = None
        self.root_layout.add_widget(self.intro)
        self.root_layout.add_widget(self.menu)
        self.menu.opacity = 0
        self.intro.start()
        return self.root_layout

    def show_menu(self):
        if self.game:
            self.root_layout.remove_widget(self.game)
            self.game = None
        self.menu.opacity = 1
        self.intro.opacity = 0
        self.menu.start_button.bind(on_press=self.start_game)
        self.menu.quit_button.bind(on_press=self.stop_app)

    def start_game(self, instance):
        self.menu.opacity = 0
        self.game = GameWidget(size=(WINDOW_WIDTH, WINDOW_HEIGHT))
        self.root_layout.add_widget(self.game)

    def stop_app(self, instance):
        self.stop()

if __name__ == "__main__":
    SnakeLegendsApp().run()
