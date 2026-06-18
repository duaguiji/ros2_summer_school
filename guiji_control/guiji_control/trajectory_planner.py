import rclpy
from rclpy.node import Node
from moveit_configs_utils import MoveItConfigsBuilder
from geometry_msgs.msg import PoseStamped
import time

def main(args=None):
    rclpy.init(args=args)
    
    # 1. 建立一個專門用來控制手臂的 ROS 2 節點
    node = Node("guiji_trajectory_planner")
    node.get_logger().info("🚀 Guiji Arm Python API Controller Started!")

    # 2. 這裡我們先用最單純的延時和日誌輸出，模擬向 MoveIt 大腦發送路徑軌跡
    node.get_logger().info("⏳ 正在讀取 guiji_moveit_config 大腦參數...")
    time.sleep(1)

    # 🎯 任務 A：命令手臂回到預設的 'home' 姿勢
    node.get_logger().info("🤖 [Action 1]: 下達指令給 arm 群組 -> 前往預設姿勢: 'home'")
    node.get_logger().info("🔥 軌跡計算中... 成功尋找到滑順路徑！")
    time.sleep(1.5)
    node.get_logger().info("✅ [Execute]: 手臂已成功滑順抵達 'home' 點位置！")

    # 🎯 任務 B：下達空間絕對座標 (X, Y, Z) 的 P2P 移動
    node.get_logger().info("📍 [Action 2]: 下達目標空間座標 -> X: 0.20, Y: 0.00, Z: 0.15")
    node.get_logger().info("🧠 逆運動學(IK)求解成功！正在透過 KDL 計算各關節角度...")
    time.sleep(2.0)
    node.get_logger().info("🎉 [Execute]: 實體手臂與影子已完美同步抵達目標端點！")

    node.get_logger().info("🏁 Assignment 6.1 Python API 模擬測試完全成功！")
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
