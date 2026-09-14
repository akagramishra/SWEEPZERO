from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QProgressBar, QFrame,
    QSizePolicy
)

from theme import mono, INK, INK_DIM, INK_FAINT, CYAN, LINE_SOFT


class StatTile(QWidget):
    def __init__(self, label, value="--"):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(7)

        self.value_label = QLabel(value)
        self.value_label.setFont(mono(30, QFont.Weight.Medium, -0.4))
        self.value_label.setStyleSheet(f"color: {INK};")

        self.name_label = QLabel(label.upper())
        self.name_label.setFont(mono(9, QFont.Weight.DemiBold, 1.8))
        self.name_label.setStyleSheet(f"color: {INK_FAINT};")

        layout.addWidget(self.value_label)
        layout.addWidget(self.name_label)
        layout.addStretch()

    def set_value(self, text):
        self.value_label.setText(text)


def _divider():
    line = QFrame()
    line.setFixedWidth(1)
    line.setStyleSheet(f"background: {LINE_SOFT}; border: none;")
    return line


class StatsPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 6, 4, 2)
        layout.setSpacing(26)

        # labels name the actual quantity: the first is how many scans
        # found something, the last is how much of the traffic we caught
        self.hits = StatTile("detections / scans", "0 / 0")
        self.accuracy = StatTile("scan hit rate", "0.0 %")
        self.confidence = StatTile("recall of all emissions", "0.00")

        # the accuracy figure is the one a viewer should land on first
        self.accuracy.value_label.setStyleSheet(f"color: {CYAN};")

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(7)

        self.confidence.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        conf_block = QVBoxLayout()
        conf_block.setSpacing(9)
        conf_block.addWidget(self.confidence)
        conf_block.addWidget(self.bar)
        conf_block.addStretch()

        layout.addWidget(self.hits)
        layout.addWidget(_divider())
        layout.addWidget(self.accuracy)
        layout.addWidget(_divider())
        layout.addLayout(conf_block)
        layout.addStretch()

    def update_stats(self, hits, total, confidence):
        self.hits.set_value(f"{hits} / {total}")

        accuracy = (hits / total * 100) if total else 0.0
        self.accuracy.set_value(f"{accuracy:.1f} %")

        self.confidence.set_value(f"{confidence:.2f}")
        self.bar.setValue(int(confidence * 100))
