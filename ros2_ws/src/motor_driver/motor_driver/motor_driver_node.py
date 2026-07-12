import rclpy
from rclpy.node import Node
from std_msgs.msg import String
class MotorDriverNode(Node):
    def __init__(self):
        super().__init__('motor_driver_node')
        self.subscription = self.create_subscription(
            String,
            'motor_cmd',
            self.motor_command_callback,
            10
        )
        self.get_logger().info(
            'Motor Driver Node Started!'
        )
    def motor_command_callback(self, msg):
        self.get_logger().info(
            f'Received motor command: {msg.data}'
        )
def main(args=None):
    rclpy.init(args=args)
    node = MotorDriverNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
if __name__ == '__main__':
    main()