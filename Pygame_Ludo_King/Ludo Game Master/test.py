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
    MockPlayer("Van Kiet", "Red"),
    MockPlayer("Tai Nhat", "Blue"),
    MockPlayer("Minh Quyet", "Yellow"),
    MockPlayer("Van Tai", "Green")
]

def load_ranking():
    """Tải background cho bảng xếp hạng từ file TMX"""
    try:
        # Load map từ file TMX
        ranking_map = load_pygame('mapfinal/ranking.tmx')
        
        # Lấy kích thước từ file TMX (số ô * kích thước mỗi ô)
        width = ranking_map.width * ranking_map.tilewidth
        height = ranking_map.height * ranking_map.tileheight
        
        # Tạo surface với kích thước lấy từ file TMX
        ranking_surface = pygame.Surface((width, height))
        
        # Vẽ từng layer của map lên surface
        for layer in ranking_map.visible_layers:
            if hasattr(layer, "data"):
                for x, y, gid in layer:
                    tile = ranking_map.get_tile_image_by_gid(gid)
                    if tile:
                        ranking_surface.blit(tile, (x * ranking_map.tilewidth, 
                                                  y * ranking_map.tileheight))
                        
    except Exception as e:
        print(f"Error loading ranking TMX: {e}")
        # Nếu load thất bại thì fill màu trắng và sử dụng kích thước mặc định
        width, height = 400, 400
        ranking_surface = pygame.Surface((width, height))
        ranking_surface.fill((255, 255, 255))
        
    return ranking_surface, (width, height)

# Load background cho ranking
bgRanking, (ranking_width, ranking_height) = load_ranking()

def draw_ranking(win):
    """Vẽ bảng xếp hạng"""
    # Xóa màn hình
    win.fill(WHITE)
    
    # Vẽ background mờ cho toàn màn hình
    s = pygame.Surface((925, 725))
    s.set_alpha(128)
    s.fill((0, 0, 0))
    win.blit(s, (0, 0))
    
    # Tính toán vị trí để đặt bảng xếp hạng ở giữa màn hình
    ranking_x = (winX - ranking_width) // 2
    ranking_y = (winY - ranking_height) // 2
    
    # Vẽ background bảng xếp hạng từ file TMX với kích thước chính xác
    ranking_rect = pygame.Rect(ranking_x, ranking_y, ranking_width, ranking_height)
    win.blit(bgRanking, (ranking_x, ranking_y))
    pygame.draw.rect(win, BLACK, ranking_rect, 2)  # Vẽ viền đen
    
    # Vẽ tiêu đề - căn giữa theo chiều ngang của bảng xếp hạng
    title_font = pygame.font.SysFont("segoeui", 36, bold=True)
    title = title_font.render("RANKING", True, BLACK)
    title_x = ranking_x + (ranking_width - title.get_width()) // 2
    win.blit(title, (title_x, ranking_y + 50))
    
    # Vẽ danh sách người chơi - căn đều trong bảng
    vn_font = pygame.font.SysFont("segoeui", 28, bold=True)
    y_spacing = (ranking_height - 125) // 5 # Khoảng cách giữa các dòng
    y_pos = ranking_y + 185
    for i, player in enumerate(finished_players, 1):
        color = COLORS[player.color]
        text = vn_font.render(f"No {i}: {player.name}", True, color)
        text_x = ranking_x + 130
        win.blit(text, (text_x, y_pos))
        y_pos += y_spacing
    
    # Vẽ nút Quit Game với vị trí text có thể tùy chỉnh
    # Các tham số có thể tùy chỉnh
    button_padding_x = 30  # Padding ngang từ text tới viền button
    button_padding_y = 15  # Padding dọc từ text tới viền button
    
    # Vị trí text tương đối so với ranking panel có thể tùy chỉnh dễ dàng
    text_rel_x = 0.5  # Vị trí X của text (0.5 = giữa ranking)
    text_rel_y = 0.92 # Vị trí Y của text (1.0 = dưới cùng của ranking)
    
    # Render text
    title_text = vn_font.render("Quit", True, BLACK)
    text_width = title_text.get_width()
    text_height = title_text.get_height()
    
    # Tính toán vị trí tuyệt đối của text
    text_x = ranking_x + (ranking_width * text_rel_x) - (text_width // 2)
    text_y = ranking_y + (ranking_height * text_rel_y) - (text_height // 2)
    
    # Tạo button dựa trên vị trí text và padding
    global title_ranking_button
    title_ranking_button = pygame.Rect(
        text_x - button_padding_x,
        text_y - button_padding_y,
        text_width + (button_padding_x * 2),
        text_height + (button_padding_y * 2)
    )
    
    # Vẽ text
    win.blit(title_text, (text_x, text_y))
    
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