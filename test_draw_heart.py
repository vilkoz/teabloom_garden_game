"""Simple tester for ProceduralBackground._draw_heart

Run this script to open a small Pygame window and visualize hearts.
Controls:
 - Click: add a sample heart at mouse
 - R: regenerate background
 - ESC or window close: quit
"""
import pygame
import random
import sys

from game.ui.procedural_background import ProceduralBackground


def main():
    pygame.init()
    size = (900, 600)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Test _draw_heart")
    clock = pygame.time.Clock()

    bg = ProceduralBackground(size[0], size[1], seed=1234)
    bg.animated = True  # enable animations for testing

    samples = []
    # preload a few sample hearts with varying sizes/colors
    for i in range(7):
        samples.append({
            "x": 80 + i * 110,
            "y": 160,
            "size": 12 + i * 6,
            "color": (255, 100 + i * 15, 140 + i * 10),
        })

    running = True
    while running:
        dt = clock.tick(60)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                if ev.key == pygame.K_r:
                    bg = ProceduralBackground(size[0], size[1], seed=random.randint(0, 99999))
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                samples.append({"x": mx, "y": my, "size": random.randint(14, 36), "color": (255, random.randint(90, 220), random.randint(120, 255))})

        # update background animations (pass ms)
        bg.update(dt)

        # draw
        screen.fill((0, 0, 0))
        bg.draw(screen)

        # draw sample hearts using the internal helper
        for s in samples:
            bg._draw_heart(screen, s["x"], s["y"], s["size"], s["color"])

        # simple UI text
        font = pygame.font.SysFont(None, 20)
        txt = font.render("Click to add heart — R to regen background — ESC to quit", True, (30, 30, 30))
        screen.blit(txt, (10, 10))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pygame.quit()
        raise
