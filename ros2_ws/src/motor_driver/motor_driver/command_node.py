import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class CommandNode(Node):
    def __init__(self):
        super().__init__('command_node')

        self.publisher_ = self.create_publisher(
            String,
            'motor_cmd',
            10
        )

        self.valid_commands = [
            'forward',
            'backward',
            'left',
            'right',
            'stop'
        ]

        self.get_logger().info(
            'Command Node Started!'
        )

        self.get_logger().info(
            'Available commands: '
            'forward, backward, left, right, stop, quit'
        )

    def publish_command(self, command):
        msg = String()
        msg.data = command

        self.publisher_.publish(msg)

        self.get_logger().info(
            f'Published: {msg.data}'
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
        rclpy.shutdown()


if __name__ == '__main__':
    main()