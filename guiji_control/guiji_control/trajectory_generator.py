#!/usr/bin/env list
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math

class TrajectoryGenerator(Node):

    def __init__(self):
        super().__init__('trajectory_generator')
        
        # 1. 建立 Publisher，發布到 /joint_states 管道，隊列大小為 10
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # 2. 建立定時器（Timer），每 0.05 秒（50毫秒）執行一次更新回呼函式
        self.timer_period = 0.05  # 50 ms
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        
        # 3. 定義軌跡點 (定義 5 個關節姿態點，讓手臂在這 5 個姿勢間平滑移動)
        # 每個姿勢包含 5 個關節：[arm_0_joint, arm_1_joint, arm_2_joint, gripper_left_joint, gripper_right_joint]
        self.waypionts = [
            [0.0,   0.0,   0.0,   0.0,  0.0],   # 姿勢 1：初始原點
            [1.57,  0.5,   -0.5,  0.04, 0.04],  # 姿勢 2：轉向右邊、手臂微彎、夾爪張開
            [0.0,   1.0,   0.5,   0.0,  0.0],   # 姿勢 3：回到前方、手臂往前探、夾爪閉合
            [-1.57, -0.5,  1.0,   0.04, 0.04],  # 姿勢 4：轉向左邊、手臂舉高、夾爪張開
            [0.0,   -1.0,  -0.5,  0.0,  0.0]    # 姿勢 5：回到前方、手臂收回、夾爪閉合
        ]
        
        # 4. 控制軌跡插值所需的內部變數
        self.current_wp_idx = 0
        self.next_wp_idx = 1
        self.t = 0.0                # 插值進度參數 (0.0 到 1.0)
        self.speed = 0.02           # 每 50ms 前進的插值步長 (決定手臂移動的快慢)

        self.get_logger().info('軌跡生成節點已啟動，開始自動控制手臂擺動！')

    def timer_callback(self):
        # 建立 JointState 訊息實體
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        
        # ⚠️ 這裡的名稱必須與你 guiji.urdf 裡面的關節名稱完全一致！
        msg.name = [
            'arm_0_joint', 
            'arm_1_joint', 
            'arm_2_joint', 
            'gripper_left_joint', 
            'gripper_right_joint'
        ]

        # 5. 線性插值計算（線性平滑過渡位置）
        current_pose = self.waypionts[self.current_wp_idx]
        next_pose = self.waypionts[self.next_wp_idx]
        
        interpolated_positions = []
        for i in range(len(current_pose)):
            # 公式：p = p_start + t * (p_end - p_start)
            p = current_pose[i] + self.t * (next_pose[i] - current_pose[i])
            interpolated_positions.append(p)
            
        msg.position = interpolated_positions

        # 6. 發布關節狀態訊息
        self.joint_pub.publish(msg)

        # 7. 更新插值時間進度
        self.t += self.speed
        if self.t >= 1.0:
            self.t = 0.0
            self.current_wp_idx = self.next_wp_idx
            # 當到達最後一個點時，自動循環回到第一個點
            self.next_wp_idx = (self.next_wp_idx + 1) % len(self.waypionts)


def main(args=None):
    rclpy.init(args=args)
    node = TrajectoryGenerator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()