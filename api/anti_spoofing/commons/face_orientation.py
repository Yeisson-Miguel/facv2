import cv2
import os
import random


class Face_Orientation():

    def __init__(self):
        self.pathDirectory = os.path.dirname(os.path.abspath(__file__))
        self.pathDetectPerfilFace = os.path.join(
            self.pathDirectory, '../files/haarcascade_profileface.xml')
        self.pathDetectFrontalFace = os.path.join(
            self.pathDirectory, '../files/haarcascade_frontalface_alt.xml')
        self.profile_face = cv2.CascadeClassifier(self.pathDetectPerfilFace)
        self.frontal_face = cv2.CascadeClassifier(self.pathDetectFrontalFace)
        self.orientation_front = False
        self.orientation_side_1 = False
        self.orientation_side_2 = False
        self.option = random.randint(1, 4)

    """
    Metodo para detectar y retornar los objetos detectados segun el clasificador ingresado,
    en este caso para caras de perfil y en frontal
    """

    def detect(self, img, cascade):
        rects, _, confidence = cascade.detectMultiScale3(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30),
                                                         flags=cv2.CASCADE_SCALE_IMAGE, outputRejectLevels=True)
        if len(rects) == 0:
            return (), ()
        rects[:, 2:] += rects[:, :2]
        return rects, confidence

    """
    Metodo para decidir que paso a seguir para confirmar la comprobacion segun un numero aleatorio
    """

    def decide_orientation(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.sign_guide(img, self.option)
        if self.option == 1:
            return self.face_orientation_1_side(img, gray, self.option)
        elif self.option == 2:
            return self.face_orientation_1_side(img, gray, self.option)
        elif self.option == 3:
            return self.face_orientation_2_sides(img, gray, self.option)
        else:
            return self.face_orientation_2_sides(img, gray, self.option)

    """
    Metodo encargado de validar que la cara este frontal despues de cada giro de la cabeza 
    """

    def face_orientation_front(self, img, gray):
        box_frontal, w_frontal = self.detect(gray, self.frontal_face)
        if len(box_frontal) != 0 and w_frontal[0] >= 107 and not(self.orientation_front):
            cv2.putText(
                img, f"Lado Frontal: OK", (200, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            self.orientation_front = True
        if not(self.orientation_front):
            cv2.putText(
                img, f"Lado Frontal: NO", (200, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        return self.orientation_front

    """
    Metodo que hace un pequeño seguimiento para comprobar que la persona gire la cabeza a la izquierda o a la derecha
    """

    def face_orientation_1_side(self, img, gray, option):
        gray_flipped = cv2.flip(gray, 1)
        if option == 1:
            box_1, w_1 = self.detect(gray, self.profile_face)
            tilt_side = 2.5
            #side_1 = "Izq"
        elif option == 2:
            box_1, w_1 = self.detect(gray_flipped, self.profile_face)
            tilt_side = 2.0
            #side_1 = "Der"
        if self.face_orientation_front(img, gray):
            if len(box_1) != 0 and w_1[0] >= tilt_side and not(self.orientation_side_1):
                self.orientation_side_1 = True
                self.orientation_front = False
            if self.orientation_side_1 and self.orientation_front:
                cv2.putText(
                    img, "COMPROBACION: OK", (380, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 131, 10), 2)
                return True
            else:
                return False

    """
    Metodo que hace un pequeño seguimiento para comprobar que la persona gire la cabeza a la izquierda y luego derecha o viceversa
    """

    def face_orientation_2_sides(self, img, gray, option):
        gray_flipped = cv2.flip(gray, 1)

        if option == 3:
            box_1, w_1 = self.detect(gray, self.profile_face)
            box_2, w_2 = self.detect(gray_flipped, self.profile_face)
            tilt_side = 2.5
        elif option == 4:
            box_1, w_1 = self.detect(gray_flipped, self.profile_face)
            box_2, w_2 = self.detect(gray, self.profile_face)
            tilt_side = 2.0

        if self.face_orientation_front(img, gray):

            if len(box_1) != 0 and w_1[0] >= tilt_side and not(self.orientation_side_2):
                self.orientation_side_1 = True
                self.orientation_front = False
            if (len(box_2) != 0) and w_2[0] >= tilt_side and self.orientation_side_1:
                self.orientation_side_2 = True
                self.orientation_side_1 = False
                self.orientation_front = False
        if self.orientation_side_2 and not (self.orientation_side_1) and self.orientation_front:
            cv2.putText(
                img, "COMPROBACION:  OK", (380, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 131, 10), 2)
            return True
        else:
            return False

    """
    Metodo que dibuja la indicacion de comprobacion cuando es de un solo lado
    """

    def sign_guide_1_side(self, img, pointInit, pointFinish):
        if not(self.orientation_side_1):
            cv2.arrowedLine(img, pointInit, pointFinish, (0, 0, 255), 8)

    """
    Metodo que dibuja las indicaciones de comprobacion cuando son dos lados
    """

    def sign_guide_2_side(self, img, pointInitSide1, pointFinishSide1, pointInitSide2, pointFinishSide2):
        if not (self.orientation_side_1) and not (self.orientation_side_2):
            cv2.arrowedLine(img, pointInitSide1,
                            pointFinishSide1, (0, 0, 255), 8)
        if self.orientation_side_1 and not (self.orientation_side_2):
            cv2.arrowedLine(img, pointInitSide1,
                            pointFinishSide1, (0, 255, 0), 8)
            cv2.arrowedLine(img, pointInitSide2,
                            pointFinishSide2, (0, 0, 255), 8)
        if self.orientation_side_2 and not (self.orientation_side_1) and not(self.orientation_front):
            cv2.arrowedLine(img, pointInitSide1,
                            pointFinishSide1, (0, 255, 0), 8)
            cv2.arrowedLine(img, pointInitSide2,
                            pointFinishSide2, (0, 255, 0), 8)

    """
    Metodo que asigna las indicaciones de comprobacion segun el numero alatorio dado
    """

    def sign_guide(self, img, option):
        if option == 1:
            self.sign_guide_1_side(img, (150, 190), (80, 190))
        elif option == 2:
            self.sign_guide_1_side(img, (420, 190), (510, 190))
        elif option == 3:
            self.sign_guide_2_side(
                img, (150, 190), (80, 190), (420, 190), (510, 190))
        else:
            self.sign_guide_2_side(
                img, (420, 190), (510, 190), (150, 190), (80, 190))
