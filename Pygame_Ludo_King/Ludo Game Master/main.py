from pygame.locals import *
from Pawns import *
from Players import *
from States import *
from Stars import stars
import pygame
import random
import pytmx
import os
from main_board import MainBoard
from pytmx.util_pygame import load_pygame
from alert_manager import AlertManager
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
# Pygame Initialized
pygame.init()

alert_manager = AlertManager()

# window dimension coordinates in pixels
winX = 925  # Tăng chiều rộng để thêm sidebar
winY = 725
sidebarX = 200  # Chiều rộng của sidebar

# set and initialize the pygame display
win = pygame.display.set_mode((winX, winY))

# Load dice images
dice_images = [
    pygame.image.load(resource_path('img/1_block.png')),
    pygame.image.load(resource_path('img/2_block.png')),
    pygame.image.load(resource_path('img/3_block.png')),
    pygame.image.load(resource_path('img/4_block.png')),
    pygame.image.load(resource_path('img/5_block.png')),
    pygame.image.load(resource_path('img/6_block.png'))
]
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
COLORS = {
    'Red': (255, 0, 0),
    'Blue': (0, 0, 255),
    'Yellow': (255, 255, 0),
    'Green': (128, 0, 128)
}

# Font
font = pygame.font.Font(None, 32)

# Các nút trong sidebar
roll_button = pygame.Rect(735, 290, 180, 50)
title_button = pygame.Rect(745, 10, 160, 40)
title_ranking_button = pygame.Rect(400, 400, 200, 50)

# Global declarations
global roll_button_enabled, showing_dialog, showing_ranking, yes_button, no_button

# Game state variables
showing_dialog = False
showing_ranking = False  # Biến kiểm tra đang hiện dialog
roll_button_enabled = True  # Trạng thái nút tung xúc xắc
can_move = False  # Biến kiểm tra có thể di chuyển không
dice_animating = False  # Biến kiểm tra xúc xắc đang animating
yes_button = pygame.Rect(410, 260, 60, 30)  # Nút "Có"
no_button = pygame.Rect(530, 260, 90, 30)  # Nút "Không"
current_dice1 = dice_images[0]  # Mặt xúc xắc 1
current_dice2 = dice_images[0]  # Mặt xúc xắc 2
dice_num1 = 1  # Số hiện tại trên xúc xắc 1
dice_num2 = 1  # Số hiện tại trên xúc xắc 2
last_turn_change_time = 0  # Thời điểm chuyển lượt cuối cùng
TURN_CHANGE_DELAY = 500 
# Biến lưu thông báo hiệu ứng sao và alert
star_effect_message = ""
star_effect_time = 0
alert_time = 0

# Thêm biến toàn cục để xử lý doubles và roll_again
DOUBLES_DELAY = 1500  # Thời gian chờ (ms) khi tung được xúc xắc đôi
last_doubles_time = 0  # Thời điểm tung được xúc xắc đôi
doubles_waiting = False  # Đang trong trạng thái chờ sau khi tung được đôi
got_roll_again_ai = False  # AI nhận được hiệu ứng roll_again

# Biến để lưu thứ tự về đích
finished_players = []

# Game constants
BOARD_SIZE = 800
DICE_SIZE = 50
PAWN_SIZE = 20

# AI decision weights
AI_DECISION_WEIGHTS = {
    'finish': 1000,    # Weight for finishing a pawn
    'capture': 80,     # Weight for capturing an opponent
    'safe_spot': 50,   # Weight for reaching a safe spot
    'start': 40,       # Weight for getting a pawn out of home
    'progress': 30,    # Weight for general forward progress
    'block': 25        # Weight for creating blockades
}

