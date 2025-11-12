import pygame
from pathlib import Path

class AudioManager:
    def __init__(self):
        self.enabled = True
        self.music_volume = 0.5  # 50% por defecto
        self.sfx_volume = 0.7    # 70% por defecto
        try:
            pygame.mixer.init()
            self._ready = True
            pygame.mixer.music.set_volume(self.music_volume)
        except Exception:
            self._ready = False

    def play(self, path):
        if not self.enabled or not self._ready:
            return
        p = Path(path)
        if not p.exists():
            return
        try:
            sound = pygame.mixer.Sound(str(p))
            sound.set_volume(self.sfx_volume)
            sound.play()
        except Exception:
            pass
    
    def play_music(self, path, loops=-1):
        """Reproduce musica de fondo en loop"""
        if not self.enabled or not self._ready:
            return
        p = Path(path)
        if not p.exists():
            return
        try:
            pygame.mixer.music.load(str(p))
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops)
        except Exception:
            pass

    def stop_music(self):
        """Detiene la musica de fondo"""
        if self._ready:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass

    def set_music_volume(self, volume):
        """Ajusta el volumen de la musica (0.0 a 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        if self._ready:
            try:
                pygame.mixer.music.set_volume(self.music_volume)
            except Exception:
                pass

    def set_sfx_volume(self, volume):
        """Ajusta el volumen de los efectos de sonido (0.0 a 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
