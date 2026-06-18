import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import time

class GuijiDirectPlanner(Node):
    def __init__(self):
        super().__init__('guiji_trajectory_planner')
        self.get_logger().info("🚀 Guiji Arm Python Direct Controller Initialized!")
        
        # 🛰️ 管道 A：直接對接馬達控制器接口 (ros2_control / move_group 都在聽這個)
        self.trajectory_pub = self.create_publisher(
            JointTrajectory, 
            '/arm_controller/joint_trajectory', 
            10
        )
        
        # 🛰️ 管道 B：全域狀態強灌接口
        self.joint_state_pub = self.create_publisher(
            JointState, 
            '/joint_states', 
            10
        )
        
        # 建立一個定時器，每 0.5 秒發射一次指令
        self.timer = self.create_timer(0.5, self.timer_callback)
        self.count = 0

    def timer_callback(self):
        self.count += 1
        
        # 🎯 設定我們用 Python 指定的馬達目標角度 (弧度)
        # 這裡會讓手臂做出一個滑順往前的帥氣動作
        target_positions = [0.5, 0.3, -0.2] 
        joint_names = ['arm_0_joint', 'arm_1_joint', 'arm_2_joint']

        # 🎛️ 封裝管道 A 的軌跡控制訊息 (這是工業級控制最愛的格式)
        traj_msg = JointTrajectory()
        traj_msg.joint_names = joint_names
        
        point = JointTrajectoryPoint()
        point.positions = target_positions
        point.time_from_start.sec = 1 # 限定 1 秒內飛過去
        traj_msg.points.append(point)
        
        # 廣播出去！
        self.trajectory_pub.publish(traj_msg)

        # 🎛️ 封裝管道 B 的狀態訊息 (雙重保險)
        state_msg = JointState()
        state_msg.header.stamp = self.get_clock().now().to_msg()
        state_msg.name = joint_names
        state_msg.position = target_positions
        self.joint_state_pub.publish(state_msg)

        if self.count == 1:
            self.get_logger().info(f"🤖 [Python 發射]: 成功強灌關節目標角度: {target_positions}")
            self.get_logger().info("🔥 訊號已強行穿透命名空間，請看 RViz2 畫面！")

def main(args=None):
    rclpy.init(args=args)
    planner = GuijiDirectPlanner()
    try:
        rclpy.spin(planner)
    except KeyboardInterrupt:
        pass
    planner.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
