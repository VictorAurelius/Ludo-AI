import pygame
import random
from pygame.locals import *
from Pawns import TILE_SIZE

class Star(pygame.sprite.Sprite):
    def __init__(self, position):
        super(Star, self).__init__()
        self.surf = pygame.image.load('img/Star.png')
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(center=(position[0] * TILE_SIZE - 13, position[1] * TILE_SIZE - 13))
        self.position = position
        
    def check_exact_collision(self, pawn):
        """Kiểm tra va chạm dựa trên vị trí trung tâm của ô"""
        # Lấy vị trí trung tâm của pawn và sao (dưới dạng số ô, không phải pixel)
        pawn_center = ((pawn.rect.center[0] + 13) // TILE_SIZE, (pawn.rect.center[1] + 13) // TILE_SIZE)
        # So sánh vị trí ô
        return pawn_center == (self.position[0], self.position[1])
        
    def apply_effect(self, pawn, statekeeper):
        effect = random.randint(0, 2)
        if effect == 1:
            # Xúc xắc thêm lần nữa
            return "roll_again"
        elif effect == 2:
            # Dịch chuyển ngẫu nhiên
            valid_positions = []
            for pos in range(1, 97):
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
        elif effect == 0:
            # Dịch chuyển ngẫu nhiên
            valid_positions = []
            for pos in range(1, 97):
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
restricted_positions = [1, 25, 49, 73, 93, 94, 95, 96, 97, 98, 99,
                        100, 101, 102, 103, 104, 105, 106, 107, 108]

# Dict lưu vị trí của các ô trên bàn cờ (lấy từ redDICT làm chuẩn)
positions = {
    1: (4, 11),
    2: (5, 11),
    3: (6, 11),
    4: (7, 11),
    5: (8, 11),
    6: (9, 11),
    7: (10, 11),
    8: (11, 11),
    9: (11, 10), 
    10: (11, 9),
    11: (11, 8),
    12: (11, 7),
    13: (11, 6),
    14: (11, 5),
    15: (11, 4),
    16: (11, 3),
    17: (12, 3),
    18: (13, 3),
    19: (14, 3),
    20: (15, 3),
    21: (16, 3),
    22: (17, 3),
    23: (18, 3),
    24: (19, 3),
    25: (19, 4),
    26: (19, 5),
    27: (19, 6),
    28: (19, 7),
    29: (19, 8),
    30: (19, 9),
    31: (19, 10),
    32: (19, 11),
    33: (20, 11),
    34: (21, 11),
    35: (22, 11),
    36: (23, 11),
    37: (24, 11),
    38: (25, 11),
    39: (26, 11),
    40: (27, 11),
    41: (27, 12),
    42: (27, 13),
    43: (27, 14),
    44: (27, 15),
    45: (27, 16),
    46: (27, 17),
    47: (27, 18),
    48: (27, 19),
    49: (26, 19),
    50: (25, 19),
    51: (24, 19),
    52: (23, 19),
    53: (22, 19),
    54: (21, 19),
    55: (20, 19),
    56: (19, 19),
    57: (19, 20),
    58: (19, 21),
    59: (19, 22),
    60: (19, 23),
    61: (19, 24),
    62: (19, 25),
    63: (19, 26),
    64: (19, 27),
    65: (18, 27),
    66: (17, 27),
    67: (16, 27),
    68: (15, 27),
    69: (14, 27),
    70: (13, 27),
    71: (12, 27),
    72: (11, 27),
    73: (11, 26),
    74: (11, 25),
    75: (11, 24),
    76: (11, 23),
    77: (11, 22),
    78: (11, 21),
    79: (11, 20),
    80: (11, 19),
    81: (10, 19),
    82: (9, 19),
    83: (8, 19),
    84: (7, 19),
    85: (6, 19),
    86: (5, 19),
    87: (4, 19),
    88: (3, 19),
    89: (3, 18),
    90: (3, 17),
    91: (3, 16),
    92: (3, 15),
    93: (4, 15),
    94: (5, 15),
    95: (6, 15),
    96: (7, 15),
    97: (15, 4),
    98: (15, 5),
    99: (15, 6),
    100: (15, 7),
    101: (26, 15),
    102: (25, 15),
    103: (24, 15),
    104: (23, 15),
    105: (15, 26),
    106: (15, 25),
    107: (15, 24),
    108: (15, 23),
    109: (3, 14),
    110: (3, 13),
    111: (3, 12),
    112: (3, 11)
}

# Tạo list vị trí có thể đặt sao
available_positions = []
for pos, coord in positions.items():
    if pos not in restricted_positions:
        available_positions.append(coord)

# Chọn ngẫu nhiên 8 vị trí để đặt sao
star_positions = random.sample(available_positions, 15)

# Tạo list chứa các đối tượng Star
stars = pygame.sprite.Group()
for pos in star_positions:
    star = Star(pos)
    stars.add(star)