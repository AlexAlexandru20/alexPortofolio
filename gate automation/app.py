from website import createApp, connectDB
from website.queue_manager import get_queue
from website.gate_instructions import getMsg
from website.models import Gates
from website.routes import startDetecting, started
import multiprocessing

app = createApp()

last_lp = None

def checkQueue(queue):
    global last_lp
    while True:
            try:
                with app.app_context():
                    if not queue.empty():
                        message = queue.get(timeout=0.5)
                        print("Received message:", message)
                        lp, car_type = message
                        if lp != last_lp:
                            last_lp = lp
                            getMsg(lp, car_type)
            except Exception as e:
                print('Error:', e)
                continue


def getCameras():
    with app.app_context():
        with connectDB() as session:
            webcam1 = None
            webcam2 = None
            gate = session.query(Gates).first()
            if gate:
                webcam1 = gate.webcam1_id
                webcam2 = gate.webcam2_id
        return (webcam1, webcam2)


if __name__ == '__main__':
    queue = get_queue()
    print(queue)
    process = multiprocessing.Process(target=checkQueue, args=(queue,), daemon=True)
    process.start()

    if not started:
        startDetecting(getCameras(), queue)
    

    app.run(debug=True)
