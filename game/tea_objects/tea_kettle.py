"""Tea kettle - gaiwan for brewing"""
import pygame
import math
from typing import Any


class TeaKettle:
    """Represents the tea kettle on the cha ban"""
    STATE_EMPTY = "empty"
    STATE_HAS_TEA = "has_tea"
    STATE_BREWING = "brewing"
    STATE_READY = "ready"
    
    def __init__(self, position, sprite_loader):
        self.base_position = position
        self.position = list(position)
        self.state = self.STATE_EMPTY
        self.tea_data: None | dict[Any, Any] = None
        self.brew_timer = 0
        self.brew_duration = 0
        self.width = 120
        self.height = 120
        self.sprite_loader = sprite_loader
        self.is_pouring = False
        self.pouring_timer = 0
        self.pouring_duration = 800  # 800ms pour animation
        self.pour_rotation = 0  # Rotation angle when pouring
        self.should_snap_back_after_pour = False
        self.pour_target_position = None  # Target to pour into
        
    def add_tea(self, tea_data):
        if self.state == self.STATE_EMPTY:
            self.state = self.STATE_HAS_TEA
            self.tea_data = tea_data
            return True
        return False
    
    def add_water(self):
        if self.state == self.STATE_HAS_TEA:
            self.state = self.STATE_BREWING
            self.brew_duration = self.tea_data['brew_time'] if self.tea_data is not None else 0  # Keep in seconds
            self.brew_timer = 0
            return True
        return False
    
    def update(self, dt):
        if self.state == self.STATE_BREWING:
            self.brew_timer += dt
            if self.brew_timer >= self.brew_duration:
                self.state = self.STATE_READY
        
        # Handle pouring animation with rotation
        if self.is_pouring:
            self.pouring_timer += dt
            # Calculate rotation angle (0 to 25 degrees)
            progress = min(1.0, self.pouring_timer / self.pouring_duration)
            self.pour_rotation = int(25 * progress)
            
            if self.pouring_timer >= self.pouring_duration:
                self.is_pouring = False
                self.pouring_timer = 0
                self.pour_rotation = 0
                # Snap back after animation completes
                if self.should_snap_back_after_pour:
                    self.snap_back()
                    self.should_snap_back_after_pour = False
    
    def pour_to_cha_hai(self, snap_back_after=False, target_position=None):
        if self.state == self.STATE_READY:
            self.is_pouring = True
            self.pouring_timer = 0
            self.pour_rotation = 0
            self.should_snap_back_after_pour = snap_back_after
            self.pour_target_position = target_position
            
            # Position kettle above and to the left of target when pouring
            if target_position:
                self.position = [target_position[0] - 50, target_position[1] - 100]
            
            tea_data = self.tea_data
            self.reset()
            return tea_data
        return None
    
    def start_pouring(self, target_position=None):
        """Start the pouring rotation animation preview"""
        if self.state == self.STATE_READY:
            self.is_pouring = True
            self.pouring_timer = 0
            self.pour_rotation = 0
            self.pour_target_position = target_position
            
            # Position kettle above and to the left of target when pouring
            if target_position:
                self.position = [target_position[0] - 50, target_position[1] - 100]
    
    def reset(self):
        self.state = self.STATE_EMPTY
        self.tea_data = None
        self.brew_timer = 0
        self.brew_duration = 0
    
    def snap_back(self):
        """Return to base position"""
        self.position = list(self.base_position)
    
    def get_brew_progress(self):
        if self.state == self.STATE_BREWING and self.brew_duration > 0:
            return min(1.0, self.brew_timer / self.brew_duration)
        return 0
    
    def draw(self, screen):
        x, y = self.position
        
        # Map state to sprite variant
        sprite_variant = None
        if self.state == self.STATE_EMPTY:
            sprite_variant = "empty"
        elif self.state == self.STATE_HAS_TEA:
            sprite_variant = "tea_leaves"
        elif self.state == self.STATE_BREWING:
            sprite_variant = "brewing"
        elif self.state == self.STATE_READY:
            sprite_variant = "ready"
        
        # Try to get sprite
        sprite = self.sprite_loader.get_sprite('gaiwan', sprite_variant) if self.sprite_loader else None
        
        if sprite:
            # Apply rotation if pouring
            if self.is_pouring and self.pour_rotation > 0:
                rotated_sprite = pygame.transform.rotate(sprite, -self.pour_rotation)
                sprite_rect = rotated_sprite.get_rect(center=(x, y))
                screen.blit(rotated_sprite, sprite_rect)
            else:
                sprite_rect = sprite.get_rect(center=(x, y))
                screen.blit(sprite, sprite_rect)
        else:
            # Fallback to colored shapes
            if self.state == self.STATE_EMPTY:
                color = (200, 200, 200)
            elif self.state == self.STATE_HAS_TEA:
                color = self.tea_data.get('color', (100, 150, 100))
            elif self.state == self.STATE_BREWING:
                color = (180, 150, 100)
            else:  # READY
                color = (255, 215, 0)
            
            pygame.draw.rect(screen, color, (x - 40, y - 40, 80, 80), border_radius=10)
            pygame.draw.rect(screen, (80, 60, 40), (x - 40, y - 40, 80, 80), 3, border_radius=10)
            pygame.draw.circle(screen, color, (x + 45, y), 10)
            pygame.draw.arc(screen, (80, 60, 40), (x - 60, y - 30, 30, 60), 0, math.pi, 3)
        
        # Draw state text below sprite
        font = pygame.font.Font(None, 16)
        if self.state == self.STATE_EMPTY:
            text = "Empty"
        elif self.state == self.STATE_HAS_TEA:
            text = "Add ♨"
        elif self.state == self.STATE_BREWING:
            progress = int(self.get_brew_progress() * 100)
            text = f"{progress}%"
        elif self.state == self.STATE_READY:
            text = "Ready!"
        else:
            text = ""
        
        if text:
            text_surface = font.render(text, True, (50, 50, 50))
            text_rect = text_surface.get_rect(center=(x, y + 70))
            bg_rect = text_rect.inflate(6, 3)
            pygame.draw.rect(screen, (255, 255, 255), bg_rect, border_radius=3)
            screen.blit(text_surface, text_rect)
    
    def contains_point(self, point):
        x, y = self.position
        return (x - 50 <= point[0] <= x + 50 and y - 50 <= point[1] <= y + 50)
