"""Sprite Viewer and Configuration Editor"""
import pygame
import json
import sys
from pathlib import Path
from game.sprite_loader import get_sprite_loader, load_all_game_sprites


class SpriteViewer:
    def __init__(self):
        pygame.init()
        
        # Screen setup
        self.width = 1400
        self.height = 900
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Sprite Viewer & Editor")
        
        # Colors
        self.bg_color = (240, 240, 240)
        self.form_bg = (255, 255, 255)
        self.text_color = (50, 50, 50)
        self.button_color = (70, 130, 180)
        self.button_hover = (100, 160, 210)
        self.input_bg = (250, 250, 250)
        self.input_active = (255, 255, 200)
        
        # Fonts
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Load config
        self.config_path = Path("data/sprites_config.json")
        self.sprites_config = self.load_config()
        
        # Load sprites
        self.sprite_loader = get_sprite_loader()
        self.load_all_sprites()
        
        # Scrolling
        self.scroll_offset = 0
        self.scroll_speed = 50
        
        # Editing state
        self.selected_sprite_index = None
        self.editing_field = None
        self.input_text = ""
        self.modified_sprite_indices = set()  # Track which sprites were modified
        self.click_coords = {}  # Track clicked coordinates for each sprite index
        
        # UI elements
        self.scroll_up_btn = pygame.Rect(self.width - 100, 50, 80, 40)
        self.scroll_down_btn = pygame.Rect(self.width - 100, 100, 80, 40)
        self.submit_btn = pygame.Rect(self.width // 2 - 100, self.height - 80, 200, 50)
        
        # Clock
        self.clock = pygame.time.Clock()
        self.running = True
    
    def load_config(self):
        """Load sprite configuration from JSON"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file not found: {self.config_path}")
            return []
    
    def save_config(self):
        """Save sprite configuration to JSON"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.sprites_config, f, indent=2)
            print("Configuration saved successfully!")
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def load_all_sprites(self):
        """Load all sprites using the centralized sprite loader"""
        load_all_game_sprites()
        print(f"Loaded {len(self.sprites_config)} sprite groups")
    
    def reload_sprites(self):
        """Reload only modified sprites after config change"""
        if not self.modified_sprite_indices:
            print("No sprites modified, skipping reload")
            return
        
        print(f"Reloading {len(self.modified_sprite_indices)} modified sprite(s)...")
        
        # Reload only modified sprites
        for idx in self.modified_sprite_indices:
            sprite_config = self.sprites_config[idx]
            
            # Clear only this sprite from cache
            sprite_name = sprite_config['name']
            if sprite_name in self.sprite_loader.sprites:
                del self.sprite_loader.sprites[sprite_name]
            
            # Reload this sprite
            self.sprite_loader.load_grid(
                sprite_config['name'],
                sprite_config['variants'],
                grid_cols=sprite_config['grid_cols'],
                grid_rows=sprite_config['grid_rows'],
                sprite_size=tuple(sprite_config['sprite_size']),
                render_size=tuple(sprite_config.get('render_size', sprite_config['sprite_size'])),
                border_offset=tuple(sprite_config.get('border_offset', [0, 0])),
                grid_offset=tuple(sprite_config.get('grid_offset', [0, 0]))
            )
            print(f"✓ Reloaded {len(sprite_config['variants'])} sprites for '{sprite_config['name']}'")
        
        # Clear modified tracking
        self.modified_sprite_indices.clear()
        print("Reload complete!")
    
    def handle_events(self):
        """Handle pygame events"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Scroll buttons
                    if self.scroll_up_btn.collidepoint(mouse_pos):
                        self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
                    elif self.scroll_down_btn.collidepoint(mouse_pos):
                        max_scroll = max(0, len(self.sprites_config) * 400 - 500)
                        self.scroll_offset = min(max_scroll, self.scroll_offset + self.scroll_speed)
                    
                    # Submit button
                    elif self.submit_btn.collidepoint(mouse_pos):
                        if self.save_config():
                            self.reload_sprites()
                    
                    # Check sprite config rows for editing
                    else:
                        self.check_sprite_click(mouse_pos)
            
            elif event.type == pygame.KEYDOWN:
                if self.editing_field is not None:
                    if event.key == pygame.K_RETURN:
                        self.save_field_edit(reload=True)
                    elif event.key == pygame.K_ESCAPE:
                        self.cancel_field_edit()
                    elif event.key == pygame.K_UP:
                        # Increment value by 1
                        try:
                            current = int(self.input_text)
                            self.input_text = str(current + 1)
                            self.save_field_edit(reload=True)
                        except ValueError:
                            pass
                    elif event.key == pygame.K_DOWN:
                        # Decrement value by 1
                        try:
                            current = int(self.input_text)
                            self.input_text = str(max(0, current - 1))  # Don't go below 0
                            self.save_field_edit(reload=True)
                        except ValueError:
                            pass
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        self.input_text += event.unicode
            
            elif event.type == pygame.MOUSEWHEEL:
                # Mouse wheel scrolling
                self.scroll_offset = max(0, self.scroll_offset - event.y * 30)
                max_scroll = max(0, len(self.sprites_config) * 400 - 500)
                self.scroll_offset = min(max_scroll, self.scroll_offset)
    
    def check_sprite_click(self, mouse_pos):
        """Check if user clicked on a sprite config field or texture"""
        y_start = 120 - self.scroll_offset
        
        for i, sprite_config in enumerate(self.sprites_config):
            row_y = y_start + i * 400
            
            if row_y < -400 or row_y > self.height - 100:
                continue
            
            # Check if clicked on texture (top part, after sprite name)
            texture_rect = pygame.Rect(20, row_y + 40, 200, 200)
            if texture_rect.collidepoint(mouse_pos):
                # Calculate relative coordinates within texture
                rel_x = mouse_pos[0] - texture_rect.x
                rel_y = mouse_pos[1] - texture_rect.y
                
                # Load actual texture to get real dimensions
                texture_path = self.sprite_loader.assets_dir / f"{sprite_config['name']}_grid.png"
                if texture_path.exists():
                    import pygame as pg
                    texture = pg.image.load(str(texture_path))
                    tex_w, tex_h = texture.get_size()
                    
                    # Scale coordinates to actual texture size
                    actual_x = int(rel_x * tex_w / 200)
                    actual_y = int(rel_y * tex_h / 200)
                    
                    self.click_coords[i] = (actual_x, actual_y)
                    print(f"Clicked at texture coordinates: ({actual_x}, {actual_y})")
                return
            
            # Check if clicked on editable fields (moved to bottom part)
            fields = [
                ('grid_cols', pygame.Rect(800, row_y + 280, 60, 30)),
                ('grid_rows', pygame.Rect(900, row_y + 280, 60, 30)),
                ('border_offset_x', pygame.Rect(1000, row_y + 280, 60, 30)),
                ('border_offset_y', pygame.Rect(1100, row_y + 280, 60, 30)),
                ('grid_offset_x', pygame.Rect(1200, row_y + 280, 60, 30)),
                ('grid_offset_y', pygame.Rect(1300, row_y + 280, 60, 30)),
                ('sprite_size_x', pygame.Rect(800, row_y + 330, 60, 30)),
                ('sprite_size_y', pygame.Rect(900, row_y + 330, 60, 30)),
                ('render_size_x', pygame.Rect(1000, row_y + 330, 60, 30)),
                ('render_size_y', pygame.Rect(1100, row_y + 330, 60, 30)),
            ]
            
            for field_name, rect in fields:
                if rect.collidepoint(mouse_pos):
                    self.selected_sprite_index = i
                    self.editing_field = field_name
                    
                    # Get current value
                    if 'border_offset' in field_name:
                        idx = 0 if field_name.endswith('_x') else 1
                        self.input_text = str(sprite_config.get('border_offset', [0, 0])[idx])
                    elif 'grid_offset' in field_name:
                        idx = 0 if field_name.endswith('_x') else 1
                        self.input_text = str(sprite_config.get('grid_offset', [0, 0])[idx])
                    elif 'render_size' in field_name:
                        idx = 0 if field_name.endswith('_x') else 1
                        default_size = sprite_config.get('sprite_size', [100, 100])
                        self.input_text = str(sprite_config.get('render_size', default_size)[idx])
                    elif 'sprite_size' in field_name:
                        idx = 0 if field_name.endswith('_x') else 1
                        self.input_text = str(sprite_config.get('sprite_size', [100, 100])[idx])
                    else:
                        self.input_text = str(sprite_config[field_name])
                    return
    
    def save_field_edit(self, reload=False):
        """Save the edited field value and optionally reload config"""
        if self.selected_sprite_index is not None and self.editing_field is not None:
            try:
                value = int(self.input_text)
                sprite_config = self.sprites_config[self.selected_sprite_index]
                
                if 'border_offset' in self.editing_field:
                    idx = 0 if self.editing_field.endswith('_x') else 1
                    if 'border_offset' not in sprite_config:
                        sprite_config['border_offset'] = [0, 0]
                    sprite_config['border_offset'][idx] = value
                    print(f"Updated border_offset[{idx}] to {value}")
                elif 'grid_offset' in self.editing_field:
                    idx = 0 if self.editing_field.endswith('_x') else 1
                    if 'grid_offset' not in sprite_config:
                        sprite_config['grid_offset'] = [0, 0]
                    sprite_config['grid_offset'][idx] = value
                    print(f"Updated grid_offset[{idx}] to {value}")
                elif 'render_size' in self.editing_field:
                    idx = 0 if self.editing_field.endswith('_x') else 1
                    if 'render_size' not in sprite_config:
                        sprite_config['render_size'] = sprite_config.get('sprite_size', [100, 100]).copy()
                    sprite_config['render_size'][idx] = value
                    print(f"Updated render_size[{idx}] to {value}")
                elif 'sprite_size' in self.editing_field:
                    idx = 0 if self.editing_field.endswith('_x') else 1
                    if 'sprite_size' not in sprite_config:
                        sprite_config['sprite_size'] = [100, 100]
                    sprite_config['sprite_size'][idx] = value
                    print(f"Updated sprite_size[{idx}] to {value}")
                else:
                    sprite_config[self.editing_field] = value
                    print(f"Updated {self.editing_field} to {value}")
                
                # Track that this sprite was modified
                self.modified_sprite_indices.add(self.selected_sprite_index)
                
                # Save and reload if requested
                if reload:
                    if self.save_config():
                        self.reload_sprites()
            except ValueError:
                print(f"Invalid value: {self.input_text}")
        
        if not reload:  # Only clear editing state if not using arrow keys
            self.editing_field = None
            self.input_text = ""
    
    def cancel_field_edit(self):
        """Cancel editing"""
        self.editing_field = None
        self.input_text = ""
    
    def draw(self):
        """Draw the viewer"""
        self.screen.fill(self.bg_color)
        
        # Title
        title = self.font_large.render("Sprite Viewer & Configuration Editor", True, self.text_color)
        self.screen.blit(title, (20, 20))
        
        # Instructions
        instructions = self.font_small.render(
            "Click on grid_cols or grid_rows to edit | Press Enter to save, Esc to cancel | Scroll with mouse wheel or buttons",
            True, (100, 100, 100)
        )
        self.screen.blit(instructions, (20, 60))
        
        # Draw scroll buttons
        mouse_pos = pygame.mouse.get_pos()
        
        up_color = self.button_hover if self.scroll_up_btn.collidepoint(mouse_pos) else self.button_color
        pygame.draw.rect(self.screen, up_color, self.scroll_up_btn, border_radius=5)
        up_text = self.font_medium.render("^", True, (255, 255, 255))
        up_rect = up_text.get_rect(center=self.scroll_up_btn.center)
        self.screen.blit(up_text, up_rect)
        
        down_color = self.button_hover if self.scroll_down_btn.collidepoint(mouse_pos) else self.button_color
        pygame.draw.rect(self.screen, down_color, self.scroll_down_btn, border_radius=5)
        down_text = self.font_medium.render("v", True, (255, 255, 255))
        down_rect = down_text.get_rect(center=self.scroll_down_btn.center)
        self.screen.blit(down_text, down_rect)
        
        # Draw sprite rows
        y_start = 120 - self.scroll_offset
        
        for i, sprite_config in enumerate(self.sprites_config):
            row_y = y_start + i * 400
            
            # Skip if off screen
            if row_y < -400 or row_y > self.height - 100:
                continue
            
            self.draw_sprite_row(sprite_config, row_y, i)
        
        # Draw submit button
        submit_color = self.button_hover if self.submit_btn.collidepoint(mouse_pos) else self.button_color
        pygame.draw.rect(self.screen, submit_color, self.submit_btn, border_radius=8)
        submit_text = self.font_medium.render("Save Configuration", True, (255, 255, 255))
        submit_rect = submit_text.get_rect(center=self.submit_btn.center)
        self.screen.blit(submit_text, submit_rect)
        
        pygame.display.flip()
    
    def draw_sprite_row(self, sprite_config, y, index):
        """Draw a row with texture + sprites on top, config on bottom"""
        # Background
        row_rect = pygame.Rect(10, y, self.width - 20, 380)
        pygame.draw.rect(self.screen, self.form_bg, row_rect, border_radius=5)
        pygame.draw.rect(self.screen, (200, 200, 200), row_rect, 2, border_radius=5)
        
        # === TOP PART: Texture + Sprites ===
        
        # Sprite name
        name_text = self.font_medium.render(f"{sprite_config['name']}", True, self.text_color)
        self.screen.blit(name_text, (20, y + 10))
        
        # Draw full texture
        texture_path = self.sprite_loader.assets_dir / f"{sprite_config['name']}_grid.png"
        if texture_path.exists():
            try:
                texture = pygame.image.load(str(texture_path)).convert_alpha()
                # Scale texture to fit 200x200
                texture_scaled = pygame.transform.scale(texture, (200, 200))
                self.screen.blit(texture_scaled, (20, y + 40))
                
                # Draw border around texture
                pygame.draw.rect(self.screen, (100, 100, 100), (20, y + 40, 200, 200), 2)
            except:
                pass
        
        # Display click coordinates if available
        if index in self.click_coords:
            coord_x, coord_y = self.click_coords[index]
            coord_text = self.font_small.render(f"Clicked: ({coord_x}, {coord_y})", True, (200, 0, 0))
            self.screen.blit(coord_text, (240, y + 10))
        
        # Draw loaded sprite variants
        x_offset = 240
        for variant in sprite_config['variants'][:10]:  # Show max 10 variants
            sprite = self.sprite_loader.get_sprite(sprite_config['name'], variant)
            if sprite:
                # Scale sprite to fit
                max_size = 60
                sprite_scaled = pygame.transform.scale(sprite, (max_size, max_size))
                self.screen.blit(sprite_scaled, (x_offset, y + 40))
                
                # Variant name
                variant_text = self.font_small.render(variant[:8], True, self.text_color)
                v_rect = variant_text.get_rect(center=(x_offset + max_size // 2, y + 105))
                self.screen.blit(variant_text, v_rect)
                
                x_offset += max_size + 10
        
        # Separator line between top and bottom parts
        pygame.draw.line(self.screen, (200, 200, 200), (20, y + 250), (self.width - 30, y + 250), 2)
        
        # === BOTTOM PART: Configuration ===
        
        # Configuration info
        config_x = 20
        config_y = y + 260
        
        border_offset = sprite_config.get('border_offset', [0, 0])
        grid_offset = sprite_config.get('grid_offset', [0, 0])
        render_size = sprite_config.get('render_size', sprite_config['sprite_size'])
        
        info_lines = [
            f"Variants: {len(sprite_config['variants'])}",
            f"Grid: {sprite_config['grid_cols']}x{sprite_config['grid_rows']}",
            f"Extract: {sprite_config['sprite_size'][0]}x{sprite_config['sprite_size'][1]}",
            f"Render: {render_size[0]}x{render_size[1]}",
            f"Border: {border_offset[0]}, {border_offset[1]}",
            f"Spacing: {grid_offset[0]}, {grid_offset[1]}",
        ]
        
        for i, line in enumerate(info_lines):
            text = self.font_small.render(line, True, self.text_color)
            self.screen.blit(text, (config_x, config_y + i * 20))
        
        # Editable fields - First row
        y_offset = y + 280
        self.draw_editable_field("grid_cols", sprite_config['grid_cols'], 800, y_offset, index)
        self.draw_editable_field("grid_rows", sprite_config['grid_rows'], 900, y_offset, index)
        self.draw_editable_field("border_offset_x", border_offset[0], 1000, y_offset, index)
        self.draw_editable_field("border_offset_y", border_offset[1], 1100, y_offset, index)
        self.draw_editable_field("grid_offset_x", grid_offset[0], 1200, y_offset, index)
        self.draw_editable_field("grid_offset_y", grid_offset[1], 1300, y_offset, index)
        
        # Editable fields - Second row
        y_offset2 = y + 330
        sprite_size = sprite_config.get('sprite_size', [100, 100])
        render_size = sprite_config.get('render_size', sprite_size)
        self.draw_editable_field("sprite_size_x", sprite_size[0], 800, y_offset2, index)
        self.draw_editable_field("sprite_size_y", sprite_size[1], 900, y_offset2, index)
        self.draw_editable_field("render_size_x", render_size[0], 1000, y_offset2, index)
        self.draw_editable_field("render_size_y", render_size[1], 1100, y_offset2, index)
    
    def draw_editable_field(self, field_name, value, x, y, sprite_index):
        """Draw an editable field"""
        is_editing = (self.selected_sprite_index == sprite_index and self.editing_field == field_name)
        
        # Field background
        field_rect = pygame.Rect(x, y, 60, 30)
        bg_color = self.input_active if is_editing else self.input_bg
        pygame.draw.rect(self.screen, bg_color, field_rect, border_radius=3)
        pygame.draw.rect(self.screen, (150, 150, 150), field_rect, 2, border_radius=3)
        
        # Display value or input
        display_text = self.input_text if is_editing else str(value)
        text_surface = self.font_small.render(display_text, True, self.text_color)
        text_rect = text_surface.get_rect(center=field_rect.center)
        self.screen.blit(text_surface, text_rect)
        
        # Field label
        label = self.font_small.render(field_name, True, (100, 100, 100))
        self.screen.blit(label, (x, y - 20))
    
    def run(self):
        """Main loop"""
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


def main():
    viewer = SpriteViewer()
    viewer.run()


if __name__ == "__main__":
    main()
