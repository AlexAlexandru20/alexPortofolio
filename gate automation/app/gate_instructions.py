from . import connectDB
from flask_sse import sse
from .models import White_List, Black_List, Entries
from datetime import datetime

def getMsg(lp, car_type):
    with connectDB() as session:
        if int(car_type) == 0:
            print('Autospeciala entered')
            openGateRedirect()
            enterEntry(lp, 'Autospecială', car_type)
        
        else:
            white = session.query(White_List).filter_by(license_plate=lp).first()
            black = session.query(Black_List).filter_by(license_plate=lp).first()

            if white:
                openGateRedirect()
                enterEntry(lp, white.owner, car_type)
            elif black:
                sse.publish({'message':lp}, type='black')
                print('Car it\'s in black list')
            else:
                sse.publish({'message':lp}, type='existed')
                print('Car isn\'t in any list')


def openGateRedirect():
    from .routes import existed_car
    from app import last_lp

    last_lp = None

    existed_car = False
    print('Opening Gate')


def closeGateRedirect():
    print('Closing Gate')


def enterEntry(lp, owner, car_type):
    with connectDB() as session:
        entry = datetime.now()
        new_entry = Entries(license_plate=lp, owner=owner, entry=entry, car_type=car_type)

        session.add(new_entry)

        try:
            session.commit()
            print('Details entered')
        except Exception as e:
            session.rollback()
            print('Error at entering Entries: ', e)