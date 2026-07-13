from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    motor_driver_node = Node(
        package='motor_driver',
        executable='motor_driver_node',
        name='motor_driver_node',
        output='screen',
    )

    return LaunchDescription([
        motor_driver_node,
    ])