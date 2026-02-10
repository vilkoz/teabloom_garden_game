"""Main menu scene"""
import pygame
import random
from pygame_emojis import load_emoji
from game.ui.button import Button
from game.ui.text import Text
from game.sprite_loader import get_sprite_loader
from game.ui.petal_particle import PetalParticleSystem
from game.sound_manager import get_sound_manager, SoundEffect
from game.ui.procedural_background import ProceduralBackground


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

        # Procedural background
        self.background = ProceduralBackground(self.width, self.height, seed=random.randint(0, 10000))
        
        # Create UI elements
        center_x = self.width // 2

        # Decorative rect height (top and bottom)
        decorative_h = 50

        # Button sizing and spacing requirements
        button_width = 300
        button_height = 60
        spacing = 20  # desired spacing between buttons

        # Prefer using the configured logo sprite for the title; fall back to text
        logo = self.sprite_loader.get_sprite('logo', 'single')
        if logo is not None:
            self.logo_sprite = logo
            logo_h = logo.get_height()
            self.title = None
        else:
            self.logo_sprite = None
            # approximate logo height using font size when sprite missing
            logo_h = 72
            self.title = Text("Tea Garden Cats", center_x, 150, font_size=72, 
                              color=(139, 69, 19), bold=True)

        # Compute vertical layout so that:
        # - spacing between buttons == `spacing`
        # - the gap from top decorative rect to logo, logo to buttons, and buttons to bottom decorative rect are equal
        available_h = self.height - 2 * decorative_h
        buttons_total_h = 3 * button_height + 2 * spacing
        # m is the equal margin (top to logo, between logo and buttons, bottom after buttons)
        m = (available_h - logo_h - buttons_total_h) // 3
        if m < 0:
            m = spacing

        # Positions
        logo_top = decorative_h + m
        self.logo_center_y = int(logo_top + logo_h / 2)

        first_button_y = logo_top + logo_h + m
        button_x = (self.width - button_width) // 2

        self.play_button = Button(button_x, int(first_button_y), button_width, button_height, 
                                  "Play", color=(144, 238, 144))
        self.stats_button = Button(button_x, int(first_button_y + button_height + spacing), button_width, button_height, 
                                   "Statistics", color=(135, 206, 250))
        self.quit_button = Button(button_x, int(first_button_y + 2 * (button_height + spacing)), button_width, button_height, 
                                  "Quit", color=(255, 182, 193))
        
        # Display hearts
        self.hearts_text = Text(f"Hearts: {self.game_state.hearts}", 
                               20, 20, font_size=36, color=(255, 0, 127), bold=True)
        
        # Mute button
        self.mute_button_rect = pygame.Rect(self.width - 60, self.height - 100, 50, 40)
        
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
        # Update procedural background animations
        self.background.update(dt)
        
        return None
    
    def draw(self):
        """Draw the menu"""
        # Background (procedural greenery)
        self.background.draw(self.screen)
        
        # Draw decorative elements
        decorative_color = (235, 226, 217)
        pygame.draw.rect(self.screen, decorative_color, (0, 0, self.width, 50))
        pygame.draw.rect(self.screen, decorative_color, 
                        (0, self.height - 50, self.width, 50))
        
        # Draw title (logo if available) and subtitle
        if getattr(self, 'logo_sprite', None):
            rect = self.logo_sprite.get_rect(center=(self.width // 2, self.logo_center_y))
            self.screen.blit(self.logo_sprite, rect)
        else:
            if getattr(self, 'title', None) is not None:
                self.title.y = self.logo_center_y
                self.title.draw(self.screen, center=True)
        
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
        