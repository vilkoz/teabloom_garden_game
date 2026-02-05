"""Tea god figure - for disposing tea and leaves"""
import pygame


class TeaGod:
    """Represents the tea god/tea pet figure on the cha ban"""
    
    STATE_CLEAN = "clean"
    STATE_POURING_TEA = "pouring_tea"
    STATE_DROPPING_LEAVES = "dropping_leaves"
    
    def __init__(self, position, sprite_loader):
        self.position = position
        self.state = self.STATE_CLEAN
        self.width = 80
        self.height = 80
        self.sprite_loader = sprite_loader
        self.animation_timer = 0
        self.animation_duration = 800  # 800ms animation
        self.animation_frame = 1
        
    def update(self, dt):
        """Update animation"""
        if self.state != self.STATE_CLEAN:
            self.animation_timer += dt
            
            # Toggle between frame 1 and 2
            if self.animation_timer >= self.animation_duration / 2:
                self.animation_frame = 2
            else:
                self.animation_frame = 1
            
            # Reset to clean after animation completes
            if self.animation_timer >= self.animation_duration:
                self.state = self.STATE_CLEAN
                self.animation_timer = 0
                self.animation_frame = 1
    
    def receive_tea(self):
        """Receive poured tea"""
        self.state = self.STATE_POURING_TEA
        self.animation_timer = 0
        self.animation_frame = 1
        return True
    
    def receive_leaves(self):
        """Receive tea leaves"""
        self.state = self.STATE_DROPPING_LEAVES
        self.animation_timer = 0
        self.animation_frame = 1
        return True
    
    def draw(self, screen):
        x, y = self.position
        
        # Map state to sprite variant
        sprite_variant = None
        if self.state == self.STATE_CLEAN:
            sprite_variant = "clean"
        elif self.state == self.STATE_POURING_TEA:
            sprite_variant = f"pouring_tea_{self.animation_frame}"
        elif self.state == self.STATE_DROPPING_LEAVES:
            sprite_variant = f"dropping_leaves_{self.animation_frame}"
        
        # Try to get sprite
        sprite = self.sprite_loader.get_sprite('tea_god', sprite_variant) if self.sprite_loader else None
        
        if sprite:
            sprite_rect = sprite.get_rect(center=(x, y))
            screen.blit(sprite, sprite_rect)
        else:
            # Fallback rendering
            color = (139, 119, 101)  # Stone color
            if self.state == self.STATE_POURING_TEA:
                color = (180, 140, 100)  # Wet stone
            elif self.state == self.STATE_DROPPING_LEAVES:
                color = (100, 140, 100)  # Leaves on stone
            
            pygame.draw.ellipse(screen, color, (x - 30, y - 40, 60, 80))
            pygame.draw.ellipse(screen, (80, 60, 40), (x - 30, y - 40, 60, 80), 2)
        
        # Draw label below
        font = pygame.font.Font(None, 14)
        text = "Tea God"
        text_surface = font.render(text, True, (100, 70, 50))
        text_rect = text_surface.get_rect(center=(x, y + 50))
        bg_rect = text_rect.inflate(6, 3)
        pygame.draw.rect(screen, (255, 255, 255), bg_rect, border_radius=3)
        screen.blit(text_surface, text_rect)
    
    def contains_point(self, point):
        x, y = self.position
        return (x - 40 <= point[0] <= x + 40 and y - 40 <= point[1] <= y + 40)
