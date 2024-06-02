import cv2, os
import matplotlib.pyplot as plt
from ultralytics import YOLO
from sort.sort import *
from util import readLP, getCar

mot_tracker = Sort()

auto = YOLO(os.path.join('app', 'models', 'yolov8n.pt'))
lp = YOLO(os.path.join('app', 'models', 'best.pt'))
img_path = os.path.join('app', 'img', 'car10.jpg')
vehicles = [2, 3, 5, 7]

img = cv2.imread(img_path)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

detections = auto(img_rgb)[0]

detections_ = []
recognitions = {}

for detection in detections.boxes.data.tolist():
    x1, y1, x2, y2, score, class_id = detection

    if int(class_id) in vehicles:
        cv2.rectangle(img_rgb, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        detections_.append(detection)
    
if detections_:
    track_ids = mot_tracker.update(np.asarray(detections_))

    license_plates = lp(img_rgb)[0]

    for license_plate in license_plates.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = license_plate

        cv2.rectangle(img_rgb, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)

        xcar1, ycar1, xcar2, ycar2, car_id = getCar(license_plate, track_ids)

        if car_id != -1:
            LP_crop = img_rgb[int(y1):int(y2), int(x1):int(x2), :]

            LP_crop_blur = cv2.GaussianBlur(LP_crop, (5, 5), 2)

            LP_crop_gray = cv2.cvtColor(LP_crop, cv2.COLOR_BGR2GRAY)

            LP_crop_thresh = cv2.adaptiveThreshold(LP_crop_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 13, 4)
                    
            LP_text, LP_type = readLP(LP_crop_thresh)
            print('License Plate: ', LP_text)

            if not LP_text:
                LP_crop_blur1 = cv2.medianBlur(LP_crop_blur, 5)
                LP_crop_gray = cv2.cvtColor(LP_crop_blur1, cv2.COLOR_BGR2GRAY)
                LP_crop_thresh = cv2.adaptiveThreshold(LP_crop_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)
                LP_text, LP_type = readLP(LP_crop_thresh)
                        
            print('License Plate: ', LP_text)

            cv2.imwrite(os.path.join('app', 'img', 'car_img_2.jpg'), LP_crop_thresh)

