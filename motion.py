from machine import UART, Pin
import time

# Initialize UART1 with the appropriate pins and baud rate
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

def parse_sensor_data(data):
    """
    Parses the sensor data to extract motion status and distance.
    """
    try:
        # Decode bytes to string and split into individual messages
        decoded_data = data.decode('utf-8').split("\r\n")
        
        for line in decoded_data:
            if line.startswith("$DFDMD"):
                # Split the line into components
                parts = line.split(",")
                if len(parts) >= 6:
                    motion_status = parts[1].strip()  # Motion status: 0 or 1
                    distance = parts[3].strip()      # Distance value
                    
                    # Validate distance
                    try:
                        distance = float(distance) if distance else None
                    except ValueError:
                        distance = None
                    
                    # Display the parsed motion status and distance
                    motion_state = "MOTION DETECTED!!" if motion_status == "1" else "No Motion Detected"
                    if distance is not None:
                        print(f"Motion: {motion_state}, Distance: {distance:.3f} meters")
                    else:
                        print(f"Motion: {motion_state}, Distance: Unknown meters")
                    return motion_state, distance
                else:
                    print(f"[DEBUG] Malformed line: {line}")
    except Exception as e:
        print(f"[ERROR] Failed to parse sensor data: {e}")
    return None, None

def main():
    while True:
        if uart.any():
            raw_data = uart.read(128)  # Adjust to the maximum packet size
            if raw_data:
                parse_sensor_data(raw_data)
        time.sleep(0.5)

if __name__ == "__main__":
    main()
