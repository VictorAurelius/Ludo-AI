import pygame
from pygame.locals import *
from Players import *
import time

TILE_SIZE = 25 
MAP_WIDTH = 29
MAP_HEIGHT = 29



# Pawn Constructor
class Pawn(pygame.sprite.Sprite):
    def __init__(self, surf, dict, startpos, number):
        super(Pawn, self).__init__()
        self.surf = surf
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        # counter attribute
        self.counter = 0
        self.dict = dict
        # represents which pawn this is
        self.number = number
        self.startpos = startpos
        self.rect = self.surf.get_rect(center=self.startpos)
        # represents the pawns active status
        self.activepawn = False
        # is the pawn a king? not fully implemented yet
        self.king = False
        self.kingPawn = 0
        #if this object is the first pawn of the player it belongs to, then it is set to be the active pawn upon object initialization
        if self.number == 1:
            self.activepawn = True
        # Thêm các thuộc tính cho animation
        self.is_animating = False
        self.animation_path = []
        self.animation_index = 0
        self.animation_speed = 1  # Số frame để đi qua 1 ô

    #pawn movement method
    def move(self, dice, statekeeper):
        StateKpr = statekeeper
        # add the dice roll value to the pawn's counter
        old_counter = self.counter
        self.counter += dice
        if self.counter == 96 or self.counter == 97:
            print('PawnKing')
            self.kingPawn += 1
            #pawn state is set to inactive
            self.activepawn = False
            #this attribute is not fully implemented
            self.king = True
        elif self.counter > 97:
            self.counter -= dice
        # self.rect.center = self.dict[self.counter]  
        # Khởi tạo animation path thay vì di chuyển trực tiếp
        self.setup_animation_path(old_counter, self.counter)
        self.is_animating = True
        self.animation_index = 0
        
        # Đảm bảo statuekeeper được cập nhật
        StateKpr.reset_counterlist_status()
        
    def setup_animation_path(self, start_pos, end_pos):
        """Tạo đường đi mượt mà giữa các ô"""
        self.animation_path = []
        
        # Tạo điểm trung gian giữa các ô
        steps_per_square = 10  # Số bước trung gian giữa mỗi ô
        
        for pos in range(start_pos + 1, end_pos + 1):
            # Vị trí hiện tại
            if pos == start_pos + 1:
                # Nếu là ô đầu tiên, lấy vị trí hiện tại của quân cờ làm điểm bắt đầu
                current_pos = self.rect.center
            else:
                # Nếu không phải ô đầu tiên, lấy vị trí ô trước đó
                current_pos = self.dict[pos-1]
            
            # Vị trí đích (ô tiếp theo)
            target_pos = self.dict[pos]
            
            # Tạo các bước di chuyển trung gian
            for step in range(1, steps_per_square + 1):
                # Tính toán vị trí trung gian bằng nội suy tuyến tính
                progress = step / steps_per_square
                x = current_pos[0] + (target_pos[0] - current_pos[0]) * progress
                y = current_pos[1] + (target_pos[1] - current_pos[1]) * progress
                
                self.animation_path.append((x, y))
            
    def update_animation(self):
        # Di chuyển quân cờ theo animation path
        if self.is_animating:
            if self.animation_index < len(self.animation_path):
                # Chỉ cập nhật vị trí mỗi animation_speed frame
                current_time = pygame.time.get_ticks()
                
                # Thêm biến để theo dõi thời gian cho mỗi quân cờ
                if not hasattr(self, 'last_animation_time'):
                    self.last_animation_time = current_time
                    
                # Chỉ di chuyển khi đã qua đủ thời gian
                if current_time - self.last_animation_time > self.animation_speed * 10:  # Nhân với 10 để chuyển đổi thành ms
                    self.rect.center = self.animation_path[self.animation_index]
                    self.animation_index += 1
                    self.last_animation_time = current_time
            else:
                self.is_animating = False
                self.just_finished_animation = True  # Đánh dấu vừa hoàn thành animation
                
    #update the pawn status variables to represent the current status of the pawns.
    def update_pawn_state(self, activeplayer, nextplayer):        
        ActPlayer = activeplayer
        NxtPlayer = nextplayer      
        #check which pawn this object instance refers to because it is made active by the player move method by calling this method
        if self.number == 1:
            #change the next pawn to active (Note: the index starts at 0 so index 1 is the second pawn)
            ActPlayer.pawnlist[1].activepawn = True
            # set the pawn of the next player to active 
            self.set_next_player_pawn(NxtPlayer)
        elif self.number == 2:
            ActPlayer.pawnlist[2].activepawn = True
            self.set_next_player_pawn(NxtPlayer)
        elif self.number == 3:
            ActPlayer.pawnlist[3].activepawn = True
            self.set_next_player_pawn(NxtPlayer)
        elif self.number == 4:
            ActPlayer.pawnlist[0].activepawn = True
            self.set_next_player_pawn(NxtPlayer)
            
    #determine and set the pawn status of the next player in preperation for their turn           
    def set_next_player_pawn(self, nextplayer):
        # for the pawns belonging to the next player
        for pawn in nextplayer.pawnlist:            
            #find active Pawn            
            if pawn.activepawn:
                #deactivate it
                pawn.activepawn = False
                #identify pawn that was deactivated
                if pawn.number == 1:                 
                    #activate the next pawn to be active
                    nextplayer.pawnlist[1].activepawn = True
                elif pawn.number == 2:               
                    nextplayer.pawnlist[2].activepawn = True
                elif pawn.number == 3:
                    nextplayer.pawnlist[3].activepawn = True
                elif pawn.number == 4:              
                    nextplayer.pawnlist[0].activepawn = True
                #loop can stop because the next player pawn is set because the active pawn was found
                break
            #else keep looping until active pawn is found
            else:
                continue
            
    

