import usb.backend.libusb1
import usb.core
import sys
import serial
import argparse
import random


# Parse command-line arguments
parser = argparse.ArgumentParser(description='Steering Data Transmitter')
parser.add_argument('--simulate', action='store_true', help='Use simulated steering data instead of real hardware')
args = parser.parse_args()

# Set up backend for pyusb
backend = usb.backend.libusb1.get_backend(find_library=lambda x: "C:\\libusb-1.0.27\\MinGW64\\dll\\libusb-1.0.dll")

# Find USB device with a specific vendor and product ID, if not in simulation mode
if not args.simulate:
    dev = usb.core.find(idVendor=0x046d, idProduct=0xc262, backend=backend)
    if dev is None:
        sys.exit("No USB device found. Exiting...")

    # Get active USB configuration
    cfg = dev.get_active_configuration()

    # Get the first interface
    intf = cfg[(0, 0)]

    # Get the second endpoint from the interface
    ep2 = intf[1]

    # Check if the kernel driver is active and detach it if necessary (skip on Windows)
    intfNum = intf.bInterfaceNumber
    if sys.platform != 'win32':  # Skip this block on Windows
        print("USB is busy?", dev.is_kernel_driver_active(intfNum))
        if dev.is_kernel_driver_active(intfNum):
            dev.detach_kernel_driver(intfNum)

# Set up serial communication
try:
    ser = serial.Serial(
        port='COM9',
        baudrate=115200,
        parity=serial.PARITY_ODD,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )
    if ser.isOpen():
        ser.close()
    ser.open()
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    sys.exit(1)

# Function to simulate steering data
def simulate_steering_data():
    # Simulate data: customize these values as needed
    acc = random.uniform(0.0, 2.5)  # Random acceleration from 0.0 to 2.5
    brake = random.uniform(0.0, 2.0)  # Random braking from 0.0 to 2.0
    steer = random.uniform(-1.0, 1.0)  # Random steering from -1.0 (left) to 1.0 (right)
    return acc, brake, steer

# Continuously read data and send over serial port
while True:
    try:
        if args.simulate:
            acc, brake, steer = simulate_steering_data()
        else:
            data = ep2.read(64)  # Read data from endpoint
            acc = 1 - data[6] / 255
            brake = 1 - data[7] / 255
            steer = (data[4] + (data[5] * 255)) / (256 * 255)

        print("Acc: {:.2f} | Brake: {:.2f} | Steer: {:.2f}".format(acc, brake, steer))

        # Format and send data over serial
        message = "{},{},{}\n".format(int(acc * 255), int(brake * 255), int(steer * 255 * 256))
        # ser.write(message.encode('utf-8'))
        # message = "{},{},{}|".format(int(acc * 255), int(brake * 255), int(steer * 255 * 256))
        # message = f"{int(acc * 255)},{int(brake * 255)},{int(steer * 255 * 256)}\n"
        ser.write(message.encode())



    except usb.core.USBError as e:
        if e.args == ('Operation timed out',):
            continue
        else:
            print(f"USB Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        break  # or continue based on your application's needs

