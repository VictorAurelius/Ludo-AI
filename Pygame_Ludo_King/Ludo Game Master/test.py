import pygame
import sys
from pygame.locals import *
from pytmx.util_pygame import load_pygame

# Khởi tạo pygame
pygame.init()

# Kích thước màn hình
winX, winY = 925, 725

# Tạo cửa sổ
win = pygame.display.set_mode((winX, winY))
pygame.display.set_caption("Test Ranking")

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = {
    'Red': (255, 0, 0),
    'Blue': (0, 0, 255),
    'Yellow': (255, 255, 0),
    'Green': (0, 255, 0)
}

# Nút trong bảng xếp hạng
title_ranking_button = pygame.Rect(400, 400, 200, 50)

# Lớp giả lập Player để hiển thị bảng xếp hạng
class MockPlayer:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.pawns_home = 4

# Danh sách người chơi đã hoàn thành
finished_players = [
    MockPlayer("Người chơi 1", "Red"),
    MockPlayer("Người chơi 2", "Blue"),
    MockPlayer("Người chơi 3", "Yellow"),
    MockPlayer("Người chơi 4", "Green")
]

def load_ranking():
    """Tải background cho bảng xếp hạng từ file TMX"""
    # Tạo surface cho bảng xếp hạng với kích thước 400x400
    ranking_surface = pygame.Surface((400, 400))
    
    try:
        # Load map từ file TMX
        ranking_map = load_pygame('mapfinal/ranking.tmx')
        
        # Vẽ từng layer của map lên surface
        for layer in ranking_map.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, gid in layer:
                    tile = ranking_map.get_tile_image_by_gid(gid)
                    if tile:
                        ranking_surface.blit(tile, (x * ranking_map.tilewidth, 
                                                  y * ranking_map.tileheight))
                        
    except Exception as e:
        print(f"Error loading ranking TMX: {e}")
        # Nếu load thất bại thì fill màu trắng
        ranking_surface.fill((255, 255, 255))
        
    return ranking_surface

# Load background cho ranking
bgRanking = load_ranking()

def draw_ranking(win):
    """Vẽ bảng xếp hạng"""
    # Xóa màn hình
    win.fill(WHITE)
    
    # Vẽ background mờ cho toàn màn hình
    s = pygame.Surface((925, 725))
    s.set_alpha(128)
    s.fill((0, 0, 0))
    win.blit(s, (0, 0))
    
    # Vẽ background bảng xếp hạng từ file TMX
    ranking_rect = pygame.Rect(300, 100, 400, 400)
    win.blit(bgRanking, (300, 100))
    pygame.draw.rect(win, BLACK, ranking_rect, 2)  # Vẽ viền đen
    
    # Vẽ tiêu đề
    vn_font = pygame.font.SysFont("segoeui", 36)
    title = vn_font.render("BẢNG XẾP HẠNG", True, BLACK)
    win.blit(title, (400, 120))
    
    # Vẽ danh sách người chơi
    y_pos = 180
    for i, player in enumerate(finished_players, 1):
        color = COLORS[player.color]
        text = vn_font.render(f"Hạng {i}: {player.name}", True, color)
        win.blit(text, (320, y_pos))
        y_pos += 60
    
    # Vẽ nút Tiêu đề
    pygame.draw.rect(win, BLACK, title_ranking_button, 2)
    title_text = vn_font.render("Tiêu đề", True, BLACK)
    win.blit(title_text, (450, 410))
    
    # Cập nhật màn hình
    pygame.display.flip()

# Vòng lặp chính
def main():
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            elif event.type == MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if title_ranking_button.collidepoint(mouse_pos):
                    print("Đã nhấn nút Tiêu đề")
        
        # Vẽ bảng xếp hạng
        draw_ranking(win)
        
        # Giới hạn FPS
        clock.tick(30)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()