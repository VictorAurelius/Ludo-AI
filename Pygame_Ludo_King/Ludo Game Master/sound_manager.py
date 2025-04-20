import pygame
import os
import sys

def resource_path(relative_path):
    """Xác định đường dẫn tài nguyên cho cả development và PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        # Khi chạy từ file .exe (tạo bởi PyInstaller)
        base_path = sys._MEIPASS
    else:
        # Khi chạy bình thường từ code
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class SoundManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        pygame.mixer.init()
        
        # Biến trạng thái nhạc
        self.music_playing = True
        
        # Tải hình ảnh nút nhạc
        self.music_button_on = pygame.image.load(resource_path('img/regular_03.png'))
        self.music_button_off = pygame.image.load(resource_path('img/pressed_03.png'))
        
        # Kích thước và vị trí nút nhạc
        self.music_button_size = (32, 32)
        self.music_button_on = pygame.transform.scale(self.music_button_on, self.music_button_size)
        self.music_button_off = pygame.transform.scale(self.music_button_off, self.music_button_size)
        self.music_button_pos = (750, 20)
        self.music_button_rect = pygame.Rect(self.music_button_pos, self.music_button_size)
        
        # Tải nhạc nền
        try:
            pygame.mixer.music.load(resource_path('sound/nhac-nen.mp3'))
            pygame.mixer.music.set_volume(0.5)  # 50% âm lượng
            pygame.mixer.music.play(-1)  # -1 để lặp vô hạn
        except Exception as e:
            print(f"Không thể tải nhạc nền: {e}")
            
        self._initialized = True
    
    def toggle_music(self):
        """Bật/tắt nhạc nền"""
        self.music_playing = not self.music_playing
        
        if self.music_playing:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
    
    def stop_music(self):
        """Dừng hoàn toàn nhạc khi thoát game"""
        try:
            if pygame.mixer.get_init():  # Kiểm tra xem mixer đã được khởi tạo chưa
                pygame.mixer.music.stop()
        except Exception:
            pass  # Bỏ qua lỗi nếu mixer không còn tồn tại
    
    def draw_music_button(self, screen, scroll_x=0, scroll_y=0):
        """Vẽ nút bật/tắt nhạc"""
        music_button_img = self.music_button_on if self.music_playing else self.music_button_off
        adjusted_pos = (self.music_button_pos[0] - scroll_x, self.music_button_pos[1] - scroll_y)
        screen.blit(music_button_img, adjusted_pos)
    
    def check_music_button_click(self, pos, scroll_x=0, scroll_y=0):
        """Kiểm tra xem đã nhấp vào nút nhạc chưa"""
        adjusted_rect = pygame.Rect(
            self.music_button_pos[0] - scroll_x, 
            self.music_button_pos[1] - scroll_y,
            self.music_button_size[0], 
            self.music_button_size[1]
        )
        if adjusted_rect.collidepoint(pos):
            self.toggle_music()
            return True
        return False