def draw_alert(win, text):
    # Tạo surface bán trong suốt cho background
    alert_bg = pygame.Surface((400, 50))
    alert_bg.set_alpha(200)
    alert_bg.fill((0, 0, 0))
    
    # Vẽ background ở giữa màn hình
    x = (winX - 400) // 2
    y = 50
    win.blit(alert_bg, (x, y))
    
    # Vẽ text
    vn_font = pygame.font.SysFont("segoeui", 28)
    text_surface = vn_font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(winX // 2, y + 25))
    win.blit(text_surface, text_rect)

def load_dialog():
    """Tải background cho dialog từ file TMX"""
    # Tạo surface cho dialog với kích thước 230x100
    dialog_surface = pygame.Surface((230, 100))
    
    try:
        # Load map từ file TMX
        dialog_map = load_pygame(resource_path('mapfinal/slide_bar.tmx'))
        
        # Vẽ từng layer của map lên surface
        for layer in dialog_map.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, gid in layer:
                    tile = dialog_map.get_tile_image_by_gid(gid)
                    if tile:
                        dialog_surface.blit(tile, (x * dialog_map.tilewidth, 
                                                 y * dialog_map.tileheight))
    except Exception as e:
        print(f"Error loading dialog TMX: {e}")
        # Nếu load thất bại thì fill màu trắng
        dialog_surface.fill((255, 255, 255))
        
    return dialog_surface

def load_ranking():
    """Tải background cho bảng xếp hạng từ file TMX"""
    try:
        # Load map từ file TMX
        ranking_map = load_pygame(resource_path('mapfinal/ranking.tmx'))
        
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

def load_sidebar():
    """Tải background sidebar từ file TMX"""
    # Tạo surface cho sidebar với kích thước 200x725
    sidebar_surface = pygame.Surface((200, 725))
    
    try:
        # Load map từ file TMX
        sidebar_map = load_pygame(resource_path('mapfinal/slide_bar.tmx'))
        
        # Vẽ từng layer của map lên surface
        for layer in sidebar_map.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, gid in layer:
                    tile = sidebar_map.get_tile_image_by_gid(gid)
                    if tile:
                        sidebar_surface.blit(tile, (x * sidebar_map.tilewidth, 
                                                  y * sidebar_map.tileheight))
                        
    except Exception as e:
        print(f"Error loading sidebar TMX: {e}")
        # Nếu load thất bại thì fill màu trắng
        sidebar_surface.fill((255, 255, 255))
        
    return sidebar_surface

#load the board background
def load_map():
    # Tạo surface mới có kích thước bằng với cửa sổ game
    map_surface = pygame.Surface((725, 725))
    
    # Load map từ file TMX 
    game_map = load_pygame(resource_path('mapfinal/mapludo.tmx'))
    
    # Vẽ từng layer của map lên surface mới
    for layer in game_map.visible_layers:
        for x, y, gid in layer:
            tile = game_map.get_tile_image_by_gid(gid)
            if tile:
                map_surface.blit(tile, (x * game_map.tilewidth, y * game_map.tileheight))
    
    return map_surface  # Trả về surface đã vẽ map

def load_roll_button():
    """Tải background cho nút roll từ file hình ảnh"""
    try:
        # Tải trực tiếp hình ảnh từ đường dẫn trong TSX
        button_img = pygame.image.load(resource_path('assets_ver1/TinySwords/UI/Ribbons/Ribbon_Yellow_3Slides.png'))
        return button_img
    except Exception as e:
        print(f"Error loading roll button image: {e}")
        # Nếu load thất bại thì tạo surface màu vàng nhạt
        button_surface = pygame.Surface((120, 40))
        button_surface.fill((255, 255, 204))
        return button_surface
roll_button_bg = None

def load_quit_dialog():
    """Tải background cho dialog từ file quit_game.tmx"""
    try:
        # Load map từ file TMX
        quit_map = load_pygame(resource_path('mapfinal/quit_game.tmx'))
        
        # Lấy kích thước từ file TMX (số ô * kích thước mỗi ô)
        width = quit_map.width * quit_map.tilewidth
        height = quit_map.height * quit_map.tileheight
        
        # Tạo surface với kích thước lấy từ file TMX
        dialog_surface = pygame.Surface((width, height))
        
        # Vẽ từng layer của map lên surface
        for layer in quit_map.visible_layers:
            if hasattr(layer, "data"):
                for x, y, gid in layer:
                    tile = quit_map.get_tile_image_by_gid(gid)
                    if tile:
                        dialog_surface.blit(tile, (x * quit_map.tilewidth, 
                                                 y * quit_map.tileheight))
    except Exception as e:
        print(f"Error loading quit_game.tmx: {e}")
        # Nếu load thất bại thì fill màu trắng và sử dụng kích thước mặc định
        dialog_surface = pygame.Surface((300, 150))
        dialog_surface.fill((255, 255, 255))
        
    return dialog_surface, (width, height)

# Khởi tạo bàn cờ từ Tiled
bgBoard = load_map()
bgSidebar = load_sidebar()
bgRanking, (ranking_width, ranking_height) = load_ranking()
bgDialog = load_dialog()


def draw_dialog(win):
    # Load the quit_game.tmx file
    bgQuitDialog, (dialog_width, dialog_height) = load_quit_dialog()
    
    # Vẽ background mờ cho toàn màn hình
    s = pygame.Surface((925, 725))
    s.set_alpha(128)
    s.fill((0, 0, 0))
    win.blit(s, (0, 0))
    
    # Tính toán vị trí để đặt dialog ở giữa màn hình
    dialog_x = (925 - dialog_width) // 2
    dialog_y = (725 - dialog_height) // 2
    
    # Vẽ dialog box với kích thước lấy từ TMX file
    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    win.blit(bgQuitDialog, (dialog_x, dialog_y))
    pygame.draw.rect(win, BLACK, dialog_rect, 2)
    
    # Vẽ text
    vn_font = pygame.font.SysFont("segoeui", 24)
    text = vn_font.render(u"Do you want to exit the game?", True, BLACK)

    # Tính toán vị trí để đặt text căn giữa dialog
    text_x = dialog_x + (dialog_width - text.get_width()) // 2
    text_y = dialog_y + 50
    
    win.blit(text, (text_x, text_y))

    # ========== CUSTOMIZABLE BUTTON POSITIONS ==========
    # Padding cho buttons
    padding_x = 20
    padding_y = 10
    
    # Render text buttons
    yes_text = vn_font.render(u"Yes", True, BLACK)
    no_text = vn_font.render(u"No", True, BLACK)
    
    # Kích thước text
    yes_text_width = yes_text.get_width()
    yes_text_height = yes_text.get_height()
    no_text_width = no_text.get_width()
    no_text_height = no_text.get_height()
    
    # Tùy chỉnh vị trí relative to dialog
    # Có thể thay đổi các giá trị này để di chuyển buttons
    yes_rel_x = 0.25  # 30% từ bên trái của dialog
    no_rel_x = 0.75   # 70% từ bên trái của dialog
    buttons_rel_y = 0.77  # 75% từ bên trên của dialog
    
    # Tính toán vị trí tuyệt đối cho text
    yes_text_x = dialog_x + int(dialog_width * yes_rel_x) - (yes_text_width // 2)
    no_text_x = dialog_x + int(dialog_width * no_rel_x) - (no_text_width // 2)
    buttons_y = dialog_y + int(dialog_height * buttons_rel_y) - (yes_text_height // 2)
    
    # Tạo button rects dựa trên vị trí và kích thước text + padding
    global yes_button, no_button
    yes_button = pygame.Rect(
        yes_text_x - padding_x, 
        buttons_y - padding_y,
        yes_text_width + (padding_x * 2),
        yes_text_height + (padding_y * 2)
    )
    
    no_button = pygame.Rect(
        no_text_x - padding_x, 
        buttons_y - padding_y,
        no_text_width + (padding_x * 2),
        no_text_height + (padding_y * 2)
    )
    
    
    # Vẽ text ở vị trí đã tính toán
    win.blit(yes_text, (yes_text_x, buttons_y))
    win.blit(no_text, (no_text_x, buttons_y))

def draw_sidebar(win, Statekpr):
    global star_effect_message, star_effect_time, dice_animating
    
    win.blit(bgSidebar, (725, 0))
    
    # Font cho tiếng Việt
    vn_font = pygame.font.SysFont("segoeui", 20)
    
    # Thay thế đoạn code vẽ nút tiêu đề bằng:
    # Vẽ nút Tiêu đề với kích thước dựa trên text
    # Vẽ nút Tiêu đề với kích thước dựa trên text
    bold_font = pygame.font.SysFont("segoeui", 20, bold=True)  # Tạo font chữ đậm
    title_text = bold_font.render(u"Back", True, BLACK)
    text_rect = title_text.get_rect()
    # Thêm padding 20px cho chiều rộng và 10px cho chiều cao
    title_button = pygame.Rect(795, 625, text_rect.width + 20, text_rect.height + 10)
    # Cập nhật biến title_button toàn cục để sự kiện click hoạt động đúng
    globals()['title_button'] = title_button

    # Căn giữa text trong button
    text_x = title_button.centerx - text_rect.width // 2
    text_y = title_button.centery - text_rect.height // 2
    win.blit(title_text, (text_x, text_y))    
    
    # Tạo font chữ đậm với font segoe ui
    bold_font = pygame.font.SysFont("segoeui", 20, bold=True)
    # Chọn màu text dựa trên trạng thái của nút
    if not roll_button_enabled or dice_animating:
        text_color = GRAY  # Màu xám khi vô hiệu hóa
    else:
        text_color = BLACK  # Màu đen khi hoạt động bình thường

    roll_text = bold_font.render("ROLL", True, text_color)
    
    # Tính toán kích thước và vị trí cho button dựa trên text
    text_rect = roll_text.get_rect()
    padding_x = 40  # Padding ngang
    padding_y = 20  # Padding dọc
    button_width = text_rect.width + padding_x
    button_height = text_rect.height + padding_y
    
    # Cập nhật vị trí button để căn giữa trong sidebar
    button_x = 730 + ((200 - button_width) // 2)  # Căn giữa trong sidebar
    button_y = 220  # Giữ nguyên vị trí y
    
    # Cập nhật Rect của roll_button
    roll_button = pygame.Rect(button_x, button_y, button_width, button_height)
    globals()['roll_button'] = roll_button  # Cập nhật biến toàn cục
    
    # Vẽ background của button
    try:
        # Chỉnh kích thước background phù hợp với kích thước button
        scaled_bg = pygame.transform.scale(roll_button_bg, (button_width, button_height))
        
        # Nếu nút bị vô hiệu hóa hoặc đang animation, tạo hiệu ứng tối màu
        if not roll_button_enabled or dice_animating:
            # Tạo bản sao của hình ảnh để làm tối
            darkened_bg = scaled_bg.copy()
            
            # Lặp qua từng pixel để chỉ làm tối những phần không trong suốt
            for x in range(button_width):
                for y in range(button_height):
                    color = darkened_bg.get_at((x, y))
                    # Nếu pixel không trong suốt (alpha > 0), giảm độ sáng của nó
                    if color[3] > 0:  # Kiểm tra giá trị alpha
                        # Giảm độ sáng bằng cách nhân với 0.7 (có thể điều chỉnh)
                        r, g, b, a = color
                        darkened_color = (int(r * 0.7), int(g * 0.7), int(b * 0.7), a)
                        darkened_bg.set_at((x, y), darkened_color)
            
            # Vẽ phiên bản đã làm tối
            win.blit(darkened_bg, (button_x, button_y))
        else:
            # Vẽ bình thường nếu nút đang được kích hoạt
            win.blit(scaled_bg, (button_x, button_y))
    except (TypeError, AttributeError):
        # Nếu không có background hoặc lỗi, vẽ button mặc định
        if not roll_button_enabled or dice_animating:
            # Vẽ nút màu xám đậm khi vô hiệu hóa
            pygame.draw.rect(win, (160, 160, 140), roll_button)  # Màu xám tối hơn
        else:
            # Vẽ nút màu vàng nhạt khi kích hoạt
            pygame.draw.rect(win, (255, 255, 204), roll_button)  # Màu vàng nhạt
        
        # Vẽ viền đen
        pygame.draw.rect(win, BLACK, roll_button, 2)
    
    # Tính toán vị trí để căn giữa text trong button mới
    text_x = roll_button.centerx - text_rect.width // 2
    text_y = roll_button.centery - text_rect.height // 2 - 5
    
    # Vẽ text đã được căn giữa
    win.blit(roll_text, (text_x, text_y))

    
    # Hiển thị 2 hình xúc xắc
    scaled_dice1 = pygame.transform.scale(current_dice1, (60, 60))
    scaled_dice2 = pygame.transform.scale(current_dice2, (60, 60))
    win.blit(scaled_dice1, (765, 80))
    win.blit(scaled_dice2, (830, 80))
    
    # Hiển thị tổng hai xúc xắc CHỈ KHI ANIMATION KẾT THÚC
    if not dice_animating:  # Chỉ hiển thị khi animation kết thúc
        total = dice_num1 + dice_num2
        # Tạo font chữ đậm với font segoe ui và cỡ chữ 24
        bold_font = pygame.font.SysFont("segoeui", 16, bold=True)
        total_text = bold_font.render(f"SUM POINT: {total}", True, (0, 0, 139))  # Màu xanh navy
        # Tính toán vị trí để căn giữa text
        text_rect = total_text.get_rect()
        text_x = 825 - text_rect.width // 2
        text_y = 185
        win.blit(total_text, (text_x, text_y))
    
    # Hiển thị thông tin quân cờ của từng người chơi
    y_pos = 310
    for player in Statekpr.players:
        
        # Xác định màu khung
        frame_color = COLORS[player.color]
        
        is_current_player = (Statekpr.display_player == player)
        
        # Tạo hình chữ nhật cho khung
        player_frame = pygame.Rect(755, y_pos + 20, 140, 45)
        
        # Chỉ vẽ cạnh dưới của khung
        if is_current_player:  # Loại bỏ điều kiện not dice_animating
            # Vẽ đường dưới đậm hơn cho người chơi hiện tại
            pygame.draw.line(win, frame_color, 
                            (player_frame.left, player_frame.bottom), 
                            (player_frame.right, player_frame.bottom), 
                            6)  # Đường dày 6px
        else:
            # Vẽ đường dưới mỏng cho người chơi khác
            pygame.draw.line(win, frame_color, 
                            (player_frame.left, player_frame.bottom), 
                            (player_frame.right, player_frame.bottom), 
                            1)  # Đường mỏng 1px
        
        # Hiển thị số lần bị đá
        bold_font = pygame.font.SysFont("segoeui", 20, bold=True)
        text = bold_font.render(f"DIE: {player.times_kicked}", True, (255, 0, 0))
        win.blit(text, (810, y_pos + 25))
        
        # Thêm khoảng cách giữa các khung
        y_pos += 75
    
    # Hiển thị thông báo hiệu ứng sao
    if star_effect_message and pygame.time.get_ticks() - star_effect_time < 2000:
        text = vn_font.render(star_effect_message, True, (255, 215, 0))  # Màu vàng
        # Đặt thông báo ở dưới thông tin người chơi
        win.blit(text, (735, y_pos + 20))

def draw_sidebar_with_scroll(win, Statekpr):
    """Vẽ sidebar với vị trí đã được điều chỉnh theo cuộn"""
    global star_effect_message, star_effect_time, dice_animating
    
    # Vẽ background sidebar
    blit_with_scroll(win, bgSidebar, (725, 0))
    
    # Font cho tiếng Việt
    vn_font = pygame.font.SysFont("segoeui", 20)
    
    # Vẽ nút Tiêu đề với kích thước dựa trên text
    bold_font = pygame.font.SysFont("segoeui", 20, bold=True)
    title_text = bold_font.render(u"Back", True, BLACK)
    text_rect = title_text.get_rect()
    
    # Thêm padding và tính toán vị trí có tính đến cuộn
    title_button_adjusted = pygame.Rect(
        795 - scroll_x, 625 - scroll_y, 
        text_rect.width + 20, text_rect.height + 10
    )
    
    # Cập nhật biến title_button toàn cục (không áp dụng cuộn)
    globals()['title_button'] = pygame.Rect(
        795, 625, 
        text_rect.width + 20, text_rect.height + 10
    )

    # Căn giữa text trong button
    text_x = title_button_adjusted.centerx - text_rect.width // 2
    text_y = title_button_adjusted.centery - text_rect.height // 2
    win.blit(title_text, (text_x, text_y))
    
    
    # Tính toán vị trí roll_button có tính đến cuộn
    bold_font = pygame.font.SysFont("segoeui", 18, bold=True)
    if not roll_button_enabled or dice_animating:
        text_color = GRAY
    else:
        text_color = BLACK

    roll_text = bold_font.render("ROLL", True, text_color)
    
    text_rect = roll_text.get_rect()
    padding_x = 40
    padding_y = 20
    button_width = text_rect.width + padding_x
    button_height = text_rect.height + padding_y
    
    button_x = 730 + ((200 - button_width) // 2)
    button_y = 220
    
    # Cập nhật roll_button không có cuộn (cho sự kiện click)
    roll_button = pygame.Rect(button_x, button_y, button_width, button_height)
    globals()['roll_button'] = roll_button
    
    # Tính toán vị trí đã cuộn cho việc hiển thị
    button_x_adjusted = button_x - scroll_x
    button_y_adjusted = button_y - scroll_y
    
    # Vẽ nút với vị trí đã cuộn
    try:
        scaled_bg = pygame.transform.scale(roll_button_bg, (button_width, button_height))
        if not roll_button_enabled or dice_animating:
            darkened_bg = scaled_bg.copy()
            for x in range(button_width):
                for y in range(button_height):
                    color = darkened_bg.get_at((x, y))
                    if color[3] > 0:
                        r, g, b, a = color
                        darkened_color = (int(r * 0.7), int(g * 0.7), int(b * 0.7), a)
                        darkened_bg.set_at((x, y), darkened_color)
            win.blit(darkened_bg, (button_x_adjusted, button_y_adjusted))
        else:
            win.blit(scaled_bg, (button_x_adjusted, button_y_adjusted))
    except (TypeError, AttributeError):
        if not roll_button_enabled or dice_animating:
            pygame.draw.rect(win, (160, 160, 140), pygame.Rect(button_x_adjusted, button_y_adjusted, button_width, button_height))
        else:
            pygame.draw.rect(win, (255, 255, 204), pygame.Rect(button_x_adjusted, button_y_adjusted, button_width, button_height))
        pygame.draw.rect(win, BLACK, pygame.Rect(button_x_adjusted, button_y_adjusted, button_width, button_height), 2)
    
    # Tính toán vị trí text với cuộn
    text_x = button_x_adjusted + (button_width - text_rect.width) // 2
    text_y = button_y_adjusted + (button_height - text_rect.height) // 2 - 5
    win.blit(roll_text, (text_x, text_y))

    # Hiển thị xúc xắc với vị trí cuộn
    scaled_dice1 = pygame.transform.scale(current_dice1, (60, 60))
    scaled_dice2 = pygame.transform.scale(current_dice2, (60, 60))
    win.blit(scaled_dice1, (765 - scroll_x, 80 - scroll_y))
    win.blit(scaled_dice2, (830 - scroll_x, 80 - scroll_y))
    
    # Hiển thị tổng hai xúc xắc CHỈ KHI ANIMATION KẾT THÚC
    if not dice_animating:  # Chỉ hiển thị khi animation kết thúc
        total = dice_num1 + dice_num2
        # Tạo font chữ đậm với font segoe ui và cỡ chữ 24
        bold_font = pygame.font.SysFont("segoeui", 16, bold=True)
        total_text = bold_font.render(f"SUM POINT: {total}", True, (0, 0, 139))  # Màu xanh navy
        # Tính toán vị trí để căn giữa text
        text_rect = total_text.get_rect()
        text_x = 825 - text_rect.width // 2
        text_y = 185
        win.blit(total_text, (text_x - scroll_x, text_y - scroll_y))
    
    # Hiển thị thông tin quân cờ của từng người chơi
    y_pos = 310
    for player in Statekpr.players:
        
        # Xác định màu khung
        frame_color = COLORS[player.color]
        
        is_current_player = (Statekpr.display_player == player)
        
        # Tạo hình chữ nhật cho khung
        player_frame = pygame.Rect(755 - scroll_x, y_pos - scroll_y + 20, 140, 45)
        
        # Chỉ vẽ cạnh dưới của khung
        if is_current_player:  # Loại bỏ điều kiện not dice_animating
            # Vẽ đường dưới đậm hơn cho người chơi hiện tại
            pygame.draw.line(win, frame_color, 
                            (player_frame.left, player_frame.bottom), 
                            (player_frame.right, player_frame.bottom), 
                            6)  # Đường dày 6px
        else:
            # Vẽ đường dưới mỏng cho người chơi khác
            pygame.draw.line(win, frame_color, 
                            (player_frame.left, player_frame.bottom), 
                            (player_frame.right, player_frame.bottom), 
                            1)  # Đường mỏng 1px
        
        # Hiển thị số lần bị đá
        bold_font = pygame.font.SysFont("segoeui", 20, bold=True)
        text = bold_font.render(f"DIE: {player.times_kicked}", True, (255, 0, 0))
        win.blit(text, (810 - scroll_x, y_pos + 25 - scroll_y))
        
        # Thêm khoảng cách giữa các khung
        y_pos += 75
    
    # Hiển thị thông báo hiệu ứng sao
    if star_effect_message and pygame.time.get_ticks() - star_effect_time < 2000:
        text = vn_font.render(star_effect_message, True, (255, 215, 0))  # Màu vàng
        # Đặt thông báo ở dưới thông tin người chơi
        win.blit(text, (735 - scroll_x, y_pos + 20 - scroll_y))

def draw_ranking(win):
    """Vẽ bảng xếp hạng"""
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
    y_spacing = (ranking_height - 125) // 5  # Khoảng cách giữa các dòng
    y_pos = ranking_y + 185
    for i, player in enumerate(finished_players, 1):
        color = COLORS[player.color]
        text = vn_font.render(f"NO {i}: {player.name}", True, color)
        text_x = ranking_x + 130
        win.blit(text, (text_x, y_pos))
        y_pos += y_spacing
    
    # Vẽ nút Quit Game với vị trí text có thể tùy chỉnh
    # Các tham số có thể tùy chỉnh
    button_padding_x = 30  # Padding ngang từ text tới viền button
    button_padding_y = 15  # Padding dọc từ text tới viền button
    
    # Vị trí text tương đối so với ranking panel có thể tùy chỉnh dễ dàng
    text_rel_x = 0.5  # Vị trí X của text (0.5 = giữa ranking)
    text_rel_y = 0.92  # Vị trí Y của text (1.0 = dưới cùng của ranking)
    
    # Render text
    global title_ranking_button
    title_text = vn_font.render("QUIT", False, BLACK)
    text_width = title_text.get_width()
    text_height = title_text.get_height()
    
    # Tính toán vị trí tuyệt đối của text
    text_x = ranking_x + (ranking_width * text_rel_x) - (text_width // 2)
    text_y = ranking_y + (ranking_height * text_rel_y) - (text_height // 2)
    
    # Tạo button dựa trên vị trí text và padding
    title_ranking_button = pygame.Rect(
        text_x - button_padding_x,
        text_y - button_padding_y,
        text_width + (button_padding_x * 2),
        text_height + (button_padding_y * 2)
    )
    
    # Vẽ text
    win.blit(title_text, (text_x, text_y))
    
# MainFunction
# Animation constants
DICE_ANIMATION_FRAMES = 15  # Number of frames for animation
DICE_ANIMATION_SPEED = 50   # Milliseconds between frames

# Biến toàn cục cho việc cuộn màn hình
scroll_x = 0  # Vị trí cuộn theo chiều ngang
scroll_y = 0  # Vị trí cuộn theo chiều dọc
SCROLL_SPEED = 15  # Tốc độ cuộn mỗi lần
is_scrolling = False  # Đang kéo thả để cuộn hay không
scroll_start_pos = (0, 0)  # Vị trí bắt đầu kéo

def update_scroll_limits():
    """Cập nhật giới hạn cuộn dựa trên kích thước cửa sổ và màn hình"""
    global scroll_x, scroll_y
    
    # Lấy thông tin kích thước màn hình
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h
    
    # Tính toán giới hạn cuộn
    max_scroll_x = max(0, winX - screen_width + 200)  # +50 là đệm
    max_scroll_y = max(0, winY - screen_height + 200)  # +50 là đệm
    
    # Giới hạn vị trí cuộn trong phạm vi cho phép
    scroll_x = max(0, min(scroll_x, max_scroll_x))
    scroll_y = max(0, min(scroll_y, max_scroll_y))
    
    return max_scroll_x > 0 or max_scroll_y > 0  # Trả về True nếu cần cuộn

def blit_with_scroll(surface, image, position):
    """Vẽ hình ảnh với vị trí đã được điều chỉnh theo cuộn"""
    x, y = position
    surface.blit(image, (x - scroll_x, y - scroll_y))

def get_ai_move(pawns, dice_value, board_state):
    """
    Determine the best move for an AI player.
    Returns the index of the pawn to move, or None if no valid moves.
    """
    best_score = -float('inf')
    best_move = None
    
    # Calculate game phase (0-1) based on how many pawns are finished
    finished_pawns = sum(1 for pawn in pawns if pawn.finished)
    game_phase = finished_pawns / len(pawns)
    
    # Adjust weights based on game phase
    weights = AI_DECISION_WEIGHTS.copy()
    if game_phase > 0.5:  # Late game
        weights['finish'] *= 1.5
        weights['progress'] *= 1.2
        weights['capture'] *= 0.8
    
    for i, pawn in enumerate(pawns):
        if not pawn.can_move(dice_value):
            continue
            
        future_pos = pawn.get_future_position(dice_value)
        if future_pos is None:
            continue
            
        score = 0
        
        # Basic scoring
        if pawn.will_finish(dice_value):
            score += weights['finish']
        elif can_capture_opponent(future_pos, board_state):
            score += weights['capture']
        elif is_safe_spot(future_pos):
            score += weights['safe_spot']
        elif pawn.current_position == -1 and dice_value == 6:
            score += weights['start']
            
        # Progress scoring with distance consideration
        progress = (future_pos - pawn.current_position) / 100
        if game_phase > 0.5:  # Late game: prefer moves closer to finish
            remaining_distance = 57 - future_pos if future_pos <= 57 else 0
            progress *= (1 + (1 - remaining_distance/57))
        score += weights['progress'] * progress
        
        # Strategic positioning
        if not is_safe_spot(future_pos):
            # Check if move could be captured in next turn
            risk_score = 0
            for player_pawns in board_state.values():
                for other_pawn in player_pawns:
                    if can_reach_position(other_pawn, future_pos, 6):  # Assume worst case (roll of 6)
                        risk_score -= 20  # Penalty for risky position
            score += risk_score
            
        # Bonus for creating blockades with friendly pawns
        for friendly_pawn in pawns:
            if friendly_pawn != pawn and not friendly_pawn.finished:
                if abs(friendly_pawn.current_position - future_pos) <= 1:
                    score += weights['block']
        
        if score > best_score:
            best_score = score
            best_move = i
            
    return best_move

def can_reach_position(pawn, target_pos, max_moves):
    """Helper function to check if a pawn can reach a position within given moves"""
    current_pos = pawn.current_position
    if current_pos == -1:  # Pawn in home
        return False
    distance = abs(target_pos - current_pos)
    return distance <= max_moves

def main(player_names=None):
    global alert_manager,last_doubles_time, roll_button_bg,doubles_waiting, scroll_x, scroll_y, is_scrolling, scroll_start_pos
    
    # Reset các biến cuộn
    scroll_x = 0
    scroll_y = 0
    is_scrolling = False
    scroll_start_pos = (0, 0)
    
    # Tải background cho nút roll
    roll_button_bg = load_roll_button()
    
    # Lấy thông tin về độ phân giải màn hình
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h
    
    # Tính toán tọa độ để cửa sổ xuất hiện ở giữa màn hình
    pos_x = (screen_width - winX) // 2
    pos_y = (screen_height - winY) // 2
    
    # Đặt vị trí cửa sổ vào giữa màn hình
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{pos_x},{pos_y}"
    
    # Khởi tạo lại Pygame display (quan trọng)
    win = pygame.display.set_mode((winX, winY))
    pygame.display.set_caption("Ludo Game")  # Đặt tiêu đề cho cửa sổ
    
    # Khởi tạo lại Pygame display (quan trọng)
    pygame.display.set_mode((925, 725))
    # Declare globals at the start of function
    global current_dice1, current_dice2, roll_button_enabled, dice_num1, dice_num2, can_move
    global showing_dialog, showing_ranking, dice_animating, display_player, finished_players
    
    # Reset states
    finished_players = []
    showing_dialog = False
    showing_ranking = False
    
    # main Objects
    #Initialize statekeeper object
    Statekpr = Statekeep()
    #Initialize clock
    clock = pygame.time.Clock()
    
    Statekpr.update_display_player()
    
    # Khởi tạo các biến xúc xắc
    current_dice1 = dice_images[0]  # Mặt xúc xắc 1
    current_dice2 = dice_images[0]  # Mặt xúc xắc 2
    dice_num1 = 1  # Số hiện tại trên xúc xắc 1
    dice_num2 = 1  # Số hiện tại trên xúc xắc 2
    
    # Dice animation variables
    dice_animating = False
    animation_frame = 0
    animation_timer = 0
    final_dice_value1 = 0
    final_dice_value2 = 0
    last_animation_time = 0
    
    # Biến để kiểm tra nếu có quân đang di chuyển
    any_pawn_animating = False
    last_turn_change_time = pygame.time.get_ticks()  # Thêm dòng này
    # Thêm biến để theo dõi thời gian delay cho AI
    AI_MOVE_DELAY = 1000  # 1 giây delay
    last_ai_move_time = 0

    # for each player in the players list
    for i, player in enumerate(Statekpr.players):
        #pass the statekeeper object to the players
        player.set_statekeeper(Statekpr)
        # Gán tên cho các người chơi
        if player_names and i < len(player_names):
            player.name = player_names[i]
            # Initialize AI engine if this is an AI player
            if "[AI]" in player.name:
                player.is_ai = True
                from ai_engine import LudoAI
                player.ai_engine = LudoAI(Statekpr)
    #Set while loop variable
    mainLoop = True
    
    # Kiểm tra va chạm với sao
    got_roll_again = False  # Biến để kiểm tra có được tung lại không
    teleported = False  # Biến để đánh dấu quân vừa được dịch chuyển
    valid_move = False  # Biến để kiểm tra nước đi hợp lệ
    
    teleport_chain_active = False  # Theo dõi nếu đang trong chuỗi teleport
    last_teleport_time = 0  # Thời gian teleport cuối cùng
    
    def check_star_collision(pawn, current_player=None):
        nonlocal got_roll_again, teleported
        for star in stars:
            if star.check_exact_collision(pawn):
                effect = star.apply_effect(pawn, Statekpr)
                if effect == "roll_again":
                    alert_manager.add_alert("Được tung xúc xắc thêm lần nữa!", 3000)
                    # Không chuyển lượt, cho phép tung xúc xắc lại
                    roll_button_enabled = True
                    got_roll_again = True
                    
                elif effect == "teleported":
                    alert_manager.add_alert("Dịch chuyển đến vị trí ngẫu nhiên!", 3000)
                    teleported = True
                    
                    # Thay vì di chuyển ngay lập tức, sử dụng animation teleport
                    old_pos = pawn.rect.center
                    new_pos = pawn.rect.center  # Vị trí mới đã được cập nhật trong apply_effect
                    
                    # Khởi tạo animation teleport
                    pawn.start_teleport(new_pos)
                    
                    # Đánh dấu chuỗi teleport đang hoạt động
                    teleport_chain_active = True
                    last_teleport_time = pygame.time.get_ticks()
                    
                    # Vô hiệu hóa nút tung xúc xắc trong khi animation đang chạy
                    roll_button_enabled = False
                else:  # effect == "died"
                    alert_manager.add_alert("Quân cờ đã về chuồng!", 3000)
                    teleport_chain_active = False
                return True
        return False
    
    #main game loop
    while mainLoop:
        # Vẽ map từ Tiled
        win.blit(bgBoard, (0,0))
        #Set clock Tick
        clock.tick(30)
        #update status keeper with every iteration of the main loop
        Statekpr.update()

        # Xử lý lượt đi của AI
        current_player = Statekpr.display_player
        current_time = pygame.time.get_ticks()
        
        if (current_player and current_player.is_ai and 
            not any_pawn_animating and 
            not dice_animating and 
            roll_button_enabled and 
            current_time - last_turn_change_time >= TURN_CHANGE_DELAY and
            current_time - last_ai_move_time >= AI_MOVE_DELAY):
            
            print(f"AI {current_player.name} đang tung xúc xắc")
            # AI tung xúc xắc
            # AI tung xúc xắc
            dice_animating = True
            animation_frame = 0
            final_dice_value1 = random.randint(0, 5)
            final_dice_value2 = random.randint(0, 5)
            dice_num1 = final_dice_value1 + 1
            dice_num2 = final_dice_value2 + 1
            current_player.dice1 = dice_num1
            current_player.dice2 = dice_num2
            print(f"AI tung được {dice_num1} và {dice_num2}, tổng: {dice_num1 + dice_num2}")
            roll_button_enabled = False
            
            last_animation_time = current_time
            
            # Sau khi tung xúc xắc, AI sẽ thực hiện nước đi
            #valid_move = current_player.Turn()  # Enable AI turn processing
            last_ai_move_time = current_time

        # Kiểm tra nếu AI đang chờ do tung được doubles
        if doubles_waiting and current_player and current_player.is_ai:
            current_time = pygame.time.get_ticks()
            if current_time - last_doubles_time >= DOUBLES_DELAY:
                # Đã đợi đủ thời gian, kích hoạt lại nút tung xúc xắc cho AI
                doubles_waiting = False
                
               

        # Initialize both dice with value 1 at start
        if not dice_animating and current_dice1 is None:
            current_dice1 = dice_images[0]
            current_dice2 = dice_images[0]
        
        # Kiểm tra nếu có quân cờ đang animation
        any_pawn_animating = False
        for player in Statekpr.players:
            player.update_self()
            if player.pawns_home == 4 and player not in finished_players:
                finished_players.append(player)
                message = f"{player.name} đã hoàn thành trò chơi!"
                alert_manager.add_alert(message, 5000)
                print(message)
                if len(finished_players) == len(Statekpr.players):
                    # Game has ended, disable roll button and show ranking
                    roll_button_enabled = False
                    showing_ranking = True
                    print("Hiển thị bảng xếp hạng - tất cả người chơi đã hoàn thành")
            for pawn in player.pawnlist:
                # Cập nhật animation
                pawn.update_animation()
                if pawn.is_dying:
                    pawn.update_animation()
                    any_pawn_animating = True
                # Thêm kiểm tra teleporting
                if pawn.teleporting:
                    pawn.update_animation()
                    any_pawn_animating = True
                # Kiểm tra nếu quân đang di chuyển
                if pawn.is_move:
                    pawn.update_animation()  # Cập nhật vị trí của quân trong animation
                    any_pawn_animating = True
                
                # Cập nhật hiệu ứng phát sáng
                pawn.update_glow()
                    
                if hasattr(pawn, 'just_finished_animation') and pawn.just_finished_animation:
                    # Quân vừa hoàn thành animation, xử lý các hiệu ứng sau di chuyển
                    pawn.just_finished_animation = False
                    pawn_owner = None
                    for pl in Statekpr.players:
                        if pawn in pl.pawnlist:
                            pawn_owner = pl
                            break
                    
                    # Đặt thời gian để kiểm tra chuỗi teleport
                    last_animation_end_time = pygame.time.get_ticks()
                    
                    # Đặt cờ để cho biết đã kiểm tra va chạm với sao
                    star_checked = False
                    chain_continues = False
                                                    
                    got_roll_again = False  # Reset biến
                    teleported = False  # Reset biến
                    
                    # Kiểm tra va chạm với sao ban đầu
                    star_hit = check_star_collision(pawn, pawn_owner)
                    star_checked = True
                    
                    # Nếu vừa teleport và nhận được hiệu ứng teleport mới, đánh dấu chuỗi tiếp tục
                    if teleported:
                        teleport_chain_active = True
                        last_teleport_time = pygame.time.get_ticks()
                        chain_continues = True
                        
                    elif not teleported:
                        teleport_chain_active = False
                    
                    if hasattr(pawn, 'teleporting') and pawn.teleporting == False and pawn.counter > 0:
                        # Kiểm tra va chạm với quân địch
                        new_pos = pawn.rect.center
                        for other_player in Statekpr.players:
                            if other_player != pawn_owner:  # Chỉ kiểm tra với quân của người chơi khác
                                for other_pawn in other_player.pawnlist:
                                    if (other_pawn.rect.center == new_pos and 
                                        other_pawn.counter > 0 and 
                                        not other_pawn.is_dying and 
                                        not hasattr(other_pawn, 'just_moved_out')):
                                        print(f"Quân của {current_player.name} ăn quân của {other_player.name}")
                                        other_pawn.start_death_animation()
                                        other_player.pawns -= 1
                                        other_player.times_kicked += 1
                                        break

                        # Tiếp tục xử lý các hiệu ứng khác và chuyển lượt như cũ
                        if pawn.counter == 96 or pawn.counter == 97 and not pawn.king:
                            print('PawnKing')
                            pawn.counter = 0
                            # Tìm người chơi sở hữu quân này
                            for player in Statekpr.players:
                                if pawn in player.pawnlist:
                                    # Tăng số quân về đích nếu chưa được tăng
                                    if not hasattr(pawn, 'has_reached_finish') or not pawn.has_reached_finish:
                                        player.pawns_home += 1
                                        pawn.has_reached_finish = True
                                        
                                    # Xác định vị trí về đích theo màu
                                    if player.color == "Red":
                                        finish_pos_dict = scale_finish_dict(RED_FINISH_POSITIONS, TILE_SIZE)
                                    elif player.color == "Blue":
                                        finish_pos_dict = scale_finish_dict(BLUE_FINISH_POSITIONS, TILE_SIZE)
                                    elif player.color == "Yellow":
                                        finish_pos_dict = scale_finish_dict(YELLOW_FINISH_POSITIONS, TILE_SIZE)
                                    elif player.color == "Green":
                                        finish_pos_dict = scale_finish_dict(GREEN_FINISH_POSITIONS, TILE_SIZE)
                                    else:
                                        finish_pos_dict = None
                                    
                                    # Nếu có vị trí đích, thiết lập để teleport đến đó
                                    if finish_pos_dict and pawn.number in finish_pos_dict:
                                        pawn.finish_position = finish_pos_dict[pawn.number]
                                        pawn.has_reached_finish = True
                                        pawn.start_teleport(pawn.finish_position)
                                        teleported = True
                                        pawn.activepawn = False
                                        pawn.king = True
                                        
                                        # Kiểm tra nếu người chơi vừa về đích hết và chưa có trong danh sách
                                        if player.pawns_home == 4 and player not in finished_players:
                                            finished_players.append(player)
                                            message = f"{player.name} đã hoàn thành trò chơi!"
                                            alert_manager.add_alert(message, 5000)
                                            print(message)
                                            
                                            # Hiển thị bảng xếp hạng nếu tất cả người chơi đã hoàn thành
                                            if len(finished_players) == len(Statekpr.players):
                                                showing_ranking = True
                                                roll_button_enabled = False
                                                print("Hiển thị bảng xếp hạng - tất cả người chơi đã hoàn thành")
                                                for player in Statekpr.players:
                                                    player.turn = False
                                                    player.active = False
                                    break
                            
                        star_checked = True
                            
                        # Nếu nhận được teleport từ sao, đánh dấu chuỗi tiếp tục
                        if teleported:
                            teleport_chain_active = True
                            last_teleport_time = pygame.time.get_ticks()
                            chain_continues = True
                            
                        if not teleported:
                            teleport_chain_active = False
                        roll_button_enabled = True  # Kích hoạt lại nút tung xúc xắc
                        # Enable lại nút tung xúc xắc và chuyển lượt nếu không có hiệu ứng đặc biệt
                        if not got_roll_again and not teleported:
                            roll_button_enabled = True
                            if valid_move:
                                # Reset trạng thái quân cờ
                                for p in pawn_owner.pawnlist:
                                    p.activepawn = False
                                    p.clickable = False
                            elif teleported:
                                roll_button_enabled = False  # Đợi animation teleport hoàn thành
                            
                        # Nếu đã kiểm tra va chạm với sao và không có chuỗi teleport tiếp tục
                        if star_checked and not chain_continues:
                            # CHỈ chuyển lượt nếu không còn trong chuỗi teleport và không được tung lại xúc xắc
                            if not teleport_chain_active and valid_move and not got_roll_again:
                                # Reset trạng thái quân cờ
                                for p in pawn_owner.pawnlist:
                                    p.activepawn = False
                                    p.clickable = False
                                
                                # Kích hoạt nút tung xúc xắc và chuyển lượt
                                roll_button_enabled = True
                                if not got_roll_again:
                                    Statekpr.find_next_valid_player()
                                    Statekpr.update_display_player()
                                    last_turn_change_time = pygame.time.get_ticks()
                            
                        # Xóa trạng thái just_moved_out nếu có và đã hoàn thành mọi kiểm tra
                        if hasattr(pawn, 'just_moved_out'):
                            delattr(pawn, 'just_moved_out')

        
        alert_manager.update()
        
        # Update dice animation
        if dice_animating:
            current_time = pygame.time.get_ticks()
            if current_time - last_animation_time >= DICE_ANIMATION_SPEED:
                animation_frame += 1
                last_animation_time = current_time
                
                if animation_frame < DICE_ANIMATION_FRAMES:
                    # Show random dice faces during animation
                    random_face1 = random.randint(0, 5)
                    random_face2 = random.randint(0, 5)
                    current_dice1 = dice_images[random_face1]
                    current_dice2 = dice_images[random_face2]
                else:
                    # Animation complete - show final values
                    current_dice1 = dice_images[final_dice_value1]
                    current_dice2 = dice_images[final_dice_value2]
                    dice_animating = False
                    
                    # Kiểm tra có thể di chuyển không
                    can_move = False
                    dice_sum = dice_num1 + dice_num2
                    
                    # Xác định người chơi hiện tại dựa trên lượt
                    current_player = None
                    if Statekpr.redTurn:
                        current_player = Statekpr.playerRed
                    elif Statekpr.blueTurn:
                        current_player = Statekpr.playerBlue
                    elif Statekpr.yellowTurn:
                        current_player = Statekpr.playerYellow
                    elif Statekpr.greenTurn:
                        current_player = Statekpr.playerGreen
                    if current_player and current_player.is_ai:
                        print(f"AI {current_player.name} đang thực hiện nước đi")
                        try:
                            # Thực hiện lượt của AI
                            move_success,got_roll_again = current_player.Turn()
                            pygame.time.delay(100)
                            
                            doubles = dice_num1 == dice_num2
                            can_move = move_success
                            any_pawn_animating = False
                            # THÊM DÒNG DEBUG NÀY
                            print(f"AI {current_player.name} - doubles: {doubles}, move_success: {move_success}")
        
                            # Sửa phần xử lý AI rolls doubles
                            if (doubles or got_roll_again) and move_success:
                                message = "tung được xúc xắc đôi" if doubles else "nhận hiệu ứng roll thêm lần"
                                print(f"AI {current_player.name} {message}, được đi tiếp")
                                alert_manager.add_alert(f"{current_player.name} {message}, được đi tiếp!", 2000)
                                
                                # Đánh dấu trạng thái chờ đợi sau khi tung được doubles hoặc roll_again
                                doubles_waiting = True
                                last_doubles_time = pygame.time.get_ticks()
                                
                                # QUAN TRỌNG: KHÔNG đặt roll_button_enabled = False ở đây
                                # roll_button_enabled = False
                                
                                # Thay vào đó, đặt lại biến và giữ lượt cho AI hiện tại
                                roll_button_enabled = True  # Cho phép AI tiếp tục tung xúc xắc
                                # KHÔNG gọi Statekpr.find_next_valid_player() để giữ lượt cho AI
                            else:
                                # Không phải doubles/roll_again hoặc không di chuyển được, chuyển lượt
                                print(f"AI {current_player.name} kết thúc lượt")
                                roll_button_enabled = True
                                Statekpr.find_next_valid_player()
                                Statekpr.update_display_player()
                                last_turn_change_time = pygame.time.get_ticks()
                        except Exception as e:
                            print(f"Lỗi khi xử lý lượt AI: {e}")
                            # Đảm bảo chuyển lượt kể cả khi có lỗi
                            Statekpr.find_next_valid_player()
                            Statekpr.update_display_player()
                            roll_button_enabled = True
                            last_turn_change_time = pygame.time.get_ticks()

                        dice_sum = dice_num1 + dice_num2 
                        # Quan trọng: return ở đây để tránh xử lý thêm
                        continue
                    roll_button_enabled = False  # Disable nút để chờ người chơi chọn quân
                    
                    # Đặt tất cả quân về trạng thái không clickable
                    for player in Statekpr.players:
                        for pawn in player.pawnlist:
                            pawn.clickable = False
                    
                    # Kích hoạt quân có thể di chuyển
                    for pawn in current_player.pawnlist:
                        # Skip pawns that have already reached finish
                        if hasattr(pawn, 'has_reached_finish') and pawn.has_reached_finish:
                            pawn.clickable = False
                            continue

                        # Kích hoạt quân trong chuồng CHỈ khi tổng >= 10
                        if pawn.counter == 0:
                            # Chỉ cho phép di chuyển nếu tổng >= 10
                            if dice_sum >= 10:
                                # Kiểm tra xem vị trí xuất phát đã có quân cùng màu không
                                position_blocked = False
                                start_position = pawn.dict[1]
                            else:
                                position_blocked = True
                            for other_pawn in current_player.pawnlist:
                                if other_pawn != pawn and other_pawn.rect.center == start_position:
                                    position_blocked = True
                                    break
                            
                            if not position_blocked:
                                pawn.activepawn = True
                                pawn.clickable = True  # Đánh dấu quân có thể click
                                can_move = True
                            
                        # Kích hoạt quân đã trên bàn có thể di chuyển
                        elif pawn.counter > 0 and pawn.counter + dice_sum <= 97:
                            # Kiểm tra vị trí đích có quân cùng màu không
                            position_blocked = False
                            target_position = pawn.dict[pawn.counter + dice_sum]
                            for other_pawn in current_player.pawnlist:
                                if other_pawn != pawn and other_pawn.rect.center == target_position:
                                    position_blocked = True
                                    break
                            
                            if not position_blocked:
                                pawn.activepawn = True
                                pawn.clickable = True  # Đánh dấu quân có thể click
                                can_move = True
                            
                    if not can_move:
                        # Không có nước đi hợp lệ, chuyển lượt và giữ nút enable
                        roll_button_enabled = True
                        Statekpr.find_next_valid_player()
                        last_turn_change_time = pygame.time.get_ticks()
                    Statekpr.update_display_player()
        
        #Set event logic
        for event in pygame.event.get():
            #set basic Quit
            if event.type == QUIT:
                mainLoop = False
                return False
            #check for key presses
            if event.type == KEYDOWN:
                #set Escape Key quit
                if event.key == K_ESCAPE:
                    mainLoop = False
                    return False
                
            # Xử lý sự kiện cuộn chuột
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Xử lý sự kiện click hiện có...
                
                # Thêm xử lý cuộn bằng bánh xe chuột (scrollwheel)
                if event.button == 4:  # Cuộn lên
                    scroll_y = max(0, scroll_y - SCROLL_SPEED)
                    update_scroll_limits()
                elif event.button == 5:  # Cuộn xuống
                    scroll_y += SCROLL_SPEED
                    update_scroll_limits()
                    
                # Bắt đầu kéo thả để cuộn
                elif event.button == 3:  # Chuột phải
                    is_scrolling = True
                    scroll_start_pos = event.pos
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)
            
            # Xử lý kéo thả để cuộn
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:  # Chuột phải
                    is_scrolling = False
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            
            # Cuộn theo chuột khi kéo thả
            elif event.type == pygame.MOUSEMOTION:
                if is_scrolling:
                    # Tính toán khoảng cách di chuyển
                    dx = scroll_start_pos[0] - event.pos[0]
                    dy = scroll_start_pos[1] - event.pos[1]
                    
                    # Cập nhật vị trí cuộn
                    scroll_x += dx
                    scroll_y += dy
                    
                    # Cập nhật giới hạn cuộn
                    update_scroll_limits()
                    
                    # Cập nhật vị trí bắt đầu cho lần di chuyển tiếp theo
                    scroll_start_pos = event.pos
                
            # Xử lý sự kiện click chuột
            if event.type == MOUSEBUTTONDOWN and not any_pawn_animating:  # Chỉ cho phép click khi không có animation
                mouse_pos = event.pos
                # Điều chỉnh vị trí chuột theo vị trí cuộn
                adjusted_mouse_pos = (mouse_pos[0] + scroll_x, mouse_pos[1] + scroll_y)
                
                if showing_ranking:
                    #Kiểm tra click vào nút Tiêu đề trong bảng xếp hạng
                    if title_ranking_button.collidepoint(mouse_pos):
                        mainLoop = False
                        finished_players.clear()  # Clear finished players list
                        return "restart"  # Signal to restart game
                # Xử lý dialog nếu đang hiển thị
                if showing_dialog:
                    if yes_button.collidepoint(mouse_pos):
                        # Quay về main_board và hủy màn chơi hiện tại
                        mainLoop = False
                        return None
                    elif no_button.collidepoint(mouse_pos):
                        showing_dialog = False
                    # Nếu đang hiện dialog, không xử lý bất kỳ click nào khác
                    continue
                
                # Kiểm tra click vào nút tiêu đề khi không hiện dialog
                if title_button.collidepoint(adjusted_mouse_pos):
                    showing_dialog = True
                    continue
                
                # Kiểm tra nếu click vào nút tung xúc xắc
                if roll_button.collidepoint(adjusted_mouse_pos) and roll_button_enabled and not dice_animating:
                    if not Statekpr.gamestart:
                        Statekpr.start_game()
                    # Start dice animation
                    dice_animating = True
                    animation_frame = 0
                    animation_timer = 0
                    last_animation_time = pygame.time.get_ticks()
                    # Pre-determine final dice values
                    
                    final_dice_value1 = random.randint(0, 5)
                    final_dice_value2 = random.randint(0, 5)
                    dice_num1 = final_dice_value1 + 1  # Store final numbers (1-6)
                    dice_num2 = final_dice_value2 + 1
                    dice_sum = dice_num1 + dice_num2  # Calculate sum
        
                    
                
                # Kiểm tra click vào quân cờ khi nút tung xúc xắc đang disable
                if not roll_button_enabled:
                    # Xác định người chơi hiện tại dựa trên lượt
                    current_player = None
                    if Statekpr.redTurn:
                        current_player = Statekpr.playerRed
                    elif Statekpr.blueTurn:
                        current_player = Statekpr.playerBlue
                    elif Statekpr.yellowTurn:
                        current_player = Statekpr.playerYellow
                    elif Statekpr.greenTurn:
                        current_player = Statekpr.playerGreen
                        
                    # Chỉ cho phép di chuyển quân của người chơi đang đến lượt
                    for pawn in current_player.pawnlist:
                        # Kiểm tra va chạm chính xác hơn với quân cờ
                        distance_threshold = 15  # Giá trị ngưỡng khoảng cách, có thể điều chỉnh
                        pawn_center = pawn.rect.center
                        # Điều chỉnh vị trí chuột theo vị trí cuộn
                        adjusted_mouse_pos = (mouse_pos[0] + scroll_x, mouse_pos[1] + scroll_y)
                        mouse_distance = ((adjusted_mouse_pos[0] - pawn_center[0])**2 + (adjusted_mouse_pos[1] - pawn_center[1])**2)**0.5
                        if mouse_distance <= distance_threshold:
                            # Kiểm tra điều kiện được phép click
                            can_click = False
                            position_blocked = False
                            
                            # Trường hợp 1: Quân chưa từng được click (trong chuồng hoặc trên bàn)
                            if pawn.counter == 0:
                                # Kiểm tra vị trí xuất phát có quân cùng màu không
                                start_position = pawn.dict[1]
                                for other_pawn in current_player.pawnlist:
                                    if other_pawn != pawn and other_pawn.rect.center == start_position:
                                        position_blocked = True
                                        break
                                # Chỉ cho click khi tung được tổng lớn hơn hoặc bằng 10
                                if (dice_num1 + dice_num2) >= 10 and not position_blocked:
                                    can_click = True
                                elif (dice_num1 + dice_num2) < 10:
                                    position_blocked = False
                            
                            # Trường hợp 2: Quân đã từng được click (có thể click với bất kỳ số nào)
                            else:
                                # Kiểm tra ngay nếu vượt quá 97
                                if pawn.counter + (dice_num1 + dice_num2) > 97:
                                    # Hiển thị thông báo lỗi
                                    alert_manager.add_alert("Không thể di chuyển quá đích!", 2000)
                                else:
                                    # Kiểm tra vị trí đích có quân cùng màu không
                                    target_position = pawn.dict[pawn.counter + dice_num1 + dice_num2]
                                    for other_pawn in current_player.pawnlist:
                                        if other_pawn != pawn and other_pawn.rect.center == target_position:
                                            position_blocked = True
                                            break
                                    
                                    # Quân trên bàn và có thể di chuyển
                                    if pawn.counter > 0 and not position_blocked:
                                        can_click = True
                            
                            if can_click:  # Chỉ xử lý khi can_click = True
                            
                                # Bỏ chọn tất cả quân cờ khác
                                for other_pawn in current_player.pawnlist:
                                    other_pawn.activepawn = False
                                    
                                # Kiểm tra nước đi hợp lệ
                                valid_move = False
                                
                                # Trường hợp 1: Xuất quân (quân đang ở chuồng và tổng >= 10)
                                if pawn.counter == 0 and dice_num1 + dice_num2 >= 10:
                                    pawn.counter = 1  # Đặt counter là 1 (vị trí xuất phát)
                                    new_pos = pawn.dict[1]  # Đặt quân ở vị trí xuất phát
                                    for other_player in Statekpr.players:
                                        if other_player != current_player:  # Chỉ kiểm tra với quân của người chơi khác
                                            for other_pawn in other_player.pawnlist:
                                                if (other_pawn.rect.center == new_pos and 
                                                    other_pawn.counter > 0 and 
                                                    not other_pawn.is_dying):
                                                    print(f"Quân của {current_player.name} ăn quân của {other_player.name} khi xuất quân")
                                                    other_pawn.start_death_animation()
                                                    other_player.pawns -= 1
                                                    other_player.times_kicked += 1
                                                    alert_manager.add_alert(f"{current_player.name} ăn quân của {other_player.name}!", 2000)
                                                    break
                                    pawn.start_teleport(new_pos)  # Đặt quân ở vị trí xuất phát
                                    current_player.pawns += 1  # Tăng số quân trên bàn
                                    valid_move = True
                                    
                                    # Vô hiệu hóa nút tung xúc xắc trong khi animation đang chạy
                                    roll_button_enabled = False
                                    
                                # Trường hợp 2: Di chuyển quân trên bàn (chỉ khi quân không phải vừa được xuất ra)
                                elif pawn.counter > 0 and pawn.counter + dice_num1 + dice_num2 <= 97:
                                    # Lưu vị trí mới
                                    new_pos = pawn.dict[pawn.counter + dice_num1 + dice_num2]
                                    
                                    # Bỏ chọn tất cả quân cờ khác
                                    for other_pawn in current_player.pawnlist:
                                        other_pawn.activepawn = False

                                    # Di chuyển quân với tổng hai xúc xắc
                                    pawn.move(dice_num1 + dice_num2, Statekpr)
                                    valid_move = True
                                    # Vô hiệu hóa nút tung xúc xắc trong khi animation đang chạy
                                    roll_button_enabled = False
                                    
                                # Bỏ trạng thái clickable của tất cả quân
                                for player_pawn in current_player.pawnlist:
                                    player_pawn.clickable = False

                            if position_blocked:
                                # Hiển thị thông báo nếu click vào quân không thể di chuyển do bị chặn
                                alert_manager.add_alert("Đã có quân của bạn ở đó!", 2000)
                            
                            break  # Đặt break ra ngoài, chỉ thoát khỏi vòng lặp sau khi kiểm tra xong
       
        # Vẽ map với vị trí cuộn
        win.fill((0, 0, 0))  # Xóa màn hình
        blit_with_scroll(win, bgBoard, (0, 0))

        # Vẽ sidebar với vị trí cuộn
        blit_with_scroll(win, bgSidebar, (725, 0))

        # Vẽ sao
        for star in stars:
            star_rect = star.rect.copy()
            star_rect.x -= scroll_x
            star_rect.y -= scroll_y
            win.blit(star.surf, star_rect)

        # Vẽ sidebar với vị trí cuộn
        draw_sidebar_with_scroll(win, Statekpr)

        # Vẽ sprites với vị trí cuộn
        for entity in allSprites:
            entity_rect = entity.rect.copy()
            entity_rect.x -= scroll_x
            entity_rect.y -= scroll_y
            # Vẽ hiệu ứng phát sáng nếu entity là Pawn và có thể click
            if isinstance(entity, Pawn):
                entity.draw_with_glow(win, entity_rect.center)
            
            win.blit(entity.surf, entity_rect)
        
        # Vẽ các thông báo - đặt ở cuối để hiển thị trên cùng
        alert_manager.draw(win)
            
        # Vẽ dialog nếu đang hiển thị
        if showing_dialog:
            draw_dialog(win)
            
        if showing_ranking:
            draw_ranking(win)
            
        pygame.display.flip()

# if this is the main python script, run the MainBoard
if __name__ == '__main__':
    from main_board import MainBoard
    board = MainBoard()
    board.run()