import select
import sys
import termios
import tty

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.qos import QoSProfile


class CommandNode(Node):
    def __init__(self):
        super().__init__('command_node')

        self.logger = self.get_logger()

        # DN-015: 명시적인 QoS Profile 생성
        self.qos_profile = QoSProfile(
            depth=10
        )

        self.publisher_ = self.create_publisher(
            Twist,
            '/cmd_vel',
            self.qos_profile
        )

        # ROS2 Parameter 선언
        self.declare_parameter('linear_speed', 0.5)
        self.declare_parameter('angular_speed', 0.8)

        # Parameter 값 가져오기
        self.linear_speed = (
            self.get_parameter('linear_speed')
            .get_parameter_value()
            .double_value
        )

        self.angular_speed = (
            self.get_parameter('angular_speed')
            .get_parameter_value()
            .double_value
        )

        self.validate_speed_parameters()

        self.logger.info(
            'Keyboard Teleop Node Started!'
        )

        self.logger.info(
            'QoS Profile configured | '
            'history=KEEP_LAST, depth=10'
        )

        self.logger.info(
            f'Initial parameters | '
            f'linear_speed={self.linear_speed:.2f} m/s, '
            f'angular_speed={self.angular_speed:.2f} rad/s'
        )

        self.print_instructions()

    def validate_speed_parameters(self):
        if self.linear_speed < 0.0:
            self.logger.error(
                f'Invalid linear_speed: '
                f'{self.linear_speed:.2f}'
            )
            raise ValueError(
                'linear_speed must be non-negative'
            )

        if self.angular_speed < 0.0:
            self.logger.error(
                f'Invalid angular_speed: '
                f'{self.angular_speed:.2f}'
            )
            raise ValueError(
                'angular_speed must be non-negative'
            )

        if self.linear_speed == 0.0:
            self.logger.warn(
                'linear_speed is 0.0. '
                'Forward and backward commands '
                'will not move the robot.'
            )

        if self.angular_speed == 0.0:
            self.logger.warn(
                'angular_speed is 0.0. '
                'Turning commands will not rotate the robot.'
            )

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

        self.logger.debug(
            f'Preparing Twist message | '
            f'linear.x={msg.linear.x:.2f}, '
            f'angular.z={msg.angular.z:.2f}'
        )

        self.publisher_.publish(msg)

        self.logger.info(
            f'Published velocity | '
            f'linear.x={linear_x:.2f} m/s, '
            f'angular.z={angular_z:.2f} rad/s'
        )

    def process_key(self, key):
        self.logger.debug(
            f'Raw keyboard input: {repr(key)}'
        )

        # Raw Mode에서는 Ctrl+C가 '\x03'으로 들어온다.
        if key == '\x03':
            raise KeyboardInterrupt

        if key == 'w':
            self.logger.info(
                'Forward command selected.'
            )

            self.publish_velocity(
                linear_x=self.linear_speed
            )

        elif key == 'x':
            self.logger.info(
                'Backward command selected.'
            )

            self.publish_velocity(
                linear_x=-self.linear_speed
            )

        elif key == 'a':
            self.logger.info(
                'Left turn command selected.'
            )

            self.publish_velocity(
                angular_z=self.angular_speed
            )

        elif key == 'd':
            self.logger.info(
                'Right turn command selected.'
            )

            self.publish_velocity(
                angular_z=-self.angular_speed
            )

        elif key == 's':
            self.logger.info(
                'Stop command selected.'
            )

            self.publish_velocity()

        elif key == 'q':
            self.linear_speed += 0.1

            self.logger.info(
                f'Linear speed increased | '
                f'new={self.linear_speed:.2f} m/s'
            )

        elif key == 'z':
            previous_speed = self.linear_speed

            self.linear_speed = max(
                0.0,
                self.linear_speed - 0.1
            )

            self.logger.info(
                f'Linear speed decreased | '
                f'previous={previous_speed:.2f} m/s, '
                f'new={self.linear_speed:.2f} m/s'
            )

            if self.linear_speed == 0.0:
                self.logger.warn(
                    'Linear speed reached 0.0 m/s.'
                )

        elif key == 'e':
            self.angular_speed += 0.1

            self.logger.info(
                f'Angular speed increased | '
                f'new={self.angular_speed:.2f} rad/s'
            )

        elif key == 'c':
            previous_speed = self.angular_speed

            self.angular_speed = max(
                0.0,
                self.angular_speed - 0.1
            )

            self.logger.info(
                f'Angular speed decreased | '
                f'previous={previous_speed:.2f} rad/s, '
                f'new={self.angular_speed:.2f} rad/s'
            )

            if self.angular_speed == 0.0:
                self.logger.warn(
                    'Angular speed reached 0.0 rad/s.'
                )

        else:
            self.logger.warn(
                f'Unknown key: {repr(key)} | '
                f'Stop command will be sent.'
            )

            self.publish_velocity()


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

    node = None
    settings = termios.tcgetattr(sys.stdin)

    try:
        node = CommandNode()

        while rclpy.ok():
            key = get_key(settings)

            if key:
                node.process_key(key)

    except KeyboardInterrupt:
        if node is not None:
            node.logger.info(
                'Keyboard interrupt received. '
                'Command Node is shutting down.'
            )

    except ValueError as error:
        if node is not None:
            node.logger.error(
                f'Command Node initialization failed: '
                f'{error}'
            )

    finally:
        if node is not None:
            node.logger.info(
                'Publishing final stop command.'
            )

            node.publish_velocity()

        termios.tcsetattr(
            sys.stdin,
            termios.TCSADRAIN,
            settings
        )

        if node is not None:
            node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()