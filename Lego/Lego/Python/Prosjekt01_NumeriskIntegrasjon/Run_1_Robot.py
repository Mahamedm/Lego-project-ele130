#!/usr/bin/env pybricks-micropython


# Legger til mappene midlertidig i søkestien
import os
import sys
import _thread
from time import sleep, perf_counter
p_root = os.getcwd() #root of project
sys.path.append(p_root)
sys.path.append(p_root+"/"+"HovedFiler")
sys.path.append(p_root+"/"+"moduler")
#_______________________________________________________

# importing relevant functions & variables to run on the robot
import config
from Main import Configs, data, init, addMeasurements, MathCalculations, setMotorPower, stopMotors
from funksjoner import RetreiveInputs, writeToFile, packLiveData, setPorts, CustomStopError, WriteAllToFile
try:
    from EV3AndJoystick import *
    from pybricks.parameters import Port
    import pybricks.ev3devices as devices
except Exception as e:
    sys.print_exception(e)
    pass  # for å kunne eksportere funksjoner



# Reading stop signal from laptop and exiting safely
ProgramEnded = False # boolean flagg for å stoppe programmet fra pc-en
def StopLoop(robot):
    global ProgramEnded
    connection = robot.connection
    while True:
        try:
            msg = connection.recv(1024)
            if msg == b"Stop":
                print('received stop signal')
                ProgramEnded = True
                break
        except OSError:
            pass


# Modify live plot lists to run for a longer time keeping constant size
def limit_measurements(data, k):
    max_values = 1000 # how many values to save on ev3
    if k >= max_values:
        k = max_values-1
        g_map = data.__dict__
        for key in g_map:
            if len(g_map[key]) > max_values: # make sure lists are not empty
                g_map[key].pop(0) # runs at O(n), but neglishable since n = max_values --> O(1)
    return k
#-----------------------------



