"""Tea Ceremony Game Scene - New Implementation"""
import pygame
import random
import json
import math
from ..sprite_loader import get_sprite_loader


class TeaDisk:
    """Represents a draggable tea disk in the tea drawer"""
    def __init__(self, tea_data, position):
        self.tea_data = tea_data
        self.base_position = position
        self.position = list(position)
        self.dragging = False
        self.radius = 40
        self.sprite_loader = get_sprite_loader()
        
    def draw(self, screen):
        x, y = int(self.position[0]), int(self.position[1])
        
        # Try to get sprite for this tea
        tea_id = self.tea_data['id']
        sprite = self.sprite_loader.get_sprite('tea_disks', tea_id)
        
        if sprite:
            # Draw sprite centered
            sprite_rect = sprite.get_rect(center=(x, y))
            screen.blit(sprite, sprite_rect)
        else:
            # Fallback to colored circle
            color = self.tea_data.get('color', (100, 150, 100))
            pygame.draw.circle(screen, color, (x, y), self.radius)
            pygame.draw.circle(screen, (80, 60, 40), (x, y), self.radius, 2)
        
        # Draw tea name (shortened)
        font = pygame.font.Font(None, 16)
        name = self.tea_data['name'][:8]
        text_surface = font.render(name, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(x, y - 5))
        
        # Add background for text
        bg_rect = text_rect.inflate(4, 2)
        s = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, 150), s.get_rect(), border_radius=3)
        screen.blit(s, bg_rect)
        screen.blit(text_surface, text_rect)
        
        # Draw brew time
        time_text = f"{self.tea_data['brew_time']}s"
        time_surface = font.render(time_text, True, (255, 255, 200))
        time_rect = time_surface.get_rect(center=(x, y + 10))
        
        bg_rect2 = time_rect.inflate(4, 2)
        s2 = pygame.Surface(bg_rect2.size, pygame.SRCALPHA)
        pygame.draw.rect(s2, (0, 0, 0, 150), s2.get_rect(), border_radius=3)
        screen.blit(s2, bg_rect2)
        screen.blit(time_surface, time_rect)
        
        # Draw lock if not unlocked
        if not self.tea_data.get('unlocked', False):
            lock_sprite = self.sprite_loader.get_sprite('lock_icon', 'single')
            if lock_sprite:
                lock_rect = lock_sprite.get_rect(center=(x, y))
                screen.blit(lock_sprite, lock_rect)
            else:
                s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (0, 0, 0, 150), (self.radius, self.radius), self.radius)
                screen.blit(s, (x - self.radius, y - self.radius))
                20
        self.height = 120
        self.sprite_loader = get_sprite_loader() = pygame.font.Font(None, 24)
                lock_surface = lock_font.render("🔒", True, (255, 200, 0))
                lock_rect = lock_surface.get_rect(center=(x, y))
                screen.blit(lock_surface, lock_rect)
    
    def contains_point(self, point):
        dx = point[0] - self.position[0]
        dy = point[1] - self.position[1]
        return dx*dx + dy*dy <= self.radius*self.radius
    
    def snap_back(self):
        self.position = list(self.base_position)


