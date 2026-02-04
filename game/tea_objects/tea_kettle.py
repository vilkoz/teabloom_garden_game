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
        self.position = position
        self.state = self.STATE_EMPTY
        self.tea_data: None | dict[Any] = None
        self.brew_timer = 0
        self.brew_duration = 0
        self.width = 120
        self.height = 120
        self.sprite_loader = sprite_loader
        
    def add_tea(self, tea_data):
        if self.state == self.STATE_EMPTY:
            self.state = self.STATE_HAS_TEA
            self.tea_data = tea_data
            return True
        return False
    
    def add_water(self):
        if self.state == self.STATE_HAS_TEA:
            self.state = self.STATE_BREWING
            self.brew_duration = self.tea_data['brew_time']  # Keep in seconds
            self.brew_timer = 0
            return True
        return False
    
    def update(self, dt):
        if self.state == self.STATE_BREWING:
            self.brew_timer += dt
            if self.brew_timer >= self.brew_duration:
                self.state = self.STATE_READY
    
    def pour_to_cha_hai(self):
        if self.state == self.STATE_READY:
            tea_data = self.tea_data
            self.reset()
            return tea_data
        return None
    
    def reset(self):
        self.state = self.STATE_EMPTY
        self.tea_data = None
        self.brew_timer = 0
        self.brew_duration = 0
    
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
