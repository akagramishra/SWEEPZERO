from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt



def framed(widget, title=None):
    frame = QFrame()
    frame.setObjectName("tile")
    frame.setStyleSheet("""
        QFrame#tile {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 4px;
        }
    """)

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(8, 8, 8, 8)

    if title:
        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #8b949e; font-size: 31px; border: 1px;")
        layout.addWidget(label)

    layout.addWidget(widget)
    return frame