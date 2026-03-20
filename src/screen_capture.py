"""ROGUE — Screen Capture (mss + scrot fallback) → base64 PNG."""
import base64, logging, subprocess, tempfile, os
from typing import Optional
try:
    import mss, mss.tools
    HAS_MSS = True
except ImportError:
    HAS_MSS = False
from .config import config
logger = logging.getLogger(__name__)

class ScreenCapture:
    def __init__(self):
        self.monitor_num = config.SCREEN_CAPTURE_MONITOR
        self.enabled = config.SCREEN_CAPTURE_ENABLE

    def capture_b64(self, monitor: Optional[int] = None) -> Optional[str]:
        if not self.enabled: return None
        monitor = monitor or self.monitor_num
        if HAS_MSS: return self._capture_mss(monitor)
        return self._capture_scrot()

    def _capture_mss(self, monitor: int) -> Optional[str]:
        try:
            with mss.mss() as sct:
                monitors = sct.monitors
                mon = monitors[min(monitor, len(monitors) - 1)]
                shot = sct.grab(mon)
                buf = mss.tools.to_png(shot.rgb, shot.size)
                return base64.b64encode(buf).decode("utf-8")
        except Exception as e:
            logger.error("mss failed: %s", e)
            return self._capture_scrot()

    def _capture_scrot(self) -> Optional[str]:
        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                tmp = f.name
            r = subprocess.run(["scrot", tmp], capture_output=True, timeout=5)
            if r.returncode != 0: return None
            with open(tmp, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            logger.error("scrot failed: %s", e)
            return None

screen = ScreenCapture()
