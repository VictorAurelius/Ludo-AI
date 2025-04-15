from pygame.locals import *
from Pawns import *
from Players import *
from States import *
from Stars import stars
import pygame
import pytmx
import os
from main_board import MainBoard
from pytmx.util_pygame import load_pygame
from alert_manager import AlertManager
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
    pygame.image.load('img/1_block.png'),
    pygame.image.load('img/2_block.png'),
    pygame.image.load('img/3_block.png'),
    pygame.image.load('img/4_block.png'),
    pygame.image.load('img/5_block.png'),
    pygame.image.load('img/6_block.png')
]
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
COLORS = {
    'Red': (255, 0, 0),
    'Blue': (0, 0, 255),
    'Yellow': (255, 255, 0),
    'Green': (0, 255, 0)
}

# Font
font = pygame.font.Font(None, 32)

# Các nút trong sidebar
roll_button = pygame.Rect(735, 290, 180, 50)
title_button = pygame.Rect(745, 10, 160, 40)
title_ranking_button = pygame.Rect(400, 400, 200, 50)

# Các biến toàn cục
roll_button_enabled = True  # Trạng thái nút tung xúc xắc
can_move = False  # Biến kiểm tra có thể di chuyển không
dice_animating = False  # Biến kiểm tra xúc xắc đang animating
# Reset for new game
showing_dialog = False  # Biến kiểm tra đang hiện dialog
yes_button = pygame.Rect(410, 260, 60, 30)  # Nút "Có"
no_button = pygame.Rect(530, 260, 90, 30)  # Nút "Không"
current_dice1 = dice_images[0]  # Mặt xúc xắc 1
current_dice2 = dice_images[0]  # Mặt xúc xắc 2
dice_num1 = 1  # Số hiện tại trên xúc xắc 1
dice_num2 = 1  # Số hiện tại trên xúc xắc 2

# Biến lưu thông báo hiệu ứng sao và alert
star_effect_message = ""
star_effect_time = 0
alert_time = 0

# Biến để lưu thứ tự về đích
finished_players = []

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

def load_sidebar():
    """Tải background sidebar từ file TMX"""
    # Tạo surface cho sidebar với kích thước 200x725
    sidebar_surface = pygame.Surface((200, 725))
    
    try:
        # Load map từ file TMX
        sidebar_map = load_pygame('mapfinal/slide_bar.tmx')
        
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
    game_map = load_pygame('mapfinal/mapludo.tmx')
    
    # Vẽ từng layer của map lên surface mới
    for layer in game_map.visible_layers:
        for x, y, gid in layer:
            tile = game_map.get_tile_image_by_gid(gid)
            if tile:
                map_surface.blit(tile, (x * game_map.tilewidth, y * game_map.tileheight))
    
    return map_surface  # Trả về surface đã vẽ map

# Khởi tạo bàn cờ từ Tiled
bgBoard = load_map()
bgSidebar = load_sidebar()
bgRanking = load_ranking()

def draw_dialog(win):
    # Vẽ background mờ
    s = pygame.Surface((925, 725))
    s.set_alpha(128)
    s.fill((0, 0, 0))
    win.blit(s, (0, 0))
    
    # Vẽ dialog box
    dialog_rect = pygame.Rect(400, 200, 230, 100)
    pygame.draw.rect(win, WHITE, dialog_rect)
    pygame.draw.rect(win, BLACK, dialog_rect, 2)
    
    # Vẽ text
    vn_font = pygame.font.SysFont("segoeui", 24)
    text = vn_font.render(u"Bạn có muốn trở về", True, BLACK)
    text2 = vn_font.render(u"trang tiêu đề không?", True, BLACK)
    win.blit(text, (410, 200))
    win.blit(text2, (410, 220))
    
    # Vẽ nút Có/Không
    pygame.draw.rect(win, BLACK, yes_button, 2)
    pygame.draw.rect(win, BLACK, no_button, 2)
    yes_text = vn_font.render(u"Có", True, BLACK)
    no_text = vn_font.render(u"Không", True, BLACK)
    win.blit(yes_text, (425, 255))
    win.blit(no_text, (540, 255))

