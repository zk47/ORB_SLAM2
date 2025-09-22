import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

# 设置中文字体支持
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial Unicode MS"]
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

def quaternion_to_rotation_matrix(q):
    """
    将四元数转换为旋转矩阵
    q: 四元数，格式为 [qx, qy, qz, qw]
    """
    qx, qy, qz, qw = q
    return np.array([
        [1 - 2*qy**2 - 2*qz**2, 2*qx*qy - 2*qz*qw, 2*qx*qz + 2*qy*qw],
        [2*qx*qy + 2*qz*qw, 1 - 2*qx**2 - 2*qz**2, 2*qy*qz - 2*qx*qw],
        [2*qx*qz - 2*qy*qw, 2*qy*qz + 2*qx*qw, 1 - 2*qx**2 - 2*qy**2]
    ])

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

def visualize_trajectory(trajectory, title="相机轨迹与姿态可视化 (TUM格式)", pose_step=10, axis_length=0.08):
    """
    可视化3D轨迹及相机姿态
    pose_step: 每隔多少个点绘制一次姿态坐标轴（默认10）
    axis_length: 姿态坐标轴的长度（默认0.08米，更短的箭头）
    """
    if len(trajectory) == 0:
        print("没有可可视化的轨迹数据")
        return
    
    # 提取位置和姿态信息
    tx = trajectory[:, 1]
    ty = trajectory[:, 2]
    tz = trajectory[:, 3]
    quaternions = trajectory[:, 4:8]  # 提取四元数 [qx, qy, qz, qw]
    
    # 创建3D图形
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # 绘制轨迹
    ax.plot(tx, ty, tz, label='相机轨迹', linewidth=2, alpha=0.7)
    
    # 标记起点和终点
    ax.scatter(tx[0], ty[0], tz[0], c='green', s=100, label='起点')
    ax.scatter(tx[-1], ty[-1], tz[-1], c='red', s=100, label='终点')
    
    # 绘制相机姿态（每隔pose_step个点绘制一次）
    for i in range(0, len(trajectory), pose_step):
        # 获取位置
        x, y, z = tx[i], ty[i], tz[i]
        
        # 获取四元数并转换为旋转矩阵
        q = quaternions[i]
        rot_mat = quaternion_to_rotation_matrix(q)
        
        # 计算相机坐标系的三个轴在世界坐标系中的方向
        x_axis = rot_mat[:, 0] * axis_length  # X轴（红色）
        y_axis = rot_mat[:, 1] * axis_length  # Y轴（绿色）
        z_axis = rot_mat[:, 2] * axis_length  # Z轴（蓝色）
        
        # 绘制更短的坐标轴箭头
        ax.quiver(x, y, z, x_axis[0], x_axis[1], x_axis[2], color='r', length=axis_length, normalize=True)
        ax.quiver(x, y, z, y_axis[0], y_axis[1], y_axis[2], color='g', length=axis_length, normalize=True)
        ax.quiver(x, y, z, z_axis[0], z_axis[1], z_axis[2], color='b', length=axis_length, normalize=True)
    
    # 添加姿态坐标轴图例
    ax.scatter([], [], [], c='r', label='X轴 (右)')
    ax.scatter([], [], [], c='g', label='Y轴 (下)')
    ax.scatter([], [], [], c='b', label='Z轴 (前)')
    
    # 设置坐标轴标签
    ax.set_xlabel('X (米)')
    ax.set_ylabel('Y (米)')
    ax.set_zlabel('Z (米)')
    
    # 设置标题和图例
    ax.set_title(title)
    ax.legend()
    
    # 保持坐标轴比例一致
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
    parser = argparse.ArgumentParser(description='可视化TUM格式的轨迹文件及相机姿态')
    parser.add_argument('file_path', nargs='?', default='trajectory.txt', 
                      help='TUM轨迹文件路径 (默认: trajectory.txt)')
    parser.add_argument('--pose-step', type=int, default=10, 
                      help='每隔多少个点绘制一次姿态坐标轴 (默认: 10)')
    parser.add_argument('--axis-length', type=float, default=0.08, 
                      help='姿态坐标轴的长度 (默认: 0.08米，更短的箭头)')
    args = parser.parse_args()
    
    # 读取轨迹数据
    print(f"正在读取轨迹文件: {args.file_path}")
    trajectory = read_tum_trajectory(args.file_path)
    
    if len(trajectory) > 0:
        print(f"成功读取 {len(trajectory)} 个轨迹点")
        # 可视化轨迹和姿态
        visualize_trajectory(trajectory, 
                           pose_step=args.pose_step, 
                           axis_length=args.axis_length)
    else:
        print("未能读取到有效的轨迹数据")

if __name__ == "__main__":
    main()
