import pygame
import sys
from main_board import MainBoard
import importlib
import gc

def run_game():
    pygame.init()
    
    while True:
        try:
            # Chạy màn hình chính và nhận tên người chơi
            menu = MainBoard()
            player_names = menu.run()
            
            if player_names:
                # Đảm bảo main module được import lại mỗi lần để tái khởi tạo
                try:
                    # Xóa module main từ sys.modules để đảm bảo nó được tải lại hoàn toàn
                    import sys
                    if 'main' in sys.modules:
                        del sys.modules['main']
                    if 'Players' in sys.modules:
                        del sys.modules['Players']
                    if 'Pawns' in sys.modules:
                        del sys.modules['Pawns']
                    if 'States' in sys.modules:
                        del sys.modules['States']
                        
                    # Chạy garbage collector để giải phóng bộ nhớ
                    gc.collect()
                        
                    # Tải lại tất cả các module liên quan
                    import main
                    
                    # Gọi main với tên người chơi đã nhập
                    result = main.main(player_names)
                    
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