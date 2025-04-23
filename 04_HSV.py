import cv2
import numpy as np

# 打开摄像头
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("无法打开摄像头")
    exit()

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        print("无法读取摄像头帧，检查摄像头是否被占用")
        continue

    # 转换为 HSV 颜色空间
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 定义红色范围（包含两个区间）
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    # 生成掩码
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    # 形态学操作（去除噪点）
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # 轮廓检测
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 画出轮廓
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 1000:  # 忽略小面积噪声
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # 绿色框标记红色物体

    # 叠加掩码到原始图像，让红色区域更明显
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # 显示原始图像 + 标记的红色区域
    cv2.imshow("Original Frame", frame)  # 原始摄像头画面
    cv2.imshow("Red Color Detection", result)  # 只显示红色区域
    cv2.imshow("Mask", mask)  # 掩码图像（调试用）

    # 按 'q' 或 ESC 退出
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        print("退出程序")
        break

cap.release()
cv2.destroyAllWindows()