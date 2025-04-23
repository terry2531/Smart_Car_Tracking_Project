import cv2
import numpy as np

# Open camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("无法Open camera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        print("Cannot read from camera帧，检查摄像头是否被占用")
        continue

    # Convert to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define red color range (two intervals)
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    # Create mask
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    # Morphological operations (remove noise)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Contour detection
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 1000:  # Ignore small areas (noise)
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green box marks red object

    # Overlay mask to highlight red regions
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # Display original frame + highlighted red area
    cv2.imshow("Original Frame", frame)  # Raw camera frame
    cv2.imshow("Red Color Detection", result)  # Only red area
    cv2.imshow("Mask", mask)  # Mask image (for debug)

    # 按 'q' 或 ESC 退出
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        print("Exit program")
        break

cap.release()
cv2.destroyAllWindows()