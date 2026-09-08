# RFEnvironment.py
import numpy as np
import random as rd


class Emitter:
    def __init__(self, bands, period, on_duration=1, jitter=0, start_time=0):
        """
        bands: single band index (int) for fixed-frequency, or list of bands for agile
        period: how often it becomes active (timesteps)
        on_duration: how many consecutive timesteps it stays active per period
        jitter: max random offset added/subtracted from period each cycle
        start_time: timestep this emitter starts existing (for pop-up emitters)
        """
        self.bands = bands if isinstance(bands, list) else [bands]
        self.period = period
        self.on_duration = on_duration
        self.jitter = jitter
        self.start_time = start_time

    def get_active_band_at(self, t, rng):
        if t < self.start_time:
            return None  # ye bas emitter ko sahi time pe start karna.

        elapsed = t - self.start_time # emitter ke POV mein time.
        cycle_index = elapsed // self.period # kaunsa cycle chal raha hai
        cycle_pos = elapsed % self.period #emitter ki apne period mein posiition.

        #Jitter -yahan ek galti ye hui thi ki, jitter har cycle pe same hona chahiye, isse pehle wo har ek timestep ki function call pe alag alag ho raha tha, isse model ka behaviour unpredictable ho raha tha.
        if self.jitter:
            seed_val = id(self) + cycle_index
            cycle_rng = rd.Random(seed_val)
            jittered_on_start = cycle_rng.randint(-self.jitter, self.jitter)
        else:
            jittered_on_start = 0

        if jittered_on_start <= cycle_pos < jittered_on_start + self.on_duration: #Just ki aap transmission window mein ho ki nhi.
            band = self.bands[cycle_index % len(self.bands)]
            return band
        return None


class RFEnvironment:
    def __init__(self, num_bands=10, num_timesteps=200, emitters=None, seed=None):
        self.num_bands = num_bands
        self.num_timesteps = num_timesteps
        self.rng = rd.Random(seed)
        self.emitters = emitters if emitters is not None else self._default_emitters()
        self.ground_truth = self._generate_ground_truth()

    def _default_emitters(self):
        return [
            Emitter(bands=3, period=10, on_duration=2, jitter=1),          # periodic radar
            Emitter(bands=[2, 5, 8], period=15, on_duration=1, jitter=0),  # frequency-agile
            Emitter(bands=6, period=12, on_duration=2, jitter=1, start_time=80),  # pop-up
        ]

    def _generate_ground_truth(self):
        grid = np.zeros((self.num_bands, self.num_timesteps), dtype=int)
        for t in range(self.num_timesteps):
            for emitter in self.emitters:
                band = emitter.get_active_band_at(t, self.rng)
                if band is not None:
                    grid[band, t] = 1
        return grid


if __name__ == "__main__":
    env = RFEnvironment()
    print(env.ground_truth)
    print("Total active cells:", env.ground_truth.sum())