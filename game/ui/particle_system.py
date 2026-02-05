"""Particle system for visual effects"""
import random
import pygame


class Particle:
    """Single particle instance"""
    def __init__(self, x, y, variant, speed, lifetime):
        self.x = x
        self.y = y
        self.variant = variant
        self.speed = speed
        self.lifetime = lifetime
        self.alpha = 255
    
    def update(self, dt):
        """Update particle position and lifetime"""
        self.lifetime -= dt
        self.y -= self.speed * (dt / 1000.0)
        self.alpha = max(0, min(255, int(255 * (self.lifetime / 1000.0))))
        return self.lifetime > 0
    
    def draw(self, screen, sprite_loader, sprite_name):
        """Draw the particle"""
        sprite = sprite_loader.get_sprite(sprite_name, self.variant) if sprite_loader else None
        if sprite:
            sprite_with_alpha = sprite.copy()
            sprite_with_alpha.set_alpha(self.alpha)
            sprite_rect = sprite_with_alpha.get_rect(center=(self.x, self.y))
            screen.blit(sprite_with_alpha, sprite_rect)


class ParticleSystem:
    """Manages all particle effects in the game"""
    def __init__(self, sprite_loader):
        self.sprite_loader = sprite_loader
        self.particles = []
    
    def spawn_hearts(self, position, count=5):
        """Spawn heart particles at the given position"""
        variants = ['small', 'medium', 'large']
        for i in range(count):
            particle = Particle(
                x=position[0] + random.randint(-20, 20),
                y=position[1] + random.randint(-20, 10),
                variant=random.choice(variants),
                speed=random.uniform(20, 50),
                lifetime=random.uniform(800, 1200)
            )
            self.particles.append((particle, 'heart_particles'))
    
    def update(self, dt):
        """Update all particles"""
        for particle, sprite_name in self.particles[:]:
            if not particle.update(dt):
                self.particles.remove((particle, sprite_name))
    
    def draw(self, screen):
        """Draw all particles"""
        for particle, sprite_name in self.particles:
            particle.draw(screen, self.sprite_loader, sprite_name)
