# UnlockTool - Professional Device Servicing Suite

**Version 2.1.0** | Multi-Platform | Offline Support

## 📋 Overview

UnlockTool is a comprehensive **Android & iOS device servicing platform** combining professional-grade functionality with an intuitive user interface. Designed for technicians, repair shops, IT specialists, and power users.

### 🎯 Primary Features

#### 🤖 **Android Management**
- **Device Detection** - Auto-detect Android devices in ADB, Fastboot, DIAG, and EDL modes
- **FRP Bypass** - Multiple methods for Google Factory Reset Protection removal
- **Screen Lock Removal** - Remove Android screen locks without data loss
- **Bootloader Unlock** - Unlock device bootloaders for custom firmware
- **IMEI Repair** - Restore corrupted or invalid IMEI numbers
- **Firmware Flashing** - Flash complete firmware or specific partitions
- **Backup & Restore** - Full device backup and selective restoration
- **Factory Reset** - Clean device reset with optional data preservation
- **Partition Management** - Format and manage individual partitions

#### 🍎 **iOS Management**  
- **Device Detection** - Detect iPhone/iPad via iTunes/USB
- **Activation Removal** - Bypass iCloud/Apple ID activation locks
- **Passcode Bypass** - Remove screen lock passcode codes
- **Data Backup** - Create full device backups
- **Data Restore** - Restore from backup files
- **File Manager** - Browse and manage iOS files
- **App Management** - Install, remove, or update applications

#### ⚡ **Flashing Tool**
- **Firmware Management** - Load and validate firmware packages
- **Partition Browser** - View detailed partition information
- **Flash Options** - Data format, verification, Knox security
- **Progress Monitoring** - Real-time flash progress with status logs
- **Error Recovery** - Automatic error detection and recovery

#### 🚨 **Emergency Recovery**
- **Boot Mode Selection** - Boot to Recovery, Bootloader, Fastboot, DIAG
- **Force Reboot** - Force device restart from any state
- **Emergency Flash** - Flash firmware in emergency situations
- **Recovery Logs** - Detailed operation logs for troubleshooting

#### 🤖 **Auto Exploit**
- **Smart Device Analysis** - Automatic device compatibility detection
- **Operation Sequencing** - Optimal method selection and execution
- **Multi-Method Support** - Multiple exploit methods per operation
- **Real-Time Feedback** - Live progress updates and status reporting

---

## 🔧 System Requirements

| Requirement | Specification |
|------------|---------------|
| **OS** | Windows 10/11, macOS 10.14+, Ubuntu 18.04+ |
| **RAM** | 4 GB minimum (8 GB recommended) |
| **CPU** | Multi-core processor (Intel/AMD/Apple Silicon) |
| **Storage** | 2 GB free space for firmware files |
| **USB** | USB 2.0+ port for device connection |

---

## 🚀 Quick Start

### Windows
1. Extract `unlock_tool-main-windows-x86_64.zip`
2. Run `unlock_tool.exe`
3. Accept EULA
4. Enter license: `kptjms991` (super admin, no base64 encoding)
5. Connect device

### Linux
1. Extract `unlock_tool-v2.1.0-linux-x86_64.tar.gz`
2. Run `./unlock_tool/unlock_tool`
3. Accept EULA
4. Enter license: `kptjms991` (super admin)
5. Connect device

### macOS
1. Extract DMG file
2. Drag UnlockTool to Applications
3. Run UnlockTool
4. Accept EULA  
5. Enter license: `kptjms991`
6. Connect device

---

## 📱 Supported Devices

### Android Brands
- **Samsung** - Galaxy S series, Note series, A series, Z series
- **Xiaomi** - Redmi, POCO, Mi series
- **Huawei** - P series, Mate series, Nova series
- **OPPO** - Find series, Reno series
- **Vivo** - V series, Y series, X series
- **OnePlus** - All recent models
- **Motorola** - Moto G, E, Edge series
- **Google** - Pixel series
- **Realme** - Realme numbered series
- **ASUS** - ROG, Zenfone series

