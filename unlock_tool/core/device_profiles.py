"""
Device Profile Management System
Centralized device configuration and compatibility tracking
"""

import json
from typing import Optional, Dict, List, Any
from pathlib import Path
from enum import Enum

from core.logger import Logger


class DeviceFamily(Enum):
    """Device family classifications"""
    SAMSUNG_GALAXY = "samsung_galaxy"
    XIAOMI = "xiaomi"
    OPPO_REALME = "oppo_realme"
    VIVO_IQOO = "vivo_iqoo"
    GOOGLE_PIXEL = "google_pixel"
    MOTOROLA = "motorola"
    ONEPLUS = "oneplus"
    HONOR = "honor"
    NOTHING = "nothing"
    TECNO_INFINIX = "tecno_infinix"
    ASUS = "asus"
    OTHER = "other"


class ExploitMethod(Enum):
    """Exploitation methods available"""
    FRP_BYPASS = "frp_bypass"
    EDL_MODE = "edl_mode"
    FASTBOOT_UNLOCK = "fastboot_unlock"
    RECOVERY_MODE = "recovery_mode"
    ADB_SIDELOAD = "adb_sideload"
    DIAG_MODE = "diag_mode"
    BOOTLOADER_UNLOCK = "bootloader_unlock"
    VAULTKEEPER = "vaultkeeper"
    FIREHOSE_LOADER = "firehose"


class DeviceProfile:
    """Individual device profile with capabilities"""
    
    def __init__(self, 
                 brand: str,
                 model: str,
                 codename: str,
                 family: DeviceFamily,
                 supported_exploits: List[ExploitMethod],
                 chipset: str,
                 android_version_min: int,
                 android_version_max: int,
                 notes: str = ""):
        
        self.brand = brand
        self.model = model
        self.codename = codename
        self.family = family
        self.supported_exploits = supported_exploits
        self.chipset = chipset
        self.android_version_min = android_version_min
        self.android_version_max = android_version_max
        self.notes = notes
    
    def supports_exploit(self, method: ExploitMethod) -> bool:
        """Check if device supports specific exploit"""
        return method in self.supported_exploits
    
    def is_supported_android_version(self, version: int) -> bool:
        """Check if Android version is supported"""
        return self.android_version_min <= version <= self.android_version_max
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        return {
            'brand': self.brand,
            'model': self.model,
            'codename': self.codename,
            'family': self.family.value,
            'exploits': [e.value for e in self.supported_exploits],
            'chipset': self.chipset,
            'android_min': self.android_version_min,
            'android_max': self.android_version_max,
            'notes': self.notes
        }


