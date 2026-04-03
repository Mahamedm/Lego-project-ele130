from struct import unpack
from time import perf_counter

# Bunch klassen arver fra dictionary og gir støtte til punktum-notasjon
# Fordi vi bruker punktum-notasjon er det ikke eksplisitt 
# at det vi kaller på er en funksjon/metode eller en egendefinert-variabel
# OBS! unngå å navngi listene dine med innebygde metoder fra dictionary

# minimalt støtte til punktumnotasjon i micropython
# må bruk Bunch.__dict__ for å finne attributes
class Bunch(dict):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.__dict__.update(self)


# Støttes i python 3, men ikke i micropython. Mye mer funksjonalitet
# konverterer dataobjektet bunch til denne typen når vi detekterer at vi er på PC
class BunchPython(dict):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.__dict__ = self

# Imitates tic toc from matlab
# Returnerer 0 når du kaller tic
class clock:
    def __init__(self):
        self.t0 = 0
    def tic(self):
        self.t0 = perf_counter()
        return 0
    def toc(self):
        return perf_counter() - self.t0


# Denne klassen arver fra innebygd liste
# Fungere som append når: index = len(list) O(1) + litt overhead
# Fungere som delete+insert når: index < len(list) O(n) ~ 10x slower
# Fordi den arver fra liste kan du bruke alle innebygde metoder f.eks append
class List(list):
	def __init__(self, argList=[]):
		super().__init__(argList)
		self.size = len(self) 
        # in micropython it seems like creating a counter size
        # is faster than actually calling len(self) (not the case in python3)
		
	def __setitem__(self,index,value):
		# wish this to be as fast as possible when simulating append
		if index == self.size:
			self.append(value)
			self.size+=1
			return
		
		# All other checks will take longer ~10x slower (avoid doing this)
		dif = (index+1)-self.size
		if index < 0:
			raise Exception("Cannot add values negative indices")

		if dif < 1:
			del(self[index])
			self.insert(index,value)
			return

		self.size+=dif
		self.extend([None] * (dif-1) + [value])


# Raiser denne erroren når vi trykker på knappene til roboten ved livePlot = False
class CustomStopError(Exception):
    pass

# Konverterer tekst-variabler, 
# henter ut verdier, formaterer til en streng og returnerer
# Bruker liste for å unngå overheads fra += string concats og konverterer til streng
#from time import perf_counter
def writeToFile(d_map,k,meas,keyOrder,init):   
    
    # Ability to test with custom key_order (used in unit tests)
   
    last_index = len(keyOrder)-1
    str_list = []

    if k == 0:
        # Skriv variabelnavn på første linje og marker om dette er en måling eller beregning 
        g_map = init.__dict__
        for i,v in enumerate(keyOrder):
            if v in meas:
                if i == last_index:
                    str_list.append(v)
                    str_list.append("=meas\n")
                else:
                    str_list.append(v)
                    str_list.append("=meas,")
            else:
                if i == last_index:
                    str_list.append(v)
                    str_list.append("=calc\n")
                else:
                    str_list.append(v)
                    str_list.append("=calc,")

        # lagring av initialmålinger som brukes i addmeasurements/mathcalculations
        # er initialmålings-listen tom, så bruker lagrer vi en tom streng istede
        if len(g_map) == 0:
            str_list.append("No specified init-data\n")
        else:
            for i,v in enumerate(g_map):
                value = g_map[v]
                if i == len(g_map)-1:
                    str_list.append(str(v))
                    str_list.append("=")
                    str_list.append(str(value))
                    str_list.append("\n")
                else:
                    str_list.append(str(v)) 
                    str_list.append("=")
                    str_list.append(str(value))
                    str_list.append(",")
        

      
    # Så skriver vi bare verdiene som strenger
    for i,v in enumerate(keyOrder):
        try:
            value = d_map[v][-1]
            if value == True:
                value = 1
            elif value == False:
                value = 0
            elif value == None:
                value = ""
                
            if i == last_index:
                str_list.append(str(value))
            else:
                str_list.append(str(value))
                str_list.append(",")
        except IndexError:
            if i != last_index:
                str_list.append(",")
   
 
    str_list.append("\n")
    streng = ''.join(str_list)
    return streng
