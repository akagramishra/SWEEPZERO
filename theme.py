"""
Visual design system for SweepZero.

Nothing in here knows anything about scheduling, emitters or the receiver —
it is purely tokens (colour / type / spacing), a global Qt stylesheet, and the
`framed()` tile helper that every panel is wrapped in.
"""

from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                               QWidget, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


# ----------------------------------------------------------------- palette
# Cool blue-black ground so the cyan reads as phosphor rather than neon.
BG          = "#05080B"   # app ground, bottom of gradient
BG_TOP      = "#0A1117"   # app ground, top of gradient
PANEL       = "#0B1218"   # tile surface
PANEL_INSET = "#070C11"   # recessed screens (spectrum plot)
LINE        = "#1B2832"   # tile border
LINE_SOFT   = "#132029"   # hairline rules
TRACK       = "#111C24"   # progress-bar groove

INK         = "#D8E4E9"   # primary text
INK_DIM     = "#7E959E"   # secondary text
INK_FAINT   = "#4C616C"   # labels, axis ticks

CYAN        = "#35D6E0"   # primary accent
CYAN_DIM    = "#17777F"   # accent, low state
CYAN_RGB    = (53, 214, 224)
GREEN       = "#46D07F"   # contacts / live status
GREEN_RGB   = (70, 208, 127)
AMBER       = "#F2B44C"   # reserved: warnings

MONO_STACK = ["Cascadia Mono", "Consolas", "DejaVu Sans Mono", "Courier New"]
UI_STACK   = ["Segoe UI Variable Display", "Segoe UI", "Inter", "Arial"]


def mono(px=12, weight=QFont.Weight.Normal, tracking=0.0):
    """Monospace face — used for every number, label and readout."""
    f = QFont()
    f.setFamilies(MONO_STACK)
    f.setPixelSize(px)
    f.setWeight(weight)
    if tracking:
        f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, tracking)
    return f


def ui(px=13, weight=QFont.Weight.Normal, tracking=0.0):
    """UI face — used for titles and prose."""
    f = QFont()
    f.setFamilies(UI_STACK)
    f.setPixelSize(px)
    f.setWeight(weight)
    if tracking:
        f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, tracking)
    return f


# -------------------------------------------------------------- stylesheet
APP_QSS = f"""
QMainWindow {{
    background: qlineargradient(x1:0, y1:0, x2:0.35, y2:1,
                stop:0 {BG_TOP}, stop:1 {BG});
}}

QMainWindow > QWidget {{
    background: transparent;
}}

QWidget {{
    color: {INK};
    font-family: "Segoe UI Variable Display", "Segoe UI", Inter, Arial, sans-serif;
    font-size: 13px;
}}

QLabel {{
    background: transparent;
}}

QFrame#tile {{
    background: {PANEL};
    border: 1px solid {LINE};
    border-radius: 8px;
}}

QFrame#rule {{
    background: {LINE_SOFT};
    border: none;
}}

QLabel#tileTick {{
    background: {CYAN};
    border: none;
    border-radius: 1px;
}}

QLabel#chip {{
    color: {INK_DIM};
    background: {PANEL};
    border: 1px solid {LINE};
    border-radius: 5px;
    padding: 5px 11px;
}}

QLabel#chipAccent {{
    color: {CYAN};
    background: rgba(53, 214, 224, 22);
    border: 1px solid rgba(53, 214, 224, 60);
    border-radius: 5px;
    padding: 5px 11px;
}}

QProgressBar {{
    background: {TRACK};
    border: none;
    border-radius: 4px;
}}

QProgressBar::chunk {{
    border-radius: 4px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {CYAN_DIM}, stop:1 {CYAN});
}}

QPlainTextEdit#logView {{
    background: transparent;
    border: none;
    color: {INK_DIM};
    selection-background-color: rgba(53, 214, 224, 70);
    selection-color: {INK};
}}

QScrollBar:vertical {{
    background: transparent;
    width: 9px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: #253440;
    border-radius: 4px;
    min-height: 26px;
}}

QScrollBar::handle:vertical:hover {{
    background: #314654;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}
"""


# ------------------------------------------------------------------- tile
def framed(widget, title=None, subtitle=None):
    """
    Wrap any widget in a titled tile.

    `subtitle` is optional and describes, in plain words, what the panel is
    actually showing — so nobody has to guess whether a figure is a live
    measurement or ground truth.

    Existing two-argument calls keep working unchanged.
    """
    frame = QFrame()
    frame.setObjectName("tile")

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(14, 12, 14, 14)
    layout.setSpacing(10)

    if title:
        head = QWidget()
        head.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        head_col = QVBoxLayout(head)
        head_col.setContentsMargins(0, 0, 0, 0)
        head_col.setSpacing(4)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(9)

        tick = QLabel()
        tick.setObjectName("tileTick")
        tick.setFixedSize(3, 11)

        label = QLabel(title.upper())
        label.setObjectName("tileTitle")
        label.setFont(mono(10, QFont.Weight.DemiBold, 1.9))
        label.setStyleSheet(f"color: {INK_DIM};")

        title_row.addWidget(tick)
        title_row.addWidget(label)
        title_row.addStretch()
        head_col.addLayout(title_row)

        if subtitle:
            sub = QLabel(subtitle)
            sub.setObjectName("tileSubtitle")
            sub.setFont(mono(10))
            sub.setStyleSheet(f"color: {INK_FAINT}; padding-left: 12px;")
            head_col.addWidget(sub)

        layout.addWidget(head)

        rule = QFrame()
        rule.setObjectName("rule")
        rule.setFixedHeight(1)
        layout.addWidget(rule)

    layout.addWidget(widget)
    return frame
