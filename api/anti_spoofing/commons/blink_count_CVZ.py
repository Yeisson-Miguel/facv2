import cv2
from api.anti_spoofing.config.settings import *


class BlinkCountCVZ():

    def __init__(self):
        self.idList = [22, 23, 24, 26, 110, 157, 158, 159, 160,
                       161, 130, 243, 362, 385, 387, 263, 373, 380]
        self.ratioList = []
        self.blinkCount = 0
        self.totalBlink = 0
        self.countBlinkHaarAndCVZone = 0
        self.isBlinkCVZ = False
        self.counter = 0
        self.color = (0, 0, 255)
        self.distance = 0
        self.threshould_one = threshold_1
        self.threshould_two = threshold_2

    """
    Se toman puntos de referencia de los ojos,despues se toman las coordenadas
    y se calcula la distancia de estos puntos para referenciar si se produjo un parpadeo, y se
    envia estas distancias al metodo get_ratio()
    """

    def run_blink_detector(self, img, faces, detector):
        if faces:
            face = faces[0]
            leftUp = face[159]
            leftDow = face[23]
            leftLeft = face[130]
            leftRight = face[243]
            lenghtHor, _ = detector.findDistance(leftLeft, leftRight)
            lenghtVer, _ = detector.findDistance(leftUp, leftDow)
            self.get_ratio(img, lenghtHor, lenghtVer)

    """
    Metodo que detecta si se hizo un parpadeo,primero se calcula la "distancia" que hace referencia 
    al area del cuadrado donde se detecta el rostro y se compara con unos limites definidos para limitar
    que tan cerca/lejos se puede estar el rostro para contar los parpadeos. Despues, recibe un promedio de radio(umbral) y lo compara
    con algun umbral definido, ademas la variable counter se encarga de almacenar la cantidad 
    de puntos que bajan del umbral para evitar que cada punto lo tome como un parpadeo (cantidad de frames).
    Una vez detecta 10 puntos, significa que se realizo un parpadeo y vuelve a ser cero.
    """

    def detect_flicker(self, img, ratioAvg):
        if self.distance > 31304 and self.distance < 83000:
            if self.distance > 46200 and self.distance < 83000:
                if ratioAvg < self.threshould_one and self.counter == 0:
                    self.blinkCount += 1
                    self.totalBlink += 1
                    self.isBlinkCVZ = True
                    self.color = (0, 255, 0)
                    self.counter = 1
            elif self.distance >= 31304 and self.distance < 46200:
                if ratioAvg < self.threshould_two and self.counter == 0:
                    self.blinkCount += 1
                    self.totalBlink += 1
                    self.isBlinkCVZ = True
                    self.color = (0, 255, 0)
                    self.counter = 1

        if self.counter != 0:
            self.counter += 1
            if self.counter > 10:
                self.color = (0, 0, 255)
                self.counter = 0
        self.show_result(img, ratioAvg)

    """
    Se va calculando el radio, se almacena en un vector los resultados (maximo 4) y se va calculando
    el promedio de los radios obtenidos en el vector para detectar si se realizo un parpadeo. Al final se llama
    el metodo detect_flicker() y se pasa por parametro dichos promedios
    """

    def get_ratio(self, img, lenghtHor, lenghtVer):
        ratio = int((lenghtVer/lenghtHor)*100)
        self.ratioList.append(ratio)
        if len(self.ratioList) > 4:
            self.ratioList.pop(0)
        ratioAvg = sum(self.ratioList)/len(self.ratioList)
        self.detect_flicker(img, ratioAvg)

    """
    Muestra la informacion de la cantidad de parpadeos y se muestra la grafica del umbral
    """

    def show_result(self, img, ratioAvg):
        cv2.putText(img, f'# Parp CVZ: {self.blinkCount}', (1, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.color, 2)
        cv2.putText(img, f'Ttl Parp CVZ: {self.totalBlink}',
                    (450, 410), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (20, 131, 10), 2)
        cv2.putText(img, f'Ambos:   {self.countBlinkHaarAndCVZone}',
                    (200, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (222, 76, 16), 3)
