from machine import UART, Pin
import time
import network
import socket
from secrets import SSID, PASSWORD  # Import Wi-Fi credentials from a separate file
import requests

# Telegram bot details
BOT_TOKEN = "INSERT BOT TOKEN"
CHAT_ID = "INSERT CHAT ID"
last_notification_time = 0  # Timestamp of the last notification
NOTIFICATION_INTERVAL = 30  # XX Second interval for notifications

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
        pass

def send_telegram_message(message):
    """
    Sends a message via Telegram bot.
    """
    global last_notification_time
    current_time = time.time()
    if motion_status == "MOTION DETECTED!!" and (current_time - last_notification_time) > NOTIFICATION_INTERVAL:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": message}
            requests.post(url, json=payload)
            last_notification_time = current_time
        except Exception as e:
            pass  # Silently handle any exceptions

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
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of the socket
    s.bind(addr)
    s.listen(1)
    print(f"[INFO] Server running at http://{ip}:80")

    while True:
        try:
            cl, addr = s.accept()
            print(f"[INFO] Connection from {addr}")
            request = cl.recv(1024).decode('utf-8')

            if "GET /data" in request:
                # Serve JSON data
                response = f'{{"motion_status": "{motion_status}", "distance": "{distance}"}}'
                cl.sendall("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n".encode('utf-8'))
                cl.sendall(response.encode('utf-8'))
            else:
                # Serve HTML page
                html = web_page()
                cl.sendall("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n".encode('utf-8'))
                
                # Send the HTML content in smaller chunks
                for i in range(0, len(html), 512):
                    cl.sendall(html[i:i+512].encode('utf-8'))
        except Exception as e:
            print(f"[ERROR] Web server error: {e}")
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
                send_telegram_message("Motion Detected!")
        time.sleep(0.5)

if __name__ == "__main__":
    main()


