"""Main menu scene"""
import pygame
import random
from pygame_emojis import load_emoji
from game.ui.button import Button
from game.ui.text import Text
from game.sprite_loader import get_sprite_loader
from game.ui.petal_particle import PetalParticleSystem
from game.sound_manager import get_sound_manager, SoundEffect


class MenuScene:
    """Main menu of the game"""
    
    def __init__(self, screen, game_state):
        self.screen = screen
        self.game_state = game_state
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Sprite loader
        self.sprite_loader = get_sprite_loader()
        
        # Sound manager
        self.sound_manager = get_sound_manager()
        
        # Particle system for falling petals
        self.petal_system = PetalParticleSystem(self.width, self.height, self.sprite_loader)
        
        # Create UI elements
        center_x = self.width // 2
        self.title = Text("Tea Garden Cats", center_x, 150, font_size=72, 
                         color=(139, 69, 19), bold=True)
        self.subtitle = Text("A cozy game about serving tea to cats", 
                           center_x, 220, font_size=28, color=(100, 100, 100))
        
        # Buttons
        button_width = 300
        button_height = 60
        button_x = (self.width - button_width) // 2
        
        self.play_button = Button(button_x, 300, button_width, button_height, 
                                  "Play", color=(144, 238, 144))
        self.stats_button = Button(button_x, 380, button_width, button_height, 
                                   "Statistics", color=(135, 206, 250))
        self.quit_button = Button(button_x, 460, button_width, button_height, 
                                  "Quit", color=(255, 182, 193))
        
        # Display hearts
        self.hearts_text = Text(f"Hearts: {self.game_state.hearts}", 
                               20, 20, font_size=36, color=(255, 0, 127), bold=True)
        
        # Mute button
        self.mute_button_rect = pygame.Rect(self.width - 60, self.height - 50, 50, 40)
        
        self.next_scene = None
    
    def handle_event(self, event):
        """Handle input events"""
        if event.type == pygame.QUIT:
            return "quit"
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check mute button
            if self.mute_button_rect.collidepoint(mouse_pos):
                self.sound_manager.toggle_music()
                self.sound_manager.play_sound(SoundEffect.BUTTON_CLICK)
                return None
            
            if self.play_button.update(mouse_pos, True):
                self.sound_manager.play_sound(SoundEffect.BUTTON_CLICK)
                return "game"
            elif self.stats_button.update(mouse_pos, True):
                self.sound_manager.play_sound(SoundEffect.BUTTON_CLICK)
                return "stats"
            elif self.quit_button.update(mouse_pos, True):
                self.sound_manager.play_sound(SoundEffect.BUTTON_CLICK)
                return "quit"
        
        return None
    
    def update(self, dt):
        """Update menu state"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        # Update buttons
        if self.play_button.update(mouse_pos, mouse_pressed):
            return "game"
        if self.stats_button.update(mouse_pos, mouse_pressed):
            return "stats"
        if self.quit_button.update(mouse_pos, mouse_pressed):
            return "quit"
        
        # Update hearts display
        self.hearts_text.set_text(f"{self.game_state.hearts} Hearts")
        
        # Update petal particle system
        self.petal_system.update(dt)
        
        return None
    
    def draw(self):
        """Draw the menu"""
        # Background
        self.screen.fill((245, 222, 179))  # Wheat color
        
        # Draw decorative elements
        pygame.draw.rect(self.screen, (210, 180, 140), (0, 0, self.width, 100))
        pygame.draw.rect(self.screen, (210, 180, 140), 
                        (0, self.height - 50, self.width, 50))
        
        # Draw title and subtitle
        self.title.draw(self.screen, center=True)
        self.subtitle.draw(self.screen, center=True)
        
        # Draw buttons
        self.play_button.draw(self.screen)
        self.stats_button.draw(self.screen)
        self.quit_button.draw(self.screen)
        
        # Draw hearts
        self.hearts_text.draw(self.screen)
        
        # Draw mute button
        mute_color = (150, 150, 150) if not self.sound_manager.music_enabled else (200, 200, 200)
        pygame.draw.rect(self.screen, mute_color, self.mute_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, (100, 100, 100), self.mute_button_rect, 2, border_radius=5)
        
        mute_icon = "🔇" if not self.sound_manager.music_enabled else "🔊"
        emoji = load_emoji(mute_icon, size=24)
        self.screen.blit(emoji, (self.mute_button_rect.centerx - 12, self.mute_button_rect.centery - 12))
        
        # Draw credits
        Text.draw_text(self.screen, "Made with love for someone special", 
                      self.width // 2, self.height - 20, 
                      font_size=24, color=(100, 100, 100), center=True)

        # Draw falling petals (behind UI)
        self.petal_system.draw(self.screen)
        