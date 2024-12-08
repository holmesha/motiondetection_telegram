# Motion Detector with Telegram Notifications

This project is a **motion detection system** that uses a Raspberry Pi Pico 2w microcontroller to monitor motion via a DFRobot C4001 MMWave sensor, display the current status on a web server, and send notifications via **Telegram** whenever motion is detected. This is ideal for home automation or security setups. 

This DFRobot is capable of sensing motion up to 25 meters, which is probably overkill for most homes, but I found it to have less false alerts than something like a Hi-Link LD2410C, which I also tried. You could also add more functionality like distance, motion AND still presence, etc. 

**I've also added a few test codes in case you want to JUST see the motion detection functionality or the webserver without Telegram**

---

## Features
- **Real-time motion detection**: Displays motion status and distance via a web server.
- **Telegram notifications**: Sends notifications for detected motion at specified intervals.
- **Web interface**: Displays live updates of motion status and distance in meters.

---

## Hardware Requirements
1. **Microcontroller**: Raspberry Pi Pico W (or a similar board with Wi-Fi and UART support).
2. **Motion sensor**: Compatible with UART (e.g., DFRobot mmWave Presence Sensor).
3. **Wi-Fi network**: For connecting the microcontroller to the web server and Telegram.
4. **Computer with Thonny IDE**: For uploading and running the script.
5. **Micro-USB cable**: To connect the microcontroller to your computer.

---

## Software Requirements
1. **MicroPython firmware**: Ensure your microcontroller is flashed with MicroPython.
2. **Thonny IDE**: For editing and uploading the Python script.
3. **Telegram Bot API**: Set up a Telegram bot to send notifications.

---

## Setting Up the Telegram Bot
![Bot Father](bot_father.jpg)
1. **Create a Telegram Bot**:
   - Open Telegram and search for **BotFather**.
   - Use the `/newbot` command and follow the prompts to create a new bot.
   - You will receive a **bot token** in the format: `123456789:ABCDefGhiJklmNoPQRsTUVwxyz`.

2. **Get the Chat ID**:
   - Start a chat with your bot in Telegram by clicking on the bot link provided by BotFather.
   - Send any message to your bot (e.g., "Hi").
   - Visit the following URL in your browser, replacing `<BOT_TOKEN>` with your bot token:
     ```
     https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
     ```
   - Look for the `"chat"` section in the response. Your **Chat ID** will be displayed.

3. **Update the Code**:
   - Replace `BOT_TOKEN` and `CHAT_ID` in the code with your actual bot token and chat ID.

---

## How to Use
### 1. Hardware Setup
- Connect your motion sensor to the Raspberry Pi Pico W:
  - **TX** of the sensor to **RX** (Pin 1) of the Pico.
  - **RX** of the sensor to **TX** (Pin 0) of the Pico.
  - Power and ground connections as per the sensor's requirements.

### 2. Flash the Code
- Upload the provided Python code to your Raspberry Pi Pico W using **Thonny IDE**.
- Save the script as `main.py` so it runs automatically on boot.

### 3. Wi-Fi Configuration
- Create a `secrets.py` file in the Pico W's filesystem:
  ```python
  SSID = "Your_WiFi_SSID"
  PASSWORD = "Your_WiFi_Password"

### 4. Running the Web Server
1. Connect to the same Wi-Fi network as the Pico W.
2. After the script starts, note the server IP address printed in the logs (e.g., `http://192.168.1.xxx:80`).
3. Open this address in your browser to view the live motion status.

### 5. Telegram Notifications
- Once motion is detected, a notification will be sent to your Telegram account with the message "Motion Detected!" at intervals of 30 seconds (configurable).

---

## Code Overview
- **`parse_sensor_data(data)`**: Parses incoming data from the motion sensor to extract motion status and distance.
- **`send_telegram_message(message)`**: Sends a Telegram notification if motion is detected.
- **`web_page()`**: Generates an HTML page to display the current motion status and distance.
- **`start_server()`**: Runs a lightweight web server for live updates.
- **`main()`**: Manages the overall workflow, including sensor reading, web server operation, and Telegram notifications.

---

## Example Outputs
### Web Server
- Displays "MOTION DETECTED!!" or "No Motion Detected".
- Shows distance in meters or "Unknown" if not available.

### Telegram Notification
- Example message: "Motion Detected!"

---

## Customization
1. **Notification Interval**:
   - Adjust the `NOTIFICATION_INTERVAL` variable (in seconds) for Telegram alerts.
2. **HTML Styling**:
   - Modify the CSS in the `web_page()` function to change the appearance.

---

## Troubleshooting
1. **Web server not accessible**:
   - Ensure the Pico W is connected to Wi-Fi and that you’re using the correct IP address.
   - Restart the Pico W if needed.
2. **Telegram bot not sending messages**:
   - Verify that the bot token and chat ID are correct.
   - Check your internet connection.

---

## License
This project is open-source and can be used and modified freely. Attribution is appreciated! 🚀
