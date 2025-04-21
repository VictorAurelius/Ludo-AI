import pygame
import random
from Pawns import *

# Player Constructor Class
class Player():
    def __init__(self, name, color, pawns):
        self.name = name
        self.color = color
        self.times_kicked = 0
        self.pawnlist = pawns
        self.pawns = 0
        self.dice1 = 0
        self.dice2 = 0
        self.pawns_home = 0
        self.temp_pawns_home = 0
        
        self.active = False
        self.turn = False
        self.Player1 = False
        self.Player2 = False
        self.Player3 = False
        self.Player4 = False
        self.is_ai = "[AI]" in str(name)
        self.ai_engine = None
        if self.is_ai:
            from ai_engine import LudoAI
            self.ai_engine = LudoAI(None)
        self.set_player_number()
    
    #this may be more useful later for naming and referencing purposes
    def set_player_number(self):
        if self.name == 'Player1':
            # if we set an attribute named after the player number, and set it to true, we can simply write if self.Player1 to check if an object on a list in a for loop is this specific player
            # this is also useful to determine if this instance of a player object is the one we intend to work with
            self.Player1 = True
        elif self.name == 'Player2':
            self.Player2 = True
        elif self.name == 'Player3':
            self.Player3 = True
        elif self.name == 'Player4':
            self.Player4 = True
            
    # this method is called before the mainloop is initialized                
    def set_statekeeper(self, statekeeper):
        #set statekeeper object as an attribute        
        self.Statekpr = statekeeper
        #set the list of players as an attribute
        self.players = self.Statekpr.players      
        # set self.player attribute to refer to the specific object it is, this can be very useful, all you have to do is write self.Player to refer to this specific instance of player object.
        if self.Player1:
             self.Player = self.Statekpr.playerRed
        elif self.Player2:
             self.Player = self.Statekpr.playerBlue
        elif self.Player3:
             self.Player = self.Statekpr.playerYellow
        elif self.Player4:
             self.Player = self.Statekpr.playerGreen             
        if self.is_ai and self.ai_engine:
            self.ai_engine.statekeeper = statekeeper
                
    #ensure player attributes are up to date and represent the current status
    def update_self(self):                  
        if self.Player1:
            # self.active is true if this player is active
            self.active = self.Statekpr.redActive
            # self.turn is true if it is currently this player's turn
            self.turn = self.Statekpr.redTurn
        elif self.Player2:
            self.active = self.Statekpr.blueActive
            self.turn = self.Statekpr.blueTurn
        elif self.Player3:
            self.active = self.Statekpr.yellowActive
            self.turn = self.Statekpr.yellowTurn
        elif self.Player4:
            self.active = self.Statekpr.greenActive
            self.turn = self.Statekpr.greenTurn      
        
        
                
    # ensure the statekeeper is updated with the latest attribute statuses        
    def update_statekeeper(self):        
        if self.Player1:
            self.Statekpr.redActive = self.active
            self.Statekpr.redTurn = self.turn
        elif self.Player2:
            self.Statekpr.blueActive = self.active
            self.Statekpr.blueTurn = self.turn
        elif self.Player3:
            self.Statekpr.yellowActive = self.active
            self.Statekpr.yellowTurn = self.turn
        elif self.Player4:
            self.Statekpr.greenActive = self.active
            self.Statekpr.greenTurn = self.turn       
        # self.activeplayer refers to the currently active player who's turn it is        
        self.Statekpr.activeplayer = self.activeplayer       
        # self.nextplayer refers to the player who's turn is next        
        self.Statekpr.nextplayer = self.nextplayer   
        
        # update the activeplayer attribute to the current active player
        # update the nextplayer attribute to player who will be active next
        # this method is called in the player Turn Method
    def update_active_and_next(self):
        self.activeplayer = self.Statekpr.activeplayer
        self.nextplayer = self.set_next_player()
        # Ensure statekeeper is updated with correct next player
        self.Statekpr.nextplayer = self.nextplayer
        
    def set_next_player(self):
        # Find current player's index
        current_index = -1
        for i, player in enumerate(self.players):
            if player == self.activeplayer:
                current_index = i
                break
                
        # Calculate next player's index
        next_index = (current_index + 1) % 4
        return self.players[next_index]

    def dice_roll(self):
        # Roll two dice
        self.dice1 = random.randint(1, 6)
        self.dice2 = random.randint(1, 6)
        total = self.dice1 + self.dice2
        print(f"Dice 1: {self.dice1}, Dice 2: {self.dice2}, Total: {total}")
        return total
        
    #attempt to move out of the starting location by rolling dice
    def move_out_onto_the_board(self, pawn=None):
        """Move a pawn from start onto the board"""
        roll = self.dice1 + self.dice2  # Sử dụng giá trị xúc xắc đã có
        # if total is >= 10, then move out onto the board
        if roll >= 10:
            # If pawn is provided, try to move that specific pawn
            if pawn is not None:
                if (pawn.counter == 0 and 
                    not (hasattr(pawn, 'king') and pawn.king) and 
                    not (hasattr(pawn, 'has_reached_finish') and pawn.has_reached_finish)):
                    # Khởi tạo start_position trước khi kiểm tra
                    start_position = pawn.dict[1]
                    # Kiểm tra vị trí xuất phát có bị chặn không
                    blocked = False
                    for other_pawn in self.pawnlist:
                        if other_pawn != pawn and other_pawn.rect.center == start_position:
                            blocked = True
                            break
                    
                    if not blocked:
                        # Xuất quân
                        pawn.counter = 1  # Đặt counter là 1 (vị trí xuất phát)
                        for other_player in self.Statekpr.players:
                            if other_player != self:  # Chỉ kiểm tra với quân của người chơi khác
                                for other_pawn in other_player.pawnlist:
                                    if (other_pawn.rect.center == start_position and 
                                        other_pawn.counter > 0 and 
                                        not hasattr(other_pawn, 'is_dying')):
                                        print(f"Quân của {self.name} ăn quân của {other_player.name} khi xuất quân")
                                        other_pawn.start_death_animation()
                                        other_player.pawns -= 1
                                        other_player.times_kicked += 1
                                        break
                        pawn.start_teleport(start_position)  # Dịch chuyển quân đến vị trí xuất phát
                        self.pawns += 1  # Tăng số quân trên bàn
                        pawn.just_moved_out = True  # Đánh dấu quân vừa xuất ra
                        if self.is_ai:
                            self.ai_action_completed = True
                        return True
                return False
            
            # If no pawn is provided, find first available pawn
            for pawn in self.pawnlist:
                if pawn.counter == 0:
                    # Khởi tạo start_position trước khi kiểm tra
                    start_position = pawn.dict[1]
                    # Kiểm tra vị trí xuất phát có bị chặn không
                    blocked = False
                    for other_pawn in self.pawnlist:
                        if other_pawn != pawn and other_pawn.rect.center == start_position:
                            blocked = True
                            break
                    
                    if not blocked:
                        # Xuất quân
                        pawn.counter = 1  # Đặt counter là 1 (vị trí xuất phát)
                        pawn.start_teleport(start_position)  # Dịch chuyển quân đến vị trí xuất phát
                        self.pawns += 1  # Tăng số quân trên bàn
                        pawn.just_moved_out = True  # Đánh dấu quân vừa xuất ra
                        if self.is_ai:
                            self.ai_action_completed = True
                        return True
            
            # Không thể xuất quân, có thể do vị trí xuất phát bị chặn
            return False
        else:
            # Roll < 10, không thể xuất quân
            return False
            
    #The method that runs when it is a player's turn
    def Turn(self):
        """Handle player turn using the AI engine for better decision making"""
        self.update_active_and_next()

        if self.is_ai:
            self.ai_action_completed = False
            print(f"{self.name} đang thực hiện lượt")

            # Get dice values
            dice_sum = self.dice1 + self.dice2
            print(f"AI tung được {self.dice1} và {self.dice2}, tổng: {dice_sum}")

            # Save initial state
            old_state = self._save_game_state()

            # Sử dụng AI engine để quyết định nước đi tốt nhất
            best_move = self.ai_engine.get_best_move(self, dice_sum)
            move_made = False

            if best_move:
                try:
                    move_type = best_move[0]
                    pawn = best_move[1]
                    old_pos = pawn.counter

                    if move_type == "move_out":
                        print(f"{self.name} quyết định xuất chuồng")
                        move_made = self.move_out_onto_the_board(pawn)
                    else: # move
                        move_data = best_move[2]
                        # Kích hoạt quân được chọn
                        for p in self.pawnlist:
                            p.activepawn = (p == pawn)

                        # Di chuyển quân
                        target_pos = move_data["target_position"]
                        pawn.move(dice_sum, self.Statekpr)
                        move_made = True

                        if move_data["can_capture"]:
                            print(f"{self.name} ăn quân tại vị trí {target_pos}")
                        elif move_data["on_star"]:
                            print(f"{self.name} di chuyển đến ô sao tại vị trí {target_pos}")
                        else:
                            print(f"{self.name} di chuyển quân từ {old_pos} đến {target_pos}")
                    
                except Exception as e:
                    print(f"Lỗi khi thực hiện nước đi: {e}")
                    self._restore_game_state(old_state)
                    move_made = False

            if move_made:
                self.ai_action_completed = True
                print(f"{self.name} hoàn thành lượt")
                pygame.time.delay(300)
            else:
                print(f"{self.name} không thể di chuyển")
                self._restore_game_state(old_state)

            # Đảm bảo không cướp lượt bot khác
           
            return move_made
        else:
            # Human player turn is handled by main.py
            print(f"{self.name} đang thực hiện lượt")
            return True
    
    #the method for moving the active players active pawn
    def move(self):
        #roll both dice and use total as movement distance
        distance = self.dice_roll()
        #loop through pawns in the players group to check for active pawn
        for pawn in self.pawnlist:
             #check which pawn is active
            if pawn.activepawn:
                #move active pawn according to dice roll total and pass distance integer variable and the statekeeper object
                pawn.move(distance, self.Statekpr)
                #update pawn states
                pawn.update_pawn_state(self.activeplayer, self.nextplayer)
                #active pawn found, moved and updated so loop can stop
                break
            #keep looping until active pawn found
            else:
                continue
        #ensure the statekeeper is kept current
        self.update_statekeeper()
              
    def can_move_pawn(self, pawn, dice_sum):
        """Check if a pawn can be moved with given dice sum"""
        # Check move from home
        if pawn.counter == 0:
            if dice_sum < 10:
                return False
            # Check if starting position is blocked by own pawn
            start_pos = pawn.dict[1]  # Sửa thành start_pos
            for other_pawn in self.pawnlist:
                if other_pawn != pawn and other_pawn.rect.center == start_pos:  # Sửa thành start_pos
                    return False
            return True

        # Check move on board
        if pawn.counter > 0:
            if pawn.counter + dice_sum > 97:
                return False
            # Check if target position is blocked by own pawn
            target_pos = pawn.dict[pawn.counter + dice_sum]
            for other_pawn in self.pawnlist:
                if other_pawn != pawn and other_pawn.rect.center == target_pos:
                    return False
            return True

        return False

    def get_valid_moves(self):
        """Get list of pawns that can move with current dice values"""
        valid_pawns = []
        dice_sum = self.dice1 + self.dice2
        for pawn in self.pawnlist:
            if self.can_move_pawn(pawn, dice_sum):
                valid_pawns.append(pawn)
        return valid_pawns

    # def move_out_onto_the_board(self, pawn):
    #     """Move a pawn from start onto the board"""
    #     if pawn in self.pawnlist and pawn.counter == 0:
    #         pawn.counter = 1
    #         pawn.rect.center = pawn.dict[1]
    #         pawn.activepawn = True
    #         self.pawns += 1
    #         return True
    #     return False

    def move_pawn(self, pawn):
        """Move a pawn by the current dice roll"""
        if not pawn or not pawn.activepawn:
            return False
            
        dice_roll = self.dice1 + self.dice2 if self.dice2 > 0 else self.dice1
        if pawn.counter == 0:  # Quân ở chuồng, chỉ di chuyển khi tổng >= 10
            if dice_roll >= 10:
                # Tạo biến start_pos trước khi sử dụng
                start_pos = pawn.dict[1]
                # Kiểm tra vị trí xuất phát có bị chặn không
                for other_pawn in self.pawnlist:
                    if other_pawn != pawn and other_pawn.rect.center == start_pos:
                        return False
                return self.move_out_onto_the_board(pawn)
            return False
        new_pos = pawn.counter + dice_roll
        
        if new_pos > 97:  # Invalid move
            return False
            
        # Check if target position is blocked by own pawn
        target_pos = pawn.dict[new_pos]
        for other_pawn in self.pawnlist:
            if other_pawn != pawn and other_pawn.rect.center == target_pos:
                return False
        pawn.activepawn = True  # Kích hoạt quân này
        print(f"AI {self.name} di chuyển quân từ {pawn.counter} đến {new_pos}")
        old_pos = pawn.counter
        # Move is valid, update pawn position
        pawn.counter = new_pos
        pawn.rect.center = target_pos
        
        # Clear just_moved_out flag if it exists
        if hasattr(pawn, 'just_moved_out'):
            pawn.just_moved_out = False
        pawn.on_star = False  # Reset trạng thái sao
        if new_pos in stars:
            star = stars[new_pos]
            print(f"Quân đã đi vào ô sao tại vị trí {new_pos}")
            pawn.on_star = True
        # Check if pawn reached home
        if new_pos == 97:
            pawn.king = True
            pawn.activepawn = False
            self.pawns -= 1
            self.pawns_home += 1  
            
        return True

    def handle_ai_turn(self):
        """Handle AI player turn"""
        if not self.is_ai or not self.ai_engine:
            return False,False
            
        # Get total dice roll
        dice_roll = self.dice1 + self.dice2 if self.dice2 > 0 else self.dice1
        print(f"=== Thông tin quân cờ của {self.name} ===")
        for i, pawn in enumerate(self.pawnlist):
            print(f"Quân {i+1}: counter={pawn.counter}, active={pawn.activepawn}, pos={pawn.rect.center}")
        print(f"Tổng số quân trên bàn: {self.pawns}")
    
        # Get best move from AI
        best_move = self.ai_engine.get_best_move(self, dice_roll)
        
        if best_move:
            move_type, pawn = best_move
            if move_type == "move_out":
                success = self.move_out_onto_the_board(pawn)
                # Kiểm tra hiệu ứng roll_again
                
                return success
            else:
                success = self.move_pawn(pawn)
                # Kiểm tra hiệu ứng roll_again
                return success
                
        return False

    # These methods are required for AI player functionality
    def _save_game_state(self):
        """Save the current game state to restore if AI move fails"""
        state = {
            'dice1': self.dice1,
            'dice2': self.dice2,
            'pawns_state': []
        }
        
        # Save state of all pawns
        for pawn in self.pawnlist:
            pawn_state = {
                'counter': pawn.counter,
                'position': pawn.rect.center,
                'activepawn': pawn.activepawn
            }
            state['pawns_state'].append(pawn_state)
            
        return state
    
    def _restore_game_state(self, state):
        """Restore game state from saved state"""
        if not state:
            return
            
        self.dice1 = state['dice1']
        self.dice2 = state['dice2']
        
        # Restore all pawns
        for i, pawn in enumerate(self.pawnlist):
            if i < len(state['pawns_state']):
                pawn_state = state['pawns_state'][i]
                pawn.counter = pawn_state['counter']
                pawn.rect.center = pawn_state['position']
                pawn.activepawn = pawn_state['activepawn']
                
        # Reset any flags
        if hasattr(self, 'ai_action_completed'):
            self.ai_action_completed = False




