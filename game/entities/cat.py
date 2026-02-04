"""Cat class for the game"""
import pygame
import json
import random
from pathlib import Path


class Cat:
    """Represents a cat visitor in the game"""
    
    # Cat states
    STATE_ARRIVING = "arriving"
    STATE_WAITING = "waiting"
    STATE_HAPPY = "happy"
    STATE_DISAPPOINTED = "disappointed"
    STATE_LEAVING = "leaving"
    
    def __init__(self, cat_data):
        self.id = cat_data['id']
        self.name = cat_data['name']
        self.description = cat_data['description']
        self.personality = cat_data['personality']
        self.favorite_tea = cat_data['favorite_tea']
        self.unlocked = cat_data['unlocked']
        self.color = tuple(cat_data['color'])
        
        # State
        self.state = self.STATE_ARRIVING
        self.wait_timer = 0.0
        self.max_wait_time = 30.0  # 30 seconds before leaving
        self.animation_timer = 0.0
        
        # Position
        self.position = (0, 0)
        self.target_position = (0, 0)
        
        # Visual
        self.surface = None
        self.thought_bubble = None
        self._create_surface()
    
    def _create_surface(self):
        """Create a simple visual representation of the cat"""
        self.surface = pygame.Surface((80, 80), pygame.SRCALPHA)
        
        # Draw cat body (circle)
        pygame.draw.circle(self.surface, self.color, (40, 50), 30)
        
        # Draw cat head (circle)
        pygame.draw.circle(self.surface, self.color, (40, 30), 25)
        
        # Draw ears (triangles)
        pygame.draw.polygon(self.surface, self.color, 
                          [(25, 20), (20, 5), (30, 15)])
        pygame.draw.polygon(self.surface, self.color, 
                          [(55, 20), (50, 15), (60, 5)])
        
        # Draw eyes
        pygame.draw.circle(self.surface, (0, 0, 0), (32, 28), 4)
        pygame.draw.circle(self.surface, (0, 0, 0), (48, 28), 4)
        pygame.draw.circle(self.surface, (255, 255, 255), (33, 27), 2)
        pygame.draw.circle(self.surface, (255, 255, 255), (49, 27), 2)
        
        # Draw nose
        pygame.draw.circle(self.surface, (255, 192, 203), (40, 35), 3)
        
        # Draw whiskers
        pygame.draw.line(self.surface, (0, 0, 0), (20, 35), (5, 33), 1)
        pygame.draw.line(self.surface, (0, 0, 0), (20, 37), (5, 40), 1)
        pygame.draw.line(self.surface, (0, 0, 0), (60, 35), (75, 33), 1)
        pygame.draw.line(self.surface, (0, 0, 0), (60, 37), (75, 40), 1)
    
    def _create_thought_bubble(self, tea_name):
        """Create thought bubble showing desired tea"""
        self.thought_bubble = pygame.Surface((100, 60), pygame.SRCALPHA)
        
        # Draw bubble
        pygame.draw.ellipse(self.thought_bubble, (255, 255, 255), (10, 10, 80, 40))
        pygame.draw.ellipse(self.thought_bubble, (0, 0, 0), (10, 10, 80, 40), 2)
        
        # Draw bubble tail
        pygame.draw.circle(self.thought_bubble, (255, 255, 255), (20, 48), 8)
        pygame.draw.circle(self.thought_bubble, (0, 0, 0), (20, 48), 8, 2)
        pygame.draw.circle(self.thought_bubble, (255, 255, 255), (15, 55), 5)
        pygame.draw.circle(self.thought_bubble, (0, 0, 0), (15, 55), 5, 2)
        
        # Draw tea cup icon
        pygame.draw.ellipse(self.thought_bubble, (144, 238, 144), (35, 20, 30, 25))
        pygame.draw.ellipse(self.thought_bubble, (0, 0, 0), (35, 20, 30, 25), 2)
    
    def arrive(self, position):
        """Cat arrives at a position"""
        self.position = list(position)
        self.target_position = position
        self.state = self.STATE_ARRIVING
        self.animation_timer = 0.0
    
    def request_tea(self, tea_id):
        """Cat requests their favorite tea"""
        self.state = self.STATE_WAITING
        self.wait_timer = 0.0
        self._create_thought_bubble(tea_id)
    
    def receive_tea(self, tea_id):
        """Cat receives tea and reacts"""
        if tea_id == self.favorite_tea:
            self.state = self.STATE_HAPPY
            self.animation_timer = 0.0
            return self.get_heart_value()
        else:
            self.state = self.STATE_DISAPPOINTED
            self.animation_timer = 0.0
            return 0
    
    def leave(self):
        """Cat leaves the garden"""
        self.state = self.STATE_LEAVING
        self.animation_timer = 0.0
    
    def get_heart_value(self):
        """Get the number of hearts this cat gives"""
        # Base value is 1, can be increased with combos
        return 1
    
    def update(self, dt):
        """Update cat state and animations"""
        self.animation_timer += dt
        
        if self.state == self.STATE_ARRIVING:
            if self.animation_timer >= 0.5:
                self.request_tea(self.favorite_tea)
        
        elif self.state == self.STATE_WAITING:
            self.wait_timer += dt
            if self.wait_timer >= self.max_wait_time:
                self.leave()
        
        elif self.state in [self.STATE_HAPPY, self.STATE_DISAPPOINTED]:
            if self.animation_timer >= 2.0:
                self.leave()
        
        elif self.state == self.STATE_LEAVING:
            if self.animation_timer >= 1.0:
                return True  # Signal that cat can be removed
        
        return False
    
    def draw(self, screen):
        """Draw the cat"""
        if self.surface:
            screen.blit(self.surface, self.position)
        
        # Draw thought bubble if waiting
        if self.state == self.STATE_WAITING and self.thought_bubble:
            bubble_pos = (self.position[0] - 10, self.position[1] - 70)
            screen.blit(self.thought_bubble, bubble_pos)
        
        # Draw emotion indicator
        if self.state == self.STATE_HAPPY:
            # Draw hearts
            heart_offset = int(abs(pygame.math.Vector2(0, -10 * (self.animation_timer % 1.0)).y))
            heart_pos = (self.position[0] + 30, self.position[1] - heart_offset)
            pygame.draw.circle(screen, (255, 0, 127), heart_pos, 8)
            pygame.draw.circle(screen, (255, 0, 127), (heart_pos[0] + 10, heart_pos[1]), 8)
            pygame.draw.polygon(screen, (255, 0, 127), [
                (heart_pos[0] - 8, heart_pos[1] + 4),
                (heart_pos[0] + 9, heart_pos[1] + 20),
                (heart_pos[0] + 18, heart_pos[1] + 4)
            ])
        
        elif self.state == self.STATE_DISAPPOINTED:
            # Draw sad face
            font = pygame.font.Font(None, 36)
            sad_text = font.render("...", True, (100, 100, 100))
            screen.blit(sad_text, (self.position[0] + 20, self.position[1] - 20))
    
    def collides_with(self, pos):
        """Check if a position collides with this cat"""
        x, y = self.position
        px, py = pos
        return x <= px <= x + 80 and y <= py <= y + 80


def load_cats():
    """Load all cat data from JSON file"""
    data_path = Path(__file__).parent.parent.parent / "data" / "cats_data.json"
    with open(data_path, 'r') as f:
        data = json.load(f)
    
    cats_data = []
    for cat_data in data['cats']:
        cats_data.append(cat_data)
    
    return cats_data


def get_random_unlocked_cat(cats_data):
    """Get a random cat that is unlocked"""
    unlocked_cats = [cat for cat in cats_data if cat['unlocked']]
    if unlocked_cats:
        return Cat(random.choice(unlocked_cats))
    return None
