import cv2
import RPi.GPIO as GPIO
import time

# 设置 GPIO 模式
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# 定义电机控制引脚
LEFT_FORWARD = 17
LEFT_BACKWARD = 27
RIGHT_FORWARD = 5
RIGHT_BACKWARD = 6

# 设置引脚为输出
motor_pins = [LEFT_FORWARD, LEFT_BACKWARD, RIGHT_FORWARD, RIGHT_BACKWARD]
for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# 控制函数
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

# 摄像头初始化
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)

# 创建追踪器
tracker = cv2.TrackerKCF_create()

# 第一帧，选择目标
ret, frame = cap.read()
if not ret:
    print("无法读取摄像头")
    exit()

bbox = cv2.selectROI("Tracking", frame, False)
tracker.init(frame, bbox)

frame_center_x = 480 // 2
tolerance = 50  # 容忍范围

while True:
    ret, frame = cap.read()
    if not ret:
        break

    success, bbox = tracker.update(frame)

    if success:
        x, y, w, h = [int(v) for v in bbox]
        target_center_x = x + w // 2

        # 绘图
        cv2.rectangle(frame, (x, y), (x + w, y + h),
                      (0, 255, 0), 2, 1)
        cv2.putText(frame, "Tracking", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # 控制逻辑
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

# 清理资源
stop()
cap.release()
cv2.destroyAllWindows()
GPIO.cleanup()