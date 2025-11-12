from PySide6.QtGui import QPixmap
from pathlib import Path

class ImageCache:
    def __init__(self):
        self._cache = {}

    def preload(self, paths):
        for p in paths:
            if p and p not in self._cache:
                try:
                    pix = QPixmap(p)
                    if not pix.isNull():
                        self._cache[p] = pix
                except Exception:
                    # silently ignore bad images
                    pass

    def get(self, path):
        # return cached pixmap or None
        pix = self._cache.get(path)
        if pix:
            return pix
        # try to load on demand if file exists
        if path:
            p = Path(path)
            if p.exists():
                pix = QPixmap(str(p))
                if not pix.isNull():
                    self._cache[path] = pix
                    return pix
        return None
