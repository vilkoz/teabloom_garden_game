"""Text rendering component"""
import pygame


class Text:
    """A simple text rendering component"""
    
    def __init__(self, text, x, y, font_size=32, color=(0, 0, 0), bold=False):
        self.text = text
        self.x = x
        self.y = y
        self.font_size = font_size
        self.color = color
        self.bold = bold
        self.font = pygame.font.Font(None, font_size)
        if bold:
            self.font.set_bold(True)
    
    def set_text(self, text):
        """Update the text"""
        self.text = text
    
    def draw(self, screen, center=False):
        """Draw the text"""
        text_surface = self.font.render(str(self.text), True, self.color)
        if center:
            text_rect = text_surface.get_rect(center=(self.x, self.y))
            screen.blit(text_surface, text_rect)
        else:
            screen.blit(text_surface, (self.x, self.y))
    
    @staticmethod
    def draw_text(screen, text, x, y, font_size=32, color=(0, 0, 0), center=False, bold=False):
        """Static method to draw text without creating an object"""
        font = pygame.font.Font(None, font_size)
        if bold:
            font.set_bold(True)
        text_surface = font.render(str(text), True, color)
        if center:
            text_rect = text_surface.get_rect(center=(x, y))
            screen.blit(text_surface, text_rect)
        else:
            screen.blit(text_surface, (x, y))