### iOS Devices
- **iPhone** - All models from iPhone 6 to iPhone 15
- **iPad** - All iPad, iPad Pro, iPad Air, iPad mini models
- **iPod** - iPod Touch 6th generation

---

## 🔐 License Management

### Super Admin Access
**Credential:** `kptjms991` (no base64/JSON encoding required)

**Grants:**
- ✅ Full feature access
- ✅ All device operations
- ✅ No expiration
- ✅ Unlimited usage

### License Formats
- Direct super admin credential (kptjms991)
- Base64-encoded license strings
- License files (.bin, .txt)

---

## ⚙️ Advanced Features

### Device Profiles
Pre-configured profiles for popular devices with:
- Device specifications
- Available exploits
- Optimal method selection
- Security considerations

### Security Advisory
- Real-time CVE tracking
- Severity classification
- Affected device listing
- Patch recommendations

### DIAG Mode Operations
- NVRAM reading/writing
- Device info retrieval
- Direct device unlock commands
- Qualcomm-specific operations

### Knox Security
- Multiple bypass methods for Samsung devices
- Samsung-specific security protocols
- Authentication protocol exploitation
- Factory binary flashing capability

---

## 🛠️ Developer Information

### Architecture
- **Backend:** Python 3.11+
- **GUI Framework:** PyQt6
- **Protocol Support:** ADB, Fastboot, DIAG, EDL, USB
- **Platform Tools:** Bundled adb, fastboot, and platform-specific utilities

### Module Structure
```
unlock_tool/
├── core/              # Core functionality
├── modules/           # Exploit and operation modules
│   ├── exploits/     # Device-specific exploits
│   ├── flash/        # Firmware flashing
│   ├── frp/          # FRP bypass
│   ├── ios/          # iOS operations
│   ├── imei/         # IMEI repair
│   └── unlock/       # Unlocking operations
├── gui/              # GUI components
├── database/         # Device profiles and CVEs
└── main.py           # Entry point
```

---

## 🔒 Security & Legal

### Warranty Disclaimer
- Use at your own risk
- May void device warranty
- Manufacturer support may be unavailable after use
- Data loss is possible - backup before operations

### License Compliance
- For authorized technicians and repair shops
- Comply with local device unlock regulations
- Respect manufacturer intellectual property
- User assumes all legal responsibility

---

## 📞 Support & Documentation

- **Documentation:** See included guides in app
- **Troubleshooting:** Emergency Recovery tab
- **Device Issues:** Auto Exploit for automatic solutions
- **Updates:** Check for firmware and tool updates in-app

---

## 📦 Distribution Formats

### Windows
- `unlock_tool.exe` - Direct executable
- `unlock_tool-main-windows-x86_64.zip` - Portable archive (97 MB)

### Linux  
- `unlock_tool` - Direct executable
- `unlock_tool-v2.1.0-linux-x86_64.tar.gz` - Portable archive (68 MB)

### macOS
- `UnlockTool.dmg` - Disk image for installation
- Universal Binary support (Intel + Apple Silicon)

---

## 🎨 UI Features

### Professional Interface
- **Dark Theme** - Eye-friendly dark color scheme
- **Tabbed Navigation** - Organized feature grouping
- **Real-time Status** - Live operation feedback
- **Progress Tracking** - Visual progress bars
- **Detailed Logging** - Color-coded operation logs

### Responsive Design
- Works on all screen resolutions
- Optimized for both 1080p and 4K displays
- Touch-friendly buttons and controls
- Scalable interface elements

---

## 📊 Operation Tracking

All operations include:
- Timestamp logging
- Success/failure indicators
- Error messages and codes
- Recovery suggestions
- Detailed operation history

---

**© 2024 UnlockTool Team | Professional Device Servicing Solutions**
