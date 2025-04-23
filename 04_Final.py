import cv2
import RPi.GPIO as GPIO
import time

# Set GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define motor control pins
LEFT_FORWARD = 17
LEFT_BACKWARD = 27
RIGHT_FORWARD = 5
RIGHT_BACKWARD = 6

# Set motor pins as output
motor_pins = [LEFT_FORWARD, LEFT_BACKWARD, RIGHT_FORWARD, RIGHT_BACKWARD]
for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# Control functions
def stop():
    for pin in motor_pins:
        GPIO.output(pin, GPIO.LOW)

def forward():
    GPIO.output(LEFT_FORWARD, GPIO.HIGH)
    GPIO.output(RIGHT_FORWARD, GPIO.HIGH)
    GPIO.output(LEFT_BACKWARD, GPIO.LOW)
    GPIO.output(RIGHT_BACKWARD, GPIO.LOW)

def left():
    GPIO.output(LEFT_FORWARD, GPIO.LOW)
    GPIO.output(RIGHT_FORWARD, GPIO.HIGH)
    GPIO.output(LEFT_BACKWARD, GPIO.LOW)
    GPIO.output(RIGHT_BACKWARD, GPIO.LOW)

def right():
    GPIO.output(LEFT_FORWARD, GPIO.HIGH)
    GPIO.output(RIGHT_FORWARD, GPIO.LOW)
    GPIO.output(LEFT_BACKWARD, GPIO.LOW)
    GPIO.output(RIGHT_BACKWARD, GPIO.LOW)

# Initialize camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)

# Create tracker
tracker = cv2.TrackerKCF_create()

# First frame, select target
ret, frame = cap.read()
if not ret:
    print("Cannot read from camera")
    exit()

bbox = cv2.selectROI("Tracking", frame, False)
tracker.init(frame, bbox)

frame_center_x = 480 // 2
tolerance = 50  # Tolerance range

while True:
    ret, frame = cap.read()
    if not ret:
        break

    success, bbox = tracker.update(frame)

    if success:
        x, y, w, h = [int(v) for v in bbox]
        target_center_x = x + w // 2

        # Draw rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h),
                      (0, 255, 0), 2, 1)
        cv2.putText(frame, "Tracking", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Control logic
        if abs(target_center_x - frame_center_x) <= tolerance:
            forward()
        elif target_center_x < frame_center_x - tolerance:
            left()
        else:
            right()
    else:
        stop()
        cv2.putText(frame, "Lost", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    cv2.imshow("Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup resources
stop()
cap.release()
cv2.destroyAllWindows()
GPIO.cleanup()