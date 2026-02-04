# Tea Garden Cats 🐱🍵

A cozy game about serving Chinese tea to adorable cats!

## 🎮 How to Play

1. **Welcome Cats** - Cats will visit your tea garden randomly
2. **See Their Request** - Each cat shows a thought bubble with their desired tea
3. **Brew Tea** - Click on a tea type to start brewing
4. **Serve Tea** - When ready, drag the tea cup to the waiting cat
5. **Collect Hearts** - Correct teas make cats happy and earn you hearts!
6. **Unlock Content** - Use hearts to unlock new tea varieties and rare cats

## 🚀 Running the Game

### Using UV (Recommended)

```bash
# Install pygame dependency
uv sync

# Run the game
uv run main.py
```

### Using Python directly

```bash
# Install pygame
pip install pygame

# Run the game
python main.py
```

## 🐱 Cats

- **Mimi** - Orange tabby who loves Jasmine Oolong
- **Luna** - Elegant black cat who loves Te Guan Yin Oolong  
- **Tofu** - Fluffy white cat who loves Silver Needle White Tea
- **Ginger** - Calico who loves Ripe Pu-erh (Unlock: 20 correct serves)
- **Petya** - Grey Siberian Cat who loves Red Tea (Unlock: 50 hearts)
- **Lapilaps** - Rare Siamese who loves Violet Ya Bao (Unlock: 100 hearts)

## 🍵 Tea Types

### Starter Teas (Always Available)
- Jasmine Oolong - 3s brew, 1 heart
- Te Guan Yin Oolong - 3s brew, 1 heart
- Silver Needle White Tea - 2s brew, 1 heart

### Unlockable Teas
- Dan Tsun Oolong (5 hearts) - 3s brew, 2 hearts
- Violet Ya Bao (15 hearts) - 2s brew, 2 hearts
- Dualist Red Tea (30 hearts) - 4s brew, 2 hearts
- Leach Tears Ripe Pu-erh (50 hearts) - 4s brew, 3 hearts
- Golden Monkey Black Tea (75 hearts) - 4s brew, 3 hearts

## 🎯 Tips

- Serve 5 cats correctly in a row for a combo bonus!
- Each tea category has different brewing times
- Keep an eye on waiting cats - they'll leave after 30 seconds
- Check your statistics to track your progress

## 📁 Project Structure

```
tea_garden_cats/
├── main.py              # Game entry point
├── game/
│   ├── game_state.py   # Game state & save system
│   ├── entities/       # Cat & Tea classes
│   ├── scenes/         # Menu, Game, Stats scenes
│   └── ui/             # UI components
├── data/
│   ├── cats_data.json  # Cat definitions
│   ├── teas_data.json  # Tea definitions
│   └── save_data.json  # Your progress (auto-generated)
└── pyproject.toml      # Project configuration
```

## 💝 Made with Love

Created with ❤️ for someone who loves cats and Chinese tea.

Enjoy your cozy tea garden! 🌸🍵🐱
