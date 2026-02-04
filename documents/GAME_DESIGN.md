# Tea Garden Cats - Game Design Document

## 🎮 Game Overview

**Title:** Tea Garden Cats  
**Genre:** Casual Puzzle/Collection Game  
**Platform:** Desktop (Python + Pygame)  
**Target Audience:** Casual gamers, cat lovers, tea enthusiasts  
**Development Time:** 2-3 weeks  

## 📖 Concept

A relaxing game where you manage a cozy Chinese tea garden visited by adorable cats. Serve different types of tea to visiting cats, collect hearts, and unlock new cats and tea varieties. Each cat has favorite teas and unique personalities.

## 🎯 Core Gameplay Loop

1. **Welcome Cats** - Different cats visit your tea garden throughout the day
2. **Serve Tea** - Click and drag tea cups to serve cats their favorite teas
3. **Collect Hearts** - Happy cats leave hearts when served their favorite tea
4. **Unlock Content** - Use hearts to unlock new tea varieties and attract rare cats
5. **Decorate Garden** - Customize your tea garden with unlockables

## 🎨 Visual Style

- **Art Style:** Cute pixel art or simple vector graphics
- **Color Palette:** Warm, cozy colors (soft greens, browns, oranges, pink)
- **Screen Resolution:** 1024x768 (scalable)
- **UI Theme:** Traditional Chinese tea house aesthetic with modern cute elements

## 🐱 Cat Characters

### Starter Cats (Always Available)
1. **Mimi** - Orange tabby, loves jasmine tea
   - Personality: Friendly and energetic
   - Favorite: Jasmine Oolong

2. **Luna** - Black cat with white paws, loves oolong tea
   - Personality: Mysterious and elegant
   - Favorite: Te Guan Yin Oolong

3. **Tofu** - White fluffy cat, loves white tea
   - Personality: Shy and sweet
   - Favorite: Silver Needle White Tea

### Unlockable Cats (Rare Visitors)
4. **Ginger** - Calico, loves pu-erh tea
   - Unlock: Serve 20 teas correctly
   - Favorite: Leach Tears Ripe Pu-erh

5. **Petya** - Grey Siberian Cat, loves red tea
   - Unlock: Collect 50 hearts
   - Favorite: Dualist Red Tea

6. **Lapilaps** - Pink-collar Siamese, loves white tea
   - Unlock: Collect 100 hearts
   - Favorite: Violet Ya Bao

## 🍵 Tea System

### Tea Categories
Each tea belongs to a category that affects its brewing time:
1. **Red Tea** - 4s brewing time (oxidized black teas)
2. **Oolong** - 3s brewing time (semi-oxidized)
3. **White Tea** - 2s brewing time (minimal processing)
4. **Raw Pu-erh** - 3s brewing time (unfermented)
5. **Ripe Pu-erh** - 4s brewing time (fermented)

Each tea also has:
- **Heart Value:** Points earned when served correctly (1-3 hearts)
- **Rarity:** Common, Uncommon, Rare

### Tea Types (Progressive Unlock)
1. **Jasmine Oolong** (Starter) - Oolong, 3s brew, 1 heart
2. **Te Guan Yin Oolong** (Starter) - Oolong, 3s brew, 1 heart
3. **Silver Needle White Tea** (Starter) - White Tea, 2s brew, 1 heart
4. **Dan Tsun Oolong** (5 hearts) - Oolong, 3s brew, 2 hearts
5. **Violet Ya Bao** (15 hearts) - White Tea, 2s brew, 2 hearts
6. **Dualist Red Tea** (30 hearts) - Red Tea, 4s brew, 2 hearts
7. **Leach Tears Ripe Pu-erh** (50 hearts) - Ripe Pu-erh, 4s brew, 3 hearts
8. **Golden Monkey Black Tea** (75 hearts) - Red Tea, 4s brew, 3 hearts

## 🎮 Game Mechanics

### Core Mechanics

1. **Cat Arrival System**
   - Cats arrive randomly every 10-20 seconds
   - Show thought bubble with their desired tea
   - Wait for 30 seconds before leaving if not served

2. **Tea Brewing**
   - Click on tea type from menu
   - Wait for brewing animation/timer
   - Drag tea cup to the cat

3. **Serving System**
   - Correct tea: Cat happy, gives hearts + purr sound
   - Wrong tea: Cat disappointed, gives 0 hearts + meow sound
   - Too slow: Cat leaves sad

4. **Progression System**
   - Hearts accumulate as currency
   - Unlock new teas and cats with hearts
   - Track statistics (teas served, cats satisfied, etc.)

