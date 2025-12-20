from math import inf
from datas import Network


class TrafficAssignment:
    def __init__(self, network: Network):
        self.network = network
        self.n = network.n
        self.names = network.get_names()
        self.adjacency = network.get_adjacency_matrix()
        self.capacity_matrix = network.get_capacity_matrix()
        self.time_link = network.get_time_link()
        self.od_pairs = network.get_demand_data()
    
    def floyd_warshall(self, time_matrix):
        """使用Floyd-Warshall算法计算所有节点对之间的最短路径"""
        n = self.n
        dist = [[inf] * n for _ in range(n)]
        path = [[-1] * n for _ in range(n)]
        
        # 初始化距离矩阵和路径矩阵
        for i in range(n):
            for j in range(n):
                if i == j:
                    dist[i][j] = 0
                elif self.adjacency[i][j]:
                    dist[i][j] = time_matrix[i][j]
                    path[i][j] = j
        
        # Floyd-Warshall算法
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        path[i][j] = path[i][k]
        
        return dist, path
    
    def get_path_from_path_matrix(self, path_matrix, origin, destination):
        """从路径矩阵中提取具体路径"""
        if path_matrix[origin][destination] == -1:
            return []
        
        path = [origin]
        current = origin
        while current != destination:
            current = path_matrix[current][destination]
            path.append(current)
        
        return path
    
    def all_or_nothing_assignment(self):
        """全有全无分配算法"""
        # 初始化流量矩阵
        flow_matrix = [[0] * self.n for _ in range(self.n)]
        
        # 计算自由流状态下的最短路径
        _, path_matrix = self.floyd_warshall(self.time_link)
        
        # 对每个OD对进行全有全无分配
        for origin, destination, demand in self.od_pairs:
            path = self.get_path_from_path_matrix(path_matrix, origin, destination)
            
            # 将整个需求分配到最短路径上
            for i in range(len(path) - 1):
                from_node = path[i]
                to_node = path[i + 1]
                flow_matrix[from_node][to_node] += demand
        
        return flow_matrix
    
    def incremental_assignment(self, increments=4):
        """增量分配算法"""
        # 初始化流量矩阵
        flow_matrix = [[0] * self.n for _ in range(self.n)]
        
        # 将每个OD对的需求分成若干份
        for origin, destination, demand in self.od_pairs:
            increment = demand / increments
            
            for inc in range(increments):
                # 计算当前流量状态下的拥堵时间
                congested_time = self.network.calculate_congested_time(flow_matrix)
                
                # 计算最短路径
                _, path_matrix = self.floyd_warshall(congested_time)
                
                # 获取当前最短路径
                path = self.get_path_from_path_matrix(path_matrix, origin, destination)
                
                # 将一份需求分配到当前最短路径上
                for i in range(len(path) - 1):
                    from_node = path[i]
                    to_node = path[i + 1]
                    flow_matrix[from_node][to_node] += increment
        
        return flow_matrix
    
    def frank_wolfe_assignment(self, max_iterations=10, convergence_threshold=0.01):
        """Frank-Wolfe算法（用户均衡分配）"""
        # 初始化流量矩阵
        flow_matrix = [[0] * self.n for _ in range(self.n)]
        
        for iteration in range(max_iterations):
            # 计算当前流量状态下的拥堵时间
            congested_time = self.network.calculate_congested_time(flow_matrix)
            
            # 计算最短路径
            _, path_matrix = self.floyd_warshall(congested_time)
            
            # 执行一次全有全无分配得到辅助解
            auxiliary_flow = [[0] * self.n for _ in range(self.n)]
            for origin, destination, demand in self.od_pairs:
                path = self.get_path_from_path_matrix(path_matrix, origin, destination)
                for i in range(len(path) - 1):
                    from_node = path[i]
                    to_node = path[i + 1]
                    auxiliary_flow[from_node][to_node] += demand
            
            # 计算步长（线搜索）
            step_size = self._calculate_optimal_step_size(flow_matrix, auxiliary_flow)
            
            # 更新流量
            new_flow_matrix = [[0] * self.n for _ in range(self.n)]
            for i in range(self.n):
                for j in range(self.n):
                    new_flow_matrix[i][j] = (1 - step_size) * flow_matrix[i][j] + step_size * auxiliary_flow[i][j]
            
            # 检查收敛性
            if self._check_convergence(flow_matrix, new_flow_matrix, convergence_threshold):
                break
            
            flow_matrix = new_flow_matrix
        
        return flow_matrix
    
    def _calculate_optimal_step_size(self, current_flow, auxiliary_flow):
        """计算Frank-Wolfe算法的最优步长"""
        # 简化的步长计算，实际应用中可能需要更复杂的线搜索
        return 2.0 / (2.0 + len(self.od_pairs))
    
    def _check_convergence(self, old_flow, new_flow, threshold):
        """检查算法是否收敛"""
        total_diff = 0
        total_flow = 0
        for i in range(self.n):
            for j in range(self.n):
                total_diff += abs(new_flow[i][j] - old_flow[i][j])
                total_flow += new_flow[i][j]
        
        if total_flow == 0:
            return True
        
        return total_diff / total_flow < threshold
    
    def print_assignment_results(self, flow_matrix, algorithm_name):
        """打印分配结果"""
        print(f"\n=== {algorithm_name}分配结果 ===")
        
        # 打印各路段流量
        print("\n各路段流量:")
        for i in range(self.n):
            for j in range(i + 1, self.n):
                if self.adjacency[i][j] and flow_matrix[i][j] > 0:
                    print(f"{self.names[i]}-{self.names[j]}: {flow_matrix[i][j]:.1f} 辆/小时")
        
        # 计算总出行时间
        total_time = self.network.calculate_total_travel_time(flow_matrix)
        print(f"\n路网总出行时间: {total_time:.1f} 分钟")
        
        # 打印各OD对的路径和时间
        print("\n各OD对路径和行程时间:")
        congested_time = self.network.calculate_congested_time(flow_matrix)
        _, path_matrix = self.floyd_warshall(congested_time)
        
        for origin, destination, demand in self.od_pairs:
            path = self.get_path_from_path_matrix(path_matrix, origin, destination)
            path_names = [self.names[node] for node in path]
            
            # 计算路径总时间
            path_time = 0
            for i in range(len(path) - 1):
                path_time += congested_time[path[i]][path[i + 1]]
            
            print(f"{self.names[origin]} → {self.names[destination]}: 需求={demand}, "
                  f"路径={'→'.join(path_names)}, 时间={path_time:.1f}分钟")