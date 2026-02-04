"""
Generate grid sprite sheets using OpenAI DALL-E API
"""
import os
from openai import OpenAI

BACKGROUND_SUFFIX = ", background must be solid black (#000000) only, no transparency, no checkerboard, no grid pattern, no texture, no gradient"

ENTITY_VARIANTS = {
    "mimi": [
        "normal: orange tabby with dark stripes, friendly expression",
        "happy: eyes closed in contentment",
        "impatient: ears back, worried expression",
        "disappointed: sad droopy eyes",
    ],
    "luna": [
        "normal: black fur with white paws and chest marking, big yellow eyes",
        "happy: eyes closed in contentment",
        "impatient: ears back, worried yellow eyes",
        "disappointed: sad droopy yellow eyes",
    ],
    "tofu": [
        "normal: pure white fluffy fur, big blue eyes, sweet shy expression",
        "happy: eyes closed, content smile",
        "impatient: ears back, worried blue eyes",
        "disappointed: sad droopy blue eyes",
    ],
    "ginger": [
        "normal: calico pattern orange black white, friendly eyes",
        "happy: eyes closed in joy",
        "impatient: ears back, anxious expression",
        "disappointed: sad eyes",
    ],
    "petya": [
        "normal: large fluffy grey Siberian, wise calm expression",
        "happy: eyes closed peacefully",
        "impatient: ears slightly back, concerned expression",
        "disappointed: sad droopy eyes",
    ],
    "lapilaps": [
        "normal: cream/tan Siamese with dark brown points, blue almond eyes, pink collar",
        "happy: eyes closed, content expression",
        "impatient: worried blue eyes, ears back",
        "disappointed: sad blue eyes",
    ],
    "gaiwan": [
        "empty: white porcelain with blue floral patterns, bowl lid saucer",
        "tea_leaves: loose green/brown leaves visible",
        "with_water: filled with water, small steam wisps",
        "brewing: amber tea liquid, steam rising",
        "ready: amber tea with golden sparkles",
    ],
    "kettle": [
        "ready: upright hot water kettle, steam from spout",
        "pouring: tilted, water stream visible",
    ],
    "chahai": [
        "empty: white porcelain with blue patterns",
        "filled: amber tea liquid visible",
    ],
    "teacup": [
        "empty: small cup with blue rim patterns",
        "filled: amber tea liquid",
    ],
    "cha_ban": [
        "single: bamboo tea tray, rectangular, parallel slats",
    ],
    "tea_drawer": [
        "single: dark lacquered wood drawer with brass handles, compartments",
    ],
    "tea_disks": [
        "jasmine_oolong: light jade green, jasmine flowers mixed in",
        "te_guan_yin: deeper jade green, tightly rolled leaves",
        "silver_needle: pale silver-white, delicate buds",
        "dan_tsun: darker green-brown, twisted leaves",
        "violet_ya_bao: purple-tinted wild buds",
        "dualist_red: deep red-brown oxidized leaves",
        "leach_tears: dark brown-black aged pu-erh",
        "golden_monkey: golden-brown with golden tips",
    ],
    "ui_hearts": [
        "filled: pink/red gradient heart",
        "empty: outline only",
    ],
    "thought_bubble": [
        "single: comic thought bubble with trailing circles",
    ],
    "lock_icon": [
        "single: golden closed padlock",
    ],
    "progress_bar": [
        "background: bamboo/wood texture bar",
        "fill: warm amber/gold fill",
    ],
    "border_frame": [
        "single: decorative Chinese garden border frame",
    ],
    "steam_particles": [
        "frame1: wispy steam variant",
        "frame2: wispy steam variant",
        "frame3: wispy steam variant",
        "frame4: dissipating steam variant",
    ],
    "heart_particles": [
        "small: pink floating heart",
        "medium: pink floating heart",
        "large: pink floating heart",
    ],
    "sparkles": [
        "frame1: golden four-pointed star",
        "frame2: larger glow",
        "frame3: brightest glow",
        "frame4: fading glow",
    ],
    "petals": [
        "frame1: pink cherry blossom petal",
        "frame2: pink cherry blossom petal",
        "frame3: pink cherry blossom petal",
    ],
}


