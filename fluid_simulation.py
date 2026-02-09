import pygame

from game.scenes.fluid_simulation_scene import *


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("2D Tea Pour Simulation")
    clock = pygame.time.Clock()
    scene = FluidSimulationScene(screen)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            res = scene.handle_event(event)
            if res == "quit":
                running = False

        scene.update(dt)
        scene.draw()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
