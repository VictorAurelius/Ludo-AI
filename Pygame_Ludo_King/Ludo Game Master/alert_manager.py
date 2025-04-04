import pygame

class AlertManager:
    def __init__(self):
        self.alerts = []  # Danh sách các thông báo [(message, time, duration)]
        self.max_alerts = 5  # Số thông báo tối đa hiển thị cùng lúc
        
    def add_alert(self, message, duration=2000):
        """Thêm một thông báo vào danh sách"""
        current_time = pygame.time.get_ticks()
        self.alerts.append((message, current_time, duration))
        
        # Nếu số thông báo vượt quá giới hạn, xóa thông báo cũ nhất
        if len(self.alerts) > self.max_alerts:
            self.alerts.pop(0)
    
    def update(self):
        """Cập nhật danh sách thông báo, loại bỏ những thông báo đã hết thời gian hiển thị"""
        current_time = pygame.time.get_ticks()
        self.alerts = [(msg, time, duration) for msg, time, duration in self.alerts
                      if current_time - time < duration]
    
    def draw(self, screen):
        """Vẽ tất cả các thông báo hiện tại"""
        if not self.alerts:
            return
            
        for i, (message, time, duration) in enumerate(self.alerts):
            # Tính toán vị trí dựa trên chỉ số (thông báo mới nhất ở dưới cùng)
            y_position = 50 + i * 60  # Khoảng cách giữa các thông báo
            
            # Tạo surface bán trong suốt cho background
            alert_bg = pygame.Surface((400, 50))
            alert_bg.set_alpha(200)
            alert_bg.fill((0, 0, 0))
            
            # Vẽ background ở giữa màn hình
            x = (screen.get_width() - 400) // 2
            screen.blit(alert_bg, (x, y_position))
            
            # Vẽ text
            vn_font = pygame.font.SysFont("segoeui", 24)
            text_surface = vn_font.render(message, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, y_position + 25))
            screen.blit(text_surface, text_rect)
            
            # Hiệu ứng fadeout khi gần hết thời gian
            time_left = duration - (pygame.time.get_ticks() - time)
            if time_left < 500:  # Nếu còn dưới 0.5 giây
                alpha = int(time_left / 500 * 255)  # Tính toán độ trong suốt
                text_surface.set_alpha(alpha)