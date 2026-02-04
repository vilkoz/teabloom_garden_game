# Tea Garden Cats - Traditional Tea Ceremony Game

## 🎮 New Game Concept: Chinese Tea Ceremony Simulator

### 🍵 Core Experience
An authentic Chinese tea ceremony experience where you serve tea to visiting cats using traditional tea equipment and methods. Educational, relaxing, and beautiful.

### 🎯 Core Gameplay Loop (IMPLEMENTED)
1. **Select tea** from the tea drawer (click and drag tea disk)
2. **Drag tea leaves** to the tea kettle (gaiwan)
3. **Drag hot water kettle** to pour water into tea kettle
4. **Wait for brewing** (2-4 seconds based on tea type) with progress display
5. **Drag brewed tea kettle** to cha hai (fairness cup)
6. **Drag cha hai** to fill small cups (8 pialas)
7. **Drag cups** to waiting cats (serve correct tea for hearts)
8. **Click happy cats** for bonus hearts (petting mechanic)!
9. **Progress through unlocks** as heart count increases

### 🎮 Current Implementation Status
- ✅ Full drag & drop system for all equipment
- ✅ Tea kettle state machine (empty → has_tea → brewing → ready)
- ✅ Brewing timer with percentage display
- ✅ Sprite loading system with DALL-E grid support
- ✅ Fallback rendering for missing sprites
- ✅ Cat patience system (15 second timer)
- ✅ Cat emotional states (arriving, waiting, happy, disappointed, leaving)
- ✅ Petting mechanic for bonus hearts
- ✅ Combo tracking system
- ✅ 8 unlockable teas with authentic Chinese names
- ✅ 6 unique cat characters with favorites

## 🎨 Screen Layout (IMPLEMENTED - 800x600)

```
┌──────────────────────────────────────────────────────────────┐
│  🌸 Border (20px green)  ❤ Hearts: 42  Combo x3  [Menu] 🌸 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │    TEA DRAWER (Brown rect 230,40, 540x80)             │ │
│  │  Tea Drawer - Drag tea to kettle                      │ │
│  │  ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐  │ │
│  │  │🍵 │ │🍵 │ │🍵 │ │🍵 │ │🔒│ │🔒│ │🔒│ │🔒│  │ │
│  │  └───┘ └───┘ └───┘ └───┘ └───┘ └───┘ └───┘ └───┘  │ │
│  │  Jas   TGY   Silv  Dan   Viol  Dual  Leach  Gold    │ │
│  │  3s    3s    2s    3s    2s    4s    4s     4s       │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌──────────────────┐        CAT VISITING AREA             │
│  │  CHA BAN         │                                       │
│  │  (30,140,        │   😺 Mimi          😺 Luna            │
│  │   240x480)       │   [💭🍵]          [💭🍵]             │
│  │                  │   [❤❤❤❤❤]        [❤❤❤❤❤]          │
│  │  ♨♨♨           │   Wants: Jasmine   Wants: Oolong      │
│  │  💧 Hot Water   │                                       │
│  │  (120, 180)      │   😺 Tofu          😺 Ginger          │
│  │  [Draggable]     │   [💭🍵]          [💭🍵]             │
│  │                  │   [❤❤❤❤❤]        [❤❤❤❤░]          │
│  │  ☕ Tea Kettle  │                                       │
│  │  (120, 280)      │            😺 Petya                   │
│  │  [████░░] 80%    │            [💭🍵]                    │
│  │  State: Brewing  │            [❤❤❤❤❤]                 │
│  │                  │                                       │
│  │  🍶 Cha Hai     │   Cats spawn every 5s                 │
│  │  (120, 400)      │   Up to 5 cats at once               │
│  │  Empty/Filled    │   Patience drains over 15s           │
│  │                  │   Click happy cats to pet!           │
│  │  🫖🫖🫖🫖        │                                       │
│  │  🫖🫖🫖🫖        │                                       │
│  │  (8 tea cups)    │                                       │
│  │  70,500+         │                                       │
│  └──────────────────┘                                       │
│                                                              │
│  INSTRUCTIONS (Bottom):                                     │
│  1. Drag tea disk to kettle    5. Drag cha hai to cups     │
│  2. Drag hot water to kettle   6. Drag cups to cats        │
│  3. Wait for brewing            7. Pet happy cats for bonus!│
│  4. Drag kettle to cha hai                                  │
├──────────────────────────────────────────────────────────────┤
│  🌸 Border (20px green) - Cha ban on left, cats on right 🌸│
└──────────────────────────────────────────────────────────────┘
```