def main():
    try:


        # Determine minimum lists to send to PC for live plotting
        plotKeys = []
        
        # Create a deterministic order of the lists
        keyOrder = [key for key in data.__dict__]
    

        # Initialize robot
        robot = Initialize(Configs)
        setPorts(robot,devices,Port)


        # Setter opp joystick eller gui knapp
        if Configs.livePlot:
            stop_type = ""

            if Configs.ConnectJoystickToPC:
                print(' --> setter opp stopp-knapp med joystick (tilkoblet pc)')
                stop_type = "joystick"
                robot.connection.send(b"joystick")

            elif robot.joystick["in_file"] is not None:
                print(' --> setter opp stopp-knapp med joystick (tilkoblet robot)')
                stop_type = "joystick"
                robot.connection.send(b"joystick")
                
            elif "connection" in robot.__dict__:
                print(' --> setter opp stopp-knapp via PC')
                stop_type = "gui"
                robot.connection.send(b"gui")
            

            # PC sends the keys to plot after reading the plotting function
            # This makes it more efficient and only sends the keys we want to plot
            recvData = b""
            while True:
                recvData += robot.connection.recv(1024)
                if recvData.find(b"?") != -1:
                    plotKeys = recvData.replace(b"?",b"").decode("utf-8").split(",")
                    break
            
            if len(plotKeys) == 0 or plotKeys[0] == "":
                print()
                print("______________ ERROR WHEN LIVE PLOTTING _______________________")
                print("You have specified to plot live data")
                print("but you have not explicitly called plt.plot(...)")
                print("Please specify which variables to plot in the plotting function")
                print('_______________________________________________________________')
                print()
                raise SystemExit()
            
            
            if stop_type == "joystick":
                _thread.start_new_thread(getJoystickValues, [robot])
            elif stop_type == "gui":
                _thread.start_new_thread(StopLoop, (robot,))

        #____________________________________________


        # Running live without plotting and minimizing time-step
        if not Configs.livePlot:

            if robot.joystick["in_file"] is not None:
                print(' --> setter opp stopp-knapp med joystick')
                _thread.start_new_thread(getJoystickValues, [robot])

            robot.brick.speaker.set_volume(2, which='Beep')
            print("\n___________STATUS_____________")
            print('Running with livePlot = False to achieve minimal time-step')
            print('begins in: 3')
            robot.brick.speaker.play_notes(['A3/4'])
            sleep(0.1)
            print('begins in: 2')
            robot.brick.speaker.play_notes(['A3/4'])
            sleep(0.1)
            print('begins in: 1')
            robot.brick.speaker.play_notes(['A3/4'])
            sleep(0.1)
            print('GO!')
            print('______________________________\n')
            if Configs.avgTs < 0.001:
                print('Robot will try and hold Ts ~= 0.001 sec')
            else:
                print('Robot will try and hold Ts ~=',Configs.avgTs,'sec')
            print('Please press CENTER, any ARROWS buttons on the robot (eller skyteknapp joystick om tilkoblet) to finish. Files will not save otherwise')
            
            robot.brick.speaker.play_notes(['A4/16'])
            robot.brick.speaker.set_volume(50, which='Beep')

        k = 0
        meas = {}
        #measKey = None # any arbitrary key from measurements
        constant_t = perf_counter()

        # Store number of #variables specified by the user in the d-object
        # if this number increases, it means they made a new list by accident and we throw an error
        numVariables = len(data.__dict__)
        d_map = data.__dict__

        # Main loop on robot --> appends and saves all measurements and calculations to file along with plotting
        while True:
            if not Configs.livePlot and len(robot.brick.buttons.pressed()) > 0:
                print('button on the EV3-robot has been pressed --> saving all data please wait')
                raise CustomStopError

            if Configs.ConnectJoystickToPC:
                RetreiveInputs(robot,config)

            addMeasurements(data,robot,init,k) # just use k to check if we are at k=0 or k>0
            
            # figure out which values are measurements and mark them in the txt_file
            if k == 0:
                for key in d_map:
                    if len(d_map[key]) > 0:
                        meas[key] = key
            #________________________________________________________________________    
            
            MathCalculations(data,k,init)

            if Configs.livePlot:

                # Skriver målinger til fil for hver iterasjon
                if len(Configs.filename)>4:
                    streng = writeToFile(d_map,k,meas,keyOrder,init)
                    robot.dataToFile.write(streng)

                # Sender live målinger og plotter
                if Configs.livePlot:
                    packLiveData(plotKeys,d_map,robot)
           

            # Setter motorverdier til roboten
            setMotorPower(data,robot)

          
            # Hvis skyteknappen trykkes inn så skal programmet avsluttes
            if config.joyMainSwitch:
                print("joyMainSwitch er satt til 1")
                if not Configs.livePlot:
                    sleep(0.1)
                    print()
                    raise CustomStopError
                break
            
            # Hvis du trykket stopp-knappen på pc-en
            elif ProgramEnded:
                print("Stopp knappen på PC-en ble trykket")
                break
            

            
            # Avoid saving long lists in online mode hogging memory of ev3 and crashing
            if Configs.limitMeasurements:
                k = limit_measurements(data,k) # will make FIR (that has m > limit) inaccurate in online mode
      
           
            # Keep the time-step similar to avgTs
            if Configs.avgTs > 0.001 and not Configs.livePlot:
                elapsed = perf_counter()-constant_t
                dt = Configs.avgTs - elapsed
                if dt > 0:
                    sleep(dt)
                constant_t = perf_counter()
            
            k += 1
            
           
            
    # creating a custom error to raise when not online to avoid traceback of errors.
    except CustomStopError:
        pass

    except MemoryError as e:
        print("\n___Status for minnebruk__")
        print("Det er fullt minne fordi variablene/listene dine ble for lange")
        print("If you wish to run for longer, set limitMeasurements in Configs to True")
        sys.print_exception(e)
        print("___________________________\n",)

    except AttributeError as e:
        print("\n_____Attribute error was caught_____")
        msg = str(e).lower()
        deviceError = False
        if msg.find("sensor") !=-1 and msg.find("bunch") !=-1:
            deviceError = True
            print("Option1: A sensor might not be connected properly to the port:")
            print("Solution: --> Check the cables to each sensor.")
            print()
            print("Option2: Two or more sensors of same type might be connected to the robot")
            print("Solution: --> Specify port-number at the end of the sensor name: e.g robot.ColorSensor2")
            print()
            print("Option3: Maybe you are trying to access the data (som holder listene dine) with an invalid attribute that happens to have the word 'sensor' in it")
            print("Solution: --> Check if the attribute name is typed correct (case sensitive) or exists")


        elif msg.find("motor") !=-1 and msg.find("bunch") !=-1:
            deviceError = True
            print("Option1: A motor is not connected properly to the port:")
            print("Solution: --> Check the cables to each motor or restart the robot")
            print()
            print("Option2: Maybe you are trying to access the data (som holder listene dine) with an invalid attribute that happens to have the word 'motor' in it")
            print("Solution: --> Check if the attribute name is typed correct (case sensitive) or exists")

            
       
        if deviceError:
            print()
            # Presenterer motorer og sensorer som roboten har tilgang til:
            sensorList = []
            motorList = []
            for key in robot.__dict__:
                if key.lower().find("sensor") != -1:
                    sensorList.append(key)
                elif key.lower().find("motor") != -1:
                    motorList.append(key)
            print('++++++++Sensor & Motors++++++++')
            print('Sensorer oppdaget av roboten:')
            for sensor in sensorList:
                print("-",sensor)

            print('\nMotorer oppdaget av roboten:')
            for motor in motorList:
                print("-",motor)
            print('+++++++++++++++++++++++++++++++')

        print("Specific error message:")
        sys.print_exception(e)
        print('_______________________________')
        print()

    except Exception as e:
        print('encountered error in robot main thread')
        
        if len(data.__dict__) != numVariables:
            print()
            print('______Error: Created variables in d-object during running time______')
            print("You have created a new list/variable in the data-object during runtime.")
            print("The number of variables you have should be static.")
            print("This usually happens when you do data.nameOfAttribute = value when")
            print("'nameOfAttribute' hasn't been defined beforehand.")
            print('Solution: Check functions in Main.py and make sure to use append()')
            print("____________________________________________________________________")
            print()
        else:
            sys.print_exception(e)

    finally:

        if not Configs.livePlot:
            robot.brick.speaker.beep()
        stopMotors(robot)

        CloseJoystick(robot,Configs) # Close any connection firsst
        
        WriteAllToFile(robot,Configs,d_map,keyOrder,init,meas) # has a check to only write -> livePlot=False
        CloseFile(robot) # then close file
        
        robot.brick.speaker.beep()
        sys.exit()
        


if __name__ == '__main__':
    if Configs.Online:
        main()
    else:
        print()
        raise Exception("This file can only be run when Online=True")