from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from .util import getWebcams
from . import connectDB
from .models import Gates, White_List, Black_List, Admins
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import logout_user, login_user, login_required, current_user
from .detect import process_video
from .queue_manager import get_queue
from .gate_instructions import openGateRedirect, closeGateRedirect, enterEntry
import multiprocessing

routes = Blueprint('routes', __name__)

existed_car = False
login = False
started = False

LP_text = None
carT = None

processes = {}



def checkUser():
    global login

    if login:
        user = current_user.username
    else:
        user = ''

    return user


def checkGatesNum():
    gates = {}
    with connectDB() as session:
        existed_gates = session.query(Gates).all()

        if existed_gates:
            for gate in existed_gates:
                gates[gate.id] = {'name': gate.name}
        
        return gates


def startDetecting(webcams, queue):
    webcam1, webcam2 = webcams

    global processes


    if webcam1 is not None:
        try:
            if 'webcam1' in processes:
                processes['webcam1'].terminate()
                processes['webcam1'].join()
            process1 = multiprocessing.Process(target=process_video, args=(webcam1, queue))
            process1.start()
            processes['webcam1'] = process1
        except Exception as e:
            print('Error 1: ', e)

    if webcam2 is not None:
        try:
            if 'webcam2' in processes:
                processes['webcam2'].terminate()
                processes['webcam2'].join()
            process2 = multiprocessing.Process(target=process_video, args=(webcam2, queue))
            process2.start()
            processes['webcam2'] = process2
        except Exception as e:
            print('Error 2: ', e)


def stopDetecting(webcam1, webcam2):
    global processes

    if webcam1:
        if 'webcam1' in processes:
            processes['webcam1'].terminate()
            processes['webcam1'].join()
            del processes['webcam1']
    elif webcam2:
        if 'webcam2' in processes:
            processes['webcam2'].terminate()
            processes['webcam2'].join()
            del processes['webcam2']


@routes.route('/')
def home():
    gates = checkGatesNum()
    return render_template('index.html', gates=gates, user=checkUser())


@routes.route('/checkExistance')
def checkExistance():
    global existed_car, LP_text, login, carT

    return jsonify({'existed': existed_car, 'lp': LP_text, 'car_type': carT, 'login': login}), 200

@routes.route('/startDetect/', methods=['POST', 'GET'])
def startDetect():
    if request.method == 'POST':
        global started
        started = True
        queue = get_queue()

        data = request.get_json()
        webcams = data.get('webcams')

        webcam1 = webcams[0]
        webcam2 = webcams[1]

        startDetecting((webcam1, webcam2), queue)
        started = False

        return jsonify({'status': 'Processes started'}), 200


@routes.route('/auth', methods=['POST', 'GET'])
def auth():
    if request.method == 'POST':
        global login
        username = request.form.get('username')
        password = request.form.get('password')

        with connectDB() as session:
            user = session.query(Admins).filter_by(username=username).first()
            if user:
                if check_password_hash(user.password, password):
                    login_user(user, remember=True)
                    login = True
                    return jsonify(), 200
                else:
                    return jsonify({'error': 'password'}), 500
            else:
                return jsonify({'error': 'user'}), 500


@routes.route('addUser', methods=['POST', 'GET'])
def addUser():
    if request.method == 'POST':
        code = request.form.get('unique-code')
        username = request.form.get('username_create')
        password = request.form.get('password_create')

        total = 0
        print('Len', len(code))

        for n in code:
            total = total + int(n)

        print(total)    

        if len(code) == 5 and total % 8 == 7:
            with connectDB() as session:
                user = session.query(Admins).filter_by(username=username).first()

                if not user:
                    hashed = generate_password_hash(password, method='pbkdf2:sha256')

                    new_user = Admins(username=username, password=hashed)

                    session.add(new_user)

                    try:
                        session.commit()
                        return jsonify(), 200
                    except Exception as e:
                        session.rollback()
                        print(e)
                        return jsonify(), 500
                else:
                    return jsonify({'error': 'existed'}), 500
        else:
            return jsonify({'error': 'code'}), 500


@routes.route('/existedCar/<lp_text>/<car_type>')
def carDetails(lp_text, car_type):
    global existed_car, login, LP_text, carT

    LP_text = lp_text
    carT = car_type

    existed_car = True

    return render_template('existed_car.html', gates=checkGatesNum(), LP_text=lp_text, user=checkUser(), car_type=int(car_type))


@routes.route('/getCameras')
def getCameras():
    variants, cameras = getWebcams()
    return jsonify(cameras)


@routes.route('/addGate', methods=['POST', 'GET'])
def addGate():
    if request.method== 'POST':
        data = request.get_json()

        name = data.get('gate_name')
        webcam1 = data.get('webcam1')
        webcam2 = data.get('webcam2')

        with connectDB() as session:
            existed_gate = session.query(Gates).filter_by(webcam1_id=webcam1).first()
            if not existed_gate:
                new_gate = Gates(name=name, webcam1_id=webcam1, webcam2_id=webcam2)
                session.add(new_gate)

                try:
                    session.commit()
                    return redirect(url_for('routes.home'))
                
                except Exception as e:
                    session.rollback()
                    print('error', e)
                    return jsonify({'error': e}), 500
            else:
                return jsonify({'error': 'existed'}), 500
            

