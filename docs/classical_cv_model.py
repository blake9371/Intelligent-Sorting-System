import cv2
import numpy as np
import os
import glob

IMAGE_FOLDER = os.path.join(os.getcwd(), "Dataset1", "fasteners", "1")
THRESHOLD = 0.05
R_list = []

image_paths = []
image_paths.extend(glob.glob(os.path.join(IMAGE_FOLDER, "*.jpg")))

if len(image_paths) == 0:
    raise RuntimeError(f"No images found in folder: {IMAGE_FOLDER}")

print(f"Found {len(image_paths)} images.")
print("=" * 50)
z=1
for image_path in image_paths:
    print(f"\nProcessing: {os.path.basename(image_path)}")
    image = cv2.imread(image_path)
    if image is None:
        print("Could not read image. Skipping...")
        continue
    display = image.copy()

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5, 5),0)
    _, binary = cv2.threshold(blur,0,255,cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(binary,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        print("No object detected. Skipping...")
        continue
    largest = max(contours,key=cv2.contourArea)
    image_area = binary.shape[0] * binary.shape[1]

    # # If the detected region is huge, assume the
    # # background is white and invert it.
    # if cv2.contourArea(largest) > image_area * 0.5:
    #     binary = cv2.bitwise_not(binary)

    kernel = np.ones((5, 5),np.uint8)
    binary = cv2.morphologyEx(binary,cv2.MORPH_OPEN,kernel)
    binary = cv2.morphologyEx(binary,cv2.MORPH_CLOSE,kernel)
    contours, hierarchy = cv2.findContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None or len(contours) == 0:
        print("No contours found. Skipping...")
        continue

    outer_contours = []
    for i, contour in enumerate(contours):
        parent = hierarchy[0][i][3]
        area = cv2.contourArea(contour)
        if parent == -1 and area > 500:
            outer_contours.append((i, contour, area))
    if len(outer_contours) == 0:
        print("Could not find object contour. Skipping...")
        continue

    outer_index, outer_contour, outer_area = max(outer_contours,key=lambda x: x[2])

    hole_contours = []
    child = hierarchy[0][outer_index][2]

    while child != -1:
        hole = contours[child]
        hole_area = cv2.contourArea(hole)
        if hole_area > 10:
            hole_contours.append(hole)
        child = hierarchy[0][child][0]

    if len(hole_contours) > 0:
        largest_hole = max(hole_contours,key=cv2.contourArea)
        hole_area = cv2.contourArea(largest_hole)
    else:
        hole_area = 0

    R = hole_area/outer_area
    R_list.append(R)

    if R > THRESHOLD:
        classification = "NUT"
    else:
        classification = "BOLT"

    print(f"Outer area : {outer_area:.2f}")
    print(f"Hole area  : {hole_area:.2f}")
    print(f"R          : {R:.4f}")
    print(f"Result     : {classification}")
    print("*"*10)

    cv2.drawContours(display,[outer_contour],-1,(0, 255, 0),3)
    if len(hole_contours) > 0:
        cv2.drawContours(display,[largest_hole],-1,(255, 0, 0),3)

    cv2.putText(display,f"R = {R:.4f}",(30, 40),cv2.FONT_HERSHEY_SIMPLEX,1,(0, 255, 255),2)
    cv2.putText(display,classification,
        (30, 85),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.5,
        (0, 255, 0)
        if classification == "NUT"
        else (0, 0, 255),
        3
    )

    cv2.imwrite(f"segmentation/{z}.jpg",binary)
    cv2.imwrite(f"classification/{z}.jpg",display)
    z+=1