#_________________________________________________________

# More fine grained control over plotting x and y with slices
def customSlicePlot(data,plotSlice):
    Info = plotSlice.strip().split("[")
    ListName,start,end = None,None,None


    # Leave it to the program to handle dimensions of data plottet
    if len(Info) == 1:
        if Info[0] not in data.__dict__:
            raise KeyError("{0}".format(Info[0]))
        ListName = Info[0]
        start = 0
        end = None if len(data[ListName]) == 0 else len(data[ListName])

    elif len(Info) == 2:
        ListName = Info[0].strip()
        sliceInfo = Info[1].strip().strip("]")
        if sliceInfo.find(":") == -1:
            errMsg = 'You have sent in format {0} to plotting. Must have this format --> "{1}[a:b]" '.format(plotSlice,ListName)
            raise Exception(errMsg)
        pos = sliceInfo.find(":")
        start = 0
        end = None if len(data[ListName]) == 0 else len(data[ListName])

        try:
            start = int(sliceInfo[:pos])
        except ValueError:
            pass
        try:
            end = int(sliceInfo[pos+1:])
        except ValueError:
            pass

    else:
        errMsg = 'You have sent in format {0} to plotting. Must have this format --> "ListeNavn[a:b]"'.format(plotSlice)
        raise Exception(errMsg)

   
    return ListName,start,end
        


# funksjonen lagrer alle målingene/beregninger i en loop og tar tid avhengig av hvor lav avgTs vi spesifiserte
def WriteAllToFile(robot,Configs,d_map,keyOrder,init,meas):
    if not Configs.livePlot:
        import sys
        print('Please wait while the program is writing to file...')
        # find length of the largest list
        longest = -1
        cur_key = None
        for key in d_map:
            if len(d_map[key]) > longest:
                cur_key = key
                longest = len(d_map[key])
        # Write everything in one go to the file
        max_iter = len(d_map[cur_key])
       
        print()
        print("SAVING FILE PLEASE WAIT PATIENTLY")
        print('There is in total {max_iter} measurements and calculations to save'.format(max_iter=max_iter))
        for k in range(max_iter):
            
            if k%10 == 0:
                val = "progress: {:.2f} %".format(100*k/max_iter)
                sys.stdout.write("\r" + val)

            str_list = []
            last_index = len(keyOrder)-1
            if k == 0:
                g_map = init.__dict__
                for i,v in enumerate(keyOrder):
                    if v in meas:
                        if i == last_index:
                            str_list.append(v)
                            str_list.append("=meas\n")
                        else:
                            str_list.append(v)
                            str_list.append("=meas,")
                    else:
                        if i == last_index:
                            str_list.append(v)
                            str_list.append("=calc\n")
                        else:
                            str_list.append(v)
                            str_list.append("=calc,")

                # lagring av initialmålinger som brukes i addmeasurements/mathcalculations
                # er initialmålings-listen tom, så bruker lagrer vi en tom streng istede
                if len(g_map) == 0:
                    str_list.append("No specified init-data\n")
                else:
                    for i,v in enumerate(g_map):
                        value = g_map[v]
                        if i == len(g_map)-1:
                            str_list.append(str(v))
                            str_list.append("=")
                            str_list.append(str(value))
                            str_list.append("\n")
                        else:
                            str_list.append(str(v)) 
                            str_list.append("=")
                            str_list.append(str(value))
                            str_list.append(",")

            for i,v in enumerate(keyOrder):
                try:

                    idx = (len(d_map[v]) - max_iter) + k
                    if idx >= 0:
                        value = d_map[v][idx]
                    else:
                        raise ValueError

                    if value == True:
                        value = 1
                    elif value == False:
                        value = 0
                    elif value == None:
                        value = ""

                    if i == last_index:
                        str_list.append(str(value))
                    else:
                        str_list.append(str(value))
                        str_list.append(",")
                except (IndexError,StopIteration,ValueError):
                    if i != last_index:
                        str_list.append(",")

            str_list.append("\n")
          
            streng = ''.join(str_list)
            robot.dataToFile.write(streng)

        sys.stdout.write("\r" + "progress: 100%")



