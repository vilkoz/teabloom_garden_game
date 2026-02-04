"""Progress bar component"""
import pygame


class ProgressBar:
    """A simple progress bar component"""
    
    def __init__(self, x, y, width, height, max_value=100, 
                 bg_color=(100, 100, 100), fg_color=(0, 255, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.max_value = max_value
        self.current_value = 0
        self.bg_color = bg_color
        self.fg_color = fg_color
    
    def set_value(self, value):
        """Set the current value of the progress bar"""
        self.current_value = max(0, min(value, self.max_value))
    
    def set_max_value(self, max_value):
        """Set the maximum value"""
        self.max_value = max_value
    
    def get_progress(self):
        """Get progress as a ratio (0.0 to 1.0)"""
        if self.max_value == 0:
            return 0.0
        return self.current_value / self.max_value
    
    def draw(self, screen, show_text=False):
        """Draw the progress bar"""
        # Draw background
        pygame.draw.rect(screen, self.bg_color, self.rect)
        
        # Draw progress
        progress = self.get_progress()
        progress_width = int(self.rect.width * progress)
        progress_rect = pygame.Rect(self.rect.x, self.rect.y, 
                                    progress_width, self.rect.height)
        pygame.draw.rect(screen, self.fg_color, progress_rect)
        
        # Draw border
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        
        # Draw text if requested
        if show_text:
            font = pygame.font.Font(None, 24)
            text = f"{int(self.current_value)}/{int(self.max_value)}"
            text_surface = font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)
