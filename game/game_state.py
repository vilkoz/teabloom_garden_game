"""Game state management"""
import json
from pathlib import Path


class GameState:
    """Manages the overall game state and progression"""
    
    def __init__(self):
        self.hearts = 0
        
        # Load tea data to get defaults and unlock costs
        self.teas_data = self._load_teas_data()
        self.cat_data = self._load_cats_data()
        
        # Set default unlocked teas from data
        self.unlocked_teas = [tea['id'] for tea in self.teas_data if tea.get('unlocked', False)]
        self.unlocked_cats = [cat['id'] for cat in self.cat_data if cat.get('unlocked', False)]
        self.statistics = {
            'teas_served': 0,
            'cats_satisfied': 0,
            'cats_disappointed': 0,
            'total_hearts': 0,
            'correct_serves': 0,
            'wrong_serves': 0,
            'play_time': 0.0
        }
        self.current_combo = 0
        self.best_combo = 0
        
        # Save file path
        self.save_path = Path(__file__).parent.parent / "data" / "save_data.json"
        
        # Try to load existing save
        self.load_progress()
    
    def _load_teas_data(self):
        """Load teas data from JSON file"""
        teas_path = Path(__file__).parent.parent / "data" / "teas_data.json"
        try:
            with open(teas_path, 'r') as f:
                data = json.load(f)
                return data.get('teas', []) if isinstance(data, dict) else data
        except Exception as e:
            print(f"Failed to load teas data: {e}")
            return []

    def _load_cats_data(self):
        """Load cats data from JSON file"""
        cats_path = Path(__file__).parent.parent / "data" / "cats_data.json"
        try:
            with open(cats_path, 'r') as f:
                data = json.load(f)
                return data.get('cats', []) if isinstance(data, dict) else data
        except Exception as e:
            print(f"Failed to load cats data: {e}")
            return []
    
    def add_hearts(self, amount):
        """Add hearts to the player's total"""
        self.hearts += amount
        self.statistics['total_hearts'] += amount
        self.check_unlocks()
    
    def spend_hearts(self, amount):
        """Spend hearts (for unlocks)"""
        if self.hearts >= amount:
            self.hearts -= amount
            return True
        return False
    
    def unlock_tea(self, tea_id):
        """Unlock a new tea type"""
        if tea_id not in self.unlocked_teas:
            self.unlocked_teas.append(tea_id)
            return True
        return False
    
    def unlock_cat(self, cat_id):
        """Unlock a new cat"""
        if cat_id not in self.unlocked_cats:
            self.unlocked_cats.append(cat_id)
            return True
        return False
    
    def is_tea_unlocked(self, tea_id):
        """Check if a tea is unlocked"""
        return tea_id in self.unlocked_teas
    
    def is_cat_unlocked(self, cat_id):
        """Check if a cat is unlocked"""
        return cat_id in self.unlocked_cats
    
    def record_serve(self, correct):
        """Record a tea serving"""
        self.statistics['teas_served'] += 1
        if correct:
            self.statistics['correct_serves'] += 1
            self.statistics['cats_satisfied'] += 1
            self.current_combo += 1
            if self.current_combo > self.best_combo:
                self.best_combo = self.current_combo
        else:
            self.statistics['wrong_serves'] += 1
            self.statistics['cats_disappointed'] += 1
            self.current_combo = 0
    
    def get_combo_bonus(self):
        """Get bonus hearts from combo"""
        if self.current_combo >= 5:
            return 1
        return 0
    
    def check_unlocks(self):
        """Check if player has reached unlock milestones"""
        unlocks = []
        
        # Tea unlocks based on unlock_cost from data
        for tea in self.teas_data:
            unlock_cost = tea.get('unlock_cost', 0)
            if unlock_cost > 0 and self.statistics['total_hearts'] >= unlock_cost:
                if self.unlock_tea(tea['id']):
                    unlocks.append(('tea', tea['id']))

        for cat in self.cat_data:
            unlock_cost = cat.get('unlock_requirement', 0)
            if unlock_cost > 0 and self.statistics['total_hearts'] >= unlock_cost:
                if self.unlock_cat(cat['id']):
                    unlocks.append(('cat', cat['id']))
        
        return unlocks
    
    def update_playtime(self, dt):
        """Update total play time"""
        self.statistics['play_time'] += dt
    
    def save_progress(self):
        """Save game progress to file"""
        save_data = {
            'hearts': self.hearts,
            'unlocked_teas': self.unlocked_teas,
            'unlocked_cats': self.unlocked_cats,
            'statistics': self.statistics,
            'best_combo': self.best_combo
        }
        
        try:
            with open(self.save_path, 'w') as f:
                json.dump(save_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save: {e}")
            return False
    
    def load_progress(self):
        """Load game progress from file"""
        if not self.save_path.exists():
            return False
        
        try:
            with open(self.save_path, 'r') as f:
                save_data = json.load(f)
            
            self.hearts = save_data.get('hearts', 0)
            self.unlocked_teas = save_data.get('unlocked_teas', self.unlocked_teas)
            self.unlocked_cats = save_data.get('unlocked_cats', self.unlocked_cats)
            self.statistics = save_data.get('statistics', self.statistics)
            self.best_combo = save_data.get('best_combo', 0)
            
            return True
        except Exception as e:
            print(f"Failed to load save: {e}")
            return False
    
    def reset_progress(self):
        """Reset all progress"""
        self.__init__()
        if self.save_path.exists():
            self.save_path.unlink()
