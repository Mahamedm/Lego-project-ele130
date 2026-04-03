# Importing packages and setting up paths
import os
import sys
import socket
import traceback
from multiprocessing import Process
p_root = os.getcwd() #root of project
sys.path.append(p_root)
sys.path.append(os.path.join(p_root, r'HovedFiler'))
sys.path.append(os.path.join(p_root, r'Moduler'))
from plotClass import PlotObject
from funksjoner import BunchPython, writeToFile, unpackMeasurement, parseMeasurements
from Main import Configs, data, MathCalculations, lagPlot
data = BunchPython(data.__dict__)


def offline():
    try:
        # Leser av fil online file og skriver til offline med nye berekninger
        # fr: file read
        # fw: file write
        with open(p_root+"/Data/"+Configs.filename,"r") as fr:

            # parsing out which keys are measurements
            keys = []   # store names of measurements + calculations
            m_keys = [] # store names of measurements
            init = BunchPython()
            meta_data = fr.readline().rstrip().split(",")
            for rawkey in meta_data:
                if rawkey.find("=meas") != -1:
                    key = rawkey.replace("=meas","")
                    m_keys.append(key)
                key = rawkey.replace("=calc","").replace("=meas","")
                keys.append(key)
            
            

            # parsing out initial values to calculate offline
            initial_verdier = fr.readline().rstrip().split(",")
            for g_data in initial_verdier:
                try:
                    v = g_data.split("=")
                    init[v[0]] = parseMeasurements(v[1])
                except IndexError:
                    # dersom du ikke har initialmålinger
                    pass
            
            # parsing out measurements and recalculating in offline
            dataFromFile = fr.readlines()
            if len(Configs.filenameOffline)>4:
                fw = open(p_root+"/Data/"+Configs.filenameOffline,"w",encoding="utf-8")
                for k,EachRow in enumerate(dataFromFile):
                    m_data = EachRow.split(",")
                    unpackMeasurement(data, keys, m_keys, m_data)

                    MathCalculations(data,k,init)
                    
                    try:
                        streng = writeToFile(data,k,m_keys,keys,init)
                        fw.write(streng)
                    except Exception:
                        traceback.print_exc()
                        fw.close()
                fw.close()
        
       
        # tilslutt plotter vi data
        plt = PlotObject(data, Configs)
        lagPlot(plt)
        plt.stopPlot()

    except Exception:
        traceback.print_exc()
        sys.exit()


def sendInputs(connection):
    from JoystickPyglet import main
    main(connection)
    #from JoystickPygame import main
    #main(connection)
#_______________________________________________________


# Setup sockets
def main():

    # ConnectJoystickToPC=True, setup socket object and connect to EV3.
    if Configs.ConnectJoystickToPC:
        inputSock = SetupInputSocket()
        if Configs.livePlot:
            Process(target=sendInputs, args = (inputSock,)).start() # running in separate process
        else:
            sendInputs(inputSock) # running in main thread


    # If Online=True & livePlot=True, setup socket object and connect to EV3.
    if Configs.livePlot:
        print("__________Status for connection________",flush=True)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        try:
            addr = (Configs.EV3_IP, 8070)
            print("Attempting to connect to {}".format(addr),flush=True)
            sock.connect(addr)
            DataToOnlinePlot = sock.recv(1024)
            if DataToOnlinePlot == b"ack":
                print("Connection established for plotting",flush=True)
            else:
                print("no ack")
                sys.exit()
        except socket.timeout:
            print("IP-adressen er mest sannsynlig endret. Vennligst sjekk ip-addressen",flush=True)
            traceback.print_exc()
            sys.exit()

        except Exception:
            print("\n____________Error with socket running ONLINE________________________",flush=True)
            print("Possible solutions to help you debug",flush=True)
            print('Did you mean to run this file offline but has online=True?',flush=True)
            print("Did you run this file without running Run_1_Robot.py first?",flush=True)
            print("Did your ip-address change? (usually this)",flush=True)
            traceback.print_exc()
            sys.exit()
        finally:
            print("_______________________________________\n",flush=True)
    
        try:
            msg = sock.recv(1024)
            if msg == b"joystick":
                print('Stoppknapp: skyte-knappen, joystikken',flush=True)
                plt = PlotObject(data, Configs, sock, False)
            else:
                print('Stoppknapp: se skjermen',flush=True)
                plt = PlotObject(data, Configs, sock)
            lagPlot(plt)

            plotKeys = ""
            for i,key in enumerate(plt.DataToPlot):
                if i == len(plt.DataToPlot)-1:
                    plotKeys += key
                else:
                    plotKeys += key + ","
            msg = bytes(plotKeys, "utf-8") + b"?"
            sock.send(msg)

            plt.startPlot()
        except Exception:
            traceback.print_exc()
            sys.exit()



def SetupInputSocket():
    input_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        addr = (Configs.EV3_IP, 8080)
        input_sock.connect(addr)
        signalData = input_sock.recv(1024)
        if signalData == b"ack":
            print("Connection established for Joystick through pygame")
        else:
            print("no ack")
            sys.exit()
    except socket.timeout:
        print("failed (sjekk om IP addressen er forandret)")
        sys.exit()
    except Exception as e:
        print(e)
        sys.exit()
    
    input_sock.setblocking(False)
    return input_sock
    


if __name__=="__main__":
    if Configs.Online:
        print("Starter ikke programmet etter noen sekunder kan det hende at ip-adressen er endret\n",flush=True)
        main()
    else:
        print("Running in Offline\n",flush=True)
        offline()