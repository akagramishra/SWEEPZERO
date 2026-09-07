from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout


class HeaderPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(20)

        title = QLabel("EW SCAN CONSOLE")
        title.setStyleSheet(
            "color: #e6edf3; font-size: 19px; letter-spacing: 2px;"
        )

        self.clock = QLabel("T + 000.000 s")
        self.clock.setStyleSheet(
            "color: #8b949e; font-family: monospace; font-size: 14px;"
        )

        self.band = QLabel("band: --")
        self.band.setStyleSheet(
            "color: #39c5cf; font-family: monospace; font-size: 14px;"
        )

        self.status = QLabel("● SIM")
        self.status.setStyleSheet("color: #3fb950; font-size: 15px;")

        layout.addWidget(title)
        layout.addWidget(self.clock)
        layout.addWidget(self.band)
        layout.addStretch()
        layout.addWidget(self.status)

    def update_header(self, t, band):
        self.clock.setText(f"T + {t:07.3f} s")
        self.band.setText(f"band: {band}")