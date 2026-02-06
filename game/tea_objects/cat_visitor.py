"""Cat visitor - customers who want tea"""
import pygame
import math
import random
from datetime import datetime, timedelta
from ..sound_manager import get_sound_manager, SoundEffect


class CatVisitor:
    """Enhanced cat for the visiting area"""
    def __init__(self, cat_data, slot_position, slot_index, sprite_loader, particle_system):
        self.cat_data = cat_data
        self.slot_position = slot_position
        self.slot_index = slot_index
        self.position = list(slot_position)
        self.state = "arriving"
        self.patience = 100
        self.patience_max = 100
        self.waiting_time = 0
        self.waiting_limit = 15000  # 15 seconds
        self.served = False
        self.happiness = 0
        self.animation_timer = 0
        self.sprite_loader = sprite_loader
        self.particle_system = particle_system
        self.sound_manager = get_sound_manager()
        self._leaving_sound_played = False
        
        # Generate random birthday (cat can be 0-15 years old)
        self.birthday = self._generate_random_birthday()
    
    def _generate_random_birthday(self):
        """Generate a random birthday for the cat (0-15 years ago)"""
        today = datetime.now()
        # Random age between 0 and 15 years (in days)
        age_in_days = random.randint(0, 15 * 365)
        birthday = today - timedelta(days=age_in_days)
        # Format as readable string
        return birthday.strftime("%B %d, %Y")
    
    def get_rect(self):
        """Get the collision rect for the cat"""
        x, y = int(self.position[0]), int(self.position[1])
        return pygame.Rect(x - 40, y - 40, 80, 80)
    
    def contains_point(self, point):
        """Check if a point is inside the cat's area"""
        return self.get_rect().collidepoint(point)
        
    def update(self, dt):
        self.animation_timer += dt
        
        if self.state == "arriving":
            # Arrive from right
            target_x = self.slot_position[0]
            if self.position[0] > target_x:
                self.position[0] -= 0.5
            else:
                self.position[0] = target_x
                self.state = "waiting"
        
        elif self.state == "waiting":
            self.waiting_time += dt
            self.patience = max(0, 100 - (self.waiting_time / self.waiting_limit * 100))
            
            if self.patience <= 0:
                self.state = "leaving"
        
        elif self.state == "happy":
            # Wait a bit then leave
            if self.animation_timer > 2000:
                self.state = "leaving"
        
        elif self.state == "disappointed":
            if self.animation_timer > 1500:
                self.state = "leaving"
        
        elif self.state == "leaving":
            if not self._leaving_sound_played:
                self.sound_manager.play_sound(SoundEffect.CAT_LEAVE)
                self._leaving_sound_played = True
            self.position[0] += 3
    
    def receive_tea(self, tea_id):
        if self.served:
            return None
        
        self.served = True
        favorite = self.cat_data.get('favorite_tea', '')
        
        if tea_id == favorite:
            self.state = "happy"
            self.happiness = 100
            self.animation_timer = 0
            return {"match": True, "hearts": 3}
        else:
            self.state = "disappointed"
            self.animation_timer = 0
            return {"match": False, "hearts": 1}
    
    def can_pet(self):
        return self.state == "happy" and self.animation_timer < 2500
    
    def pet(self):
        if self.can_pet():
            self.particle_system.spawn_hearts(self.position, count=5)
            return 1  # Bonus heart
        return 0
    
    def draw(self, screen):
        x, y = int(self.position[0]), int(self.position[1])
        
        # Map game state to sprite variant
        if self.state == "happy":
            sprite_variant = "happy"
        elif self.state == "disappointed":
            sprite_variant = "disappointed"
        elif self.patience < 40:
            sprite_variant = "impatient"
        else:
            sprite_variant = "normal"
        
        # Try to get cat sprite
        cat_id = self.cat_data['id']
        sprite = self.sprite_loader.get_sprite(cat_id, sprite_variant) if self.sprite_loader else None
        
        if sprite:
            # Draw sprite centered
            sprite_rect = sprite.get_rect(center=(x, y))
            screen.blit(sprite, sprite_rect)
        else:
            # Fallback rendering
            cat_color = self.cat_data.get('color', (255, 140, 0))
            pygame.draw.circle(screen, cat_color, (x, y), 35)
            pygame.draw.circle(screen, (50, 50, 50), (x, y), 35, 2)
            
            ear_points_left = [(x - 20, y - 25), (x - 30, y - 45), (x - 10, y - 35)]
            ear_points_right = [(x + 20, y - 25), (x + 30, y - 45), (x + 10, y - 35)]
            pygame.draw.polygon(screen, cat_color, ear_points_left)
            pygame.draw.polygon(screen, cat_color, ear_points_right)
            pygame.draw.polygon(screen, (50, 50, 50), ear_points_left, 2)
            pygame.draw.polygon(screen, (50, 50, 50), ear_points_right, 2)
            
            if self.state == "happy":
                pygame.draw.arc(screen, (50, 50, 50), (x - 20, y - 10, 12, 8), 0, math.pi, 2)
                pygame.draw.arc(screen, (50, 50, 50), (x + 8, y - 10, 12, 8), 0, math.pi, 2)
            else:
                pygame.draw.circle(screen, (255, 255, 255), (x - 12, y - 5), 6)
                pygame.draw.circle(screen, (255, 255, 255), (x + 12, y - 5), 6)
                pygame.draw.circle(screen, (50, 50, 50), (x - 12, y - 5), 3)
                pygame.draw.circle(screen, (50, 50, 50), (x + 12, y - 5), 3)
            
            if self.state == "happy":
                pygame.draw.arc(screen, (50, 50, 50), (x - 8, y + 5, 16, 10), math.pi, 2*math.pi, 2)
            elif self.state == "disappointed":
                pygame.draw.arc(screen, (50, 50, 50), (x - 8, y + 15, 16, 10), 0, math.pi, 2)
        
        # Draw name below
        font = pygame.font.Font(None, 16)
        name_text = font.render(self.cat_data['name'], True, (100, 70, 50))
        name_rect = name_text.get_rect(center=(x, y + 50))
        screen.blit(name_text, name_rect)
        
        # Draw thought bubble with favorite tea
        if self.state == "waiting":
            bubble_x, bubble_y = x + 60, y - 40
            pygame.draw.circle(screen, (255, 255, 255), (bubble_x, bubble_y), 25)
            pygame.draw.circle(screen, (100, 100, 100), (bubble_x, bubble_y), 25, 2)
            pygame.draw.circle(screen, (255, 255, 255), (x + 45, y - 15), 8)
            pygame.draw.circle(screen, (255, 255, 255), (x + 40, y - 5), 5)
            
            # Draw tea emoji in bubble
            bubble_font = pygame.font.Font(None, 28)
            fav_tea_text = bubble_font.render("Tea", True, (100, 150, 100))
            fav_rect = fav_tea_text.get_rect(center=(bubble_x, bubble_y))
            screen.blit(fav_tea_text, fav_rect)
        
        # Draw patience bar
        if self.state == "waiting":
            bar_width = 60
            bar_height = 6
            bar_x = x - bar_width // 2
            bar_y = y + 65
            
            # Background
            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            
            # Patience fill
            patience_width = int(bar_width * (self.patience / 100))
            if self.patience > 60:
                color = (100, 200, 100)
            elif self.patience > 30:
                color = (255, 200, 0)
            else:
                color = (255, 100, 100)
            pygame.draw.rect(screen, color, (bar_x, bar_y, patience_width, bar_height))
    
    def is_off_screen(self):
        return self.position[0] > 850
