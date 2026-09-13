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

    def _bands_to_spectrum(self, band_data, num_bands=10):
        """
        Convert a dict of {band_index: amplitude} into a 512-point spectrum.
        band_data: {0: 1.0, 1: 0.0, 2: 0.0, ...}  — amplitude per band
        Each band maps to a chunk of the 512 frequency bins.
        Active bands get a tall peak; inactive bands get noise-floor.
        """
        spectrum = np.full(512, -100.0)  # noise floor in dBm
        bins_per_band = 512 // num_bands

        for band, amp in band_data.items():
            if amp > 0:
                start = band * bins_per_band
                end = start + bins_per_band
                center = (start + end) / 2
                peak = 40.0 * np.exp(
                    -((np.arange(512) - center) ** 2) / (2 * (bins_per_band / 3) ** 2)
                )
                spectrum += peak

        spectrum += self.rng.normal(0, 1.5, size=512)
        return spectrum

    def update_spectrum(self, band_data=None):
        """
        band_data: optional dict {band_index: amplitude}
                   e.g. {0: 0.0, 1: 0.0, 2: 1.0, 3: 1.0, ...}
                   If None, shows only the noise floor.
        """
        if band_data is None:
            power = self._bands_to_spectrum({})
        else:
            power = self._bands_to_spectrum(band_data)
        self.curve.setData(self.freqs, power)