import math

from PySide6.QtCore import Qt, QRectF, QPointF, QTimer
from PySide6.QtGui import (
    QPainter, QPen, QColor, QConicalGradient, QBrush, QRadialGradient, QFont
)
from PySide6.QtWidgets import QWidget, QSizePolicy

from theme import mono, CYAN_RGB, GREEN_RGB


class SweepPanel(QWidget):
    RINGS = 5
    TRAIL_DEG = 50
    RPM = 20 #rads/s

    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(240, 240)
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
        p.setRenderHint(QPainter.Antialiasing)#meaning that the edges will be smotoehr

        w, h = self.width(), self.height()
        radius = min(w, h) / 2 - 16
        if radius <= 0:
            return
        p.translate(w / 2, h / 2)

        cr, cg, cb = CYAN_RGB
        gr, gg, gb = GREEN_RGB
        scope = QRectF(-radius, -radius, 2 * radius, 2 * radius)

        # --- scope glass -------------------------------------------------
        ground = QRadialGradient(0, 0, radius)
        ground.setColorAt(0.0, QColor(17, 42, 48))
        ground.setColorAt(0.55, QColor(10, 25, 31))
        ground.setColorAt(1.0, QColor(6, 13, 18))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(ground))
        p.drawEllipse(scope)

        # --- graticule: spokes then range rings --------------------------
        p.setPen(QPen(QColor(cr, cg, cb, 26), 1))
        for deg in range(0, 360, 30):
            rad = math.radians(deg)
            p.drawLine(QPointF(0, 0),
                       QPointF(radius * math.cos(rad), radius * math.sin(rad)))

        p.setBrush(Qt.NoBrush)
        for i in range(1, self.RINGS + 1):
            r = radius * i / self.RINGS
            outer = (i == self.RINGS)
            p.setPen(QPen(QColor(cr, cg, cb, 78 if outer else 32),
                          1.4 if outer else 1.0))
            p.drawEllipse(QRectF(-r, -r, 2 * r, 2 * r))

        # range readout, stacked just left of the vertical so it never
        # collides with the N bearing label
        p.setFont(mono(9))
        p.setPen(QPen(QColor(cr, cg, cb, 85)))
        for i in range(1, self.RINGS + 1):
            r = radius * i / self.RINGS
            p.drawText(QRectF(-72, -r + 2, 54, 13),
                       Qt.AlignRight | Qt.AlignVCenter, f"{i * 20}")

        # cardinal bearings — Qt's y axis points down, so 270 deg is up
        p.setFont(mono(9, QFont.Weight.DemiBold, 1.2))
        p.setPen(QPen(QColor(cr, cg, cb, 125)))
        for deg, tag in ((270, "N"), (0, "E"), (90, "S"), (180, "W")):
            rad = math.radians(deg)
            lx = (radius - 13) * math.cos(rad)
            ly = (radius - 13) * math.sin(rad)
            p.drawText(QRectF(lx - 10, ly - 8, 20, 16), Qt.AlignCenter, tag)

        # --- afterglow wedge ---------------------------------------------
        # Both the wedge and its gradient run anticlockwise from the beam,
        # which is the side the beam has already passed over.
        trail = self.TRAIL_DEG / 360
        grad = QConicalGradient(0, 0, -self.angle)
        grad.setColorAt(0.0, QColor(cr, cg, cb, 150))
        grad.setColorAt(trail * 0.25, QColor(cr, cg, cb, 78))
        grad.setColorAt(trail * 0.60, QColor(cr, cg, cb, 30))
        grad.setColorAt(trail, QColor(cr, cg, cb, 0))
        grad.setColorAt(1.0, QColor(cr, cg, cb, 0))
        p.setBrush(QBrush(grad))
        p.setPen(Qt.NoPen)
        p.drawPie(scope, int(-self.angle * 16), int(self.TRAIL_DEG * 16))

        # --- sweep line, drawn three times for the bloom ------------------
        rad = math.radians(self.angle)
        tip = QPointF(radius * math.cos(rad), radius * math.sin(rad))
        for width, alpha in ((7.0, 24), (3.5, 55), (1.6, 235)):
            p.setPen(QPen(QColor(cr, cg, cb, alpha), width,
                          Qt.SolidLine, Qt.RoundCap))
            p.drawLine(QPointF(0, 0), tip)

        # centre hub
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(cr, cg, cb, 55))
        p.drawEllipse(QPointF(0, 0), 6.0, 6.0)
        p.setBrush(QColor(cr, cg, cb, 220))
        p.drawEllipse(QPointF(0, 0), 2.4, 2.4)

        # --- contacts -----------------------------------------------------
        for bearing, rng, seen in self.contacts:
            if seen is None:
                continue
            age = (self.angle - seen) % 360
            alpha = max(0, int(255 * (1 - age / 360)))
            fade = alpha / 255
            b = math.radians(bearing)
            x, y = radius * rng * math.cos(b), radius * rng * math.sin(b)
            pt = QPointF(x, y)

            p.setPen(Qt.NoPen)
            p.setBrush(QColor(gr, gg, gb, int(42 * fade)))
            p.drawEllipse(pt, 10.0, 10.0)

            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(gr, gg, gb, int(130 * fade)), 1.0))
            p.drawEllipse(pt, 6.5, 6.5)

            p.setPen(Qt.NoPen)
            p.setBrush(QColor(gr, gg, gb, alpha))
            p.drawEllipse(pt, 3.2, 3.2)
