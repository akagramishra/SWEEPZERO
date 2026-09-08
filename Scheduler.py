# schedulers.py
import numpy as np
import random

class PatternScheduler:
    def __init__(self, num_bands):
        self.num_bands = num_bands

    def decide(self, timestep, receiver_history):
        # On first timestep, pick band 0 (or could also random)
        if timestep == 0:
            return 0

        # Group observed hits by band (only v==1)
        obs_by_band = {b: [] for b in range(self.num_bands)}
        for t, b, v in receiver_history:
            if v == 1:
                obs_by_band[b].append(t)

        # Predict next active timestep for each band
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
                        # confidence decreases with distance
                        confidence = 1.0 / (abs(timestep - next_time) + 1)
                        predictions[band] = confidence
            elif len(times) == 1:
                predictions[band] = 0.1   # low confidence for one hit
            else:
                predictions[band] = 0.0   # no hits yet

        # Pick band with highest confidence
        if predictions:
            max_conf = max(predictions.values())
            if max_conf == 0.0:
                # No known pattern – explore randomly
                return random.randint(0, self.num_bands - 1)
            best_band = max(predictions, key=predictions.get)
            return best_band
        else:
            return 0