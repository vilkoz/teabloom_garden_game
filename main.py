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
        
        # Show loading screen and load sprites
        self._load_sprites_with_screen()
        
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
    
    def _load_sprites_with_screen(self):
        """Load all sprites with visual feedback on screen"""
        loading_messages = []
        
        def add_message(msg):
            """Add a message to the loading screen"""
            loading_messages.append(msg)
            self._draw_loading_screen(loading_messages)
        
        # Initial message
        add_message("🎨 Loading game sprites...")
        
        # Load all sprites using centralized function
        try:
            load_all_game_sprites(message_callback=add_message)
        except Exception as e:
            add_message(f"❌ Error loading sprites: {e}")
            add_message("Press any key to exit...")
            self._wait_for_input()
            pygame.quit()
            sys.exit(1)
        
        add_message("")
        add_message("Press any key to continue...")
        
        # Wait for user input
        #self._wait_for_input()
    
    def _wait_for_input(self):
        """Wait for user to press a key or click"""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    waiting = False
            self.clock.tick(30)
    
    def _draw_loading_screen(self, messages):
        """Draw the loading screen with messages"""
        # Background
        self.screen.fill((245, 235, 220))
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Tea Garden Cats 🐱🍵", True, (100, 70, 50))
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
        visible_messages = messages[-25:] if len(messages) > 25 else messages  # Show last 25 messages
        
        for i, msg in enumerate(visible_messages):
            color = (50, 150, 50) if msg.startswith("✓") else (100, 100, 100)
            if msg.startswith("✅"):
                color = (0, 180, 0)
            if msg.startswith("Press"):
                color = (200, 100, 0)
            
            text_surface = message_font.render(msg, True, color)
            text_rect = text_surface.get_rect(midtop=(self.width // 2, start_y + i * 22))
            self.screen.blit(text_surface, text_rect)
        
        # Update display
        pygame.display.flip()
        
        # Process events to prevent window freeze
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
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
