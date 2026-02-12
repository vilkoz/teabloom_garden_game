"""Title scene shown when player reaches Valentine threshold"""
import pygame
import time
from ..ui.tooltip import Tooltip

class TitleScene:
    def __init__(self, screen, game_state, text=None):
        self.screen = screen
        self.game_state = game_state
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.clock = pygame.time.Clock()
        # Ukrainian default text (extensive)
        self.text = text or (
            "З Днем Валентина, моя маленька мапко!\n"
            "Ти робиш моє серце теплим щоразу, коли ти поруч.\n"
            "Дякую за сміх, за обійми і за всі маленькі моменти — вони для мене безцінні.\n"
            "Нехай цей день буде наповнений цукерками, усмішками і мільйоном поцілунків для тебе."
        )
        self.font = pygame.font.Font(None, 40)
        self.small_font = pygame.font.Font(None, 28)
        self.displayed = ""
        self.char_index = 0
        self.char_timer = 0.0
        self.char_interval = 40  # milliseconds between chars
        self.finished = False
        self.finish_time = None
        self.buttons = []  # (rect, label, action)
        self.tooltip = Tooltip()
        # prepare buttons positions
        btn_w, btn_h = 220, 50
        # particle system for fireworks (if available via sprite_loader)
        self.particle_system = None
        try:
            # try to reuse global particle system if present on game_state or screen
            self.particle_system = getattr(self.game_state, 'particle_system', None)
        except Exception:
            self.particle_system = None
        # fireworks timing
        self.next_firework = 0
        self.firework_interval = 800  # ms between fireworks
        gap = 20
        x1 = self.width//2 - btn_w - gap//2
        x2 = self.width//2 + gap//2
        y = self.height - 120
        self.buttons.append((pygame.Rect(x1, y, btn_w, btn_h), "Продовжити гру", "continue"))
        self.buttons.append((pygame.Rect(x2, y, btn_w, btn_h), "Головне меню", "menu"))

    def handle_event(self, event):
        # Accept mouse down or up for compatibility and Enter/Escape keys
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            pos = pygame.mouse.get_pos()
            for rect, label, action in self.buttons:
                if rect.collidepoint(pos):
                    # debug print to help troubleshooting
                    print(f"TitleScene: button pressed -> {action}")
                    if action == 'continue':
                        return 'game'
                    elif action == 'menu':
                        return 'menu'
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return 'game'
            if event.key == pygame.K_ESCAPE:
                return 'menu'
        return None

    def update(self, dt):
        if not self.finished:
            self.char_timer += dt
            while self.char_timer >= self.char_interval and self.char_index < len(self.text):
                self.char_timer -= self.char_interval
                self.displayed += self.text[self.char_index]
                self.char_index += 1
            if self.char_index >= len(self.text) and not self.finished:
                # append kiss sign (emoji)
                self.displayed = self.displayed + '\n💋'
                self.finished = True
                self.finish_time = pygame.time.get_ticks()
        else:
            # spawn fireworks periodically after finished
            if self.particle_system:
                self.next_firework -= dt
                if self.next_firework <= 0:
                    # pick a random x across envelope area
                    env_x = int(self.width * 0.14)
                    env_w = int(self.width * 0.72)
                    fx = env_x + random.randint(40, env_w - 40)
                    fy = int(self.height * 0.3)
                    # upward vector
                    vx = random.uniform(-60, 60)
                    vy = random.uniform(-600, -400)
                    self.particle_system.spawn_explosion((fx, fy), (vx, vy), count=18, spread=0.8,
                                                         color=(255, random.randint(120,220), random.randint(80,160)))
                    self.next_firework = self.firework_interval
        return None

    def draw_envelope(self):
        # draw a simple envelope-like background centered
        env_w = int(self.width * 0.72)
        env_h = int(self.height * 0.56)
        env_x = (self.width - env_w) // 2
        env_y = (self.height - env_h) // 2
        # envelope base
        pygame.draw.rect(self.screen, (255, 244, 238), (env_x, env_y, env_w, env_h), border_radius=12)
        pygame.draw.rect(self.screen, (200, 160, 160), (env_x, env_y, env_w, env_h), 4, border_radius=12)
        # flap triangle
        points = [(env_x, env_y), (env_x + env_w//2, env_y + env_h//3), (env_x + env_w, env_y)]
        pygame.draw.polygon(self.screen, (255, 232, 230), points)
        pygame.draw.lines(self.screen, (200,160,160), False, points, 2)
        return env_x, env_y, env_w, env_h

    def draw(self):
        # background
        self.screen.fill((240, 230, 236))
        # envelope
        env_x, env_y, env_w, env_h = self.draw_envelope()
        # render displayed text letter-by-letter inside envelope
        lines = self.displayed.split('\n')
        padding = 40
        y = env_y + padding
        for line in lines:
            # wrap long lines
            text_surf = self.font.render(line, True, (80, 30, 60))
            text_rect = text_surf.get_rect(topleft=(env_x + padding, y))
            self.screen.blit(text_surf, text_rect)
            y += text_rect.height + 6
        # draw buttons
        for rect, label, action in self.buttons:
            pygame.draw.rect(self.screen, (250, 200, 210), rect, border_radius=8)
            pygame.draw.rect(self.screen, (160, 80, 100), rect, 2, border_radius=8)
            txt = self.small_font.render(label, True, (40, 20, 30))
            txt_r = txt.get_rect(center=rect.center)
            self.screen.blit(txt, txt_r)

    def run_once(self, dt):
        # convenience to update+draw
        self.update(dt)
        self.draw()

