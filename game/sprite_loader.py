"""Sprite loader for grid-based sprite sheets"""
import pygame
import os
from pathlib import Path


class SpriteLoader:
    """Loads and manages sprite sheets from grid images"""
    
    def __init__(self, assets_dir="assets/images/grids"):
        self.assets_dir = Path(assets_dir)
        self.sprites = {}
        self.fallback_surfaces = {}
        
    def load_grid(self, entity_name, variants, grid_cols=None, grid_rows=None, sprite_size=(100, 100)):
        """
        Load a grid sprite sheet and extract individual sprites
        
        Args:
            entity_name: Name of the entity (e.g., 'mimi', 'gaiwan')
            variants: List of variant names (e.g., ['normal', 'happy', 'impatient', 'disappointed'])
            grid_cols: Number of columns in the grid (auto-calculated if None)
            grid_rows: Number of rows in the grid (auto-calculated if None)
            sprite_size: Size of each sprite after extraction
        """
        grid_path = self.assets_dir / f"{entity_name}_grid.png"
        
        # Check if file exists
        if not grid_path.exists():
            print(f"⚠️  Grid not found: {grid_path}")
            self._create_fallback_sprites(entity_name, variants, sprite_size)
            return False
        
        try:
            # Load the grid image
            grid_image = pygame.image.load(str(grid_path)).convert_alpha()
            grid_width, grid_height = grid_image.get_size()
            
            # Calculate grid dimensions if not provided
            total_variants = len(variants)
            if grid_cols is None:
                grid_cols = 1
                while grid_cols * grid_cols < total_variants:
                    grid_cols += 1
            if grid_rows is None:
                grid_rows = (total_variants + grid_cols - 1) // grid_cols
            
            # Calculate cell size
            cell_width = grid_width // grid_cols
            cell_height = grid_height // grid_rows
            
            # Extract each sprite
            if entity_name not in self.sprites:
                self.sprites[entity_name] = {}
            
            for idx, variant in enumerate(variants):
                row = idx // grid_cols
                col = idx % grid_cols
                
                # Extract the sprite from the grid
                x = col * cell_width
                y = row * cell_height
                
                sprite_surface = pygame.Surface((cell_width, cell_height), pygame.SRCALPHA)
                sprite_surface.blit(grid_image, (0, 0), (x, y, cell_width, cell_height))
                
                # Remove black background (replace with transparency)
                self._remove_black_background(sprite_surface)
                
                # Scale to desired size
                if (cell_width, cell_height) != sprite_size:
                    sprite_surface = pygame.transform.smoothscale(sprite_surface, sprite_size)
                
                # Store the sprite
                variant_name = variant.split(":")[0].strip()
                self.sprites[entity_name][variant_name] = sprite_surface
                
            print(f"✓ Loaded {len(variants)} sprites for '{entity_name}'")
            return True
            
        except Exception as e:
            print(f"❌ Error loading grid for '{entity_name}': {e}")
            self._create_fallback_sprites(entity_name, variants, sprite_size)
            return False
    
    def _remove_black_background(self, surface):
        """Replace pure black (#000000) with transparency"""
        width, height = surface.get_size()
        for x in range(width):
            for y in range(height):
                color = surface.get_at((x, y))
                # If pixel is pure black or very close to black, make it transparent
                if color.r < 10 and color.g < 10 and color.b < 10:
                    surface.set_at((x, y), (0, 0, 0, 0))
    
    def _create_fallback_sprites(self, entity_name, variants, sprite_size):
        """Create simple colored rectangles as fallback"""
        if entity_name not in self.sprites:
            self.sprites[entity_name] = {}
        
        # Use different colors for different entities
        fallback_colors = {
            'mimi': (255, 165, 0),
            'luna': (50, 50, 50),
            'tofu': (245, 245, 245),
            'ginger': (200, 120, 80),
            'petya': (150, 150, 150),
            'lapilaps': (230, 200, 180),
            'gaiwan': (220, 220, 220),
            'kettle': (100, 100, 120),
            'chahai': (220, 220, 220),
            'teacup': (255, 255, 255),
        }
        
        base_color = fallback_colors.get(entity_name, (200, 200, 200))
        
        for variant in variants:
            variant_name = variant.split(":")[0].strip()
            surface = pygame.Surface(sprite_size, pygame.SRCALPHA)
            
            # Draw a simple colored shape
            if entity_name in ['mimi', 'luna', 'tofu', 'ginger', 'petya', 'lapilaps']:
                # Draw circle for cats
                pygame.draw.circle(surface, base_color, 
                                 (sprite_size[0]//2, sprite_size[1]//2), 
                                 sprite_size[0]//3)
            else:
                # Draw rectangle for items
                pygame.draw.rect(surface, base_color, 
                               (10, 10, sprite_size[0]-20, sprite_size[1]-20),
                               border_radius=5)
            
            self.sprites[entity_name][variant_name] = surface
    
    def get_sprite(self, entity_name, variant_name):
        """Get a specific sprite"""
        if entity_name in self.sprites and variant_name in self.sprites[entity_name]:
            return self.sprites[entity_name][variant_name]
        return None
    
    def has_sprite(self, entity_name, variant_name=None):
        """Check if a sprite exists"""
        if variant_name is None:
            return entity_name in self.sprites
        return entity_name in self.sprites and variant_name in self.sprites[entity_name]


# Global sprite loader instance
_sprite_loader = None

def get_sprite_loader():
    """Get the global sprite loader instance"""
    global _sprite_loader
    if _sprite_loader is None:
        _sprite_loader = SpriteLoader()
    return _sprite_loader


def load_all_game_sprites():
    """Load all sprites needed for the game"""
    loader = get_sprite_loader()
    
    # Cat sprites
    cat_variants = ["normal", "happy", "impatient", "disappointed"]
    for cat in ['mimi', 'luna', 'tofu', 'ginger', 'petya', 'lapilaps']:
        loader.load_grid(cat, cat_variants, grid_cols=2, grid_rows=2, sprite_size=(100, 100))
    
    # Tea equipment
    loader.load_grid('gaiwan', ["empty", "tea_leaves", "with_water", "brewing", "ready"], 
                    grid_cols=3, grid_rows=2, sprite_size=(120, 120))
    loader.load_grid('kettle', ["ready", "pouring"], 
                    grid_cols=2, grid_rows=1, sprite_size=(100, 100))
    loader.load_grid('chahai', ["empty", "filled"], 
                    grid_cols=2, grid_rows=1, sprite_size=(90, 90))
    loader.load_grid('teacup', ["empty", "filled"], 
                    grid_cols=2, grid_rows=1, sprite_size=(40, 40))
    
    # Tea disks
    tea_disk_variants = [
        "jasmine_oolong", "te_guan_yin", "silver_needle", "dan_tsun",
        "violet_ya_bao", "dualist_red", "leach_tears", "golden_monkey"
    ]
    loader.load_grid('tea_disks', tea_disk_variants, 
                    grid_cols=4, grid_rows=2, sprite_size=(80, 80))
    
    # Large assets
    loader.load_grid('cha_ban', ["single"], grid_cols=1, grid_rows=1, sprite_size=(300, 600))
    loader.load_grid('tea_drawer', ["single"], grid_cols=1, grid_rows=1, sprite_size=(800, 150))
    loader.load_grid('border_frame', ["single"], grid_cols=1, grid_rows=1, sprite_size=(1024, 768))
    
    # UI elements
    loader.load_grid('ui_hearts', ["filled", "empty"], grid_cols=2, grid_rows=1, sprite_size=(24, 24))
    loader.load_grid('thought_bubble', ["single"], grid_cols=1, grid_rows=1, sprite_size=(120, 80))
    loader.load_grid('lock_icon', ["single"], grid_cols=1, grid_rows=1, sprite_size=(40, 40))
    
    # Particles
    loader.load_grid('steam_particles', ["frame1", "frame2", "frame3", "frame4"], 
                    grid_cols=2, grid_rows=2, sprite_size=(20, 20))
    loader.load_grid('heart_particles', ["small", "medium", "large"], 
                    grid_cols=3, grid_rows=1, sprite_size=(15, 15))
    loader.load_grid('sparkles', ["frame1", "frame2", "frame3", "frame4"], 
                    grid_cols=2, grid_rows=2, sprite_size=(30, 30))
    loader.load_grid('petals', ["frame1", "frame2", "frame3"], 
                    grid_cols=3, grid_rows=1, sprite_size=(15, 15))
    
    print("\n✅ All sprite loading complete!")
    return loader