## 🎨 Original Design Mockup (Reference)

```
┌─────────────────────────────────────────────────────────────┐
│  🌸🌿 Decorative Border - Flowers & Greenery 🌿🌸          │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │  💜 HEARTS: 42    ⏱ SESSION: 5:23    🔥 COMBO: x3    │ │
│ ├─────────────────────────────────────────────────────────┤ │
│ │                                                         │ │
│ │  ┌─────────────────────────────────────────────────┐  │ │
│ │  │         TEA DRAWER (Top Center)                 │  │ │
│ │  │  ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐   │  │ │
│ │  │  │🍵 │ │🍵 │ │🍵 │ │🔒│ │🔒│ │🔒│ │🔒│   │  │ │
│ │  │  └───┘ └───┘ └───┘ └───┘ └───┘ └───┘ └───┘   │  │ │
│ │  │  Jas-  Te    Silv  Dan   Viol  Dual  Leach     │  │ │
│ │  │  mine  Guan  er    Tsun  et    ist   Tears     │  │ │
│ │  │  3s    Yin   2s    3s    2s    4s    4s        │  │ │
│ │  └─────────────────────────────────────────────────┘  │ │
│ │                                                         │ │
│ │  ┌──────────────────┐      TEA TABLE VIEW            │ │
│ │  │  CHA BAN (Tea    │                                 │ │
│ │  │  Board/Tray)     │      CAT VISITING AREA         │ │
│ │  │                  │                                 │ │
│ │  │  💧 Hot Water   │   😺        😺        😺      │ │
│ │  │  ☕ Tea Kettle  │  [💭]      [💭]      [💭]     │ │
│ │  │  (Brewing...)    │  Mimi      Luna      Tofu      │ │
│ │  │  [████░░] 80%    │  Oolong    White     Jasmine    │ │
│ │  │                  │  [❤❤❤❤❤]  [❤❤❤❤❤]  [❤❤❤❤❤]  │ │
│ │  │  🍶 Cha Hai     │                                 │ │
│ │  │  (Pour vessel)   │                                 │ │
│ │  │                  │         😺        😺           │ │
│ │  │  🫖🫖🫖🫖        │        [💭]      [💭]          │ │
│ │  │  🫖🫖🫖🫖        │        Ginger    Petya          │ │
│ │  │  (8 tea cups)    │        Pu-erh    Red Tea       │ │
│ │  │                  │        [❤❤❤❤░]  [❤❤❤❤❤]      │ │
│ │  │  [Click to pet]  │                                 │ │
│ │  └──────────────────┘                                 │ │
│ │                                                         │ │
│ │  💡 TIP: tea → kettle + water → brew → cha hai → cups → cats │ │
│ └─────────────────────────────────────────────────────┘ │
│  🌸🌿 Decorative Border - Bamboo & Cherry Blossoms 🌿🌸│
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Implementation Details (Current State)

### Module Structure
```
game/
├── tea_objects/           # Modular equipment system
│   ├── __init__.py       # Exports all classes
│   ├── tea_disk.py       # 80 lines - Draggable tea selection
│   ├── tea_kettle.py     # 127 lines - Gaiwan brewing logic
│   ├── hot_water_kettle.py  # 54 lines - Water source
│   ├── cha_hai.py        # 66 lines - Fairness cup
│   ├── tea_cup.py        # 60 lines - Individual serving cups
│   └── cat_visitor.py    # 190 lines - Cat AI and emotions
├── scenes/
│   └── game_scene.py     # 324 lines - Main game orchestration
└── sprite_loader.py      # Sprite grid loading system
```

### Key Metrics
- **Total Code:** ~900 lines across modular files
- **Tea Types:** 8 authentic Chinese teas
- **Cat Characters:** 6 unique personalities
- **Draggable Objects:** 4 types (tea disks, water kettle, kettle, cups)
- **Cat Spawn Rate:** 5 seconds
- **Max Cats:** 5 simultaneous visitors
- **Patience Timer:** 15 seconds per cat
- **Brew Times:** 2-4 seconds (tea dependent)
- **Pet Bonus Window:** 2.5 seconds after serving
- **Screen Size:** 800x600px (scalable)

### State Management
```python
# Tea Kettle States
STATE_EMPTY → STATE_HAS_TEA → STATE_BREWING → STATE_READY → (loop)