class TeaKettle:
    """Represents the tea kettle on the cha ban"""
    STATE_EMPTY = "empty"
    STATE_HAS_TEA = "has_tea"
    STATE_BREWING = "brewing"
    STATE_READY = "ready"
    
    def __init__(self, position):
        self.position = position
        self.state = self.STATE_EMPTY
        self.tea_data = None
        self.brew_timer = 0
        self.brew_duration = 0
        self.width = 100
        self.height = 100
        
    def add_tea(self, tea_data):
        if self.state == self.STATE_EMPTY:
            self.state = self.STATE_HAS_TEA
            self.tea_data = tea_data
            return True
        return False
    
    def add_water(self):
        if self.state == self.STATE_HAS_TEA:
            self.state = self.STATE_BREWING
            self.brew_duration = self.tea_data['brew_time']  # Keep in seconds to match dt
            self.brew_timer = 0
            return True
        return False
    
    def update(self, dt):
        if self.state == self.STATE_BREWING:
            self.brew_timer += dt
            if self.brew_timer >= self.brew_duration:
                self.state = self.STATE_READY
    
    def pour_to_cha_hai(self):
        if self.state == self.STATE_READY:
            tea_data = self.tea_data
            self.reset()
            return tea_data
        return None
    
    def reset(self):
        self.state = self.STATE_EMPTY
        self.tea_data = None
        self.brew_timer = 0
        self.brew_duration = 0
    
    def get_brew_progress(self):
        if self.state == self.STATE_BREWING and self.brew_duration > 0:
            return min(1.0, self.brew_timer / self.brew_duration)
        return 0
    
    def draw(self, screen):
        x, y = self.position
        Map state to sprite variant
        sprite_variant = None
        if self.state == self.STATE_EMPTY:
            sprite_variant = "empty"
        elif self.state == self.STATE_HAS_TEA:
            sprite_variant = "tea_leaves"
        elif self.state == self.STATE_BREWING:
            sprite_variant = "brewing"
        elif self.state == self.STATE_READY:
            sprite_variant = "ready"
        
        # Try to get sprite
        sprite = self.sprite_loader.get_sprite('gaiwan', sprite_variant)
        
        if sprite:
            sprite_rect = sprite.get_rect(center=(x, y))
            screen.blit(sprite, sprite_rect)
        else:
            # Fallback to colored shapes
            if self.state == self.STATE_EMPTY:
                color = (200, 200, 200)
            elif self.state == self.STATE_HAS_TEA:
                color = self.tea_data.get('color', (100, 150, 100))
            elif self.state == self.STATE_BREWING:
                color = (180, 150, 100)
            else:  # READY
                color = (255, 215, 0)
            
            pygame.draw.rect(screen, color, (x - 40, y - 40, 80, 80), border_radius=10)
            pygame.draw.rect(screen, (80, 60, 40), (x - 40, y - 40, 80, 80), 3, border_radius=10)
            pygame.draw.circle(screen, color, (x + 45, y), 10)
            pygame.draw.arc(screen, (80, 60, 40), (x - 60, y - 30, 30, 60), 0, math.pi, 3)
        
        # Draw state text below sprite
        font = pygame.font.Font(None, 16)
        if self.state == self.STATE_EMPTY:
            text = "Empty"
        elif self.state == self.STATE_HAS_TEA:
            text = "Add ♨"
        elif self.state == self.STATE_BREWING:
            progress = int(self.get_brew_progress() * 100)
            text = f"{progress}%"
        elif self.state == self.STATE_READY:
            text = "Ready!"
        else:
            text = ""
        
        if text:
            text_surface = font.render(text, True, (50, 50, 50))
            text_rect = text_surface.get_rect(center=(x, y + 70))
            # Background for text
            bg_rect = text_rect.inflate(6, 3)
            pygame.draw.rect(screen, (255, 255, 255), bg_rect, border_radius=3)
            screen.blit(text_surface, text_rect)
    
    def contains_point(self, point):
        x, y = self.position
        return (x - 50 <= point[0] <= x + 50 and y - 50 <= point[1] <= y + 50)


