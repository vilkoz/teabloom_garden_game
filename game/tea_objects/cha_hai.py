"""Cha hai - fairness cup"""
import pygame
import math


class ChaHai:
    """Represents the fairness cup"""
    def __init__(self, position, sprite_loader):
        self.position = position
        self.tea_data = None
        self.width = 90
        self.height = 90
        self.sprite_loader = sprite_loader
        
    def pour_from_kettle(self, tea_data):
        if self.tea_data is None:
            self.tea_data = tea_data
            return True
        return False
    
    def pour_to_cup(self):
        if self.tea_data:
            tea_data = self.tea_data
            self.tea_data = None
            return tea_data
        return None
    
    def draw(self, screen):
        x, y = self.position
        
        # Get appropriate sprite
        sprite_variant = "empty" if self.tea_data is None else "filled"
        sprite = self.sprite_loader.get_sprite('chahai', sprite_variant) if self.sprite_loader else None
        
        if sprite:
            sprite_rect = sprite.get_rect(center=(x, y))
            screen.blit(sprite, sprite_rect)
            
            # Label when filled
            if self.tea_data:
                font = pygame.font.Font(None, 14)
                label = font.render("Pour→", True, (50, 50, 50))
                label_rect = label.get_rect(center=(x, y + 50))
                bg_rect = label_rect.inflate(4, 2)
                pygame.draw.rect(screen, (255, 255, 255), bg_rect, border_radius=3)
                screen.blit(label, label_rect)
        else:
            # Fallback rendering
            color = (220, 220, 220) if self.tea_data is None else self.tea_data.get('color', (180, 120, 80))
            pygame.draw.ellipse(screen, color, (x - 30, y - 25, 60, 50))
            pygame.draw.ellipse(screen, (80, 60, 40), (x - 30, y - 25, 60, 50), 2)
            pygame.draw.circle(screen, color, (x + 35, y), 6)
            pygame.draw.arc(screen, (80, 60, 40), (x - 45, y - 15, 20, 30), 0, math.pi, 2)
            
            if self.tea_data:
                font = pygame.font.Font(None, 14)
                label = font.render("Pour→", True, (255, 255, 255))
                label_rect = label.get_rect(center=(x, y))
                screen.blit(label, label_rect)
    
    def contains_point(self, point):
        x, y = self.position
        return (x - 35 <= point[0] <= x + 35 and y - 30 <= point[1] <= y + 30)
