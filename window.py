from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget
from PySide6.QtCore import QTimer, Qt
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
        self.resize(1180, 840)

        NUM_BANDS = 10

        self.env = RFEnvironment(num_bands=NUM_BANDS, seed=42)
        self.receiver = Receiver(self.env)
        self.scheduler = AdaptiveScheduler(NUM_BANDS)
        self.current_timestep = 0

        self.total_hits = 0
        self.total_misses = 0
        self.running_max_possible = 0

        # bands we have ever detected, and bands whose period the scheduler
        # has now confirmed — both only used to decide what is worth logging
        self.seen_bands = set()
        self.locked_bands = set()
        self.last_hit_at = {}

        self.sweep = SweepPanel()
        self.spectrum = SpectrumPanel()
        self.stats = StatsPanel()
        self.stattile = StatTile("caught / occurred", "0 / 0")
        self.actionlog = ActionLogPanel(
            "Action Log",
            "detections and pattern locks · newest at the bottom",
        )

        central = QWidget()
        self.setCentralWidget(central)
        self.master_layout = QVBoxLayout(central)
        self.master_layout.setContentsMargins(16, 12, 16, 16)
        self.master_layout.setSpacing(14)

        self.row_layout_Header = QHBoxLayout()
        self.row_layout_Middle = QHBoxLayout()
        self.row_layout_Footer = QHBoxLayout()

        self.master_layout.addLayout(self.row_layout_Header, 22)
        self.master_layout.addLayout(self.row_layout_Middle, 52)
        self.master_layout.addLayout(self.row_layout_Footer, 18)

        for row in (self.row_layout_Header,
                    self.row_layout_Middle,
                    self.row_layout_Footer):
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(14)

        self.header = HeaderPanel()
        self.header.setFixedHeight(58)
        self.row_layout_Header.addWidget(self.header, 52, Qt.AlignTop)
        self.row_layout_Header.addWidget(self.actionlog, 48)

        self.row_layout_Middle.addWidget(
            framed(self.sweep, "Sweep",
                   "antenna rotation, 20 rpm · display only"), 40)
        self.row_layout_Middle.addWidget(
            framed(self.spectrum, "RF Spectrum",
                   "ground truth · every emitter on air, not receiver output"), 40)

        self.row_layout_Footer.addWidget(
            framed(self.stats, "Statistics",
                   "what the scheduler found, measured two ways"), 40)
        self.row_layout_Footer.addWidget(
            framed(self.stattile, "Detections",
                   "emissions caught · of those that occurred"), 20)

        self.t = 0.0
        self.dt = 0.033
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(33)

    def _log_event(self, band, value):
        """
        Decide whether this tick is worth a line in the action log.

        At 30 ticks a second, logging every scan would be an unreadable blur,
        so only detections are reported — plus the two moments that actually
        say something about what the scheduler has learned.

        This only *reads* the scheduler's existing helpers; it never changes
        scheduler state.
        """
        if value != 1:
            return

        gap = self.current_timestep - self.last_hit_at.get(band, self.current_timestep)
        self.last_hit_at[band] = self.current_timestep

        if band not in self.seen_bands:
            self.seen_bands.add(band)
            self.actionlog.log(self.current_timestep, band, "FIRST CONTACT", "new")
        elif band in self.locked_bands:
            # already predicting this one — the interval is the interesting part
            self.actionlog.log(
                self.current_timestep, band, f"TRACKING   +{gap}t", "track"
            )
        else:
            self.actionlog.log(self.current_timestep, band, "DETECTED", "hit")

        if band in self.locked_bands:
            return

        # three confirmed bursts is the point the scheduler starts trusting
        # its period estimate for this band — worth announcing once
        hit_times = self.scheduler._get_hits_by_band(self.receiver.history)[band]
        bursts = self.scheduler._get_burst_starts(hit_times)
        if len(bursts) >= 3:
            period = self.scheduler._estimate_period(bursts)
            self.locked_bands.add(band)
            self.actionlog.log(
                self.current_timestep, band,
                f"PATTERN LOCK  period ~{period}t", "lock"
            )

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

        self._log_event(band, value)

        self.t += self.dt
        self.current_timestep += 1