@routes.route('/addTo', methods=['POST', 'GET'])
def addTo():
    if request.method == 'POST':
        data = request.get_json()

        entry_type = data.get('addTo')
        owner = data.get('owner')
        LP_text = data.get('LP')

        print(entry_type)

        with connectDB() as session:
            if int(entry_type) == 0:
                white = session.query(White_List).filter_by(license_plate=LP_text).first()
                black = session.query(Black_List).filter_by(license_plate=LP_text).first()
                if white or black:
                    return jsonify({'error': 'existed'}), 500
                else:
                    new_White = White_List(license_plate=LP_text, owner=owner)

                    session.add(new_White)
            else:
                white = session.query(White_List).filter_by(license_plate=LP_text).first()
                black = session.query(Black_List).filter_by(license_plate=LP_text).first()
                if white or black:
                    return jsonify({'error': 'existed'}), 500
                else:
                    new_Black = Black_List(license_plate=LP_text, owner=owner)

                    session.add(new_Black)
            
            try:
                session.commit()
                return jsonify(), 200
            except Exception as e:
                session.rollback()
                print('Error: ', e)
                return jsonify(), 500
            

@routes.route('/editGate', methods=['POST', 'GET'])
@login_required
def editGate():
    if request.method == 'POST':
            global processes
            data = request.get_json()

            name = data.get('name')
            web1 = data.get('webcam1')
            web2 = data.get('webcam2')

            with connectDB() as session:
                gates = checkGatesNum()
                gate = session.query(Gates).first()
                if gate:
                    if name != gate.name and name != '' and name is not None:
                        gate.name = name
                    elif web1 != gate.webcam1_id:
                        gate.webcam1_id = web1
                        stopDetecting(web1, None)
                        try:
                            process1 = multiprocessing.Process(target=process_video, args=(web1,))
                            process1.start()
                            processes['webcam1'] = process1
                        except Exception as e:
                            print('Error 1: ', e)
                    elif web2 != gate.webcam2_id:
                        gate.webcam2_id = web2
                        stopDetecting(None, web2)
                        try:
                            process2 = multiprocessing.Process(target=process_video, args=(web2,))
                            process2.start()
                            processes['webcam2'] = process2
                        except Exception as e:
                            print('Error 2: ', e)

                    try:
                        session.commit()
                        return jsonify(), 200
                    except Exception as e:
                        session.rollback()
                        print(e)
                        return jsonify(), 500


    with connectDB() as session:
        gates = checkGatesNum()
        gate = session.query(Gates).first()
        gate_name = ''
        cam1_name = ''
        cam2_name = ''
        webcam1 = ''
        webcam2 = ''

        if gate:
            gate_name = gate.name
            webcam1 = gate.webcam1_id
            webcam2 = gate.webcam2_id

            cam1_name = 'Alegeți o cameră disponibilă'
            cam2_name = 'Alegeți o cameră disponibilă'

            variants, cameras = getWebcams()

            for id, cam_details in cameras.items():
                if webcam1 == id:
                    cam1_name = cam_details['name']
                elif webcam2 == id:
                    cam2_name = cam_details['name']
            
        return render_template('gate_details.html', gate_name = gate_name, webcam1=cam1_name, webcam2=cam2_name, gates=gates, webcam1_id = webcam1, webcam2_id=webcam2, login=login, user=checkUser())


@routes.route('/delGate', methods=['DELETE'])
@login_required
def delGate():
    if request.method == 'DELETE':
        with connectDB() as session:
            gate = session.query(Gates).first()
            if gate:
                webcam1 = gate.webcam1_id
                webcam2 = gate.webcam2_id
                try:
                    session.delete(gate)
                    session.commit()
                    try:
                        stopDetecting(webcam1, webcam2)
                    except Exception as e:
                        print('Error: ', e)

                    return jsonify(), 200
                except Exception as e:
                    session.rollback()
                    print(e)
                    return jsonify(), 500


@routes.route('/moveWhite/', methods=['POST', 'GET'])
def moveWhite():
    if request.method == 'POST':
        data = request.get_json()

        lp_text = data.get('lp_text')

        with connectDB() as session:
            black = session.query(Black_List).filter_by(license_plate=lp_text).first()

            if black:
                new_white = White_List(license_plate = lp_text, owner=black.owner)

                session.add(new_white)

                try:
                    session.commit()

                    session.delete(black)

                    session.commit()

                    return jsonify(), 200
                except Exception as e:
                    session.rollback()

                    print('Error: ', e)
                    return jsonify(), 500


@routes.route('/openGate', methods=['GET', 'OPEN', 'DO'])
def openGate():
    global existed_car

    if request.method == 'OPEN':
        openGateRedirect()
        data = request.get_json()

        lp = data.get('lp')
        owner = data.get('owner')
        enterEntry(lp, owner, 1)
        return jsonify(), 200
    
    if request.method == 'DO':
        openGateRedirect()
        return jsonify(), 200
    
    return jsonify({'exists': existed_car}), 200

@routes.route('/closeGate')
def closeGate():
    closeGateRedirect()
    return jsonify(), 200


@routes.route('/logout')
@login_required
def logout():
    global login
    logout_user()
    login = False
    return redirect(url_for('routes.home'))