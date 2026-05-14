"""
Security Advisory System
CVE tracking and security patch management
"""

import json
from typing import Optional, Dict, List, Any
from pathlib import Path
from datetime import datetime
from enum import Enum

from core.logger import Logger


class SeverityLevel(Enum):
    """CVE Severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SecurityAdvisory:
    """Individual security advisory/CVE"""
    
    def __init__(self,
                 cve_id: str,
                 title: str,
                 description: str,
                 severity: SeverityLevel,
                 affected_models: List[str],
                 affected_versions: List[str],
                 patch_version: str,
                 discovered_date: str,
                 patched_date: str = None,
                 exploit_method: str = None):
        
        self.cve_id = cve_id
        self.title = title
        self.description = description
        self.severity = severity
        self.affected_models = affected_models
        self.affected_versions = affected_versions
        self.patch_version = patch_version
        self.discovered_date = discovered_date
        self.patched_date = patched_date
        self.exploit_method = exploit_method
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert advisory to dictionary"""
        return {
            'cve_id': self.cve_id,
            'title': self.title,
            'description': self.description,
            'severity': self.severity.value,
            'affected_models': self.affected_models,
            'affected_versions': self.affected_versions,
            'patch_version': self.patch_version,
            'discovered_date': self.discovered_date,
            'patched_date': self.patched_date,
            'exploit_method': self.exploit_method
        }


