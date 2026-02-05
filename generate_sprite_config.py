"""
Generate or update sprites_config.json based on grid images and entity definitions
"""
import os
import json
from PIL import Image
from generate_cat_image import ENTITY_VARIANTS


def calculate_grid_size(num_variants):
    """Calculate grid columns and rows for a given number of variants"""
    columns = 1
    while columns * columns < num_variants:
        columns += 1
    rows = (num_variants + columns - 1) // columns
    return columns, rows


def analyze_grid_image(image_path, entity_name):
    """Analyze a grid image and return sprite configuration"""
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            
            variants = ENTITY_VARIANTS.get(entity_name, [])
            if not variants:
                print(f"⚠️  No variants found for {entity_name}")
                return None
            
            num_variants = len(variants)
            grid_cols, grid_rows = calculate_grid_size(num_variants)
            
            # Calculate sprite size (divide image by grid)
            sprite_width = width // grid_cols
            sprite_height = height // grid_rows
            
            # Extract variant names (remove descriptions)
            variant_names = [v.split(":")[0].strip() for v in variants]
            
            # Determine reasonable render size
            # For cats, scale down to 100x100
            # For small items, keep original size
            if entity_name in ['mimi', 'luna', 'tofu', 'ginger', 'petya', 'lapilaps']:
                render_size = [100, 100]
            elif max(sprite_width, sprite_height) > 300:
                # Large sprites, scale down
                scale = 100 / max(sprite_width, sprite_height)
                render_size = [int(sprite_width * scale), int(sprite_height * scale)]
            else:
                # Keep original size
                render_size = [sprite_width, sprite_height]
            
            config = {
                "name": entity_name,
                "variants": variant_names,
                "grid_cols": grid_cols,
                "grid_rows": grid_rows,
                "sprite_size": [sprite_width, sprite_height],
                "render_size": render_size,
                "border_offset": [0, 0],
                "grid_offset": [0, 0]
            }
            
            print(f"✓ {entity_name}: {width}x{height} image → {grid_cols}x{grid_rows} grid → {sprite_width}x{sprite_height} sprites")
            return config
            
    except FileNotFoundError:
        print(f"⚠️  Image not found: {image_path}")
        return None
    except Exception as e:
        print(f"❌ Error analyzing {entity_name}: {e}")
        return None


def generate_config(grids_dir="assets/images/grids/", output_file="data/sprites_config.json"):
    """Generate sprites_config.json from grid images"""
    configs = []
    
    print("🔍 Scanning grid images...\n")
    
    # Process all entities from ENTITY_VARIANTS
    for entity_name in sorted(ENTITY_VARIANTS.keys()):
        image_path = os.path.join(grids_dir, f"{entity_name}_grid.png")
        
        if os.path.exists(image_path):
            config = analyze_grid_image(image_path, entity_name)
            if config:
                configs.append(config)
        else:
            print(f"⚠️  Missing: {entity_name}_grid.png")
    
    if configs:
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write to file
        with open(output_file, 'w') as f:
            json.dump(configs, f, indent=2)
        
        print(f"\n✅ Generated {output_file} with {len(configs)} sprite configurations")
        print(f"\n💡 Use sprite_viewer.py to fine-tune border_offset and grid_offset values")
    else:
        print("\n❌ No valid configurations generated")


def update_config(entity_name, grids_dir="assets/images/grids/", config_file="data/sprites_config.json"):
    """Update a single entity in the config file"""
    image_path = os.path.join(grids_dir, f"{entity_name}_grid.png")
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return False
    
    # Load existing config
    try:
        with open(config_file, 'r') as f:
            configs = json.load(f)
    except FileNotFoundError:
        configs = []
    
    # Generate new config for entity
    new_config = analyze_grid_image(image_path, entity_name)
    if not new_config:
        return False
    
    # Find and update existing entry, or append new one
    updated = False
    for i, config in enumerate(configs):
        if config['name'] == entity_name:
            # Preserve manual adjustments (border_offset, grid_offset)
            if 'border_offset' in config and config['border_offset'] != [0, 0]:
                new_config['border_offset'] = config['border_offset']
                print(f"  Preserved border_offset: {config['border_offset']}")
            if 'grid_offset' in config and config['grid_offset'] != [0, 0]:
                new_config['grid_offset'] = config['grid_offset']
                print(f"  Preserved grid_offset: {config['grid_offset']}")
            
            configs[i] = new_config
            updated = True
            break
    
    if not updated:
        configs.append(new_config)
    
    # Write back
    with open(config_file, 'w') as f:
        json.dump(configs, f, indent=2)
    
    print(f"✅ Updated {entity_name} in {config_file}")
    return True


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python generate_sprite_config.py <command> [entity_name]")
        print("\nCommands:")
        print("  generate    - Generate entire sprites_config.json from all grid images")
        print("  update <entity> - Update a single entity in the config")
        print("\nExamples:")
        print("  python generate_sprite_config.py generate")
        print("  python generate_sprite_config.py update mimi")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "generate":
        generate_config()
    elif command == "update":
        if len(sys.argv) < 3:
            print("❌ Error: Please specify entity name")
            print("Usage: python generate_sprite_config.py update <entity_name>")
            sys.exit(1)
        entity = sys.argv[2]
        update_config(entity)
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: generate, update")
        sys.exit(1)
