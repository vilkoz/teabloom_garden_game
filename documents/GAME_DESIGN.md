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
│   ├── scenes/
│   │   ├── menu_scene.py  # Main menu
│   │   ├── game_scene.py  # Main gameplay
│   │   └── shop_scene.py  # Unlock shop
│   ├── entities/
│   │   ├── cat.py         # Cat class
│   │   └── tea.py         # Tea class
│   └── ui/
│       ├── button.py      # UI button component
│       ├── text.py        # Text rendering
│       └── progress_bar.py
├── assets/
│   ├── images/
│   │   ├── cats/          # Cat sprites
│   │   ├── teas/          # Tea cup sprites
│   │   ├── backgrounds/   # Garden backgrounds
│   │   └── ui/            # UI elements
│   ├── sounds/
│   │   ├── music/         # Background music
│   │   └── sfx/           # Sound effects
│   └── fonts/
│       └── main_font.ttf
├── data/
│   ├── cats_data.json     # Cat definitions
│   ├── teas_data.json     # Tea definitions
│   └── save_data.json     # Player progress
├── pyproject.toml
└── README.md
```

### Key Classes

```python
# Cat class
class Cat:
    - name: str
    - sprite: pygame.Surface
    - favorite_tea: str
    - position: tuple
    - state: str (waiting, happy, disappointed, leaving)
    - wait_timer: float
    
    + arrive()
    + request_tea()
    + receive_tea(tea_type)
    + leave()
    + give_hearts()

# Tea class
class Tea:
    - name: str
    - brew_time: float
    - heart_value: int
    - sprite: pygame.Surface
    - is_brewing: bool
    
    + start_brew()
    + update_brew(dt)
    + serve()

# GameState class
class GameState:
    - hearts: int
    - unlocked_teas: list
    - unlocked_cats: list
    - statistics: dict
    - current_combo: int
    
    + save_progress()
    + load_progress()
    + add_hearts(amount)
    + unlock_tea(tea_name)
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

### Phase 1 - Core Gameplay (Week 1)
- [ ] Basic game window and main loop
- [ ] 3 starter cats with simple sprites
- [ ] 3 starter teas
- [ ] Cat arrival and departure system
- [ ] Tea brewing and serving
- [ ] Heart collection system
- [ ] Basic UI (heart counter, tea menu)

### Phase 2 - Polish (Week 2)
- [ ] Better graphics/sprites
- [ ] Sound effects and music
- [ ] Save/load system
- [ ] Unlock system (3 more cats, 5 more teas)
- [ ] Shop/unlock menu
- [ ] Statistics screen

### Phase 3 - Enhancement (Week 3)
- [ ] Animations and particle effects
- [ ] Combo system
- [ ] Special events (golden cat)
- [ ] Garden decorations
- [ ] Tutorial/help screen
- [ ] Final polish and bug fixes

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
