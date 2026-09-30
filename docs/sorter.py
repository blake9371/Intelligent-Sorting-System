import cv2
import numpy as np
import serial
import time

esp = serial.Serial('COM10', 115200, timeout=1)

time.sleep(2)

url = "http://10.98.116.130:8080/video"
cap = cv2.VideoCapture(url)

# Minimum area required for an inner contour
MIN_HOLE_AREA = 1500

# Number of consecutive same classifications required
REQUIRED_CONSECUTIVE = 5

# Current servo/classification state
# Start with 1
current_state = 1

# Recent classification history
signal_history = []


while True:

    ret, frame = cap.read()

    if not ret:
        print("Error")
        break

    # ---------------- ROI ----------------

    x1, y1 = 300, 300
    x2, y2 = 1200, 1000

    frame = frame[y1:y2, x1:x2]

    # ---------------- EDGE DETECTION ----------------

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(
        gray,
        (11, 11),
        0
    )

    edges = cv2.Canny(
        blur,
        60,
        150
    )

    kernel = np.ones((5, 5), np.uint8)

    mask = cv2.morphologyEx(
        edges,
        cv2.MORPH_CLOSE,
        kernel
    )

    # ---------------- FIND CONTOURS ----------------

    contours, hierarchy = cv2.findContours(
        mask,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if len(contours) > 0 and hierarchy is not None:

        # Find largest contour
        largest_index = max(
            range(len(contours)),
            key=lambda i: cv2.contourArea(contours[i])
        )

        largest_contour = contours[largest_index]

        largest_area = cv2.contourArea(
            largest_contour
        )

        # ---------------- VALID OBJECT ----------------

        if 1000 < largest_area < 20000:

            # ---------------- FIND INNER CONTOUR ----------------

            hole_contour = None
            hole_area = 0

            child = hierarchy[0][largest_index][2]

            while child != -1:

                current_area = cv2.contourArea(
                    contours[child]
                )

                if current_area > hole_area:
                    hole_area = current_area
                    hole_contour = contours[child]

                child = hierarchy[0][child][0]

            # ---------------- CLASSIFICATION ----------------

            if hole_area >= MIN_HOLE_AREA:

                label = "NUT"

                # Nut = 1
                current_signal = 1

            else:

                label = "BOLT"

                # Bolt = 2
                current_signal = 2

            # ---------------- SIGNAL HISTORY ----------------

            signal_history.append(current_signal)

            # Keep only latest 5 signals
            if len(signal_history) > REQUIRED_CONSECUTIVE:
                signal_history.pop(0)

            # ---------------- STATE CHANGE ----------------

            if len(signal_history) == REQUIRED_CONSECUTIVE:

                # Five consecutive 1s
                if all(signal == 1 for signal in signal_history):

                    if current_state != 1:

                        esp.write(b'1')

                        print(
                            "5 CONSECUTIVE NUTS → "
                            "Sent 1 → Servo 135°"
                        )

                        current_state = 1

                    # Clear history after evaluating
                    signal_history.clear()

                # Five consecutive 2s
                elif all(signal == 2 for signal in signal_history):

                    if current_state != 2:

                        esp.write(b'2')

                        print(
                            "5 CONSECUTIVE BOLTS → "
                            "Sent 2 → Servo 45°"
                        )

                        current_state = 2

                    # Clear history after evaluating
                    signal_history.clear()

            # ---------------- DRAW OUTER CONTOUR ----------------

            x, y, w, h = cv2.boundingRect(
                largest_contour
            )

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            cv2.drawContours(
                frame,
                [largest_contour],
                -1,
                (0, 255, 0),
                2
            )

            # ---------------- DRAW HOLE ----------------

            if (
                hole_contour is not None
                and hole_area >= MIN_HOLE_AREA
            ):

                cv2.drawContours(
                    frame,
                    [hole_contour],
                    -1,
                    (255, 0, 0),
                    2
                )

            # ---------------- DISPLAY ----------------

            cv2.putText(
                frame,
                f"{label} | Hole: {hole_area:.0f}",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            # Show classification history
            history_text = "".join(
                str(s) for s in signal_history
            )

            cv2.putText(
                frame,
                f"History: {history_text}",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2
            )

            # Show current state
            cv2.putText(
                frame,
                f"State: {current_state}",
                (20, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

    # ---------------- DISPLAY ----------------

    cv2.imshow("Camera", frame)
    cv2.imshow("Mask", mask)

    if cv2.waitKey(1) & 0xFF == 27:
        break


cap.release()
esp.close()
cv2.destroyAllWindows()