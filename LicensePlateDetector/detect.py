from ultralytics import YOLO
import cv2, os
from sort.sort import *
from util import getCar, readLP
from collections import Counter

class VehicleDetection:
    def __init__(self, gate_id_tuple, message_queue):
        self.mot_tracker = Sort()
        self.auto = YOLO(os.path.join('app', 'models', 'yolov8n.pt'))
        self.lp = YOLO(os.path.join('app', 'models', 'best.pt'))
        self.video_path = os.path.join('app', 'video', 'video8.mp4')
        self.vehicles = [2, 3, 5, 7]
        self.fps = 0
        self.interval = 0
        self.frame_num = 0
        self.gate_id = self.stringedit(gate_id_tuple)
        self.message_queue = message_queue
        self.recognitions = {}  # Store all recognitions
        self.lp_path = os.path.join('app', 'img', 'lp_img.jpg')
        self.car_path = os.path.join('app', 'img', 'car_img.jpg')


    def stringedit(self, tupleGate):
        if isinstance(tupleGate, tuple):
            index, = tupleGate
            return index
        else:
            return tupleGate
    

    def process_video(self):
        print(self.gate_id)
        cap = cv2.VideoCapture(self.video_path)

        if not cap.isOpened():
            print('Error: cap is not open')
            return
        
        self.fps= cap.get(cv2.CAP_PROP_FPS)
        self.frame_num = 0

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            self._process_frame(frame)
            
            self.frame_num += 1
        
        cap.release()

    def _process_frame(self, frame):
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        detections = self.auto(img_rgb)[0]

        detections_ = []

        for detection in detections.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = detection

            if int(class_id) in self.vehicles:
                cv2.rectangle(img_rgb, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                detections_.append(detection)
            
        if detections_:
            track_ids = self.mot_tracker.update(np.asarray(detections_))

            license_plates = self.lp(img_rgb)[0]

            # Initialize flags
            bgr_car_crop_saved = False
            LP_crop_saved = False

            for license_plate in license_plates.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = license_plate

                cv2.rectangle(img_rgb, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)

                xcar1, ycar1, xcar2, ycar2, car_id = getCar(license_plate, track_ids)

                if car_id != -1:
                    LP_crop = img_rgb[int(y1):int(y2), int(x1):int(x2), :]
                    cv2.imwrite(self.lp_path, LP_crop)
                    LP_crop_gray = cv2.cvtColor(LP_crop, cv2.COLOR_BGR2GRAY)

                    LP_crop_thresh = cv2.adaptiveThreshold(LP_crop_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 13, 4)
                    
                    LP_text, LP_type = readLP(LP_crop_thresh)
                    print('License Plate: ', LP_text)

                    if not LP_text:
                        LP_crop_blur = cv2.GaussianBlur(LP_crop, (5, 5), 2)
                        LP_crop_blur1 = cv2.medianBlur(LP_crop_blur, 5)
                        LP_crop_gray = cv2.cvtColor(LP_crop_blur1, cv2.COLOR_BGR2GRAY)
                        LP_crop_thresh = cv2.adaptiveThreshold(LP_crop_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)
                        LP_text, LP_type = readLP(LP_crop_thresh)
                        
                    print('License Plate: ', LP_text)

                    if LP_type is not None:
                        if car_id not in self.recognitions:
                            self.recognitions[car_id] = []

                        self.recognitions[car_id].append({'LP_text': LP_text,
                                                        'LP_type': LP_type})
                        
                        for car_id, recognitions_list in self.recognitions.items():
                            print('Length of list: ', len(recognitions_list))
                            if len(recognitions_list) >= 10:
                                min_type = min(recognition['LP_type'] for recognition in recognitions_list)
                                if min_type == 0:
                                    all_LP = Counter(recognition['LP_text'] for recognition in recognitions_list if recognition['LP_type'] == 0)
                                    most_common_LP, count = all_LP.most_common(1)[0]
                                    try:
                                        bgr_car_crop = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)  # Slice to swap BGR channels
                                        cv2.imwrite(self.car_path, bgr_car_crop)
                                        bgr_car_crop_saved = True
                                                    
                                        cv2.imwrite(self.lp_path, LP_crop)
                                        LP_crop_saved = True
                                    except Exception as e:
                                        print('Error: ', e)
                                                
                                    if bgr_car_crop_saved and LP_crop_saved:
                                        self.message_queue.put((self.gate_id, most_common_LP, 0))
                                        bgr_car_crop_saved = False
                                        LP_crop_saved = False

                                elif min_type == 1:
                                    all_LP = Counter(recognition['LP_text'] for recognition in recognitions_list if recognition['LP_type'] == 1)
                                    most_common_LP, count = all_LP.most_common(1)[0]
                                    try:
                                        bgr_car_crop = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)  # Slice to swap BGR channels
                                        cv2.imwrite(self.car_path, bgr_car_crop)
                                        bgr_car_crop_saved = True
                                                    
                                        cv2.imwrite(self.lp_path, LP_crop)
                                        LP_crop_saved = True
                                    except Exception as e:
                                        print('Error: ', e)
                                                
                                    if bgr_car_crop_saved and LP_crop_saved:
                                        self.message_queue.put((self.gate_id, most_common_LP, 1))
                                        bgr_car_crop_saved = False
                                        LP_crop_saved = False