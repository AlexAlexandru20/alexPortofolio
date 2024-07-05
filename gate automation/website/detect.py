from ultralytics import YOLO
import cv2, os
from .util import getCar, readLP
from .sort.sort import *

auto = YOLO(os.path.join('app', 'models', 'yolov8n.pt'))
lp = YOLO(os.path.join('app', 'models', 'best.pt'))

mot_tracker = Sort()

video_path = os.path.join('app', 'video', 'video9.mp4')

vehicles = [2, 3, 5, 7]

fps = 0
interval = 0
frame_num = 0

recognitions = {}  # Store all recognitions
no_detections = []

lp_path = os.path.join('website', 'static', 'images', 'lp.jpg')
car_path = os.path.join('website', 'static', 'images', 'car.jpg')


def stringedit(tupleGate):
        if isinstance(tupleGate, tuple):
            index, = tupleGate
            return index
        else:
            return tupleGate
    

def process_video(gate_id, queue):
        print('Gate: ', gate_id)
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print('Error: cap is not open')
            return
        
        fps= cap.get(cv2.CAP_PROP_FPS)
        frame_num = 0

        while True:
            ret, frame = cap.read()

            if not ret:
                break
            
            if frame_num % 5 == 0:
                _process_frame(frame, queue)
            
            frame_num += 1
        
        cap.release()

def _process_frame(frame, queue):
        from app import app
        from .routes import existed_car
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        detections = auto(img_rgb)[0]

        detections_ = []

        for detection in detections.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = detection

            if int(class_id) in vehicles:
                cv2.rectangle(img_rgb, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                detections_.append(detection)
            
        if detections_:
            track_ids = mot_tracker.update(np.asarray(detections_))

            license_plates = lp(img_rgb)[0]

            # Initialize flags
            bgr_car_crop_saved = False
            LP_crop_saved = False

            for license_plate in license_plates.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = license_plate

                cv2.rectangle(img_rgb, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)

                xcar1, ycar1, xcar2, ycar2, car_id = getCar(license_plate, track_ids)

                if car_id != -1:
                    LP_crop = img_rgb[int(y1):int(y2), int(x1):int(x2), :]
                    cv2.imwrite(lp_path, LP_crop)
                    LP_crop_gray = cv2.cvtColor(LP_crop, cv2.COLOR_BGR2GRAY)

                    LP_crop_thresh = cv2.adaptiveThreshold(LP_crop_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 13, 4)
                    
                    LP_text, LP_type, LP_score = readLP(LP_crop_thresh)

                    if not LP_text:
                        LP_crop_blur = cv2.GaussianBlur(LP_crop, (5, 5), 2)
                        LP_crop_blur1 = cv2.medianBlur(LP_crop_blur, 5)
                        LP_crop_gray = cv2.cvtColor(LP_crop_blur1, cv2.COLOR_BGR2GRAY)
                        LP_crop_thresh = cv2.adaptiveThreshold(LP_crop_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)
                        LP_text, LP_type, LP_score = readLP(LP_crop_thresh)
                        

                    if LP_type is not None:
                        if car_id not in recognitions:
                            recognitions[car_id] = []

                        recognitions[car_id].append({'LP_text': LP_text,
                                                        'LP_type': LP_type,
                                                        'LP_score': LP_score})
                        print(recognitions)
                        
                        for car_id, recognitions_list in recognitions.items():
                            if len(recognitions_list) >= 4:
                                min_type = min(recognition['LP_type'] for recognition in recognitions_list)
                                if min_type == 0:
                                    max_score = max(recognition['LP_score'] for recognition in recognitions_list if recognition['LP_type'] == 0)

                                    most_common_LP = [recognition['LP_text'] for recognition in recognitions_list if recognition['LP_score'] == max_score]

                                    if most_common_LP:
                                        most_common_LP = most_common_LP[0]

                                    try:
                                        os.remove(car_path)
                                        bgr_car_crop = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
                                        cv2.imwrite(car_path, bgr_car_crop)
                                        bgr_car_crop_saved = True
                                        os.remove(lp_path)   
                                        cv2.imwrite(lp_path, LP_crop)
                                        LP_crop_saved = True
                                    except Exception as e:
                                        print('Error: ', e)
                                                
                                    if bgr_car_crop_saved and LP_crop_saved:
                                        print('Sending Message: ', most_common_LP)
                                        putMessage(most_common_LP, 0, app, queue)
                                        print('Message sent')
                                        bgr_car_crop_saved = False
                                        LP_crop_saved = False

                                elif min_type == 1:
                                    max_score = max(recognition['LP_score'] for recognition in recognitions_list if recognition['LP_type'] == 1)

                                    most_common_LP = [recognition['LP_text'] for recognition in recognitions_list if recognition['LP_score'] == max_score]

                                    if most_common_LP:
                                        most_common_LP = most_common_LP[0]
                                    try:
                                        bgr_car_crop = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
                                        if os.path.exists(car_path):
                                            os.remove(car_path)
                                        try:
                                            cv2.imwrite(car_path, bgr_car_crop)
                                        except Exception as e:
                                            print('Error at saving picture1: ', e)
                                        bgr_car_crop_saved = True
                                        
                                        if os.path.exists(lp_path):
                                            os.remove(lp_path)
                                        try:
                                            cv2.imwrite(lp_path, LP_crop)
                                        except Exception as e:
                                            print('Error at saving picture2: ', e)
                                        LP_crop_saved = True
                                    except Exception as e:
                                        print('Error: ', e)
                                                
                                    if bgr_car_crop_saved and LP_crop_saved:
                                        print('Sending Message: ', most_common_LP)
                                        putMessage(most_common_LP, 1, app, queue)
                                        print('Message sent')
                                        bgr_car_crop_saved = False
                                        LP_crop_saved = False
        else:
            existed_car = False
            no_detections.append('now')

            if len(no_detections) == 5:
                recognitions.clear()
                no_detections.clear()
            
            


def putMessage(msg, car_type, app, queue):
    try:
        with app.app_context():
            print('Queue 2: ', queue)
            queue.put((msg, car_type))
    except Exception as e:
        print('Error at sending queue: ', e)