### Bonus Features
- **Combo System:** Serve 5 cats correctly in a row for bonus hearts
- **Special Events:** Golden cat appears randomly and gives 5x hearts
- **Daily Rewards:** Log in daily for bonus hearts
- **Weather System:** Different ambiance (sunny, rainy) affects cat visits

## 🖥️ Technical Architecture

### File Structure
```
tea_garden_cats/
├── main.py                 # Game entry point
├── game/
│   ├── __init__.py
│   ├── game_state.py      # Core game state management
│   ├── sprite_loader.py   # Sprite loading system with grid extraction
│   ├── scenes/
│   │   ├── menu_scene.py  # Main menu
│   │   ├── game_scene.py  # Main gameplay (tea ceremony)
│   │   └── stats_scene.py # Statistics/achievements
│   ├── tea_objects/       # Tea ceremony equipment module
│   │   ├── __init__.py
│   │   ├── tea_disk.py    # Draggable tea selection
│   │   ├── tea_kettle.py  # Gaiwan for brewing
│   │   ├── hot_water_kettle.py  # Water source
│   │   ├── cha_hai.py     # Fairness cup
│   │   ├── tea_cup.py     # Small serving cups
│   │   └── cat_visitor.py # Cat visitors with AI
│   ├── entities/
│   │   └── button.py      # UI button component
│   └── ui/
│       └── button.py      # UI elements
├── assets/
│   └── images/
│       └── grids/         # DALL-E generated sprite grids
├── data/
│   ├── cats_data.json     # Cat definitions (6 cats)
│   ├── teas_data.json     # Tea definitions (8 teas)
│   └── save_data.json     # Player progress
├── documents/
│   ├── GAME_DESIGN.md     # This document
│   ├── GAME_SCENE_DESIGN.md  # Scene layouts
│   ├── IMAGE_PROMPTS.md   # DALL-E prompts
│   └── QUICK_IMAGE_GUIDE.md  # Sprite generation guide
├── generate_cat_image.py  # DALL-E sprite generator
├── pyproject.toml
└── README.md
```

### Key Classes (Actual Implementation)

```python
# CatVisitor class (tea_objects/cat_visitor.py)
class CatVisitor:
    - cat_data: dict
    - position: list
    - state: str (arriving, waiting, happy, disappointed, leaving)
    - patience: float (0-100)
    - waiting_time: float
    - served: bool
    - happiness: int
    - animation_timer: float
    - sprite_loader: SpriteLoader
    
    + update(dt)
    + receive_tea(tea_id) -> dict
    + can_pet() -> bool
    + pet() -> int
    + draw(screen)
    + is_off_screen() -> bool

# TeaKettle class (tea_objects/tea_kettle.py)
class TeaKettle:
    - position: tuple
    - state: str (empty, has_tea, brewing, ready)
    - tea_data: dict
    - brew_timer: float
    - brew_duration: float
    - sprite_loader: SpriteLoader
    
    + add_tea(tea_data) -> bool
    + add_water() -> bool
    + update(dt)
    + pour_to_cha_hai() -> dict
    + get_brew_progress() -> float
    + draw(screen)

# TeaDisk class (tea_objects/tea_disk.py)
class TeaDisk:
    - tea_data: dict
    - position: list
    - dragging: bool
    - radius: int
    - sprite_loader: SpriteLoader
    
    + draw(screen)
    + contains_point(point) -> bool
    + snap_back()

# SpriteLoader class (sprite_loader.py)
class SpriteLoader:
    - sprite_cache: dict
    - grid_size: tuple
    
    + load_grid(name, variants, grid_layout)
    + get_sprite(entity_name, variant) -> Surface
    + _remove_black_background(surface) -> Surface
    + _create_fallback_sprite(name, variant, size) -> Surface

# GameState class
class GameState:
    - hearts: int
    - teas_served: int
    - cats_satisfied: int
    - current_combo: int
    - best_combo: int
    - unlocked_teas: set
    - unlocked_cats: set
    
    + save_progress()
    + load_progress()
    + add_hearts(amount)
    + reset_combo()
```

### Dependencies (pyproject.toml)
```toml
[project]
name = "tea-garden-cats"
version = "0.1.0"
description = "A cozy game about serving tea to cats"
requires-python = ">=3.10"
dependencies = [
    "pygame>=2.5.0",
]
```

## 🎵 Audio Design

### Music
- **Main Menu:** Soft traditional Chinese instrumental
- **Gameplay:** Relaxing guzheng and erhu melody
- **Shop:** Upbeat but calm melody

### Sound Effects
- Cat purr (happy)
- Cat meow (disappointed)
- Tea pouring
- Coin/heart collect sound
- Unlock chime
- Combo multiplier sound

