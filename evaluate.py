from RFEnvironment import RFEnvironment
from receiver import Receiver
from Newscheduler import AdaptiveScheduler

class RoundRobinScheduler:
    def __init__(self, num_bands):
        self.num_bands = num_bands
        self.next_band = 0

    def decide(self, timestep, receiver_history):
        band = self.next_band
        self.next_band = (self.next_band + 1) % self.num_bands
        return band


def run(scheduler_cls, env, verbose=False):
    receiver = Receiver(env)
    scheduler = scheduler_cls(env.num_bands)
    hits = 0
    band_visits = {}

    for t in range(env.num_timesteps):
        band = scheduler.decide(t, receiver.history)
        value = receiver.observe(band, t)
        hits += value
        band_visits[band] = band_visits.get(band, 0) + 1

    if verbose:
        print("Band visits:", band_visits)

    return hits


if __name__ == "__main__":
    rr_total = 0
    adaptive_total = 0
    max_total = 0

    for seed in range(25):
        env = RFEnvironment(num_timesteps=1000, seed=seed)
        rr_total += run(RoundRobinScheduler, env)
        adaptive_total += run(AdaptiveScheduler, env)
        max_total += env.ground_truth.sum()

    print(f"RoundRobin total: {rr_total} / {max_total}  (avg {rr_total/25:.1f} per run)")
    print(f"Adaptive total:   {adaptive_total} / {max_total}  (avg {adaptive_total/25:.1f} per run)")
