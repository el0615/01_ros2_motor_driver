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
        self.timer = self.create_timer(
            1.0,
            self.publish_command
        )
        self.get_logger().info(
            'Command Node Started!'
        )
    def publish_command(self):
        msg = String()
        msg.data = 'forward'
        self.publisher_.publish(msg)
        self.get_logger().info(
            f'Published: {msg.data}'
        )
def main(args=None):
    rclpy.init(args=args)
    node = CommandNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
if __name__ == '__main__':
    main()
