import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
import serial
import time

class SerialToROS2Joy(Node):
    def __init__(self):
        super().__init__('serial_to_ros2_joy')
        self.publisher_ = self.create_publisher(Joy, 'joy', 10)
        self.serial_port = serial.Serial(
            port='COM9',  # Update as needed
            baudrate=115200,
            parity=serial.PARITY_ODD,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
        if not self.serial_port.isOpen():
            self.serial_port.open()
        self.timer = self.create_timer(0.1, self.timer_callback)  # Adjust the timing based on your needs

    def timer_callback(self):
        if self.serial_port.in_waiting > 0:
            data = self.serial_port.readline().decode('utf-8').strip()
            self.process_and_publish(data)

    def process_and_publish(self, data):
        try:
            parts = data.split(',')
            if len(parts) == 3:
                joy_message = Joy()
                joy_message.header.stamp = self.get_clock().now().to_msg()
                joy_message.axes = [float(parts[0])/255.0, float(parts[1])/255.0, float(parts[2])/(255.0*256)]
                joy_message.buttons = [0]  # Update or modify based on your data structure
                self.publisher_.publish(joy_message)
                self.get_logger().info('Publishing: "%s"' % joy_message)
        except Exception as e:
            self.get_logger().error('Failed to process data: %s' % str(e))

def main(args=None):
    rclpy.init(args=args)
    node = SerialToROS2Joy()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
