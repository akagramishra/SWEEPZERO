# better model since last one sucks.

import numpy as np
import random


class AdaptiveScheduler:
    def __init__(self, num_bands):
        self.num_bands = num_bands #yk total no of bands available. 


    def _get_hits_by_band(self, receiver_history):
        # Saari successful predictions ko collect karna and bandwise arrange.

        hits_by_band = {
            band: []
            for band in range(self.num_bands)
        }

        for timestep, band, value in receiver_history:
            if value == 1:
                hits_by_band[band].append(timestep)

        return hits_by_band


    def _get_burst_starts(self, hit_times):
        # this basically acts as a channi to take out successful hits that are of the same burst, and in teh end we have an array containing only unique bursts (their first hits more precisely)

        if not hit_times:
            return []

        burst_starts = [hit_times[0]]

        for i in range(1, len(hit_times)):

            current_hit = hit_times[i]
            previous_hit = hit_times[i - 1]

            if current_hit > previous_hit + 1:
                burst_starts.append(current_hit)

        return burst_starts


    def _estimate_period(self, burst_starts):

        if len(burst_starts) < 2:
            return None

        differences = np.diff(burst_starts)

        return int(np.median(differences)) # average nhi lena chahiye shayad (?)


    def _get_last_observed_time(self, band, receiver_history):
        for timestep, observed_band, value in reversed(receiver_history):
            if observed_band == band:
                return timestep
        return None    # ye agar bade number pe scale hua to bohot slow ho jayga model (i think?)


    def decide(self, timestep, receiver_history):
        if timestep == 0:
            return random.randint(0, self.num_bands - 1)
        hits_by_band = self._get_hits_by_band(receiver_history)
        scores = {}


        for band in range(self.num_bands):

            score = 0.0


            # -----------------------------------
            # 1. PERIODICITY SCORE
            # -----------------------------------

            hit_times = hits_by_band[band]

            burst_starts = self._get_burst_starts(hit_times)

            period = self._estimate_period(burst_starts)


            # need at least 3 confirming bursts before trusting a period estimate -
            # 2 points alone is too noisy (especially with jitter) and was causing
            # confident-but-wrong lock-in on bad guesses.
            if period is not None and len(burst_starts) >= 3:
                last_burst = burst_starts[-1]
                predicted_time = last_burst + period
                distance = abs(timestep - predicted_time)

                # confidence scales with how many bursts confirmed this period,
                # capping out at 5 confirming bursts.
                confidence = min(len(burst_starts) / 5, 1.0)

                if distance <= 1:  # within jitter tolerance, treat as confident
                    pattern_score = 1.0 * confidence
                else:
                    pattern_score = (1.0 / distance) * confidence
                score += pattern_score


            # -----------------------------------
            # 2. STALENESS / EXPLORATION SCORE
            # -----------------------------------

            last_checked = self._get_last_observed_time(
                band,
                receiver_history
            )


            if last_checked is None:

                # Never checked before
                exploration_score = 0.5

            else:

                time_since_check = timestep - last_checked

                # Score increases the longer
                # we've ignored this band.

                exploration_score = min(
                    time_since_check / 20,
                    0.5
                )


            score += exploration_score


            scores[band] = score


        # Pick the highest scoring band

        best_band = max(
            scores,
            key=scores.get
        )

        return best_band