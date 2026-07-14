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

        # QoS 설정
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
        self.declare_parameter('publish_rate', 10.0)

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

        self.publish_rate = (
            self.get_parameter('publish_rate')
            .get_parameter_value()
            .double_value
        )

        self.validate_parameters()

        # 현재 목표 속도
        self.target_linear_x = 0.0
        self.target_angular_z = 0.0

        # Timer 주기 계산
        timer_period = 1.0 / self.publish_rate

        # DN-016: 일정 주기로 Twist 발행
        self.timer = self.create_timer(
            timer_period,
            self.timer_callback
        )

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
            f'angular_speed={self.angular_speed:.2f} rad/s, '
            f'publish_rate={self.publish_rate:.2f} Hz'
        )

        self.print_instructions()

    def validate_parameters(self):
        if self.linear_speed < 0.0:
            self.logger.error(
                'linear_speed must be non-negative.'
            )
            raise ValueError(
                'linear_speed must be non-negative'
            )

        if self.angular_speed < 0.0:
            self.logger.error(
                'angular_speed must be non-negative.'
            )
            raise ValueError(
                'angular_speed must be non-negative'
            )

        if self.publish_rate <= 0.0:
            self.logger.error(
                'publish_rate must be greater than 0.'
            )
            raise ValueError(
                'publish_rate must be greater than 0'
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

    def timer_callback(self):
        """
        설정된 주기마다 현재 목표 속도를 Twist로 발행한다.
        """
        self.publish_velocity(
            linear_x=self.target_linear_x,
            angular_z=self.target_angular_z
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

        self.logger.debug(
            f'Timer published velocity | '
            f'linear.x={linear_x:.2f} m/s, '
            f'angular.z={angular_z:.2f} rad/s'
        )

    def process_key(self, key):
        self.logger.debug(
            f'Raw keyboard input: {repr(key)}'
        )

        if key == '\x03':
            raise KeyboardInterrupt

        if key == 'w':
            self.target_linear_x = self.linear_speed
            self.target_angular_z = 0.0

            self.logger.info(
                f'Forward target selected | '
                f'linear.x={self.target_linear_x:.2f} m/s'
            )

        elif key == 'x':
            self.target_linear_x = -self.linear_speed
            self.target_angular_z = 0.0

            self.logger.info(
                f'Backward target selected | '
                f'linear.x={self.target_linear_x:.2f} m/s'
            )

        elif key == 'a':
            self.target_linear_x = 0.0
            self.target_angular_z = self.angular_speed

            self.logger.info(
                f'Left turn target selected | '
                f'angular.z={self.target_angular_z:.2f} rad/s'
            )

        elif key == 'd':
            self.target_linear_x = 0.0
            self.target_angular_z = -self.angular_speed

            self.logger.info(
                f'Right turn target selected | '
                f'angular.z={self.target_angular_z:.2f} rad/s'
            )

        elif key == 's':
            self.set_stop_target()

            self.logger.info(
                'Stop target selected.'
            )

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

        else:
            self.logger.warn(
                f'Unknown key: {repr(key)} | '
                f'Stop target will be selected.'
            )

            self.set_stop_target()

    def set_stop_target(self):
        self.target_linear_x = 0.0
        self.target_angular_z = 0.0


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

            # Timer Callback 실행을 위해 ROS2 이벤트 처리
            rclpy.spin_once(
                node,
                timeout_sec=0.0
            )

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
            node.set_stop_target()

            # 종료 직전 정지 메시지를 즉시 한 번 발행
            node.publish_velocity()

            node.logger.info(
                'Final stop command published.'
            )

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