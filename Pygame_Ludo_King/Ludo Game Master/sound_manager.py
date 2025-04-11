import pygame
import os

class SoundManager:
    def __init__(self):
        """Initialize the sound manager"""
        self.enabled = True
        self.sounds = {}
        
        # Try to initialize mixer
        try:
            pygame.mixer.init()
            self.mixer_working = True
        except:
            print("Warning: Sound system initialization failed. Sound will be disabled.")
            self.mixer_working = False
            return

        # Define expected sound files
        sound_files = {
            'click': 'click.wav',
            'hover': 'hover.wav',
            'transition': 'transition.wav',
            'start_game': 'start_game.wav',
            'win': 'win.wav',
        }
        
        # Try to load each sound file
        sound_dir = os.path.join('assets_ver1', 'sounds')
        for sound_name, file_name in sound_files.items():
            try:
                file_path = os.path.join(sound_dir, file_name)
                if os.path.exists(file_path):
                    self.sounds[sound_name] = pygame.mixer.Sound(file_path)
                    self.sounds[sound_name].set_volume(0.3)
            except:
                # Skip if file doesn't exist or can't be loaded
                pass
        
        if not self.sounds:
            print("Warning: No sound files found. Sound effects will be simulated.")
    
    def play_sound(self, sound_name):
        """Play a sound effect if it exists and sound is enabled"""
        if not self.enabled or not self.mixer_working:
            return
            
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                # Ignore playback errors
                pass
    
    def stop_sound(self, sound_name):
        """Stop a specific sound"""
        if not self.mixer_working:
            return
            
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].stop()
            except:
                # Ignore stop errors
                pass
    
    def stop_all(self):
        """Stop all sounds"""
        if not self.mixer_working:
            return
            
        try:
            pygame.mixer.stop()
        except:
            # Ignore stop errors
            pass
    
    def toggle(self):
        """Toggle sound on/off"""
        self.enabled = not self.enabled
        if not self.enabled:
            self.stop_all()

# Global sound manager instance
_sound_manager = None

def get_sound_manager():
    """Get or create the global sound manager instance"""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager