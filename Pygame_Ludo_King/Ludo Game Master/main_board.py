import pygame
import sys

class MainBoard:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 800))
        pygame.display.set_caption("Ludo King - Cờ Cá Ngựa")
        # Load water texture
        self.water_tile = pygame.image.load("assets_ver1/TinySwords/Terrain/Water/Water.png")
        # Create a surface for the tiled background
        self.background = pygame.Surface((800, 800))
        # Tile the water texture across the background
        tile_size = 25  # from Water.tsx tilewidth/tileheight
        for y in range(0, 800, tile_size):
            for x in range(0, 800, tile_size):
                self.background.blit(self.water_tile, (x, y), (0, 0, tile_size, tile_size))
        # Sử dụng Tahoma cho tiếng Việt
        self.font = pygame.font.SysFont("tahoma", 74)
        self.small_font = pygame.font.SysFont("tahoma", 36)
        self.buttons = {
            "play": pygame.Rect(300, 250, 200, 50),
            "rules": pygame.Rect(300, 350, 200, 50),
            "developers": pygame.Rect(300, 450, 200, 50),
            "quit": pygame.Rect(300, 550, 200, 50),
            "ok": pygame.Rect(300, 650, 200, 50),
            "back": pygame.Rect(50, 650, 200, 50)
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
        self.screen.blit(self.background, (0, 0))
        title = self.font.render("LUDO", True, (255, 255, 255))
        self.screen.blit(title, (300, 150))
        button_text = {
            "play": "Chơi",
            "rules": "Luật chơi",
            "developers": "Nhà phát triển",
            "quit": "Thoát",
            "ok": "Đồng ý",
            "back": "Quay lại"
        }
        for btn_text, btn_rect in self.buttons.items():
            if btn_text not in ["ok", "back"]:
                pygame.draw.rect(self.screen, (0, 0, 0), btn_rect, 2)
                text = self.small_font.render(button_text[btn_text], True, (255, 255, 255))
                # Tính toán vị trí để căn giữa text
                text_width = text.get_width()
                text_x = btn_rect.centerx - text_width // 2
                text_y = btn_rect.centery - text.get_height() // 2
                self.screen.blit(text, (text_x, text_y))
        pygame.display.flip()

    def draw_developers(self):
        self.screen.blit(self.background, (0, 0))
        title = self.font.render("Nhà phát triển", True, (0, 0, 0))
        self.screen.blit(title, (200, 100))
        
        members = [
            u"Thành viên nhóm:",
            u"",
            u"- Nguyễn Văn Kiệt",
            u"- Nguyễn Tài Nhất",
            u"- Nguyễn Minh Quyết"
        ]
        
        y_offset = 250
        for member in members:
            text = self.small_font.render(member, True, (255, 255, 255))
            text_x = 400 - text.get_width() // 2
            self.screen.blit(text, (text_x, y_offset))
            y_offset += 50
            
        # Vẽ nút Quay lại
        pygame.draw.rect(self.screen, (0, 0, 0), self.buttons["back"], 2)
        back_text = self.small_font.render("Quay lại", True, (255, 255, 255))
        text_x = self.buttons["back"].centerx - back_text.get_width() // 2
        text_y = self.buttons["back"].centery - back_text.get_height() // 2
        self.screen.blit(back_text, (text_x, text_y))
        
        pygame.display.flip()

    def draw_name_input(self):
        self.screen.blit(self.background, (0, 0))
        prompt = self.small_font.render("Nhập tên người chơi:", True, (255, 255, 255))
        self.screen.blit(prompt, (50, 150))
        y_offset = 200
        for i in range(4):
            text = self.small_font.render(f"Người chơi {i+1}: {self.player_names[i]}", True, (255, 255, 255))
            self.screen.blit(text, (50, y_offset))
            y_offset += 80
        # Vẽ nút Đồng ý
        pygame.draw.rect(self.screen, (0, 0, 0), self.buttons["ok"], 2)
        ok_text = self.small_font.render("Bắt đầu", True, (255, 255, 255))
        text_x = self.buttons["ok"].centerx - ok_text.get_width() // 2
        text_y = self.buttons["ok"].centery - ok_text.get_height() // 2
        self.screen.blit(ok_text, (text_x, text_y))
        
        # Vẽ nút Quay lại
        pygame.draw.rect(self.screen, (0, 0, 0), self.buttons["back"], 2)
        back_text = self.small_font.render("Quay lại", True, (255, 255, 255))
        text_x = self.buttons["back"].centerx - back_text.get_width() // 2
        text_y = self.buttons["back"].centery - back_text.get_height() // 2
        self.screen.blit(back_text, (text_x, text_y))
        pygame.display.flip()

    def draw_rules(self):
        self.screen.blit(self.background, (0, 0))
        y_offset = 50
        
        # Vẽ tiêu đề
        title = self.font.render("Luật chơi", True, (255, 255, 255))
        self.screen.blit(title, (250, 100))
        
        # Vẽ từng dòng luật
        for rule in self.rules_text:
            text = self.small_font.render(rule, True, (255, 255, 255))
            self.screen.blit(text, (50, y_offset))
            y_offset += 40
            
        # Vẽ nút Quay lại
        pygame.draw.rect(self.screen, (0, 0, 0), self.buttons["back"], 2)
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
                        for i in range(4):
                            if pygame.Rect(50, 200 + i * 80, 300, 50).collidepoint(event.pos):
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
            elif self.show_developers:
                self.draw_developers()
            elif self.show_name_input:
                self.draw_name_input()
            else:
                self.draw_main_menu()


if __name__ == "__main__":
    board = MainBoard()
    board.run()