def draw_sidebar(win, Statekpr):
    global star_effect_message, star_effect_time, dice_animating
    
    win.blit(bgSidebar, (725, 0))
    
    # Font cho tiếng Việt
    vn_font = pygame.font.SysFont("segoeui", 20)
    
    # Vẽ nút Tiêu đề
    pygame.draw.rect(win, BLACK, title_button, 2)
    title_text = vn_font.render(u"Tiêu đề", True, BLACK)
    win.blit(title_text, (790, 15))
    
    # Hiển thị người chơi đang đến lượt
    text = vn_font.render(u"Lượt của:", True, BLACK)
    win.blit(text, (735, 60))
    
    # Nếu display_player chưa được khởi tạo, khởi tạo ban đầu dựa trên lượt
    if Statekpr.display_player is None:
        Statekpr.update_display_player()
            
    # Hiển thị tên người chơi hiện tại
    color = COLORS[Statekpr.display_player.color]
    text = vn_font.render(Statekpr.display_player.name, True, color)
    win.blit(text, (735, 90))
    
    # Vẽ nút tung xúc xắc
    button_color = GRAY
    if not roll_button_enabled or dice_animating:  # Thêm điều kiện dice_animating
        button_color = (100, 100, 100)  # Tối màu khi disable hoặc đang animation
    pygame.draw.rect(win, button_color, roll_button)
    text = vn_font.render(u"Tung xúc xắc", True, WHITE)
    win.blit(text, (770, 298))
    
    # Hiển thị 2 hình xúc xắc
    scaled_dice1 = pygame.transform.scale(current_dice1, (80, 80))
    scaled_dice2 = pygame.transform.scale(current_dice2, (80, 80))
    win.blit(scaled_dice1, (745, 140))
    win.blit(scaled_dice2, (835, 140))
    
    # Hiển thị tổng hai xúc xắc CHỈ KHI ANIMATION KẾT THÚC
    if not dice_animating:  # Chỉ hiển thị khi animation kết thúc
        total = dice_num1 + dice_num2
        total_text = vn_font.render(f"Tổng: {total}", True, BLACK)
        win.blit(total_text, (790, 233))
    
    # Hiển thị thông tin quân cờ của từng người chơi
    y_pos = 360
    for player in Statekpr.players:
        color = COLORS[player.color]
        text = vn_font.render(f"{player.name}:", True, color)
        win.blit(text, (735, y_pos))
        
        # Đếm số quân về đích (counter = 52)
        text = vn_font.render(f"Về đích: {player.pawns_home}", True, BLACK)
        win.blit(text, (745, y_pos + 30))
        
        # Hiển thị số lần bị đá
        text = vn_font.render(f"Bị đá: {player.times_kicked}", True, BLACK)
        win.blit(text, (745, y_pos + 55))
        
        y_pos += 90
    
    # Hiển thị thông báo hiệu ứng sao
    if star_effect_message and pygame.time.get_ticks() - star_effect_time < 2000:
        text = vn_font.render(star_effect_message, True, (255, 215, 0))  # Màu vàng
        # Đặt thông báo ở dưới thông tin người chơi
        win.blit(text, (735, y_pos + 20))

def draw_ranking(win):
    """Vẽ bảng xếp hạng"""
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
    title_text = vn_font.render(u"Tiêu đề", True, BLACK)
    win.blit(title_text, (450, 410))
    
# MainFunction
# Animation constants
DICE_ANIMATION_FRAMES = 15  # Number of frames for animation
DICE_ANIMATION_SPEED = 50   # Milliseconds between frames

