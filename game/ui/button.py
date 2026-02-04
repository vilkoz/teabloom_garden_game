"""UI Button component"""
import pygame


class Button:
    """A clickable button UI component"""
    
    def __init__(self, x, y, width, height, text, color=(100, 200, 100), 
                 hover_color=(120, 220, 120), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.is_pressed = False
        self.font = pygame.font.Font(None, 32)
    
    def update(self, mouse_pos, mouse_pressed):
        """Update button state"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Check for click
        if self.is_hovered and mouse_pressed:
            if not self.is_pressed:
                self.is_pressed = True
                return True  # Button was clicked
        else:
            self.is_pressed = False
        
        return False
    
    def draw(self, screen):
        """Draw the button"""
        # Choose color based on hover state
        current_color = self.hover_color if self.is_hovered else self.color
        
        # Draw button background
        pygame.draw.rect(screen, current_color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        
        # Draw button text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
