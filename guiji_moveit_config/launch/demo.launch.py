import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder

def generate_launch_description():
    guiji_share = get_package_share_directory("guiji")
    moveit_share = get_package_share_directory("guiji_moveit_config")

    with open(os.path.join(guiji_share, "urdf", "guiji.urdf"), 'r') as f:
        robot_description_content = f.read()

    # 1. 建立完整的 MoveIt 配置
    moveit_config = (
        MoveItConfigsBuilder("guiji", package_name="guiji_moveit_config")
        .robot_description(file_path=os.path.join(guiji_share, "urdf", "guiji.urdf"))
        .robot_description_semantic(file_path=os.path.join(moveit_share, "config", "guiji.srdf"))
        .trajectory_execution(file_path=os.path.join(moveit_share, "config", "moveit_controllers.yaml"))
        .robot_description_kinematics(file_path=os.path.join(moveit_share, "config", "kinematics.yaml"))
        .joint_limits(file_path=os.path.join(moveit_share, "config", "joint_limits.yaml"))
        .to_moveit_configs()
    )

    full_parameters = moveit_config.to_dict()
    full_parameters['robot_description'] = robot_description_content

    # 2. MoveIt 大腦節點
    run_move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[full_parameters],
    )

    # 3. RViz2 視覺化介面
    rviz_config_file = os.path.join(guiji_share, "config", "config.rviz")
    rviz_args = ["-d", rviz_config_file] if os.path.exists(rviz_config_file) else []
    run_rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=rviz_args,
        parameters=[full_parameters],
    )

    # 4. 機器人狀態發布器 (Robot State Publisher)
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="both",
        parameters=[{'robot_description': robot_description_content}],
    )

    # 5. 靜態座標發布器
    static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_transform_publisher",
        output="log",
        arguments=["0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "world", "base_link"],
    )

    # ✨ 萬用新解：使用最穩定的 joint_state_publisher 代理模擬馬達
    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        name="joint_state_publisher",
        parameters=[{
            'source_list': ['/move_group/fake_controller_joint_states'],
            'rate': 50
        }],
    )

    return LaunchDescription([
        static_tf,
        robot_state_publisher,
        joint_state_publisher,   # 👈 萬用關節代理上線
        run_move_group_node,
        run_rviz_node,
    ])
