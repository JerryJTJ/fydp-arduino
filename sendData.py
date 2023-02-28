import time
import serial
from random import randrange

START_MARKER = "<"
END_MARKER = ">"
DATA_STARTED = False
DATA_BUFFER = ""
MESSAGE_COMPLETE = False

# Functions:
def setup_serial(baud_rate, serial_port_name):
    """Setups the serial port"""

    global SERIALPORT

    SERIALPORT = serial.Serial(
        port=serial_port_name, baudrate=baud_rate, timeout=0, rtscts=True
    )

    print("Serial port " + serial_port_name + " opened  Baudrate " + str(baud_rate))

    wait_for_arduino()


def send_to_arduino(string_to_send):
    """Sends a message to the Arduino with start- and end-markers."""

    # this adds the start- and end-markers before sending
    global SERIALPORT

    string_with_markers = f"{START_MARKER}{string_to_send}{END_MARKER}"

    try:
        SERIALPORT.write(string_with_markers.encode("utf-8"))
    except serial.SerialException as error:
        print("Error sending data to Arduino:", error)


def recv_like_arduino():
    """Setups start/end markers for recieving"""

    global DATA_STARTED, DATA_BUFFER, MESSAGE_COMPLETE

    if SERIALPORT.inWaiting() > 0 and not MESSAGE_COMPLETE:
        x = SERIALPORT.read().decode("utf-8")  # decode needed for Python3

        if DATA_STARTED:
            if x != END_MARKER:
                DATA_BUFFER += x
            else:
                DATA_STARTED = False
                MESSAGE_COMPLETE = True
        elif x == START_MARKER:
            DATA_BUFFER = ""
            DATA_STARTED = True

    if MESSAGE_COMPLETE:
        MESSAGE_COMPLETE = False
        return DATA_BUFFER
    else:
        return "XXX"


def wait_for_arduino():
    """Wait until the Arduino sends 'Arduino is ready' - allows time for Arduino reset.
    It also ensures that any bytes left over from a previous message are discarded"""

    print("Waiting for Arduino to reset")

    msg = ""
    while msg.find("Arduino is ready") == -1:
        msg = recv_like_arduino()
        if msg != "XXX":
            print(msg)


# Program
def send_message(baud_rate, port, message, timeout):
    """Sends message thru Serial port"""

    # Setup Serial Port, change baud rate & port as needed
    setup_serial(baud_rate, port)

    # Send a message at intervals
    send_to_arduino(message)
    print(": Python Sent Message: \t\t\t", message)

    timeout_time = time.time() + timeout

    while True:
        # Check for a reply
        arduino_reply = recv_like_arduino()

        if arduino_reply != "XXX":
            print(": Arduino Recieved: \t\t\t", arduino_reply)
            SERIALPORT.close()
            return

        if time.time() > timeout_time:
            print("Error: Timed out after ", timeout, " s.")
            SERIALPORT.close()
            return


# Code for Testing
# send_message(9600, "COM3", "ERROR", 5)
# send_message(9600, "COM3", "OK", 5)
# send_message(9600, "COM3", "ERROR", 0.001)
# send_message(9600, "COM3", "OK", 0.001)
