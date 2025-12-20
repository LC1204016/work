import json
from math import inf, sqrt


class Network:
    def __init__(self, network_file:str, demand_file:str): # 文件名
        with open(network_file, 'r', encoding='utf-8') as f:
            network = json.load(f)
            nodes = network['nodes']
            links = network['links']

        self.names = nodes['name']
        self.x = nodes['x'] #坐标
        self.y = nodes['y']
        self.between = links['between'] # 相邻节点名
        self.capacity = links['capacity'] # 相邻节点通行能力
        self.speed_max = links['speedmax'] # 相邻节点限速
        self.n = len(self.names)

        # 读取需求数据
        with open(demand_file, 'r', encoding='utf-8') as f:
            demand = json.load(f)
        
        self.demand_from = demand['from']
        self.demand_to = demand['to']
        self.demand_amount = demand['amount']
        
        # 初始化各种矩阵
        self.time_link = [[inf] * self.n for _ in range(self.n)] # 相邻节点最短时间
        self.capacity_matrix = [[0] * self.n for _ in range(self.n)] # 通行能力矩阵
        self.adjacency = [[False] * self.n for _ in range(self.n)] # 邻接矩阵
        
        # 初始化各种矩阵
        for z, (c1, c2) in enumerate(self.between):
            i = self.names.index(c1)
            j = self.names.index(c2)
            x1, y1 = self.x[i], self.y[i]
            x2, y2 = self.x[j], self.y[j]
            distance = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            
            # 计算自由流行程时间（分钟）
            free_flow_time = 60 * distance / self.speed_max[z]
            self.time_link[i][j] = self.time_link[j][i] = free_flow_time
            self.capacity_matrix[i][j] = self.capacity_matrix[j][i] = self.capacity[z]
            self.adjacency[i][j] = self.adjacency[j][i] = True

    def get_time_link(self) -> list:
        """获取相邻节点自由流行程时间矩阵"""
        return self.time_link

    def get_names(self):
        """获取节点名称列表"""
        return self.names
    
    def get_coordinates(self):
        """获取节点坐标"""
        return self.x, self.y
    
    def get_capacity_matrix(self):
        """获取通行能力矩阵"""
        return self.capacity_matrix
    
    def get_adjacency_matrix(self):
        """获取邻接矩阵"""
        return self.adjacency
    
    def get_demand_data(self):
        """获取需求数据"""
        od_pairs = []
        for i in range(len(self.demand_from)):
            from_idx = self.names.index(self.demand_from[i])
            to_idx = self.names.index(self.demand_to[i])
            od_pairs.append((from_idx, to_idx, self.demand_amount[i]))
        return od_pairs
    
    def calculate_congested_time(self, flow_matrix):
        """根据流量计算拥堵时间"""
        congested_time = [[inf] * self.n for _ in range(self.n)]
        for i in range(self.n):
            for j in range(self.n):
                if self.adjacency[i][j] and self.capacity_matrix[i][j] > 0:
                    # 拥堵函数: t(q) = t0 * (1 + q/cap)^2
                    ratio = flow_matrix[i][j] / self.capacity_matrix[i][j]
                    congested_time[i][j] = self.time_link[i][j] * (1 + ratio) ** 2
        return congested_time
    
    def calculate_total_travel_time(self, flow_matrix):
        """计算路网总出行时间"""
        total_time = 0
        for i in range(self.n):
            for j in range(self.n):
                if self.adjacency[i][j] and flow_matrix[i][j] > 0:
                    congested_time = self.time_link[i][j] * (1 + flow_matrix[i][j] / self.capacity_matrix[i][j]) ** 2
                    total_time += congested_time * flow_matrix[i][j]
        return total_time