import pygame
import pytmx
import os

class MenuManager:
    def __init__(self, screen):
        self.screen = screen
        self.current_menu = "main"
        
        # Load TMX files with error handling
        try:
            tmx_path = os.path.join("UI", "main_menu.tmx")
            if not os.path.exists(tmx_path):
                raise FileNotFoundError(f"Could not find {tmx_path}")
            self.main_menu_map = pytmx.load_pygame(tmx_path)
            
            tmx_path = os.path.join("UI", "sp_menu.tmx")
            if not os.path.exists(tmx_path):
                raise FileNotFoundError(f"Could not find {tmx_path}")
            self.sp_menu_map = pytmx.load_pygame(tmx_path)
            
            print("Successfully loaded TMX files")
            print(f"Main menu layers: {list(self.main_menu_map.layernames.keys())}")
            print(f"SP menu layers: {list(self.sp_menu_map.layernames.keys())}")
            
        except Exception as e:
            print(f"Error loading TMX files: {e}")
            raise
        
        # Font for drawing text
        try:
            # Try to find the best font with Vietnamese support
            system_fonts = [
                "arial", "segoeui", "tahoma", "calibri",  # Common fonts with Vietnamese support
                "notosans", "roboto", "times new roman"
            ]
            
            font_loaded = False
            for font_name in system_fonts:
                try:
                    self.title_font = pygame.font.SysFont(font_name, 90)
                    test_render = self.title_font.render("Tiếng Việt", True, (0,0,0))
                    if test_render:
                        self.menu_font = pygame.font.SysFont(font_name, 42)
                        self.content_font = pygame.font.SysFont(font_name, 36)
                        print(f"Using system font: {font_name}")
                        font_loaded = True
                        break
                except:
                    continue
            
            if not font_loaded:
                # Fallback to default font
                print("No suitable Vietnamese font found, using default")
                self.title_font = pygame.font.Font(None, 90)
                self.menu_font = pygame.font.Font(None, 42)
                self.content_font = pygame.font.Font(None, 36)
                
        except Exception as e:
            print(f"Could not load font: {e}")
            # Fallback to default fonts
            self.title_font = pygame.font.Font(None, 90)
            self.menu_font = pygame.font.Font(None, 42)
            self.content_font = pygame.font.Font(None, 36)
        
        # Colors
        self.NORMAL_COLOR = (0, 0, 0)  # Màu đen cho text thường
        self.HOVER_COLOR = (255, 165, 0)  # Màu cam khi hover
        self.CLICK_COLOR = (220, 20, 60)  # Màu đỏ khi click
        self.TITLE_COLOR = (0, 0, 0)  # Màu đen cho tiêu đề
        
        # Layer configurations with explicit ordering and properties
        self.layer_config = {
            'water': {'order': 1, 'alpha': 255},
            'rock': {'order': 2, 'alpha': 255},
            'grass': {'order': 3, 'alpha': 255},
            'tree': {'order': 4, 'alpha': 255},
            'deco': {'order': 5, 'alpha': 255},
            'ban': {'order': 6, 'alpha': 255, 'use_offset': True},
            'button': {'order': 7, 'alpha': 255, 'use_offset': True},
            'bong': {'order': 8, 'alpha': 200, 'use_offset': True}
        }
        
        # Get sorted layer order
        self.layer_order = sorted(self.layer_config.keys(), 
                                key=lambda x: self.layer_config[x]['order'])
        
        # Menu content matching TMX banner positions
        self.menu_text = {
            "main": {
                "title": {"text": "LUDO", "pos": (400, 125)},  # Tiêu đề căn chỉnh với banner
                "buttons": [
                    {"text": "Chơi game", "pos": (400, 400)},  # Button vị trí tương ứng với layer button 
                    {"text": "Luật chơi", "pos": (400, 470)},  
                    {"text": "Nhà phát triển", "pos": (400, 540)},
                    {"text": "Thoát", "pos": (400, 610)}
                ]
            },
            "rules": {
                "title": {"text": "Luật chơi", "pos": (400, 150)},
                "content": [
                    {"text": "1. Mỗi người chơi có 4 quân cờ", "pos": (400, 300)},
                    {"text": "2. Tung được 6 để đưa quân ra khỏi chuồng", "pos": (400, 340)},
                    {"text": "3. Di chuyển quân theo số trên xúc xắc", "pos": (400, 380)},
                    {"text": "4. Đá quân đối thủ khi đến ô có quân", "pos": (400, 420)},
                    {"text": "5. Gặp sao sẽ được hiệu ứng đặc biệt", "pos": (400, 460)},
                    {"text": "6. Đưa 4 quân về đích để chiến thắng", "pos": (400, 500)}
                ],
                "buttons": [
                    {"text": "Trở về", "pos": (400, 610)}
                ]
            },
            "developers": {
                "title": {"text": "Nhà phát triển", "pos": (400, 150)},
                "content": [
                    {"text": "Nhóm phát triển:", "pos": (400, 300)},
                    {"text": "1. Nguyễn Văn A - Leader", "pos": (400, 340)},
                    {"text": "2. Trần Thị B - Developer", "pos": (400, 380)},
                    {"text": "3. Lê Văn C - Developer", "pos": (400, 420)},
                    {"text": "4. Phạm Thị D - Designer", "pos": (400, 460)}
                ],
                "buttons": [
                    {"text": "Trở về", "pos": (400, 610)}
                ]
            }
        }

        # Button click areas matched with TMX button layer
        self.buttons = {
            "main": [
                {"rect": pygame.Rect(320, 380, 160, 40), "action": "start_game", "hover": False},  # Điều chỉnh vị trí các button
                {"rect": pygame.Rect(320, 450, 160, 40), "action": "rules", "hover": False},       # để khớp với layer button trong TMX
                {"rect": pygame.Rect(320, 520, 160, 40), "action": "developers", "hover": False},
                {"rect": pygame.Rect(320, 590, 160, 40), "action": "exit", "hover": False}
            ],
            "rules": [
                {"rect": pygame.Rect(300, 590, 200, 40), "action": "main", "hover": False}
            ],
            "developers": [
                {"rect": pygame.Rect(300, 590, 200, 40), "action": "main", "hover": False}
            ]
        }
        
        self.active_button = None
        self.debug_mode = True  # Enable to show layer info

    def draw_layer(self, tmx_map, layer_name):
        """Draw a specific layer from TMX map with proper offset"""
        if layer_name not in tmx_map.layernames:
            if self.debug_mode:
                print(f"Layer '{layer_name}' not found in map")
            return

        layer = tmx_map.layernames[layer_name]
        config = self.layer_config[layer_name]
        
        # Get layer offset if specified
        offset_x = layer.offsetx if hasattr(layer, 'offsetx') and config['use_offset'] else 0
        offset_y = layer.offsety if hasattr(layer, 'offsety') and config['use_offset'] else 0
        
        if self.debug_mode:
            print(f"Drawing layer '{layer_name}' with offset ({offset_x}, {offset_y})")
        
        # Create a surface for this layer
        layer_surface = pygame.Surface((925, 725), pygame.SRCALPHA)
        
        # Draw tiles
        for x, y, gid in layer:
            if gid:
                tile = tmx_map.get_tile_image_by_gid(gid)
                if tile:
                    pos_x = x * tmx_map.tilewidth + offset_x
                    pos_y = y * tmx_map.tileheight + offset_y
                    layer_surface.blit(tile, (pos_x, pos_y))
        
        # Apply layer alpha
        layer_surface.set_alpha(config['alpha'])
        
        # Blit the layer surface onto the screen
        self.screen.blit(layer_surface, (0, 0))

    def draw_text(self, text, pos, font=None, color=None):
        """Draw centered text"""
        if font is None:
            font = self.menu_font
        if color is None:
            color = self.NORMAL_COLOR
            
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=pos)
        self.screen.blit(text_surface, text_rect)

    def draw(self):
        """Draw current menu screen"""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Select map based on current menu
        tmx_map = self.main_menu_map if self.current_menu == "main" else self.sp_menu_map
        
        if self.debug_mode:
            print(f"\nDrawing {self.current_menu} menu")
        
        # Draw all layers in order
        for layer_name in self.layer_order:
            # Skip bong layer in main menu
            if (layer_name == "bong" and self.current_menu == "main"):
                continue
            self.draw_layer(tmx_map, layer_name)
        
        # Get current menu content
        menu_content = self.menu_text[self.current_menu]
        
        # Draw title
        self.draw_text(menu_content["title"]["text"], 
                      menu_content["title"]["pos"], self.title_font)
        
        # Draw content if available
        if "content" in menu_content:
            for content_item in menu_content["content"]:
                self.draw_text(content_item["text"], 
                             content_item["pos"], self.content_font)
        
        # Draw buttons with hover effects
        mouse_pos = pygame.mouse.get_pos()
        for i, button in enumerate(menu_content["buttons"]):
            button_info = self.buttons[self.current_menu][i]
            color = self.NORMAL_COLOR
            
            if button_info["rect"].collidepoint(mouse_pos):
                color = self.HOVER_COLOR
            if self.active_button == button_info:
                color = self.CLICK_COLOR
                
            self.draw_text(button["text"], button["pos"], color=color)

    def handle_click(self, pos):
        """Handle mouse click events"""
        buttons = self.buttons[self.current_menu]
        
        for button in buttons:
            if button["rect"].collidepoint(pos):
                self.active_button = button
                action = button["action"]
                
                if action == "start_game":
                    return "start_game"
                elif action in ["rules", "developers"]:
                    if self.debug_mode:
                        print(f"Switching to {action} menu")
                    self.current_menu = action
                elif action == "main":
                    if self.debug_mode:
                        print("Returning to main menu")
                    self.current_menu = "main"
                elif action == "exit":
                    return "exit"
                break
        
        return None
