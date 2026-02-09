"""Popup notification UI component

Handles opening a text popup and spawning a large heart particle effect
for a short duration when opened.
"""
import pygame


class PopupNotification:
    """Simple popup notification with auto-close and heart burst effect."""
    def __init__(self, screen_size, particle_system, sprite_loader=None):
        self.screen_size = screen_size
        self.particle_system = particle_system
        self.sprite_loader = sprite_loader

        self.active = False
        self.text = ""
        self.timer = 0
        self.duration = 3000  # ms total popup duration
        self.heart_effect_time = 3000  # ms during which hearts spawn
        self.heart_spawn_interval = 300  # ms between heart bursts
        self.heart_acc = 0
        self.position = (screen_size[0] // 2, 140)

    def open(self, text, position=None):
        """Open the popup with text. Position is optional (x,y)."""
        self.text = text
        self.active = True
        self.timer = 0
        self.heart_acc = 0
        if position:
            self.position = position
        # immediate big burst
        try:
            self.particle_system.spawn_explosion(self.position, (0, -200), count=30)
        except Exception:
            pass

    def handle_event(self, event):
        """Handle events (click to dismiss)."""
        if not self.active:
            return None
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            # compute popup rect
            popup_w, popup_h = 420, 80
            popup_x = self.position[0] - popup_w // 2
            popup_y = self.position[1] - popup_h // 2
            if popup_x <= mx <= popup_x + popup_w and popup_y <= my <= popup_y + popup_h:
                self.active = False
        return None

    def update(self, dt):
        """Update timers and spawn heart bursts while active."""
        if not self.active:
            return
        self.timer += dt
        if self.timer <= self.heart_effect_time:
            self.heart_acc += dt
            while self.heart_acc >= self.heart_spawn_interval:
                self.heart_acc -= self.heart_spawn_interval
                try:
                    # repeated moderate bursts while active
                    self.particle_system.spawn_explosion(self.position, (0, -200), count=6)
                except Exception:
                    pass

        if self.timer >= self.duration:
            self.active = False

    def draw(self, screen):
        """Draw the popup box and text (no update logic)."""
        if not self.active:
            return

        popup_w, popup_h = 420, 80
        x = self.position[0] - popup_w // 2
        y = self.position[1] - popup_h // 2

        # Background with slight shadow
        shadow_rect = pygame.Rect(x + 4, y + 6, popup_w, popup_h)
        pygame.draw.rect(screen, (0, 0, 0, 60), shadow_rect, border_radius=12)

        bg_rect = pygame.Rect(x, y, popup_w, popup_h)
        pygame.draw.rect(screen, (255, 245, 235), bg_rect, border_radius=12)
        pygame.draw.rect(screen, (150, 110, 90), bg_rect, 2, border_radius=12)

        # Text
        font = pygame.font.Font(None, 28)
        lines = []
        # accept either single string or list
        if isinstance(self.text, (list, tuple)):
            lines = list(self.text)
        else:
            lines = [self.text]

        for i, line in enumerate(lines):
            txt = font.render(line, True, (60, 40, 30))
            txt_rect = txt.get_rect(center=(self.position[0], y + 20 + i * 26))
            screen.blit(txt, txt_rect)
