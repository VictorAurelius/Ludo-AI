import pygame
import pytmx
from sound_manager import get_sound_manager

class MenuManager:
    def __init__(self, screen):
        self.screen = screen
        self.current_menu = "main"
        
        # Initialize sound manager
        self.sound_manager = get_sound_manager()
        
        # Load TMX files
        self.main_menu_map = pytmx.load_pygame("UI/main_menu.tmx")
        self.sp_menu_map = pytmx.load_pygame("UI/sp_menu.tmx")
        
        # Font for drawing text
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 48)
        self.content_font = pygame.font.Font(None, 32)
        
        # Colors
        self.NORMAL_COLOR = (255, 255, 255)
        self.HOVER_COLOR = (255, 255, 0)
        self.CLICK_COLOR = (255, 160, 0)
        
        # Transition effect
        self.transition_alpha = 255
        self.transitioning = False
        self.transition_speed = 10
        self.target_menu = None
        
        # Menu content
        self.menu_text = {
            "main": {
                "title": {"text": "LUDO", "pos": (400, 130)},
                "buttons": [
                    {"text": "Chơi game", "pos": (400, 280)},
                    {"text": "Luật chơi", "pos": (400, 350)},
                    {"text": "Nhà phát triển", "pos": (400, 420)},
                    {"text": "Thoát", "pos": (400, 490)}
                ]
            },
            "rules": {
                "title": {"text": "Luật chơi", "pos": (400, 130)},
                "content": [
                    {"text": "1. Mỗi người chơi có 4 quân cờ", "pos": (400, 250)},
                    {"text": "2. Tung được 6 để đưa quân ra khỏi chuồng", "pos": (400, 290)},
                    {"text": "3. Di chuyển quân theo số trên xúc xắc", "pos": (400, 330)},
                    {"text": "4. Đá quân đối thủ khi đến ô có quân", "pos": (400, 370)},
                    {"text": "5. Gặp sao sẽ được hiệu ứng đặc biệt", "pos": (400, 410)},
                    {"text": "6. Đưa 4 quân về đích để chiến thắng", "pos": (400, 450)}
                ],
                "buttons": [
                    {"text": "Trở về", "pos": (400, 490)}
                ]
            },
            "developers": {
                "title": {"text": "Nhà phát triển", "pos": (400, 130)},
                "content": [
                    {"text": "Nhóm phát triển:", "pos": (400, 250)},
                    {"text": "1. Nguyễn Văn A - Leader", "pos": (400, 290)},
                    {"text": "2. Trần Thị B - Developer", "pos": (400, 330)},
                    {"text": "3. Lê Văn C - Developer", "pos": (400, 370)},
                    {"text": "4. Phạm Thị D - Designer", "pos": (400, 410)}
                ],
                "buttons": [
                    {"text": "Trở về", "pos": (400, 490)}
                ]
            }
        }

        # Button click areas
        self.buttons = {
            "main": [
                {"rect": pygame.Rect(300, 260, 200, 40), "action": "start_game", "hover": False},
                {"rect": pygame.Rect(300, 330, 200, 40), "action": "rules", "hover": False},
                {"rect": pygame.Rect(300, 400, 200, 40), "action": "developers", "hover": False},
                {"rect": pygame.Rect(300, 470, 200, 40), "action": "exit", "hover": False}
            ],
            "rules": [
                {"rect": pygame.Rect(300, 470, 200, 40), "action": "main", "hover": False}
            ],
            "developers": [
                {"rect": pygame.Rect(300, 470, 200, 40), "action": "main", "hover": False}
            ]
        }
        
        # Track active button and last hover state
        self.active_button = None
        self.last_hover = False

    def start_transition(self, target_menu):
        """Start transition to new menu"""
        self.transitioning = True
        self.transition_alpha = 0
        self.target_menu = target_menu
        self.sound_manager.play_sound('transition')

    def update_transition(self):
        """Update transition effect"""
        if self.transitioning:
            self.transition_alpha += self.transition_speed
            if self.transition_alpha >= 255:
                self.transitioning = False
                if self.target_menu:
                    self.current_menu = self.target_menu
                    self.target_menu = None
                self.transition_alpha = 255

    def draw_layer(self, tmx_map, layer_name):
        """Draw a specific layer from TMX map"""
        if layer_name in tmx_map.layernames:
            layer = tmx_map.layernames[layer_name]
            for x, y, gid in layer:
                if gid:
                    tile = tmx_map.get_tile_image_by_gid(gid)
                    if tile:
                        offset_x = layer.offsetx if hasattr(layer, 'offsetx') else 0
                        offset_y = layer.offsety if hasattr(layer, 'offsety') else 0
                        pos_x = x * tmx_map.tilewidth + offset_x
                        pos_y = y * tmx_map.tileheight + offset_y
                        self.screen.blit(tile, (pos_x, pos_y))

    def draw_text(self, text, pos, font=None, color=None):
        """Draw centered text"""
        if font is None:
            font = self.menu_font
        if color is None:
            color = self.NORMAL_COLOR
            
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=pos)
        self.screen.blit(text_surface, text_rect)

    def update_button_states(self, mouse_pos, mouse_pressed):
        """Update button hover and active states"""
        if self.transitioning:
            return
            
        any_hover = False
        buttons = self.buttons[self.current_menu]
        
        # Reset all hover states
        for button in buttons:
            button["hover"] = False
            
        # Check for hover and active states
        for button in buttons:
            if button["rect"].collidepoint(mouse_pos):
                button["hover"] = True
                any_hover = True
                if mouse_pressed[0]:  # Left mouse button pressed
                    if self.active_button != button:
                        self.sound_manager.play_sound('click')
                    self.active_button = button
                    return
        
        # Play hover sound when first hovering over a button
        if any_hover and not self.last_hover:
            self.sound_manager.play_sound('hover')
        self.last_hover = any_hover
                    
        if not any(mouse_pressed):  # No mouse buttons pressed
            self.active_button = None

    def draw(self):
        """Draw current menu screen"""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Select map based on current menu
        tmx_map = self.main_menu_map if self.current_menu == "main" else self.sp_menu_map
        
        # Draw map layers
        layers = ['water', 'rock', 'grass', 'tree', 'deco', 'ban']
        for layer in layers:
            self.draw_layer(tmx_map, layer)

        # Get current menu content
        menu_content = self.menu_text[self.current_menu]
        
        # Draw title
        self.draw_text(menu_content["title"]["text"], menu_content["title"]["pos"], self.title_font)
        
        # Draw content if available
        if "content" in menu_content:
            for content_item in menu_content["content"]:
                self.draw_text(content_item["text"], content_item["pos"], self.content_font)
        
        # Draw buttons with hover effects
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        self.update_button_states(mouse_pos, mouse_pressed)
        
        for i, button in enumerate(menu_content["buttons"]):
            button_info = self.buttons[self.current_menu][i]
            color = self.NORMAL_COLOR
            
            if button_info["hover"]:
                color = self.HOVER_COLOR
            if self.active_button == button_info:
                color = self.CLICK_COLOR
                
            self.draw_text(button["text"], button["pos"], color=color)

        # Draw transition effect
        if self.transitioning:
            fade_surface = pygame.Surface((925, 725))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.transition_alpha)
            self.screen.blit(fade_surface, (0, 0))
            self.update_transition()

    def handle_click(self, pos):
        """Handle mouse click events"""
        if self.transitioning:
            return None

        # Get button areas for current menu
        buttons = self.buttons[self.current_menu]
        
        # Check each button
        for button in buttons:
            if button["rect"].collidepoint(pos):
                action = button["action"]
                
                # Play appropriate sound
                if action == "start_game":
                    self.sound_manager.play_sound('start_game')
                else:
                    self.sound_manager.play_sound('click')
                
                # Handle action
                if action == "start_game":
                    return "start_game"
                elif action == "rules":
                    self.start_transition("rules")
                elif action == "developers":
                    self.start_transition("developers")
                elif action == "main":
                    self.start_transition("main")
                elif action == "exit":
                    return "exit"
                break
        
        return None