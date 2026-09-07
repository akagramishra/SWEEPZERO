import numpy as np
import pyqtgraph as pg


class SpectrumPanel(pg.PlotWidget):
    def __init__(self):
        super().__init__()

        self.setBackground("#0d1117")
        self.setLabel("bottom", "Frequency", units="MHz")
        self.setLabel("left", "Power", units="dBm")
        self.showGrid(x=True, y=True, alpha=0.2)
        self.setYRange(-110, -50)
        

        self.freqs = np.linspace(8000, 12000, 512)

        self.curve = self.plot(
            pen=pg.mkPen("#39c5cf", width=1),
            fillLevel=-110,
            brush=(57, 197, 207, 40),
        )

        self.rng = np.random.default_rng(20260911)
        self.update_spectrum()

    def make_fake_power(self):
        noise = self.rng.normal(-95, 2.0, size=self.freqs.size)
        peak_a = 32 * np.exp(-((self.freqs - 9350) ** 2) / (2 * 25**2))
        peak_b = 14 * np.exp(-((self.freqs - 9820) ** 2) / (2 * 20**2))
        return noise + peak_a + peak_b

    def update_spectrum(self, power=None):
        if power is None:
            power = self.make_fake_power()
        self.curve.setData(self.freqs, power)