# ALL GROUPS OF SPRITES
redPawn = pygame.sprite.Group()
bluePawn = pygame.sprite.Group()
yellowPawn = pygame.sprite.Group()
greenPawn = pygame.sprite.Group()
allSprites = pygame.sprite.Group()

# Hàm helper để chuyển đổi dictionary
def scale_dict(dict_pos, scale):
    return {k: ((v[0] * scale) - 13, (v[1] * scale) - 13) for k, v in dict_pos.items()}

# RED PAWNS
redDICT = {
    1: (4, 11),   # Điểm xuất phát đỏ (87)
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
    97: (7, 15)}
# PNG
redpng = pygame.image.load('assets_ver1/assets_nhat/Red/Warrior_Red1.png')

redp1 = Pawn(redpng, scale_dict(redDICT, TILE_SIZE), (- 13 + TILE_SIZE * 5, 4 * TILE_SIZE - 13), 1 )
redp2 = Pawn(redpng, scale_dict(redDICT, TILE_SIZE), (- 13 + TILE_SIZE * 8, 4 * TILE_SIZE - 13), 2)
redp3 = Pawn(redpng, scale_dict(redDICT, TILE_SIZE), (- 13 + TILE_SIZE * 5, 7 * TILE_SIZE - 13), 3)
redp4 = Pawn(redpng, scale_dict(redDICT, TILE_SIZE), (- 13 + TILE_SIZE * 8, 7 * TILE_SIZE - 13), 4)

RedPawnList = [redp1, redp2, redp3, redp4]
for rp in RedPawnList:
    allSprites.add(rp)
    redPawn.add(rp)
print(len(redPawn))

# BLUE PAWNS
blueDICT = {
    1: (19, 4),   # Điểm xuất phát xanh lá
    2: (19, 5),
    3: (19, 6),
    4: (19, 7),
    5: (19, 8),
    6: (19, 9),
    7: (19, 10),
    8: (19, 11),
    9: (20, 11),
    10: (21, 11),
    11: (22, 11),
    12: (23, 11),
    13: (24, 11),
    14: (25, 11),
    15: (26, 11),
    16: (27, 11),
    17: (27, 12),
    18: (27, 13),
    19: (27, 14),
    20: (27, 15),
    21: (27, 16),
    22: (27, 17),
    23: (27, 18),
    24: (27, 19),
    25: (26, 19),
    26: (25, 19),
    27: (24, 19),
    28: (23, 19),
    29: (22, 19),
    30: (21, 19),
    31: (20, 19),
    32: (19, 19),
    33: (19, 20),
    34: (19, 21),
    35: (19, 22),
    36: (19, 23),
    37: (19, 24),
    38: (19, 25),
    39: (19, 26),
    40: (19, 27),
    41: (18, 27),
    42: (17, 27),
    43: (16, 27),
    44: (15, 27),
    45: (14, 27),
    46: (13, 27),
    47: (12, 27),
    48: (11, 27),
    49: (11, 26),
    50: (11, 25),
    51: (11, 24),
    52: (11, 23),
    53: (11, 22),
    54: (11, 21),
    55: (11, 20),
    56: (11, 19),
    57: (10, 19),
    58: (9, 19),
    59: (8, 19),
    60: (7, 19),
    61: (6, 19),
    62: (5, 19),
    63: (4, 19),
    64: (3, 19),
    65: (3, 18),
    66: (3, 17),
    67: (3, 16),
    68: (3, 15),
    69: (3, 14),
    70: (3, 13),
    71: (3, 12),
    72: (3, 11),
    73: (4, 11),
    74: (5, 11),
    75: (6, 11),
    76: (7, 11),
    77: (8, 11),
    78: (9, 11),
    79: (10, 11),
    80: (11, 11),
    81: (11, 10),
    82: (11, 9),
    83: (11, 8),
    84: (11, 7),
    85: (11, 6),
    86: (11, 5),
    87: (11, 4),
    88: (11, 3),
    89: (12, 3),
    90: (13, 3),
    91: (14, 3),
    92: (15, 3),
    93: (15, 4),
    94: (15, 5),
    95: (15, 6),
    96: (15, 7),
    97: (15, 7)}

