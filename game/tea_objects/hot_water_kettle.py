"""Hot water kettle - draggable water source"""
import pygame


class HotWaterKettle:
    """Represents the hot water kettle - always ready"""
    def __init__(self, position, sprite_loader):
        self.base_position = position
        self.position = list(position)
        self.dragging = False
        self.width = 100
        self.height = 100
        self.sprite_loader = sprite_loader
        self.is_pouring = False
        self.pouring_timer = 0
        self.pouring_duration = 800  # 800ms pour animation
        self.should_snap_back_after_pour = False
        self.pour_target_position = None  # Target to pour into
    
    def update(self, dt):
        """Update animation timers"""
        if self.is_pouring:
            self.pouring_timer += dt
            if self.pouring_timer >= self.pouring_duration:
                self.is_pouring = False
                self.pouring_timer = 0
                # Snap back after animation completes
                if self.should_snap_back_after_pour:
                    self.snap_back()
                    self.should_snap_back_after_pour = False
    
    def start_pouring(self, snap_back_after=False, target_position=None):
        """Start the pouring animation"""
        self.is_pouring = True
        self.pouring_timer = 0
        self.should_snap_back_after_pour = snap_back_after
        self.pour_target_position = target_position
        
        # Position kettle above and to the left of target when pouring
        if target_position:
            self.position = [target_position[0] - 50, target_position[1] - 100]
        
    def draw(self, screen):
        x, y = int(self.position[0]), int(self.position[1])
        
        # Try to get sprite - use pouring variant if actively pouring
        sprite_variant = 'pouring' if self.is_pouring else 'ready'
        sprite = self.sprite_loader.get_sprite('kettle', sprite_variant) if self.sprite_loader else None
        
        if sprite:
            sprite_rect = sprite.get_rect(center=(x, y))
            screen.blit(sprite, sprite_rect)
            
            # Draw steam above sprite
            font = pygame.font.Font(None, 20)
            steam_text = font.render("~~~", True, (200, 220, 255))
            steam_rect = steam_text.get_rect(center=(x, y - 60))
            screen.blit(steam_text, steam_rect)
        else:
            # Fallback rendering
            pygame.draw.rect(screen, (100, 100, 120), (x - 35, y - 35, 70, 70), border_radius=8)
            pygame.draw.rect(screen, (60, 60, 80), (x - 35, y - 35, 70, 70), 3, border_radius=8)
            pygame.draw.circle(screen, (100, 100, 120), (x + 40, y), 8)
            
            font = pygame.font.Font(None, 20)
            steam_text = font.render("~~~", True, (200, 220, 255))
            steam_rect = steam_text.get_rect(center=(x, y - 50))
            screen.blit(steam_text, steam_rect)
            
            label_font = pygame.font.Font(None, 14)
            label_text = label_font.render("Hot Water", True, (255, 255, 255))
            label_rect = label_text.get_rect(center=(x, y))
            screen.blit(label_text, label_rect)
    
    def contains_point(self, point):
        x, y = self.position
        return (x - 40 <= point[0] <= x + 40 and y - 40 <= point[1] <= y + 40)
    
    def snap_back(self):
        self.position = list(self.base_position)
