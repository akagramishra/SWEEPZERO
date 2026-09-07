from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QProgressBar
)


class StatTile(QWidget):
    def __init__(self, label, value="--"):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setSpacing(2)
    
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(
            "color: #e6edf3; font-family: monospace; font-size: 26px;"
        )

        self.name_label = QLabel(label)
        self.name_label.setStyleSheet("color: #8b949e; font-size: 11px;")

        layout.addWidget(self.value_label)
        layout.addWidget(self.name_label)

    def set_value(self, text):
        self.value_label.setText(text)


class StatsPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setSpacing(24)

        self.hits = StatTile("hits", "0 / 0")
        self.accuracy = StatTile("accuracy", "0.0 %")
        self.confidence = StatTile("model confidence", "0.00")

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(6)
        self.bar.setStyleSheet("""
            QProgressBar { background: #21262d; border: none; }
            QProgressBar::chunk { background: #39c5cf; }
        """)

        conf_block = QVBoxLayout()
        conf_block.addWidget(self.confidence)
        conf_block.addWidget(self.bar)

        layout.addWidget(self.hits)
        layout.addWidget(self.accuracy)
        layout.addLayout(conf_block)
        layout.addStretch()

    def update_stats(self, hits, total, confidence):
        self.hits.set_value(f"{hits} / {total}")

        accuracy = (hits / total * 100) if total else 0.0
        self.accuracy.set_value(f"{accuracy:.1f} %")

        self.confidence.set_value(f"{confidence:.2f}")
        self.bar.setValue(int(confidence * 100))