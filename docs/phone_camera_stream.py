import cv2 as cv
import time

#FPS = 30; Resolution = 1920 x 1080
url = "http://192.168.1.53:8080/video"
cap = cv.VideoCapture(url)
frame_count = 0
start_time = time.time()
check = True

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to receive frame")
        break
    if check:
        height, width = frame.shape[:2]
        print("Resolution:", width, "x", height)
        check = False
    frame_count +=1
    cv.imshow("Phone Camera", frame)

    if cv.waitKey(1) & 0xFF == 27:
        break

elapsed = time.time() - start_time
fps = frame_count/elapsed
print(f"FPS: {int(fps)}")

cap.release()
cv.destroyAllWindows()