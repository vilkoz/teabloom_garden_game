"""Statistics scene"""
import pygame
from game.ui.button import Button
from game.ui.text import Text


class StatsScene:
    """Statistics and achievements scene"""
    
    def __init__(self, screen, game_state):
        self.screen = screen
        self.game_state = game_state
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Back button
        self.back_button = Button(self.width // 2 - 100, self.height - 80, 
                                  200, 60, "Back", color=(200, 200, 200))
    
    def handle_event(self, event):
        """Handle input events"""
        if event.type == pygame.QUIT:
            return "quit"
        
        return None
    
    def update(self, dt):
        """Update scene"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        if self.back_button.update(mouse_pos, mouse_pressed):
            return "menu"
        
        return None
    
    def draw(self):
        """Draw the statistics"""
        # Background
        self.screen.fill((245, 245, 220))
        
        # Title
        Text.draw_text(self.screen, "Statistics", self.width // 2, 50, 
                      font_size=64, color=(139, 69, 19), center=True)
        
        # Stats
        stats = self.game_state.statistics
        y_offset = 150
        line_height = 40
        
        stat_lines = [
            f"Total Hearts Earned: {stats['total_hearts']}",
            f"Current Hearts: {self.game_state.hearts}",
            f"",
            f"Teas Served: {stats['teas_served']}",
            f"Cats Satisfied: {stats['cats_satisfied']} 😺",
            f"Cats Disappointed: {stats['cats_disappointed']} 😿",
            f"",
            f"Correct Serves: {stats['correct_serves']}",
            f"Wrong Serves: {stats['wrong_serves']}",
            f"",
            f"Best Combo: {self.game_state.best_combo}",
            f"Current Combo: {self.game_state.current_combo}",
            f"",
            f"Play Time: {int(stats['play_time'] // 60)}m {int(stats['play_time'] % 60)}s",
        ]
        
        for i, line in enumerate(stat_lines):
            if line:  # Skip empty lines
                Text.draw_text(self.screen, line, self.width // 2, 
                             y_offset + i * line_height, 
                             font_size=32, color=(50, 50, 50), center=True)
        
        # Draw back button
        self.back_button.draw(self.screen)
