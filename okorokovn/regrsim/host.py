import math
import random
import joblib

class Host:
    def __init__(
        self,
        interval,
        cable_delay,
        target_delay,
        switch_delay=0,
        nhops=0,
        cwnd=1,
        aimd=(0.5, 0.5),
        scaling=True,
    ):
        self.start = round(interval[0])
        self.end = round(interval[1])
        self.cable_delay = cable_delay
        self.switch_delay = switch_delay
        self.hops_delay = nhops * (cable_delay + switch_delay)
        self.target_delay = target_delay
        self.cwnd = cwnd
        self.alpha_inc = aimd[0]
        self.beta_dec = aimd[1]
        self.scaling = scaling
        self.next = 0
        self.total_acked = 0
        self.async_delay = random.random()
        self.base_target = 1.1 * cable_delay
        self.mdf_max = 0.5
        self.min_cwnd = 0.001
        self.max_cwnd = int(self.base_target + self.hops_delay)
        self.fs_min_cwnd = 0.1
        self.fs_max_cwnd = self.max_cwnd
        self.fs_range = target_delay - self.base_target
        self.alpha = self.fs_range / (1.0 / math.sqrt(self.fs_min_cwnd) - 1.0 / math.sqrt(self.fs_max_cwnd))
        self.beta = -self.alpha / math.sqrt(self.fs_max_cwnd)
        if cwnd < 1:
            self.pacing_delay = self.cable_delay * (1.0 / cwnd - 1.0)
        else:
            self.pacing_delay = 0
        self.last_decrease = 0
        self.usage = [0, 0, 0, 0, 0, 0, 0, 0]
        self.prev_rtt = None
        
        # Loading model
        self.model = joblib.load('model.pkl')

    def target(self, cwnd):
        if self.scaling:
            return (
                self.base_target
                + self.hops_delay
                + max(0, min(self.alpha / math.sqrt(cwnd) + self.beta, self.fs_range))
            )
        return self.target_delay

    def process_event(self, rtt, delay, now):
        cwnd_prev = self.cwnd
        can_decrease = (now - self.last_decrease) >= rtt
        target_delay = self.target(self.cwnd)
        
        first = 1
        if self.prev_rtt:
            prev_rtt = self.prev_rtt
            first = 0
        else:
            prev_rtt = rtt
        self.prev_rtt = rtt
        
        self.total_acked += 1
        
        self.cwnd = self.model.predict([
            cwnd_prev,
            int(can_decrease),
            target_delay,
            self.total_acked,
            self.pacing_delay,
            rtt,
            prev_rtt,
            delay,
            now,])

        return (
            cwnd_prev,
            int(can_decrease),
            target_delay,
            self.total_acked,
            self.pacing_delay,
            first,
            rtt,
            prev_rtt,
            delay,
            now,
            self.cwnd,
            [0],
        )