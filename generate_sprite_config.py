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


def detect_border_offset(img, threshold=10):
    """Detect border offset by finding first non-black pixels from edges"""
    pixels = img.load()
    width, height = img.size
    
    # Find left border
    left_offset = 0
    for x in range(width // 2):
        has_content = False
        for y in range(height):
            if pixels[x, y][:3] != (0, 0, 0) and sum(pixels[x, y][:3]) > threshold:
                has_content = True
                break
        if has_content:
            left_offset = x
            break
    
    # Find top border
    top_offset = 0
    for y in range(height // 2):
        has_content = False
        for x in range(width):
            if pixels[x, y][:3] != (0, 0, 0) and sum(pixels[x, y][:3]) > threshold:
                has_content = True
                break
        if has_content:
            top_offset = y
            break
    
    return [left_offset, top_offset]


def detect_grid_offset(img, grid_cols, grid_rows, border_offset):
    """Detect spacing between grid cells"""
    pixels = img.load()
    width, height = img.size
    
    if grid_cols <= 1 and grid_rows <= 1:
        return [0, 0]
    
    # Calculate expected cell size including any spacing
    available_width = width - 2 * border_offset[0]
    available_height = height - 2 * border_offset[1]
    
    # Try to detect horizontal spacing (if multiple columns)
    h_offset = 0
    if grid_cols > 1:
        cell_width = available_width // grid_cols
        # Look for black gap between first and second cell
        check_x = border_offset[0] + cell_width
        gap_start = None
        for x in range(check_x - 50, check_x + 50):
            if 0 <= x < width:
                is_black = True
                for y in range(border_offset[1] + 10, min(border_offset[1] + 100, height)):
                    if pixels[x, y][:3] != (0, 0, 0) and sum(pixels[x, y][:3]) > 10:
                        is_black = False
                        break
                if is_black and gap_start is None:
                    gap_start = x - (border_offset[0] + cell_width)
                elif not is_black and gap_start is not None:
                    h_offset = gap_start
                    break
    
    # Try to detect vertical spacing (if multiple rows)
    v_offset = 0
    if grid_rows > 1:
        cell_height = available_height // grid_rows
        # Look for black gap between first and second row
        check_y = border_offset[1] + cell_height
        gap_start = None
        for y in range(check_y - 50, check_y + 50):
            if 0 <= y < height:
                is_black = True
                for x in range(border_offset[0] + 10, min(border_offset[0] + 100, width)):
                    if pixels[x, y][:3] != (0, 0, 0) and sum(pixels[x, y][:3]) > 10:
                        is_black = False
                        break
                if is_black and gap_start is None:
                    gap_start = y - (border_offset[1] + cell_height)
                elif not is_black and gap_start is not None:
                    v_offset = gap_start
                    break
    
    return [h_offset, v_offset]


def analyze_grid_image(image_path, entity_name, existing_config=None):
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
            
            # Detect border offset
            border_offset = detect_border_offset(img)
            
            # Detect grid offset
            grid_offset = detect_grid_offset(img, grid_cols, grid_rows, border_offset)
            
            # Calculate sprite size accounting for offsets
            available_width = width - 2 * border_offset[0] - (grid_cols - 1) * grid_offset[0]
            available_height = height - 2 * border_offset[1] - (grid_rows - 1) * grid_offset[1]
            sprite_width = available_width // grid_cols
            sprite_height = available_height // grid_rows
            
            # Extract variant names (remove descriptions)
            variant_names = [v.split(":")[0].strip() for v in variants]
            
            # Determine render size (preserve from existing config if available)
            if existing_config and 'render_size' in existing_config:
                render_size = existing_config['render_size']
                print(f"  Preserved render_size: {render_size}")
            else:
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
                "border_offset": border_offset,
                "grid_offset": grid_offset
            }
            
            offset_info = ""
            if border_offset != [0, 0] or grid_offset != [0, 0]:
                offset_info = f" [border:{border_offset}, grid:{grid_offset}]"
            print(f"✓ {entity_name}: {width}x{height} image → {grid_cols}x{grid_rows} grid → {sprite_width}x{sprite_height} sprites{offset_info}")
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
    
    # Load existing config to preserve render_size
    existing_configs = {}
    try:
        with open(output_file, 'r') as f:
            for config in json.load(f):
                existing_configs[config['name']] = config
    except FileNotFoundError:
        pass
    
    print("🔍 Scanning grid images...\n")
    
    # Process all entities from ENTITY_VARIANTS
    for entity_name in sorted(ENTITY_VARIANTS.keys()):
        image_path = os.path.join(grids_dir, f"{entity_name}_grid.png")
        
        if os.path.exists(image_path):
            existing_config = existing_configs.get(entity_name)
            config = analyze_grid_image(image_path, entity_name, existing_config)
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
        print(f"\n💡 Use sprite_viewer.py to verify and fine-tune if needed")
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
    
    # Find existing config for this entity
    existing_config = None
    for config in configs:
        if config['name'] == entity_name:
            existing_config = config
            break
    
    # Generate new config for entity (preserves render_size from existing)
    new_config = analyze_grid_image(image_path, entity_name, existing_config)
    if not new_config:
        return False
    
    # Find and update existing entry, or append new one
    updated = False
    for i, config in enumerate(configs):
        if config['name'] == entity_name:
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