# Cat States
arriving → waiting → (happy/disappointed) → leaving

# Game Flow
Select Tea → Add Water → Brew → Pour → Fill Cups → Serve → Pet
```

### Collision Detection
- **Contains Point:** Used for all drag targets
- **Circle Collision:** Tea disks and cups (radius-based)
- **Rectangle Collision:** Equipment and cats (bounding boxes)
- **Snap Back:** Failed drops return objects to base_position

### Performance Features
- **Sprite Caching:** All sprites loaded once at startup
- **Fallback System:** Colored shapes when sprites missing
- **Efficient Updates:** Only active objects update
- **Smart Spawning:** Checks for available slots before spawning

### Known Limitations
- No sound effects yet
- Particle effects planned but not implemented
- Save system creates file in /Users/vitaliirybalko/git/data/
- No tutorial or help screen (instructions shown inline)
- Combo system tracks but doesn't affect gameplay

### Next Implementation Steps
1. Generate all sprites via DALL-E (~$1.00 cost)
2. Add sound effects (brewing, pouring, cat sounds)
3. Implement particle effects (steam, sparkles, hearts, petals)
4. Add proper save/load UI
5. Create tutorial overlay for first-time players
6. Polish combo system with visual feedback
7. Add achievements and statistics screen

---

## 🍵 Traditional Tea Equipment Design

### Tea Drawer (Top Center - Expandable)
```
┌───────────────────────────────────────────────────────┐
│                    TEA STORAGE                        │
│  ╔═══╗ ╔═══╗ ╔═══╗ ╔═══╗ ╔═══╗ ╔═══╗ ╔═══╗ ╔═══╗   │
│  ║🍵 ║ ║🍵 ║ ║🍵 ║ ║🔒║ ║🔒║ ║🔒║ ║🔒║ ║🔒║   │
│  ╚═══╝ ╚═══╝ ╚═══╝ ╚═══╝ ╚═══╝ ╚═══╝ ╚═══╝ ╚═══╝   │
│  Jasmine Te Guan  Silver  Dan    Violet Dualist      │
│  Oolong  Yin      Needle  Tsun   Ya Bao  Red Tea    │
│  ⏱ 3s   ⏱ 3s     ⏱ 2s    ⏱ 3s   ⏱ 2s   ⏱ 4s       │
│                                                       │
│  [← Scroll] Shows 6 at a time [Scroll →]            │
└───────────────────────────────────────────────────────┘

Fe 😺 Cat Visiting Area (Center-Right)

### Cat Display
```
Each Cat Slot:
┌──────────────┐
│     😺       │  <- Cat sprite (sitting)
│              │
│    [💭🍵]    │  <- Thought bubble with tea type
│              │
│    MIMI      │  <- Cat name
│  Wants:      │
│  Jasmine     │  <- Tea request
│  Oolong      │
│              │
│  [❤❤❤❤❤]   │  <- Patience meter (5 hearts)
│  Click: Pet  │  <- Interaction hint
└──────────────┘

Up to 5 cats visible at once
3 cats in top row, 2 in bottom row
```