def main(player_names=None):
    global alert_manager
    
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
    global current_dice1, current_dice2, roll_button_enabled, dice_num1, dice_num2, can_move, showing_dialog, dice_animating, display_player, finished_players
    finished_players = []
    
    # Reset dialog state
    showing_dialog = False
    
    # main Objects
    #Initialize statekeeper object
    Statekpr = Statekeep()
    #Initialize clock
    clock = pygame.time.Clock()
    
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
    
    # for each player in the players list
    for i, player in enumerate(Statekpr.players):
        #pass the statekeeper object to the players
        player.set_statekeeper(Statekpr)
        # Gán tên cho các người chơi
        if player_names and i < len(player_names):
            player.name = player_names[i]
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

        # Initialize both dice with value 1 at start
        if not dice_animating and current_dice1 is None:
            current_dice1 = dice_images[0]
            current_dice2 = dice_images[0]
        
        # Kiểm tra nếu có quân cờ đang animation
        any_pawn_animating = False
        for player in Statekpr.players:
            for pawn in player.pawnlist:
                # Cập nhật animation
                pawn.update_animation()
                # Thêm kiểm tra teleporting
                if pawn.teleporting:
                    pawn.update_animation()
                    any_pawn_animating = True
                # Kiểm tra nếu quân đang di chuyển
                if pawn.is_move:
                    pawn.update_animation()  # Cập nhật vị trí của quân trong animation
                    any_pawn_animating = True
                elif hasattr(pawn, 'just_finished_animation') and pawn.just_finished_animation:
                    # Quân vừa hoàn thành animation, xử lý các hiệu ứng sau di chuyển
                    pawn.just_finished_animation = False
                    
                    # Đặt thời gian để kiểm tra chuỗi teleport
                    last_animation_end_time = pygame.time.get_ticks()
                    
                    # Đặt cờ để cho biết đã kiểm tra va chạm với sao
                    star_checked = False
                    chain_continues = False
                                                
                    got_roll_again = False  # Reset biến
                    teleported = False  # Reset biến
                    
                    # Kiểm tra va chạm với sao ban đầu
                    star_hit = check_star_collision(pawn, current_player)
                    star_checked = True
                    
                    # Nếu vừa teleport và nhận được hiệu ứng teleport mới, đánh dấu chuỗi tiếp tục
                    if teleported:
                        teleport_chain_active = True
                        last_teleport_time = pygame.time.get_ticks()
                        chain_continues = True
                        
                    elif not teleported:
                        teleport_chain_active = False
                    
                    if hasattr(pawn, 'teleporting') and pawn.teleporting == False and pawn.counter == 1:
                        # Kiểm tra có quân nào của đối thủ ở vị trí mới không
                        new_pos = pawn.rect.center
                        for other_player in Statekpr.players:
                            if other_player != current_player:
                                for other_pawn in other_player.pawnlist:
                                    if other_pawn.rect.center == new_pos:
                                        # Đá quân về chuồng và tăng biến đếm số lần bị đá
                                        other_pawn.counter = 0
                                        other_pawn.rect.center = other_pawn.startpos
                                        other_player.pawns -= 1
                                        other_player.times_kicked += 1
                                        break
                                    
                        # Kiểm tra va chạm với sao sau khi teleport
                        check_star_collision(pawn, current_player)
                        star_checked = True
                        
                        # Nếu nhận được teleport từ sao, đánh dấu chuỗi tiếp tục
                        if teleported:
                            teleport_chain_active = True
                            last_teleport_time = pygame.time.get_ticks()
                            chain_continues = True
                            
                        if not teleported:
                            teleport_chain_active = False
                                    
                        # Enable lại nút tung xúc xắc
                        roll_button_enabled = True
                        
                        
                        # Cập nhật người chơi hiển thị sau khi chuyển lượt
                        Statekpr.update_display_player()    
                        
                    # Nếu đã kiểm tra va chạm với sao và không có chuỗi teleport tiếp tục
                    if star_checked and not chain_continues:
                        # CHỈ chuyển lượt nếu không còn trong chuỗi teleport và không được tung lại xúc xắc
                        if not teleport_chain_active and valid_move and not got_roll_again:
                            # Kích hoạt nút tung xúc xắc
                            roll_button_enabled = True
                            
                            Statekpr.find_next_valid_player()
                            
                            # Cập nhật người chơi hiển thị sau khi chuyển lượt
                            Statekpr.update_display_player()        
                    
                    # Kiểm tra nếu quân đã về đích (counter = 52 hoặc 53) để tăng số quân về đích
                    if pawn.counter == 96 or pawn.counter == 97:
                        # Tìm người chơi sở hữu quân này và tăng pawns_home
                        for player in Statekpr.players:
                            if pawn in player.pawnlist:
                                # Kiểm tra nếu người chơi vừa về đích hết và chưa có trong danh sách
                                if player.pawns_home == 4 and player not in finished_players:
                                    finished_players.append(player)
                                break
                    # Lấy vị trí hiện tại làm new_pos
                    new_pos = pawn.rect.center
                    # Kiểm tra có quân nào của đối thủ ở vị trí mới không
                    for other_player in Statekpr.players:
                        if other_player != current_player:
                            for other_pawn in other_player.pawnlist:
                                if other_pawn.rect.center == new_pos:
                                    # Đá quân về chuồng và tăng biến đếm số lần bị đá
                                    other_pawn.counter = 0
                                    other_pawn.rect.center = other_pawn.startpos
                                    other_player.pawns -= 1
                                    other_player.times_kicked += 1
                                    break
                    
                    
                    
                    if roll_button_enabled == False:
                        roll_button_enabled = True
                            
                # Kiểm tra điều kiện hiển thị bảng xếp hạng
                showing_ranking = len(finished_players) >= 3
        
        # Cập nhật danh sách thông báo
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
                
            # Xử lý sự kiện click chuột
            if event.type == MOUSEBUTTONDOWN and not any_pawn_animating:  # Chỉ cho phép click khi không có animation
                mouse_pos = event.pos
                
                if showing_ranking:
                    #Kiểm tra click vào nút Tiêu đề trong bảng xếp hạng
                    if title_ranking_button.collidepoint(mouse_pos):
                        mainLoop = False
                        return None
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
                if title_button.collidepoint(mouse_pos):
                    showing_dialog = True
                    continue
                
                # Kiểm tra nếu click vào nút tung xúc xắc
                if roll_button.collidepoint(mouse_pos) and roll_button_enabled and not dice_animating:
                    if not Statekpr.gamestart:
                        Statekpr.start_game()
                    # Start dice animation
                    dice_animating = True
                    animation_frame = 0
                    animation_timer = 0
                    last_animation_time = pygame.time.get_ticks()
                    # Pre-determine final dice values
                    import random
                    final_dice_value1 = random.randint(0, 5)
                    final_dice_value2 = random.randint(0, 5)
                    dice_num1 = final_dice_value1 + 1  # Store final numbers (1-6)
                    dice_num2 = final_dice_value2 + 1
                    dice_sum = dice_num1 + dice_num2  # Calculate sum
        
                    # Kiểm tra có thể di chuyển không
                    can_move = False
                    
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
                        
                    roll_button_enabled = False  # Disable nút để chờ người chơi chọn quân
                    
                    # Kích hoạt quân có thể di chuyển
                    for pawn in current_player.pawnlist:
                        # Kích hoạt quân trong chuồng nếu tổng >= 10
                        if pawn.counter == 0 and dice_sum >= 10:
                            # Kiểm tra xem vị trí xuất phát đã có quân cùng màu không
                            position_blocked = False
                            start_position = pawn.dict[1]
                            for other_pawn in current_player.pawnlist:
                                if other_pawn != pawn and other_pawn.rect.center == start_position:
                                    position_blocked = True
                                    break
                            
                            if not position_blocked:
                                pawn.activepawn = True
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
                                can_move = True
                            
                    if not can_move:
                        # Không có nước đi hợp lệ, chuyển lượt và giữ nút enable
                        roll_button_enabled = True
                        Statekpr.find_next_valid_player()
                
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
                        mouse_distance = ((mouse_pos[0] - pawn_center[0])**2 + (mouse_pos[1] - pawn_center[1])**2)**0.5
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
                                    pawn.start_teleport(new_pos)  # Đặt quân ở vị trí xuất phát
                                    current_player.pawns += 1  # Tăng số quân trên bàn
                                    valid_move = True
                                    
                                    # Vô hiệu hóa nút tung xúc xắc trong khi animation đang chạy
                                    roll_button_enabled = False
                                    
                                    Statekpr.update_display_player()
                                    
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

                            if position_blocked:
                                # Hiển thị thông báo nếu click vào quân không thể di chuyển do bị chặn
                                alert_manager.add_alert("Đã có quân của bạn ở đó!", 2000)
                            
                            break  # Đặt break ra ngoài, chỉ thoát khỏi vòng lặp sau khi kiểm tra xong
       
        # Vẽ sao
        for star in stars:
            win.blit(star.surf, star.rect)

        # Vẽ sidebar và sprites
        draw_sidebar(win, Statekpr)
        for entity in allSprites:
            win.blit(entity.surf, entity.rect)
        
        # Vẽ các thông báo - đặt ở cuối để hiển thị trên cùng
        alert_manager.draw(win)
        
        # Cập nhật màn hình
        pygame.display.update()
            
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