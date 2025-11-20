import json
from collections import defaultdict
from math import sqrt
from work1 import work1
# 打开文件network.json
with open('network.json', 'r', encoding='utf-8') as f:
    network = json.load(f)

# 读取数据
nodes = network['nodes']
names = nodes['name']
x_c = nodes['x']
y_c = nodes['y']

links = network['links']
between = links['between']
capacity = links['capacity']
speedmax = links['speedmax']

# 建立路网
link = defaultdict(list) #link[A] = [(B,capacity,speedmax,distance)] 终点 通行能力 限速 距离

for z,x_to_y in enumerate(between):
    x = x_to_y[0]
    y = x_to_y[1]
    x1, x2 = x_c[names.index(x)],x_c[names.index(y)]
    y1, y2 = y_c[names.index(x)],y_c[names.index(y)]
    distance = int(sqrt((x2-x1)**2 + (y2-y1)**2))
    link[x].append((y, capacity[z], speedmax[z], distance))
    link[y].append((x, capacity[z], speedmax[z], distance))

# 打开文件demand.json
with open('demand.json', 'r', encoding='utf-8') as f:
    demand = json.load(f)

# 读取数据
x_from = demand['from']
t_to = demand['to']
amount = demand['amount']

work1(link,names)