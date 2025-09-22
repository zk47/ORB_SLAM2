import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

# 设置中文字体支持
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial Unicode MS"]
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

def read_tum_trajectory(file_path):
    """
    读取TUM格式的轨迹文件
    TUM格式: 时间戳 tx ty tz qx qy qz qw
    """
    trajectory = []
    with open(file_path, 'r') as f:
        for line in f:
            # 忽略注释和空行
            if line.startswith('#') or line.strip() == '':
                continue
            
            # 分割数据并转换为浮点数
            try:
                data = list(map(float, line.strip().split()))
                if len(data) == 8:  # 确保是完整的TUM格式数据
                    timestamp = data[0]
                    tx, ty, tz = data[1], data[2], data[3]
                    qx, qy, qz, qw = data[4], data[5], data[6], data[7]
                    trajectory.append([timestamp, tx, ty, tz, qx, qy, qz, qw])
                else:
                    print(f"警告: 无效的数据行，跳过: {line}")
            except ValueError:
                print(f"警告: 无法解析的数据行，跳过: {line}")
    
    return np.array(trajectory)

def visualize_trajectory(trajectory, title="相机轨迹可视化 (TUM格式)"):
    """可视化3D轨迹"""
    if len(trajectory) == 0:
        print("没有可可视化的轨迹数据")
        return
    
    # 提取位置信息
    tx = trajectory[:, 1]
    ty = trajectory[:, 2]
    tz = trajectory[:, 3]
    
    # 创建3D图形
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # 绘制轨迹
    ax.plot(tx, ty, tz, label='相机轨迹', linewidth=2)
    
    # 标记起点和终点
    ax.scatter(tx[0], ty[0], tz[0], c='green', s=100, label='起点')
    ax.scatter(tx[-1], ty[-1], tz[-1], c='red', s=100, label='终点')
    
    # 设置坐标轴标签
    ax.set_xlabel('X (米)')
    ax.set_ylabel('Y (米)')
    ax.set_zlabel('Z (米)')
    
    # 设置标题和图例
    ax.set_title(title)
    ax.legend()
    
    # 设置坐标轴比例相等，便于观察
    max_range = max([
        np.max(tx) - np.min(tx),
        np.max(ty) - np.min(ty),
        np.max(tz) - np.min(tz)
    ])
    mid_x = (np.max(tx) + np.min(tx)) / 2
    mid_y = (np.max(ty) + np.min(ty)) / 2
    mid_z = (np.max(tz) + np.min(tz)) / 2
    
    ax.set_xlim(mid_x - max_range/2, mid_x + max_range/2)
    ax.set_ylim(mid_y - max_range/2, mid_y + max_range/2)
    ax.set_zlim(mid_z - max_range/2, mid_z + max_range/2)
    
    plt.show()

def main():
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='可视化TUM格式的轨迹文件')
    parser.add_argument('file_path', nargs='?', default='trajectory.txt', 
                      help='TUM轨迹文件路径 (默认: trajectory.txt)')
    args = parser.parse_args()
    
    # 读取轨迹数据
    print(f"正在读取轨迹文件: {args.file_path}")
    trajectory = read_tum_trajectory(args.file_path)
    
    if len(trajectory) > 0:
        print(f"成功读取 {len(trajectory)} 个轨迹点")
        # 可视化轨迹
        visualize_trajectory(trajectory)
    else:
        print("未能读取到有效的轨迹数据")

if __name__ == "__main__":
    main()