### Cat States & Animations
```
ARRIVING:
😺 → Walks in from side, sits down
     Shows thought bubble
     Full patience (5 hearts)

WAITING:
😺💭 Patience slowly decreasing
     Tail swishing gently
     Occasional meow

IMPATIENT:
😿💭 Only 1-2 hearts left
     Shaking, ears back
     Faster tail movement

HAPPY (Correct Tea):
😸✨ Hearts burst animation!
     Purring particle effects
     Drinks tea happily
     Can be pet for bonus!

DISAPPOINTED (Wrong Tea):
😿💔 Loses 1 patience heart
     Sad expression
     Still waiting...

LEAVING:
😿→ Walks away if patience runs out
     Or walks away happily if served
```

### Petting Mechanic
```
When Cat is Happy (just served correct tea):
┌──────────────┐
│     😸✨     │
│              │
│  [PET ME!]   │  <- Click here!
│   🐾         │
│              │
│  +1 Bonus    │
│  Heart!      │
└──────────────┘

Effects:
- Click on happy cat
- Hand cursor appears
- Cat purrs louder
- Extra heart particle
- Cat stays a bit longer
- Increases friendship level
```
│  ║   └──────────┘            ║  │
│  ║                            ║  │
│  ║   TEA CUPS (Pialas)       ║  │
│  ║   🫖 🫖 🫖 🫖            ║  │
│  ║   🫖 🫖 🫖 🫖            ║  │
│  ║   [8 small cups]           ║  │
│  ║                            ║  │
│  ╚════════════════════════════╝  │
│  Traditional bamboo tea tray    │
└──────────────────────────────────┘
```

### Hot Water Kettle
```
Always Ready:        Pouring Water:       Refilling:
┌──────────┐        ┌──────────┐        ┌──────────┐
│  ♨♨♨    │        │  💧→→    │        │  ~~~~    │
│          │        │  Pouring │        │ Refill   │
│  Ready   │   →    │  Hot     │   →    │ (auto)   │
│ Drag to  │        │  Water   │        │  100°C   │
│ Tea Pot  │        │          │        │          │
└──────────┘        └──────────┘        └──────────┘

Features:
- Always has hot water (unlimited)
- Drag to tea kettle to add water
- Shows steam particles (♨)
- Pouring animation with water stream
- Essential step for brewing tea!
```

### Tea Kettle States (IMPLEMENTED)
```python
STATE_EMPTY = "empty"           # Ready for tea leaves
STATE_HAS_TEA = "has_tea"       # Tea added, needs water
STATE_BREWING = "brewing"       # Water added, actively brewing
STATE_READY = "ready"           # Brewing complete, ready to pour

Transitions:
EMPTY --[add_tea()]--> HAS_TEA
HAS_TEA --[add_water()]--> BREWING
BREWING --[timer >= duration]--> READY
READY --[pour_to_cha_hai()]--> EMPTY

Visual States:
- empty: Grey sprite, "Empty" text
- has_tea: Tea color sprite, "Add ♨" text
- brewing: Animated sprite, "80%" progress text
- ready: Golden sprite, "Ready!" text

update(dt) method:
  if state == BREWING:
    brew_timer += dt
    if brew_timer >= brew_duration:
      state = READY
```

### Cha Hai (Fairness Cup)
```
Empty:               Filled:              Pouring:
┌─────────┐         ┌─────────┐         ┌─────────┐
│         │         │  ~~~~   │         │  ~~~→   │
│  Empty  │    →    │  Jasmine│    →    │  Pour   │
│         │         │  Tea    │         │  to     │
│         │         │  Ready  │         │  Cups   │
└─────────┘         └─────────┘         └─────────┘

Purpose: Ensures equal strength tea for all cups
Drag to cups: pours evenly into all 8 cups
```

### Tea Cups (8 Pialas)
`` 🎮 Complete Drag & Drop Flow (IMPLEMENTED)

### Step-by-Step Gameplay
```
1. SELECT TEA
   Tea Drawer (8 disks) → Click and drag tea disk
   ↓
   Disk follows cursor, shows dragging state
   Drop on kettle: kettle.add_tea(tea_data) → STATE_HAS_TEA

