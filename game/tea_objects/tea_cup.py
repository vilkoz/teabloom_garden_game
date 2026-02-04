"""Tea cup - small serving cup"""
import pygame


class TeaCup:
    """Represents a small tea cup"""
    def __init__(self, position, index, sprite_loader):
        self.base_position = position
        self.position = list(position)
        self.index = index
        self.tea_data = None
        self.dragging = False
        self.radius = 20
        self.sprite_loader = sprite_loader
        
    def fill(self, tea_data):
        if self.tea_data is None:
            self.tea_data = tea_data
            return True
        return False
    
    def empty(self):
        tea_data = self.tea_data
        self.tea_data = None
        return tea_data
    
    def draw(self, screen):
        x, y = int(self.position[0]), int(self.position[1])
        
        # Get appropriate sprite
        sprite_variant = "empty" if self.tea_data is None else "filled"
        sprite = self.sprite_loader.get_sprite('teacup', sprite_variant) if self.sprite_loader else None
        
        if sprite:
            sprite_rect = sprite.get_rect(center=(x, y))
            screen.blit(sprite, sprite_rect)
        else:
            # Fallback rendering
            color = (255, 255, 255) if self.tea_data is None else self.tea_data.get('color', (180, 120, 80))
            pygame.draw.circle(screen, color, (x, y), self.radius)
            pygame.draw.circle(screen, (80, 60, 40), (x, y), self.radius, 2)
            
            if self.tea_data:
                pygame.draw.circle(screen, self.tea_data.get('color', (180, 120, 80)), (x, y), self.radius - 5)
    
    def contains_point(self, point):
        dx = point[0] - self.position[0]
        dy = point[1] - self.position[1]
        return dx*dx + dy*dy <= self.radius*self.radius
    
    def snap_back(self):
        self.position = list(self.base_position)
