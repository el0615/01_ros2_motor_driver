import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class CommandNode(Node):
    def __init__(self):
        super().__init__('command_node')

        self.publisher_ = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.valid_commands = [
            'forward',
            'backward',
            'left',
            'right',
            'stop'
        ]

        self.get_logger().info('Command Node Started!')
        self.get_logger().info(
            'Available commands: '
            'forward, backward, left, right, stop, quit'
        )

    def publish_command(self, command):
        msg = Twist()

        # 모든 속도값을 먼저 0으로 초기화
        msg.linear.x = 0.0
        msg.linear.y = 0.0
        msg.linear.z = 0.0

        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = 0.0

        if command == 'forward':
            msg.linear.x = 0.5

        elif command == 'backward':
            msg.linear.x = -0.5

        elif command == 'left':
            msg.angular.z = 0.8

        elif command == 'right':
            msg.angular.z = -0.8

        elif command == 'stop':
            # 모든 값이 이미 0이므로 별도 변경 없음
            pass

        self.publisher_.publish(msg)

        self.get_logger().info(
            f'Published command: {command} | '
            f'linear.x={msg.linear.x:.2f}, '
            f'angular.z={msg.angular.z:.2f}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = CommandNode()

    try:
        while rclpy.ok():
            command = input(
                'Enter command '
                '(forward/backward/left/right/stop/quit): '
            ).strip().lower()

            if command == 'quit':
                node.get_logger().info(
                    'Command Node shutting down.'
                )
                break

            if command in node.valid_commands:
                node.publish_command(command)

            else:
                node.get_logger().warn(
                    f'Unknown command: {command}'
                )

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