class HotWaterKettle:
    """Represents the hot water kettle - always ready"""
    def __init__(self, position):
        self.base_position = position
        self.position = list(position)
        self.dragging = False
        self.width = 80
        self.height = 80
        
    def draw(self, screen):
        x, y = int(self.position[0]), int(self.position[1])
        
        # Draw kettle body
        pygame.draw.rect(screen, (100, 100, 120), (x - 35, y - 35, 70, 70), border_radius=8)
        pygame.draw.rect(screen, (60, 60, 80), (x - 35, y - 35, 70, 70), 3, border_radius=8)
        
        # Draw spout
        pygame.draw.circle(screen, (100, 100, 120), (x + 40, y), 8)
        
        # Draw steam
        font = pygame.font.Font(None, 20)
        steam_text = font.render("♨♨♨", True, (200, 220, 255))
        steam_rect = steam_text.get_rect(center=(x, y - 50))
        screen.blit(steam_text, steam_rect)
        
        # Draw label
        label_font = pygame.font.Font(None, 14)
        label_text = label_font.render("Hot Water", True, (255, 255, 255))
        label_rect = label_text.get_rect(center=(x, y))
        screen.blit(label_text, label_rect)
    
    def contains_point(self, point):
        x, y = self.position
        return (x - 40 <= point[0] <= x + 40 and y - 40 <= point[1] <= y + 40)
    
    def snap_back(self):
        self.position = list(self.base_position)


class ChaHai:
    """Represents the fairness cup"""
    def __init__(self, position):
        self.position = position
        self.tea_data = None
        self.width = 90
        self.height = 90
        self.sprite_loader = get_sprite_loader()
        
    def pour_from_kettle(self, tea_data):
        if self.tea_data is None:
            self.tea_data = tea_data
            return True
        return False
    
    def pour_to_cup(self):
        if self.tea_data:
            tea_data = self.tea_data
            self.tea_data = None
            return tea_data
        return None
    
    def draw(self, screen):
        x, y = self.position
        
        # Get appropriate sprite
        sprite_variant = "empty" if self.tea_data is None else "filled"
        sprite = self.sprite_loader.get_sprite('chahai', sprite_variant)
        
        if sprite:
            sprite_rect = sprite.get_rect(center=(x, y))
            screen.blit(sprite, sprite_rect)
            
            # Label when filled
            if self.tea_data:
                font = pygame.font.Font(None, 14)
                label = font.render("Pour→", True, (50, 50, 50))
                label_rect = label.get_rect(center=(x, y + 50))
                bg_rect = label_rect.inflate(4, 2)
                pygame.draw.rect(screen, (255, 255, 255), bg_rect, border_radius=3)
                screen.blit(label, label_rect)
        else:
            # Fallback rendering
            color = (220, 220, 220) if self.tea_data is None else self.tea_data.get('color', (180, 120, 80))
            pygame.draw.ellipse(screen, color, (x - 30, y - 25, 60, 50))
            pygame.draw.ellipse(screen, (80, 60, 40), (x - 30, y - 25, 60, 50), 2)
            pygame.draw.circle(screen, color, (x + 35, y), 6)
            pygame.draw.arc(screen, (80, 60, 40), (x - 45, y - 15, 20, 30), 0, math.pi, 2)
            
            if self.tea_data:
                font = pygame.font.Font(None, 14)
                label = font.render("Pour→", True, (255, 255, 255))
                label_rect = label.get_rect(center=(x, y))
                screen.blit(label, label_rect)
    
    def contains_point(self, point):
        x, y = self.po20
        self.sprite_loader = get_sprite_loader()tion
        return (x - 35 <= point[0] <= x + 35 and y - 30 <= point[1] <= y + 30)


class TeaCup:
    """Represents a small tea cup"""
    def __init__(self, position, index):
        self.base_position = position
        self.position = list(position)
        self.index = index
        self.tea_data = None
        self.dragging = False
        self.radius = 18
        
    def fill(self, tea_data):
        if self.tea_data is None:
            self.tea_data = tea_data
            return True
        return False
    
    def empty(self):
        tea_data = self.tea_data
        self.tea_data = None
        return tea_data
    
    def draw(self, screen):
        x, y = int(self.position[0]), int(self.position[1])
        Get appropriate sprite
        sprite_variant = "empty" if self.tea_data is None else "filled"
        sprite = self.sprite_loader.get_sprite('teacup', sprite_variant)
        
        if sprite:
            sprite_rect = sprite.get_rect(center=(x, y))
            screen.blit(sprite, sprite_rect)
        else:
            # Fallback rendering
            color = (255, 255, 255) if self.tea_data is None else self.tea_data.get('color', (180, 120, 80))
            pygame.draw.circle(screen, color, (x, y), self.radius)
            pygame.draw.circle(screen, (80, 60, 40), (x, y), self.radius, 2)
            
            if self.tea_data:
            if self.tea_data:
            pygame.draw.circle(screen, self.tea_data.get('color', (180, 120, 80)), (x, y), self.radius - 5)
    
    def contains_point(self, point):
        dx = point[0] - self.position[0]
        dy = point[1] - self.position[1]
        return dx*dx + dy*dy <= self.radius*self.radius
    
    def snap_back(self):
        self.position = list(self.base_position)


