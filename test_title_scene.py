"""Test runner for TitleScene
Run with: uv run test_title_scene.py
This will open a pygame window and display the title scene until you press the buttons or close the window.
"""
import pygame
from game.game_state import GameState
from game.scenes.title_scene import TitleScene

def main():
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption('Title Scene Test')
    clock = pygame.time.Clock()

    gs = GameState()
    # ensure total_hearts >= 120 to trigger directly if needed
    gs.statistics['total_hearts'] = max(gs.statistics.get('total_hearts', 0), 120)

    scene = TitleScene(screen, gs)

    running = True
    while running:
        dt = clock.tick(175)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                res = scene.handle_event(event)
                if res in ('menu','game'):
                    print('Button pressed:', res)
                    running = False
        scene.run_once(dt)
        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()
