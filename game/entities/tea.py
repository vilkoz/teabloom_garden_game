"""Tea class for the game"""
import pygame
import json
from pathlib import Path


class Tea:
    """Represents a tea type in the game"""
    
    def __init__(self, tea_data):
        self.id = tea_data['id']
        self.name = tea_data['name']
        self.category = tea_data['category']
        self.brew_time = tea_data['brew_time']
        self.heart_value = tea_data['heart_value']
        self.rarity = tea_data['rarity']
        self.unlocked = tea_data['unlocked']
        self.unlock_cost = tea_data['unlock_cost']
        self.color = tuple(tea_data['color'])
        
        # Brewing state
        self.is_brewing = False
        self.brew_timer = 0.0
        self.is_ready = False
        
        # Position and visual
        self.position = (0, 0)
        self.dragging = False
        self.surface = None
        self._create_surface()
    
    def _create_surface(self):
        """Create a simple visual representation of the tea"""
        self.surface = pygame.Surface((60, 60), pygame.SRCALPHA)
        # Draw tea cup
        pygame.draw.ellipse(self.surface, self.color, (10, 10, 40, 40))
        pygame.draw.ellipse(self.surface, (255, 255, 255), (10, 10, 40, 40), 2)
        # Draw handle
        pygame.draw.arc(self.surface, (255, 255, 255), (45, 20, 15, 20), 0, 3.14, 2)
    
    def start_brew(self):
        """Start brewing the tea"""
        if not self.unlocked:
            return False
        self.is_brewing = True
        self.brew_timer = 0.0
        self.is_ready = False
        return True
    
    def update_brew(self, dt):
        """Update the brewing process"""
        if not self.is_brewing:
            return
        
        self.brew_timer += dt
        if self.brew_timer >= self.brew_time:
            self.is_ready = True
            self.is_brewing = False
    
    def serve(self):
        """Serve the tea (reset state)"""
        if not self.is_ready:
            return False
        
        self.is_brewing = False
        self.is_ready = False
        self.brew_timer = 0.0
        return True
    
    def get_brew_progress(self):
        """Get brewing progress (0.0 to 1.0)"""
        if not self.is_brewing:
            return 1.0 if self.is_ready else 0.0
        return min(self.brew_timer / self.brew_time, 1.0)
    
    def draw(self, screen, position=None):
        """Draw the tea cup"""
        if position:
            self.position = position
        
        if self.surface:
            screen.blit(self.surface, self.position)
            
            # Draw brewing progress bar if brewing
            if self.is_brewing:
                progress = self.get_brew_progress()
                bar_width = 60
                bar_height = 5
                bar_x = self.position[0]
                bar_y = self.position[1] + 65
                
                # Background
                pygame.draw.rect(screen, (100, 100, 100), 
                               (bar_x, bar_y, bar_width, bar_height))
                # Progress
                pygame.draw.rect(screen, (0, 255, 0), 
                               (bar_x, bar_y, int(bar_width * progress), bar_height))
            
            # Draw ready indicator
            if self.is_ready:
                pygame.draw.circle(screen, (0, 255, 0), 
                                 (self.position[0] + 50, self.position[1] + 10), 8)
    
    def collides_with(self, pos):
        """Check if a position collides with this tea cup"""
        x, y = self.position
        px, py = pos
        return x <= px <= x + 60 and y <= py <= y + 60


def load_teas():
    """Load all tea data from JSON file"""
    data_path = Path(__file__).parent.parent.parent / "data" / "teas_data.json"
    with open(data_path, 'r') as f:
        data = json.load(f)
    
    teas = []
    for tea_data in data['teas']:
        teas.append(Tea(tea_data))
    
    return teas, data['categories']
