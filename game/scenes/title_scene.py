"""Title scene shown when player reaches Valentine threshold"""
import random
import pygame
import time
from pygame_emojis import load_emoji
from ..sprite_loader import get_sprite_loader
from ..ui.particle_system import ParticleSystem
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
            "З Днем Валентина, моя маленька мапко (minimaps))!\n"
            "Як промені літнього сонця, ти робиш моє життя щасливим.\n"
            "Дякую тобі за наші вечори, поїздки, чаювання, сміх,\n"
            "за обійми і за всі маленькі моменти — вони для мене безцінні.\n"
            "Нехай цей день буде наповнений прогулянками, слодощами\n"
            "звісно чаєм, усмішками і мільйоном поцілунків для тебе.\n"
            "Твій лапілапс."
        )
        self.font = pygame.font.Font(None, 40)
        self.small_font = pygame.font.Font(None, 28)
        self.displayed = ""
        self.char_index = 0
        self.char_timer = 0.0
        self.char_interval = 40  # milliseconds between chars
        self.finished = False
        self.finish_time = None
        self.kiss_ready = False
        # Animation sequencing
        self.phase = "open"  # open -> lift -> front -> text
        self.phase_time = 0
        self.open_duration = 800
        self.lift_duration = 900
        self.front_duration = 600
        self.buttons = []  # (rect, label, action)
        self.tooltip = Tooltip()
        self.sprite_loader = get_sprite_loader()
        # Local particle system for fireworks
        self.particle_system = ParticleSystem(self.sprite_loader)
        self.kiss_emoji = load_emoji("💋", size=42)
        self.heart_emoji = load_emoji("❤️", size=256)
        self.frog_emoji = load_emoji("🐸", size=64)
        self.wolf_emoji = load_emoji("🐺", size=64)
        self.heart_surface = None  # created on first draw based on envelope size
        self.paper_pos = [self.width // 2, self.height // 2]
        self.paper_scale = 0.85
        # prepare buttons positions
        btn_w, btn_h = 220, 50
        # fireworks timing
        self.next_firework = 200  # start shortly after text begins
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
            self.phase_time += dt
            if self.phase == "open" and self.phase_time >= self.open_duration:
                self.phase = "lift"
                self.phase_time = 0
            elif self.phase == "lift" and self.phase_time >= self.lift_duration:
                self.phase = "front"
                self.phase_time = 0
            elif self.phase == "front" and self.phase_time >= self.front_duration:
                self.phase = "text"
                self.phase_time = 0

            if self.phase == "text":
                self.char_timer += dt
                while self.char_timer >= self.char_interval and self.char_index < len(self.text):
                    self.char_timer -= self.char_interval
                    self.displayed += self.text[self.char_index]
                    self.char_index += 1
                if self.char_index >= len(self.text) and not self.finished:
                    self.finished = True
                    self.finish_time = pygame.time.get_ticks()
                    self.kiss_ready = True
        # spawn fireworks while text animates and after
        if self.particle_system and self.char_index > 0:
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
        # advance existing particles
        if self.particle_system:
            self.particle_system.update(dt)
        return None

    def draw_envelope(self):
        # draw a simple envelope-like background centered
        env_w = int(self.width * 0.82)
        env_h = int(self.height * 0.64)
        env_x = (self.width - env_w) // 2
        env_y = (self.height - env_h) // 2
        # envelope base
        pygame.draw.rect(self.screen, (255, 244, 238), (env_x, env_y, env_w, env_h), border_radius=12)
        pygame.draw.rect(self.screen, (200, 160, 160), (env_x, env_y, env_w, env_h), 4, border_radius=12)
        # flap triangle opens upward with progress
        open_progress = min(1.0, max(0.0, self.phase_time / self.open_duration)) if self.phase == "open" else 1.0
        flap_raise = int(env_h * 0.25 * open_progress)
        flap_mid_y = env_y + env_h//3 - flap_raise
        points = [(env_x, env_y), (env_x + env_w//2, flap_mid_y), (env_x + env_w, env_y)]
        pygame.draw.polygon(self.screen, (255, 232, 230), points)
        pygame.draw.lines(self.screen, (200,160,160), False, points, 2)
        return env_x, env_y, env_w, env_h, open_progress

    def draw(self):
        # background
        self.screen.fill((240, 230, 236))
        # envelope
        env_x, env_y, env_w, env_h, open_progress = self.draw_envelope()

        # ensure heart paper matches envelope size
        if self.heart_surface is None:
            paper_w = int(env_w * 1.2)
            paper_h = int(env_h * 1.2)
            self.heart_surface = self._create_heart_paper(paper_w, paper_h)

        # paper animation (heart sheet)
        paper_visible = self.heart_surface is not None and (self.phase in ("lift", "front", "text") or self.finished)
        if paper_visible:
            # base position: center of envelope
            base_x = env_x + env_w // 2
            base_y = env_y + env_h // 2
            lift_ratio = 0.0
            front_ratio = 0.0
            if self.phase == "lift":
                lift_ratio = min(1.0, self.phase_time / self.lift_duration)
            elif self.phase == "front":
                lift_ratio = 1.0
                front_ratio = min(1.0, self.phase_time / self.front_duration)
            elif self.phase in ("text",) or self.finished:
                lift_ratio = 1.0
                front_ratio = 1.0

            lifted_y = base_y - int(env_h * 0.6 * lift_ratio)
            scale = 0.65 + 0.10 * front_ratio
            surf = pygame.transform.smoothscale(
                self.heart_surface,
                (int(self.heart_surface.get_width() * scale), int(self.heart_surface.get_height() * scale)),
            )
            # slide toward true screen center as we move to front
            target_x = self.width // 2
            target_y = self.height // 2 - int(env_h * 0.08)
            center_x = int(base_x + (target_x - base_x) * front_ratio)
            center_y_base = lifted_y - int(10 * front_ratio)
            center_y = int(center_y_base + (target_y - center_y_base) * front_ratio)
            surf_rect = surf.get_rect(center=(center_x, center_y))
            self.screen.blit(surf, surf_rect)

        # render displayed text letter-by-letter on the paper (after placed)
        padding = 40
        lines = self._wrap_lines(self.displayed, self.font, env_w - 2 * padding)
        # If paper is visible, anchor text to its top; otherwise use envelope
        if paper_visible:
            base_y_for_text = surf_rect.top + 30
            base_x_for_text = surf_rect.left + padding // 2
        else:
            base_y_for_text = env_y + padding
            base_x_for_text = env_x + padding // 2
        y = base_y_for_text
        for line in lines:
            # wrap long lines
            text_surf = self.font.render(line, True, (80, 30, 60))
            text_rect = text_surf.get_rect(topleft=(base_x_for_text, y))
            self.screen.blit(text_surf, text_rect)
            y += text_rect.height + 6
        if self.kiss_ready and self.kiss_emoji:
            kiss_rect = self.kiss_emoji.get_rect(topleft=(base_x_for_text + 200, y - 40))
            self.screen.blit(self.kiss_emoji, kiss_rect)
        # draw buttons
        for rect, label, action in self.buttons:
            pygame.draw.rect(self.screen, (250, 200, 210), rect, border_radius=8)
            pygame.draw.rect(self.screen, (160, 80, 100), rect, 2, border_radius=8)
            txt = self.small_font.render(label, True, (40, 20, 30))
            txt_r = txt.get_rect(center=rect.center)
            self.screen.blit(txt, txt_r)
        if self.particle_system:
            self.particle_system.draw(self.screen)

    def run_once(self, dt):
        # convenience to update+draw
        self.update(dt)
        self.draw()

    def _create_heart_paper(self, width, height):
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        paper_color = (255, 250, 245)
        heart_color = (255, 170, 190)
        pygame.draw.rect(surf, paper_color, (0, 0, width, height), border_radius=12)
        pygame.draw.rect(surf, (200, 160, 170), (0, 0, width, height), 3, border_radius=12)
        # simple heart shape centered
        cx, cy = width // 2, int(height * 0.4)
        size = int(min(width, height) * 0.28)
        top_offset = size // 2
        left_circle_center = (cx - top_offset, cy - top_offset)
        right_circle_center = (cx + top_offset, cy - top_offset)
        pygame.draw.circle(surf, heart_color, left_circle_center, top_offset)
        pygame.draw.circle(surf, heart_color, right_circle_center, top_offset)
        points = [
            (cx - size, cy - top_offset),
            (cx, cy + size),
            (cx + size, cy - top_offset),
        ]
        pygame.draw.polygon(surf, heart_color, points)
        wolf_size = self.wolf_emoji.get_width()
        wolf_rect = self.wolf_emoji.get_rect(center=(cx, cy + wolf_size // 2))
        surf.blit(self.wolf_emoji, wolf_rect)
        return surf

    def _wrap_lines(self, text, font, max_width):
        lines = []
        for raw_line in text.split('\n'):
            words = raw_line.split(' ')
            current = ""
            for word in words:
                tentative = word if not current else current + " " + word
                if font.size(tentative)[0] <= max_width:
                    current = tentative
                else:
                    if current:
                        lines.append(current)
                    # if a single word is too long, force it on its own line
                    current = word
            if current:
                lines.append(current)
        return lines

