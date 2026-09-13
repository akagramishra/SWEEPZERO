import numpy as np
import random

class PatternScheduler:
    def __init__(self, num_bands):
        self.num_bands = num_bands

    def decide(self, timestep, receiver_history):
        if timestep == 0:
            return 0

        obs_by_band = {b: [] for b in range(self.num_bands)}
        for t, b, v in receiver_history:
            if v == 1:
                obs_by_band[b].append(t)

        predictions = {}
        for band in range(self.num_bands):
            times = obs_by_band[band]
            if len(times) >= 2:
                diffs = np.diff(times)
                period = int(np.median(diffs)) if len(diffs) > 0 else None
                if period is not None and period > 0:
                    next_time = times[-1] + period
                    if next_time == timestep:
                        predictions[band] = 1.0
                    else:
                        confidence = 1.0 / (abs(timestep - next_time) + 1)
                        predictions[band] = confidence
            elif len(times) == 1:
                predictions[band] = 0.1
            else:
                predictions[band] = 0.0

        if predictions:
            max_conf = max(predictions.values())
            if max_conf == 0.0:
                return random.randint(0, self.num_bands - 1)
            best_band = max(predictions, key=predictions.get)
            return best_band
        else:
            return 0