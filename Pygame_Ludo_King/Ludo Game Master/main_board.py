import pygame
import sys
from pytmx.util_pygame import load_pygame  # Thêm import pytmx

class MainBoard:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 800))
        pygame.display.set_caption("Ludo AI")
        self.font = pygame.font.SysFont("tahoma", 74)
        self.small_font = pygame.font.SysFont("tahoma", 36)
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

        # Tải bản đồ từ file .tmx
        self.map_data = load_pygame("assets_ver1/main_menu.tmx")  # Đường dẫn tới file .tmx
        self.map_layer = pygame.Surface((self.map_data.width * self.map_data.tilewidth,
                                         self.map_data.height * self.map_data.tileheight))

        # Tải bản đồ cho rules
        self.rules_map_data = load_pygame("assets_ver1/sp_menu.tmx")
        self.rules_map_layer = pygame.Surface((self.rules_map_data.width * self.rules_map_data.tilewidth,
                                            self.rules_map_data.height * self.rules_map_data.tileheight))

        # Tải bản đồ cho start menu
        self.start_map_data = load_pygame("assets_ver1/start_menu.tmx")
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

    def draw_main_menu(self):
        # Vẽ background từ bản đồ
        self.screen.blit(self.map_layer, (0, 0))

        title = self.font.render("LUDO", True, (0, 0, 0))
        self.screen.blit(title, (330, 100))
        button_text = {
            "play": "Play",
            "rules": "Rules",
            "quit": "Quit",
            "ok": "Start",
            "back": "Back",
            "developer": "Developers",
        }
        # Xóa đoạn vẽ text quit trùng lặp
        for btn_text, btn_rect in self.buttons.items():
            if btn_text not in ["ok", "back", "quit"]:
                text = self.small_font.render(button_text[btn_text], True, (0, 0, 0))
                # Tính toán vị trí để căn giữa text
                text_width = text.get_width()
                text_x = btn_rect.centerx - text_width // 2
                text_y = btn_rect.centery - text.get_height() // 2
                self.screen.blit(text, (text_x, text_y))

        # Tùy chỉnh font chữ cho nút quit
        quit_button_font_size = 28  # Giá trị mặc định cho kích thước font chữ của nút quit
        quit_font = pygame.font.SysFont("tahoma", quit_button_font_size)

        # Vẽ nút Quit với font chữ được tùy chỉnh
        quit_text = quit_font.render(button_text["quit"], True, (0, 0, 0))
        text_x = self.buttons["quit"].centerx - quit_text.get_width() // 2
        text_y = self.buttons["quit"].centery - quit_text.get_height() // 2
        self.screen.blit(quit_text, (text_x, text_y))

        pygame.display.flip()


    def draw_name_input(self):
        # Vẽ background từ bản đồ start menu
        self.screen.blit(self.start_map_layer, (0, 0))
        
        prompt = self.small_font.render("START A NEW GAME", True, (0, 0, 0))
        self.screen.blit(prompt, (240, 50))
        
        y_offset = 100
        for i in range(4):
            text = self.small_font.render(f"Player {i+1}: {self.player_names[i]}", True, (0, 0, 0))
            self.screen.blit(text, (50, y_offset))
            y_offset += 50

        # Thêm khả năng chỉnh sửa vị trí nút ok
        ok_button_x = 425  # Giá trị mặc định cho vị trí x của nút ok
        ok_button_y = 715  # Giá trị mặc định cho vị trí y của nút ok

        # Thêm khả năng tùy chỉnh kích thước và font chữ của nút ok
        ok_button_width = 250  # Giá trị mặc định cho chiều rộng của nút ok
        ok_button_height = 60  # Giá trị mặc định cho chiều cao của nút ok
        ok_button_font_size = 27  # Giá trị mặc định cho kích thước font chữ của nút ok

        # Cập nhật vùng bấm của nút ok với kích thước mới
        ok_button_rect = pygame.Rect(ok_button_x, ok_button_y, ok_button_width, ok_button_height)

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
        back_button_rect = pygame.Rect(back_button_x, back_button_y, back_button_width, back_button_height)

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
        # Vẽ background từ bản đồ rules
        self.screen.blit(self.rules_map_layer, (0, 0))
        y_offset = 200  # Tăng giá trị ban đầu để các dòng bắt đầu thấp hơn
        initial_offset = 50  # Giá trị cố định để tăng vị trí dòng đầu tiên
        y_offset += initial_offset  # Chỉ tăng vị trí dòng đầu tiên

        # Vẽ tiêu đề
        title = self.font.render("Rules", True, (0, 0, 0))
        self.screen.blit(title, (340, 100))

        # Tạo font nhỏ hơn cho rules_text
        small_rules_font = pygame.font.SysFont("tahoma", 24)

        # Vẽ từng dòng luật với font nhỏ hơn
        for rule in self.rules_text:
            text = small_rules_font.render(rule, True, (0, 0, 0))
            self.screen.blit(text, (240, y_offset))
            y_offset += 40  # Khoảng cách giữa các dòng không thay đổi
            
        # Thêm khả năng chỉnh sửa vị trí nút back
        back_button_x = 320  # Giá trị mặc định cho vị trí x của nút back
        back_button_y = 720  # Giá trị mặc định cho vị trí y của nút back

        # Thêm khả năng tùy chỉnh kích thước và font chữ của nút back
        back_button_width = 250  # Giá trị mặc định cho chiều rộng của nút back
        back_button_height = 60  # Giá trị mặc định cho chiều cao của nút back
        back_button_font_size = 28  # Giá trị mặc định cho kích thước font chữ của nút back

        # Cập nhật vùng bấm của nút back với kích thước mới
        back_button_rect = pygame.Rect(back_button_x, back_button_y, back_button_width, back_button_height)

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
        # Vẽ background từ bản đồ rules
        self.screen.blit(self.rules_map_layer, (0, 0))
        y_offset = 50
        title = self.font.render("Developers", True, (0, 0, 0))
        self.screen.blit(title, (250, 100))

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
            self.screen.blit(text, (240, y_offset))
            y_offset += 40  # Khoảng cách giữa các dòng không thay đổi

        # Thêm khả năng chỉnh sửa vị trí nút back
        back_button_x = 320  # Giá trị mặc định cho vị trí x của nút back
        back_button_y = 720  # Giá trị mặc định cho vị trí y của nút back

        # Thêm khả năng tùy chỉnh kích thước và font chữ của nút back
        back_button_width = 250  # Giá trị mặc định cho chiều rộng của nút back
        back_button_height = 60  # Giá trị mặc định cho chiều cao của nút back
        back_button_font_size = 28  # Giá trị mặc định cho kích thước font chữ của nút back

        # Cập nhật vùng bấm của nút back với kích thước mới
        back_button_rect = pygame.Rect(back_button_x, back_button_y, back_button_width, back_button_height)

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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.show_developers:
                    if self.buttons["back"].collidepoint(event.pos):
                        self.show_developers = False
                elif self.show_rules:
                    if self.buttons["back"].collidepoint(event.pos):
                        self.show_rules = False
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
                        for i in range(4):
                            if pygame.Rect(50, 100 + i * 50, 300, 50).collidepoint(event.pos):
                                self.active_input = i
                else:
                    if self.buttons["developer"].collidepoint(event.pos):
                        self.show_developers = True
                    elif self.buttons["play"].collidepoint(event.pos):
                        self.show_name_input = True
                    elif self.buttons["rules"].collidepoint(event.pos):
                        self.show_rules = True
                    elif self.buttons["quit"].collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
            elif event.type == pygame.KEYDOWN and self.show_name_input:
                if event.key == pygame.K_BACKSPACE:
                    self.player_names[self.active_input] = self.player_names[self.active_input][:-1]
                else:
                    self.player_names[self.active_input] += event.unicode
        
        return None  # Không có kết quả đặc biệt

    def run(self):
        while True:
            result = self.handle_events()
            if result:  # Nếu handle_events trả về kết quả (tức là tên người chơi)
                return result  # Trả về tên người chơi cho mã gọi

            if self.show_rules:
                self.draw_rules()
            elif self.show_name_input:
                self.draw_name_input()
            elif self.show_developers:
                self.draw_developers()
            else:
                self.draw_main_menu()

if __name__ == "__main__":
    board = MainBoard()
    board.run()