## 📊 Game Progression

### Milestones
- **5 Hearts:** Unlock Dan Tsun Oolong
- **10 Hearts:** Unlock garden decoration slot 1
- **15 Hearts:** Unlock Violet Ya Bao
- **20 Hearts:** Unlock Ginger cat
- **30 Hearts:** Unlock Dualist Red Tea
- **35 Hearts:** Unlock combo meter display
- **50 Hearts:** Unlock Petya cat + Leach Tears Ripe Pu-erh
- **75 Hearts:** Unlock special background music + Golden Monkey Black Tea
- **100 Hearts:** Unlock Lapilaps cat (Rare!)
- **150 Hearts:** Unlock all content + endless mode

## 🎯 MVP (Minimum Viable Product) Features

### Phase 1 - Core Gameplay (Week 1) ✅ COMPLETED
- [x] Basic game window and main loop
- [x] 6 cats with sprite system and fallbacks
- [x] 8 different Chinese teas
- [x] Cat arrival and departure system with patience
- [x] Traditional tea ceremony brewing (7-step process)
- [x] Heart collection system
- [x] Basic UI (heart counter, tea drawer, combo display)
- [x] Drag & drop mechanics for all tea equipment
- [x] Brewing timer with progress display
- [x] Petting mechanic for bonus hearts

### Phase 2 - Polish (Week 2) 🔄 IN PROGRESS
- [x] Sprite loading system with grid extraction
- [x] DALL-E 3 integration for sprite generation
- [x] Fallback rendering system
- [x] Modular code structure (tea_objects module)
- [ ] Sound effects and music
- [x] Save/load system (basic implementation)
- [x] Unlock system (all cats and teas)
- [ ] Shop/unlock menu UI
- [x] Statistics tracking

### Phase 3 - Enhancement (Week 3) 📋 PLANNED
- [ ] Generate all sprite assets via DALL-E
- [ ] Particle effects (steam, sparkles, hearts, petals)
- [x] Combo system (basic tracking)
- [ ] Special events (golden cat)
- [ ] Background decorations and animations
- [ ] Tutorial/help screen
- [ ] Final polish and bug fixes
- [ ] Sound and music integration

## 🎨 UI Mockup Description

### Main Game Screen
```
┌─────────────────────────────────────────────────┐
│ 🏮 Tea Garden Cats        ❤️ Hearts: 25       │
├─────────────────────────────────────────────────┤
│                                                 │
│         🌸  [Garden Background]  🌸            │
│                                                 │
│     😺💭🍵    😺💭🍵      (Cats with          │
│                           thought bubbles)     │
│                                                 │
│     😺        (One happy cat)                  │
│                                                 │
├─────────────────────────────────────────────────┤
│ Tea Menu:                                       │
│ [🍵 Jasmine] [🍵 Oolong] [🍵 White]          │
│ [🔒 Pu-erh] [🔒 Black] [🔒 Flower]           │
│                                                 │
│              [Shop 🏪] [Stats 📊]              │
└─────────────────────────────────────────────────┘
```

## 🎁 Personal Touches for Your Girlfriend

1. **Hidden Easter Eggs:**
   - A special cat with her name that appears rarely
   - Her favorite tea as the most valuable
   - Her birthday as a special event day

2. **Personal Messages:**
   - Loading screen quotes about love and cats
   - Achievement descriptions with inside jokes
   - Cat names inspired by your relationship

3. **Customization:**
   - Option to name the tea garden after her
   - Photo frame decoration that could hold her picture
   - Special "Love Mode" with heart-shaped tea cups

## 🚀 Getting Started

### Setup Commands
```bash
# Navigate to project directory
cd tea_garden_cats

# Initialize UV project
uv init

# Add pygame dependency
uv add pygame

# Create virtual environment
uv venv

# Run the game
uv run main.py
```

## 📝 Development Notes

- Keep code modular for easy expansion
- Use JSON files for data (easy to add more cats/teas)
- Implement save system early
- Test on different screen sizes
- Consider adding difficulty levels later
- Potential for mobile port with touch controls

## 🎉 Future Expansion Ideas

- Multiplayer: Visit friends' tea gardens
- Seasonal events (Chinese New Year, Mid-Autumn Festival)
- Cat collector album with detailed descriptions
- Tea encyclopedia with real tea facts
- Garden expansion: Multiple rooms/areas
- Mini-games: Tea ceremony, cat toy crafting
- Achievement system with badges

---

**Created with ❤️ for someone who loves cats and Chinese tea**

*Start small, iterate often, and most importantly - have fun building it together!*
