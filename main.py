from AuraArmVrep import AuraArmVrep

if __name__ == "__main__":
    #arm = AuraArmVrep("127.0.0.1", 19999)

    arm = AuraArmVrep("192.168.15.29",19997)

    arm.debug()

   # arm.testAruco()

    # arm.collectingData2DWithAruco(1e4, "arucoDataPyhton.csv")


    print("finsh")
