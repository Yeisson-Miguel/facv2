import cv2
from cvzone.FaceMeshModule import FaceMeshDetector
from api.anti_spoofing.config.settings import *
from api.anti_spoofing.commons.blink_count_haar import *
from api.anti_spoofing.commons.face_orientation import *
from api.face_liveness.face_liveness_detection.face_liveness import *
from api.anti_spoofing.commons.save_info_file import *

detector = FaceMeshDetector(maxFaces=1)
#cap = cv2.VideoCapture(0, cv2.CAP_ANY) 

"""
Metodo principal de la aplicacion, en este se hace la transmision de Stream,
se valida el reconocimiento Liveness, desbloqueo facial mediante movimientos del rostro
y conteo de parpadeos y redirecciona a otra pagina segun el resultado obtenido
"""


def detect_motion(video, id):
    #detector = FaceMeshDetector(maxFaces=1)
    #video = cv2.VideoCapture(-1, cv2.CAP_ANY) #CAP_V4L2,cv2.CAP_V4L,cv2.CAP_DSHOW,cv2.CAP_ANY
    blink_counter_haar = BlinkCountHaar()
    face_orientation = Face_Orientation()
    face_liveness = Face_Liveness()
    init_time_limit = None
    time_init = True
    flag_app = True
    reset_camera(video)

    while flag_app:
        ret, frame = video.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame, faces_detector = detector.findFaceMesh(frame, draw=False)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (7, 7), 0)

            if face_liveness.recognition_liveness(frame, count_liveness):
                if face_orientation.decide_orientation(frame):
                    if time_init:
                        init_time_limit = default_timer()
                        time_init = False
                    blink_counter_haar.run_blink_detector(
                        video, frame, faces_detector, detector)
                    if blink_counter_haar.limit_number_blink(init_time_limit, number_blink, time_count_blink):
                        flag_app = False
                        video.release()

            (flag, encodedImage) = cv2.imencode(".jpg", frame)
            if not flag:
                continue
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
            
    result = check_verification(blink_counter_haar.limit_number_blink(
        init_time_limit, number_blink, time_count_blink), blink_counter_haar.validation_blink, video)
    info = id + " " + result['status']
    # Emitir una respuesta a traves de una API
    write_file(info)
    
    return result


"""
Metodo encargado de cerrar la comunicacion de Hardware y Software de los recursos de la camara,
este metodo es utilizado principalmente con el objetivo de evitar algun problema al momento de refrestar la pagina,
y que los recursos de la camara esten ocupados en segundo plano por una instancia anterior
"""


def reset_camera(cap):
    cap.release()
    cap.open(-1, cv2.CAP_ANY)


"""
Metodo para retornar el estado al finalizar la transmision; "success" si cumplio el numero de parpadeos
en el tiempo establecido ó "fail" en caso contrario
"""


def check_verification(limit_number_blink, validation_blink, cap):
    if limit_number_blink:
        if validation_blink:
            cap.release()
            return {"status": "success"}
        if not(validation_blink):
            cap.release()
            return {"status": "fail"}


"""
metodo encargado de leer el archivo donde se almacenara el resultado final de la secuencia de antispoofing
y retorna el resultado "fail" o "success"
"""


def observe_transmission(id):
    return read_line(id)
