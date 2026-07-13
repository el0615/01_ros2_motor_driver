import select
import sys
import termios
import tty

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

        self.linear_speed = 0.5
        self.angular_speed = 0.8

        self.get_logger().info('Keyboard Teleop Node Started!')
        self.print_instructions()

    def print_instructions(self):
        print(
            '\n'
            'Keyboard Teleop Controls\n'
            '------------------------\n'
            'w : move forward\n'
            'x : move backward\n'
            'a : turn left\n'
            'd : turn right\n'
            's : stop\n'
            '\n'
            'q : increase linear speed\n'
            'z : decrease linear speed\n'
            'e : increase angular speed\n'
            'c : decrease angular speed\n'
            '\n'
            'Ctrl+C : quit\n'
        )

    def publish_velocity(
        self,
        linear_x=0.0,
        angular_z=0.0
    ):
        msg = Twist()

        msg.linear.x = linear_x
        msg.linear.y = 0.0
        msg.linear.z = 0.0

        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = angular_z

        self.publisher_.publish(msg)

        self.get_logger().info(
            f'Published velocity | '
            f'linear.x={linear_x:.2f} m/s, '
            f'angular.z={angular_z:.2f} rad/s'
        )

    def process_key(self, key):
        # Raw terminal mode에서는 Ctrl+C가 '\x03'으로 입력된다.
        if key == '\x03':
            raise KeyboardInterrupt

        if key == 'w':
            self.publish_velocity(
                linear_x=self.linear_speed
            )

        elif key == 'x':
            self.publish_velocity(
                linear_x=-self.linear_speed
            )

        elif key == 'a':
            self.publish_velocity(
                angular_z=self.angular_speed
            )

        elif key == 'd':
            self.publish_velocity(
                angular_z=-self.angular_speed
            )

        elif key == 's':
            self.publish_velocity()

        elif key == 'q':
            self.linear_speed += 0.1
            self.get_logger().info(
                f'Linear speed increased: '
                f'{self.linear_speed:.2f} m/s'
            )

        elif key == 'z':
            self.linear_speed = max(
                0.0,
                self.linear_speed - 0.1
            )

            self.get_logger().info(
                f'Linear speed decreased: '
                f'{self.linear_speed:.2f} m/s'
            )

        elif key == 'e':
            self.angular_speed += 0.1

            self.get_logger().info(
                f'Angular speed increased: '
                f'{self.angular_speed:.2f} rad/s'
            )

        elif key == 'c':
            self.angular_speed = max(
                0.0,
                self.angular_speed - 0.1
            )

            self.get_logger().info(
                f'Angular speed decreased: '
                f'{self.angular_speed:.2f} rad/s'
            )

        else:
            self.publish_velocity()

            self.get_logger().warn(
                f'Unknown key: {repr(key)} '
                f'— stop command sent'
            )


def get_key(settings):
    tty.setraw(sys.stdin.fileno())

    ready, _, _ = select.select(
        [sys.stdin],
        [],
        [],
        0.1
    )

    if ready:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(
        sys.stdin,
        termios.TCSADRAIN,
        settings
    )

    return key


def main(args=None):
    rclpy.init(args=args)

    node = CommandNode()
    settings = termios.tcgetattr(sys.stdin)

    try:
        while rclpy.ok():
            key = get_key(settings)

            if key:
                node.process_key(key)

    except KeyboardInterrupt:
        node.get_logger().info(
            'Keyboard interrupt received.'
        )

    finally:
        # 종료 전에 정지 명령 전송
        node.publish_velocity()

        termios.tcsetattr(
            sys.stdin,
            termios.TCSADRAIN,
            settings
        )

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()