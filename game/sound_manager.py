"""Sound manager for the game - handles all audio playback"""
import os
import pygame
from pathlib import Path
from typing import Optional, Dict
from enum import Enum
from .packaging import resource_path


class SoundEffect(Enum):
    """Enumeration of all sound effects in the game"""
    # UI Sounds
    BUTTON_CLICK = "button_click.wav"
    BUTTON_HOVER = "button_hover.mp3"
    SUCCESS = "success.wav"
    ERROR = "error.wav"
    NOTIFICATION = "notification.wav"
    HEART_COLLECT = "heart_collect.wav"
    
    # Tea Preparation Sounds
    WATER_POUR = "water_pour.wav"
    TEA_POUR = "cup_fill.wav"
    CUP_FILL = "cup_fill.wav"
    LEAVES_DISPOSE = "leaves_dispose.wav"
    PICKUP = "pickup.mp3"
    
    # Cat Sounds
    CAT_ARRIVE = "cat_arrive.mp3"
    CAT_HAPPY = "cat_happy.wav"
    CAT_DISAPPOINTED = "cat_disappointed.wav"
    CAT_LEAVE = "cat_arrive.wav"
    CAT_PET = "cat_pet.wav"
    
    # Ambient/Background
    BACKGROUND_MUSIC = "background_music.mp3"
    AMBIENT_GARDEN = "ambient_garden.mp3"


class SoundManager:
    """
    Manages all sound effects and music in the game.
    
    Features:
    - Lazy loading of sound files
    - Volume control for SFX and music separately
    - Fallback for missing sound files
    - Easy-to-use API for playing sounds
    """
    MUSIC_SOUND_TABLE = {
        SoundEffect.BACKGROUND_MUSIC: 0.5,
        SoundEffect.AMBIENT_GARDEN: 1.0,
    }
    
    _instance: Optional['SoundManager'] = None
    
    def __init__(self, sounds_dir: str = "assets/sounds"):
        """
        Initialize the sound manager.
        
        Args:
            sounds_dir: Directory containing sound files
        """
        # Resolve sounds directory (handle PyInstaller bundles)
        if os.path.isabs(sounds_dir):
            self.sounds_dir = Path(sounds_dir)
        else:
            self.sounds_dir = Path(resource_path(sounds_dir))
        self.sounds: Dict[SoundEffect, pygame.mixer.Sound] = {}
        self.music: Dict[SoundEffect, pygame.mixer.Sound] = {}
        self.music_volume = 0.1
        self.sfx_volume = 0.7
        self.muted = False
        self.music_enabled = True
        self.sfx_enabled = True
        
        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Create sounds directory if it doesn't exist
        self.sounds_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_instance(cls, sounds_dir: str = "assets/sounds") -> 'SoundManager':
        """
        Get or create the singleton instance of SoundManager.
        
        Args:
            sounds_dir: Directory containing sound files
            
        Returns:
            The singleton SoundManager instance
        """
        if cls._instance is None:
            cls._instance = cls(sounds_dir)
        return cls._instance
    
    def _load_sound(self, sound_effect: SoundEffect) -> Optional[pygame.mixer.Sound]:
        """
        Load a sound file from disk.
        
        Args:
            sound_effect: The sound effect to load
            
        Returns:
            The loaded Sound object, or None if loading fails
        """
        sound_path = self.sounds_dir / sound_effect.value
        
        try:
            if sound_path.exists():
                sound = pygame.mixer.Sound(str(sound_path))
                return sound
            else:
                # Silently fail for missing sound files (graceful degradation)
                return None
        except pygame.error as e:
            print(f"Warning: Could not load sound {sound_effect.value}: {e}")
            return None
    
    def play_sound(self, sound_effect: SoundEffect, volume: Optional[float] = None):
        """
        Play a sound effect.
        
        Args:
            sound_effect: The sound effect to play
            volume: Optional volume override (0.0 to 1.0)
        """
        if not self.sfx_enabled or self.muted:
            return
        
        # Lazy load the sound if not already loaded
        if sound_effect not in self.sounds:
            loaded_sound = self._load_sound(sound_effect)
            if loaded_sound:
                self.sounds[sound_effect] = loaded_sound
            else:
                # Sound file not found, skip silently
                return
        
        sound = self.sounds[sound_effect]
        if sound:
            # Set volume
            actual_volume = volume if volume is not None else self.sfx_volume
            sound.set_volume(actual_volume)
            sound.play()
    
    def play_music(self, sound_effect: SoundEffect, loops: int = -1, fade_ms: int = 0):
        """
        Play background music.
        
        Args:
            sound_effect: The music file to play
            loops: Number of times to loop (-1 for infinite)
            fade_ms: Fade in time in milliseconds
        """
        print("Playing music:", sound_effect.value)
        if not self.music_enabled or self.muted:
            return
        
        music_path = self.sounds_dir / sound_effect.value
        
        try:
            print("Attempting to play music:", music_path)
            if music_path.exists():
                print("Music file found:", music_path)
                music = self._load_sound(sound_effect)
                volume = self.MUSIC_SOUND_TABLE.get(sound_effect, 0.5)
                if music is None:
                    return
                print("Music loaded:", music_path)
                self.music[sound_effect] = music
                music.set_volume(volume * self.music_volume)
                music.play(loops, fade_ms=fade_ms)
                # pygame.mixer.music.load(str(music_path))
                # pygame.mixer.music.set_volume(self.music_volume)
                # pygame.mixer.music.play(loops, fade_ms=fade_ms)
        except pygame.error as e:
            print(f"Warning: Could not play music {sound_effect.value}: {e}")
    
    def stop_music(self, fade_ms: int = 0):
        """
        Stop background music.
        
        Args:
            fade_ms: Fade out time in milliseconds
        """
        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()
    
    def pause_music(self):
        """Pause background music"""
        if SoundEffect.BACKGROUND_MUSIC in self.music:
            self.music[SoundEffect.BACKGROUND_MUSIC].set_volume(0)
    
    def unpause_music(self):
        """Unpause background music"""
        if SoundEffect.BACKGROUND_MUSIC in self.music:
            correction_volume = self.MUSIC_SOUND_TABLE.get(SoundEffect.BACKGROUND_MUSIC, 0.5)
            self.music[SoundEffect.BACKGROUND_MUSIC].set_volume(self.music_volume * correction_volume)
    
    def set_music_volume(self, volume: float):
        """
        Set music volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        for sound_effect, music in self.music.items():
            correction_volume = self.MUSIC_SOUND_TABLE.get(sound_effect, 0.5)
            music.set_volume(self.music_volume * correction_volume)
    
    def set_sfx_volume(self, volume: float):
        """
        Set sound effects volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def toggle_mute(self) -> bool:
        """
        Toggle mute state.
        
        Returns:
            The new mute state
        """
        self.muted = not self.muted
        if self.muted:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
        return self.muted
    
    def toggle_music(self) -> bool:
        """
        Toggle music on/off.
        
        Returns:
            The new music enabled state
        """
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.pause_music()
        else:
            self.unpause_music()
        return self.music_enabled
    
    def toggle_sfx(self) -> bool:
        """
        Toggle sound effects on/off.
        
        Returns:
            The new SFX enabled state
        """
        self.sfx_enabled = not self.sfx_enabled
        return self.sfx_enabled
    
    def cleanup(self):
        """Clean up sound resources"""
        pygame.mixer.music.stop()
        self.sounds.clear()


# Convenience function for getting the global sound manager
def get_sound_manager() -> SoundManager:
    """Get the global sound manager instance"""
    return SoundManager.get_instance()
