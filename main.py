"""Tea Garden Cats - Main Game Entry Point"""
import pygame
import sys
from game.game_state import GameState
from game.scenes.menu_scene import MenuScene
from game.scenes.game_scene import GameScene
from game.scenes.stats_scene import StatsScene
from game.scenes.loading_scene import LoadingScene
from game.sound_manager import get_sound_manager, SoundEffect


class Game:
    """Main game class"""
    
    def __init__(self):
        pygame.init()
        
        # Screen setup
        self.width = 1024
        self.height = 768
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Teabloom Garden 🐱🍵")
        
        # Clock for frame rate
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Show loading screen and load sprites
        self._load_sprites_with_screen()
        
        # Initialize sound system
        self.sound_manager = get_sound_manager()
        # Start background music with fade-in
        self.sound_manager.play_music(SoundEffect.BACKGROUND_MUSIC, loops=-1, fade_ms=1000)
        self.sound_manager.play_music(SoundEffect.AMBIENT_GARDEN, loops=-1, fade_ms=1000)
        
        # Game state
        self.game_state = GameState()
        
        # Scenes
        self.scenes = {
            # initialize only first scene
            'menu': MenuScene(self.screen, self.game_state),
            'game': GameScene,
            'stats': StatsScene,
        }
        
        self.current_scene = 'menu'
        self.running = True
    
    def _load_sprites_with_screen(self):
        """Delegate loading with on-screen feedback to LoadingScene."""
        loader = LoadingScene(self.screen)
        loader.run()
    
    # loading display logic moved to `game.scenes.loading_scene.LoadingScene`
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Calculate delta time in milliseconds
            dt = self.clock.tick(self.fps)
            
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
                        elif result == 'stats':
                            self.scenes['stats'] = StatsScene(self.screen, self.game_state)
            
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
                        elif result == 'stats':
                            self.scenes['stats'] = StatsScene(self.screen, self.game_state)
            
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
