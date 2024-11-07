from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from time import sleep
from sklearn.preprocessing import StandardScaler
import json

# Getting log info (Mininet + iperf3 + cubic)

n = 100 # number of senders
t = 100 # incast duration

class MyTopo(Topo):
    def build(self, senders_c=n):
        receiver = self.addHost('receiver')
        switch = self.addSwitch('s0')
        self.addLink(receiver, switch, bw=10 ** 3)
        sender = self.addHost('sender')
        self.addLink(sender, switch, bw=10 ** 3)
   
topo = MyTopo()
net = Mininet(topo=topo, controller=Controller)

net.start()

receiver = net.get('receiver')
receiver.cmd('iperf3 -s -p 8080 -J > ./log/receiver_log.json &')

sender = net.get('sender')
sender.cmd(f'iperf3 -c {receiver.IP()} -p 8080 -t {t} -P {n} -i 1 -C cubic -V -J > ./log/sender_log.json &')

sleep(t + 5)

net.stop()

# Dataset creating

with open('./log/sender_log.json', 'r') as file:
    lines = file.readlines()[1:] 

json_content = ''.join(lines)

try:
    data = json.loads(json_content)
except json.JSONDecodeError as e:
    print(e)

x, y = [], []

for interval in data['intervals']:
    for log in interval['streams']:
        y.append(log['snd_cwnd'])
        x.append(list(log.values())[4 : -2])

ratio = 0.2
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

# Decision tree Regression

reg = DecisionTreeRegressor(max_depth=3, random_state=42)

reg.fit(x_train, y_train)

y_pred = reg.predict(x_test)

# Result

std_y_pred = StandardScaler().fit_transform(np.array(y_pred).reshape(-1, 1))
std_y_test = StandardScaler().fit_transform(np.array(y_test).reshape(-1, 1))

print('MSE: ', mean_squared_error(std_y_test, std_y_pred), '\n', "R2: ", r2_score(y_test, y_pred))