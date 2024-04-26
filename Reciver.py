import serial
import time

# Constants for data scaling
SCALE_ACC = 255.0
SCALE_BRAKE = 255.0
SCALE_STEER = 65536.0  # 255.0 * 256

def read_from_serial(port):
    try:
        # Configure and open the serial port
        ser = serial.Serial(port, baudrate=115200, timeout=1,
                            parity=serial.PARITY_ODD, stopbits=serial.STOPBITS_ONE,
                            bytesize=serial.EIGHTBITS)

        if not ser.isOpen():
            ser.open()

        print(f"Connected to {port}. Reading data...")

        # Continuously read and print data from the serial port
        while True:
            try:
                data = ser.readline().decode('utf-8').strip()
                if data:  # If data is not empty
                    # Split the data into its components
                    components = data.split(',')
                    if len(components) == 3:
                        try:
                            acc = int(components[0]) / SCALE_ACC
                            brake = int(components[1]) / SCALE_BRAKE
                            steer = int(components[2]) / SCALE_STEER
                            print(f"Acc: {acc:.2f} | Brake: {brake:.2f} | Steer: {steer:.2f}")
                        except ValueError:
                            print("Error: Data format invalid.", data)
                    else:
                        print("Received:", data)
            except serial.SerialException as e:
                print(f"Error reading data: {e}")
                break
            except UnicodeDecodeError:
                print("Error decoding data. Possible bad data received.")

            time.sleep(0.1)  # Small delay to prevent overwhelming the CPU

    except serial.SerialException as e:
        print(f"Could not open serial port {port}: {e}")
    finally:
        if ser and ser.isOpen():
            ser.close()
            print("Serial port closed.")

if __name__ == "__main__":
    COM_PORT = 'COM3'  # Set this to the correct COM port
    read_from_serial(COM_PORT)
