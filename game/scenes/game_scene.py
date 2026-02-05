"""Main tea ceremony game scene"""
import pygame
import random
import json
from ..sprite_loader import get_sprite_loader
from ..tea_objects import TeaDisk, TeaKettle, HotWaterKettle, ChaHai, TeaCup, CatVisitor
from ..tea_objects.tea_god import TeaGod
from ..ui.tooltip import Tooltip


class GameScene:
    def __init__(self, screen, game_state):
        self.screen = screen
        self.game_state = game_state
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Get sprite loader
        self.sprite_loader = get_sprite_loader()
        
        # Load tea data
        with open('data/teas_data.json', 'r') as f:
            tea_data = json.load(f)
            self.all_teas = tea_data if isinstance(tea_data, list) else tea_data.get('teas', [])
            for tea in self.all_teas:
                tea['brew_time'] = tea.get('brew_time', 5.0) * 1000.0  # Default brew time if not specified
        
        # Load cat data
        with open('data/cats_data.json', 'r') as f:
            cat_data = json.load(f)
            self.all_cats = cat_data.get('cats', []) if isinstance(cat_data, dict) else cat_data
        
        # Tea drawer (top center)
        self.tea_disks = []
        self._init_tea_drawer()
        
        # Cha ban equipment (top left)
        self.hot_water_kettle = HotWaterKettle((120, 180), self.sprite_loader)
        self.tea_kettle = TeaKettle((120, 280), self.sprite_loader)
        self.cha_hai = ChaHai((120, 400), self.sprite_loader)
        self.tea_cups = []
        self._init_tea_cups()
        self.tea_god = TeaGod((220, 260), self.sprite_loader)
        
        # Cat visiting area (center-right)
        self.cat_visitors = []
        self.cat_spawn_timer = 0
        #self.cat_spawn_interval = 30000  # 30 seconds
        self.cat_spawn_interval = 3000  # 30 seconds
        
        # Dragging state
        self.dragging_object = None
        self.drag_offset = (0, 0)
        
        # UI
        self.menu_button_rect = pygame.Rect(self.width - 120, 10, 110, 40)
        self.tooltip = Tooltip()
        self.hovered_cat = None
        self.hovered_tea_cup = None
        
        # Spawn first cat
        self._spawn_cat()
    
    def _init_tea_drawer(self):
        """Initialize tea disks in the drawer"""
        start_x = 250
        spacing = 90
        y = 80
        
        for i, tea_data in enumerate(self.all_teas):
            x = start_x + (i % 8) * spacing
            disk = TeaDisk(tea_data, (x, y), self.sprite_loader, self.game_state)
            self.tea_disks.append(disk)
    
    def _init_tea_cups(self):
        """Initialize 8 tea cups on the cha ban"""
        cup_positions = [
            (70, 500), (120, 500), (170, 500), (220, 500),
            (70, 550), (120, 550), (170, 550), (220, 550)
        ]
        for i, pos in enumerate(cup_positions):
            self.tea_cups.append(TeaCup(pos, i, self.sprite_loader))
    
    def _spawn_cat(self):
        """Spawn a new cat in an available slot"""
        if len(self.cat_visitors) >= 5:
            return
        
        # Get available cats from game state
        available_cats = [c for c in self.all_cats if self.game_state.is_cat_unlocked(c['id'])]
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
            cat = CatVisitor(cat_data, (slot_x, slot_y), slot_index, self.sprite_loader)
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
                if self.game_state.is_tea_unlocked(disk.tea_data['id']) and disk.contains_point(mouse_pos):
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
                self.dragging_object = self.tea_kettle
                self.drag_offset = (self.tea_kettle.position[0] - mouse_pos[0], 
                                   self.tea_kettle.position[1] - mouse_pos[1])
                return None
            
            # Check for dragging cha hai (to pour to cups)
            if self.cha_hai.tea_data and self.cha_hai.contains_point(mouse_pos):
                self.dragging_object = self.cha_hai
                self.drag_offset = (self.cha_hai.position[0] - mouse_pos[0], 
                                   self.cha_hai.position[1] - mouse_pos[1])
                return None
            
            # Check for dragging filled cups
            for cup in self.tea_cups:
                if cup.tea_data and cup.contains_point(mouse_pos):
                    self.dragging_object = cup
                    cup.dragging = True
                    self.drag_offset = (cup.position[0] - mouse_pos[0], cup.position[1] - mouse_pos[1])
                    return None
        
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check for cat hover (only when not dragging)
            if not self.dragging_object:
                self.hovered_cat = None
                for cat in self.cat_visitors:
                    if cat.contains_point(mouse_pos):
                        self.hovered_cat = cat
                        break
                
                # Check for tea cup hover
                self.hovered_tea_cup = None
                for cup in self.tea_cups:
                    if cup.tea_data and cup.contains_point(mouse_pos):
                        self.hovered_tea_cup = cup
                        break
            
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
                
                elif self.dragging_object == self.tea_kettle:
                    self.dragging_object.position = [mouse_pos[0] + self.drag_offset[0],
                                                     mouse_pos[1] + self.drag_offset[1]]
                    # Preview pouring animation when hovering over cha hai
                    if self.cha_hai.contains_point(mouse_pos) and self.tea_kettle.state == "ready":
                        if not self.tea_kettle.is_pouring:
                            self.tea_kettle.start_pouring(target_position=self.cha_hai.position)
                
                elif self.dragging_object == self.cha_hai:
                    self.dragging_object.position = [mouse_pos[0] + self.drag_offset[0],
                                                     mouse_pos[1] + self.drag_offset[1]]
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging_object:
                mouse_pos = pygame.mouse.get_pos()
                
                # Handle tea disk drop
                if isinstance(self.dragging_object, TeaDisk):
                    if self.tea_kettle.contains_point(mouse_pos):
                        self.tea_kettle.add_tea(self.dragging_object.tea_data)
                    self.dragging_object.snap_back()
                    self.dragging_object.dragging = False
                
                # Handle hot water kettle drop
                elif isinstance(self.dragging_object, HotWaterKettle):
                    if self.tea_kettle.contains_point(mouse_pos):
                        added = self.tea_kettle.add_water()
                        if added:
                            # Start pouring animation and snap back after it completes
                            # Position kettle above and to the left of tea kettle
                            self.hot_water_kettle.start_pouring(
                                snap_back_after=True,
                                target_position=self.tea_kettle.position
                            )
                        else:
                            self.dragging_object.snap_back()
                    else:
                        self.dragging_object.snap_back()
                    self.dragging_object.dragging = False
                
                # Handle tea kettle pour to cha hai
                elif self.dragging_object == self.tea_kettle:
                    if self.tea_god.contains_point(mouse_pos):
                        # Dispose tea leaves
                        if self.tea_kettle.tea_data:
                            self.tea_kettle.tea_data = None
                            self.tea_kettle.state = self.tea_kettle.STATE_EMPTY
                            self.tea_god.receive_leaves()
                        self.tea_kettle.snap_back()
                    elif self.cha_hai.contains_point(mouse_pos):
                        tea_data = self.tea_kettle.pour_to_cha_hai(
                            snap_back_after=True,
                            target_position=self.cha_hai.position
                        )
                        if tea_data:
                            self.cha_hai.pour_from_kettle(tea_data)
                    else:
                        # Reset position if not dropped on cha hai
                        self.tea_kettle.snap_back()
                
                # Handle cha hai pour to cups
                elif self.dragging_object == self.cha_hai:
                    if self.tea_god.contains_point(mouse_pos):
                        # Dispose tea from cha hai
                        if self.cha_hai.tea_data:
                            self.cha_hai.tea_data = None
                            self.tea_god.receive_tea()
                        self.cha_hai.position = [120, 400]
                    else:
                        for cup in self.tea_cups:
                            if cup.contains_point(mouse_pos) and not cup.tea_data:
                                tea_data = self.cha_hai.pour_to_cup()
                                if tea_data:
                                    cup.fill(tea_data)
                                break
                        # Reset position
                        self.cha_hai.position = [120, 400]
                
                # Handle cup drop on cat
                elif isinstance(self.dragging_object, TeaCup):
                    if self.tea_god.contains_point(mouse_pos):
                        # Dispose tea from cup
                        tea_data = self.dragging_object.tea_data
                        if tea_data:
                            self.dragging_object.empty()
                            self.tea_god.receive_tea()
                    else:
                        # Check cat serving
                        for cat in self.cat_visitors:
                            cat_rect = pygame.Rect(cat.position[0] - 40, cat.position[1] - 40, 80, 80)
                            if cat_rect.collidepoint(mouse_pos) and cat.state == "waiting":
                                tea_data = self.dragging_object.empty()
                                if tea_data:
                                    result = cat.receive_tea(tea_data['id'])
                                    if result:
                                        self.game_state.add_hearts(result['hearts'])
                                break
                    
                    self.dragging_object.snap_back()
                    self.dragging_object.dragging = False
                
                self.dragging_object = None
                self.drag_offset = (0, 0)
        
        return None
    
    def update(self, dt):
        # Update tea kettle brewing and animations
        self.tea_kettle.update(dt)
        self.hot_water_kettle.update(dt)
        self.tea_god.update(dt)
        
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
        # Background - solid color
        self.screen.fill((245, 235, 220))
        
        # Draw border frame sprite if available
        border_sprite = self.sprite_loader.get_sprite('border_frame', 'single') if self.sprite_loader else None
        if border_sprite:
            # Center the border frame
            border_rect = border_sprite.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(border_sprite, border_rect)
        else:
            # Fallback: Draw decorative border rectangles
            border_color = (100, 150, 100)
            pygame.draw.rect(self.screen, border_color, (0, 0, self.width, 20))
            pygame.draw.rect(self.screen, border_color, (0, self.height - 20, self.width, 20))
            pygame.draw.rect(self.screen, border_color, (0, 0, 20, self.height))
            pygame.draw.rect(self.screen, border_color, (self.width - 20, 0, 20, self.height))
        
        # Draw tea drawer area
        pygame.draw.rect(self.screen, (139, 90, 60), (230, 40, 540, 80), border_radius=10)
        pygame.draw.rect(self.screen, (80, 50, 30), (230, 40, 540, 80), 3, border_radius=10)
        
        drawer_font = pygame.font.Font(None, 20)
        drawer_label = drawer_font.render("Tea Drawer - Drag tea to kettle", True, (255, 255, 200))
        drawer_rect = drawer_label.get_rect(center=(500, 30))
        self.screen.blit(drawer_label, drawer_rect)
        
        # Draw tea disks (except if being dragged)
        for disk in self.tea_disks:
            if disk != self.dragging_object:
                disk.draw(self.screen)
        
        # Draw cha ban area
        pygame.draw.rect(self.screen, (160, 120, 80), (30, 140, 240, 480), border_radius=10)
        
        cha_ban_font = pygame.font.Font(None, 20)
        cha_ban_label = cha_ban_font.render("Cha Ban", True, (255, 255, 200))
        cha_ban_rect = cha_ban_label.get_rect(center=(150, 150))
        self.screen.blit(cha_ban_label, cha_ban_rect)
        
        # Draw equipment on cha ban (except if being dragged)
        # Draw hot water kettle first if not pouring, or last if pouring (to appear on top)
        if self.hot_water_kettle != self.dragging_object and not self.hot_water_kettle.is_pouring:
            self.hot_water_kettle.draw(self.screen)
        # Draw tea kettle first if not pouring, or last if pouring
        if self.tea_kettle != self.dragging_object and not self.tea_kettle.is_pouring:
            self.tea_kettle.draw(self.screen)
        # Draw hot water kettle after tea kettle when pouring (on top of tea kettle)
        if self.hot_water_kettle != self.dragging_object and self.hot_water_kettle.is_pouring:
            self.hot_water_kettle.draw(self.screen)
        if self.cha_hai != self.dragging_object:
            self.cha_hai.draw(self.screen)
        # Draw tea kettle after cha hai when pouring (on top of cha hai)
        if self.tea_kettle != self.dragging_object and self.tea_kettle.is_pouring:
            self.tea_kettle.draw(self.screen)
        for cup in self.tea_cups:
            if cup != self.dragging_object:
                cup.draw(self.screen)
        # Draw tea god
        self.tea_god.draw(self.screen)
        
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
        hearts_text = hearts_font.render(f"Hearts: {self.game_state.hearts}", True, (200, 50, 50))
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
        
        # Draw dragged object last (on top of everything)
        if self.dragging_object:
            self.dragging_object.draw(self.screen)
        
        # Draw tooltip (on top of everything)
        if self.hovered_cat:
            mouse_pos = pygame.mouse.get_pos()
            cat_data = self.hovered_cat.cat_data
            tooltip_info = {
                "Description": cat_data['description'],
                "Personality": cat_data['personality'],
                "Birthday": self.hovered_cat.birthday
            }
            self.tooltip.draw(self.screen, mouse_pos, cat_data['name'], tooltip_info)
        
        # Draw tea cup tooltip
        elif self.hovered_tea_cup and self.hovered_tea_cup.tea_data:
            mouse_pos = pygame.mouse.get_pos()
            tea_data = self.hovered_tea_cup.tea_data
            tooltip_info = {
                "Type": tea_data.get('category', 'Unknown').replace('_', ' ').title(),
                "Brew Time": f"{tea_data.get('brew_time', 0) / 1000:.1f}s"
            }
            self.tooltip.draw(self.screen, mouse_pos, tea_data['name'], tooltip_info)
