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


class ExplosionParticle:
    """Particle that follows a ballistic trajectory given an initial velocity vector.

    Position and velocity are in pixels and pixels/second respectively. Gravity
    is applied to vertical velocity every update. Draws as a simple circle when
    no sprite is available.
    """
    def __init__(self, x, y, vx, vy, color=(255, 100, 120), size=6, lifetime=1200, gravity=600):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color
        self.size = int(size)
        self.lifetime = float(lifetime)
        self.alpha = 255
        self.gravity = float(gravity)

    def update(self, dt):
        """Update position using simple ballistic physics."""
        # dt in ms
        secs = dt / 1000.0
        # integrate velocity
        self.vy += self.gravity * secs
        self.x += self.vx * secs
        self.y += self.vy * secs
        self.lifetime -= dt
        self.alpha = max(0, min(255, int(255 * (self.lifetime / 1000.0))))
        self.variant = random.choice(['small', 'medium', 'large'])
        return self.lifetime > 0

    def draw(self, screen, sprite_loader, sprite_name=None):
        """Draw the explosion particle as a circle (uses sprite if provided).

        Signature matches `Particle.draw` so ParticleSystem can treat both
        uniformly: `particle.draw(screen, sprite_loader, sprite_name)`.
        """
        # If a sprite name is provided and loader available, prefer sprite
        if sprite_loader and sprite_name:
            sprite = sprite_loader.get_sprite(sprite_name, self.variant)
            if sprite:
                sprite_with_alpha = sprite.copy()
                sprite_with_alpha.set_alpha(self.alpha)
                rect = sprite_with_alpha.get_rect(center=(int(self.x), int(self.y)))
                screen.blit(sprite_with_alpha, rect)
                return

        # Fallback: draw a colored circle with alpha
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        surf_col = (*self.color, self.alpha)
        pygame.draw.circle(surf, surf_col, (self.size, self.size), self.size)
        rect = surf.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(surf, rect)


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

    def spawn_explosion(self, position, vector, count=12, spread=0.6, color=(255, 180, 80)):
        """Spawn explosion particles that are thrown with an initial vector.

        - `position`: (x,y) spawn origin in pixels
        - `vector`: (vx, vy) base initial velocity in pixels/second
        - `count`: number of fragments
        - `spread`: randomness multiplier for velocity variation
        - `color`: RGB tuple for fallback drawing
        """
        base_vx, base_vy = vector
        for i in range(count):
            # small random offset from the origin
            ox = position[0] + random.uniform(-6, 6)
            oy = position[1] + random.uniform(-6, 6)

            # perturb the base velocity
            vx = base_vx + random.uniform(-abs(base_vx) * spread, abs(base_vx) * spread) + random.uniform(-120, 120)
            vy = base_vy + random.uniform(-abs(base_vy) * spread, abs(base_vy) * spread) + random.uniform(-120, 120)

            size = random.randint(3, 8)
            lifetime = random.uniform(700, 1400)
            particle = ExplosionParticle(ox, oy, vx, vy, color=color, size=size, lifetime=lifetime)
            # sprite_name None -> fallback circle draw
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