2. ADD WATER
   Hot Water Kettle (always ready) → Drag to tea kettle
   ↓
   Drop on kettle: kettle.add_water() → STATE_BREWING
   Auto-starts brewing timer with tea's brew_duration
   Progress bar updates: [████░░] 80%

3. WAIT FOR BREWING
   Tea Kettle updates every frame
   ↓
   self.brew_timer += dt
   if brew_timer >= brew_duration: STATE_READY
   Progress: min(1.0, brew_timer / brew_duration) * 100%

4. POUR TO CHA HAI
   Drag tea kettle handle → Drop on Cha Hai
   ↓
   kettle.pour_to_cha_hai() returns tea_data
   cha_hai.pour_from_kettle(tea_data) accepts tea
   Kettle resets to STATE_EMPTY

5. FILL CUPS
   Drag Cha Hai → Drop on any empty cup
   ↓
   cha_hai.pour_to_cup() returns tea_data
   cup.fill(tea_data) accepts tea
   Cha Hai empties, ready for next batch

6. SERVE CAT
   Drag filled cup → Drop on waiting cat
   ↓
   cat.receive_tea(tea_id) checks favorite
   ✓ Correct: {"match": True, "hearts": 3}
          cat.state = "happy", can be petted
   ✗ Wrong: {"match": False, "hearts": 1}
          cat.state = "disappointed"

7. PET HAPPY CAT (Optional Bonus)
   Click on happy cat (state="happy", animation_timer < 2500ms)
   ↓
   cat.pet() returns 1 bonus heart
   game_state.add_hearts(1)
   Cat leaves happily after 3 seconds
```

### Sprite System (IMPLEMENTED)
```
SpriteLoader Singleton:
- Loads 1024x1024 grid images from assets/images/grids/
- Automatically splits grids into individual sprites
- Removes black (#000000) backgrounds
- Caches all sprites in memory
- Provides fallback colored shapes if sprites missing

Supported Entities:
- Cats: mimi, luna, tofu, ginger, petya, lapilaps
  Variants: normal, happy, disappointed, impatient
- Equipment: gaiwan, kettle, chahai, teacup, tea_disks
  Variants: empty, filled, brewing, ready, etc.
- Particles: steam, sparkles, hearts, petals
- UI: borders, buttons, hearts display

Generation:
- DALL-E 3 script: python generate_cat_image.py <entity>
- Prompts in documents/IMAGE_PROMPTS.md
- Cost: ~$0.04 per image
```

### Drag Visual Feedback
```
Dragging Item:
- Item follows cursor
- Semi-transparent ghost at origin
- Drop shadow under dragged item
- Valid drop zones highlight green
- Invalid zones remain neutral

Valid Drop:
- Green glow on target
- Snap to position animation
- Success particle effect
- Sound: pleasant ding

Invalid Drop:
- Red flash on target
- Item returns to origin (smooth bounce)
- Error sound: gentle buzz
```

**Error Feedback:**
- Wrong tea: Gentle red flash + disappointed sound
- Cat leaves: Fade out + sad particles
- Can't brew: Shake animation + error sound

### Accessibility

- Large click targets (minimum 60x60px)
- High contrast for all text
- Clear visual states (locked/unlocked/brewing/ready)
- Animation can be reduced (option in settings)
- Colorblind-friendly indicators (not just color)

### Mobile-Ready Considerations (Future)

- Touch targets 44x44px minimum
- Swipe to scroll tea menu
- Tap to select, tap cat to serve
- Larger UI elements
- Simplified effects for performance

---

## Implementation Priority

### Phase 1: Core Visual Improvements
1. Better color scheme and backgrounds
2. Improved cat sprites with expressions
3. Better tea cup cards with clear states
4. Proper thought bubbles

### Phase 2: Polish & Feedback
1. Hover and click states
2. Animations (brewing, serving, reactions)
3. Particle effects
4. Better notifications

### Phase 3: Atmosphere
1. Background decorations
2. Ambient animations
3. Sound effects integration
4. Weather/time effects

---

**Goal:** Transform from functional prototype to delightful, polished experience that your girlfriend will love! 💕
