import platform
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class VolumeManager:
    """Manage system volume control"""
    
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.current_volume = 50
        self.pycaw_available = False
        
        if enabled and platform.system() == 'Windows':
            self._init_pycaw()
        else:
            logger.warning("Volume control disabled or not on Windows")
    
    def _init_pycaw(self):
        """Initialize PyCaw for Windows audio control"""
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            devices = AudioUtilities.GetSpeakers() # get the speakers access from devicee
            interface = devices.Activate(
                IAudioEndpointVolume._iid_,
                CLSCTX_ALL,
                None
            ) 
            self.volume = cast(interface, POINTER(IAudioEndpointVolume))
            
            self.vol_range = self.volume.GetVolumeRange()
            self.min_vol = self.vol_range[0]
            self.max_vol = self.vol_range[1]
            
            self.pycaw_available = True
            logger.info("PyCaw initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PyCaw: {e}")
            self.pycaw_available = False


    def set_volume(self, volume_percent):
        """Set system volume using scalar scale  for accurate %
        """
        self.current_volume = max(0, min(100, volume_percent)) 

        if not self.enabled or not self.pycaw_available:
            "if pycaw is not set properly then exits"
            return

        try:
            scalar = self.current_volume / 100.0 # converting to scaler bcoz windows internally uses it not DB(descibel)
            self.volume.SetMasterVolumeLevelScalar(scalar, None)
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")

    def get_volume(self):
        """Get accurate current system volume % using scalar"""
        if not self.enabled or not self.pycaw_available: # not enabled or pycaw not available then return current volume
            return self.current_volume

        try:
            scalar = self.volume.GetMasterVolumeLevelScalar()
            self.current_volume = int(scalar * 100)
            return self.current_volume
        except Exception as e:
            logger.error(f"Failed to get volume: {e}")
            return self.current_volume

    def mute(self):
        """Mute system audio"""
        if self.pycaw_available:
            try:
                self.volume.SetMute(1, None)
            except Exception as e:
                logger.error(f"Failed to mute: {e}")
    
    def unmute(self):
        """Unmute system audio"""
        if self.pycaw_available:
            try:
                self.volume.SetMute(0, None)
            except Exception as e:
                logger.error(f"Failed to unmute: {e}")