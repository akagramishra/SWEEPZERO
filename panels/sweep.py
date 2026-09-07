import math

from PySide6.QtCore import Qt, QRectF, QPointF, QTimer
from PySide6.QtGui import QPainter, QPen, QColor, QConicalGradient, QBrush
from PySide6.QtWidgets import QWidget


class SweepPanel(QWidget):
    RINGS = 5
    TRAIL_DEG = 50
    RPM = 20

    def __init__(self):
        super().__init__()
        self.angle = 0.0
        # (bearing_deg, range_fraction, last_seen_angle)
        self.contacts = [
            [37.0, 0.62, None],
            [154.0, 0.85, None],
            [268.0, 0.40, None],
            [311.0, 0.72, None],
        ]

    
    def advance(self):
        step = self.RPM * 360 / 60 * 0.033
        prev = self.angle
        self.angle = (self.angle + step) % 360

        for c in self.contacts:
            if self._swept_ar(prev, self.angle, c[0]):
                c[2] = self.angle
        self.update()

    def _swept_ar(self, a, b, target):
        if b < a:
            return target >= a or target <= b
        return a <= target <= b

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        radius = min(w, h) / 2 - 10
        p.translate(w / 2, h / 2)

        p.setPen(QPen(QColor("#21262d"), 1))
        for i in range(1, self.RINGS + 1):
            r = radius * i / self.RINGS
            p.drawEllipse(QRectF(-r, -r, 2 * r, 2 * r))
        for deg in range(0, 360, 30):
            rad = math.radians(deg)
            p.drawLine(QPointF(0, 0),
                       QPointF(radius * math.cos(rad), radius * math.sin(rad)))

        grad = QConicalGradient(0, 0, -self.angle)
        grad.setColorAt(0.0, QColor(57, 197, 207, 110))
        grad.setColorAt(self.TRAIL_DEG / 360, QColor(57, 197, 207, 0))
        grad.setColorAt(1.0, QColor(57, 197, 207, 0))
        p.setBrush(QBrush(grad))
        p.setPen(Qt.NoPen)
        p.drawPie(QRectF(-radius, -radius, 2 * radius, 2 * radius),
                  int(-self.angle * 16), int(-self.TRAIL_DEG * 16))

        rad = math.radians(self.angle)
        p.setPen(QPen(QColor("#39c5cf"), 2))
        p.drawLine(QPointF(0, 0),
                   QPointF(radius * math.cos(rad), radius * math.sin(rad)))

        for bearing, rng, seen in self.contacts:
            if seen is None:
                continue
            age = (self.angle - seen) % 360
            alpha = max(0, int(255 * (1 - age / 360)))
            b = math.radians(bearing)
            x, y = radius * rng * math.cos(b), radius * rng * math.sin(b)
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(63, 185, 80, alpha))
            p.drawEllipse(QPointF(x, y), 4, 4)