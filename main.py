"""Tea Garden Cats - Main Game Entry Point"""
import pygame
import sys
from game.game_state import GameState
from game.scenes.menu_scene import MenuScene
from game.scenes.game_scene import GameScene
from game.scenes.stats_scene import StatsScene
from game.sprite_loader import load_all_game_sprites


class Game:
    """Main game class"""
    
    def __init__(self):
        pygame.init()
        
        # Screen setup
        self.width = 1024
        self.height = 768
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Tea Garden Cats 🐱🍵")
        
        # Clock for frame rate
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Load all sprites
        print("🎨 Loading game sprites...")
        load_all_game_sprites()
        
        # Game state
        self.game_state = GameState()
        
        # Scenes
        self.scenes = {
            'menu': MenuScene(self.screen, self.game_state),
            'game': GameScene(self.screen, self.game_state),
            'stats': StatsScene(self.screen, self.game_state)
        }
        
        self.current_scene = 'menu'
        self.running = True
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(self.fps) / 1000.0  # Convert to seconds
            
            # Get current scene
            scene = self.scenes.get(self.current_scene)
            
            if not scene:
                print(f"Error: Scene '{self.current_scene}' not found")
                self.running = False
                continue
            
            # Handle events
            for event in pygame.event.get():
                result = scene.handle_event(event)
                if result:
                    if result == "quit":
                        self.running = False
                    else:
                        # Scene transition
                        self.current_scene = result
                        # Recreate scene to reset state
                        if result == 'game':
                            self.scenes['game'] = GameScene(self.screen, self.game_state)
            
            # Update scene
            if self.running:
                result = scene.update(dt)
                if result:
                    if result == "quit":
                        self.running = False
                    else:
                        self.current_scene = result
                        # Recreate scene to reset state
                        if result == 'game':
                            self.scenes['game'] = GameScene(self.screen, self.game_state)
            
            # Draw scene
            scene.draw()
            
            # Update display
            pygame.display.flip()
        
        # Cleanup
        self.game_state.save_progress()
        pygame.quit()
        sys.exit()


def main():
    """Entry point"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
