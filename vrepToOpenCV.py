import numpy as np
import cv2
import vrep


class VrepToOpenCV:
    __client_id = -1
    __visionSensorHandle = -1

    def __init__(self, name_in_vrep, client_id):
        self.__client_id = client_id
        self.__visionSensorHandle = self.__connectPiece(name_in_vrep)
        self.__loadCameraCalibration("cameraCalibration.npz")

    def __getImage(self):
        status, res, image = vrep.simxGetVisionSensorImage(self.__client_id, self.__visionSensorHandle, 0,
                                                           vrep.simx_opmode_streaming)
        if status == vrep.simx_return_ok:
            image = np.array(image, np.uint8)
            image = image.reshape((res[0], res[1], 3))
            return cv2.flip(image, 0)
        else:
            return np.array(0)

    def __loadCameraCalibration(self, file_name):
        self.__cameraMatrix, self.__distanceCoefficients = np.load(file_name).values()

    def __connectPiece(self, name_in_vrep):
        status, piece = vrep.simxGetObjectHandle(self.__client_id, name_in_vrep, vrep.simx_opmode_blocking)

        if status == vrep.simx_return_ok:
            return piece
        else:
            return status

    def getArucoPos(self):

        aruco_squared_dimension = 0.0035

        frame = self.__getImage()

        if frame.ndim == 0:
            return None, None, None

        marker_dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(frame, marker_dictionary)

        if ids is None:
            return None, None, None

        rotation_vectors, translation_vectors, _ = cv2.aruco.estimatePoseSingleMarkers(corners, aruco_squared_dimension,
                                                                                       self.__cameraMatrix,
                                                                                       self.__distanceCoefficients)

        cv2.aruco.drawDetectedMarkers(frame, corners)

        return translation_vectors[:, :, 0].mean(), translation_vectors[:, :, 1].mean(), translation_vectors[:, :,
                                                                                         2].mean()

    def showImage(self, image=np.zeros(1)):

        name_window = "OpenCV Image"
        cv2.namedWindow(name_window, cv2.WINDOW_NORMAL)
        if image.size == 1:
            cv2.imshow(name_window, self.__getImage())
        else:
            cv2.imshow(name_window, image)

        cv2.waitKey(60)
