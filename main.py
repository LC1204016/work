from datas import Network
from algorithms import TrafficAssignment
from visualization import NetworkVisualization
import os


def main():
    """主程序"""
    print("=== 交通分配计算软件 ===\n")
    
    # 初始化网络
    network = Network('network.json', 'demand.json')
    assignment = TrafficAssignment(network)
    visualization = NetworkVisualization(network)
    
    # 创建输出目录
    if not os.path.exists('output'):
        os.makedirs('output')
    
    print("1. 不考虑拥堵，任意两点间的最快的路径是什么？")
    print("=" * 50)
    
    # 计算自由流状态下的最短路径
    time_link = network.get_time_link()
    _, path_matrix = assignment.floyd_warshall(time_link)
    
    names = network.get_names()
    for i in range(len(names)):
        for j in range(len(names)):
            if i != j:
                path = assignment.get_path_from_path_matrix(path_matrix, i, j)
                if path:
                    path_names = [names[node] for node in path]
                    path_time = 0
                    for k in range(len(path) - 1):
                        path_time += time_link[path[k]][path[k + 1]]
                    print(f"{names[i]} → {names[j]}: {' → '.join(path_names)}, 时间: {path_time:.1f} 分钟")
    
    print("\n2. 交通分配算法比较")
    print("=" * 50)
    
    # 全有全无分配
    print("\n正在执行全有全无分配...")
    all_or_nothing_flow = assignment.all_or_nothing_assignment()
    assignment.print_assignment_results(all_or_nothing_flow, "全有全无")
    
    # 增量分配
    print("\n正在执行增量分配...")
    incremental_flow = assignment.incremental_assignment(increments=4)
    assignment.print_assignment_results(incremental_flow, "增量分配")
    
    # Frank-Wolfe算法
    print("\n正在执行Frank-Wolfe算法...")
    frank_wolfe_flow = assignment.frank_wolfe_assignment(max_iterations=10)
    assignment.print_assignment_results(frank_wolfe_flow, "Frank-Wolfe")
    
    print("\n3. 单个OD对分析 (A → F)")
    print("=" * 50)
    
    # 获取A到F的索引
    a_idx = names.index('A')
    f_idx = names.index('F')
    
    # 分析A到F的路径
    for algorithm_name, flow_matrix in [("全有全无", all_or_nothing_flow), 
                                       ("增量分配", incremental_flow), 
                                       ("Frank-Wolfe", frank_wolfe_flow)]:
        print(f"\n{algorithm_name}算法下A→F的分配:")
        
        # 计算拥堵时间
        congested_time = network.calculate_congested_time(flow_matrix)
        _, path_matrix = assignment.floyd_warshall(congested_time)
        
        # 获取A到F的最短路径
        path = assignment.get_path_from_path_matrix(path_matrix, a_idx, f_idx)
        path_names = [names[node] for node in path]
        
        # 计算路径时间和流量
        path_time = 0
        path_flows = []
        for k in range(len(path) - 1):
            from_node = path[k]
            to_node = path[k + 1]
            path_time += congested_time[from_node][to_node]
            path_flows.append(flow_matrix[from_node][to_node])
        
        print(f"路径: {' → '.join(path_names)}")
        print(f"总时间: {path_time:.1f} 分钟")
        print("各路段流量:")
        for k in range(len(path) - 1):
            print(f"  {names[path[k]]} → {names[path[k+1]]}: {path_flows[k]:.1f} 辆/小时")
    
    print("\n4. 可视化结果")
    print("=" * 50)
    
    # 生成各种算法的可视化结果
    algorithms = [
        (all_or_nothing_flow, "全有全无分配"),
        (incremental_flow, "增量分配"),
        (frank_wolfe_flow, "Frank-Wolfe算法")
    ]
    
    # 单独保存每种算法的结果
    for flow_matrix, algorithm_name in algorithms:
        fig, ax = visualization.plot_network(flow_matrix, algorithm_name)
        filename = f"output/{algorithm_name.replace(' ', '_')}.png"
        visualization.save_plot(fig, filename)
    
    # 比较图
    flow_matrices = [flow for flow, _ in algorithms]
    algorithm_names = [name for _, name in algorithms]
    fig, axes = visualization.compare_algorithms(flow_matrices, algorithm_names)
    visualization.save_plot(fig, "output/算法比较.png")
    
    print("\n所有结果已保存到 output/ 目录")


if __name__ == "__main__":
    main()