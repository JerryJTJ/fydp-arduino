import time
import serial
from random import randrange

START_MARKER = "<"
END_MARKER = ">"
DATA_STARTED = False
DATA_BUFFER = ""
MESSAGE_COMPLETE = False

# Functions:


def setupSerial(baudRate, serialPortName):

    global serialPort

    serialPort = serial.Serial(
        port=serialPortName, baudrate=baudRate, timeout=0, rtscts=True
    )

    print("Serial port " + serialPortName + " opened  Baudrate " + str(baudRate))

    waitForArduino()


def sendToArduino(stringToSend):
    """Sends a message to the Arduino with start- and end-markers."""

    # this adds the start- and end-markers before sending
    global serialPort

    stringWithMarkers = "{}{}{}".format(START_MARKER, stringToSend, END_MARKER)

    try:
        serialPort.write(stringWithMarkers.encode("utf-8"))
    except serial.SerialException as error:
        print("Error sending data to Arduino:", error)


def recvLikeArduino():

    global serialPort, DATA_STARTED, DATA_BUFFER, MESSAGE_COMPLETE

    if serialPort.inWaiting() > 0 and not MESSAGE_COMPLETE:
        x = serialPort.read().decode("utf-8")  # decode needed for Python3

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


def waitForArduino():

    # wait until the Arduino sends 'Arduino is ready' - allows time for Arduino reset
    # it also ensures that any bytes left over from a previous message are discarded

    print("Waiting for Arduino to reset")

    msg = ""
    while msg.find("Arduino is ready") == -1:
        msg = recvLikeArduino()
        if not (msg == "XXX"):
            print(msg)


# Program

# Setup Serial Port, change baud rate & port as needed
setupSerial(9600, "COM3")

# Code for Testing
messagesList = ["ERROR", "OK", "OK", "OK"]
count = 0
replyCount = 0
prevTime = time.time()
while True:
    # check for a reply
    arduinoReply = recvLikeArduino()
    if not (arduinoReply == "XXX"):
        print(replyCount, ": Arduino Recieved: \t\t\t\t", arduinoReply)
        replyCount += 1

        # send a message at intervals
    if time.time() - prevTime > 1.0:
        messageToSend = messagesList[randrange(3)]
        sendToArduino(messageToSend)
        print(count, ": Python Sent Message: \t\t\t", messageToSend)
        prevTime = time.time()
        count += 1
