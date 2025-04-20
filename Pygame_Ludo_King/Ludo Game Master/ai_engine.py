import copy
import random
import numpy as np
from Players import Player
from Pawns import Pawn
from Stars import Star
class LudoAI:
    def __init__(self, statekeeper):
        self.statekeeper = statekeeper
        self.MAX_DEPTH = 2  # Reduced depth for better performance
        # Trọng số cho các yếu tố đánh giá
        self.weights = {
            'progress': 3.0,         # Tiến độ cơ bản
            'finish': 200.0,         # Về đích
            'near_finish': [80, 50, 30],  # Gần đích (90+, 80+, 70+)
            'star_position': 25.0,   # Đứng ở vị trí sao
            'danger_position': -40.0,  # Vị trí nguy hiểm (13 từ đích)
            'enemy_threat': -25.0,   # Bị đe dọa
            'capture_opportunity': 20.0,  # Cơ hội ăn quân
            'board_presence': [-50, -20, 40, 20],  # 0, 1, 2-3, 4 quân
            'eating': 50.0,          # Ăn quân
            'star_move': 30.0,       # Di chuyển đến sao
            'danger_range': -20.0,   # Trong tầm ăn quân
            'difficult_goal': [-100, -80, -60, -40],  # Vị trí khó về đích
            'exact_goal': [-100, -80, -60, -40],      # Cần roll chính xác
            'starting': [120, 100, 80, 60]           # Ưu tiên xuất quân
        }

    def evaluate_state(self, player):
        """
        Hàm đánh giá trạng thái game sử dụng trọng số
        """
        score = 0
        star_positions = [5, 18, 31, 44, 57, 70, 83]
        
        # 1. Đánh giá tiến độ và vị trí của quân
        pawns_on_board = 0
        for pawn in player.pawnlist:
            if pawn.king:
                # Quân về đích được nhiều điểm nhất
                score += self.weights['finish']
                continue
                
            if pawn.counter > 0:
                pawns_on_board += 1
                # Điểm cơ bản cho khoảng cách đã đi
                score += pawn.counter * self.weights['progress']
                
                # Thưởng cho quân gần đích
                if pawn.counter >= 90:
                    score += self.weights['near_finish'][0]
                elif pawn.counter >= 80:
                    score += self.weights['near_finish'][1]
                elif pawn.counter >= 70:
                    score += self.weights['near_finish'][2]
                    
                # Thưởng cho quân ở vị trí sao
                if pawn.counter in star_positions:
                    score += self.weights['star_position']
                    
                # Phạt cho vị trí nguy hiểm (13 bước từ đích)
                if 97 - pawn.counter == 13:
                    score += self.weights['danger_position']
        
        # 2. Đánh giá vị thế chiến thuật
        enemy_threats = 0  # Số quân đối thủ có thể ăn quân ta
        our_threats = 0    # Số quân ta có thể ăn quân đối thủ
        
        for other_player in self.statekeeper.players:
            if other_player != player:
                for enemy_pawn in other_player.pawnlist:
                    if not enemy_pawn.king:
                        for own_pawn in player.pawnlist:
                            if not own_pawn.king and own_pawn.counter > 0:
                                distance = abs(own_pawn.counter - enemy_pawn.counter)
                                # Trong tầm ăn quân (1-6 bước)
                                if 1 <= distance <= 6:
                                    if enemy_pawn.counter > own_pawn.counter:
                                        enemy_threats += 1
                                    else:
                                        our_threats += 1
        
        # Cộng/trừ điểm dựa trên các mối đe dọa
        score += enemy_threats * self.weights['enemy_threat']
        score += our_threats * self.weights['capture_opportunity']
        
        # 3. Đánh giá vị thế tổng thể
        # Thưởng cho việc có nhiều quân trên bàn (2-3 quân là tốt nhất)
        if pawns_on_board == 0:
            score += self.weights['board_presence'][0]
        elif pawns_on_board == 1:
            score += self.weights['board_presence'][1]
        elif pawns_on_board == 2 or pawns_on_board == 3:
            score += self.weights['board_presence'][2]
        else:
            score += self.weights['board_presence'][3]
            
        return score

    def get_possible_moves(self, player, dice_roll):
        """Generate all possible moves for the current state"""
        possible_moves = []
        
        # Xét từng quân của người chơi
        for pawn in player.pawnlist:
            # Trường hợp 1: Quân trong chuồng và tổng xúc xắc >= 10
            if pawn.counter == 0 and dice_roll >= 10:
                # Kiểm tra vị trí xuất phát có quân cùng màu không
                blocked = False
                start_pos = pawn.dict[1]
                for other_pawn in player.pawnlist:
                    if other_pawn != pawn and other_pawn.rect.center == start_pos:
                        blocked = True
                        break
                
                if not blocked:
                    possible_moves.append(("move_out", pawn))
            
            # Trường hợp 2: Quân đã trên bàn
            elif pawn.counter > 0 and not pawn.king:
                # Kiểm tra không vượt quá đích
                if pawn.counter + dice_roll <= 97:
                    # Kiểm tra vị trí đích không bị chặn bởi quân cùng màu
                    blocked = False
                    target_pos = pawn.dict[pawn.counter + dice_roll]
                    for other_pawn in player.pawnlist:
                        if other_pawn != pawn and other_pawn.rect.center == target_pos:
                            blocked = True
                            break
                    
                    if not blocked:
                        # Kiểm tra có ăn được quân đối thủ không
                        can_capture = False
                        for other_player in self.statekeeper.players:
                            if other_player != player:
                                for enemy_pawn in other_player.pawnlist:
                                    if (enemy_pawn.rect.center == target_pos and 
                                        enemy_pawn.counter > 0 and
                                        not enemy_pawn.king):
                                        can_capture = True
                                        break
                        
                        # Kiểm tra có đi vào ô sao không
                        # star_positions = [5, 18, 31, 44, 57, 70, 83]
                        on_star = (pawn.counter + dice_roll) in Star.star_positions
                        
                        # Tạo nước đi với metadata
                        move_data = {
                            "target_position": pawn.counter + dice_roll,
                            "can_capture": can_capture,
                            "on_star": on_star,
                            "distance_to_goal": 97 - (pawn.counter + dice_roll)
                        }
                        
                        possible_moves.append(("move", pawn, move_data))
        
        return possible_moves

    def evaluate_move(self, player, move, dice_roll):
        """Đánh giá một nước đi cụ thể"""
        if not move:
            return float('-inf')
            
        move_type = move[0]
        pawn = move[1]
        score = 0
        
        # Đếm số quân đang active trên bàn (không tính quân đã về đích)
        active_pawns = sum(1 for p in player.pawnlist if p.counter > 0 and not p.king)
        
        if move_type == "move":
            move_data = move[2]
            new_pos = move_data["target_position"]
            score += new_pos * self.weights['progress']  # Càng gần đích càng tốt
            
            # Ăn quân
            if move_data["can_capture"]:
                score += self.weights['eating']
            
            # Vị trí sao
            if move_data["on_star"]:
                score += self.weights['star_move']
                
            # Tránh đi vào vị trí nguy hiểm
            for other_player in self.statekeeper.players:
                if other_player != player:
                    for enemy_pawn in other_player.pawnlist:
                        if not enemy_pawn.king:
                            distance = abs(new_pos - enemy_pawn.counter)
                            if 1 <= distance <= 6:  # Trong tầm ăn quân
                                score += self.weights['danger_range']
                                
            # Xử lý các vị trí khó về đích khi có nhiều hơn 1 quân trên bàn
            if active_pawns > 1:
                distance_to_goal = move_data["distance_to_goal"]
                
                # 1. Khoảng cách 10-13 bước
                if distance_to_goal == 13 and dice_roll in (9, 10, 11, 12):
                    score += self.weights['difficult_goal'][0]
                elif distance_to_goal == 12 and dice_roll in (9, 10, 11):
                    score += self.weights['difficult_goal'][1]
                elif distance_to_goal == 11 and dice_roll in (9, 10):
                    score += self.weights['difficult_goal'][2]
                elif distance_to_goal == 10 and dice_roll == 9:
                    score += self.weights['difficult_goal'][3]
                    
                # 2. Khoảng cách 1-4 bước (cần roll số chính xác)
                elif 1 <= distance_to_goal <= 4:
                    index = min(distance_to_goal - 1, 3)  # 0-based index
                    score += self.weights['exact_goal'][index]
            
        else:  # move_out
            index = min(active_pawns, 3)  # Giới hạn đến index 3
            score += self.weights['starting'][index]
            
        return score

    def get_best_move(self, player, dice_roll):
        """Tìm nước đi tốt nhất dựa trên đánh giá từng nước đi"""
        possible_moves = self.get_possible_moves(player, dice_roll)
        
        if not possible_moves:
            return None
            
        # Áp dụng nhiễu ngẫu nhiên cho các quyết định
        exploration_factor = 0.1
        
        # Đánh giá từng nước đi và thêm nhiễu ngẫu nhiên
        rated_moves = []
        for move in possible_moves:
            base_score = self.evaluate_move(player, move, dice_roll)
            noise = np.random.normal(0, exploration_factor * abs(base_score) if base_score != 0 else 0.1)
            final_score = base_score + noise
            rated_moves.append((move, final_score))
            
            # Debug info
            move_desc = f"xuất chuồng" if move[0] == "move_out" else f"di chuyển từ {move[1].counter} đến {move[2]['target_position']}"
            print(f"Nước đi: {move_desc} -> điểm: {base_score:.2f} (+ nhiễu {noise:.2f}) = {final_score:.2f}")
        
        # Chọn nước đi tốt nhất
        best_move = max(rated_moves, key=lambda x: x[1])[0]
        
        # In thông tin về nước đi được chọn
        if best_move[0] == "move":
            move_data = best_move[2]
            move_desc = f"di chuyển quân từ {best_move[1].counter} đến {move_data['target_position']}"
            capture_info = " (ăn quân)" if move_data["can_capture"] else ""
            star_info = " (đến ô sao)" if move_data["on_star"] else ""
            print(f"AI chọn {move_desc}{capture_info}{star_info}")
        else:
            print(f"AI chọn xuất quân từ chuồng")
        
        return best_move

    # Các hàm hỗ trợ phục vụ minimax
    def _save_state(self, player, pawn):
        """Save complete game state for accurate state tracking"""
        state = {
            'player_state': {
                'pawns': player.pawns,
                'pawns_home': player.pawns_home,
                'active': player.active,
                'turn': player.turn,
                'dice1': player.dice1,
                'dice2': player.dice2,
                'times_kicked': player.times_kicked
            },
            'pawn_states': {}
        }
        
        # Save states for all pawns
        for p in player.pawnlist:
            state['pawn_states'][id(p)] = {
                'counter': p.counter,
                'active': p.activepawn,
                'king': p.king,
                'rect': p.rect.copy(),
                'just_moved_out': getattr(p, 'just_moved_out', False)
            }
            
        return state

    def _restore_state(self, player, pawn, old_state):
        """Restore complete game state accurately"""
        # Restore player state
        player_state = old_state['player_state']
        player.pawns = player_state['pawns']
        player.pawns_home = player_state['pawns_home']
        player.active = player_state['active']
        player.turn = player_state['turn']
        player.dice1 = player_state['dice1']
        player.dice2 = player_state['dice2']
        player.times_kicked = player_state['times_kicked']
        
        # Restore all pawns
        for p in player.pawnlist:
            if id(p) in old_state['pawn_states']:
                pawn_state = old_state['pawn_states'][id(p)]
                p.counter = pawn_state['counter']
                p.activepawn = pawn_state['active']
                p.king = pawn_state['king']
                p.rect = pawn_state['rect'].copy()
                p.just_moved_out = pawn_state['just_moved_out']