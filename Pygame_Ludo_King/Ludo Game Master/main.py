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
from menu_manager import MenuManager
from sound_manager import get_sound_manager
import random

# Pygame Initialized
pygame.init()

# Window dimension coordinates in pixels
winX = 925
winY = 725

# Set and initialize the pygame display
win = pygame.display.set_mode((winX, winY))
pygame.display.set_caption("Ludo Game")

# Initialize managers
alert_manager = AlertManager()
menu_manager = None
sound_manager = get_sound_manager()
statekpr = None

# Game states
GAME_STATE_MENU = "menu"
GAME_STATE_PLAYING = "playing"
GAME_STATE_PAUSED = "paused"
GAME_STATE_TRANSITION = "transition"
current_game_state = GAME_STATE_MENU

# Game UI Elements
roll_button = pygame.Rect(735, 290, 180, 50)
title_button = pygame.Rect(745, 10, 160, 40)
title_ranking_button = pygame.Rect(400, 400, 200, 50)
yes_button = pygame.Rect(410, 260, 60, 30)
no_button = pygame.Rect(530, 260, 90, 30)
sound_button = pygame.Rect(875, 10, 40, 40)

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

# Game variables
dice_images = []
bgBoard = None
current_dice1 = None
current_dice2 = None
dice_num1 = 1
dice_num2 = 1
roll_button_enabled = True
can_move = False
dice_animating = False
showing_dialog = False
finished_players = []

def draw_sound_button():
    """Draw sound control button"""
    is_enabled = sound_manager.enabled and sound_manager.initialized
    mouse_hover = sound_button.collidepoint(pygame.mouse.get_pos())
    button_color = GRAY if is_enabled else BLACK
    if mouse_hover:
        button_color = (min(button_color[0] + 30, 255),
                       min(button_color[1] + 30, 255),
                       min(button_color[2] + 30, 255))
    
    pygame.draw.rect(win, button_color, sound_button)
    pygame.draw.polygon(win, WHITE, [
        (sound_button.x + 10, sound_button.y + 15),
        (sound_button.x + 20, sound_button.y + 10),
        (sound_button.x + 20, sound_button.y + 30),
        (sound_button.x + 10, sound_button.y + 25)
    ])
    
    if not is_enabled:
        pygame.draw.line(win, WHITE,
                        (sound_button.x + 10, sound_button.y + 10),
                        (sound_button.x + 30, sound_button.y + 30), 2)

def load_game_assets():
    """Load all game assets"""
    global dice_images, bgBoard
    try:
        # Load dice images
        dice_images = [
            pygame.image.load('img/1_block.png'),
            pygame.image.load('img/2_block.png'),
            pygame.image.load('img/3_block.png'),
            pygame.image.load('img/4_block.png'),
            pygame.image.load('img/5_block.png'),
            pygame.image.load('img/6_block.png')
        ]
        # Load game board
        bgBoard = load_map()
        return True
    except Exception as e:
        print(f"Error loading assets: {e}")
        return False

def load_map():
    """Load and render the game map"""
    map_surface = pygame.Surface((725, 725))
    game_map = load_pygame('mapfinal/mapludo.tmx')
    for layer in game_map.visible_layers:
        for x, y, gid in layer:
            tile = game_map.get_tile_image_by_gid(gid)
            if tile:
                map_surface.blit(tile, (x * game_map.tilewidth, y * game_map.tileheight))
    return map_surface

def init_game_variables():
    """Initialize or reset all game variables"""
    global roll_button_enabled, can_move, dice_animating, showing_dialog
    global current_dice1, current_dice2, dice_num1, dice_num2, finished_players
    global dice_images, statekpr
    
    roll_button_enabled = True
    can_move = False
    dice_animating = False
    showing_dialog = False
    finished_players = []
    
    if dice_images:
        current_dice1 = dice_images[0]
        current_dice2 = dice_images[0]
    dice_num1 = 1
    dice_num2 = 1
    
    statekpr = Statekeep()

def draw_dialog(win):
    """Draw dialog box asking to return to title"""
    s = pygame.Surface((winX, winY))
    s.set_alpha(128)
    s.fill(BLACK)
    win.blit(s, (0, 0))
    
    dialog_rect = pygame.Rect(400, 200, 230, 100)
    pygame.draw.rect(win, WHITE, dialog_rect)
    pygame.draw.rect(win, BLACK, dialog_rect, 2)
    
    vn_font = pygame.font.SysFont("segoeui", 24)
    text = vn_font.render(u"Bạn có muốn trở về", True, BLACK)
    text2 = vn_font.render(u"trang tiêu đề không?", True, BLACK)
    win.blit(text, (410, 200))
    win.blit(text2, (410, 220))
    
    mouse_pos = pygame.mouse.get_pos()
    yes_color = GRAY if yes_button.collidepoint(mouse_pos) else BLACK
    no_color = GRAY if no_button.collidepoint(mouse_pos) else BLACK
    
    pygame.draw.rect(win, yes_color, yes_button, 2)
    pygame.draw.rect(win, no_color, no_button, 2)
    
    yes_text = vn_font.render(u"Có", True, yes_color)
    no_text = vn_font.render(u"Không", True, no_color)
    win.blit(yes_text, (425, 255))
    win.blit(no_text, (540, 255))

def handle_menu():
    """Handle menu state"""
    global menu_manager
    
    if menu_manager is None:
        menu_manager = MenuManager(win)
    
    for event in pygame.event.get():
        if event.type == QUIT:
            return False
        elif event.type == MOUSEBUTTONDOWN:
            if sound_button.collidepoint(event.pos):
                sound_manager.toggle()
                sound_manager.play_sound('click')
            else:
                action = menu_manager.handle_click(event.pos)
                if action == "start_game":
                    init_game_variables()
                    return action
                elif action == "exit":
                    return False
    
    menu_manager.draw()
    draw_sound_button()
    return True

def handle_game_events():
    """Handle game state events"""
    global showing_dialog
    
    for event in pygame.event.get():
        if event.type == QUIT:
            return False
        elif event.type == MOUSEBUTTONDOWN:
            if showing_dialog:
                if yes_button.collidepoint(event.pos):
                    return "menu"
                elif no_button.collidepoint(event.pos):
                    showing_dialog = False
                sound_manager.play_sound('click')
            else:
                if title_button.collidepoint(event.pos):
                    showing_dialog = True
                    sound_manager.play_sound('click')
                elif sound_button.collidepoint(event.pos):
                    sound_manager.toggle()
                    sound_manager.play_sound('click')
    
    return True

def handle_game():
    """Handle game state"""
    global statekpr
    
    win.blit(bgBoard, (0, 0))
    
    if statekpr:
        statekpr.update()
    
    result = handle_game_events()
    if result != True:
        return result
    
    draw_sound_button()
    
    if showing_dialog:
        draw_dialog(win)
    
    return True

def main():
    """Main game loop"""
    global current_game_state
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        clock.tick(60)
        
        if current_game_state == GAME_STATE_MENU:
            result = handle_menu()
            if result == "start_game":
                current_game_state = GAME_STATE_PLAYING
            elif not result:
                running = False
        
        elif current_game_state == GAME_STATE_PLAYING:
            result = handle_game()
            if result == "menu":
                current_game_state = GAME_STATE_MENU
            elif not result:
                running = False
        
        pygame.display.flip()

if __name__ == "__main__":
    if not load_game_assets():
        print("Failed to load game assets!")
        pygame.quit()
        exit(1)
    
    main()
    pygame.quit()