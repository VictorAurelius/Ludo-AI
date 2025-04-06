import pygame
from pygame.locals import *
from Players import *
import time
import os
import pytmx
from pytmx.util_pygame import load_pygame

TILE_SIZE = 25 
MAP_WIDTH = 29
MAP_HEIGHT = 29

# Dictionary lưu vị trí các quân về đích
RED_FINISH_POSITIONS = {
    1: (9, 13),
    2: (10, 13),
    3: (12, 13),
    4: (13, 13)
}

BLUE_FINISH_POSITIONS = {
    1: (13, 9),
    2: (14, 9),
    3: (16, 9),
    4: (17, 9)
}

YELLOW_FINISH_POSITIONS = {
    1: (17, 13),
    2: (18, 13),
    3: (20, 13),
    4: (21, 13)
}

GREEN_FINISH_POSITIONS = {
    1: (13, 17),
    2: (14, 17),
    3: (16, 17),
    4: (17, 17)
}

# Hàm helper để scale vị trí về đích
def scale_finish_dict(finish_dict, scale):
    return {k: ((v[0] * scale) - 13, (v[1] * scale) - 13) for k, v in finish_dict.items()}

# Tạo hàm để load animation từ Tiled
def load_animations_from_tileset(tileset_path):
    animations = {}
    if os.path.exists(tileset_path):
        try:
            import xml.etree.ElementTree as ET
            
            # Đọc file tsx bằng ElementTree thay vì pytmx
            tree = ET.parse(tileset_path)
            root = tree.getroot()
            
            # Lấy thông tin cơ bản của tileset
            tilewidth = int(root.get('tilewidth', 0))
            tileheight = int(root.get('tileheight', 0))
            
            # Lấy đường dẫn tới file ảnh
            image_element = root.find('image')
            if image_element is not None:
                image_path = image_element.get('source')
                # Chuẩn hóa đường dẫn tới file ảnh
                base_dir = os.path.dirname(tileset_path)
                image_path = os.path.normpath(os.path.join(base_dir, image_path))
                
                # Tải spritesheet nếu file tồn tại
                if os.path.exists(image_path):
                    spritesheet = pygame.image.load(image_path).convert_alpha()
                    
                    # Lấy các animation từ các phần tử tile
                    for tile_elem in root.findall('tile'):
                        tile_id = int(tile_elem.get('id', 0))
                        
                        # Tìm thuộc tính animation_name
                        animation_name = None
                        prop_elem = tile_elem.find('properties/property[@name="animation_name"]')
                        if prop_elem is not None:
                            animation_name = prop_elem.get('value')
                        
                        if animation_name:
                            # Tìm các frame của animation
                            animation_elem = tile_elem.find('animation')
                            if animation_elem is not None:
                                animation_frames = []
                                
                                for frame_elem in animation_elem.findall('frame'):
                                    frame_id = int(frame_elem.get('tileid', 0))
                                    duration = int(frame_elem.get('duration', 100))
                                    
                                    # Tính vị trí của frame trong spritesheet
                                    columns = int(root.get('columns', 1))
                                    frame_x = (frame_id % columns) * tilewidth
                                    frame_y = (frame_id // columns) * tileheight
                                    
                                    # Cắt frame từ spritesheet
                                    frame_image = pygame.Surface((tilewidth, tileheight), pygame.SRCALPHA)
                                    frame_image.blit(spritesheet, (0, 0), pygame.Rect(frame_x, frame_y, tilewidth, tileheight))
                                    
                                    # Thêm frame vào animation
                                    animation_frames.append((frame_image, duration))
                                
                                # Lưu animation
                                if animation_frames:
                                    animations[animation_name] = animation_frames
        except Exception as e:
            print(f"Loi khi tai animation tu file tsx: {e}")
    
    return animations

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
        # Thêm biến để xử lý teleport
        self.teleporting = False
        self.teleport_phase = None  # "starting" hoặc "end"
        self.teleport_target = None  # Vị trí đích khi teleport
        #if this object is the first pawn of the player it belongs to, then it is set to be the active pawn upon object initialization
        if self.number == 1:
            self.activepawn = True
        # Thêm các thuộc tính cho animation
        self.is_move = False
        self.animation_path = []
        self.animation_index = 0
        self.animation_speed = 1  # Số frame để đi qua 1 ô
        
        # Thuộc tính cho stand_left animation
        self.current_state = "stand_left"  # Trạng thái hiện tại (stand_left, walk, attack...)
        self.frame_index = 0  # Frame hiện tại trong animation
        self.last_frame_update = pygame.time.get_ticks()
        self.animations = {}  # Dictionary chứa các animation
        
        # Thời gian giữa mỗi chuyển frame
        self.frame_delay = 100  # Milliseconds
        
        self.has_reached_finish = False  # Đánh dấu quân đã về đích chưa
        self.finish_position = None  # Vị trí cuối cùng sau khi về đích


    #pawn movement method
    def move(self, dice, statekeeper):
        StateKpr = statekeeper
        # add the dice roll value to the pawn's counter
        old_counter = self.counter
        self.counter += dice
        if self.counter == 96 or self.counter == 97:
            print('PawnKing')
            self.kingPawn += 1
            
            # Xác định màu của quân cờ để lấy vị trí đích tương ứng
            player_color = None
            for player in StateKpr.players:
                if self in player.pawnlist:
                    player_color = player.color
                    # Tăng số quân về đích của player, nhưng chỉ tăng một lần
                    if not self.has_reached_finish:
                        player.pawns_home += 1
                    break
            
            # Lấy vị trí đích dựa vào số thứ tự và màu của quân
            if player_color == "Red":
                finish_pos_dict = scale_finish_dict(RED_FINISH_POSITIONS, TILE_SIZE)
            elif player_color == "Blue":
                finish_pos_dict = scale_finish_dict(BLUE_FINISH_POSITIONS, TILE_SIZE)
            elif player_color == "Yellow":
                finish_pos_dict = scale_finish_dict(YELLOW_FINISH_POSITIONS, TILE_SIZE)
            elif player_color == "Green":
                finish_pos_dict = scale_finish_dict(GREEN_FINISH_POSITIONS, TILE_SIZE)
            else:
                finish_pos_dict = None
            
            if finish_pos_dict and self.number in finish_pos_dict:
                # Lấy vị trí đích từ dictionary
                self.finish_position = finish_pos_dict[self.number]
                
                # Khởi tạo animation path và đánh dấu đã về đích
                self.setup_animation_path(old_counter, self.counter)
                self.is_move = True
                self.animation_index = 0
                self.has_reached_finish = True  # Đánh dấu quân đã về đích
            else:
                # Nếu không có vị trí đích cụ thể, sử dụng vị trí mặc định
                self.setup_animation_path(old_counter, self.counter)
                self.is_move = True
                self.animation_index = 0
            
            # Đặt trạng thái không active và là king
            self.activepawn = False
            self.king = True
            
        elif self.counter > 97:
            self.counter -= dice
        
        # Khởi tạo animation path thay vì di chuyển trực tiếp
        self.setup_animation_path(old_counter, self.counter)
        self.is_move = True
        self.animation_index = 0
        self.last_frame_update = pygame.time.get_ticks()  # Reset thời gian frame
        
        # Đảm bảo statuekeeper được cập nhật
        StateKpr.reset_counterlist_status()
        
    def start_teleport(self, target_pos):
        """Bắt đầu quá trình dịch chuyển"""
        self.teleporting = True
        self.teleport_phase = "starting"
        self.teleport_target = target_pos
        self.current_state = "teleport_starting"
        self.frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()
        # Xác định hướng để quay về sau khi teleport
        current_x = self.rect.center[0]
        target_x = target_pos[0]
        
        # Lưu hướng để sau khi teleport quân sẽ đứng yên với hướng này
        self.teleport_direction = "right" if target_x > current_x else "left"
        
        
    def setup_animation_path(self, start_pos, end_pos):
        """Tạo đường đi mượt mà giữa các ô"""
        self.animation_path = []
        self.direction_changes = []  # Lưu hướng di chuyển cho từng đoạn
        
        # Tạo điểm trung gian giữa các ô
        steps_per_square = 10  # Số bước trung gian giữa mỗi ô
        
        prev_direction = None  # Hướng di chuyển trước đó
        # Lấy hướng hiện tại của quân trước khi di chuyển
        if hasattr(self, 'current_state') and self.current_state:
            # Trích xuất hướng từ current_state (stand_left, walk_right, etc.)
            parts = self.current_state.split('_')
            if len(parts) > 1:
                prev_direction = parts[-1]  # Lấy phần cuối (left/right)
            else:
                prev_direction = "left"  # Mặc định
        else:
            prev_direction = "left"  # Mặc định nếu không xác định được
        
        # Lưu hướng cuối cùng của quân trước khi di chuyển
        last_known_horizontal_direction = prev_direction
        
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
            
            # Xác định hướng di chuyển
            dx = target_pos[0] - current_pos[0]
            dy = target_pos[1] - current_pos[1]
            
            # Xác định hướng chính: left, right hoặc giữ nguyên hướng
            if abs(dx) > abs(dy):  # Di chuyển theo chiều ngang nhiều hơn
                direction = "right" if dx > 0 else "left"
                # Cập nhật hướng ngang đã biết
                last_known_horizontal_direction = direction
            else:
                # Khi di chuyển theo chiều dọc, giữ nguyên hướng ngang cuối cùng đã biết
                direction = last_known_horizontal_direction
            
            # Tạo các bước di chuyển trung gian
            for step in range(1, steps_per_square + 1):
                # Tính toán vị trí trung gian bằng nội suy tuyến tính
                progress = step / steps_per_square
                x = current_pos[0] + (target_pos[0] - current_pos[0]) * progress
                y = current_pos[1] + (target_pos[1] - current_pos[1]) * progress
                
                self.animation_path.append((x, y))
                self.direction_changes.append(direction)
        # Cập nhật trạng thái ban đầu dựa trên hướng đầu tiên
        if self.direction_changes:
            first_direction = self.direction_changes[0]
            self.current_state = f"walk_{first_direction}"
            
    def update_animation(self):
        if self.teleporting:
            
            current_time = pygame.time.get_ticks()
            
            # Kiểm tra xem đã đến lúc cập nhật frame chưa
            if current_time - self.last_frame_update > self.frame_delay:
                # Xác định số frame trong animation hiện tại
                animation_key = f"teleport_{self.teleport_phase}"
                
                if animation_key in self.animations:
                    num_frames = len(self.animations[animation_key])
                    
                    # Cập nhật frame index
                    self.frame_index += 1
                    
                    # Kiểm tra kết thúc animation
                    if self.frame_index >= num_frames:
                        # Nếu đang trong phase "starting", chuyển sang phase "end"
                        if self.teleport_phase == "starting":
                            # Di chuyển tới vị trí đích
                            self.rect.center = self.teleport_target
                            self.teleport_phase = "end"
                            self.current_state = "teleport_end"
                            self.frame_index = 0
                        else:  # Kết thúc teleport
                            self.teleporting = False
                            self.teleport_phase = None
                            # Sử dụng hướng đã lưu từ trước
                            if hasattr(self, 'teleport_direction'):
                                self.current_state = f"stand_{self.teleport_direction}"
                            else:
                                self.current_state = "stand_left"  # Fallback
                            self.frame_index = 0
                            self.just_finished_animation = True  # Đánh dấu đã hoàn thành animation
                    else:
                        # Cập nhật surface hiện tại
                        frame_data = self.animations[animation_key][self.frame_index % num_frames]
                        self.surf = frame_data[0]
                        
                        # Đặt lại colorkey và rect
                        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
                        old_center = self.rect.center
                        self.rect = self.surf.get_rect(center=old_center)
                    
                    # Cập nhật thời gian frame cuối
                    self.last_frame_update = current_time
        # Di chuyển quân cờ theo animation path
        elif self.is_move:
            if self.animation_index < len(self.animation_path):
                # Chỉ cập nhật vị trí mỗi animation_speed frame
                current_time = pygame.time.get_ticks()
                
                # Thêm biến để theo dõi thời gian cho mỗi quân cờ
                if not hasattr(self, 'last_animation_time'):
                    self.last_animation_time = current_time
                    
                # Chỉ di chuyển khi đã qua đủ thời gian
                if current_time - self.last_animation_time > self.animation_speed * 10:  # Nhân với 10 để chuyển đổi thành ms
                    # Cập nhật hướng di chuyển nếu cần
                    if self.animation_index < len(self.direction_changes):
                        direction = self.direction_changes[self.animation_index]
                        walk_state = f"walk_{direction}"
                        
                        # Chỉ cập nhật nếu hướng thay đổi để tránh reset animation
                        if self.current_state != walk_state:
                            self.current_state = walk_state
                            self.frame_index = 0
                    
                    self.rect.center = self.animation_path[self.animation_index]
                    self.animation_index += 1
                    self.last_animation_time = current_time
                    
                # Cập nhật animation walk trong khi di chuyển
                if self.current_state in self.animations and self.animations[self.current_state]:
                    # Chỉ cập nhật animation nếu đã qua đủ thời gian frame_delay
                    if current_time - self.last_frame_update > self.frame_delay:
                        # Lấy số frame trong animation hiện tại
                        num_frames = len(self.animations[self.current_state])
                        
                        # Cập nhật frame index
                        self.frame_index = (self.frame_index + 1) % num_frames
                        
                        # Cập nhật surface hiện tại
                        frame_data = self.animations[self.current_state][self.frame_index]
                        original_surf = self.surf  # Lưu surface hiện tại
                        self.surf = frame_data[0]  # frame_data[0] là surface, frame_data[1] là duration
                        
                        # Đặt lại colorkey và rect
                        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
                        old_center = self.rect.center
                        self.rect = self.surf.get_rect(center=old_center)
                        
                        # Cập nhật thời gian frame cuối
                        self.last_frame_update = current_time
            else:
                self.is_move = False
                # Kiểm tra nếu quân đã về đích và có vị trí đích cuối cùng
                if self.has_reached_finish and self.finish_position:
                    # Dùng teleport để di chuyển đến vị trí đích cuối cùng
                    self.start_teleport(self.finish_position)
                    # Reset flag để không teleport lại
                    self.has_reached_finish = False
                else:
                    # Xử lý hoàn thành animation bình thường
                    self.just_finished_animation = True  # Đánh dấu vừa hoàn thành animation
                    
                    # Chuyển về trạng thái đứng yên sau khi di chuyển
                    if hasattr(self, 'direction_changes') and self.direction_changes:
                        last_direction = self.direction_changes[-1]
                        self.current_state = f"stand_{last_direction}"
                    else:
                        self.current_state = "stand_left"  # Mặc định quay trái
                    self.frame_index = 0
        elif not self.is_move and self.current_state in self.animations and self.animations[self.current_state]:
            current_time = pygame.time.get_ticks()
            
            # Kiểm tra xem đã đến lúc cập nhật frame chưa
            if current_time - self.last_frame_update > self.frame_delay:
                # Lấy số frame trong animation hiện tại
                num_frames = len(self.animations[self.current_state])
                
                # Cập nhật frame index
                self.frame_index = (self.frame_index + 1) % num_frames
                
                # Cập nhật surface hiện tại
                frame_data = self.animations[self.current_state][self.frame_index]
                self.surf = frame_data[0]  # frame_data[0] là surface, frame_data[1] là duration
                
                # Đặt lại colorkey và rect
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)
                old_center = self.rect.center
                self.rect = self.surf.get_rect(center=old_center)
                
                # Cập nhật thời gian frame cuối
                self.last_frame_update = current_time
                
    
    def load_animations(self, tileset_path):
        """Tải animations từ file tileset"""
        self.animations = load_animations_from_tileset(tileset_path)
                
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

# Đường dẫn đến các file tileset animation
blue_anim_path = 'mapfinal/WBlue_Animation.tsx'
red_anim_path = 'mapfinal/WBlue_Animation.tsx'  # Giả sử có file này
yellow_anim_path = 'mapfinal/WBlue_Animation.tsx'  # Giả sử có file này
green_anim_path = 'mapfinal/WBlue_Animation.tsx'  # Giả sử có file này

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
    rp.load_animations(red_anim_path)
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
# Tải animations cho các quân cờ màu xanh
for bp in BluePawnList:
    bp.load_animations(blue_anim_path)
    allSprites.add(bp)
    bluePawn.add(bp)
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
# Tải animations cho các quân cờ màu vàng
for yp in YellowPawnList:
    yp.load_animations(yellow_anim_path)
    allSprites.add(yp)
    yellowPawn.add(yp)
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
# Tải animations cho các quân cờ màu xanh lá
for gp in GreenPawnList:
    gp.load_animations(green_anim_path)
    allSprites.add(gp)
    greenPawn.add(gp)
print(len(greenPawn))