# PNG
bluepng = pygame.image.load('assets_ver1/assets_nhat/Blue/Warrior_Blue1.png')

bluep1 = Pawn(bluepng, scale_dict(blueDICT, TILE_SIZE), (- 13 + TILE_SIZE * 22, 4 * TILE_SIZE - 13), 1 )
bluep2 = Pawn(bluepng, scale_dict(blueDICT, TILE_SIZE), (- 13 + TILE_SIZE * 25, 4 * TILE_SIZE - 13), 2)
bluep3 = Pawn(bluepng, scale_dict(blueDICT, TILE_SIZE), (- 13 + TILE_SIZE * 22, 7 * TILE_SIZE - 13), 3)
bluep4 = Pawn(bluepng, scale_dict(blueDICT, TILE_SIZE), (- 13 + TILE_SIZE * 25, 7 * TILE_SIZE - 13), 4)

BluePawnList = [bluep1, bluep2, bluep3, bluep4]
for rp in BluePawnList:
    allSprites.add(rp)
    bluePawn.add(rp)
print(len(bluePawn))

# YELLOW PAWNS
yellowDICT = {
    1: (26, 19),  # Điểm xuất phát vàng
    2: (25, 19),
    3: (24, 19),
    4: (23, 19),
    5: (22, 19),
    6: (21, 19),
    7: (20, 19),
    8: (19, 19),
    9: (19, 20),
    10: (19, 21),
    11: (19, 22),
    12: (19, 23),
    13: (19, 24),
    14: (19, 25),
    15: (19, 26),
    16: (19, 27),
    17: (18, 27),
    18: (17, 27),
    19: (16, 27),
    20: (15, 27),
    21: (14, 27),
    22: (13, 27),
    23: (12, 27),
    24: (11, 27),
    25: (11, 26),
    26: (11, 25),
    27: (11, 24),
    28: (11, 23),
    29: (11, 22),
    30: (11, 21),
    31: (11, 20),
    32: (11, 19),
    33: (10, 19),
    34: (9, 19),
    35: (8, 19),
    36: (7, 19),
    37: (6, 19),
    38: (5, 19),
    39: (4, 19),
    40: (3, 19),
    41: (3, 18),
    42: (3, 17),
    43: (3, 16),
    44: (3, 15),
    45: (3, 14),
    46: (3, 13),
    47: (3, 12),
    48: (3, 11),
    49: (4, 11),
    50: (5, 11),
    51: (6, 11),
    52: (7, 11),
    53: (8, 11),
    54: (9, 11),
    55: (10, 11),
    56: (11, 11),
    57: (11, 10),
    58: (11, 9),
    59: (11, 8),
    60: (11, 7),
    61: (11, 6),
    62: (11, 5),
    63: (11, 4),
    64: (11, 3),
    65: (12, 3),
    66: (13, 3),
    67: (14, 3),
    68: (15, 3),
    69: (16, 3),
    70: (17, 3),
    71: (18, 3),
    72: (19, 3),
    73: (19, 4),
    74: (19, 5),
    75: (19, 6),
    76: (19, 7),
    77: (19, 8),
    78: (19, 9),
    79: (19, 10),
    80: (19, 11),
    81: (20, 11),
    82: (21, 11),
    83: (22, 11),
    84: (23, 11),
    85: (24, 11),
    86: (25, 11),
    87: (26, 11),
    88: (27, 11),
    89: (27, 12),
    90: (27, 13),
    91: (27, 14),
    92: (27, 15),
    93: (26, 15),
    94: (25, 15),
    95: (24, 15),
    96: (23, 15),
    97: (23, 15)}

# PNG
yellowpng = pygame.image.load('assets_ver1/assets_nhat/Yellow/Warrior_Yellow1.png')

