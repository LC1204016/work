import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from datas import Network

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


class NetworkVisualization:
    def __init__(self, network: Network):
        self.network = network
        self.names = network.get_names()
        self.x, self.y = network.get_coordinates()
        self.adjacency = network.get_adjacency_matrix()
        self.n = network.n
    
    def plot_network(self, flow_matrix=None, title="交通网络"):
        """绘制交通网络图，可选显示流量"""
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # 绘制节点
        for i in range(self.n):
            ax.scatter(self.x[i], self.y[i], s=500, c='lightblue', edgecolors='black', zorder=2)
            ax.text(self.x[i], self.y[i], self.names[i], fontsize=12, ha='center', va='center', fontweight='bold')
        
        # 绘制边和流量
        max_flow = max([max(row) for row in flow_matrix]) if flow_matrix and any(any(row) for row in flow_matrix) else 1
        
        for i in range(self.n):
            for j in range(i + 1, self.n):
                if self.adjacency[i][j]:
                    # 计算边的流量（双向之和）
                    flow = 0
                    if flow_matrix:
                        flow = flow_matrix[i][j] + flow_matrix[j][i]
                    
                    # 根据流量确定边的颜色和粗细
                    if flow > 0:
                        # 归一化流量到[0, 1]范围
                        normalized_flow = min(flow / max_flow, 1.0) if max_flow > 0 else 0
                        color = plt.cm.Reds(normalized_flow)
                        linewidth = 1 + 4 * normalized_flow  # 线宽从1到5
                    else:
                        color = 'gray'
                        linewidth = 1
                    
                    # 绘制边
                    ax.plot([self.x[i], self.x[j]], [self.y[i], self.y[j]], 
                           color=color, linewidth=linewidth, zorder=1)
                    
                    # 标注流量
                    if flow > 0:
                        mid_x = (self.x[i] + self.x[j]) / 2
                        mid_y = (self.y[i] + self.y[j]) / 2
                        ax.text(mid_x, mid_y + 0.5, f'{flow:.0f}', 
                               fontsize=10, ha='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        # 设置图表属性
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('X坐标 (km)', fontsize=12)
        ax.set_ylabel('Y坐标 (km)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.set_aspect('equal')
        
        # 添加图例
        if flow_matrix and any(any(row) for row in flow_matrix):
            # 创建流量图例
            legend_elements = []
            flow_values = [0, max_flow * 0.25, max_flow * 0.5, max_flow * 0.75, max_flow]
            labels = ['0', f'{max_flow * 0.25:.0f}', f'{max_flow * 0.5:.0f}', 
                     f'{max_flow * 0.75:.0f}', f'{max_flow:.0f}']
            
            for flow_val, label in zip(flow_values, labels):
                if flow_val == 0:
                    color = 'gray'
                    linewidth = 1
                else:
                    normalized_flow = flow_val / max_flow
                    color = plt.cm.Reds(normalized_flow)
                    linewidth = 1 + 4 * normalized_flow
                
                legend_elements.append(plt.Line2D([0], [0], color=color, linewidth=linewidth, 
                                                label=f'流量: {label} 辆/小时'))
            
            ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
        
        plt.tight_layout()
        return fig, ax
    
    def compare_algorithms(self, flow_matrices, algorithm_names):
        """比较不同算法的分配结果"""
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        axes = axes.flatten()
        
        for idx, (flow_matrix, algorithm_name) in enumerate(zip(flow_matrices, algorithm_names)):
            ax = axes[idx]
            
            # 绘制节点
            for i in range(self.n):
                ax.scatter(self.x[i], self.y[i], s=300, c='lightblue', edgecolors='black', zorder=2)
                ax.text(self.x[i], self.y[i], self.names[i], fontsize=10, ha='center', va='center', fontweight='bold')
            
            # 绘制边和流量
            max_flow = max([max(row) for row in flow_matrix]) if flow_matrix and any(any(row) for row in flow_matrix) else 1
            
            for i in range(self.n):
                for j in range(i + 1, self.n):
                    if self.adjacency[i][j]:
                        # 计算边的流量（双向之和）
                        flow = 0
                        if flow_matrix:
                            flow = flow_matrix[i][j] + flow_matrix[j][i]
                        
                        # 根据流量确定边的颜色和粗细
                        if flow > 0:
                            normalized_flow = min(flow / max_flow, 1.0) if max_flow > 0 else 0
                            color = plt.cm.Reds(normalized_flow)
                            linewidth = 1 + 3 * normalized_flow
                        else:
                            color = 'gray'
                            linewidth = 1
                        
                        # 绘制边
                        ax.plot([self.x[i], self.x[j]], [self.y[i], self.y[j]], 
                               color=color, linewidth=linewidth, zorder=1)
                        
                        # 标注流量
                        if flow > 0:
                            mid_x = (self.x[i] + self.x[j]) / 2
                            mid_y = (self.y[i] + self.y[j]) / 2
                            ax.text(mid_x, mid_y + 0.3, f'{flow:.0f}', 
                                   fontsize=8, ha='center', bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))
            
            # 设置子图属性
            total_time = self.network.calculate_total_travel_time(flow_matrix)
            ax.set_title(f'{algorithm_name}\n总出行时间: {total_time:.1f} 分钟', fontsize=12, fontweight='bold')
            ax.set_xlabel('X坐标 (km)', fontsize=10)
            ax.set_ylabel('Y坐标 (km)', fontsize=10)
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.set_aspect('equal')
        
        plt.tight_layout()
        return fig, axes
    
    def save_plot(self, fig, filename):
        """保存图表到文件"""
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"图表已保存到 {filename}")