import pygame
import sys
from main_board import MainBoard
import importlib
import gc
import os

def run_game():
    pygame.init()
    # Lấy thông tin màn hình
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h
    
    # Kích thước cửa sổ game
    winX = 925
    winY = 725
    
    # Căn giữa cửa sổ
    pos_x = (screen_width - winX) // 2
    pos_y = (screen_height - winY) // 2
    
    # Đặt vị trí cửa sổ
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{pos_x},{pos_y}"
    
    while True:
        try:
            # Chạy màn hình chính và nhận tên người chơi
            print("[DEBUG] Creating new MainBoard instance")
            menu = MainBoard()
            print("[DEBUG] Running MainBoard")
            player_names = menu.run()
            print(f"[DEBUG] MainBoard run completed, player_names: {player_names}")
            
            if player_names:
                # Đảm bảo main module được import lại mỗi lần để tái khởi tạo
                try:
                    # Xóa module main từ sys.modules để đảm bảo nó được tải lại hoàn toàn
                    import sys
                    modules_to_reload = ['main', 'Players', 'Pawns', 'States', 'Stars', 'menu_manager']
                    print("[DEBUG] Cleaning up modules for reload:")
                    for module in modules_to_reload:
                        if module in sys.modules:
                            print(f"[DEBUG] Removing module: {module}")
                            del sys.modules[module]
                    if 'alert_manager' in sys.modules:
                        print("[DEBUG] Removing alert_manager module")
                        del sys.modules['alert_manager']
                    
                    print("[DEBUG] Clearing game state and reinitializing")
                    # Initialize sprite groups
                    global redPawn, bluePawn, yellowPawn, greenPawn, allSprites
                    
                    # Create new sprite groups
                    from pygame.sprite import Group
                    redPawn = Group()
                    bluePawn = Group()
                    yellowPawn = Group()
                    greenPawn = Group()
                    allSprites = Group()
                    
                    print("[DEBUG] New sprite groups initialized")
                        
                    # Chạy garbage collector để giải phóng bộ nhớ
                    gc.collect()
                        
                    # Tải lại tất cả các module liên quan
                    print("[DEBUG] Reloading main module")
                    import main
                    
                    # Gọi main với tên người chơi đã nhập
                    print("[DEBUG] Starting main game with player names")
                    result = main.main(player_names)
                    print(f"[DEBUG] Game result: {result}")
                    
                    # Xử lý kết quả
                    if result == False:  # Người chơi muốn thoát game hoàn toàn
                        pygame.quit()
                        sys.exit()
                    elif result == "restart":
                        # Tiếp tục vòng lặp để hiển thị menu chính và bắt đầu ván mới
                        continue
                    # Nếu result là None, quay lại vòng lặp và hiển thị menu chính
                except Exception as e:
                    print(f"Loi khi tai lai tro choi: {e}")
                    continue  # Vẫn tiếp tục vòng lặp để hiển thị menu chính
            else:
                # Nếu không có tên người chơi (ví dụ: người dùng thoát)
                pygame.quit()
                sys.exit()
        except Exception as e:
            print(f"Loi: {e}")
            # Tiếp tục vòng lặp nếu có lỗi để không đóng ứng dụng

if __name__ == "__main__":
    run_game()