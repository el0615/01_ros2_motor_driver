import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class MotorDriverNode(Node):
    def __init__(self):
        super().__init__('motor_driver_node')

        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.velocity_command_callback,
            10
        )

        self.get_logger().info(
            'Motor Driver Node Started!'
        )

    def velocity_command_callback(self, msg):
        linear_x = msg.linear.x
        angular_z = msg.angular.z

        self.get_logger().info(
            f'Received velocity command | '
            f'linear.x={linear_x:.2f}, '
            f'angular.z={angular_z:.2f}'
        )

        if linear_x > 0.0 and angular_z == 0.0:
            self.get_logger().info('Move Forward')

        elif linear_x < 0.0 and angular_z == 0.0:
            self.get_logger().info('Move Backward')

        elif linear_x == 0.0 and angular_z > 0.0:
            self.get_logger().info('Turn Left')

        elif linear_x == 0.0 and angular_z < 0.0:
            self.get_logger().info('Turn Right')

        elif linear_x == 0.0 and angular_z == 0.0:
            self.get_logger().info('Motor Stop')

        else:
            self.get_logger().info(
                'Combined linear and angular motion'
            )


def main(args=None):
    rclpy.init(args=args)

    node = MotorDriverNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        node.get_logger().info(
            'Keyboard interrupt received.'
        )

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()