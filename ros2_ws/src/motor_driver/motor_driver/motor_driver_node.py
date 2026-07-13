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
            self.move_forward(linear_x)

        elif linear_x < 0.0 and angular_z == 0.0:
            self.move_backward(abs(linear_x))

        elif linear_x == 0.0 and angular_z > 0.0:
            self.turn_left(angular_z)

        elif linear_x == 0.0 and angular_z < 0.0:
            self.turn_right(abs(angular_z))

        elif linear_x == 0.0 and angular_z == 0.0:
            self.stop()

        else:
            self.move_combined(
                linear_speed=linear_x,
                angular_speed=angular_z
            )

    def move_forward(self, speed):
        self.get_logger().info(
            f'Move Forward | speed={speed:.2f} m/s'
        )

    def move_backward(self, speed):
        self.get_logger().info(
            f'Move Backward | speed={speed:.2f} m/s'
        )

    def turn_left(self, angular_speed):
        self.get_logger().info(
            f'Turn Left | angular speed={angular_speed:.2f} rad/s'
        )

    def turn_right(self, angular_speed):
        self.get_logger().info(
            f'Turn Right | angular speed={angular_speed:.2f} rad/s'
        )

    def stop(self):
        self.get_logger().info(
            'Motor Stop'
        )

    def move_combined(self, linear_speed, angular_speed):
        direction = 'left' if angular_speed > 0.0 else 'right'

        self.get_logger().info(
            f'Combined Motion | '
            f'linear speed={linear_speed:.2f} m/s, '
            f'turning {direction}, '
            f'angular speed={abs(angular_speed):.2f} rad/s'
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