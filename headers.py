from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QFrame
from PySide6.QtGui import QFont

from theme import mono, ui, INK, INK_DIM, CYAN, GREEN, LINE


class HeaderPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(14)

        # accent bar — anchors the wordmark to the left edge
        bar = QFrame()
        bar.setFixedWidth(3)
        bar.setStyleSheet(f"background: {CYAN}; border: none; border-radius: 1px;")

        title = QLabel("EW SCAN CONSOLE")
        title.setFont(ui(21, QFont.Weight.DemiBold, 3.2))
        title.setStyleSheet(f"color: {INK};")

        self.clock = QLabel("T + 000.000 s")
        self.clock.setObjectName("chip")
        self.clock.setFont(mono(13, QFont.Weight.Medium, 0.6))

        self.band = QLabel("band: --")
        self.band.setObjectName("chipAccent")
        self.band.setFont(mono(13, QFont.Weight.DemiBold, 0.6))

        self.status = QLabel("\u25cf  SIM")
        self.status.setFont(mono(11, QFont.Weight.DemiBold, 1.6))
        self.status.setStyleSheet(f"color: {GREEN};")

        layout.addWidget(bar)
        layout.addWidget(title)
        layout.addSpacing(6)
        layout.addWidget(self.clock)
        layout.addWidget(self.band)
        layout.addStretch()
        layout.addWidget(self.status)

    def update_header(self, t, band):
        self.clock.setText(f"T + {t:07.3f} s")
        self.band.setText(f"band: {band}")
