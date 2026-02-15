"""Loading scene with on-screen messages and asset loading logic."""
import sys
import threading
import pygame
from game.sprite_loader import load_all_game_sprites

from game.scenes.fluid_simulation_scene import FluidSimulationScene


class LoadingScene:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.clock = pygame.time.Clock()
        self._messages = []
        self._lock = threading.Lock()
        self._done = False
        self._error = False

        # background fluid simulation scene
        self.sim_scene = FluidSimulationScene(screen)

    def run(self):
        def add_message(msg: str):
            with self._lock:
                self._messages.append(msg)

        add_message("Loading game sprites...")

        def loader():
            try:
                load_all_game_sprites(message_callback=add_message)
            except Exception as e:
                add_message(f"Error loading sprites: {e}")
                add_message("Press any key to exit...")
                self._error = True
            finally:
                add_message("")
                add_message("Press any key to continue...")
                self._done = True

        t = threading.Thread(target=loader, daemon=True)
        t.start()

        while True:
            dt = self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    if self._done:
                        if self._error:
                            pygame.quit()
                            sys.exit(1)
                        t.join()
                        return

            # draw static simulation background
            self.sim_scene.update(dt / 1000.0)
            self.sim_scene.draw()

            # draw messages overlay
            with self._lock:
                msgs = list(self._messages)
            self._draw_loading_screen(msgs)

    def _draw_loading_screen(self, messages):
        # Background
        #self.screen.fill((245, 235, 220, 0.5))

        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Teabloom garden", True, (100, 70, 50))
        title_rect = title_text.get_rect(center=(self.width // 2, 80))
        self.screen.blit(title_text, title_rect)

        # Subtitle
        subtitle_font = pygame.font.Font(None, 24)
        subtitle_text = subtitle_font.render("Loading game assets...", True, (150, 120, 90))
        subtitle_rect = subtitle_text.get_rect(center=(self.width // 2, 130))
        self.screen.blit(subtitle_text, subtitle_rect)

        # Messages
        message_font = pygame.font.Font(None, 20)
        start_y = 180
        message_left = 80
        visible_messages = messages[-25:] if len(messages) > 25 else messages

        for i, msg in enumerate(visible_messages):
            color = (50, 150, 50) if msg.startswith("Loaded") else (100, 100, 100)
            if msg.startswith("All sprite loading complete"):
                color = (0, 180, 0)
            if msg.startswith("Press"):
                color = (200, 100, 0)

            text_surface = message_font.render(msg, True, color)
            text_rect = text_surface.get_rect(topleft=(message_left, start_y + i * 22))
            self.screen.blit(text_surface, text_rect)

        # Update display
        pygame.display.flip()
