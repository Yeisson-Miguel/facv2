import tensorflow as tf
import numpy as np
import pickle
import cv2
import os
# uncomment this line if you want to run your tensorflow model on CPU
# os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # -1


class Face_Liveness():

    def __init__(self):
        self.path_directory = os.path.dirname(os.path.abspath(__file__))
        self.path_file_face_liveness = os.path.join(
            self.path_directory, 'liveness.model')
        self.path_file_face_label_encoder = os.path.join(
            self.path_directory, 'label_encoder.pickle')
        self.path_detector_folder = os.path.join(
            self.path_directory, 'face_detector')
        self.path_file_enconded_faces = os.path.join(
            self.path_directory, '../face_recognition/encoded_faces.pickle')
        self.confidence = 0.5
        self.args = {'model': self.path_file_face_liveness, 'le': self.path_file_face_label_encoder, 'detector': self.path_detector_folder,
                     'encodings': self.path_file_enconded_faces, 'confidence': self.confidence}
        self.sequence_count = 0
        self.confirmation_liveness = False
        (self.encoded_data, self.detector_net,
         self.liveness_model, self.le) = self.load_files_liveness()

    """
    Metodo que carga detector de rostros serializado,cargue el modelo del detector de vida y el codificador de etiquetas desde el disco
    """

    def load_files_liveness(self):
        with open(self.args['encodings'], 'rb') as file:
            encoded_data = pickle.loads(file.read())
        proto_path = os.path.sep.join(
            [self.args['detector'], 'deploy.prototxt'])
        model_path = os.path.sep.join(
            [self.args['detector'], 'res10_300x300_ssd_iter_140000.caffemodel'])
        detector_net = cv2.dnn.readNetFromCaffe(proto_path, model_path)

        liveness_model = tf.keras.models.load_model(self.args['model'])
        le = pickle.loads(open(self.args['le'], 'rb').read())
        return encoded_data, detector_net, liveness_model, le

    """
    Metodo que dibuja el marco de la cara en la pantalla y la informacion de esta misma
    """

    def print_info_window(self, frame, label_name, label, startX, startY, endX, endY):
        if label_name == 'fake':
            cv2.putText(frame, "Don't try to Spoof !", (startX, endY + 25),
                        cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)

        cv2.putText(frame, label, (startX, startY - 10),
                    cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
        cv2.rectangle(frame, (startX, startY),
                      (endX, endY), (0, 0, 255), 4)

    """
    Metodo encargado de reconocer si es una persona real la que se encuentra frente a la camara 
    o solamente es una fotografia o video
    """

    def recognition_liveness(self, frame, count_liveness):
        if not(self.confirmation_liveness):
            (h, w) = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(
                frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

            self.detector_net.setInput(blob)
            detections = self.detector_net.forward()

            for i in range(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]

                if confidence > self.args['confidence']:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype('int')

                    startX = max(0, startX-20)
                    startY = max(0, startY-20)
                    endX = min(w, endX+20)
                    endY = min(h, endY+20)

                    face = frame[startY:endY, startX:endX]

                    try:
                        face = cv2.resize(face, (32, 32))
                    except:
                        break

                    face = face.astype('float') / 255.0
                    face = tf.keras.preprocessing.image.img_to_array(face)
                    face = np.expand_dims(face, axis=0)

                    preds = self.liveness_model.predict(face)[0]
                    j = np.argmax(preds)
                    label_name = self.le.classes_[j]

                    label = f'{label_name}: {preds[j]:.4f}'
                    if label_name == 'fake':
                        self.sequence_count = 0
                    else:
                        self.sequence_count += 1
                    if self.sequence_count >= count_liveness:
                        self.confirmation_liveness = True
                    self.print_info_window(
                        frame, label_name, label, startX, startY, endX, endY)
            return self.confirmation_liveness
        else:
            return self.confirmation_liveness