class CatVisitor:
    """Enhanced cat for the visiting area"""
    def __init__(self, cat_data, slot_position, slot_index):
        self.cat_data = cat_data
        self.slot_position = slot_position
        self.slot_index = slot_index
        self.position = list(slo
        self.sprite_loader = get_sprite_loader()t_position)
        self.state = "arriving"
        self.patience = 100
        self.patience_max = 100
        self.waiting_time = 0
        self.waiting_limit = 15000  # 15 seconds
        self.served = False
        self.happiness = 0
        self.animation_timer = 0
        
    def update(self, dt):
        self.animation_timer += dt
        
        if self.state == "arriving":
            # Arrive from right
            target_x = self.slot_position[0]
            if self.position[0] > target_x:
                self.position[0] -= 0.5
            else:
                self.position[0] = target_x
                self.state = "waiting"
        
        elif self.state == "waiting":
            self.waiting_time += dt
            self.patience = max(0, 100 - (self.waiting_time / self.waiting_limit * 100))
            
            if self.patience <= 0:
                self.state = "leaving"
        
        elif self.state == "happy":
            # Wait a bit then leave
            if self.animation_timer > 3000:
                self.state = "leaving"
        
        elif self.state == "disappointed":
            if self.animation_timer > 2000:
                self.state = "leaving"
        
        elif self.state == "leaving":
            self.position[0] += 1
    
    def receive_tea(self, tea_id):
        if self.served:
            return None
        
        self.served = True
        favorite = self.cat_data.get('favorite_tea', '')
        
        if tea_id == favorite:
            self.state = "happy"
            self.happiness = 100
            self.animation_timer = 0
            return {"match": True, "hearts": 3}
        else:
            self.state = "disappointed"
            self.animation_timer = 0
            return {"match": False, "hearts": 1}
    
    def can_pet(self):
        return self.state == "happy" and self.animation_timer < 2500
    
    def peMap game state to sprite variant
        if self.state == "happy":
            sprite_variant = "happy"
        elif self.state == "disappointed":
            sprite_variant = "disappointed"
        elif self.patience < 40:
            sprite_variant = "impatient"
        else:
            sprite_variant = "normal"
        
        # Try to get cat sprite
        cat_id = self.cat_data['id']
        sprite = self.sprite_loader.get_sprite(cat_id, sprite_variant)
        
        if sprite:
            # Draw sprite centered
            sprite_rect = sprite.get_rect(center=(x, y))
            screen.blit(sprite, sprite_rect)
        else:
            # Fallback rendering
            cat_color = self.cat_data.get('color', (255, 140, 0))
            pygame.draw.circle(screen, cat_color, (x, y), 35)
            pygame.draw.circle(screen, (50, 50, 50), (x, y), 35, 2)
            
            ear_points_left = [(x - 20, y - 25), (x - 30, y - 45), (x - 10, y - 35)]
            ear_points_right = [(x + 20, y - 25), (x + 30, y - 45), (x + 10, y - 35)]
            pygame.draw.polygon(screen, cat_color, ear_points_left)
            pygame.draw.polygon(screen, cat_color, ear_points_right)
            pygame.draw.polygon(screen, (50, 50, 50), ear_points_left, 2)
            pygame.draw.polygon(screen, (50, 50, 50), ear_points_right, 2)
            
            if self.state == "happy":
                pygame.draw.arc(screen, (50, 50, 50), (x - 20, y - 10, 12, 8), 0, math.pi, 2)
                pygame.draw.arc(screen, (50, 50, 50), (x + 8, y - 10, 12, 8), 0, math.pi, 2)
            else:
                pygame.draw.circle(screen, (255, 255, 255), (x - 12, y - 5), 6)
                pygame.draw.circle(screen, (255, 255, 255), (x + 12, y - 5), 6)
                pygame.draw.circle(screen, (50, 50, 50), (x - 12, y - 5), 3)
                pygame.draw.circle(screen, (50, 50, 50), (x + 12, y - 5), 3)
            
            if self.state == "happy":
                pygame.draw.arc(screen, (50, 50, 50), (x - 8, y + 5, 16, 10), math.pi, 2*math.pi, 2)
            elif self.state == "disappointed":
                pygame.draw.circle(screen, (255, 255, 255), (x + 12, y - 5), 6)
            pygame.draw.circle(screen, (50, 50, 50), (x - 12, y - 5), 3)
            pygame.draw.circle(screen, (50, 50, 50), (x + 12, y - 5), 3)
        
        # Draw mouth based on state
        if self.state == "happy":
            pygame.draw.arc(screen, (50, 50, 50), (x - 8, y + 5, 16, 10), math.pi, 2*math.pi, 2)
        elif self.state == "disappointed":
            pygame.draw.arc(screen, (50, 50, 50), (x - 8, y + 15, 16, 10), 0, math.pi, 2)
        
        # Draw name below
        font = pygame.font.Font(None, 16)
        name_text = font.render(self.cat_data['name'], True, (100, 70, 50))
        name_rect = name_text.get_rect(center=(x, y + 50))
        screen.blit(name_text, name_rect)
        
        # Draw thought bubble with favorite tea
        if self.state == "waiting":
            bubble_x, bubble_y = x + 60, y - 40
            pygame.draw.circle(screen, (255, 255, 255), (bubble_x, bubble_y), 25)
            pygame.draw.circle(screen, (100, 100, 100), (bubble_x, bubble_y), 25, 2)
            pygame.draw.circle(screen, (255, 255, 255), (x + 45, y - 15), 8)
            pygame.draw.circle(screen, (255, 255, 255), (x + 40, y - 5), 5)
            
            # Draw tea emoji in bubble
            bubble_font = pygame.font.Font(None, 28)
            fav_tea_text = bubble_font.render("🍵", True, (100, 150, 100))
            fav_rect = fav_tea_text.get_rect(center=(bubble_x, bubble_y))
            screen.blit(fav_tea_text, fav_rect)
        
        # Draw patience bar
        if self.state == "waiting":
            bar_width = 60
            bar_height = 6
            bar_x = x - bar_width // 2
            bar_y = y + 65
            
            # Background
            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            
            # Patience fill
            patience_width = int(bar_width * (self.patience / 100))
            if self.patience > 60:
                color = (100, 200, 100)
            elif self.patience > 30:
                color = (255, 200, 0)
            else:
                color = (255, 100, 100)
            pygame.draw.rect(screen, color, (bar_x, bar_y, patience_width, bar_height))
    
    def is_off_screen(self):
        return self.position[0] > 900


