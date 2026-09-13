# RFEnvironment.py
import numpy as np
import random as rd

class Emitter:
    def __init__(self, bands, period, on_duration=1, jitter=0, start_time=0, emitter_id=0):
        """
        bands: single band index (int) for fixed-frequency, or list of bands for agile
        period: how often it becomes active (timesteps)
        on_duration: how many consecutive timesteps it stays active per period
        jitter: max random offset added/subtracted from period each cycle
        start_time: timestep this emitter starts existing (for pop-up emitters)
        emitter_id: stable identifier used to seed jitter deterministically
                    (id(self) was memory-address based, not truly reproducible)
        """
        self.bands = bands if isinstance(bands, list) else [bands]
        self.period = period
        self.on_duration = on_duration
        self.jitter = jitter
        self.start_time = start_time
        self.emitter_id = emitter_id

    def get_active_band_at(self, t, rng):
        if t < self.start_time:
            return None  # ye bas emitter ko sahi time pe start karna.

        elapsed = t - self.start_time  # emitter ke POV mein time.
        cycle_index = elapsed // self.period  # kaunsa cycle chal raha hai
        cycle_pos = elapsed % self.period  # emitter ki apne period mein posiition.

        # Jitter - har cycle pe same hona chahiye, har timestep pe naya nahi.
        # seeded off emitter_id (not id(self)) so it's actually reproducible
        # across runs/machines, not just an accident of memory layout.
        if self.jitter:
            seed_val = self.emitter_id * 100000 + cycle_index
            cycle_rng = rd.Random(seed_val)
            jittered_on_start = cycle_rng.randint(-self.jitter, self.jitter)
        else:
            jittered_on_start = 0

        if jittered_on_start <= cycle_pos < jittered_on_start + self.on_duration:
            band = self.bands[cycle_index % len(self.bands)]
            return band
        return None

class RFEnvironment:
    def __init__(self, num_bands=10, num_timesteps=None, emitters=None, seed=None):
        """
        num_timesteps=None  →  live / infinite mode (use is_active())
        num_timesteps=N     →  pre-generated grid mode (use .ground_truth)
        """
        self.num_bands = num_bands
        self.num_timesteps = num_timesteps
        self.rng = rd.Random(seed)
        self.emitters = emitters if emitters is not None else self._default_emitters()

        # Only pre-generate the grid if a finite length was requested
        if num_timesteps is not None:
            self.ground_truth = self._generate_ground_truth()
        else:
            self.ground_truth = None  # live mode — no grid

    def _default_emitters(self):
        return [
            Emitter(bands=3, period=10, on_duration=2, jitter=1, emitter_id=0),          # periodic radar
            Emitter(bands=[2, 5, 8], period=15, on_duration=1, jitter=0, emitter_id=1),  # frequency-agile
            Emitter(bands=6, period=12, on_duration=2, jitter=1, start_time=80, emitter_id=2),  # pop-up
        ]

    def _generate_ground_truth(self):
        grid = np.zeros((self.num_bands, self.num_timesteps), dtype=int)
        for t in range(self.num_timesteps):
            for emitter in self.emitters:
                band = emitter.get_active_band_at(t, self.rng)
                if band is not None:
                    grid[band, t] = 1
        return grid

    def is_active(self, band, timestep):
        """
        Live-query mode — no pre-generated grid needed.
        Returns 1 if the given band is transmitting at this timestep, else 0.
        """
        for emitter in self.emitters:
            active_band = emitter.get_active_band_at(timestep, self.rng)
            if active_band == band:
                return 1
        return 0

    def active_bands_at(self, timestep):
        """
        Returns a list of all bands transmitting at this timestep.
        Useful for the spectrum panel.
        """
        active = []
        for emitter in self.emitters:
            band = emitter.get_active_band_at(timestep, self.rng)
            if band is not None:
                active.append(band)
        return active

if __name__ == "__main__":
    # Quick smoke test — live mode
    env = RFEnvironment()
    for t in range(10):
        print(f"t={t}: active bands = {env.active_bands_at(t)}")

    # Grid mode still works
    env2 = RFEnvironment(num_timesteps=50, seed=42)
    print("Grid sum:", env2.ground_truth.sum())