yellowp1 = Pawn(yellowpng, scale_dict(yellowDICT, TILE_SIZE), (- 13 + TILE_SIZE * 22, 21 * TILE_SIZE - 13), 1 )
yellowp2 = Pawn(yellowpng, scale_dict(yellowDICT, TILE_SIZE), (- 13 + TILE_SIZE * 25, 21 * TILE_SIZE - 13), 2)
yellowp3 = Pawn(yellowpng, scale_dict(yellowDICT, TILE_SIZE), (- 13 + TILE_SIZE * 22, 24 * TILE_SIZE - 13), 3)
yellowp4 = Pawn(yellowpng, scale_dict(yellowDICT, TILE_SIZE), (- 13 + TILE_SIZE * 25, 24 * TILE_SIZE - 13), 4)

YellowPawnList = [yellowp1, yellowp2, yellowp3, yellowp4]
for rp in YellowPawnList:
    allSprites.add(rp)
    yellowPawn.add(rp)
print(len(yellowPawn))

# GREEN PAWNS
greenDICT = { 
    1: (11, 26),  # Điểm xuất phát xanh dương/tím
    2: (11, 25),
    3: (11, 24),
    4: (11, 23),
    5: (11, 22),
    6: (11, 21),
    7: (11, 20),
    8: (11, 19),
    9: (10, 19),
    10: (9, 19),
    11: (8, 19),
    12: (7, 19),
    13: (6, 19),
    14: (5, 19),
    15: (4, 19),
    16: (3, 19),
    17: (3, 18),
    18: (3, 17),
    19: (3, 16),
    20: (3, 15),
    21: (3, 14),
    22: (3, 13),
    23: (3, 12),
    24: (3, 11),
    25: (4, 11),
    26: (5, 11),
    27: (6, 11),
    28: (7, 11),
    29: (8, 11),
    30: (9, 11),
    31: (10, 11),
    32: (11, 11),
    33: (11, 10),
    34: (11, 9),
    35: (11, 8),
    36: (11, 7),
    37: (11, 6),
    38: (11, 5),
    39: (11, 4),
    40: (11, 3),
    41: (12, 3),
    42: (13, 3),
    43: (14, 3),
    44: (15, 3),
    45: (16, 3),
    46: (17, 3),
    47: (18, 3),
    48: (19, 3),
    49: (19, 4),
    50: (19, 5),
    51: (19, 6),
    52: (19, 7),
    53: (19, 8),
    54: (19, 9),
    55: (19, 10),
    56: (19, 11),
    57: (20, 11),
    58: (21, 11),
    59: (22, 11),
    60: (23, 11),
    61: (24, 11),
    62: (25, 11),
    63: (26, 11),
    64: (27, 11),
    65: (27, 12),
    66: (27, 13),
    67: (27, 14),
    68: (27, 15),
    69: (27, 16),
    70: (27, 17),
    71: (27, 18),
    72: (27, 19),
    73: (26, 19),
    74: (25, 19),
    75: (24, 19),
    76: (23, 19),
    77: (22, 19),
    78: (21, 19),
    79: (20, 19),
    80: (19, 19),
    81: (19, 20),
    82: (19, 21),
    83: (19, 22),
    84: (19, 23),
    85: (19, 24),
    86: (19, 25),
    87: (19, 26),
    88: (19, 27),
    89: (18, 27),
    90: (17, 27),
    91: (16, 27),
    92: (15, 27),
    93: (15, 26),
    94: (15, 25),
    95: (15, 24),
    96: (15, 23),
    97: (15, 23)}

# PNG
greenpng = pygame.image.load('assets_ver1/assets_nhat/Purple/Warrior_Purple1.png')

greenp1 = Pawn(greenpng, scale_dict(greenDICT, TILE_SIZE), (- 13 + TILE_SIZE * 5, 21 * TILE_SIZE - 13), 1 )
greenp2 = Pawn(greenpng, scale_dict(greenDICT, TILE_SIZE), (- 13 + TILE_SIZE * 8, 21 * TILE_SIZE - 13), 2)
greenp3 = Pawn(greenpng, scale_dict(greenDICT, TILE_SIZE), (- 13 + TILE_SIZE * 5, 24 * TILE_SIZE - 13), 3)
greenp4 = Pawn(greenpng, scale_dict(greenDICT, TILE_SIZE), (- 13 + TILE_SIZE * 8, 24 * TILE_SIZE - 13), 4)

GreenPawnList = [greenp1, greenp2, greenp3, greenp4]
for rp in GreenPawnList:
    allSprites.add(rp)
    greenPawn.add(rp)
print(len(greenPawn))