class DeviceProfileManager:
    """
    Device Profile Management System
    
    Provides centralized device compatibility and exploit method tracking
    """
    
    def __init__(self, profile_db_path: str = None, logger: Logger = None):
        """Initialize profile manager"""
        self.logger = logger or Logger(__name__)
        self.profile_db_path = Path(profile_db_path) if profile_db_path else \
                              Path(__file__).parent.parent.parent / 'database' / 'device_profiles.json'
        self.profiles: Dict[str, DeviceProfile] = {}
        self._load_profiles()
        self._initialize_default_profiles()
    
    def _load_profiles(self):
        """Load profiles from database"""
        try:
            if self.profile_db_path.exists():
                with open(self.profile_db_path, 'r') as f:
                    data = json.load(f)
                    for key, profile_data in data.items():
                        try:
                            profile = self._profile_from_dict(profile_data)
                            self.profiles[key] = profile
                        except Exception as e:
                            self.logger.warning(f"Failed to load profile {key}: {e}")
                self.logger.info(f"Loaded {len(self.profiles)} device profiles")
        except Exception as e:
            self.logger.warning(f"Failed to load profile database: {e}")
    
    def _profile_from_dict(self, data: Dict) -> DeviceProfile:
        """Create profile from dictionary"""
        return DeviceProfile(
            brand=data['brand'],
            model=data['model'],
            codename=data['codename'],
            family=DeviceFamily(data['family']),
            supported_exploits=[ExploitMethod(e) for e in data['exploits']],
            chipset=data['chipset'],
            android_version_min=data['android_min'],
            android_version_max=data['android_max'],
            notes=data.get('notes', '')
        )
    
    def _initialize_default_profiles(self):
        """Initialize default device profiles"""
        default_profiles = [
            DeviceProfile(
                brand="Samsung",
                model="Galaxy S24 Ultra",
                codename="dm3q",
                family=DeviceFamily.SAMSUNG_GALAXY,
                supported_exploits=[
                    ExploitMethod.FRP_BYPASS,
                    ExploitMethod.EDL_MODE,
                    ExploitMethod.DIAG_MODE,
                    ExploitMethod.RECOVERY_MODE
                ],
                chipset="Snapdragon 8 Gen 3",
                android_version_min=14,
                android_version_max=15,
                notes="Latest flagship, Knox 5.0"
            ),
            DeviceProfile(
                brand="Xiaomi",
                model="14 Ultra",
                codename="apollo",
                family=DeviceFamily.XIAOMI,
                supported_exploits=[
                    ExploitMethod.EDL_MODE,
                    ExploitMethod.FASTBOOT_UNLOCK,
                    ExploitMethod.FRP_BYPASS
                ],
                chipset="Snapdragon 8 Gen 3",
                android_version_min=14,
                android_version_max=15,
                notes="Supports Mi Unlock"
            ),
            DeviceProfile(
                brand="Google",
                model="Pixel 9 Pro",
                codename="caiman",
                family=DeviceFamily.GOOGLE_PIXEL,
                supported_exploits=[
                    ExploitMethod.FRP_BYPASS,
                    ExploitMethod.FASTBOOT_UNLOCK,
                    ExploitMethod.EDL_MODE
                ],
                chipset="Tensor G4",
                android_version_min=14,
                android_version_max=15,
                notes="Tensor devices"
            ),
            DeviceProfile(
                brand="OnePlus",
                model="12",
                codename="phoenix",
                family=DeviceFamily.ONEPLUS,
                supported_exploits=[
                    ExploitMethod.FASTBOOT_UNLOCK,
                    ExploitMethod.FRP_BYPASS,
                    ExploitMethod.EDL_MODE
                ],
                chipset="Snapdragon 8 Gen 3",
                android_version_min=14,
                android_version_max=15,
                notes="Open bootloader devices"
            ),
            DeviceProfile(
                brand="Motorola",
                model="Razr 50",
                codename="guacamole",
                family=DeviceFamily.MOTOROLA,
                supported_exploits=[
                    ExploitMethod.FRP_BYPASS,
                    ExploitMethod.RECOVERY_MODE,
                    ExploitMethod.ADB_SIDELOAD
                ],
                chipset="Snapdragon 7 Gen 3",
                android_version_min=13,
                android_version_max=14,
                notes="Budget-friendly devices"
            ),
        ]
        
        for profile in default_profiles:
            key = f"{profile.brand}_{profile.codename}".lower()
            if key not in self.profiles:
                self.profiles[key] = profile
        
        self.logger.info(f"Initialized {len(default_profiles)} default profiles")
    
    def find_profile(self, brand: str = None, model: str = None, 
                    codename: str = None) -> Optional[DeviceProfile]:
        """
        Find device profile by brand/model/codename
        
        Args:
            brand: Device brand
            model: Device model
            codename: Device codename (most reliable)
            
        Returns:
            Profile if found, None otherwise
        """
        try:
            # Search by codename first (most reliable)
            if codename:
                for profile in self.profiles.values():
                    if profile.codename.lower() == codename.lower():
                        return profile
            
            # Search by brand and model
            if brand and model:
                for profile in self.profiles.values():
                    if (profile.brand.lower() == brand.lower() and
                        profile.model.lower() == model.lower()):
                        return profile
            
            return None
            
        except Exception as e:
            self.logger.error(f"Profile search failed: {e}")
            return None
    
    def get_compatible_exploits(self, profile: DeviceProfile, 
                               android_version: int) -> List[ExploitMethod]:
        """
        Get compatible exploits for device
        
        Args:
            profile: Device profile
            android_version: Target Android version
            
        Returns:
            List of compatible exploitation methods
        """
        try:
            compatible = []
            
            if not profile.is_supported_android_version(android_version):
                self.logger.warning(
                    f"Android {android_version} outside supported range "
                    f"{profile.android_version_min}-{profile.android_version_max}"
                )
            
            for exploit in profile.supported_exploits:
                compatible.append(exploit)
            
            self.logger.info(f"Compatible exploits: {[e.value for e in compatible]}")
            
            return compatible
            
        except Exception as e:
            self.logger.error(f"Exploit compatibility check failed: {e}")
            return []
    
    def add_profile(self, profile: DeviceProfile) -> bool:
        """Add custom device profile"""
        try:
            key = f"{profile.brand}_{profile.codename}".lower()
            self.profiles[key] = profile
            self.logger.info(f"Added profile: {profile.model}")
            self._save_profiles()
            return True
        except Exception as e:
            self.logger.error(f"Failed to add profile: {e}")
            return False
    
    def _save_profiles(self):
        """Save profiles to database"""
        try:
            self.profile_db_path.parent.mkdir(parents=True, exist_ok=True)
            data = {k: v.to_dict() for k, v in self.profiles.items()}
            
            with open(self.profile_db_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            self.logger.info(f"Saved {len(self.profiles)} profiles")
        except Exception as e:
            self.logger.error(f"Failed to save profiles: {e}")
    
    def get_profile_summary(self, profile: DeviceProfile) -> str:
        """Get human-readable profile summary"""
        return (
            f"{profile.brand} {profile.model}\n"
            f"Codename: {profile.codename}\n"
            f"Chipset: {profile.chipset}\n"
            f"Android: {profile.android_version_min}-{profile.android_version_max}\n"
            f"Exploits: {', '.join([e.value for e in profile.supported_exploits])}\n"
            f"Notes: {profile.notes}"
        )
    
    def list_profiles(self, family: DeviceFamily = None) -> List[DeviceProfile]:
        """List profiles, optionally filtered by family"""
        profiles = list(self.profiles.values())
        
        if family:
            profiles = [p for p in profiles if p.family == family]
        
        return sorted(profiles, key=lambda p: (p.brand, p.model))
