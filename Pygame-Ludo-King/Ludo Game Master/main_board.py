import pygame
import sys

class MainBoard:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((900, 600))
        pygame.display.set_caption("Ludo King - Cờ Cá Ngựa")
        # Sử dụng Tahoma cho tiếng Việt
        self.font = pygame.font.SysFont("tahoma", 74)
        self.small_font = pygame.font.SysFont("tahoma", 36)
        self.buttons = {
            "play": pygame.Rect(350, 200, 200, 50),
            "rules": pygame.Rect(350, 300, 200, 50),
            "quit": pygame.Rect(350, 400, 200, 50),
            "ok": pygame.Rect(350, 500, 200, 50),
            "back": pygame.Rect(50, 500, 200, 50)
        }
        self.player_names = ["", "", "", ""]
        self.show_name_input = False
        self.show_rules = False
        self.active_input = 0
        
        # Luật chơi
        rules_text_unicode = [
            u"",
            u"1. Mỗi người chơi có 4 quân cờ",
            u"2. Tung 2 con xúc xắc để di chuyển quân",
            u"3. Cần tung được tổng 2 con xúc xắc >= 10 để đưa",
            u"    quân vào bàn cờ",
            u"4. Quân có thể đá quân địch về vị trí xuất phát",
            u"5. Người chơi phải đưa tất cả quân về đích để thắng",
            u"6. Quân di chuyển số ô bằng tổng 2 con xúc xắc"
        ]
        self.rules_text = rules_text_unicode

    def draw_main_menu(self):
        self.screen.fill((255, 255, 255))
        title = self.font.render("LUDO", True, (0, 0, 0))
        self.screen.blit(title, (350, 50))
        button_text = {
            "play": "Chơi",
            "rules": "Luật chơi",
            "quit": "Thoát",
            "ok": "Đồng ý",
            "back": "Quay lại"
        }
        for btn_text, btn_rect in self.buttons.items():
            if btn_text not in ["ok", "back"]:
                pygame.draw.rect(self.screen, (0, 0, 0), btn_rect, 2)
                text = self.small_font.render(button_text[btn_text], True, (0, 0, 0))
                # Tính toán vị trí để căn giữa text
                text_width = text.get_width()
                text_x = btn_rect.centerx - text_width // 2
                text_y = btn_rect.centery - text.get_height() // 2
                self.screen.blit(text, (text_x, text_y))
        self.draw_team_members()
        pygame.display.flip()

    def draw_team_members(self):
        members = [u"- Nguyễn Văn Kiệt", u"- Nguyễn Tài Nhất", u"- Nguyễn Minh Quyết"]
        y_offset = 450
        for member in members:
            text = self.small_font.render(member, True, (0, 0, 0))
            self.screen.blit(text, (50, y_offset))
            y_offset += 45

    def draw_name_input(self):
        self.screen.fill((255, 255, 255))
        prompt = self.small_font.render("Nhập tên người chơi:", True, (0, 0, 0))
        self.screen.blit(prompt, (50, 50))
        y_offset = 100
        for i in range(4):
            text = self.small_font.render(f"Người chơi {i+1}: {self.player_names[i]}", True, (0, 0, 0))
            self.screen.blit(text, (50, y_offset))
            y_offset += 50
        # Vẽ nút Đồng ý
        pygame.draw.rect(self.screen, (0, 0, 0), self.buttons["ok"], 2)
        ok_text = self.small_font.render("Bắt đầu", True, (0, 0, 0))
        text_x = self.buttons["ok"].centerx - ok_text.get_width() // 2
        text_y = self.buttons["ok"].centery - ok_text.get_height() // 2
        self.screen.blit(ok_text, (text_x, text_y))
        
        # Vẽ nút Quay lại
        pygame.draw.rect(self.screen, (0, 0, 0), self.buttons["back"], 2)
        back_text = self.small_font.render("Quay lại", True, (0, 0, 0))
        text_x = self.buttons["back"].centerx - back_text.get_width() // 2
        text_y = self.buttons["back"].centery - back_text.get_height() // 2
        self.screen.blit(back_text, (text_x, text_y))
        pygame.display.flip()

    def draw_rules(self):
        self.screen.fill((255, 255, 255))
        y_offset = 50
        
        # Vẽ tiêu đề
        title = self.font.render("Luật chơi", True, (0, 0, 0))
        self.screen.blit(title, (250, 20))
        
        # Vẽ từng dòng luật
        for rule in self.rules_text:
            text = self.small_font.render(rule, True, (0, 0, 0))
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
                    if self.buttons["play"].collidepoint(event.pos):
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
            else:
                self.draw_main_menu()

if __name__ == "__main__":
    board = MainBoard()
    board.run()