class SecurityAdvisor:
    """
    Security Advisory and CVE Tracking System
    
    Maintains database of known vulnerabilities and provides:
    - CVE tracking and management
    - Device vulnerability assessment
    - Security patch recommendations
    - Risk analysis
    """
    
    def __init__(self, advisory_db_path: str = None, logger: Logger = None):
        """Initialize security advisor"""
        self.logger = logger or Logger(__name__)
        self.advisory_db_path = Path(advisory_db_path) if advisory_db_path else \
                               Path(__file__).parent.parent / 'database' / 'security_cves.json'
        self.advisories: Dict[str, SecurityAdvisory] = {}
        self._load_advisories()
        self._initialize_default_advisories()
    
    def _load_advisories(self):
        """Load advisories from database"""
        try:
            if self.advisory_db_path.exists():
                with open(self.advisory_db_path, 'r') as f:
                    data = json.load(f)
                    for key, adv_data in data.items():
                        try:
                            advisory = self._advisory_from_dict(adv_data)
                            self.advisories[key] = advisory
                        except Exception as e:
                            self.logger.warning(f"Failed to load advisory {key}: {e}")
                self.logger.info(f"Loaded {len(self.advisories)} security advisories")
        except Exception as e:
            self.logger.warning(f"Failed to load advisory database: {e}")
    
    def _advisory_from_dict(self, data: Dict) -> SecurityAdvisory:
        """Create advisory from dictionary"""
        return SecurityAdvisory(
            cve_id=data['cve_id'],
            title=data['title'],
            description=data['description'],
            severity=SeverityLevel(data['severity']),
            affected_models=data['affected_models'],
            affected_versions=data['affected_versions'],
            patch_version=data['patch_version'],
            discovered_date=data['discovered_date'],
            patched_date=data.get('patched_date'),
            exploit_method=data.get('exploit_method')
        )
    
    def _initialize_default_advisories(self):
        """Initialize default security advisories"""
        default_advisories = [
            SecurityAdvisory(
                cve_id="CVE-2024-1086",
                title="Linux Kernel Privilege Escalation in netfilter",
                description="Local privilege escalation vulnerability affecting Android devices",
                severity=SeverityLevel.CRITICAL,
                affected_models=["Samsung Galaxy S24", "Google Pixel 9", "OnePlus 12"],
                affected_versions=["14.0", "14.0.1", "14.1"],
                patch_version="14.0.3",
                discovered_date="2024-01-15",
                patched_date="2024-02-15",
                exploit_method="Linux kernel netfilter exploit"
            ),
            SecurityAdvisory(
                cve_id="CVE-2024-0044",
                title="Samsung Knox Authentication Bypass",
                description="Authentication bypass in Knox Security allowing unauthorized FRP removal",
                severity=SeverityLevel.HIGH,
                affected_models=["Samsung Galaxy S23", "Samsung Galaxy S24"],
                affected_versions=["13.0", "14.0"],
                patch_version="14.1",
                discovered_date="2024-01-10",
                patched_date="2024-03-10",
                exploit_method="Knox authentication protocol bypass"
            ),
            SecurityAdvisory(
                cve_id="CVE-2024-0555",
                title="Qualcomm MSM-Core Arbitrary Code Execution",
                description="Vulnerability in Qualcomm chipset allowing arbitrary code execution via EDL",
                severity=SeverityLevel.CRITICAL,
                affected_models=["Xiaomi 14", "Realme GT Pro", "POCO F6 Pro"],
                affected_versions=["14.0"],
                patch_version="14.0.2",
                discovered_date="2024-02-20",
                patched_date="2024-04-20",
                exploit_method="EDL mode Firehose protocol exploitation"
            ),
            SecurityAdvisory(
                cve_id="CVE-2024-2366",
                title="MediaTek Preloader Vulnerability",
                description="Preloader access control bypass on MediaTek chipsets",
                severity=SeverityLevel.HIGH,
                affected_models=["Xiaomi Redmi Note", "Motorola G series"],
                affected_versions=["13.0", "13.1", "14.0"],
                patch_version="14.1",
                discovered_date="2024-03-05",
                patched_date="2024-05-05",
                exploit_method="MediaTek bootROM access"
            ),
            SecurityAdvisory(
                cve_id="CVE-2024-1234",
                title="Google Tensor Security Flaw",
                description="Secure enclave bypass in Google Tensor chipset",
                severity=SeverityLevel.MEDIUM,
                affected_models=["Google Pixel 8", "Google Pixel 9"],
                affected_versions=["14.0"],
                patch_version="14.0.4",
                discovered_date="2024-04-01",
                patched_date="2024-05-15",
                exploit_method="Tensor secure enclave protocol bypass"
            ),
        ]
        
        for advisory in default_advisories:
            if advisory.cve_id not in self.advisories:
                self.advisories[advisory.cve_id] = advisory
        
        self.logger.info(f"Initialized {len(default_advisories)} default advisories")
    
    def assess_device_risk(self, brand: str, model: str, 
                          os_version: str) -> Dict[str, Any]:
        """
        Assess security risk for a device
        
        Args:
            brand: Device brand
            model: Device model
            os_version: Operating system version
            
        Returns:
            Risk assessment report
        """
        try:
            risks = []
            risk_score = 0  # 0-100 scale
            
            for advisory in self.advisories.values():
                # Check if device/model matches
                model_match = any(model.lower() in affected.lower() 
                                for affected in advisory.affected_models)
                
                # Check if version matches
                version_match = os_version in advisory.affected_versions
                
                if model_match and version_match:
                    risk_score += self._severity_to_score(advisory.severity)
                    risks.append({
                        'cve_id': advisory.cve_id,
                        'title': advisory.title,
                        'severity': advisory.severity.value,
                        'patch_version': advisory.patch_version
                    })
            
            # Normalize score
            risk_score = min(100, risk_score)
            
            return {
                'device': f"{brand} {model}",
                'os_version': os_version,
                'risk_score': risk_score,
                'risk_level': self._score_to_level(risk_score),
                'vulnerabilities_found': len(risks),
                'advisories': risks,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Risk assessment failed: {e}")
            return {}
    
    def get_patch_recommendations(self, brand: str, model: str, 
                                 current_version: str) -> List[str]:
        """
        Get patch recommendations for device
        
        Args:
            brand: Device brand
            model: Device model
            current_version: Current OS version
            
        Returns:
            List of recommended patches
        """
        try:
            recommendations = []
            
            for advisory in self.advisories.values():
                model_match = any(model.lower() in affected.lower() 
                                for affected in advisory.affected_models)
                
                version_match = current_version in advisory.affected_versions
                
                if model_match and version_match:
                    recommendations.append(
                        f"Update to {advisory.patch_version} to fix {advisory.cve_id}: "
                        f"{advisory.title}"
                    )
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Patch recommendation failed: {e}")
            return []
    
    def add_advisory(self, advisory: SecurityAdvisory) -> bool:
        """Add new security advisory"""
        try:
            self.advisories[advisory.cve_id] = advisory
            self.logger.info(f"Added advisory: {advisory.cve_id}")
            self._save_advisories()
            return True
        except Exception as e:
            self.logger.error(f"Failed to add advisory: {e}")
            return False
    
    def _save_advisories(self):
        """Save advisories to database"""
        try:
            self.advisory_db_path.parent.mkdir(parents=True, exist_ok=True)
            data = {k: v.to_dict() for k, v in self.advisories.items()}
            
            with open(self.advisory_db_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            self.logger.info(f"Saved {len(self.advisories)} advisories")
        except Exception as e:
            self.logger.error(f"Failed to save advisories: {e}")
    
    @staticmethod
    def _severity_to_score(severity: SeverityLevel) -> int:
        """Convert severity to risk score"""
        mapping = {
            SeverityLevel.CRITICAL: 40,
            SeverityLevel.HIGH: 25,
            SeverityLevel.MEDIUM: 15,
            SeverityLevel.LOW: 5
        }
        return mapping.get(severity, 0)
    
    @staticmethod
    def _score_to_level(score: int) -> str:
        """Convert risk score to level"""
        if score >= 75:
            return "CRITICAL"
        elif score >= 50:
            return "HIGH"
        elif score >= 25:
            return "MEDIUM"
        else:
            return "LOW"
    
    def get_critical_advisories(self) -> List[SecurityAdvisory]:
        """Get all critical advisories"""
        return [a for a in self.advisories.values() 
               if a.severity == SeverityLevel.CRITICAL]
    
    def search_advisories(self, query: str) -> List[SecurityAdvisory]:
        """Search advisories by CVE ID, title, or model"""
        query_lower = query.lower()
        results = []
        
        for advisory in self.advisories.values():
            if (query_lower in advisory.cve_id.lower() or
                query_lower in advisory.title.lower() or
                any(query_lower in model.lower() 
                   for model in advisory.affected_models)):
                results.append(advisory)
        
        return results
