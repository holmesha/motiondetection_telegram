from machine import UART, Pin
import time
import network
import socket
import json
from secrets import SSID, PASSWORD  # Import Wi-Fi credentials from a separate file

# Initialize UART1 with the appropriate pins and baud rate
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

# Global variables for motion status and distance
motion_status = "Initializing..."
distance = "Unknown"

def parse_sensor_data(data):
    """
    Parses the sensor data to extract motion status and distance.
    """
    global motion_status, distance
    try:
        decoded_data = data.decode('utf-8').split("\r\n")
        for line in decoded_data:
            if line.startswith("$DFDMD"):
                parts = line.split(",")
                if len(parts) >= 6:
                    motion_state = parts[1].strip()  # Motion status: 0 or 1
                    dist_value = parts[3].strip()   # Distance value
                    
                    try:
                        distance = float(dist_value) if dist_value else "Unknown"
                    except ValueError:
                        distance = "Unknown"
                    
                    motion_status = "MOTION DETECTED!!" if motion_state == "1" else "No Motion Detected"
                    return
    except Exception as e:
        # Uncomment for debugging
        # print(f"[ERROR] Failed to parse sensor data: {e}")
        pass

def web_page():
    """
    Creates the HTML content for the web page.
    """
    return """<!DOCTYPE html>
<html>
<head>
    <title>Motion Detector</title>
    <style>
        h1 {
            font-size: 2em;
            font-weight: bold;
            text-align: center;
        }
        h2 {
            text-align: center;
        }
        #motion_status {
            color: red;
        }
    </style>
    <script>
        async function updateData() {
            try {
                const response = await fetch('/data');
                const data = await response.json();
                document.getElementById('motion_status').innerText = data.motion_status;
                document.getElementById('distance').innerText = data.distance + " meters";
                document.getElementById('motion_status').style.color = (data.motion_status === "MOTION DETECTED!!") ? "green" : "red";
            } catch (error) {
                console.error('Error fetching motion data:', error);
            }
        }
        setInterval(updateData, 1000); // Fetch data every 1 second
    </script>
</head>
<body>
    <h1>MOTION DETECTOR</h1>
    <h2 id="motion_status">Initializing...</h2>
    <h2>Distance: <span id="distance">Unknown meters</span></h2>
</body>
</html>"""

def start_server():
    """
    Starts the web server to display sensor data.
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    while not wlan.isconnected():
        time.sleep(1)

    print("[INFO] Connected to Wi-Fi:", wlan.ifconfig())
    ip = wlan.ifconfig()[0]

    addr = (ip, 80)
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print(f"[INFO] Server running at http://{ip}:80")

    while True:
        cl, addr = s.accept()
        try:
            request = cl.recv(1024).decode('utf-8')
            # Uncomment for debugging
            # print("[INFO] Request received:", request)

            if "GET /data" in request:
                try:
                    response = {
                        "motion_status": motion_status,
                        "distance": distance,
                    }
                    cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
                    cl.send(json.dumps(response))
                except Exception as e:
                    # Uncomment for debugging
                    # print("[ERROR] Failed to send JSON response:", e)
                    pass
            else:
                cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
                cl.send(web_page())
        except Exception as e:
            # Uncomment for debugging
            # print("[ERROR] Exception in handling request:", e)
            pass
        finally:
            cl.close()

def main():
    """
    Main function to handle sensor data and run the web server.
    """
    import _thread
    _thread.start_new_thread(start_server, ())

    while True:
        if uart.any():
            raw_data = uart.read(128)
            if raw_data:
                parse_sensor_data(raw_data)
        time.sleep(0.5)

if __name__ == "__main__":
    main()
