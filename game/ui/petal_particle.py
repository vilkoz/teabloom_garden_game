"""Petal particle for falling cherry blossom effect"""
import random
import pygame
from .particle_system import Particle


class PetalParticle(Particle):
    """Cherry blossom petal with 3-stage lifecycle"""
    
    def __init__(self, width, height):
        """Initialize a petal particle
        
        Args:
            width: Screen width for boundary calculations
            height: Screen height for target position
        """
        # Target position on the ground
        target_x = random.randint(50, width - 50)
        target_y = random.randint(height - 150, height - 100)
        
        # Starting position with random offset
        x = target_x + random.randint(-100, 100)
        y = random.randint(-50, -20)
        
        # Select variant
        variants = ['frame1', 'frame2', 'frame3']
        variant = random.choice(variants)
        
        # Initialize base particle
        super().__init__(x, y, variant, random.uniform(30, 60), float('inf'))
        
        # Petal-specific properties
        self.target_x = target_x
        self.target_y = target_y
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-50, 50)
        
        # Lifecycle stage: 'falling', 'resting', 'disappearing'
        self.stage = 'falling'
        self.rest_time = random.uniform(3000, 5000)
        self.fade_timer = 2000
    
    def update(self, dt):
        """Update petal state
        
        Args:
            dt: Delta time in milliseconds
            
        Returns:
            bool: True if particle should continue, False if should be removed
        """
        # Always rotate
        self.rotation += self.rotation_speed * (dt / 1000.0)
        
        if self.stage == 'falling':
            # Move toward target position
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = (dx**2 + dy**2)**0.5
            
            if distance < 5:
                self.stage = 'resting'
                self.x = self.target_x
                self.y = self.target_y
            else:
                # Move toward target
                speed_dt = self.speed * (dt / 1000.0)
                self.x += (dx / distance) * speed_dt
                self.y += (dy / distance) * speed_dt
        
        elif self.stage == 'resting':
            self.rest_time -= dt
            if self.rest_time <= 0:
                self.stage = 'disappearing'
        
        elif self.stage == 'disappearing':
            self.fade_timer -= dt
            self.alpha = max(0, int(255 * (self.fade_timer / 2000)))
            if self.fade_timer <= 0:
                return False
        
        return True
    
    def draw(self, screen, sprite_loader, sprite_name):
        """Draw the petal with rotation
        
        Args:
            screen: Pygame screen surface
            sprite_loader: Sprite loader instance
            sprite_name: Name of sprite to load
        """
        sprite = sprite_loader.get_sprite(sprite_name, self.variant) if sprite_loader else None
        if sprite:
            # Rotate and apply alpha
            rotated_sprite = pygame.transform.rotate(sprite, self.rotation)
            rotated_sprite.set_alpha(self.alpha)
            sprite_rect = rotated_sprite.get_rect(center=(self.x, self.y))
            screen.blit(rotated_sprite, sprite_rect)


class PetalParticleSystem:
    """Manages multiple falling cherry blossom petals"""
    
    def __init__(self, width, height, sprite_loader):
        """Initialize petal particle system
        
        Args:
            width: Screen width
            height: Screen height
            sprite_loader: Sprite loader instance
        """
        self.width = width
        self.height = height
        self.sprite_loader = sprite_loader
        self.particles = []
        self.spawn_timer = 0
        self.spawn_interval = 300  # Spawn petal every 300ms
        self.sprite_name = 'petals'
    
    def spawn_petal(self):
        """Spawn a single petal particle"""
        petal = PetalParticle(self.width, self.height)
        self.particles.append(petal)
    
    def update(self, dt):
        """Update all petals
        
        Args:
            dt: Delta time in milliseconds
        """
        # Spawn new petals
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_petal()
        
        # Update existing petals
        for petal in self.particles[:]:
            if not petal.update(dt):
                self.particles.remove(petal)
    
    def draw(self, screen):
        """Draw all petals
        
        Args:
            screen: Pygame screen surface
        """
        for petal in self.particles:
            petal.draw(screen, self.sprite_loader, self.sprite_name)

