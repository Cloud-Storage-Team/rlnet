from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel 
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.node import Controller
from time import sleep
import threading
import numpy as np

n = 10

vals = []

def target_cwnd(senders):
    for _ in range(10):
        for i in range(len(senders)):
            res: str = senders[i].cmd('ss -i | grep -o \'cwnd:[0-9]*\'')
            vals.append(int(res[5:]))
            print(senders[i].cmd('ss -i | grep -o \'cwnd:[0-9]*\''))
        sleep(1)

class MyTopo(Topo):
    def build(self, senders_c=n):
        receiver = self.addHost('receiver')
        switch = self.addSwitch('s0')
        self.addLink(receiver, switch)
        for i in range(0, senders_c):
            sender_i = self.addHost(f'sender{i}')
            self.addLink(sender_i, switch)
   
topo = MyTopo()
net = Mininet(topo=topo, controller=Controller)

net.start()

receiver = net.get('receiver')
receiver.cmd('sysctl -w net.ipv4.tcp_congestion_control=bbr')
receiver.cmd('iperf -s -p 10101 > /dev/null 2>&1 &')

senders = []
for i in range(n):
    sender = net.get(f'sender{i}')
    senders.append(sender)
    sender.cmd('sysctl -w net.ipv4.tcp_congestion_control=bbr')
    sender.cmd(f'iperf -c {receiver.IP()} -p 10101 -t 10 > /dev/null 2>&1 &')

t = threading.Thread(target=target_cwnd, args=([senders]))
t.daemon = True
t.start()

sleep(10)

net.stop()

print(np.mean(vals))
