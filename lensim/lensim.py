import importlib
import toml

from collections import namedtuple
from heapq import heappop, heappush


Target = namedtuple("Target", "name ptr")


class Event:
    def __init__(self, timestamp, target, state):
        self.timestamp = timestamp
        self.rtt = 0
        self.target = target
        self.state = state

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def process(self, process_time, new_target, new_state):
        self.rtt += process_time
        self.target = new_target
        self.state = new_state


class LenSim:
    def __init__(self, config_path="./lensim/config/exp_incast100.toml"):
        cfg = toml.load(config_path)
        nic = importlib.import_module(cfg["nic"]["module"])
        self.nic_list = {ptr: nic.NIC(ptr, cfg["nic"]) for ptr in range(cfg["nic"]["count"])}
        host = importlib.import_module(cfg["host"]["module"])
        self.host_list = {ptr: host.Host(ptr, cfg["host"]) for ptr in range(cfg["host"]["count"])}

        self.event_loop = []
        for host in self.host_list.values():
            new_event = Event(0, Target("host", host.ptr), None)
            heappush(self.event_loop, (0, new_event))

    def simulate(self):
        while self.event_loop:
            _, event = heappop(self.event_loop)
            match event.target.name:
                case "nic":
                    self.nic_list[event.target.ptr].process_event(event)
                case "host":
                    self.host_list[event.target.ptr].process_event(event)

        print("Simulation complete")

    def _info(self):
        self.nic_list[0]._info()
        self.host_list[0]._info()


if __name__ == "__main__":
    exp = LenSim()
    exp.simulate()
    exp._info()
