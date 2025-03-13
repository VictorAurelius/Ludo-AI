import pygame
import random
from pygame.locals import *

class Star(pygame.sprite.Sprite):
    def __init__(self, position):
        super(Star, self).__init__()
        self.surf = pygame.image.load('img/Star.png')
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(center=position)
        
    def apply_effect(self, pawn, statekeeper):
        effect = random.randint(1, 3)
        if effect == 1:
            # Xúc xắc thêm lần nữa
            return "roll_again"
        elif effect == 2:
            # Dịch chuyển ngẫu nhiên
            valid_positions = []
            for pos in range(1, 53):
                can_move = True
                new_pos = pawn.dict[pos]
                # Kiểm tra vị trí có quân nào không
                for player in statekeeper.players:
                    for other_pawn in player.pawnlist:
                        if other_pawn != pawn and other_pawn.rect.center == new_pos:
                            can_move = False
                            break
                    if not can_move:
                        break
                if can_move:
                    valid_positions.append(pos)
            
            if valid_positions:
                new_pos = random.choice(valid_positions)
                pawn.counter = new_pos
                pawn.rect.center = pawn.dict[new_pos]
                return "teleported"
        else:
            # Về chuồng
            pawn.counter = 0
            pawn.rect.center = pawn.startpos
            # Tìm người chơi sở hữu quân này
            for player in statekeeper.players:
                if pawn in player.pawnlist:
                    player.pawns -= 1
                    break
            return "died"

# Tạo list chứa các vị trí có thể đặt sao
# Bỏ qua các vị trí xuất phát và đích
restricted_positions = [1, 13, 25, 37, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67]

# Dict lưu vị trí của các ô trên bàn cờ (lấy từ redDICT làm chuẩn)
positions = {
    1: (124, 346), 2: (177, 346), 3: (230, 346), 4: (283, 346), 5: (335, 334), 6: (346, 283),
    7: (346, 230), 8: (346, 177), 9: (346, 124), 10: (346, 71), 11: (400, 71), 12: (453, 71), 
    13: (453, 124), 14: (453, 177), 15: (453, 230), 16: (453, 283), 17: (467, 333), 18: (516, 346),
    19: (570, 346), 20: (622, 346), 21: (675, 346), 22: (728, 346), 23: (728, 400), 24: (728, 453),
    25: (675, 453), 26: (622, 453), 27: (570, 453), 28: (516, 453), 29: (467, 466), 30: (453, 516),
    31: (453, 570), 32: (453, 622), 33: (453, 675), 34: (453, 728), 35: (400, 728), 36: (346, 728),
    37: (346, 675), 38: (346, 622), 39: (346, 570), 40: (346, 516), 41: (333, 466), 42: (283, 453),
    43: (230, 453), 44: (177, 453), 45: (124, 453), 46: (71, 453), 47: (71, 400), 48: (124, 400),
    49: (177, 400), 50: (230, 400), 51: (283, 400), 52: (333, 400), 53: (400, 124), 54: (400, 177),
    55: (400, 230), 56: (400, 283), 57: (400, 330), 58: (675, 400), 59: (622, 400), 60: (570, 400),
    61: (516, 400), 62: (466, 400), 63: (400, 675), 64: (400, 622), 65: (400, 570), 66: (400, 516), 
    67: (400, 466)
}

# Tạo list vị trí có thể đặt sao
available_positions = []
for pos, coord in positions.items():
    if pos not in restricted_positions:
        available_positions.append(coord)

# Chọn ngẫu nhiên 8 vị trí để đặt sao
star_positions = random.sample(available_positions, 8)

# Tạo list chứa các đối tượng Star
stars = pygame.sprite.Group()
for pos in star_positions:
    star = Star(pos)
    stars.add(star)