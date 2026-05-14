#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android Servicing Tool  –  3uTools-style PyQt6 UI
Cross-platform (Linux + Windows). Full backend integration.
"""
import sys, os, platform
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFrame, QScrollArea, QStackedWidget,
    QSystemTrayIcon, QProgressBar, QGridLayout, QComboBox,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon

# ── backend path ──────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "unlock_tool"))

try:
    from core.exploit_manager  import ExploitManager
    from core.device_profiles  import DeviceProfileManager, DeviceFamily
    from core.security_advisor import SecurityAdvisor
    from core.device_detector  import DeviceDetector
    from core.logger           import Logger as _Logger
    from core.adb_interface    import ADBInterface
    BACKEND = True
    _log_inst = _Logger()
except ImportError as _e:
    BACKEND = False
    _log_inst = None
    print(f"⚠  Backend not found – UI-only mode  ({_e})")

# ── cross-platform font ───────────────────────────────────────────────────────
_FONT = "Segoe UI" if platform.system() == "Windows" else "Ubuntu"
_MONO = "Consolas" if platform.system() == "Windows" else "Monospace"

# ── colours ───────────────────────────────────────────────────────────────────
CH_TOP  = "#1565C0"; CH_BOT  = "#1976D2"
CN_BG   = "#1A237E"; CN_SEL  = "#283593"; CN_HOV = "#1E2A8A"
CB_BG   = "#F0F2F5"; CC_BG   = "#FFFFFF"; CC_BOR = "#DDE1E7"
CACC    = "#1976D2"; CACC_D  = "#1565C0"
CGREEN  = "#16A34A"; CRED    = "#DC2626"; CORANGE = "#D97706"
CMUTED  = "#6B7280"; CMAIN   = "#1A1A2E"; CSTATUS = "#E8EAF6"

# ── async worker ──────────────────────────────────────────────────────────────
class Worker(QObject):
    finished = pyqtSignal(bool, str)
    def __init__(self, fn, *args):
        super().__init__(); self._fn = fn; self._args = args
    def run(self):
        try:
            r = self._fn(*self._args); self.finished.emit(bool(r), str(r))
        except Exception as e:
            self.finished.emit(False, str(e))

def run_async(parent, fn, args, on_done):
    t = QThread(parent); w = Worker(fn, *args)
    w.moveToThread(t); t.started.connect(w.run)
    w.finished.connect(on_done); w.finished.connect(t.quit)
    t.start(); return t, w

# ── style helpers ─────────────────────────────────────────────────────────────
def lbl(text, size=12, bold=False, color=CMAIN):
    l = QLabel(text)
    l.setStyleSheet(f"font-size:{size}px;font-weight:{'700' if bold else '400'};"
                    f"color:{color};background:transparent;")
    return l

def sep():
    f = QFrame(); f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet(f"color:{CC_BOR};background:{CC_BOR};max-height:1px;"); return f

def make_card(title=""):
    outer = QFrame()
    outer.setStyleSheet(
        f"background:{CC_BG};border:1px solid {CC_BOR};border-radius:10px;")
    lay = QVBoxLayout(outer); lay.setContentsMargins(14,12,14,14); lay.setSpacing(8)
    if title:
        lay.addWidget(lbl(title, 13, bold=True)); lay.addWidget(sep())
    return outer, lay

def btn_primary(text, destructive=False):
    b = QPushButton(text)
    bg = CRED if destructive else CACC; hov = "#B91C1C" if destructive else CACC_D
    b.setStyleSheet(f"QPushButton{{background:{bg};color:white;border:none;"
                    f"border-radius:6px;padding:7px 16px;font-size:12px;font-weight:600;}}"
                    f"QPushButton:hover{{background:{hov};}}"
                    f"QPushButton:disabled{{background:#CBD5E1;color:#94A3B8;}}")
    return b

def btn_ghost(text):
    b = QPushButton(text)
    b.setStyleSheet(f"QPushButton{{background:white;color:{CACC};border:1px solid {CACC};"
                    f"border-radius:6px;padding:6px 14px;font-size:12px;}}"
                    f"QPushButton:hover{{background:{CSTATUS};}}"
                    f"QPushButton:disabled{{color:#94A3B8;border-color:#CBD5E1;}}")
    return b

# ══════════════════════════════════════════════════════════════════════════════
# DEVICE HEADER  (top blue banner)
# ══════════════════════════════════════════════════════════════════════════════
class DeviceHeader(QFrame):
    refresh_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(130)
        self.setStyleSheet(
            f"QFrame{{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            f"stop:0 {CH_TOP},stop:1 {CH_BOT});border:none;}}")
        lay = QHBoxLayout(self); lay.setContentsMargins(20,12,20,12); lay.setSpacing(20)

        self._icon = QLabel("📱")
        self._icon.setFixedSize(80,80)
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon.setStyleSheet(
            "background:rgba(255,255,255,0.12);border-radius:12px;"
            "color:white;font-size:36px;")
        lay.addWidget(self._icon)

        info = QVBoxLayout(); info.setSpacing(4)
        self._name = QLabel("No Device Connected")
        self._name.setStyleSheet(
            "color:white;font-size:18px;font-weight:700;background:transparent;")
        info.addWidget(self._name)

        grid = QGridLayout(); grid.setSpacing(2)
        self._f = {}
        for i,(k,v) in enumerate([("Serial","—"),("Mode","—"),("Android","—"),
                                   ("Chipset","—"),("Storage","—"),("Battery","—")]):
            row,col = divmod(i,3)
            w = QWidget(); w.setStyleSheet("background:transparent;")
            hl = QHBoxLayout(w); hl.setContentsMargins(0,0,0,0); hl.setSpacing(2)
            kl = QLabel(f"{k}: ")
            kl.setStyleSheet("color:rgba(255,255,255,0.6);font-size:11px;background:transparent;")
            vl = QLabel(v)
            vl.setStyleSheet("color:white;font-size:11px;font-weight:600;background:transparent;")
            hl.addWidget(kl); hl.addWidget(vl); hl.addStretch()
            grid.addWidget(w, row, col); self._f[k] = vl
        info.addLayout(grid)
        lay.addLayout(info, 1)

        bcol = QVBoxLayout(); bcol.setSpacing(8)
        for txt, sig in [("⟳  Refresh", self.refresh_requested),
                         ("ADB Shell",  None)]:
            b = QPushButton(txt)
            b.setFixedWidth(110)
            b.setStyleSheet(
                "QPushButton{background:rgba(255,255,255,0.15);color:white;"
                "border:1px solid rgba(255,255,255,0.3);border-radius:6px;"
                "padding:6px 10px;font-size:12px;}"
                "QPushButton:hover{background:rgba(255,255,255,0.25);}")
            if sig: b.clicked.connect(sig.emit)
            bcol.addWidget(b)
        bcol.addStretch()
        lay.addLayout(bcol)

        self._pill = QLabel("● Disconnected")
        self._pill.setStyleSheet(
            f"color:{CRED};background:rgba(0,0,0,0.25);border-radius:10px;"
            "padding:3px 10px;font-size:11px;font-weight:600;")
        lay.addWidget(self._pill, 0, Qt.AlignmentFlag.AlignTop)

    def update(self, info: dict):
        if not info:
            self._name.setText("Waiting for device…  (connect via USB)")
            self._pill.setText("● No Device")
            self._pill.setStyleSheet(
                f"color:{CRED};background:rgba(0,0,0,0.25);border-radius:10px;"
                "padding:3px 10px;font-size:11px;font-weight:600;")
            for v in self._f.values(): v.setText("—")
            return
        model = f"{info.get('manufacturer','')} {info.get('model','Unknown')}".strip()
        self._name.setText(model or "Unknown Device")
        self._f["Serial"].setText(info.get("serial","—"))
        self._f["Mode"].setText(info.get("mode","—"))
        self._f["Android"].setText(str(info.get("android_version","—")))
        self._f["Chipset"].setText(info.get("chipset","—"))
        self._f["Storage"].setText(info.get("storage","—"))
        self._f["Battery"].setText(info.get("battery","—"))
        self._pill.setText("● Connected")
        self._pill.setStyleSheet(
            f"color:{CGREEN};background:rgba(0,0,0,0.25);border-radius:10px;"
            "padding:3px 10px;font-size:11px;font-weight:600;")


# ══════════════════════════════════════════════════════════════════════════════
# NAV RAIL  (left icon sidebar)
# ══════════════════════════════════════════════════════════════════════════════
class NavBtn(QPushButton):
    def __init__(self, ico, label):
        super().__init__()
        self.setCheckable(True); self.setFixedSize(76,64)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QVBoxLayout(self); lay.setContentsMargins(0,6,0,6); lay.setSpacing(2)
        il = QLabel(ico); il.setAlignment(Qt.AlignmentFlag.AlignCenter)
        il.setStyleSheet("font-size:22px;background:transparent;color:white;")
        ll = QLabel(label); ll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ll.setWordWrap(True)
        ll.setStyleSheet("font-size:10px;background:transparent;color:rgba(255,255,255,0.8);")
        lay.addWidget(il); lay.addWidget(ll)
        self.setStyleSheet(
            f"QPushButton{{background:transparent;border:none;border-radius:8px;}}"
            f"QPushButton:hover{{background:{CN_HOV};}}"
            f"QPushButton:checked{{background:{CN_SEL};border-left:3px solid white;}}")

class NavRail(QFrame):
    page_changed = pyqtSignal(int)
    ITEMS = [("🏠","Home"),("🔓","Exploits"),("🛡️","Security"),
             ("📋","Profiles"),("⚙️","Toolbox"),("📟","Console")]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(78)
        self.setStyleSheet(f"background:{CN_BG};border:none;")
        lay = QVBoxLayout(self); lay.setContentsMargins(1,8,1,8); lay.setSpacing(4)
        self._btns = []
        for i,(ico,lbl_) in enumerate(self.ITEMS):
            b = NavBtn(ico, lbl_)
            b.clicked.connect(lambda _,idx=i: self._sel(idx))
            lay.addWidget(b); self._btns.append(b)
        lay.addStretch()
        self._sel(0)

    def _sel(self, idx):
        for i,b in enumerate(self._btns): b.setChecked(i==idx)
        self.page_changed.emit(idx)

    def select(self, idx): self._sel(idx)

# ══════════════════════════════════════════════════════════════════════════════
# HOME PAGE  (quick-action tiles)
# ══════════════════════════════════════════════════════════════════════════════
class HomePage(QWidget):
    action = pyqtSignal(str)
    TILES = [
        ("🔓","FRP Bypass",       "samsung_frp", CACC),
        ("⚡","Full Unlock Chain","full",         CRED),
        ("🔧","Knox Bypass",      "knox",         "#7C3AED"),
        ("📡","DIAG Exploit",     "diag",         "#0891B2"),
        ("💾","MTK BROM",         "mtk",          "#059669"),
        ("🔑","Lockscreen",       "lockscreen",   CORANGE),
        ("📶","IMEI Restore",     "imei",         "#DB2777"),
        ("🛡️","Security Scan",   "security",     "#1D4ED8"),
    ]
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{CB_BG};")
        sc = QScrollArea(self); sc.setWidgetResizable(True)
        sc.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        inner = QWidget(); inner.setStyleSheet(f"background:{CB_BG};")
        sc.setWidget(inner)
        rl = QVBoxLayout(self); rl.setContentsMargins(0,0,0,0); rl.addWidget(sc)
        lay = QVBoxLayout(inner); lay.setContentsMargins(20,16,20,16); lay.setSpacing(16)
        lay.addWidget(lbl("Quick Actions", 14, bold=True))
        grid = QGridLayout(); grid.setSpacing(12)
        for i,(ico,name,key,color) in enumerate(self.TILES):
            tile = QPushButton()
            tile.setFixedSize(150,110)
            tile.setCursor(Qt.CursorShape.PointingHandCursor)
            tile.setStyleSheet(
                f"QPushButton{{background:{CC_BG};border:1px solid {CC_BOR};"
                f"border-radius:10px;}}"
                f"QPushButton:hover{{border:1px solid {color};background:#F8FAFF;}}")
            tl = QVBoxLayout(tile); tl.setContentsMargins(10,12,10,10); tl.setSpacing(6)
            il = QLabel(ico); il.setAlignment(Qt.AlignmentFlag.AlignCenter)
            il.setStyleSheet(f"font-size:28px;background:transparent;color:{color};")
            nl = QLabel(name); nl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            nl.setWordWrap(True)
            nl.setStyleSheet(f"font-size:11px;font-weight:600;color:{CMAIN};background:transparent;")
            tl.addWidget(il); tl.addWidget(nl)
            tile.clicked.connect(lambda _,k=key: self.action.emit(k))
            grid.addWidget(tile, i//4, i%4)
        lay.addLayout(grid); lay.addStretch()


# ══════════════════════════════════════════════════════════════════════════════
# EXPLOITS PAGE  – correct API: all exploits take device_info dict
# ══════════════════════════════════════════════════════════════════════════════
class ExploitsPage(QWidget):
    EXPLOITS = [
        ("Qualcomm DIAG Exploit",
         "NVRAM read/write, security unlock via DIAG protocol.", "diag", False),
        ("Advanced Knox Bypass",
         "Auto-selects: EDL / VaultKeeper / recovery injection.", "knox", False),
        ("Samsung FRP Bypass",
         "TalkBack → Chromium → Knox → VaultKeeper chain.", "samsung_frp", False),
        ("Google Pixel FRP",
         "AddAccountActivity / dev-settings bypass (Android 10-14).", "pixel_frp", False),
        ("MediaTek BROM Exploit",
         "BootROM USB descriptor exploit (CVE-2020-0069).", "mtk", False),
        ("Lockscreen Removal",
         "locksettings.db replace / locksettings clear (Android 10-13).", "lockscreen", False),
        ("IMEI / QCN Restore",
         "Qualcomm DIAG NV-item IMEI read/write via serial port.", "imei", False),
        ("⚡  Full Unlock Chain",
         "ExploitManager: runs all applicable exploits in priority order.", "full", True),
    ]

    def __init__(self, get_device, log_fn, parent=None):
        super().__init__(parent)
        self._get_device = get_device; self._log = log_fn; self._thread = None
        self.setStyleSheet(f"background:{CB_BG};")
        sc = QScrollArea(self); sc.setWidgetResizable(True)
        sc.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        inner = QWidget(); inner.setStyleSheet(f"background:{CB_BG};")
        sc.setWidget(inner)
        rl = QVBoxLayout(self); rl.setContentsMargins(0,0,0,0); rl.addWidget(sc)
        lay = QVBoxLayout(inner); lay.setContentsMargins(20,16,20,16); lay.setSpacing(12)

        self._prog = QProgressBar()
        self._prog.setRange(0,0); self._prog.setVisible(False); self._prog.setFixedHeight(4)
        self._prog.setStyleSheet(
            f"QProgressBar{{background:#DDE1E7;border-radius:2px;border:none;}}"
            f"QProgressBar::chunk{{background:{CACC};border-radius:2px;}}")
        lay.addWidget(self._prog)

        self._status = lbl("Select an exploit to run.", 12, color=CMUTED)
        lay.addWidget(self._status)

        self._btns = []
        for name, desc, key, destr in self.EXPLOITS:
            card, cl = make_card()
            row = QHBoxLayout()
            info = QVBoxLayout()
            info.addWidget(lbl(name, 13, bold=True))
            info.addWidget(lbl(desc, 11, color=CMUTED))
            row.addLayout(info, 1)
            b = btn_primary("Run", destructive=destr)
            b.setFixedWidth(80)
            b.clicked.connect(lambda _,k=key: self.run(k))
            row.addWidget(b, 0, Qt.AlignmentFlag.AlignVCenter)
            cl.addLayout(row)
            lay.addWidget(card)
            self._btns.append(b)
        lay.addStretch()

    def _busy(self, v):
        self._prog.setVisible(v)
        for b in self._btns: b.setEnabled(not v)

    def run(self, key):
        if self._thread and self._thread.isRunning():
            self._log("⚠  Another operation is running."); return
        device = self._get_device()
        if not device and BACKEND:
            self._status.setText("⚠  No device connected."); return
        self._busy(True)
        self._status.setText(f"Running: {key}…")

        def work(dev, k):
            if not BACKEND: return f"Demo: {k} (no backend)"
            lg = _Logger()
            if k == "full":
                return ExploitManager(dev, lg).run()
            if k == "diag":
                from modules.exploits.qualcomm_diag_exploit import DiagExploitManager
                from core.usb_manager import USBDevice
                return DiagExploitManager(USBDevice(dev), lg).exploit()
            if k == "knox":
                from modules.unlock.security.advanced_knox_bypass import AdvancedKnoxBypass
                from core.usb_manager import USBDevice
                return AdvancedKnoxBypass(USBDevice(dev), lg).execute_best_method()
            if k == "samsung_frp":
                from modules.exploits.samsung_frp_exploit import SamsungFRPExploit
                return SamsungFRPExploit(dev, lg).exploit()
            if k == "pixel_frp":
                from modules.exploits.google_pixel_frp_exploit import GooglePixelFRPExploit
                return GooglePixelFRPExploit(dev, lg).exploit()
            if k == "mtk":
                from modules.exploits.mediatek_brom_exploit import MediaTekBROMExploit
                return MediaTekBROMExploit(dev, lg).exploit()
            if k == "lockscreen":
                from modules.exploits.lockscreen_removal_exploit import LockscreenRemovalExploit
                return LockscreenRemovalExploit(dev, lg).exploit()
            if k == "imei":
                from modules.exploits.imei_qcn_exploit import IMEIQCNExploit
                return IMEIQCNExploit(dev, lg).exploit()

        def done(ok, msg):
            self._busy(False)
            icon = "✅" if ok else "❌"
            self._status.setText(f"{icon} {msg}")
            self._log(f"{icon} [{key}] {msg}")

        self._thread, self._worker = run_async(self, work, (device, key), done)

# ══════════════════════════════════════════════════════════════════════════════
# SECURITY PAGE
# ══════════════════════════════════════════════════════════════════════════════
class SecurityPage(QWidget):
    def __init__(self, get_device, log_fn, parent=None):
        super().__init__(parent)
        self._get_device = get_device; self._log = log_fn
        self.setStyleSheet(f"background:{CB_BG};")
        lay = QVBoxLayout(self); lay.setContentsMargins(20,16,20,16); lay.setSpacing(14)

        hdr = QHBoxLayout()
        hdr.addWidget(lbl("Security Advisor", 14, bold=True)); hdr.addStretch()
        rb = btn_primary("Run Assessment"); rb.clicked.connect(self._assess)
        hdr.addWidget(rb); lay.addLayout(hdr)

        rc, rl = make_card("Risk Summary")
        self._risk = QLabel("Run an assessment to see results.")
        self._risk.setWordWrap(True)
        self._risk.setStyleSheet(f"color:{CMUTED};font-size:12px;background:transparent;")
        rl.addWidget(self._risk); lay.addWidget(rc)

        cc, cl = make_card("CVE Advisories")
        self._cve = QTextEdit(); self._cve.setReadOnly(True)
        self._cve.setFont(QFont(_MONO, 10)); self._cve.setFixedHeight(260)
        self._cve.setStyleSheet(
            f"background:#F8FAFF;border:1px solid {CC_BOR};"
            "border-radius:6px;color:#1A1A2E;padding:6px;")
        cl.addWidget(self._cve); lay.addWidget(cc); lay.addStretch()

    def _assess(self):
        if not BACKEND:
            self._risk.setText("Backend not available."); return
        try:
            dev = self._get_device() or {}
            adv = SecurityAdvisor(logger=_Logger())
            brand = dev.get("manufacturer",""); model = dev.get("model","")
            ver   = str(dev.get("android_version","14"))
            rep   = adv.assess_device_risk(brand, model, ver)
            level = rep.get("risk_level","UNKNOWN")
            color = {"CRITICAL":CRED,"HIGH":CRED,"MEDIUM":CORANGE,"LOW":CGREEN}.get(level,CMUTED)
            self._risk.setText(
                f'<span style="color:{color};font-weight:700;">{level}</span>'
                f'  –  Score: {rep.get("risk_score",0)}/100'
                f'  |  CVEs: {rep.get("vulnerabilities_found",0)}')
            self._risk.setTextFormat(Qt.TextFormat.RichText)
            lines = []
            for a in rep.get("advisories",[]):
                lines.append(f"[{a['severity'].upper():8}] {a['cve_id']}  {a['title']}\n"
                             f"           → Patch: {a['patch_version']}\n")
            recs = adv.get_patch_recommendations(brand, model, ver)
            if recs: lines += ["\nRecommendations:"] + [f"  • {r}" for r in recs]
            self._cve.setPlainText("\n".join(lines) or "No CVEs matched.")
            self._log(f"Security: {level}, {rep.get('vulnerabilities_found',0)} CVEs")
        except Exception as e:
            self._risk.setText(f"Error: {e}"); self._log(f"Security error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# PROFILES PAGE
# ══════════════════════════════════════════════════════════════════════════════
class ProfilesPage(QWidget):
    def __init__(self, log_fn, parent=None):
        super().__init__(parent)
        self._log = log_fn
        self.setStyleSheet(f"background:{CB_BG};")
        lay = QVBoxLayout(self); lay.setContentsMargins(20,16,20,16); lay.setSpacing(14)

        hdr = QHBoxLayout()
        hdr.addWidget(lbl("Device Profiles", 14, bold=True)); hdr.addStretch()
        self._combo = QComboBox()
        self._combo.setFixedWidth(180)
        self._combo.setStyleSheet(
            f"background:white;border:1px solid {CC_BOR};"
            "border-radius:6px;padding:5px 10px;font-size:12px;color:#1A1A2E;")
        self._combo.addItem("All families")
        if BACKEND:
            for f in DeviceFamily: self._combo.addItem(f.value)
        hdr.addWidget(self._combo)
        lb = btn_primary("Load"); lb.setFixedWidth(70); lb.clicked.connect(self._load)
        hdr.addWidget(lb); lay.addLayout(hdr)

        card, cl = make_card()
        self._area = QTextEdit(); self._area.setReadOnly(True)
        self._area.setFont(QFont(_MONO, 10))
        self._area.setStyleSheet(
            f"background:#F8FAFF;border:1px solid {CC_BOR};"
            "border-radius:6px;color:#1A1A2E;padding:6px;")
        cl.addWidget(self._area); lay.addWidget(card, 1)

    def _load(self):
        if not BACKEND: self._area.setPlainText("Backend not available."); return
        try:
            pm  = DeviceProfileManager(logger=_Logger())
            sel = self._combo.currentText()
            fam = DeviceFamily(sel) if sel != "All families" else None
            profiles = pm.list_profiles(family=fam)
            self._area.setPlainText(
                "\n\n".join(pm.get_profile_summary(p) for p in profiles) or "No profiles.")
            self._log(f"Loaded {len(profiles)} profiles.")
        except Exception as e:
            self._area.setPlainText(f"Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TOOLBOX PAGE
# ══════════════════════════════════════════════════════════════════════════════
class ToolboxPage(QWidget):
    TOOLS = [
        ("Reboot Device",        "reboot"),
        ("Reboot → Bootloader",  "reboot bootloader"),
        ("Reboot → Recovery",    "reboot recovery"),
        ("ADB over WiFi",        "tcpip 5555"),
        ("List Packages",        "shell pm list packages"),
        ("Device Properties",    "shell getprop"),
    ]
    def __init__(self, get_device, log_fn, parent=None):
        super().__init__(parent)
        self._get_device = get_device; self._log = log_fn
        self.setStyleSheet(f"background:{CB_BG};")
        lay = QVBoxLayout(self); lay.setContentsMargins(20,16,20,16); lay.setSpacing(14)
        lay.addWidget(lbl("Toolbox", 14, bold=True))
        grid = QGridLayout(); grid.setSpacing(10)
        for i,(name,cmd) in enumerate(self.TOOLS):
            tile = QPushButton(); tile.setFixedHeight(80)
            tile.setCursor(Qt.CursorShape.PointingHandCursor)
            tile.setStyleSheet(
                f"QPushButton{{background:{CC_BG};border:1px solid {CC_BOR};"
                f"border-radius:10px;text-align:left;padding:10px;}}"
                f"QPushButton:hover{{border:1px solid {CACC};background:#F8FAFF;}}")
            tl = QVBoxLayout(tile); tl.setContentsMargins(12,10,12,10); tl.setSpacing(4)
            tl.addWidget(lbl(name, 12, bold=True))
            tl.addWidget(lbl(f"adb {cmd}", 10, color=CMUTED))
            tile.clicked.connect(lambda _,c=cmd: self._run(c))
            grid.addWidget(tile, i//2, i%2)
        lay.addLayout(grid); lay.addStretch()

    def _run(self, cmd):
        self._log(f"$ adb {cmd}")
        if not BACKEND: self._log("(demo – no backend)"); return
        try:
            dev = self._get_device()
            serial = dev.get("serial") if dev else None
            adb = ADBInterface(_Logger())
            if cmd.startswith("shell "):
                ok, out = adb.shell(cmd[6:], device=serial)
            else:
                # use adb.run_adb_command if available, else shell
                if hasattr(adb, 'run_adb_command'):
                    ok, out = adb.run_adb_command(cmd.split(), device=serial)
                else:
                    ok, out = adb.shell(cmd, device=serial)
            self._log((out or "").strip()[:600] or ("OK" if ok else "Failed"))
        except Exception as e:
            self._log(f"Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# CONSOLE PAGE
# ══════════════════════════════════════════════════════════════════════════════
class ConsolePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{CB_BG};")
        lay = QVBoxLayout(self); lay.setContentsMargins(20,16,20,16); lay.setSpacing(8)
        hdr = QHBoxLayout()
        hdr.addWidget(lbl("Console Output", 14, bold=True)); hdr.addStretch()
        clr = btn_ghost("Clear"); clr.setFixedWidth(70); hdr.addWidget(clr)
        lay.addLayout(hdr)
        self._area = QTextEdit(); self._area.setReadOnly(True)
        self._area.setFont(QFont(_MONO, 10))
        self._area.setStyleSheet(
            f"background:#0D1117;border-radius:8px;color:#58A6FF;"
            f"padding:10px;border:1px solid {CC_BOR};")
        lay.addWidget(self._area, 1)
        clr.clicked.connect(self._area.clear)

    def append(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self._area.append(
            f'<span style="color:#6E7681">[{ts}]</span>'
            f' <span style="color:#E6EDF3">{msg}</span>')
        self._area.moveCursor(self._area.textCursor().MoveOperation.End)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Android Servicing Tool")
        self.setMinimumSize(1100, 720)
        self._device_info: dict = {}
        self._detector = DeviceDetector(_Logger()) if BACKEND else None

        p = QPalette()
        p.setColor(QPalette.ColorRole.Window,     QColor(CB_BG))
        p.setColor(QPalette.ColorRole.WindowText, QColor(CMAIN))
        p.setColor(QPalette.ColorRole.Base,       QColor(CC_BG))
        p.setColor(QPalette.ColorRole.Text,       QColor(CMAIN))
        self.setPalette(p)
        self.setStyleSheet(f"QMainWindow{{background:{CB_BG};}}")

        root_w = QWidget(); self.setCentralWidget(root_w)
        root = QVBoxLayout(root_w); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        self._header = DeviceHeader()
        self._header.refresh_requested.connect(self._refresh)
        root.addWidget(self._header)

        body = QHBoxLayout(); body.setContentsMargins(0,0,0,0); body.setSpacing(0)
        self._nav = NavRail(); self._nav.page_changed.connect(self._switch)
        body.addWidget(self._nav)

        self._console = ConsolePage()
        self._home     = HomePage()
        self._exploits = ExploitsPage(lambda: self._device_info, self._log)
        self._security = SecurityPage(lambda: self._device_info, self._log)
        self._profiles = ProfilesPage(self._log)
        self._toolbox  = ToolboxPage(lambda: self._device_info, self._log)

        self._stack = QStackedWidget()
        for pg in [self._home, self._exploits, self._security,
                   self._profiles, self._toolbox, self._console]:
            self._stack.addWidget(pg)
        body.addWidget(self._stack, 1)

        bw = QWidget(); bw.setLayout(body); root.addWidget(bw, 1)
        self._home.action.connect(self._home_action)

        # status bar
        sb = self.statusBar()
        sb.setStyleSheet(
            f"background:{CSTATUS};color:{CMUTED};"
            "font-size:11px;border-top:1px solid #DDE1E7;")
        self._sb_dev = QLabel("No device")
        self._sb_be  = QLabel(f"Backend: {'✅ Ready' if BACKEND else '⚠ UI-only'}")
        self._sb_be.setStyleSheet(f"color:{'#16A34A' if BACKEND else CORANGE};font-size:11px;")
        sb.addWidget(self._sb_dev); sb.addPermanentWidget(self._sb_be)

        try:
            self._tray = QSystemTrayIcon(QIcon(), self); self._tray.setVisible(True)
        except Exception:
            self._tray = None

        self._log("Android Servicing Tool started.")
        if BACKEND:
            self._log("✅ Backend loaded – ExploitManager / DeviceProfileManager / SecurityAdvisor ready.")
        else:
            self._log("⚠  Backend not found – UI-only / demo mode.")
        QTimer.singleShot(300, self._refresh)

        # auto-poll every 5 s when no device connected
        self._poll = QTimer(self)
        self._poll.setInterval(5000)
        self._poll.timeout.connect(self._auto_poll)
        self._poll.start()

    def _auto_poll(self):
        if not self._device_info:
            self._refresh()

    def _log(self, msg):
        self._console.append(msg)
        self.statusBar().showMessage(msg, 3000)

    def _switch(self, idx): self._stack.setCurrentIndex(idx)

    def _home_action(self, key):
        if key == "security":
            self._nav.select(2); self._stack.setCurrentIndex(2)
            QTimer.singleShot(100, self._security._assess)
        else:
            self._nav.select(1); self._stack.setCurrentIndex(1)
            QTimer.singleShot(100, lambda: self._exploits.run(key))

    def _refresh(self):
        self._log("Scanning for devices…")
        if not BACKEND:
            self._apply({"model":"Demo Device","serial":"DEMO001","mode":"adb",
                         "android_version":"14","manufacturer":"Demo","chipset":"Unknown",
                         "platform":"android"})
            return

        def _detect():
            try:
                raw = self._detector.detect_device()
                if not raw: return {}
                # Normalise: ensure keys the exploits expect are present
                info = dict(raw)
                # brand / manufacturer normalisation
                if "brand" not in info:
                    info["brand"] = info.get("manufacturer","")
                if "manufacturer" not in info:
                    info["manufacturer"] = info.get("brand","")
                # platform default
                if "platform" not in info:
                    info["platform"] = "android"
                return info
            except Exception as e:
                self._log(f"Detection error: {e}"); return {}

        def _done():
            self._apply(_detect())

        QTimer.singleShot(0, _done)

    def _apply(self, info: dict):
        self._device_info = info
        self._header.update(info)
        if info:
            model = f"{info.get('manufacturer','')} {info.get('model','')}".strip()
            self._sb_dev.setText(f"Device: {model}  [{info.get('serial','?')}]")
            self._log(f"Device: {model}  serial={info.get('serial','?')}  mode={info.get('mode','?')}")
            if self._tray:
                try:
                    self._tray.showMessage("Device Connected", model,
                        QSystemTrayIcon.MessageIcon.Information, 2000)
                except Exception: pass
        else:
            self._sb_dev.setText("No device"); self._log("No device detected.")


# ── entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Windows: enable DPI awareness
    if platform.system() == "Windows":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont(_FONT, 10))
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
