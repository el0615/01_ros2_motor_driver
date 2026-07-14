import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.qos import QoSProfile


class MotorDriverNode(Node):
    def __init__(self):
        super().__init__('motor_driver_node')

        self.logger = self.get_logger()

        # DN-015: Publisher와 동일한 QoS Profile 사용
        self.qos_profile = QoSProfile(
            depth=10
        )

        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.velocity_command_callback,
            self.qos_profile
        )

        self.logger.info(
            'Motor Driver Node Started!'
        )

        self.logger.info(
            'QoS Profile configured | '
            'history=KEEP_LAST, depth=10'
        )

        self.logger.info(
            'Waiting for velocity commands '
            'on /cmd_vel.'
        )

    def velocity_command_callback(self, msg):
        linear_x = msg.linear.x
        angular_z = msg.angular.z

        self.logger.debug(
            f'Raw Twist received | '
            f'linear.x={linear_x}, '
            f'angular.z={angular_z}'
        )

        if not math.isfinite(linear_x):
            self.logger.error(
                f'Invalid linear velocity received: '
                f'{linear_x}'
            )

            self.stop()
            return

        if not math.isfinite(angular_z):
            self.logger.error(
                f'Invalid angular velocity received: '
                f'{angular_z}'
            )

            self.stop()
            return

        self.logger.info(
            f'Received velocity command | '
            f'linear.x={linear_x:.2f} m/s, '
            f'angular.z={angular_z:.2f} rad/s'
        )

        if linear_x > 0.0 and angular_z == 0.0:
            self.move_forward(linear_x)

        elif linear_x < 0.0 and angular_z == 0.0:
            self.move_backward(
                abs(linear_x)
            )

        elif linear_x == 0.0 and angular_z > 0.0:
            self.turn_left(angular_z)

        elif linear_x == 0.0 and angular_z < 0.0:
            self.turn_right(
                abs(angular_z)
            )

        elif linear_x == 0.0 and angular_z == 0.0:
            self.stop()

        else:
            self.move_combined(
                linear_speed=linear_x,
                angular_speed=angular_z
            )

    def move_forward(self, speed):
        self.logger.info(
            f'Move Forward | '
            f'speed={speed:.2f} m/s'
        )

    def move_backward(self, speed):
        self.logger.info(
            f'Move Backward | '
            f'speed={speed:.2f} m/s'
        )

    def turn_left(self, angular_speed):
        self.logger.info(
            f'Turn Left | '
            f'angular speed={angular_speed:.2f} rad/s'
        )

    def turn_right(self, angular_speed):
        self.logger.info(
            f'Turn Right | '
            f'angular speed={angular_speed:.2f} rad/s'
        )

    def stop(self):
        self.logger.info(
            'Motor Stop | '
            'linear speed=0.00 m/s, '
            'angular speed=0.00 rad/s'
        )

    def move_combined(
        self,
        linear_speed,
        angular_speed
    ):
        direction = (
            'left'
            if angular_speed > 0.0
            else 'right'
        )

        self.logger.info(
            f'Combined Motion | '
            f'linear speed={linear_speed:.2f} m/s, '
            f'turning={direction}, '
            f'angular speed='
            f'{abs(angular_speed):.2f} rad/s'
        )


def main(args=None):
    rclpy.init(args=args)

    node = MotorDriverNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        node.logger.info(
            'Keyboard interrupt received. '
            'Motor Driver Node is shutting down.'
        )

    except Exception as error:
        node.logger.error(
            f'Unexpected Motor Driver error: '
            f'{error}'
        )
        raise

    finally:
        node.logger.info(
            'Destroying Motor Driver Node.'
        )

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()