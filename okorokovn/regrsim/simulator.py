import numpy as np
import pandas as pd
from collections import deque
from heapq import heappush, heappop
from time import time


class NewSimulator:
    def __init__(self, nic_pacing=1, queue_pacing=1, logger=False):
        self.N = 0
        self.hosts = []
        self.nic_pacing = nic_pacing
        self.queue_pacing = queue_pacing
        self.usage = None
        self.logger = logger

    def add(self, host):
        self.N += 1
        self.hosts.append(host)

    def simulate(self, loops, settling=0):
        loops = round(loops)
        events = []
        queue = deque()

        lenq = np.empty(loops)
        t_acks = [[] for _ in range(self.N)]
        cwnds = [[] for _ in range(self.N)]
        rtts = [[] for _ in range(self.N)]
        n_acked = np.zeros(self.N)

        # LOGGER
        cwnd_prev_logs = []
        can_decrease_logs = []
        target_delay_logs = []
        total_acked_logs = []
        pacing_delay_logs = []
        first_logs = []
        rtt_logs = []
        prev_rtt_logs = []
        delay_logs = []
        now_logs = []
        cwnd_logs = []
        host_idx_logs = []
        time_logs = []
        # LOGGER/

        for t in range(loops):
            if t % self.queue_pacing == 0:
                while events and events[0][0] <= t:
                    _, packet = heappop(events)
                    queue.append(packet)
                if queue:
                    tsent, m, _ = queue.popleft()
                    rtt = t - tsent

                    host = self.hosts[m]
                    (
                        cwnd_prev,
                        can_decrease,
                        target_delay,
                        total_acked,
                        pacing_delay,
                        first,
                        rtt,
                        prev_rtt,
                        delay,
                        now,
                        cwnd,
                        usage,
                    ) = host.process_event(rtt, rtt, t)

                    # LOGGER
                    if self.usage:
                        self.usage = [x + y for x, y in zip(self.usage, usage)]
                    else:
                        self.usage = usage
                    cwnd_prev_logs.append(cwnd_prev)
                    can_decrease_logs.append(can_decrease)
                    target_delay_logs.append(target_delay)
                    total_acked_logs.append(total_acked)
                    pacing_delay_logs.append(pacing_delay)
                    first_logs.append(first)
                    rtt_logs.append(rtt)
                    prev_rtt_logs.append(prev_rtt)
                    delay_logs.append(delay)
                    now_logs.append(now)
                    cwnd_logs.append(cwnd)
                    host_idx_logs.append(m)
                    time_logs.append(t)
                    # LOGGER/

                    if t >= settling:
                        t_acks[m].append(t)
                        rtts[m].append(rtt)
                        cwnds[m].append(host.cwnd)
                        n_acked[m] += 1

            if t % self.nic_pacing == 0:
                for n, host in enumerate(self.hosts):
                    if host.start <= t <= host.end:
                        if host.next - host.total_acked < host.cwnd:
                            rescaled_async_delay = self.nic_pacing * host.async_delay
                            tsent = t + rescaled_async_delay + host.pacing_delay
                            packet = (tsent, n, host.next)
                            heappush(
                                events,
                                (tsent + host.cable_delay + host.hops_delay, packet),
                            )
                            host.next += 1
            lenq[t] = len(queue)

        # LOGGER
        if self.logger:
            dataset = pd.DataFrame(
                {
                    "cwnd_prev": cwnd_prev_logs,
                    "can_decrease": can_decrease_logs,
                    "target_delay": target_delay_logs,
                    "total_acked": total_acked_logs,
                    "pacing_delay": pacing_delay_logs,
                    "first": first_logs,
                    "rtt": rtt_logs,
                    "prev_rtt": prev_rtt_logs,
                    "delay": delay_logs,
                    "now": now_logs,
                    "cwnd": cwnd_logs,
                    "host_idx": host_idx_logs,
                    "time": time_logs,
                }
            )
            var = int(time())
            dataset.to_csv(f"./log/network_log2")
            print(f"Log saved to network_log2")
            print(self.usage)
        # LOGGER/

        t_acks = [np.array(result) for result in t_acks]
        cwnds = [np.array(result) for result in cwnds]
        rtts = [np.array(result) for result in rtts]
        throughputs = n_acked * self.queue_pacing / (loops - settling)
        return lenq, t_acks, cwnds, rtts, throughputs
