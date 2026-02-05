"""Tea disk - draggable tea selection"""
import pygame


class TeaDisk:
    """Represents a draggable tea disk in the tea drawer"""
    def __init__(self, tea_data, position, sprite_loader, game_state):
        self.tea_data = tea_data
        self.base_position = position
        self.position = list(position)
        self.dragging = False
        self.radius = 40
        self.sprite_loader = sprite_loader
        self.game_state = game_state
        
    def draw(self, screen):
        x, y = int(self.position[0]), int(self.position[1])
        
        # Try to get sprite for this tea
        tea_id = self.tea_data['id']
        sprite = self.sprite_loader.get_sprite('tea_disks', tea_id) if self.sprite_loader else None
        
        if sprite:
            # Draw sprite centered
            sprite_rect = sprite.get_rect(center=(x, y))
            screen.blit(sprite, sprite_rect)
        else:
            # Fallback to colored circle
            color = self.tea_data.get('color', (100, 150, 100))
            pygame.draw.circle(screen, color, (x, y), self.radius)
            pygame.draw.circle(screen, (80, 60, 40), (x, y), self.radius, 2)
        
        # Draw tea name (shortened)
        font = pygame.font.Font(None, 16)
        name = self.tea_data['name'][:8]
        text_surface = font.render(name, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(x, y - 5))
        
        # Add background for text
        bg_rect = text_rect.inflate(4, 2)
        s = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, 150), s.get_rect(), border_radius=3)
        screen.blit(s, bg_rect)
        screen.blit(text_surface, text_rect)
        
        # Draw brew time
        time_text = f"{self.tea_data['brew_time']//1000}s"
        time_surface = font.render(time_text, True, (255, 255, 200))
        time_rect = time_surface.get_rect(center=(x, y + 10))
        
        bg_rect2 = time_rect.inflate(4, 2)
        s2 = pygame.Surface(bg_rect2.size, pygame.SRCALPHA)
        pygame.draw.rect(s2, (0, 0, 0, 150), s2.get_rect(), border_radius=3)
        screen.blit(s2, bg_rect2)
        screen.blit(time_surface, time_rect)
        
        # Draw lock if not unlocked
        if not self.game_state.is_tea_unlocked(self.tea_data['id']):
            lock_sprite = self.sprite_loader.get_sprite('lock_icon', 'single') if self.sprite_loader else None
            if lock_sprite:
                lock_rect = lock_sprite.get_rect(center=(x, y))
                screen.blit(lock_sprite, lock_rect)
            else:
                s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (0, 0, 0, 150), (self.radius, self.radius), self.radius)
                screen.blit(s, (x - self.radius, y - self.radius))
                
                lock_font = pygame.font.Font(None, 24)
                lock_surface = lock_font.render("LOCKED", True, (255, 200, 0))
                lock_rect = lock_surface.get_rect(center=(x, y))
                screen.blit(lock_surface, lock_rect)
    
    def contains_point(self, point):
        dx = point[0] - self.position[0]
        dy = point[1] - self.position[1]
        return dx*dx + dy*dy <= self.radius*self.radius
    
    def snap_back(self):
        self.position = list(self.base_position)
