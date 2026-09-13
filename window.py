from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon

from panels.spectrum import SpectrumPanel
from panels.sweep import SweepPanel
from panels.stats import StatsPanel, StatTile
from headers import HeaderPanel
from theme import framed
from panels.actionlog import ActionLogPanel

from RFEnvironment import RFEnvironment
from receiver import Receiver
from Newscheduler import AdaptiveScheduler


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        icon = QIcon("assets/icon_main.png")
        self.setWindowTitle("SweepZero")
        self.setWindowIcon(icon)
        self.resize(1000, 800)

        NUM_BANDS = 10

        self.env = RFEnvironment(num_bands=NUM_BANDS, seed=42)
        self.receiver = Receiver(self.env)
        self.scheduler = AdaptiveScheduler(NUM_BANDS)
        self.current_timestep = 0

        self.total_hits = 0
        self.total_misses = 0
        self.running_max_possible = 0

        self.sweep = SweepPanel()
        self.spectrum = SpectrumPanel()
        self.stats = StatsPanel()
        self.stattile = StatTile("Hits", "0 / 0")
        self.actionlog = ActionLogPanel("Action Log (cs)");

        central = QWidget()
        self.setCentralWidget(central)
        self.master_layout = QVBoxLayout(central)

        self.row_layout_Header = QHBoxLayout()
        self.row_layout_Middle = QHBoxLayout()
        self.row_layout_Footer = QHBoxLayout()

        self.master_layout.addLayout(self.row_layout_Header, 20)
        self.master_layout.addLayout(self.row_layout_Middle, 30)
        self.master_layout.addLayout(self.row_layout_Footer, 20)

        self.row_layout_Middle.setContentsMargins(12, 0, 12, 0)
        self.row_layout_Middle.setSpacing(12)

        self.row_layout_Header.setContentsMargins(12, 0, 12, 0)
        self.row_layout_Header.setSpacing(12)

        self.header = HeaderPanel()
        self.row_layout_Header.addWidget(self.header)
        self.row_layout_Header.addWidget(self.actionlog, 30)

        self.row_layout_Middle.addWidget(framed(self.sweep, "Sweep"), 40)
        self.row_layout_Middle.addWidget(framed(self.spectrum, "RF Spectrum"), 40)

        self.row_layout_Footer.addWidget(framed(self.stats, "Statistics"), 40)
        self.row_layout_Footer.addWidget(framed(self.stattile, "Hits"), 20)

        self.t = 0.0
        self.dt = 0.033
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(33)

    def tick(self):
        band = self.scheduler.decide(self.current_timestep, self.receiver.history)

        value = self.receiver.observe(band, self.current_timestep)

        active_now = self.env.active_bands_at(self.current_timestep)
        self.running_max_possible += len(active_now)

        if value == 1:
            self.total_hits += 1
        else:
            self.total_misses += 1
        total_scans = self.total_hits + self.total_misses

        # crude "confidence" stand-in: hit rate over what's actually been found so far
        confidence = self.total_hits / max(self.running_max_possible, 1)

        self.header.update_header(self.current_timestep, str(band))
        self.stats.update_stats(self.total_hits, total_scans, confidence)
        self.stattile.set_value(f"{self.total_hits} / {self.running_max_possible}")

        self.sweep.advance()

        freq_data = {
            b: 1.0 if b in active_now else 0.0
            for b in range(self.env.num_bands)
        }
        self.spectrum.update_spectrum(freq_data)

        self.t += self.dt
        self.current_timestep += 1