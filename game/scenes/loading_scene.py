"""Loading scene with on-screen messages and asset loading logic."""
import os
import sys
import threading
import time
import pygame
from game.sprite_loader import load_all_game_sprites

from game.shared_sim import SharedSimSurface


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

        # perf counters for temporary profiling
        self._dt_samples = []
        self._update_samples = []
        self._draw_samples = []
        self._message_count_interval = 0
        self._last_report = time.perf_counter()

        # background fluid simulation scene running in a separate process
        self.sim_surface = SharedSimSurface(self.width, self.height)
        self.sim_surface.start()

    def run(self):
        def add_message(msg: str):
            with self._lock:
                self._messages.append(msg)
                self._message_count_interval += 1

        add_message("Loading game sprites...")

        # limit numpy/BLAS threads to reduce contention during loading

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
            dt_sec = dt / 1000.0

            # perf: time draw only (sim runs out-of-process)
            t_draw_start = time.perf_counter()
            self.screen.blit(self.sim_surface.get_surface(), (0, 0))

            # draw messages overlay
            with self._lock:
                msgs = list(self._messages)
            self._draw_messages(msgs)

            pygame.display.flip()
            t_draw_end = time.perf_counter()

            # collect perf samples (keep bounded)
            self._dt_samples.append(dt_sec)
            self._update_samples.append(0.0)
            self._draw_samples.append(t_draw_end - t_draw_start)
            if len(self._dt_samples) > 600:
                self._dt_samples.pop(0)
                self._update_samples.pop(0)
                self._draw_samples.pop(0)

            now = time.perf_counter()
            if now - self._last_report >= 2.0:
                self._report_perf()
                self._last_report = now
                self._message_count_interval = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.sim_surface.shutdown()
                    pygame.quit()
                    sys.exit()
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    if self._done:
                        if self._error:
                            self.sim_surface.shutdown()
                            pygame.quit()
                            sys.exit(1)
                        t.join()
                        self.sim_surface.shutdown()
                        return

    def _draw_messages(self, messages):
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

    def _report_perf(self):
        if not self._dt_samples:
            return

        def stats(samples):
            return (
                min(samples),
                sum(samples) / len(samples),
                max(samples),
            )

        dt_min, dt_avg, dt_max = stats(self._dt_samples)
        upd_min, upd_avg, upd_max = stats(self._update_samples) if self._update_samples else (0, 0, 0)
        drw_min, drw_avg, drw_max = stats(self._draw_samples) if self._draw_samples else (0, 0, 0)

        print(
            f"[loading perf] samples={len(self._dt_samples)} "
            f"dt_ms min/avg/max={dt_min*1000:.2f}/{dt_avg*1000:.2f}/{dt_max*1000:.2f} "
            f"update_ms min/avg/max={upd_min*1000:.2f}/{upd_avg*1000:.2f}/{upd_max*1000:.2f} "
            f"draw_ms min/avg/max={drw_min*1000:.2f}/{drw_avg*1000:.2f}/{drw_max*1000:.2f} "
            f"msgs_in_window={self._message_count_interval}"
        )

        # sim runs in a separate process; no in-process breakdown here.
