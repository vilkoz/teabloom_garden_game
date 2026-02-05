"""Tooltip component for displaying information on hover"""
import pygame


class Tooltip:
    """A tooltip that can be displayed on mouse hover"""
    
    def __init__(self, max_width=300):
        self.max_width = max_width
        self.padding = 10
        self.line_spacing = 5
        self.font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 24)
        self.title_font.set_bold(True)
        self.background_color = (50, 50, 50, 230)  # Semi-transparent black
        self.text_color = (255, 255, 255)
        self.title_color = (255, 220, 100)
        self.border_color = (100, 100, 100)
        
    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = font.render(test_line, True, self.text_color)
            if test_surface.get_width() <= max_width - 2 * self.padding:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def draw(self, screen, mouse_pos, title, lines_dict):
        """
        Draw tooltip at mouse position
        
        Args:
            screen: pygame surface to draw on
            mouse_pos: tuple (x, y) of mouse position
            title: string for the title (cat name)
            lines_dict: dict with keys as labels and values as content
        """
        # Prepare all text surfaces
        title_surface = self.title_font.render(title, True, self.title_color)
        
        text_surfaces = []
        max_line_width = title_surface.get_width()
        
        for label, content in lines_dict.items():
            # Wrap content if needed
            wrapped_lines = self._wrap_text(f"{label}: {content}", self.font, self.max_width)
            for line in wrapped_lines:
                surface = self.font.render(line, True, self.text_color)
                text_surfaces.append(surface)
                max_line_width = max(max_line_width, surface.get_width())
        
        # Calculate tooltip dimensions
        tooltip_width = min(max_line_width + 2 * self.padding, self.max_width)
        line_height = self.font.get_height()
        title_height = self.title_font.get_height()
        tooltip_height = (title_height + self.line_spacing * 2 + 
                         len(text_surfaces) * (line_height + self.line_spacing) + 
                         self.padding * 2)
        
        # Position tooltip (offset from mouse to avoid cursor overlap)
        x = mouse_pos[0] + 15
        y = mouse_pos[1] + 15
        
        # Keep tooltip on screen
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        if x + tooltip_width > screen_width:
            x = mouse_pos[0] - tooltip_width - 15
        if y + tooltip_height > screen_height:
            y = mouse_pos[1] - tooltip_height - 15
        
        # Create tooltip surface with alpha
        tooltip_surface = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
        
        # Draw background with border
        pygame.draw.rect(tooltip_surface, self.background_color, 
                        (0, 0, tooltip_width, tooltip_height), border_radius=5)
        pygame.draw.rect(tooltip_surface, self.border_color, 
                        (0, 0, tooltip_width, tooltip_height), 2, border_radius=5)
        
        # Draw title
        current_y = self.padding
        tooltip_surface.blit(title_surface, (self.padding, current_y))
        current_y += title_height + self.line_spacing * 2
        
        # Draw separator line
        pygame.draw.line(tooltip_surface, self.border_color, 
                        (self.padding, current_y - self.line_spacing), 
                        (tooltip_width - self.padding, current_y - self.line_spacing), 1)
        
        # Draw text lines
        for text_surface in text_surfaces:
            tooltip_surface.blit(text_surface, (self.padding, current_y))
            current_y += line_height + self.line_spacing
        
        # Blit tooltip to screen
        screen.blit(tooltip_surface, (x, y))
