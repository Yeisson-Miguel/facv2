import cv2
import os
from timeit import default_timer
from api.anti_spoofing.commons.blink_count_CVZ import *


class BlinkCountHaar():

    def __init__(self):
        self.blink_count_cvz = BlinkCountCVZ()
        self.pathDirectory = os.path.dirname(os.path.abspath(__file__))
        self.pathFileFace = os.path.join(
            self.pathDirectory, '../files/haarcascade_frontalface_default.xml')
        self.pathFileEye = os.path.join(
            self.pathDirectory, '../files/haarcascade_eye.xml')
        self.face_cascade = cv2.CascadeClassifier(self.pathFileFace)
        self.eye_cascade = cv2.CascadeClassifier(self.pathFileEye)
        self.blink_count = 0
        self.total_blink_count = 0
        self.time_wait = default_timer()
        self.time_limit = default_timer()
        self.isBlinkHaar = False
        self.eye_flag = True
        self.show_count = True
        self.face_frame = False
        self.validation_blink = False
        self.thickness_line = 4
        self.color_blink = (0, 0, 255)
        self.color_frame = (0, 0, 255)
        self.point_init_marc = (0, 0)
        self.point_finish_marc = (0, 0)

    def run_blink_detector(self, cap, img, faces_detector, detector):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        self.blink_count_cvz.run_blink_detector(
            img, faces_detector, detector)
        for (x, y, w, h) in faces:
            self.eye_flag = False
            img = cv2.rectangle(
                img, (x, y), ((x + w), (y + h)-10), (20, 133, 11), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]
            point_face_init = (x, y)
            point_face_finish = ((x + w), (y + h)-10)
            self.face_size_in_frame(
                point_face_init, point_face_finish, roi_gray, roi_color)
        self.locate_frame(cap, img)
        self.eye_status_detection(img, self.eye_flag)
        self.comparate_blinks()

    """
    Metodo para determinar la distancia entre dos puntos sobre un mismo eje(lineas horizontales/verticales
    para el dibujo de un cuadrado/rectangulo) y despues se calcula el area para comparar el rectangulo del area de la cara con el rectangulo del marco
    """

    def calculate_distance_and_area(self, point1, point2):
        return (abs(point1[0] - point2[0]) * abs(point1[1] - point2[1]))

    """
    Metodo para detectar y pintar el cuadro de los ojos del rostro
    """

    def detect_eyes_face(self, roi_gray, roi_color):
        eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.3, 6)
        for (ex, ey, ew, eh) in eyes:
            self.eye_flag = True
            # cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh),
            #              (35, 218, 20), 2)

    """
    Metodo que detecta el estado de los ojos (abierto-cerrado) y cuenta los parpadeos
    """

    def eye_status_detection(self, img, eye_flag):
        if eye_flag:
            self.show_count = True
            self.color_blink = (0, 0, 255)
        if self.show_count and not(eye_flag) and self.face_frame:
            self.show_count = False
            self.blink_count += 1
            self.total_blink_count += 1
            self.color_blink = (0, 255, 0)
            self.isBlinkHaar = True
        self.show_result(img)

    """
    Compara si se realizo un parpadeo en ambos estilos (Haar Cascade y CVZone), mediante variables booleanas
    que cambian su estado una vez se detecta el parpadeo
    """

    def comparate_blinks(self):

        init_time = default_timer()
        if (int(init_time) % 2 == 0) and (int(init_time) != int(self.time_wait)):
            if self.isBlinkHaar and self.blink_count_cvz.isBlinkCVZ:
                self.blink_count_cvz.countBlinkHaarAndCVZone += 1
                self.isBlinkHaar = False
                self.blink_count_cvz.isBlinkCVZ = False
                self.time_wait = init_time
            else:
                self.isBlinkHaar = False
                self.blink_count_cvz.isBlinkCVZ = False
                self.time_wait = init_time

    """
    Metodo que retorna verdadero si encuentra la cara dentro del marco, de lo contrario retornara falso
    """

    def face_in_frame(self, point_init_face, point_finish_face):
        if ((point_init_face[0] > self.point_init_marc[0]) and (point_init_face[1] > self.point_init_marc[1])) and ((point_finish_face[0] < self.point_finish_marc[0]) and (point_finish_face[1] < self.point_finish_marc[1])):
            return True
        else:
            return False

    """
    Metodo para determinar si el tamaño de la cara dentro del marco corresponde a un valor aceptable
    para detectar los ojos y comenzar a contar los parpadeos
    """

    def face_size_in_frame(self, point_face_init, point_face_finish, roi_gray, roi_color):
        area_face = self.calculate_distance_and_area(
            point_face_init, point_face_finish)
        area_frame = self.calculate_distance_and_area(
            self.point_init_marc, self.point_finish_marc)
        if self.face_in_frame(point_face_init, point_face_finish) and (area_face >= (area_frame * 0.45)):
            self.blink_count_cvz.distance = area_face
            self.face_frame = True
            self.color_frame = (0, 255, 0)
            self.thickness_line = 4
            self.detect_eyes_face(roi_gray, roi_color)
        else:
            self.face_frame = False
            self.blink_count_cvz.distance = 0
            self.thickness_line = 6
            self.color_frame = (0, 0, 255)

    """
    Metodo que al momento de registrar "number_blink" parpadeos por ambos metodos(Haar-cascade y CVZONE) retorna Falso
    para detener el servicio de la camara
    """

    def limit_number_blink(self, init_time_limit, number_blink, time_count_blink):
        if init_time_limit != None:
            time_now = default_timer()
            if(self.blink_count_cvz.countBlinkHaarAndCVZone == number_blink) or (time_now - init_time_limit) >= time_count_blink:
                if self.blink_count_cvz.countBlinkHaarAndCVZone == number_blink:
                    self.validation_blink = True
                return True
            else:
                return False
    """
    Metodo para pintar un cuadro donde ira ubicada la cara y retorna los puntos
    superior izquierdo y el punto inferior derecho del cuadro
    """

    def locate_frame(self, cap, img):
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        xinit = int(width/5) + int((width/5)/3)
        yinit = int(height/8)
        xfin = int((width/5)*4) - int((width/5)/3)
        yfin = int((height/8) * 6)
        self.point_init_marc = (xinit, yinit)
        self.point_finish_marc = (xfin, yfin)
        cv2.rectangle(img, (xinit, yinit), (xfin, yfin),
                      self.color_frame, self.thickness_line)

    """
    Muestra en pantalla el numero de parpadeos
    """

    def show_result(self, img):
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(img, '# Parp Haar:' + str(self.blink_count),
                    (1, 60), font, 0.6, self.color_blink, 2)
        cv2.putText(img, 'Ttl Parp Haar:' + str(self.total_blink_count),
                    (450, 390), font, 0.6, (20, 131, 10), 2)
