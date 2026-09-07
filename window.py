from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from panels.spectrum import SpectrumPanel
from panels.sweep import SweepPanel
from panels.stats import StatsPanel
from panels.stats import StatTile
from headers import HeaderPanel
from theme import framed


class MainWindow(QMainWindow):
    def __init__(self):
        
        super().__init__()
        icon = QIcon("assets/icon_main.png")
        self.setWindowTitle("SweepZero")
        self.setWindowIcon(icon)
        self.resize(1000, 800)

        self.sweep = SweepPanel()
        self.spectrum = SpectrumPanel()
        self.stats = StatsPanel()
        self.stattile = StatTile("Hits", "0 / 0")
        
        central = QWidget()
        self.setCentralWidget(central)

        self.master_layout = QVBoxLayout(central)

        self.row_layout_Header = QHBoxLayout()
        self.row_layout_Middle = QHBoxLayout()
        self.row_layout_Footer = QHBoxLayout()

        self.master_layout.addLayout(self.row_layout_Header, 20)
        self.master_layout.addLayout(self.row_layout_Middle, 30)
        self.master_layout.addLayout(self.row_layout_Footer,20)

        self.row_layout_Middle.setContentsMargins(12, 0, 12, 0)  # left, top, right, bottom
        self.row_layout_Middle.setSpacing(12)                     # gap between the two tiles

        self.header = HeaderPanel()
        self.row_layout_Header.addWidget(self.header)

        #here is the Sweep Panel
        self.row_layout_Middle.addWidget(framed(self.sweep, "Sweep"), 40)

        #Here is the Spectrum Panel
        self.row_layout_Middle.addWidget(framed(self.spectrum, "RF Spectrum"), 40)

        #Here is the Stats Panel
        self.row_layout_Footer.addWidget(framed(self.stats, "Statistics"), 40)

        #Here is the Hits Panel
        self.row_layout_Footer.addWidget(framed(self.stattile, "Hits"), 20)

        self.t = 0.0
        self.dt = 0.033

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(33)

    def tick(self):
        self.t += self.dt

        self.sweep.advance()
        self.spectrum.update_spectrum()
        self.header.update_header(self.t, "X")
        self.stats.update_stats(4, 5, 0.88)


