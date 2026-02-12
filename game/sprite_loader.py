"""Sprite loader for grid-based sprite sheets"""
import pygame
import os
from pathlib import Path
from .packaging import resource_path


class SpriteLoader:
    """Loads and manages sprite sheets from grid images"""
    
    def __init__(self, assets_dir="assets/images/grids"):
        # Resolve assets directory for development and PyInstaller bundles
        try:
            from .packaging import resource_path
            import os
            if os.path.isabs(assets_dir):
                self.assets_dir = Path(assets_dir)
            else:
                self.assets_dir = Path(resource_path(assets_dir))
        except Exception:
            self.assets_dir = Path(assets_dir)
        self.sprites = {}
        self.fallback_surfaces = {}
        
    def load_grid(self, entity_name, variants, grid_cols=None, grid_rows=None, sprite_size=(100, 100), render_size=None, border_offset=(0, 0), grid_offset=(0, 0)):
        """
        Load a grid sprite sheet and extract individual sprites
        
        Args:
            entity_name: Name of the entity (e.g., 'mimi', 'gaiwan')
            variants: List of variant names (e.g., ['normal', 'happy', 'impatient', 'disappointed'])
            grid_cols: Number of columns in the grid (auto-calculated if None)
            grid_rows: Number of rows in the grid (auto-calculated if None)
            sprite_size: Size of each sprite cell for extraction from texture
            render_size: Size of sprite for final rendering (if None, uses sprite_size)
            border_offset: (x, y) offset from the edge of the image before grid starts
            grid_offset: (x, y) spacing between grid cells
        """
        grid_path = self.assets_dir / f"{entity_name}_grid.png"
        
        # Check if file exists
        if not grid_path.exists():
            print(f"⚠️  Grid not found: {grid_path}")
            self._create_fallback_sprites(entity_name, variants, sprite_size, render_size)
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
            
            # Use sprite_size as the cell dimensions for extraction
            cell_width = sprite_size[0]
            cell_height = sprite_size[1]
            
            # Extract each sprite
            if entity_name not in self.sprites:
                self.sprites[entity_name] = {}
            
            for idx, variant in enumerate(variants):
                row = idx // grid_cols
                col = idx % grid_cols
                
                # Extract the sprite from the grid with offsets
                x = border_offset[0] + col * (cell_width + grid_offset[0])
                y = border_offset[1] + row * (cell_height + grid_offset[1])
                
                sprite_surface = pygame.Surface((cell_width, cell_height), pygame.SRCALPHA)
                sprite_surface.blit(grid_image, (0, 0), (x, y, cell_width, cell_height))
                
                # Remove black background (replace with transparency)
                self._remove_black_background(sprite_surface)
                
                # Scale to render size if different from extraction size
                if render_size is not None and render_size != sprite_size:
                    sprite_surface = pygame.transform.smoothscale(sprite_surface, render_size)
                
                # Store the sprite (scaled to render size)
                variant_name = variant.split(":")[0].strip()
                self.sprites[entity_name][variant_name] = sprite_surface
            
            return True
            
        except Exception as e:
            print(f"Error loading grid for '{entity_name}': {e}")
            self._create_fallback_sprites(entity_name, variants, sprite_size, render_size)
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
    
    def _create_fallback_sprites(self, entity_name, variants, sprite_size, render_size=None):
        """Create simple colored rectangles as fallback"""
        if entity_name not in self.sprites:
            self.sprites[entity_name] = {}
        
        # Use render_size if provided, otherwise use sprite_size
        final_size = render_size if render_size is not None else sprite_size
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
        
        # Use render_size if provided, otherwise use sprite_size
        final_size = render_size if render_size is not None else sprite_size
        
        for variant in variants:
            variant_name = variant.split(":")[0].strip()
            surface = pygame.Surface(final_size, pygame.SRCALPHA)
            
            # Draw a simple colored shape
            if entity_name in ['mimi', 'luna', 'tofu', 'ginger', 'petya', 'lapilaps']:
                # Draw circle for cats
                pygame.draw.circle(surface, base_color, 
                                 (final_size[0]//2, final_size[1]//2), 
                                 final_size[0]//3)
            else:
                # Draw rectangle for items
                pygame.draw.rect(surface, base_color, 
                               (10, 10, final_size[0]-20, final_size[1]-20),
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
        _sprite_loader = SpriteLoader(resource_path("assets/images/grids"))
    return _sprite_loader


def load_all_game_sprites(message_callback=None):
    """Load all sprites needed for the game from sprites_config.json
    
    Args:
        message_callback: Optional callback function to receive progress messages
    """
    import json
    from pathlib import Path
    
    loader = get_sprite_loader()
    
    # Load sprite configuration
    config_path = Path(resource_path("data/sprites_config.json"))
    try:
        with open(config_path, 'r') as f:
            sprites = json.load(f)
    except FileNotFoundError:
        error_msg = f"❌ Error: Configuration file not found: {config_path}"
        print(error_msg)
        if message_callback:
            message_callback(error_msg)
        return loader
    
    # Load all sprites from configuration
    for sprite_config in sprites:
        loader.load_grid(
            sprite_config['name'],
            sprite_config['variants'],
            grid_cols=sprite_config['grid_cols'],
            grid_rows=sprite_config['grid_rows'],
            sprite_size=tuple(sprite_config['sprite_size']),
            render_size=tuple(sprite_config.get('render_size', sprite_config['sprite_size'])),
            border_offset=tuple(sprite_config.get('border_offset', [0, 0])),
            grid_offset=tuple(sprite_config.get('grid_offset', [0, 0]))
        )
        msg = f"Loaded {len(sprite_config['variants'])} sprites for '{sprite_config['name']}'"
        print(msg)
        if message_callback:
            message_callback(msg)
    
    success_msg = "All sprite loading complete!"
    print(f"\n{success_msg}")
    if message_callback:
        message_callback("")
        message_callback(success_msg)
    
    return loader