# Pakker sammen live målinger for plotting
def packLiveData(plotKeys,d_map,robot):
    LiveData = {}

    # We know key must be valid otherwise 
    # plotting section would complain
    for key in plotKeys:
        try:
            LiveData[key] = d_map[key][-1]
        except IndexError:
            pass
    msg = str(LiveData)
    
    try:
        robot.connection.send(bytes(msg, "utf-8") + b"?") # Sender målinger fra Ev3 til PC-en din
    except OSError:
        pass


# Finner ut om streng-verdien er en int eller float
# om det ikke er noen av delene returnerer den strengen tilbake
def parseMeasurements(s):
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    
    return s.strip()
    
    
# Pakker opp data i offline modus fra filenameMeasurement
def unpackMeasurement(d,keys,m_keys,Data):
    for i,key in enumerate(keys):
        if key in d and key in m_keys:
            d[key].append(parseMeasurements(Data[i]))
            
#___________________________________________________________




# Denne funksjonen kjører på roboten og henter input fra PC
# Streng-manipulasjon brukes istede for json.decode for å få lavere tidsskritt


def RetreiveInputs(robot,config):
    try:
        FORMAT = "2d14i2d" # 2 doubles 14 integers og 2 doubles
        recvData = robot.JoystickConnection.recv(8192)
        res = unpack(FORMAT,recvData)
        config.joyForwardInstance = res[0]
        config.joySideInstance = res[1]
        config.joyPOVForwardInstance = res[2]
        config.joyPOVSideInstance = res[3]
        config.joyMainSwitch = res[4]
        config.joy2Instance = res[5]
        config.joy3Instance = res[6]
        config.joy4Instance = res[7]
        config.joy5Instance = res[8]
        config.joy6Instance = res[9]
        config.joy7Instance = res[10]
        config.joy8Instance = res[11]
        config.joy9Instance = res[12]
        config.joy10Instance = res[13]
        config.joy11Instance = res[14]
        config.joy12Instance = res[15]
        config.joyPotMeterInstance = res[16]
        config.joyTwistInstance = res[17]
    except OSError:
        pass
#______________________




# Funksjonen finner sensorer og motorer som er koblet og legger dem automatisk til robot-objektet
def setPorts(robot, devices, port):

    sensor_ports = [port.S1,port.S2,port.S3,port.S4]
    motor_ports = ["A","B","C","D"]

    # Går gjennom alle attributes i ev3-pakken
    # og henter alle sensorer i pakken
    
    sensor_dict = {}
    for attribute in dir(devices):
        streng = str(attribute).lower()
        if streng.find("sensor") != -1:
            sensor_dict[str(attribute)] = 0
    #_________________________________________


    # Sjekker om det finnes sensorer av samme type
    for p in sensor_ports:
        for device_name in sensor_dict:
            try:
                sensor = getattr(devices,device_name)
                val = sensor(p)
                sensor_dict[device_name]+=1
            except (AttributeError,OSError):
                pass
    #_____________________________________________


    # Legger til sensorer (resetter gyro til 0 ved start)
    for i,p in enumerate(sensor_ports):
        for device_name in sensor_dict:
            try:
                val = getattr(devices,device_name)
                sensor = val(p)
                if device_name == "GyroSensor": 
                    sensor.reset_angle(0)
                    
                if sensor_dict[device_name] > 1:
                    setattr(robot,device_name+str(i+1),sensor)
                else:
                    setattr(robot,device_name,sensor)
            except (AttributeError,OSError):
                pass
    #______________________


    # Legger til motorer (resetter motorvinkel til 0 ved start)
    for letter in motor_ports:
        try:
            p = getattr(port,letter)
            motor = getattr(devices,"Motor")(p)
            motor.reset_angle(0)
            setattr(robot,"motor"+str(letter),motor)
        except (AttributeError,OSError):
            pass
    #______________________