# Tea Garden Cats - Traditional Tea Ceremony Game

## 🎮 New Game Concept: Chinese Tea Ceremony Simulator

### 🍵 Core Experience
An authentic Chinese tea ceremony experience where you serve tea to visiting cats using traditional tea equipment and methods. Educational, relaxing, and beautiful.

### 🎯 Core Gameplay Loop
1. **Select tea** from the tea drawer (click tea disk)
2. **Drag tea leaves** to the tea kettle
3. **Drag hot water kettle** to pour water into tea kettle
4. **Wait for brewing** (different teas, different times)
5. **Pour from tea kettle** into cha hai (fairness cup)
6. **Pour from cha hai** into small cups (8 pialas)
7. **Serve cups** to waiting cats by dragging
8. **Pet satisfied cats** for bonus hearts!
9. **Unlock new teas** as you progress

## 🎨 Screen Layout (1024x768) - Tea Table View

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

### Tea Kettle States
```
Empty:               With Tea Leaves:     With Water Added:
┌──────────┐        ┌──────────┐        ┌──────────┐
│          │        │  🍵      │        │  🍵💧    │
│          │        │  Jasmine │        │  Jasmine │
│  Empty   │   →    │  Oolong  │   →    │  Ready   │
│          │        │ Need H₂O │        │ to brew! │
└──────────┘        └──────────┘        └──────────┘
                    Drag water here!     Auto-starts brewing

Brewing:             Ready:               Pouring:
┌──────────┐        ┌──────────┐        ┌──────────┐
│  🍵💨    │        │  🍵✨    │        │  🍵→→    │
│  Jasmine │        │  Jasmine │        │  Pouring │
│  [████░] │   →    │  Ready!  │   →    │  to Cha  │
│  80% 2.4s│        │ Drag→Cha │        │   Hai    │
└──────────┘        └──────────┘        └──────────┘
Wait or quick-brew   Brewing complete!   Serving time!
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
`` 🎮 Complete Drag & Drop Flow

### Step-by-Step Gameplay
```
1. SELECT TEA
   Tea Drawer → Click tea disk
   ↓
   Disk highlights, cursor changes to tea icon

2. BREW TEA
   Drag tea disk → Drop on Kettle
   ↓
   Kettle shows tea + brewing animation
   Progress bar: [████░░] 80%
   Wait 2-4 seconds (or quick-brew)

3. POUR TO CHA HAI
   Drag Kettle → Drop on Cha Hai
   ↓
   Pouring animation
   Cha Hai fills with tea
   Kettle becomes empty

4. FILL CUPS
   Drag Cha Hai → Drop on Cup Grid
   ↓
   Auto-fills all 8 cups evenly
   OR drag to individual cups
   Cha Hai becomes empty

5. SERVE CAT
   Drag Cup → Drop on Cat
   ↓
   Check if correct tea type
   ✓ Correct: Cat happy, earn hearts, can pet
   ✗ Wrong: Cat disappointed, lose patience

6. PET (Optional Bonus)
   Click on Happy Cat
   ↓
   Petting animation
   +1 Bonus heart
   Cat purrs and leaves happily
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
