import csv, easyocr, string, re

reader = easyocr.Reader(['en'], gpu=False)

ro_jud=  ['AB', 'AR', 'AG', 'BC', 'BH', 'BN', 'BT', 'BR', 'BV', 'BZ', 'CL', 'CS', 'CJ', 'CT', 'CV', 'DB', 'DJ', 'GL', 'GR', 'GJ', 'HR', 'HD', 'IL', 'IS', 'IF', 'MM', 'MH', 'MS', 'NT', 'OT', 'PH', 'SJ', 'SM', 'SB', 'SV', 'TR', 'TM', 'TL', 'VL', 'VS', 'VN']

char_to_int = {'O': '0',
               'I': '1',
               'J': '3',
               'A': '4',
               'S': '5',
               'G': '6',
               '/': '4',
               'T': '1',
               'Z': '7',
               'z': '7',
               'B': '8',
               'L': '4'}

mai_changes = {'L': 'I',
               'l': 'I',
               'p': 'I',
               '4': 'A',
               '1': 'I',
               'i': 'I'}

int_to_char = {'0': 'O',
               '1': 'I',
               '3': 'J',
               '4': 'A',
               '5': 'S',
               '6': 'G',
               '8': 'B'}

def auto_jud_format(text):
    
    if  (text[2] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[2] in char_to_int.keys()) and \
        (text[3] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[3] in char_to_int.keys()) and \
        (text[4] in string.ascii_uppercase or text[4] in int_to_char.keys()) and \
        (text[5] in string.ascii_uppercase or text[5] in int_to_char.keys()) and \
        (text[6] in string.ascii_uppercase or text[6] in int_to_char.keys()):
        return True
    return False


def auto_buc_format(text):
    if  (text[2] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[2] in char_to_int.keys()) and \
        (text[3] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[3] in char_to_int.keys()) and \
        (text[4] in string.ascii_uppercase or text[4] in int_to_char.keys()) and \
        (text[5] in string.ascii_uppercase or text[5] in int_to_char.keys()) and \
        (text[6] in string.ascii_uppercase or text[6] in int_to_char.keys()):
        return True
    
    elif(text[2] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[2] in char_to_int.keys()) and \
        (text[3] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[3] in char_to_int.keys()) and \
        (text[4] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[4] in char_to_int.keys()) and \
        (text[5] in string.ascii_uppercase or text[5] in int_to_char.keys()) and \
        (text[6] in string.ascii_uppercase or text[6] in int_to_char.keys()) and \
        (text[7] in string.ascii_uppercase or text[7] in int_to_char.keys()):
        return True
    
    return False


def complies_format_mai(text):
    if len(text) != 8:
        return False
    
    if (text[0] == 'M') and \
       (text[1] == 'A' or text[1] in mai_changes.keys()) and \
       (text[2] == 'I' or text[2] in mai_changes.keys()) and \
       (text[3] in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'] or text[3] in char_to_int.keys()) and \
       (text[4] in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'] or text[4] in char_to_int.keys()) and \
       (text[5] in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'] or text[5] in char_to_int.keys()) and \
       (text[6] in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'] or text[6] in char_to_int.keys()) and \
       (text[7] in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'] or text[7] in char_to_int.keys()):
        return True
    else:
        return False



def formatLP(text):
    license_plates = ''
    mapping = {0: int_to_char, 1: int_to_char, 4: int_to_char, 5: int_to_char, 6: int_to_char, 2: char_to_int, 3: char_to_int}

    for j in [0, 1, 2, 3, 4, 5, 6]:
        if text[j] in mapping[j].keys():
            license_plates += mapping[j][text[j]]
        else:
            license_plates += text[j]
    
    return license_plates


def formatLP_MAI(text):
    license_plates = ''
    mapping = {0: mai_changes, 1: mai_changes, 2: mai_changes, 3: char_to_int, 4: char_to_int, 5: char_to_int, 6: char_to_int, 7: char_to_int}

    for j in [0, 1, 2, 3, 4, 5, 6, 7]:
        if text[j] in mapping[j].keys():
            license_plates += mapping[j][text[j]]
        else:
            license_plates += text[j]

    return license_plates


def getCar(license_plate, vehicle_track_ids):
    x1, y1, x2, y2, score, class_id = license_plate

    foundIt = False

    for j in range(len(vehicle_track_ids)):
        xcar1, ycar1, xcar2, ycar2, car_id = vehicle_track_ids[j]

        if x1 > xcar1 and y1 > ycar1 and x2 < xcar2 and y2 < ycar2:
            car_nr = j
            foundIt = True
            break
    if foundIt:
        return vehicle_track_ids[car_nr]
        
    return -1, -1, -1, -1, -1


def readLP(LPCrop):

    detections = reader.readtext(LPCrop, paragraph=True)
    replace = [' ', '.', ',', '-', '_', '*', "'", ':', ';']

    for detection in detections:
        bbox, text = detection

        for strg in replace:
            text = text.replace(strg, '')
            text = text.upper()
        print('Text ', text)

        validated_text = validateText(text)

        if complies_format_mai(text):
            return formatLP_MAI(text), 0
        elif validated_text is not None:
            if auto_jud_format(validated_text) or auto_buc_format(validated_text):
                return formatLP(validated_text), 1
        
    return None, None


def validateText(text):
    if len(text) == 7:
        return text
    
    for jud in ro_jud:
        index_jud = text.find(jud)

        if index_jud != -1:
            remaining_length = len(text) - index_jud - len(jud)
            print('Length: ', remaining_length)

            if remaining_length >= 5:
                print(f'Remaining letters length and jud: {jud} / {remaining_length}' )
                formated_license_plate = jud + text[index_jud + len(jud):]
                print('License: ', formated_license_plate)

                return formated_license_plate    
    
    index_jud = text.find('B')

    if index_jud != -1:
        remaining_length = len(text) - index_jud - 1
        print('Length2: ', remaining_length)

        if remaining_length >= 5:
            print(f'Remaining letters length2 {remaining_length}' )
            formated_license_plate = 'B' + text[index_jud + 1:]
            print('License2: ', formated_license_plate)

            return formated_license_plate
    
    return None