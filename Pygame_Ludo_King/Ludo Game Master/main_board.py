import pygame
import sys
import pytmx
import os
import logging
import traceback

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration constants
TMX_CONFIG = {
    'main_menu': {
        'path': 'UI/main_menu.tmx',
        'required_layers': ['ban', 'button'],
        'button_positions': {
            'play': (250, 300),
            'rules': (250, 375),
            'developers': (250, 450),
            'quit': (250, 525),
        }
    },
    'sp_menu': {
        'path': 'UI/sp_menu.tmx',
        'required_layers': ['ban', 'bong'],
        'button_positions': {
            'back': (50, 600),
            'ok': (300, 600)
        }
    }
}

COLORS = {
    'error_bg': (255, 200, 200, 200),     # Light red with alpha
    'error_text': (200, 0, 0),            # Dark red
    'error_detail': (100, 0, 0),          # Darker red
    'text': (0, 0, 0),                    # Black text
    'active_input': (240, 240, 240)       # Light gray for input highlight
}

class MainBoard:
    @staticmethod
    def resolve_path(path, base=None):
        """Resolve file path, handling both absolute and relative paths"""
        if os.path.isabs(path):
            return path
        if base is None:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.normpath(os.path.join(base, path))

    def verify_tileset(self, tmx_path, tileset_source):
        """Verify a single tileset exists and log its properties"""
        tileset_path = self.resolve_path(tileset_source, os.path.dirname(tmx_path))
        if not os.path.exists(tileset_path):
            raise FileNotFoundError(f"Tileset not found: {tileset_source} (looking in {tileset_path})")
        logger.debug(f"✓ Found tileset: {tileset_source}")
        return tileset_path

    @staticmethod
    def _create_font(size, font_name="tahoma"):
        """Create a font with fallback"""
        try:
            return pygame.font.SysFont(font_name, size)
        except pygame.error:
            return pygame.font.Font(None, size)

    def _render_text_with_shadow(self, text, font, color, surface, pos, shadow_color=None, shadow_offset=1):
        """Render text with a shadow effect"""
        if shadow_color is None:
            # Create semi-transparent shadow color
            if isinstance(color, (tuple, list)) and len(color) >= 3:
                shadow_color = (*color[:3], 128)
            else:
                shadow_color = COLORS['error_detail'][:3] + (128,)

        # Render shadow and main text
        shadow = font.render(text, True, shadow_color)
        text_surface = font.render(text, True, color)

        # Draw shadow then text
        surface.blit(shadow, (pos[0] + shadow_offset, pos[1] + shadow_offset))
        surface.blit(text_surface, pos)
        
        return text_surface.get_height()

    def _draw_error_pattern(self, surface, color, spacing=20, alpha=30):
        """Draw a diagonal error pattern on a surface"""
        pattern_color = (*color[:3], alpha)
        width, height = surface.get_size()
        
        for i in range(0, width + height, spacing):
            start_pos = (max(0, i - height), min(i, height))
            end_pos = (min(i, width), max(0, i - width))
            pygame.draw.line(surface, pattern_color, start_pos, end_pos)

    def show_error_screen(self, title, error_msg, help_messages=None):
        """Display an error screen with the given message and wait for user input"""
        try:
            # Setup error screen
            screen = pygame.display.set_mode((800, 400))
            pygame.display.set_caption("Ludo Game - Error")
            screen.fill(COLORS['error_bg'])
            
            # Setup fonts with error handling
            try:
                font = pygame.font.SysFont("tahoma", 20)
                font_bold = pygame.font.SysFont("tahoma", 24, bold=True)
            except pygame.error:
                # Fallback to default font if tahoma is not available
                font = pygame.font.Font(None, 20)
                font_bold = pygame.font.Font(None, 24)
            
            # Draw title with shadow for better visibility
            shadow_offset = 2
            title_shadow = font_bold.render(title, True, COLORS['error_detail'])
            title_surface = font_bold.render(title, True, COLORS['error_text'])
            
            title_x = 400 - title_surface.get_width() // 2
            title_y = 50
            screen.blit(title_shadow, (title_x + shadow_offset, title_y + shadow_offset))
            screen.blit(title_surface, (title_x, title_y))
            
            # Prepare and format messages
            messages = []
            if error_msg:
                messages.extend([error_msg, ""])
            if help_messages:
                messages.extend(help_messages)
            messages.extend(["", "Press any key to exit"])
            
            # Draw messages with improved visibility
            y = 120
            for msg in messages:
                if not msg:  # Handle empty lines
                    y += 15  # Smaller spacing for empty lines
                    continue
                
                text = font.render(msg, True, COLORS['text'])
                # Center messages that don't start with whitespace
                x = 400 - text.get_width() // 2 if not msg[0].isspace() else 50
                screen.blit(text, (x, y))
                y += 30
            
            pygame.display.flip()
            
            # Wait for user input with timeout
            start_time = pygame.time.get_ticks()
            waiting = True
            while waiting and pygame.time.get_ticks() - start_time < 30000:  # 30 second timeout
                for event in pygame.event.get():
                    if event.type in [pygame.QUIT, pygame.KEYDOWN]:
                        waiting = False
                pygame.time.wait(100)  # Reduce CPU usage
                
        except Exception as e:
            # Fallback to console with improved formatting
            logger.error(f"Failed to show error screen: {e}")
            print("\n" + "="*60)
            print(f"ERROR: {title}")
            print("-"*60)
            print(f"Details: {error_msg}")
            if help_messages:
                print("\nHelp:")
                for msg in help_messages:
                    print(msg)
            print("="*60 + "\n")
        
        pygame.quit()
        sys.exit(1)

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 800))
        pygame.display.set_caption("Ludo King - Cờ Cá Ngựa")
        
        # Initialize dictionaries for TMX data and backgrounds
        self.tmx_data = {}
        self.backgrounds = {}

        try:
            # Load TMX files
            logger.info("Starting TMX initialization")
            
            # Define and resolve TMX paths
            tmx_paths = {
                name: self.resolve_path(f"UI/{name}.tmx")
                for name in ["main_menu", "sp_menu"]
            }
            logger.debug(f"Resolved TMX paths: {tmx_paths}")

            # Monkey patch pytmx to handle float values
            import pytmx.pytmx
            original_types = pytmx.pytmx.types.copy()
            
            def safe_int(value):
                """Convert string to int, handling floating point strings"""
                try:
                    return int(float(value))
                except (ValueError, TypeError):
                    return 0

            pytmx.pytmx.types.update({
                'x': float,
                'y': float,
                'width': safe_int,
                'height': safe_int,
                'tilewidth': safe_int,
                'tileheight': safe_int,
                'spacing': safe_int,
                'margin': safe_int,
                'repeatx': safe_int,
                'repeaty': safe_int,
                'gid': safe_int,
                'firstgid': safe_int,
                'id': safe_int,
                'version': str,
                'tiledversion': str,
                'orientation': str,
                'renderorder': str,
                'compressionlevel': safe_int,
                'infinite': bool,
                'nextlayerid': safe_int,
                'nextobjectid': safe_int,
                # Add any other numeric properties that might contain decimals
                'parallaxx': float,
                'parallaxy': float,
                'offsetx': float,
                'offsety': float,
                'opacity': float,
            })

            def verify_tileset_paths(tmx_file):
                """Verify that all tilesets referenced in TMX file exist"""
                import re
                logger.debug(f"Verifying tilesets for {os.path.basename(tmx_file)}")
                
                # Read TMX content
                try:
                    with open(tmx_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception as e:
                    raise IOError(f"Failed to read TMX file: {e}")
                
                # Find and verify all tileset sources
                tileset_sources = re.findall(r'source="([^"]+)"', content)
                logger.info(f"Checking {len(tileset_sources)} tilesets in {os.path.basename(tmx_file)}")
                
                # Verify each tileset
                missing_tilesets = []
                for source in tileset_sources:
                    try:
                        self.verify_tileset(tmx_file, source)
                    except FileNotFoundError as e:
                        missing_tilesets.append(str(e))
                
                if missing_tilesets:
                    raise FileNotFoundError("\n".join(missing_tilesets))
                
                logger.info(f"✓ All tilesets verified for {os.path.basename(tmx_file)}")
            
            # Process each TMX file
            for name, config in TMX_CONFIG.items():
                path = tmx_paths[name]
                logger.info(f"Processing {name}.tmx...")
                
                # Verify file and tilesets
                if not os.path.exists(path):
                    raise FileNotFoundError(f"TMX file not found: {path}")
                logger.debug(f"Verifying {name}.tmx at {path}")
                # Check tilesets
                verify_tileset_paths(path)
                
                try:
                    # Load TMX
                    tmx = pytmx.load_pygame(path)
                    
                    # Verify required layers
                    found_layers = {l.name for l in tmx.visible_layers if hasattr(l, 'name')}
                    required_layers = set(config['required_layers'])
                    missing = required_layers - found_layers
                    if (missing):
                        raise ValueError(f"Missing required layers in {name}.tmx: {missing}")
                    
                    # Log layer info
                    layer_info = "\n".join([
                        f"  - {l.name}: offset({getattr(l,'offsetx', 0)}, {getattr(l,'offsety', 0)})"
                        for l in tmx.visible_layers if hasattr(l, 'name')
                    ])
                    logger.debug(f"Layers in {name}.tmx:\n{layer_info}")
                    
                except Exception as e:
                    raise RuntimeError(f"Error loading {name}.tmx: {e}")
                # Store TMX data and create background
                self.tmx_data[name] = tmx
                logger.info(f"Creating background for {name}.tmx...")
                self.backgrounds[name] = self.render_tmx(tmx)
            
            # Set up references for backward compatibility
            self.main_menu_tmx = self.tmx_data['main_menu']
            self.sp_menu_tmx = self.tmx_data['sp_menu']
            self.main_menu_bg = self.backgrounds['main_menu']
            self.sp_menu_bg = self.backgrounds['sp_menu']
            
            
            logger.info("TMX initialization complete")
        except FileNotFoundError as e:
            error_msg = str(e)
            logger.error(f"Resource not found: {error_msg}")
            self.show_error_screen(
                "Missing Game Resources",
                str(e),
                [
                    "Missing game resources. Please check:",
                    "",
                    "1. Game installation directory structure:",
                    f"   - {os.path.dirname(TMX_CONFIG['main_menu']['path'])} folder exists",
                    "   - All TMX files are present",
                    "   - All tileset images are in place",
                    "",
                    "Try reinstalling the game if the issue persists."
                ]
            )
        except ValueError as e:
            error_msg = str(e)
            logger.error(f"Invalid TMX structure: {error_msg}")
            logger.error(traceback.format_exc())
            self.show_error_screen(
                "Invalid Resource Format",
                "Game resource files are invalid or corrupted",
                [
                    "Resource format error:",
                    "",
                    f"Error: {error_msg}",
                    "",
                    "Please verify game files or reinstall."
                ]
            )
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Unexpected error: {error_msg}")
            logger.error(traceback.format_exc())
            self.show_error_screen(
                "System Error",
                "Game initialization failed",
                [
                    "An unexpected error occurred:",
                    "",
                    f"Error: {error_msg}",
                    "",
                    "Please check the game log for details."
                ]
            )
            
        # Initialize fonts for Vietnamese text
        try:
            # Load a font with better Vietnamese support
            font_path = os.path.join("fonts", "arial.ttf")  # Arial has good Vietnamese support
            
            # Try to find the best alternative font on the system
            system_fonts = [
                "arial", "segoeui", "tahoma", "calibri",  # Common fonts with Vietnamese support
                "notosans", "roboto", "times new roman"
            ]
            
            # Check if the font file already exists
            if os.path.exists(font_path):
                self.font = pygame.font.Font(font_path, 74)  # Font for title/banner
                self.small_font = pygame.font.Font(font_path, 36)  # Same font for buttons
                self.content_font = pygame.font.Font(font_path, 28)  # Font for content
                print("Loaded font from file:", font_path)
            else:
                # Create fonts directory if it doesn't exist
                os.makedirs("fonts", exist_ok=True)
                
                # Try system fonts that typically have good Vietnamese support
                font_loaded = False
                for font_name in system_fonts:
                    try:
                        self.font = pygame.font.SysFont(font_name, 74)
                        test_render = self.font.render("Tiếng Việt", True, (0,0,0))
                        if test_render:
                            self.small_font = pygame.font.SysFont(font_name, 36)
                            self.content_font = pygame.font.SysFont(font_name, 28)
                            print(f"Using system font: {font_name}")
                            font_loaded = True
                            break
                    except:
                        continue
                
                if not font_loaded:
                    # Fallback to default font
                    print("No suitable Vietnamese font found, using default")
                    self.font = pygame.font.Font(None, 74)
                    self.small_font = pygame.font.Font(None, 36)
                    self.content_font = pygame.font.Font(None, 28)
            
            # Fonts phụ cho các phần khác
            self.error_font = pygame.font.SysFont("arial", 24, bold=True)
            
        except Exception as e:
            print(f"Lỗi khi tải font: {e}")
            # Fallback to default fonts
            self.font = pygame.font.Font(None, 74)
            self.small_font = pygame.font.Font(None, 36)
            self.error_font = pygame.font.Font(None, 24)
            self.content_font = pygame.font.Font(None, 28)
        
        # Button positions aligned with TMX button layer
        self.buttons = {
            "play": pygame.Rect(250, 300, 250, 50),      # Wider buttons to match TMX
            "rules": pygame.Rect(250, 375, 250, 50),     # Adjusted vertical spacing
            "developers": pygame.Rect(250, 450, 250, 50),
            "quit": pygame.Rect(250, 525, 250, 50),
            "ok": pygame.Rect(300, 600, 200, 50),
            "back": pygame.Rect(50, 600, 200, 50)
        }
        self.player_names = ["", "", "", ""]
        self.show_name_input = False
        self.show_rules = False
        self.show_developers = False
        self.active_input = 0
        
        # Luật chơi
        rules_text_unicode = [
            u"",
            u"1. Mỗi người chơi có 4 quân cờ",
            u"2. Tung 2 con xúc xắc để di chuyển quân",
            u"3. Cần tung được tổng 2 con xúc xắc >= 10 để đưa",
            u"    quân vào bàn cờ",
            u"4. Quân có thể đá quân địch về chuồng nếu đứng cùng",
            u"    ô với quân địch",
            u"5. Người chơi phải đưa tất cả quân về đích để thắng",
            u"6. Quân di chuyển số ô bằng tổng 2 con xúc xắc",
            u"(Nếu khoảng cách từ quân đến đích nhỏ hơn 1 so với",
            u"  tổng số xúc xắc thì quân đó vẫn có thể về đích)"
        ]
        self.rules_text = rules_text_unicode

    def draw_main_menu(self):
        # Draw the main menu TMX background
        self.screen.blit(self.main_menu_bg, (0, 0))
        
        try:
            # Draw game title in the "ban" layer position
            title = self.font.render("LUDO", True, (0, 0, 0))  # Black text for visibility
            
            # Find the "ban" layer for accurate positioning
            ban_layer = None
            for layer in self.main_menu_tmx.visible_layers:
                if hasattr(layer, 'name') and layer.name == "ban":
                    ban_layer = layer
                    break
            
            if ban_layer:
                # Sử dụng vị trí của layer "ban" trong TMX
                ban_offset_x = getattr(ban_layer, 'offsetx', 0) or 0
                ban_offset_y = getattr(ban_layer, 'offsety', 0) or 0
                
                # Position title at banner position
                title_x = 420  # Center horizontally
                title_y = 60  # Căn chỉnh với banner
            else:
                # Fallback position
                title_x = 400
                title_y = 100
                print("Warning: 'ban' layer not found in TMX, using fallback position")
            
            self.screen.blit(title, (title_x - title.get_width() // 2, title_y))
            
            # Tìm layer "button" trong TMX để căn chỉnh nút chính xác
            button_layer = None
            for layer in self.main_menu_tmx.visible_layers:
                if hasattr(layer, 'name') and layer.name == "button":
                    button_layer = layer
                    break
            
            # Lấy offset của layer button nếu tìm thấy
            button_offset_x = getattr(button_layer, 'offsetx', 0) or 0
            button_offset_y = getattr(button_layer, 'offsety', 0) or 0
            
            # Định nghĩa nội dung các button
            button_text = {
                "play": "Chơi",
                "rules": "Luật chơi",
                "developers": "Nhà phát triển",
                "quit": "Thoát",
                "ok": "Đồng ý",
                "back": "Quay lại"
            }
            
            # Vẽ các button với vị trí căn giữa
            # Sử dụng small_font đã cập nhật ở constructor
            for btn_text, btn_rect in self.buttons.items():
                if btn_text not in ["ok", "back"]:
                    text = self.small_font.render(button_text[btn_text], True, (0, 0, 0))
                    # Căn giữa text trên button
                    text_x = btn_rect.centerx - text.get_width() // 2
                    text_y = btn_rect.centery - text.get_height() // 2
                    self.screen.blit(text, (text_x, text_y))
                    
        except Exception as e:
            print(f"Error rendering menu: {e}")
            
        pygame.display.flip()

    def draw_developers(self):
        # Draw the special menu TMX background
        self.screen.blit(self.sp_menu_bg, (0, 0))
        
        # Draw title in the "ban" layer position
        title = self.font.render("Nhà phát triển", True, (0, 0, 0))  # Black text
        # Position aligned with "ban" layer from TMX
        title_x = 250  # Centered in ban layer
        title_y = 50   # Top of ban layer
        self.screen.blit(title, (title_x, title_y))
        
        members = [
            u"Thành viên nhóm:",
            u"",
            u"- Nguyễn Văn Kiệt",
            u"- Nguyễn Tài Nhất",
            u"- Nguyễn Minh Quyết"
        ]
        
        y_offset = 200  # Start in "bong" layer
        for member in members:
            text = self.small_font.render(member, True, (0, 0, 0))  # Black text
            text_x = 250  # Align with bong layer
            self.screen.blit(text, (text_x, y_offset))
            y_offset += 50
            
        # Vẽ nút Quay lại
        back_text = self.small_font.render("Quay lại", True, (0, 0, 0))  # Black text for better visibility
        text_x = self.buttons["back"].centerx - back_text.get_width() // 2
        text_y = self.buttons["back"].centery - back_text.get_height() // 2
        self.screen.blit(back_text, (text_x, text_y))
        
        pygame.display.flip()

    def draw_name_input(self):
        # Draw the main menu TMX background
        self.screen.blit(self.main_menu_bg, (0, 0))
        prompt = self.small_font.render("Nhập tên người chơi:", True, (0, 0, 0))  # Black text
        # Position in the button layer, centered
        prompt_x = 400 - prompt.get_width() // 2
        self.screen.blit(prompt, (prompt_x, 150))
        # Calculate input area dimensions
        input_area_start = 200
        input_spacing = 60
        
        for i in range(4):
            text = self.small_font.render(f"Người chơi {i+1}: {self.player_names[i]}", True, (0, 0, 0))
            
            # Draw text centered
            text_x = 400 - text.get_width() // 2
            text_y = input_area_start + i * input_spacing
            
            # Draw a subtle background for active input
            if i == self.active_input:
                input_rect = pygame.Rect(250, text_y - 5, 300, 40)
                pygame.draw.rect(self.screen, (240, 240, 240), input_rect)
            
            self.screen.blit(text, (text_x, text_y))
        
        # Vẽ nút Đồng ý
        ok_text = self.small_font.render("Bắt đầu", True, (0, 0, 0))  # Black text for better visibility
        text_x = self.buttons["ok"].centerx - ok_text.get_width() // 2
        text_y = self.buttons["ok"].centery - ok_text.get_height() // 2
        self.screen.blit(ok_text, (text_x, text_y))
        
        # Vẽ nút Quay lại
        back_text = self.small_font.render("Quay lại", True, (0, 0, 0))  # Black text for better visibility
        text_x = self.buttons["back"].centerx - back_text.get_width() // 2
        text_y = self.buttons["back"].centery - back_text.get_height() // 2
        self.screen.blit(back_text, (text_x, text_y))
        pygame.display.flip()

    def draw_rules(self):
        # Draw the special menu TMX background
        self.screen.blit(self.sp_menu_bg, (0, 0))
        y_offset = 50
        
        # Draw title in the "ban" layer position
        title = self.font.render("Luật chơi", True, (0, 0, 0))  # Black text
        # Position aligned with "ban" layer from TMX
        title_x = 250  # Centered in ban layer
        title_y = 50   # Top of ban layer
        self.screen.blit(title, (title_x, title_y))
        
        # Vẽ từng dòng luật
        for rule in self.rules_text:
            text = self.small_font.render(rule, True, (0, 0, 0))  # Black text
            self.screen.blit(text, (250, y_offset))  # Align with bong layer
            y_offset += 35  # Slightly reduced spacing for better fit
            
        # Vẽ nút Quay lại (không vẽ khung nút vì đã có trong TMX)
        back_text = self.small_font.render("Quay lại", True, (0, 0, 0))
        text_x = self.buttons["back"].centerx - back_text.get_width() // 2
        text_y = self.buttons["back"].centery - back_text.get_height() // 2
        self.screen.blit(back_text, (text_x, text_y))
        
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.show_rules:
                    if self.buttons["back"].collidepoint(event.pos):
                        self.show_rules = False
                elif self.show_developers:
                    if self.buttons["back"].collidepoint(event.pos):
                        self.show_developers = False
                elif self.show_name_input:
                    if self.buttons["back"].collidepoint(event.pos):
                        self.show_name_input = False
                        # Reset player names when going back
                        self.player_names = ["", "", "", ""]
                    elif self.buttons["ok"].collidepoint(event.pos):
                        # Kiểm tra xem tất cả người chơi đã có tên chưa
                        if all(name.strip() for name in self.player_names):
                            return self.player_names  # Trả về tên người chơi
                    else:
                        # Calculate input area based on TMX button layer position
                        input_area_start = 200
                        input_width = 300
                        input_height = 50
                        input_spacing = 60
                        
                        for i in range(4):
                            # Center input rectangles like TMX buttons
                            input_rect = pygame.Rect(
                                400 - input_width // 2,  # Center horizontally
                                input_area_start + i * input_spacing,
                                input_width,
                                input_height
                            )
                            if input_rect.collidepoint(event.pos):
                                self.active_input = i
                else:
                    if self.buttons["play"].collidepoint(event.pos):
                        self.show_name_input = True
                    elif self.buttons["rules"].collidepoint(event.pos):
                        self.show_rules = True
                    elif self.buttons["developers"].collidepoint(event.pos):
                        self.show_developers = True
                    elif self.buttons["quit"].collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
            elif event.type == pygame.KEYDOWN and self.show_name_input:
                if event.key == pygame.K_BACKSPACE:
                    self.player_names[self.active_input] = self.player_names[self.active_input][:-1]
                elif event.unicode.isprintable():
                    self.player_names[self.active_input] += event.unicode
        
        return None  # Không có kết quả đặc biệt

    def render_tmx(self, tmx_data):
        """Render all layers of a TMX map to a surface with alpha channel support"""
        try:
            # Create a surface with the same size as the TMX map
            map_width = tmx_data.width * tmx_data.tilewidth
            map_height = tmx_data.height * tmx_data.tileheight
            surface = pygame.Surface((map_width, map_height), pygame.SRCALPHA)
            surface.fill((0, 0, 0, 0))  # Fill with transparent background

            width, height = surface.get_size()
            logger.debug(f"Starting to render TMX with dimensions: {width}x{height}")
            
            # Log layer info
            layer_info = []
            for layer in tmx_data.visible_layers:
                if hasattr(layer, 'name'):
                    layer_info.append(f"Layer: {layer.name}")
                    if hasattr(layer, 'offsetx'):
                        layer_info.append(f"  offsetx: {layer.offsetx}")
                    if hasattr(layer, 'offsety'):
                        layer_info.append(f"  offsety: {layer.offsety}")
            logger.debug("Found layers:\n" + "\n".join(layer_info))
            
            # Render each layer
            for layer in tmx_data.visible_layers:
                if not hasattr(layer, 'data'):
                    continue  # Skip non-tile layers
                    
                logger.debug(f"Processing layer: {getattr(layer, 'name', 'unnamed')}")
                
                # Get layer properties
                offset_x = getattr(layer, 'offsetx', 0) or 0
                offset_y = getattr(layer, 'offsety', 0) or 0
                opacity = getattr(layer, 'opacity', 1.0)
                
                logger.debug(f"Layer {layer.name}: offsetx = {offset_x}")
                logger.debug(f"Layer {layer.name}: offsety = {offset_y}")
                logger.debug(f"Layer offsets - x: {offset_x}, y: {offset_y}")
                
                # Create layer surface
                layer_surface = pygame.Surface((map_width, map_height), pygame.SRCALPHA)
                layer_surface.fill((0, 0, 0, 0))
                
                # Get the tileset for this layer
                for x, y, image in layer.tiles():
                    if not image:
                        continue
                        
                    try:
                        # Calculate position with offsets
                        pos_x = int(x * tmx_data.tilewidth + offset_x)
                        pos_y = int(y * tmx_data.tileheight + offset_y)
                        
                        # Handle opacity
                        if opacity < 1.0:
                            image = image.copy()
                            image.fill((255, 255, 255, int(opacity * 255)), 
                                    special_flags=pygame.BLEND_RGBA_MULT)
                        
                        # Blit tile to layer surface
                        layer_surface.blit(image, (pos_x, pos_y))
                    except (TypeError, AttributeError) as e:
                        logger.warning(f"Invalid tile at ({x}, {y}) in layer {layer.name}: {e}")
                        continue
                        
                # Blend layer onto main surface
                surface.blit(layer_surface, (0, 0))
                
            logger.debug("Successfully rendered all layers")
            return surface
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error rendering TMX layer: {error_msg}")
            logger.error("Stack trace:")
            logger.error(traceback.format_exc())
            
            # Return error surface
            error_surface = pygame.Surface((map_width, map_height), pygame.SRCALPHA)
            error_surface.fill(COLORS['error_bg'])
            return error_surface

    def run(self):
        while True:
            result = self.handle_events()
            if (result):  # Nếu handle_events trả về kết quả (tức là tên người chơi)
                return result  # Trả về tên người chơi cho mã gọi
                
            if self.show_rules:
                self.draw_rules()
            elif self.show_developers:
                self.draw_developers()
            elif self.show_name_input:
                self.draw_name_input()
            else:
                self.draw_main_menu()


if __name__ == "__main__":
    board = MainBoard()
    board.run()
