import pygame
import sys
from pytmx.util_pygame import load_pygame  # Thêm import pytmx
from sound_manager import SoundManager
import os

def resource_path(relative_path):
    """Xác định đường dẫn tài nguyên cho cả development và PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        # Khi chạy từ file .exe (tạo bởi PyInstaller)
        base_path = sys._MEIPASS
    else:
        # Khi chạy bình thường từ code
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class MainBoard:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 800))
        pygame.display.set_caption("Ludo AI")
        self.font = pygame.font.SysFont("tahoma", 74)
        self.small_font = pygame.font.SysFont("tahoma", 36)
        self.is_bot = [False] * 4  # Track which players are AI/bots
        
        # Thêm biến quản lý scroll
        self.scroll_x = 0
        self.scroll_y = 0
        self.is_scrolling = False
        self.scroll_start_pos = (0, 0)
        self.SCROLL_SPEED = 15
        
        self.sound_manager = SoundManager()
        # Phóng to nút âm thanh lên gấp 3 lần
        original_size = self.sound_manager.music_button_size
        new_size = (original_size[0] * 3, original_size[1] * 3)
        
        # Tải lại hình ảnh nút âm thanh với kích thước mới
        self.sound_manager.music_button_size = new_size
        self.sound_manager.music_button_on = pygame.transform.scale(self.sound_manager.music_button_on, new_size)
        self.sound_manager.music_button_off = pygame.transform.scale(self.sound_manager.music_button_off, new_size)
        
        # Cập nhật vị trí để đảm bảo nút không bị lệch khỏi màn hình
        self.sound_manager.music_button_rect = pygame.Rect(self.sound_manager.music_button_pos, new_size)
        # Điều chỉnh vị trí nút để phù hợp với kích thước mới
        self.sound_manager.music_button_pos = (700, 20)  # Điều chỉnh vị trí phù hợp
        self.sound_manager.music_button_rect = pygame.Rect(self.sound_manager.music_button_pos, new_size)
            # Kích thước của các bản đồ
        self.map_width = 800
        self.map_height = 800
        
        self.buttons = {
            "play": pygame.Rect(330, 280, 200, 50),
            "rules": pygame.Rect(330, 410, 200, 50),
            "quit": pygame.Rect(340, 645, 200, 50),
            "ok": pygame.Rect(350, 500, 200, 50),
            "back": pygame.Rect(50, 500, 200, 50),
            "developer": pygame.Rect(330, 530, 200, 50)  # Thêm nút Developers
        }
        self.player_names = ["", "", "", ""]
        self.show_name_input = False
        self.show_rules = False
        self.show_developers = False  # Add a flag for the Developers section
        self.active_input = 0
        
        # Biến tùy chỉnh khoảng cách giữa số thứ tự player và khung nhập
        self.player_number_spacing = 170  # Khoảng cách từ số thứ tự đến khung nhập
        self.input_boxes = []  # Danh sách các hộp nhập liệu

        # Tải bản đồ từ file .tmx
        self.map_data = load_pygame(resource_path("assets_ver1/main_menu.tmx"))  # Đường dẫn tới file .tmx
        self.map_layer = pygame.Surface((self.map_data.width * self.map_data.tilewidth,
                                         self.map_data.height * self.map_data.tileheight))

        # Tải bản đồ cho rules
        self.rules_map_data = load_pygame(resource_path("assets_ver1/sp_menu.tmx"))
        self.rules_map_layer = pygame.Surface((self.rules_map_data.width * self.rules_map_data.tilewidth,
                                            self.rules_map_data.height * self.rules_map_data.tileheight))

        # Tải bản đồ cho start menu
        self.start_map_data = load_pygame(resource_path("assets_ver1/start_menu.tmx"))
        self.start_map_layer = pygame.Surface((self.start_map_data.width * self.start_map_data.tilewidth,
                                        self.start_map_data.height * self.start_map_data.tileheight))

        # Vẽ bản đồ lên một surface
        for layer in self.map_data.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, image in layer.tiles():
                    self.map_layer.blit(image, (x * self.map_data.tilewidth, y * self.map_data.tileheight))

        # Vẽ bản đồ rules
        for layer in self.rules_map_data.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, image in layer.tiles():
                    self.rules_map_layer.blit(image, (x * self.rules_map_data.tilewidth, 
                                                    y * self.rules_map_data.tileheight))

        # Vẽ bản đồ start menu
        for layer in self.start_map_data.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, image in layer.tiles():
                    self.start_map_layer.blit(image, (x * self.start_map_data.tilewidth, 
                                                    y * self.start_map_data.tileheight))

        # Luật chơi
        rules_text_unicode = [
            u"",
            u"1. Each player has 4 pieces",
            u"2. Roll out a number greater",
            u"than 10 to move a piece out",
            u"3. Move pieces based on dice roll",
            u"4. Capture opponent's piece",
            u"on the same spot",
            u"5. Special effects on star tiles",
            u"6. Bring all 4 pieces home to win"
        ]
        self.rules_text = rules_text_unicode

    def update_scroll_limits(self):
        """Cập nhật giới hạn cuộn dựa trên kích thước cửa sổ và bản đồ"""
        # Lấy thông tin kích thước màn hình
        screen_width, screen_height = self.screen.get_size()
        
        # Tính toán giới hạn cuộn
        max_scroll_x = max(0, self.map_width - screen_width + 200)
        max_scroll_y = max(0, self.map_height - screen_height + 200)
        
        # Giới hạn vị trí cuộn trong phạm vi cho phép
        self.scroll_x = max(0, min(self.scroll_x, max_scroll_x))
        self.scroll_y = max(0, min(self.scroll_y, max_scroll_y))
        
        return max_scroll_x > 0 or max_scroll_y > 0  # Trả về True nếu cần cuộn
    
    def blit_with_scroll(self, image, position):
        """Vẽ hình ảnh với vị trí đã được điều chỉnh theo cuộn"""
        x, y = position
        self.screen.blit(image, (x - self.scroll_x, y - self.scroll_y))

    def draw_scrollbars(self):
        """Vẽ thanh cuộn nếu cần thiết"""
        # Lấy kích thước màn hình
        screen_width, screen_height = self.screen.get_size()
        
        # Tính giới hạn cuộn
        max_scroll_x = max(0, self.map_width - screen_width)
        max_scroll_y = max(0, self.map_height - screen_height)
        
        # Vẽ thanh cuộn ngang nếu cần
        if max_scroll_x > 0:
            # Tính tỷ lệ và kích thước thanh cuộn
            scrollbar_width = screen_width * (screen_width / self.map_width)
            scrollbar_x = (self.scroll_x / max_scroll_x) * (screen_width - scrollbar_width)
            
            # Vẽ thanh cuộn
            scrollbar_rect = pygame.Rect(scrollbar_x, screen_height - 10, scrollbar_width, 10)
            pygame.draw.rect(self.screen, (100, 100, 100), scrollbar_rect)  # Màu xám
            pygame.draw.rect(self.screen, (50, 50, 50), scrollbar_rect, 1)  # Viền đen
        
        # Vẽ thanh cuộn dọc nếu cần
        if max_scroll_y > 0:
            # Tính tỷ lệ và kích thước thanh cuộn
            scrollbar_height = screen_height * (screen_height / self.map_height)
            scrollbar_y = (self.scroll_y / max_scroll_y) * (screen_height - scrollbar_height)
            
            # Vẽ thanh cuộn
            scrollbar_rect = pygame.Rect(screen_width - 10, scrollbar_y, 10, scrollbar_height)
            pygame.draw.rect(self.screen, (100, 100, 100), scrollbar_rect)  # Màu xám
            pygame.draw.rect(self.screen, (50, 50, 50), scrollbar_rect, 1)  # Viền đen

    def draw_main_menu(self):
        # Xóa màn hình
        self.screen.fill((0, 0, 0))
        # Vẽ background từ bản đồ
        self.screen.blit(self.map_layer, (-self.scroll_x, -self.scroll_y))

        title = self.font.render("LUDO", True, (0, 0, 0))
        title_pos = (330 - self.scroll_x, 100 - self.scroll_y)
        self.screen.blit(title, title_pos)
        button_text = {
            "play": "Play",
            "rules": "Rules",
            "quit": "Quit",
            "ok": "Start",
            "back": "Back",
            "developer": "Developers",
        }
        # Cập nhật vị trí của các nút với vị trí cuộn
        adjusted_buttons = {}
        for btn_name, btn_rect in self.buttons.items():
            if btn_name not in ["ok", "back"]:  # Nút ok và back sẽ được xử lý trong các màn hình khác
                adjusted_rect = pygame.Rect(
                    btn_rect.x - self.scroll_x,
                    btn_rect.y - self.scroll_y,
                    btn_rect.width,
                    btn_rect.height
                )
                adjusted_buttons[btn_name] = adjusted_rect
                
                # Vẽ text cho các nút với vị trí đã điều chỉnh
                if btn_name not in ["ok", "back", "quit"]:
                    text = self.small_font.render(button_text[btn_name], True, (0, 0, 0))
                    text_width = text.get_width()
                    text_x = adjusted_rect.centerx - text_width // 2
                    text_y = adjusted_rect.centery - text.get_height() // 2
                    self.screen.blit(text, (text_x, text_y))

        # Tùy chỉnh font chữ cho nút quit
        quit_button_font_size = 28
        quit_font = pygame.font.SysFont("tahoma", quit_button_font_size)
        
        # Vẽ nút Quit với font chữ được tùy chỉnh
        quit_text = quit_font.render(button_text["quit"], True, (0, 0, 0))
        quit_rect = adjusted_buttons["quit"]
        text_x = quit_rect.centerx - quit_text.get_width() // 2
        text_y = quit_rect.centery - quit_text.get_height() // 2
        self.screen.blit(quit_text, (text_x, text_y))
        
        # Vẽ thanh cuộn nếu cần
        if self.update_scroll_limits():
            self.draw_scrollbars()

        self.sound_manager.draw_music_button(self.screen, self.scroll_x, self.scroll_y)
        pygame.display.flip()


    def draw_name_input(self):
        # Xóa màn hình
        self.screen.fill((0, 0, 0))
        # Vẽ background từ bản đồ start menu
        self.screen.blit(self.start_map_layer, (-self.scroll_x, -self.scroll_y))
        
        # Tạo font chữ cho prompt
        prompt_font = pygame.font.SysFont("tahoma", 37)
        prompt = prompt_font.render("START A NEW GAME", True, (0, 0, 0))
        self.screen.blit(prompt, (240 - self.scroll_x, 50 - self.scroll_y))
    
        title_font = pygame.font.SysFont("tahoma", 28)
        # Điều chỉnh vị trí của tiêu đề
        title_player = title_font.render("Player", True, (0, 0, 0))
        self.screen.blit(title_player, (115 - self.scroll_x, 230 - self.scroll_y))
        
        title_name = title_font.render("Name", True, (0, 0, 0))
        self.screen.blit(title_name, (320 - self.scroll_x, 230 - self.scroll_y))
        
        title_bot = title_font.render("Bot", True, (0, 0, 0))
        self.screen.blit(title_bot, (670 - self.scroll_x, 230 - self.scroll_y))
        
        # Tạo khung nhập và hiển thị tên người chơi
        input_font = pygame.font.SysFont("tahoma", 26)
        y_offset = 325
        self.input_boxes = []  # Reset input boxes
        
        for i in range(4):
            # Hiển thị số thứ tự người chơi
            player_number = self.small_font.render(f"{i+1}", True, (0, 0, 0))
            self.screen.blit(player_number, (140 - self.scroll_x, y_offset - self.scroll_y))
            
            # Tạo hộp nhập văn bản với vị trí tùy chỉnh dựa trên khoảng cách
            input_rect = pygame.Rect(90 + self.player_number_spacing - self.scroll_x, y_offset - self.scroll_y, 200, 40)
            self.input_boxes.append(input_rect)

            # Add toggle button for AI/Human
            toggle_rect = pygame.Rect(635 - self.scroll_x, y_offset - self.scroll_y, 100, 40)
            toggle_text = "YES" if self.is_bot[i] else "NO"
            toggle_surface = input_font.render(toggle_text, True, (0, 0, 0))
            toggle_x = toggle_rect.centerx - toggle_surface.get_width() // 2
            toggle_y = toggle_rect.centery - toggle_surface.get_height() // 2
            self.screen.blit(toggle_surface, (toggle_x, toggle_y))
            
            # Store toggle button rect for click detection
            if not hasattr(self, 'toggle_boxes'):
                self.toggle_boxes = []
            while len(self.toggle_boxes) <= i:
                self.toggle_boxes.append(None)
            self.toggle_boxes[i] = toggle_rect
            
            
            # Luôn hiển thị text đã nhập
            name_text = input_font.render(self.player_names[i], True, (0, 0, 0))
            self.screen.blit(name_text, (100 + self.player_number_spacing - self.scroll_x, y_offset + 5 - self.scroll_y))
            
            # Hiển thị dấu nháy nếu đây là ô đang được chọn
            if i == self.active_input and pygame.time.get_ticks() % 1000 < 500:
                cursor_pos = 100 + self.player_number_spacing + name_text.get_width()
                pygame.draw.line(self.screen, (0, 0, 0), (cursor_pos - self.scroll_x, y_offset + 5 - self.scroll_y), (cursor_pos - self.scroll_x, y_offset + 35 - self.scroll_y), 2)
            
            y_offset += 100

        # Thêm khả năng chỉnh sửa vị trí nút ok
        ok_button_x = 425  # Giá trị mặc định cho vị trí x của nút ok
        ok_button_y = 715  # Giá trị mặc định cho vị trí y của nút ok

        # Thêm khả năng tùy chỉnh kích thước và font chữ của nút ok
        ok_button_width = 250  # Giá trị mặc định cho chiều rộng của nút ok
        ok_button_height = 60  # Giá trị mặc định cho chiều cao của nút ok
        ok_button_font_size = 27  # Giá trị mặc định cho kích thước font chữ của nút ok

        # Cập nhật vùng bấm của nút ok với kích thước mới
        ok_button_rect = pygame.Rect(ok_button_x - self.scroll_x, ok_button_y - self.scroll_y, ok_button_width, ok_button_height)

        # Vẽ nút Đồng ý với kích thước và font chữ được tùy chỉnh
        ok_font = pygame.font.SysFont("tahoma", ok_button_font_size)
        ok_text = ok_font.render("START", True, (0, 0, 0))
        text_x = ok_button_rect.centerx - ok_text.get_width() // 2
        text_y = ok_button_rect.centery - ok_text.get_height() // 2
        self.screen.blit(ok_text, (text_x, text_y))

        # Cập nhật vùng bấm của nút ok
        self.buttons["ok"] = ok_button_rect

        # Thêm khả năng chỉnh sửa vị trí nút back
        back_button_x = 130  # Giá trị mặc định cho vị trí x của nút back
        back_button_y = 715  # Giá trị mặc định cho vị trí y của nút back

        # Thêm khả năng tùy chỉnh kích thước và font chữ của nút back
        back_button_width = 250  # Giá trị mặc định cho chiều rộng của nút back
        back_button_height = 60  # Giá trị mặc định cho chiều cao của nút back
        back_button_font_size = 27  # Giá trị mặc định cho kích thước font chữ của nút back

        # Cập nhật vùng bấm của nút back với kích thước mới
        back_button_rect = pygame.Rect(back_button_x - self.scroll_x, back_button_y - self.scroll_y, back_button_width, back_button_height)

        # Vẽ nút Quay lại với kích thước và font chữ được tùy chỉnh
        back_font = pygame.font.SysFont("tahoma", back_button_font_size)
        back_text = back_font.render("BACK", True, (0, 0, 0))
        text_x = back_button_rect.centerx - back_text.get_width() // 2
        text_y = back_button_rect.centery - back_text.get_height() // 2
        self.screen.blit(back_text, (text_x, text_y))

        # Cập nhật vùng bấm của nút back
        self.buttons["back"] = back_button_rect
        
        pygame.display.flip()

    def draw_rules(self):
        # Xóa màn hình
        self.screen.fill((0, 0, 0))
        # Vẽ background từ bản đồ rules
        self.screen.blit(self.rules_map_layer, (0 - self.scroll_x, 0 - self.scroll_y))
        y_offset = 200  # Tăng giá trị ban đầu để các dòng bắt đầu thấp hơn
        initial_offset = 50  # Giá trị cố định để tăng vị trí dòng đầu tiên
        y_offset += initial_offset  # Chỉ tăng vị trí dòng đầu tiên

        # Vẽ tiêu đề
        title = self.font.render("Rules", True, (0, 0, 0))
        self.screen.blit(title, (340 - self.scroll_x, 100 - self.scroll_y))

        # Tạo font nhỏ hơn cho rules_text
        small_rules_font = pygame.font.SysFont("tahoma", 24)

        # Vẽ từng dòng luật với font nhỏ hơn
        for rule in self.rules_text:
            text = small_rules_font.render(rule, True, (0, 0, 0))
            self.screen.blit(text, (240 - self.scroll_x, y_offset - self.scroll_y))
            y_offset += 40  # Khoảng cách giữa các dòng không thay đổi
            
        # Thêm khả năng chỉnh sửa vị trí nút back
        back_button_x = 320  # Giá trị mặc định cho vị trí x của nút back
        back_button_y = 720  # Giá trị mặc định cho vị trí y của nút back

        # Thêm khả năng tùy chỉnh kích thước và font chữ của nút back
        back_button_width = 250  # Giá trị mặc định cho chiều rộng của nút back
        back_button_height = 60  # Giá trị mặc định cho chiều cao của nút back
        back_button_font_size = 28  # Giá trị mặc định cho kích thước font chữ của nút back

        # Cập nhật vùng bấm của nút back với kích thước mới
        back_button_rect = pygame.Rect(back_button_x - self.scroll_x, back_button_y - self.scroll_y, back_button_width, back_button_height)

        # Vẽ nút Quay lại với kích thước và font chữ được tùy chỉnh
        back_font = pygame.font.SysFont("tahoma", back_button_font_size)
        back_text = back_font.render("BACK", True, (0, 0, 0))
        text_x = back_button_rect.centerx - back_text.get_width() // 2
        text_y = back_button_rect.centery - back_text.get_height() // 2
        self.screen.blit(back_text, (text_x, text_y))

        # Cập nhật vùng bấm của nút back
        self.buttons["back"] = back_button_rect
        
        pygame.display.flip()

    def draw_developers(self):
        # Xóa màn hình
        self.screen.fill((0, 0, 0))
        # Vẽ background từ bản đồ rules
        self.screen.blit(self.rules_map_layer, (0 - self.scroll_x, 0 - self.scroll_y))
        y_offset = 50
        title = self.font.render("Developers", True, (0, 0, 0))
        self.screen.blit(title, (250 - self.scroll_x, 100 - self.scroll_y))

        developers = [
            "- Nguyen Van Kiet",
            "- Nguyen Tai Nhat",
            "- Nguyen Minh Quyet"
        ]

        # Tạo font nhỏ hơn cho developers text
        small_developers_font = pygame.font.SysFont("tahoma", 32)

        # Vẽ từng dòng developers với font nhỏ hơn và vị trí tùy chỉnh
        y_offset = 300  # Tăng giá trị ban đầu để các dòng bắt đầu thấp hơn
        for dev in developers:
            text = small_developers_font.render(dev, True, (0, 0, 0))
            self.screen.blit(text, (240 - self.scroll_x, y_offset - self.scroll_y))
            y_offset += 40  # Khoảng cách giữa các dòng không thay đổi

        # Thêm khả năng chỉnh sửa vị trí nút back
        back_button_x = 320  # Giá trị mặc định cho vị trí x của nút back
        back_button_y = 720  # Giá trị mặc định cho vị trí y của nút back

        # Thêm khả năng tùy chỉnh kích thước và font chữ của nút back
        back_button_width = 250  # Giá trị mặc định cho chiều rộng của nút back
        back_button_height = 60  # Giá trị mặc định cho chiều cao của nút back
        back_button_font_size = 28  # Giá trị mặc định cho kích thước font chữ của nút back

        # Cập nhật vùng bấm của nút back với kích thước mới
        back_button_rect = pygame.Rect(back_button_x - self.scroll_x, back_button_y - self.scroll_y, back_button_width, back_button_height)

        # Vẽ nút Quay lại với kích thước và font chữ được tùy chỉnh
        back_font = pygame.font.SysFont("tahoma", back_button_font_size)
        back_text = back_font.render("BACK", True, (0, 0, 0))
        text_x = back_button_rect.centerx - back_text.get_width() // 2
        text_y = back_button_rect.centery - back_text.get_height() // 2
        self.screen.blit(back_text, (text_x, text_y))

        # Cập nhật vùng bấm của nút back
        self.buttons["back"] = back_button_rect

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Xử lý sự kiện cuộn chuột
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Xử lý cuộn bằng bánh xe chuột
                if event.button == 4:  # Cuộn lên
                    self.scroll_y = max(0, self.scroll_y - self.SCROLL_SPEED)
                    self.update_scroll_limits()
                elif event.button == 5:  # Cuộn xuống
                    self.scroll_y += self.SCROLL_SPEED
                    self.update_scroll_limits()
                    
                # Bắt đầu kéo thả để cuộn
                elif event.button == 3:  # Chuột phải
                    self.is_scrolling = True
                    self.scroll_start_pos = event.pos
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)
                
                # Xử lý click chuột trái
                elif event.button == 1:
                    # Điều chỉnh vị trí chuột để tính đến cuộn khi kiểm tra va chạm
                    adjusted_pos = (event.pos[0] + self.scroll_x, event.pos[1] + self.scroll_y)
                    
                    # Xử lý click vào các nút trong các màn hình khác nhau
                    if self.show_developers:
                        if self.buttons["back"].collidepoint(event.pos):
                            self.show_developers = False
                    elif self.show_rules:
                        if self.buttons["back"].collidepoint(event.pos):
                            self.show_rules = False
                    elif self.show_name_input:
                        if self.buttons["back"].collidepoint(event.pos):
                            self.show_name_input = False
                            self.player_names = ["", "", "", ""]
                        elif self.buttons["ok"].collidepoint(event.pos):
                            if all(name.strip() for name in self.player_names):
                                # Add [AI] suffix to AI player names and track AI players
                                player_names_with_ai = []
                                ai_players = []
                                for i in range(4):
                                    name = self.player_names[i]
                                    if self.is_bot[i]:
                                        name = f"{name} [AI]"
                                        ai_players.append(i)  # Track which players are AI
                                    player_names_with_ai.append(name)
                                return player_names_with_ai, ai_players  # Return both names and AI player indices
                        else:
                            # Check for toggle button clicks first
                            for i in range(len(self.toggle_boxes)):
                                if self.toggle_boxes[i].collidepoint(event.pos):
                                    self.is_bot[i] = not self.is_bot[i]
                                    break
                            else:
                                # If no toggle was clicked, check input boxes
                                for i in range(len(self.input_boxes)):
                                    adjusted_box = pygame.Rect(
                                        self.input_boxes[i].x,
                                        self.input_boxes[i].y,
                                        self.input_boxes[i].width,
                                        self.input_boxes[i].height
                                    )
                                    if adjusted_box.collidepoint(event.pos):
                                        self.active_input = i
                    else:
                        # Điều chỉnh vùng nhấp vào các nút trong menu chính
                        for btn_name, btn_rect in self.buttons.items():
                            if btn_rect.collidepoint(adjusted_pos):
                                if btn_name == "developer":
                                    self.show_developers = True
                                elif btn_name == "play":
                                    self.show_name_input = True
                                elif btn_name == "rules":
                                    self.show_rules = True
                                elif btn_name == "quit":
                                    pygame.quit()
                                    sys.exit()
            
            # Xử lý kéo thả để cuộn
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:  # Chuột phải
                    self.is_scrolling = False
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            
            # Xử lý di chuyển chuột để cuộn
            elif event.type == pygame.MOUSEMOTION:
                # Xử lý di chuyển khi đang cuộn
                if self.is_scrolling:
                    dx = self.scroll_start_pos[0] - event.pos[0]
                    dy = self.scroll_start_pos[1] - event.pos[1]
                    
                    self.scroll_x += dx
                    self.scroll_y += dy
                    
                    self.update_scroll_limits()
                    self.scroll_start_pos = event.pos
            
            # Xử lý nhập văn bản
            elif event.type == pygame.KEYDOWN and self.show_name_input:
                if event.key == pygame.K_BACKSPACE:
                    self.player_names[self.active_input] = self.player_names[self.active_input][:-1]
                elif len(self.player_names[self.active_input]) < 10:  # Giới hạn tối đa 10 ký tự
                    self.player_names[self.active_input] += event.unicode
                    
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Kiểm tra click nút nhạc
                if self.sound_manager.check_music_button_click(event.pos, self.scroll_x, self.scroll_y):
                    continue  # Bỏ qua xử lý click khác nếu đã click vào nút nhạc
        
        return None  # Không có kết quả đặc biệt

    def run(self):
        # Đảm bảo các giá trị ban đầu được thiết lập
        self.scroll_x = 0
        self.scroll_y = 0
        self.is_scrolling = False
        
        while True:
            result = self.handle_events()
            if result:  # Nếu handle_events trả về kết quả (tức là tên người chơi và trạng thái bot)
                return result  # Trả về tuple (tên người chơi, trạng thái bot) cho mã gọi

            if self.show_rules:
                self.draw_rules()
            elif self.show_name_input:
                self.draw_name_input()
            elif self.show_developers:
                self.draw_developers()
            else:
                self.draw_main_menu()
                
            # Kiểm tra và vẽ thanh cuộn nếu cần
            if self.update_scroll_limits():
                self.draw_scrollbars()
                
            pygame.display.flip()

if __name__ == "__main__":
    board = MainBoard()
    board.run()
