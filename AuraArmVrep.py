from vrepToOpenCV import vrep, np, VrepToOpenCV
import random
import time
import os


class AuraArmVrep:
    __joints = {"Joint#1": -1, "Joint#2": -1, "Joint#3": -1, "Joint#4": -1}
    __angles = {"alpha": -1, "beta": -1, "gamma": -1, "theta": -1}
    __visonSensors = -1

    def __init__(self, serverIP, serverPort):
        vrep.simxFinish(-1)
        self.__clientID = vrep.simxStart(serverIP, serverPort, True, True, 5000, 5)
        self.__visonSensors = VrepToOpenCV("Webcam", self.__clientID)
        self.__connectAllPeaces()
        self.__getAngles()

    def __connectPiece(self, nameInVrep):
        status, piece = vrep.simxGetObjectHandle(self.__clientID, nameInVrep, vrep.simx_opmode_blocking)

        if status == vrep.simx_return_ok:
            print("conectado ao " + nameInVrep)
            return piece
        else:
            print(nameInVrep + " não conectado")
            return status

    def __getAngles(self):
        for joint, angle in zip(list(self.__joints.values()), list(self.__angles.keys())):

            status, angle_vrep = vrep.simxGetJointPosition(
                self.__clientID, joint, vrep.simx_opmode_blocking)

            while status == vrep.simx_return_novalue_flag:
                status, angle_vrep = vrep.simxGetJointPosition(self.__clientID, joint, vrep.simx_opmode_blocking)

            if status == vrep.simx_return_ok:
                self.__angles[angle] = angle_vrep

            else:
                self.__angles[angle] = status

    def __connectAllPeaces(self):

        for joint in list(self.__joints.keys()):
            self.__joints[joint] = self.__connectPiece(joint)

    def __simulationIsActive(self):
        if vrep.simxGetConnectionId(self.__clientID) == -1:
            return False
        else:
            return True

    def setAngles(self, **angles):
        for angle, value in angles.items():
            self.__angles[angle] = value

        for joint, angle in zip(list(self.__joints.values()), list(self.__angles.values())):
            vrep.simxSetJointPosition(self.__clientID, joint, angle, vrep.simx_opmode_blocking)

    @staticmethod
    def __finish():
        vrep.simxFinish(-1)

    def debug(self):
        print("angles:", self.__angles)
        print("joints:", self.__joints)

    def testAruco(self):
        while self.__simulationIsActive():
            x, y, z = self.__visonSensors.getArucoPos()
            print("x:", x, "y:", y, "z:", z)

    def collectingData2DWithAruco(self, n_samples, file_name):

        while self.__simulationIsActive() and n_samples > 0:
            beta, gamma = self.__randomAngle()

            self.setAngles(beta=beta, gamma=gamma)
            time.sleep(0.5)

            x, y, z = self.__visonSensors.getArucoPos()

            if x is not None:
                self.__getAngles()
                self.__saveSample(file_name, self.__angles["beta"], self.__angles["gamma"], x, y, z)
                n_samples -= 1

    @staticmethod
    def __randomAngle():
        return np.pi * random.uniform(0, 1), np.pi * random.uniform(0, 1)

    @staticmethod
    def __saveSample(file_name, *sample):
        sample = np.array(sample)
        sample = sample.reshape((1, sample.size))

        if os.path.isfile(file_name):

            file = open(file_name, mode="a")
            np.savetxt(file, sample, delimiter=",")
        else:

            file = open(file_name, mode="a")
            file.write("beta,gamma,rx,ry,rz\n")
            np.savetxt(file, sample, delimiter=",")

        file.close()

    def getMeanMarkersPos(self):

        if self.__simulationIsActive():
            x, y, z = self.__visonSensors.getArucoPos()
            if x is not None:
                return np.array([x, y, z])
            else:
                return None