class GameScene:
    def __init__(self, screen, game_state):
        self.screen = screen
        self.game_state = game_state
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Load tea data
        with open('data/teas_data.json', 'r') as f:
            tea_data = json.load(f)
            self.all_teas = tea_data if isinstance(tea_data, list) else tea_data.get('teas', [])
        
        # Load cat data
        with open('data/cats_data.json', 'r') as f:
            cat_data = json.load(f)
            self.all_cats = cat_data.get('cats', []) if isinstance(cat_data, dict) else cat_data
        
        # Tea drawer (top center)
        self.tea_disks = []
        self._init_tea_drawer()
        
        # Cha ban equipment (top left)
        self.hot_water_kettle = HotWaterKettle((120, 180))
        self.tea_kettle = TeaKettle((120, 280))
        self.cha_hai = ChaHai((120, 400))
        self.tea_cups = []
        self._init_tea_cups()
        
        # Cat visiting area (center-right)
        self.cat_visitors = []
        self.cat_spawn_timer = 0
        self.cat_spawn_interval = 5000  # 5 seconds
        
        # Dragging state
        self.dragging_object = None
        self.drag_offset = (0, 0)
        
        # UI
        self.menu_button_rect = pygame.Rect(self.width - 120, 10, 110, 40)
        
        # Spawn first cat
        self._spawn_cat()
    
    def _init_tea_drawer(self):
        """Initialize tea disks in the drawer"""
        start_x = 250
        spacing = 90
        y = 80
        
        for i, tea_data in enumerate(self.all_teas):
            x = start_x + (i % 8) * spacing
            disk = TeaDisk(tea_data, (x, y))
            self.tea_disks.append(disk)
    
    def _init_tea_cups(self):
        """Initialize 8 tea cups on the cha ban"""
        cup_positions = [
            (70, 500), (120, 500), (170, 500), (220, 500),
            (70, 550), (120, 550), (170, 550), (220, 550)
        ]
        for i, pos in enumerate(cup_positions):
            self.tea_cups.append(TeaCup(pos, i))
    
    def _spawn_cat(self):
        """Spawn a new cat in an available slot"""
        if len(self.cat_visitors) >= 5:
            return
        
        # Get available cats
        available_cats = [c for c in self.all_cats if c.get('unlocked', False)]
        if not available_cats:
            return
        
        # Find empty slot
        occupied_slots = [cat.slot_index for cat in self.cat_visitors]
        available_slots = [i for i in range(5) if i not in occupied_slots]
        
        if available_slots:
            slot_index = random.choice(available_slots)
            slot_y = 200 + slot_index * 90
            slot_x = 500
            
            cat_data = random.choice(available_cats)
            cat = CatVisitor(cat_data, (slot_x, slot_y), slot_index)
            cat.position = [850, slot_y]  # Start off-screen right
            self.cat_visitors.append(cat)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check menu button
            if self.menu_button_rect.collidepoint(mouse_pos):
                return "menu"
            
            # Check for petting cats
            for cat in self.cat_visitors:
                cat_rect = pygame.Rect(cat.position[0] - 40, cat.position[1] - 40, 80, 80)
                if cat_rect.collidepoint(mouse_pos) and cat.can_pet():
                    bonus = cat.pet()
                    if bonus > 0:
                        self.game_state.add_hearts(bonus)
                        return None
            
            # Check for dragging tea disks
            for disk in self.tea_disks:
                if disk.tea_data.get('unlocked', False) and disk.contains_point(mouse_pos):
                    self.dragging_object = disk
                    disk.dragging = True
                    self.drag_offset = (disk.position[0] - mouse_pos[0], disk.position[1] - mouse_pos[1])
                    return None
            
            # Check for dragging hot water kettle
            if self.hot_water_kettle.contains_point(mouse_pos):
                self.dragging_object = self.hot_water_kettle
                self.hot_water_kettle.dragging = True
                self.drag_offset = (self.hot_water_kettle.position[0] - mouse_pos[0], 
                                   self.hot_water_kettle.position[1] - mouse_pos[1])
                return None
            
            # Check for dragging tea kettle (to pour to cha hai)
            if self.tea_kettle.state == TeaKettle.STATE_READY and self.tea_kettle.contains_point(mouse_pos):
                self.dragging_object = "tea_kettle_pour"
                return None
            
            # Check for dragging cha hai (to pour to cups)
            if self.cha_hai.tea_data and self.cha_hai.contains_point(mouse_pos):
                self.dragging_object = "cha_hai_pour"
                return None
            
            # Check for dragging filled cups
            for cup in self.tea_cups:
                if cup.tea_data and cup.contains_point(mouse_pos):
                    self.dragging_object = cup
                    cup.dragging = True
                    self.drag_offset = (cup.position[0] - mouse_pos[0], cup.position[1] - mouse_pos[1])
                    return None
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_object:
                mouse_pos = pygame.mouse.get_pos()
                
                if isinstance(self.dragging_object, TeaDisk):
                    self.dragging_object.position[0] = mouse_pos[0] + self.drag_offset[0]
                    self.dragging_object.position[1] = mouse_pos[1] + self.drag_offset[1]
                
                elif isinstance(self.dragging_object, HotWaterKettle):
                    self.dragging_object.position[0] = mouse_pos[0] + self.drag_offset[0]
                    self.dragging_object.position[1] = mouse_pos[1] + self.drag_offset[1]
                
                elif isinstance(self.dragging_object, TeaCup):
                    self.dragging_object.position[0] = mouse_pos[0] + self.drag_offset[0]
                    self.dragging_object.position[1] = mouse_pos[1] + self.drag_offset[1]
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging_object:
                mouse_pos = pygame.mouse.get_pos()
                
                # Handle tea disk drop
                if isinstance(self.dragging_object, TeaDisk):
                    if self.tea_kettle.contains_point(mouse_pos):
                        if self.tea_kettle.add_tea(self.dragging_object.tea_data):
                            pass  # Tea added successfully
                    self.dragging_object.snap_back()
                    self.dragging_object.dragging = False
                
                # Handle hot water kettle drop
                elif isinstance(self.dragging_object, HotWaterKettle):
                    if self.tea_kettle.contains_point(mouse_pos):
                        self.tea_kettle.add_water()
                    self.dragging_object.snap_back()
                    self.dragging_object.dragging = False
                
                # Handle tea kettle pour to cha hai
                elif self.dragging_object == "tea_kettle_pour":
                    if self.cha_hai.contains_point(mouse_pos):
                        tea_data = self.tea_kettle.pour_to_cha_hai()
                        if tea_data:
                            self.cha_hai.pour_from_kettle(tea_data)
                
                # Handle cha hai pour to cups
                elif self.dragging_object == "cha_hai_pour":
                    for cup in self.tea_cups:
                        if cup.contains_point(mouse_pos) and not cup.tea_data:
                            tea_data = self.cha_hai.pour_to_cup()
                            if tea_data:
                                cup.fill(tea_data)
                            break
                
                # Handle cup drop on cat
                elif isinstance(self.dragging_object, TeaCup):
                    served = False
                    for cat in self.cat_visitors:
                        cat_rect = pygame.Rect(cat.position[0] - 40, cat.position[1] - 40, 80, 80)
                        if cat_rect.collidepoint(mouse_pos) and cat.state == "waiting":
                            tea_data = self.dragging_object.empty()
                            if tea_data:
                                result = cat.receive_tea(tea_data['id'])
                                if result:
                                    self.game_state.add_hearts(result['hearts'])
                                served = True
                            break
                    
                    self.dragging_object.snap_back()
                    self.dragging_object.dragging = False
                
                self.dragging_object = None
                self.drag_offset = (0, 0)
        
        return None
    
    def update(self, dt):
        # Update tea kettle brewing
        self.tea_kettle.update(dt)
        
        # Update cats
        for cat in self.cat_visitors[:]:
            cat.update(dt)
            if cat.is_off_screen():
                self.cat_visitors.remove(cat)
        
        # Spawn new cats
        self.cat_spawn_timer += dt
        if self.cat_spawn_timer >= self.cat_spawn_interval:
            self.cat_spawn_timer = 0
            self._spawn_cat()
        
        return None
    
    def draw(self):
        # Background
        self.screen.fill((245, 235, 220))
        
        # Draw decorative border (simple for now)
        border_color = (100, 150, 100)
        pygame.draw.rect(self.screen, border_color, (0, 0, self.width, 20))  # Top
        pygame.draw.rect(self.screen, border_color, (0, self.height - 20, self.width, 20))  # Bottom
        pygame.draw.rect(self.screen, border_color, (0, 0, 20, self.height))  # Left
        pygame.draw.rect(self.screen, border_color, (self.width - 20, 0, 20, self.height))  # Right
        
        # Draw tea drawer area
        pygame.draw.rect(self.screen, (139, 90, 60), (230, 40, 540, 80), border_radius=10)
        pygame.draw.rect(self.screen, (80, 50, 30), (230, 40, 540, 80), 3, border_radius=10)
        
        drawer_font = pygame.font.Font(None, 20)
        drawer_label = drawer_font.render("Tea Drawer - Drag tea to kettle", True, (255, 255, 200))
        drawer_rect = drawer_label.get_rect(center=(500, 30))
        self.screen.blit(drawer_label, drawer_rect)
        
        # Draw tea disks
        for disk in self.tea_disks:
            disk.draw(self.screen)
        
        # Draw cha ban area
        pygame.draw.rect(self.screen, (160, 120, 80), (30, 140, 240, 480), border_radius=10)
        
        cha_ban_font = pygame.font.Font(None, 20)
        cha_ban_label = cha_ban_font.render("Cha Ban", True, (255, 255, 200))
        cha_ban_rect = cha_ban_label.get_rect(center=(150, 150))
        self.screen.blit(cha_ban_label, cha_ban_rect)
        
        # Draw equipment on cha ban
        self.hot_water_kettle.draw(self.screen)
        self.tea_kettle.draw(self.screen)
        self.cha_hai.draw(self.screen)
        for cup in self.tea_cups:
            cup.draw(self.screen)
        
        # Draw cat area label
        cat_font = pygame.font.Font(None, 22)
        cat_area_label = cat_font.render("Cat Visitors", True, (100, 70, 50))
        cat_rect = cat_area_label.get_rect(center=(550, 160))
        self.screen.blit(cat_area_label, cat_rect)
        
        # Draw cats
        for cat in self.cat_visitors:
            cat.draw(self.screen)
        
        # Draw hearts counter
        hearts_font = pygame.font.Font(None, 28)
        hearts_text = hearts_font.render(f"❤ Hearts: {self.game_state.hearts}", True, (200, 50, 50))
        hearts_rect = hearts_text.get_rect(center=(650, 30))
        self.screen.blit(hearts_text, hearts_rect)
        
        # Draw combo
        if self.game_state.current_combo > 1:
            combo_font = pygame.font.Font(None, 24)
            combo_text = combo_font.render(f"Combo x{self.game_state.current_combo}!", True, (255, 150, 0))
            combo_rect = combo_text.get_rect(center=(650, 60))
            self.screen.blit(combo_text, combo_rect)
        
        # Draw menu button
        pygame.draw.rect(self.screen, (200, 200, 200), self.menu_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, (100, 100, 100), self.menu_button_rect, 2, border_radius=5)
        
        menu_font = pygame.font.Font(None, 24)
        menu_text = menu_font.render("Menu", True, (50, 50, 50))
        menu_rect = menu_text.get_rect(center=self.menu_button_rect.center)
        self.screen.blit(menu_text, menu_rect)
        
        # Draw instructions
        instructions = [
            "1. Drag tea disk to kettle",
            "2. Drag hot water to kettle",
            "3. Wait for brewing",
            "4. Drag kettle to cha hai",
            "5. Drag cha hai to cups",
            "6. Drag cups to cats",
            "7. Pet happy cats for bonus!"
        ]
        inst_font = pygame.font.Font(None, 14)
        for i, instruction in enumerate(instructions):
            inst_text = inst_font.render(instruction, True, (100, 70, 50))
            inst_rect = inst_text.get_rect(topleft=(300, 520 + i * 14))
            self.screen.blit(inst_text, inst_rect)
