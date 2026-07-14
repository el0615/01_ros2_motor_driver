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

        # Node가 제공하는 Logger 객체를 저장
        self.logger = self.get_logger()

        self.publisher_ = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # ROS2 Parameter 선언
        self.declare_parameter('linear_speed', 0.5)
        self.declare_parameter('angular_speed', 0.8)

        # Parameter 값 읽기
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

        # 잘못된 초기 파라미터 검사
        self.validate_speed_parameters()

        self.logger.info('Keyboard Teleop Node Started!')

        self.logger.info(
            f'Initial parameters | '
            f'linear_speed={self.linear_speed:.2f} m/s, '
            f'angular_speed={self.angular_speed:.2f} rad/s'
        )

        self.print_instructions()

    def validate_speed_parameters(self):
        """초기 속도 파라미터가 올바른지 검사한다."""

        if self.linear_speed < 0.0:
            self.logger.error(
                f'Invalid linear_speed parameter: '
                f'{self.linear_speed:.2f}. '
                f'Value must be non-negative.'
            )
            raise ValueError(
                'linear_speed must be non-negative'
            )

        if self.angular_speed < 0.0:
            self.logger.error(
                f'Invalid angular_speed parameter: '
                f'{self.angular_speed:.2f}. '
                f'Value must be non-negative.'
            )
            raise ValueError(
                'angular_speed must be non-negative'
            )

        if self.linear_speed == 0.0:
            self.logger.warn(
                'linear_speed is 0.0. '
                'Forward and backward commands will not move the robot.'
            )

        if self.angular_speed == 0.0:
            self.logger.warn(
                'angular_speed is 0.0. '
                'Left and right commands will not rotate the robot.'
            )

    def print_instructions(self):
        # 조작 안내문은 로그가 아니라 사용자 인터페이스이므로 print 유지
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

        # 상세 진단용 로그
        self.logger.debug(
            f'Preparing Twist message | '
            f'linear.x={msg.linear.x:.2f}, '
            f'angular.z={msg.angular.z:.2f}'
        )

        self.publisher_.publish(msg)

        # 정상 동작 로그
        self.logger.info(
            f'Published velocity | '
            f'linear.x={linear_x:.2f} m/s, '
            f'angular.z={angular_z:.2f} rad/s'
        )

    def process_key(self, key):
        # 입력된 원시 키를 DEBUG로 기록
        self.logger.debug(
            f'Raw keyboard input received: {repr(key)}'
        )

        if key == '\x03':
            raise KeyboardInterrupt

        if key == 'w':
            self.logger.info('Forward command selected.')

            self.publish_velocity(
                linear_x=self.linear_speed
            )

        elif key == 'x':
            self.logger.info('Backward command selected.')

            self.publish_velocity(
                linear_x=-self.linear_speed
            )

        elif key == 'a':
            self.logger.info('Left turn command selected.')

            self.publish_velocity(
                angular_z=self.angular_speed
            )

        elif key == 'd':
            self.logger.info('Right turn command selected.')

            self.publish_velocity(
                angular_z=-self.angular_speed
            )

        elif key == 's':
            self.logger.info('Stop command selected.')

            self.publish_velocity()

        elif key == 'q':
            self.linear_speed += 0.1

            self.logger.info(
                f'Linear speed increased | '
                f'new value={self.linear_speed:.2f} m/s'
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
                f'new value={self.angular_speed:.2f} rad/s'
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
            # 지원하지 않는 키에서는 안전을 위해 정지 명령 전송
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
                f'Command Node initialization failed: {error}'
            )

    finally:
        if node is not None:
            # 종료 전 로봇 정지 명령 발행
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