import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # 1. 取得各功能包的安裝路徑
    guiji_share = get_package_share_directory("guiji")
    gazebo_share = get_package_share_directory("guiji_gazebo")

    # 2. 讀取你的 URDF 機器人肉體內容
    urdf_path = os.path.join(guiji_share, "urdf", "guiji.urdf")
    with open(urdf_path, 'r') as f:
        robot_description_content = f.read()

    # 3. 引入官方 Gazebo Sim 的核心啟動檔 (Jazzy 專用 ros_gz_sim)
    gz_sim_share = get_package_share_directory("ros_gz_sim")
    world_file_path = os.path.join(gazebo_share, "worlds", "guiji_world.sdf")
    
    # 啟動 Gazebo 模擬器並載入我們手搓的物理世界
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gz_sim_share, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={"gz_args": f"-r {world_file_path}"}.items(),
    )

    # 4. 機器人狀態發布器 (Robot State Publisher)
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="both",
        parameters=[{'robot_description': robot_description_content}],
    )

    # 5. 在 Gazebo 世界中「孵化 (Spawn)」手臂肉體
    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic", "robot_description",
            "-name", "guiji_arm",
            "-z", "0.0"
        ],
        output="screen",
    )

    # 6. 啟動通訊對接 (Gz Bridge)
    bridge_config = os.path.join(gazebo_share, "config", "gz_bridge.yaml")
    ros_gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[f"--config-file", bridge_config],
        output="screen",
    )

    return LaunchDescription([
        gazebo_launch,        # 1. 打開 Gazebo 房間
        robot_state_publisher,# 2. 廣播手臂結構
        spawn_robot,          # 3. 孵化手臂
        ros_gz_bridge,        # 4. 搭起通訊橋樑
    ])
