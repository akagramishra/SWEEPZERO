
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


    def _get_scans_by_band(self, receiver_history):
        # total scans per band, hit ya miss dono count — dead bands pehchanne ke liye
        scans_by_band = {}
        for timestep, band, value in receiver_history:
            scans_by_band[band] = scans_by_band.get(band, 0) + 1
        return scans_by_band


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

        # Use recent intervals so old behavior does not dominate the current estimate.
        recent_differences = differences[-5:]

        # Median is still used because it is more resistant to jitter/outliers than mean.
        return int(np.median(recent_differences)) # average nhi lena chahiye shayad (?)


    def _estimate_period_consistency(self, burst_starts):

        if len(burst_starts) < 3:
            return 0.0

        differences = np.diff(burst_starts)
        recent_differences = differences[-5:]

        median_period = np.median(recent_differences)

        if median_period <= 0:
            return 0.0

        deviation = np.median(
            np.abs(recent_differences - median_period)
        )

        consistency = 1.0 - min(
            deviation / median_period,
            1.0
        )

        return consistency


    def _estimate_jitter(self, burst_starts, period):

        if period is None or len(burst_starts) < 3:
            return 0.0

        differences = np.diff(burst_starts)
        recent_differences = differences[-5:]

        jitter = np.median(
            np.abs(recent_differences - period)
        )

        return float(jitter)


    def _get_last_observed_time(self, band, receiver_history):
        for timestep, observed_band, value in reversed(receiver_history):
            if observed_band == band:
                return timestep
        return None    # ye agar bade number pe scale hua to bohot slow ho jayga model (i think?)


    def decide(self, timestep, receiver_history):
        if timestep == 0:
            return random.randint(0, self.num_bands - 1)
        hits_by_band = self._get_hits_by_band(receiver_history)
        scans_by_band = self._get_scans_by_band(receiver_history)
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

                # tolerance widened to 2 — matches jitter + on_duration>1 bursts,
                # distance<=1 was too strict and missed the real window.
                jitter = self._estimate_jitter(
                    burst_starts,
                    period
                )

                consistency = self._estimate_period_consistency(
                    burst_starts
                )

                adaptive_tolerance = max(
                    2,
                    int(np.ceil(jitter + 1))
                )

                if distance <= adaptive_tolerance:
                    pattern_score = 1.0 * confidence
                else:
                    pattern_score = (
                        1.0 / distance
                    ) * confidence

                pattern_score *= consistency

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

                # decay slowed down + ceiling raised — 20 was capping out too fast,
                # making all stale bands look equally stale after just 10 steps.
                exploration_score = 1.0 - np.exp(
                    -time_since_check / 40
                )


            score += exploration_score


            # -----------------------------------
            # 3. DEAD-BAND PENALTY
            # -----------------------------------
            # agar band bohot baar scan hui hai but hits bohot kam/zero hain,
            # to thoda downweight karo — taaki scans genuinely uncertain
            # bands pe jayein, consistently-empty bands pe nahi.

            scan_count = scans_by_band.get(band, 0)
            hit_count = len(hit_times)

            if scan_count >= 5:
                empty_ratio = 1.0 - min(hit_count / scan_count, 1.0)
                score *= (1.0 - empty_ratio * 0.3)


            scores[band] = score


        # Pick the highest scoring band

        best_band = max(
            scores,
            key=scores.get
        )

        return best_band