def get_entity_variants(entity_name):
    """Return all asset keys that belong to a single entity."""
    return ENTITY_VARIANTS.get(entity_name, [])


def build_grid_prompt(entity_name, variants):
    """Create a single prompt that requests a grid sprite sheet of variants."""
    variant_labels = "; ".join(variants)
    total_states = len(variants)
    columns = 1
    rows = total_states
    while columns * columns < total_states:
        columns += 1
    rows = (total_states + columns - 1) // columns
    return (
        f"Pixel art, top-down 2D view. Create a single sprite sheet grid with all variants for '{entity_name}'. "
        f"Total states: {total_states}. Grid size: {columns}x{rows}. "
        f"Include these variants in separate cells with consistent scale and alignment: {variant_labels}. "
        "Arrange them in a clean grid with the specified size, no text labels, no borders, no drop shadows."
        f"{BACKGROUND_SUFFIX}"
    )


def generate_entity_grid(entity_name, grid_dir="assets/images/grids/"):
    """Generate all variants for a single entity and save as a grid image."""
    variants = get_entity_variants(entity_name)
    if not variants:
        print(f"❌ Unknown entity: {entity_name}")
        return None

    print(f"\n🧩 Generating single-prompt grid for '{entity_name}' ({len(variants)} variants)...\n")
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    prompt = build_grid_prompt(entity_name, variants)

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url
        print(f"\nGrid image generated successfully!")
        print(f"URL: {image_url}")

        import urllib.request
        os.makedirs(grid_dir, exist_ok=True)
        grid_path = os.path.join(grid_dir, f"{entity_name}_grid.png")

        print(f"Downloading grid to {grid_path}...")
        urllib.request.urlretrieve(image_url, grid_path)
        print(f"✓ Grid saved to {grid_path}")

        return grid_path

    except Exception as e:
        print(f"Error generating grid: {e}")
        return None


if __name__ == "__main__":
    import sys
    
    # Check if API key is set
    if not os.environ.get("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("\nPlease set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    # Get entity name from command line or show usage
    if len(sys.argv) < 2:
        print("Usage: python generate_cat_image.py <entity|grid_*> ")
        print("\nExamples:")
        print("  python generate_cat_image.py grid_mimi            # Grid of all mimi variants")
        print("  python generate_cat_image.py grid_gaiwan          # Grid of all gaiwan states")
        print("  python generate_cat_image.py mimi                 # Grid of all mimi variants")
        print("\nAvailable entities:")
        for name in sorted(ENTITY_VARIANTS.keys()):
            print(f"  - {name}")
        sys.exit(1)
    
    arg = sys.argv[1].lower()
    
    if arg.startswith("grid_") or arg.startswith("grid:"):
        entity = arg.split("_", 1)[1] if arg.startswith("grid_") else arg.split(":", 1)[1]
        grid_path = generate_entity_grid(entity)
        if grid_path:
            print(f"\n✅ Grid saved to {grid_path}")
            sys.exit(0)
        sys.exit(1)
    else:
        grid_path = generate_entity_grid(arg)
        if grid_path:
            print(f"\n✅ Grid saved to {grid_path}")
            sys.exit(0)
        if arg == "all":
            for name in sorted(ENTITY_VARIANTS.keys()):
                print(f"Generating  - {name}")
                grid_path = generate_entity_grid(name)
                if grid_path:
                    print(f"\n✅ Grid saved to {grid_path}")
        print(f"❌ Unknown entity: {arg}")
        print("Available entities:")
        for name in sorted(ENTITY_VARIANTS.keys()):
            print(f"  - {name}")
        sys.exit(1)
