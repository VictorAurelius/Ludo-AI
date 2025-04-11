import pygame
import os

class SoundManager:
    def __init__(self):
        """Initialize the sound manager"""
        self.enabled = True
        self.sounds = {}
        self.initialized = False
        
        # Try to initialize mixer
        try:
            pygame.mixer.init()
            self.initialized = True
        except:
            print("Sound system initialization failed. Game will continue without sound.")
            return
        
        # Define sound mapping
        sound_files = {
            'click': 'click.wav',
            'hover': 'hover.wav',
            'transition': 'transition.wav',
            'start_game': 'start_game.wav',
            'win': 'win.wav',
        }
        
        # Try to load sounds
        sound_dir = os.path.join('assets_ver1', 'sounds')
        if os.path.exists(sound_dir):
            for sound_name, file_name in sound_files.items():
                try:
                    file_path = os.path.join(sound_dir, file_name)
                    if os.path.exists(file_path):
                        self.sounds[sound_name] = pygame.mixer.Sound(file_path)
                        self.sounds[sound_name].set_volume(0.3)
                except:
                    continue
    
    def play_sound(self, sound_name):
        """Play a sound if available"""
        if self.enabled and self.initialized and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass
    
    def stop_sound(self, sound_name):
        """Stop a specific sound if available"""
        if self.initialized and sound_name in self.sounds:
            try:
                self.sounds[sound_name].stop()
            except:
                pass
    
    def stop_all(self):
        """Stop all sounds"""
        if self.initialized:
            try:
                pygame.mixer.stop()
            except:
                pass
    
    def toggle(self):
        """Toggle sound on/off"""
        if self.initialized:
            self.enabled = not self.enabled
            if not self.enabled:
                self.stop_all()

    @property
    def has_sounds(self):
        """Check if any sounds are loaded"""
        return bool(self.sounds)

# Global sound manager instance
_sound_manager = None

def get_sound_manager():
    """Get or create the global sound manager instance"""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager